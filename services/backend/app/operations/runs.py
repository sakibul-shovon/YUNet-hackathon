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

from app.actions.document_ast import DocumentASTService
from app.extraction.adapter import CaseExtractor
from app.facts.models import FactAssertion
from app.facts.schemas import FactAssertionCreate
from app.facts.service import FactService
from app.identity.models import Principal
from app.operations.models import CaseRun
from app.policy.engine import ProceduralAssessmentEngine
from app.retrieval.hybrid_retriever import HybridRetriever

logger = logging.getLogger(__name__)
TERMINAL = {"completed", "needs_review", "cancelled", "failed"}


class RunRequest(BaseModel):
    operation: Literal["extract", "assess", "draft"] = "assess"
    locale: Literal["en", "bn"] = "en"


def serialize_run(run: CaseRun) -> dict[str, Any]:
    return {
        "id": str(run.id), "case_id": str(run.case_id), "operation": run.operation,
        "status": run.status, "case_version": run.case_version,
        "cancel_requested": run.cancel_requested, "stages": run.stages,
        "result": run.result, "error_code": run.error_code,
        "created_at": run.created_at.isoformat(),
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
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
    return run


async def create_run(case_id: uuid.UUID, payload: RunRequest, principal: Principal, db: AsyncSession):
    case = await FactService.get_authorized_case(case_id, principal, db)
    if case.consent_status == "withdrawn":
        raise HTTPException(403, "Processing consent was withdrawn")
    active = await db.scalar(select(CaseRun).where(
        CaseRun.case_id == case.id, CaseRun.principal_id == principal.id,
        CaseRun.status.in_(["queued", "running"]),
    ))
    if active:
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

    No model-provider execution is claimed. The retrieval stage deliberately uses
    lexical search; the development hash adapter is not advertised as E5 inference.
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
            if run.operation == "extract":
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
                        raw_value=proposal.original_text if proposal.field_type == "money" else proposal.raw_value,
                        original_text=proposal.original_text, origin="user_narrative_extraction",
                        span_start=span.start_offset if span else None,
                        span_end=span.end_offset if span else None,
                    ), principal, db)
                    count += 1
                await stage_end(started, {"proposed_facts": count, "human_review_required": True})
                run.result = {"proposed_facts": count, "next_view": "review"}
                run.status = "needs_review"
            else:
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
                run.result = {"next_view": "paths", "assessment": assessment.model_dump(mode="json")}
                if run.operation == "draft":
                    case = await checkpoint()
                    started = await stage_start("draft_preparation", "source_linked_document_templates")
                    facts = list((await db.scalars(select(FactAssertion).where(
                        FactAssertion.case_id == case.id, FactAssertion.is_active.is_(True)
                    ))).all())
                    normalized = ProceduralAssessmentEngine.extract_facts_from_db_records(facts, case)
                    doc = DocumentASTService.generate_document_ast(case, normalized, facts, locale=run.locale)
                    await stage_end(started, {"sections": len(doc.sections), "is_submitted": False})
                    run.result = {**run.result, "next_view": "actions", "document": doc.model_dump(mode="json")}
                run.status = "completed"
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
