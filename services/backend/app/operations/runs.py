import asyncio
import datetime
import logging
import time
import uuid
from typing import Any, Literal

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.actions.document_store import load_document
from app.evidence.document_parser import DocumentParser
from app.evidence.models import EvidenceItem
from app.evidence.service import EvidenceService
from app.evidence.storage import get_storage_backend
from app.extraction.adapter import CaseExtractor
from app.facts.models import FactAssertion
from app.facts.schemas import FactAssertionCreate
from app.facts.service import FactService
from app.identity.models import Consent, Principal
from app.operations.models import CaseRun
from app.operations.record_reader import read_evidence
from app.operations.understanding import understand_situation
from app.policy.engine import ProceduralAssessmentEngine
from app.retrieval.hybrid_retriever import HybridRetriever

logger = logging.getLogger(__name__)
TERMINAL = {"completed", "needs_review", "cancelled", "failed"}


async def recover_expired_run(run: CaseRun, db: AsyncSession) -> None:
    """Bounded tasks without a heartbeat must not leave a case locked forever."""
    if run.status in TERMINAL:
        return
    latest = run.stages[-1].get('started_at') if run.stages else None
    touched = datetime.datetime.fromisoformat(latest) if latest else run.created_at
    if touched.tzinfo is None:
        touched = touched.replace(tzinfo=datetime.UTC)
    now = datetime.datetime.now(datetime.UTC)
    if now - touched < datetime.timedelta(minutes=15):
        return
    run.status = 'failed'
    run.error_code = 'operation_interrupted'
    run.finished_at = now
    run.stages = [{**stage, **({'status': 'failed', 'finished_at': now.isoformat()}
                              if stage['status'] == 'running' else {})} for stage in run.stages]
    await db.commit()


class RunRequest(BaseModel):
    operation: Literal["extract", "assess", "draft", "resolve"] = "assess"
    locale: Literal["en", "bn"] = "en"
    expected_version: int | None = None


def serialize_run(run: CaseRun) -> dict[str, Any]:
    events = []
    for index, stage in enumerate(run.stages):
        events.append({'id': f'{run.id}:{index}:start', 'sequence': len(events)+1,
                       'type': 'tool.started', 'task': stage['stage_name'],
                       'timestamp': stage['started_at']})
        if stage['status'] != 'running':
            events.append({'id': f'{run.id}:{index}:end', 'sequence': len(events)+1,
                           'type': 'tool.completed' if stage['status']=='completed' else 'tool.stopped',
                           'task': stage['stage_name'], 'timestamp': stage.get('finished_at'),
                           'details': stage.get('details', {})})
    if run.status in TERMINAL:
        events.append({'id': f'{run.id}:end', 'sequence': len(events)+1,
                       'type': 'input.required' if run.status=='needs_review' else f'run.{run.status}',
                       'timestamp': run.finished_at.isoformat() if run.finished_at else None})
    return {
        "id": str(run.id), "case_id": str(run.case_id), "operation": run.operation, "locale": run.locale,
        "status": run.status, "case_version": run.case_version,
        "cancel_requested": run.cancel_requested, "stages": run.stages,
        "result": run.result, "error_code": run.error_code,
        "created_at": run.created_at.isoformat(),
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        "events": events,
    }


async def owned_run(
    case_id: uuid.UUID, run_id: uuid.UUID, principal: Principal, db: AsyncSession
) -> CaseRun:
    await FactService.get_authorized_case(case_id, principal, db)
    run = await db.scalar(select(CaseRun).where(
        CaseRun.id == run_id, CaseRun.case_id == case_id, CaseRun.principal_id == principal.id
    ))
    if not run:
        raise HTTPException(404, "Run not found")
    await recover_expired_run(run, db)
    return run


async def create_run(case_id: uuid.UUID, payload: RunRequest, principal: Principal, db: AsyncSession):
    case = await FactService.get_authorized_case(case_id, principal, db)
    if payload.expected_version is not None and payload.expected_version != case.row_version:
        raise HTTPException(409, 'Case changed. Reload before starting the next task.')
    if case.consent_status == "withdrawn":
        raise HTTPException(403, "Processing consent was withdrawn")
    active = await db.scalar(select(CaseRun).where(
        CaseRun.case_id == case.id, CaseRun.principal_id == principal.id,
        CaseRun.status.in_(["queued", "running"]),
    ))
    if active:
        await recover_expired_run(active, db)
    if active and active.status not in TERMINAL:
        raise HTTPException(409, "An operation is already running for this case")
    run = CaseRun(
        id=uuid.uuid4(), case_id=case.id, principal_id=principal.id,
        operation=payload.operation, locale=payload.locale,
        case_version=case.row_version, status="queued", stages=[], result={},
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


async def execute_run(run_id: uuid.UUID, factory: async_sessionmaker[AsyncSession]):
    """Bounded operations, real timings, and cancellation at durable stage boundaries.

    Model acknowledgements and cached readings are recorded separately. Retrieval
    uses lexical search; the development hash adapter is not E5 inference.
    """
    async with factory() as db:
        run = await db.get(CaseRun, run_id)
        if not run:
            return
        principal = await db.get(Principal, run.principal_id)
        if not principal:
            return

        async def checkpoint():
            await db.refresh(run, attribute_names=["cancel_requested"])
            if run.cancel_requested:
                raise asyncio.CancelledError()
            case = await FactService.get_authorized_case(run.case_id, principal, db)
            if case.consent_status == "withdrawn":
                raise PermissionError("Processing consent withdrawn")
            return case

        async def stage_start(key: str, method: str):
            await checkpoint()
            run.status = "running"
            run.stages = [*run.stages, {
                "stage_name": key, "status": "running", "method": method,
                "started_at": datetime.datetime.now(datetime.UTC).isoformat(),
                "duration_ms": None, "details": {},
            }]
            await db.commit()
            return time.perf_counter()

        async def stage_end(start: float, details: dict[str, Any]):
            stages = [dict(item) for item in run.stages]
            stages[-1].update({
                "status": "completed", "duration_ms": round((time.perf_counter() - start) * 1000),
                "finished_at": datetime.datetime.now(datetime.UTC).isoformat(), "details": details,
            })
            run.stages = stages
            await db.commit()

        try:
            case = await checkpoint()
            if run.operation == "resolve":
                started = await stage_start('case_understanding', 'bounded_situation_summary')
                external_consent = await db.scalar(select(Consent).where(
                    Consent.principal_id == principal.id, Consent.case_id == case.id,
                    Consent.purpose == 'external_ai_processing', Consent.withdrawn_at.is_(None),
                ).limit(1))
                understanding = await understand_situation(case.story_narrative or case.title, run.locale) if external_consent else {
                    'summary': (case.story_narrative or case.title)[:700],
                    'method': 'original_account', 'model_executed': False,
                }
                run.result = {'understanding': understanding}
                await stage_end(started, {'method': understanding['method'],
                                         'model_executed': understanding['model_executed'],
                                         'execution_receipt': understanding.get('execution_receipt')})
            if run.operation in {"extract", "resolve"}:
                started = await stage_start("text_extraction", "deterministic_pattern_extractor")
                proposals = CaseExtractor.propose(case.story_narrative or "")
                existing = list((await db.scalars(select(FactAssertion).where(
                    FactAssertion.case_id == case.id, FactAssertion.is_active.is_(True)
                ))).all())
                count = 0
                for proposal in proposals.proposals:
                    await checkpoint()
                    if any(item.field_name == proposal.field_name for item in existing):
                        continue
                    span = next((item for item in proposals.spans if item.span_id in proposal.span_ids), None)
                    await FactService.create_assertion(case.id, FactAssertionCreate(
                        field_name=proposal.field_name, field_type=proposal.field_type,
                        raw_value=proposal.original_text if proposal.field_type in {"money", "date"} else proposal.raw_value,
                        original_text=proposal.original_text, origin="user_narrative_extraction",
                        span_start=span.start_offset if span else None,
                        span_end=span.end_offset if span else None,
                    ), principal, db)
                    count += 1
                await stage_end(started, {"proposed_facts": count, "human_review_required": True})
                run.result = {**run.result, "proposed_facts": count, "next_view": "review"}
                if run.operation == 'extract':
                    run.status = "needs_review"
            if run.operation == 'resolve':
                started = await stage_start('evidence_review', 'native_document_parsing')
                accepted = list((await db.scalars(select(EvidenceItem).where(
                    EvidenceItem.case_id == case.id, EvidenceItem.principal_id == principal.id,
                    EvidenceItem.status == 'accepted',
                ).limit(20))).all())
                findings = []
                for evidence in accepted:
                    await checkpoint()
                    # Reuse a successful reading of these exact bytes. Besides saving
                    # provider calls, this keeps reviewed quote identities stable.
                    previous_runs = list((await db.scalars(select(CaseRun).where(
                        CaseRun.case_id == case.id, CaseRun.principal_id == principal.id,
                        CaseRun.id != run.id,
                    ).order_by(CaseRun.created_at.desc()).limit(20))).all())
                    cached = next(((old, source) for old in previous_runs
                        for source in old.result.get('readings', [])
                        if source.get('id') == str(evidence.id)
                        and source.get('sha256') == evidence.sha256_hash and source.get('text')
                        and source.get('method') != 'manual_required'), None)
                    reading = ({**cached[1], 'reused_from_run': str(cached[0].id)} if cached
                               else await read_evidence(evidence, bool(external_consent)))
                    await checkpoint()
                    await db.refresh(evidence)
                    if evidence.status != 'accepted':
                        continue  # A deletion during provider processing must not restore derivatives.
                    run.result = {**run.result, 'readings': [*run.result.get('readings', []), reading]}
                    await db.commit()
                    try:
                        data = get_storage_backend().read_accepted(evidence.accepted_path)
                        mime = evidence.detected_mime_type or evidence.declared_mime_type
                        parsed = DocumentParser.parse_pdf_bytes(evidence.id, data) if mime == 'application/pdf' else None
                        if not parsed:
                            findings.append({'id': str(evidence.id), 'filename': evidence.original_filename,
                                             'requires_review': True, 'method': 'original_file'})
                            continue
                        findings.append({'id': str(evidence.id), 'filename': evidence.original_filename,
                                         'text': parsed.full_text[:3000], 'requires_review': True,
                                         'method': 'native_pdf_text'})
                        # Reading a receipt does not establish that its payment belongs
                        # to this dispute. Only an explicit source review/link counts it.
                    except (OSError, ValueError):
                        findings.append({'id': str(evidence.id), 'filename': evidence.original_filename,
                                         'requires_review': True, 'method': 'unavailable'})
                run.result = {**run.result, 'evidence_findings': findings}
                await stage_end(started, {'files_reviewed': len(findings),
                                         'native_text_files': sum(f['method']=='native_pdf_text' for f in findings),
                                         'provider_calls': sum(bool(f.get('model_executed')) and not f.get('reused_from_run') for f in run.result.get('readings', [])),
                                         'cached_readings': sum(bool(f.get('reused_from_run')) for f in run.result.get('readings', [])),
                                         'providers': sorted({f['execution_receipt']['provider'] for f in run.result.get('readings', []) if f.get('execution_receipt') and not f.get('reused_from_run')}),
                                         'readable_records': sum(bool(f.get('text')) for f in run.result.get('readings', []))})
                started = await stage_start('payment_reconciliation', 'linked_receipt_comparison')
                reconciliation = await EvidenceService.reconcile_case_payments(case.id, principal, db)
                run.result = {**run.result, 'reconciliation': reconciliation.model_dump(mode='json')}
                await stage_end(started, {'status': reconciliation.status,
                                         'difference_minor_units': reconciliation.discrepancy_minor_units})
            if run.operation != 'extract':
                started = await stage_start("source_retrieval", "bm25_lexical_with_exact_lookup")
                retrieval = HybridRetriever().retrieve(
                    query=case.story_narrative or case.title,
                    date_context=case.incident_date, dense_enabled=False, top_k=5,
                )
                await stage_end(started, {
                    "retrieved_count": len(retrieval["results"]),
                    "citation_handles": [item["citation_handle"] for item in retrieval["results"]],
                    "dense_model_executed": False,
                })
                case = await checkpoint()
                started = await stage_start("procedural_assessment", "kleene_three_valued_policy")
                assessment = await ProceduralAssessmentEngine.assess_case(case, db)
                await stage_end(started, {
                    "routes_evaluated": len(assessment.routes),
                    "supported_routes": sum(route.status == "supported" for route in assessment.routes),
                    "question_pending": assessment.next_best_question is not None,
                })
                run.result = {**run.result, "next_view": "paths", "assessment": assessment.model_dump(mode="json")}
                if run.operation == "draft":
                    case = await checkpoint()
                    started = await stage_start("draft_preparation", "source_linked_document_templates")
                    doc = await load_document(case.id, principal, db, locale=run.locale)
                    await stage_end(started, {"sections": len(doc.sections), "is_submitted": False})
                    run.result = {**run.result, "next_view": "actions", "document": doc.model_dump(mode="json")}
                run.status = "completed"
                if run.operation == 'resolve':
                    run.status = 'needs_review'
                    run.result = {**run.result, 'next_view': 'review'}
            case = await checkpoint()
            run.case_version = case.row_version
        except asyncio.CancelledError:
            await db.rollback()
            await db.refresh(run)
            run.status = "cancelled"
        except Exception:
            logger.exception("Case operation failed: %s", run_id)
            await db.rollback()
            await db.refresh(run)
            run.status = "failed"
            run.error_code = "operation_failed"
        finally:
            run.finished_at = datetime.datetime.now(datetime.UTC)
            stages = [dict(item) for item in run.stages]
            for item in stages:
                if item["status"] == "running":
                    item["status"] = run.status
                    item["finished_at"] = run.finished_at.isoformat()
            run.stages = stages
            await db.commit()
