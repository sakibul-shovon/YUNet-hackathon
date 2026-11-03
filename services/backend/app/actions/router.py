import io
import uuid
import zipfile

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.actions.action_dag import ActionDAGOut, ActionDAGService
from app.actions.destinations import ComplaintDestinationOut, ComplaintDestinationService
from app.actions.document_ast import (
    DocumentASTService,
    DocumentEditRequest,
    EditableDocumentAST,
)
from app.actions.document_store import PreparedDocument, load_document, save_document
from app.actions.draft_generator import DraftRequestGenerator, DraftRequestOut
from app.actions.export_service import (
    CaseExportOut,
    ExportService,
    RasterRedactionRequest,
)
from app.actions.portal_field_maps import PortalFieldMapOut, PortalFieldMapService
from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.evidence.models import EvidenceItem
from app.facts.models import FactAssertion
from app.facts.service import FactService
from app.identity.models import Principal
from app.policy.engine import ProceduralAssessmentEngine

router = APIRouter(tags=["Case Actions, Documents & Filing Companion"])


@router.get(
    "/v1/cases/{case_id}/actions/dag",
    response_model=ActionDAGOut,
)
async def get_case_action_dag(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P09.1: Returns remedy and stage-aware action DAG with dependency and blocking explanations."""
    return await ActionDAGService.build_action_dag(case_id, principal, db)


@router.get(
    "/v1/cases/{case_id}/documents/ast",
    response_model=EditableDocumentAST,
)
async def get_editable_document_ast(
    case_id: uuid.UUID,
    document_type: str = Query("dncrp_ccms_complaint"),
    locale: str = Query("en", pattern="^(en|bn)$"),
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P09.2: Generates editable document AST with sentence source mapping and fact/allegation tags."""
    return await load_document(case_id, principal, db, document_type, locale)


@router.post(
    "/v1/cases/{case_id}/documents/edit",
    response_model=EditableDocumentAST,
)
async def edit_document_ast_sentence(
    case_id: uuid.UUID,
    payload: DocumentEditRequest,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P09.2 & T29: Applies user edit to document AST; marks statement as user_allegation."""
    doc = await load_document(case_id, principal, db, payload.document_type, payload.locale)
    if payload.expected_revision is not None and doc.revision != payload.expected_revision:
        raise HTTPException(409, "The document changed. Reload before editing.")
    revised = DocumentASTService.apply_user_edit(doc.model_copy(deep=True), payload)
    revised.document_id = uuid.uuid4()
    revised.revision = doc.revision + 1
    await save_document(revised, principal.id, db)
    return revised


@router.get(
    "/v1/cases/{case_id}/portals/{portal_id}/fields",
    response_model=PortalFieldMapOut,
)
async def get_portal_field_map(
    case_id: uuid.UUID,
    portal_id: str,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P09.3 & T33: Returns versioned official portal field map with per-field copy data."""
    case = await FactService.get_authorized_case(case_id, principal, db)

    stmt_f = select(FactAssertion).where(
        FactAssertion.case_id == case.id,
        FactAssertion.is_active.is_(True),
    )
    res_f = await db.execute(stmt_f)
    assertions = res_f.scalars().all()
    facts = ProceduralAssessmentEngine.extract_facts_from_db_records(assertions, case)

    case_data = {
        "merchant_name": case.merchant_name,
        "story_narrative": case.story_narrative,
        "desired_outcomes": case.desired_outcomes,
        "incident_date": case.incident_date,
    }

    return PortalFieldMapService.get_field_map(portal_id, case_data, facts)


@router.post(
    "/v1/cases/{case_id}/export/{format_type}",
    response_model=CaseExportOut,
)
async def export_case_document(
    case_id: uuid.UUID,
    format_type: str,
    locale: str = Query("en", pattern="^(en|bn)$"),
    document_type: str = Query("dncrp_ccms_complaint"),
    include_evidence_index: bool = Query(True),
    include_originals: bool = Query(False),
    evidence_ids: list[uuid.UUID] = Query(default=[]),
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Exports a reviewed preparation copy. Never marks a case as filed."""
    doc = await load_document(case_id, principal, db, document_type, locale)
    doc = doc.model_copy(deep=True)
    if not include_evidence_index:
        doc.evidence_index = []
    if format_type in {"pdf", "zip"}:
        from app.actions.pdf_export import render_pdf
        pdf_bytes = await run_in_threadpool(render_pdf, doc)
        if format_type == "pdf":
            return Response(pdf_bytes, media_type="application/pdf", headers={
                "Content-Disposition": 'attachment; filename="Ebarki-draft.pdf"',
                "Cache-Control": "private, no-store",
            })
        selected = []
        if include_originals and evidence_ids:
            selected = list((await db.scalars(select(EvidenceItem).where(
                EvidenceItem.case_id == case_id, EvidenceItem.principal_id == principal.id,
                EvidenceItem.id.in_(evidence_ids), EvidenceItem.status == "accepted",
            ))).all())
            if len(selected) != len(set(evidence_ids)):
                raise HTTPException(404, "An attachment is unavailable")
            if sum(item.byte_size for item in selected) > 100 * 1024 * 1024:
                raise HTTPException(413, "Selected files exceed the 100 MB export limit")
        from app.evidence.storage import get_storage_backend
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("Ebarki-draft.pdf", pdf_bytes)
            archive.writestr("Ebarki-draft.md", ExportService.export_as_markdown(doc).content)
            for item in selected:
                name = item.original_filename.replace("\\", "/").split("/")[-1]
                name = "".join(c for c in name if c.isalnum() or c in " ._-").strip(" .") or "attachment"
                try:
                    content = get_storage_backend().read_accepted(item.accepted_path)
                except (OSError, ValueError):
                    raise HTTPException(409, "An original file is no longer available")
                archive.writestr(f"attachments/{item.id}_{name}", content)
        return Response(buffer.getvalue(), media_type="application/zip", headers={
            "Content-Disposition": 'attachment; filename="Ebarki-preparation.zip"',
            "Cache-Control": "private, no-store",
        })

    if format_type == "markdown":
        return ExportService.export_as_markdown(doc)
    elif format_type == "html":
        return ExportService.export_as_html(doc)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported export format '{format_type}'. Use 'markdown' or 'html'.",
        )


@router.post(
    "/v1/cases/{case_id}/evidence/{evidence_id}/redact",
)
async def redact_evidence_attachment(
    case_id: uuid.UUID,
    evidence_id: uuid.UUID,
    payload: RasterRedactionRequest,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P09.5 & T35: True raster redaction permanently blacking out sensitive pixels in memory."""
    case = await FactService.get_authorized_case(case_id, principal, db)

    stmt = select(EvidenceItem).where(
        EvidenceItem.id == evidence_id,
        EvidenceItem.case_id == case.id,
        EvidenceItem.status != "deleted",
    )
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evidence item not found."
        )

    if not item.accepted_path or not (item.detected_mime_type or "").startswith("image/"):
        raise HTTPException(415, "Raster redaction requires an accepted image")
    from app.evidence.storage import get_storage_backend
    original_bytes = get_storage_backend().read_accepted(item.accepted_path)

    redacted_bytes = ExportService.apply_raster_redaction(original_bytes, payload.bounding_boxes)

    return Response(content=redacted_bytes, media_type="image/png")


@router.get(
    "/v1/actions/destinations",
    response_model=list[ComplaintDestinationOut],
)
async def list_complaint_destinations():
    """P09.7 & T54: Lists official complaint destinations with link health and verified fallbacks."""
    return ComplaintDestinationService.list_destinations()


@router.get(
    "/v1/actions/destinations/{destination_id}",
    response_model=ComplaintDestinationOut,
)
async def get_complaint_destination(destination_id: str):
    """P09.7 & T54: Returns details for an official complaint destination."""
    return ComplaintDestinationService.get_destination(destination_id)


@router.get(
    "/v1/cases/{case_id}/draft",
    response_model=DraftRequestOut,
)
async def get_case_draft_request(
    case_id: uuid.UUID,
    locale: str = Query("en", pattern="^(en|bn)$"),
    remedy: str = Query("full_refund"),
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T26: Generates a respectful, legally grounded, unsubmitted dispute request draft."""
    case = await FactService.get_authorized_case(case_id, principal, db)

    stmt = select(FactAssertion).where(
        FactAssertion.case_id == case.id,
        FactAssertion.is_active.is_(True),
    )
    res = await db.execute(stmt)
    assertions = res.scalars().all()

    facts_dict = {}
    for a in assertions:
        if a.field_type == "money" and isinstance(a.typed_value, dict):
            facts_dict[a.field_name] = a.typed_value.get("minor_units")
        elif a.field_type == "date" and isinstance(a.typed_value, dict):
            facts_dict[a.field_name] = a.typed_value.get("date")
        else:
            facts_dict[a.field_name] = a.typed_value

    effective_remedy = remedy
    if case.desired_outcomes and len(case.desired_outcomes) > 0:
        effective_remedy = case.desired_outcomes[0]

    return DraftRequestGenerator.generate_draft(
        case_title=case.title,
        merchant_name=case.merchant_name,
        facts=facts_dict,
        locale=locale,
        remedy=effective_remedy,
    )


@router.get("/v1/cases/{case_id}/documents/history")
async def document_history(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    await FactService.get_authorized_case(case_id, principal, db)
    rows = await db.scalars(select(PreparedDocument).where(
        PreparedDocument.case_id == case_id, PreparedDocument.principal_id == principal.id,
    ).order_by(PreparedDocument.created_at.desc()).limit(50))
    return [{"id": str(row.id), "case_version": row.case_version,
             "revision": row.revision, "locale": row.locale,
             "document_type": row.document_type, "created_at": row.created_at.isoformat()}
            for row in rows]


@router.get("/v1/cases/{case_id}/documents/versions/{document_id}")
async def document_version(
    case_id: uuid.UUID, document_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    return await load_document(case_id, principal, db, document_id=document_id)
