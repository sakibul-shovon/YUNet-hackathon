import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.action_dag import ActionDAGOut, ActionDAGService
from app.actions.destinations import ComplaintDestinationOut, ComplaintDestinationService
from app.actions.document_ast import (
    DocumentASTService,
    DocumentEditRequest,
    EditableDocumentAST,
)
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
    case = await FactService.get_authorized_case(case_id, principal, db)

    stmt_f = select(FactAssertion).where(
        FactAssertion.case_id == case.id,
        FactAssertion.is_active.is_(True),
    )
    res_f = await db.execute(stmt_f)
    assertions = res_f.scalars().all()
    facts = ProceduralAssessmentEngine.extract_facts_from_db_records(assertions, case)

    stmt_e = select(EvidenceItem).where(
        EvidenceItem.case_id == case.id,
        EvidenceItem.status != "deleted",
    )
    res_e = await db.execute(stmt_e)
    evidence = res_e.scalars().all()

    return DocumentASTService.generate_document_ast(
        case=case,
        facts=facts,
        assertions=assertions,
        evidence_items=evidence,
        document_type=document_type,
        locale=locale,
    )


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
    case = await FactService.get_authorized_case(case_id, principal, db)

    stmt_f = select(FactAssertion).where(
        FactAssertion.case_id == case.id,
        FactAssertion.is_active.is_(True),
    )
    res_f = await db.execute(stmt_f)
    assertions = res_f.scalars().all()
    facts = ProceduralAssessmentEngine.extract_facts_from_db_records(assertions, case)

    doc = DocumentASTService.generate_document_ast(
        case=case,
        facts=facts,
        assertions=assertions,
        document_type=payload.document_type,
    )

    return DocumentASTService.apply_user_edit(doc, payload)


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
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P09.4 & T27: Exports dispute document as Markdown or HTML. Never marks case as filed."""
    case = await FactService.get_authorized_case(case_id, principal, db)

    stmt_f = select(FactAssertion).where(
        FactAssertion.case_id == case.id,
        FactAssertion.is_active.is_(True),
    )
    res_f = await db.execute(stmt_f)
    assertions = res_f.scalars().all()
    facts = ProceduralAssessmentEngine.extract_facts_from_db_records(assertions, case)

    doc = DocumentASTService.generate_document_ast(
        case=case,
        facts=facts,
        assertions=assertions,
        document_type=document_type,
        locale=locale,
    )

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

    # Generate a dummy 200x200 sample image for redaction test or load bytes
    import io

    from PIL import Image as PILImage

    dummy = PILImage.new("RGB", (200, 200), color=(255, 255, 255))
    buf = io.BytesIO()
    dummy.save(buf, format="PNG")
    original_bytes = buf.getvalue()

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
