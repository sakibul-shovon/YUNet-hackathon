import uuid

from fastapi import (
    APIRouter,
    Depends,
    Header,
    Query,
    Request,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.evidence.document_parser import DocumentParseResult
from app.evidence.schemas import (
    EvidenceItemOut,
    EvidenceSpanLinkCreate,
    EvidenceSpanLinkOut,
    PaymentReconciliationResult,
    UploadIntentCreate,
    UploadIntentOut,
)
from app.evidence.service import EvidenceService
from app.identity.models import Principal

router = APIRouter(tags=["Evidence & Upload Vault"])


@router.post(
    "/v1/uploads/init",
    response_model=UploadIntentOut,
    status_code=status.HTTP_201_CREATED,
)
async def init_upload(
    payload: UploadIntentCreate,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T10/T11: Checks case ownership and quota, reserves quota, and generates one-path signed upload intent."""
    return await EvidenceService.create_upload_intent(payload, principal, db)


@router.put(
    "/v1/uploads/{intent_id}/raw",
    status_code=status.HTTP_200_OK,
)
async def upload_raw_quarantine_data(
    intent_id: uuid.UUID,
    request: Request,
    token: str = Query(..., description="One-path upload token from init"),
    db: AsyncSession = Depends(get_db_session),
):
    """Direct-to-quarantine payload destination using the one-path upload token."""
    body_bytes = await request.body()
    await EvidenceService.receive_quarantine_data(intent_id, token, body_bytes, db)
    return {"status": "quarantined", "intent_id": intent_id}


@router.post(
    "/v1/uploads/{intent_id}/complete",
    response_model=EvidenceItemOut,
    status_code=status.HTTP_200_OK,
)
async def complete_upload(
    intent_id: uuid.UUID,
    x_simulate_scanner_outage: bool = Header(False, alias="X-Simulate-Scanner-Outage"),
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T10, T11, T12: Consumes intent once, validates server actual bytes, probes limits/malware, and moves to accepted storage."""
    return await EvidenceService.complete_upload(
        intent_id, principal, db, simulate_scanner_outage=x_simulate_scanner_outage
    )


@router.get(
    "/v1/cases/{case_id}/evidence",
    response_model=list[EvidenceItemOut],
    status_code=status.HTTP_200_OK,
)
async def list_case_evidence(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists evidence items for the authorized case owner."""
    return await EvidenceService.list_case_evidence(case_id, principal, db)


@router.get(
    "/v1/cases/{case_id}/evidence/reconciliation",
    response_model=PaymentReconciliationResult,
    status_code=status.HTTP_200_OK,
)
async def get_payment_reconciliation(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T21: Reconciles asserted transaction amount with linked evidence receipts, prompts for clarifications."""
    return await EvidenceService.reconcile_case_payments(case_id, principal, db)


@router.get(
    "/v1/cases/{case_id}/evidence/{evidence_id}",
    response_model=EvidenceItemOut,
    status_code=status.HTTP_200_OK,
)
async def get_case_evidence_item(
    case_id: uuid.UUID,
    evidence_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T01: Returns evidence item metadata for authorized case owner."""
    return await EvidenceService.get_evidence_item(case_id, evidence_id, principal, db)


@router.get(
    "/v1/cases/{case_id}/evidence/{evidence_id}/preview",
    status_code=status.HTTP_200_OK,
)
async def get_evidence_preview(
    case_id: uuid.UUID,
    evidence_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T15: Bounded private preview with owner authorization and cache exclusion. Never returns public bucket URL."""
    data, media_type, filename = await EvidenceService.get_evidence_preview_bytes(
        case_id, evidence_id, principal, db
    )
    headers = {
        "Cache-Control": "private, no-store, max-age=0, must-revalidate",
        "Pragma": "no-cache",
        "X-Content-Type-Options": "nosniff",
        "Content-Disposition": f'inline; filename="{filename}"',
    }
    return Response(content=data, media_type=media_type, headers=headers)


@router.post(
    "/v1/cases/{case_id}/evidence/{evidence_id}/spans",
    response_model=EvidenceSpanLinkOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_evidence_span_link(
    case_id: uuid.UUID,
    evidence_id: uuid.UUID,
    payload: EvidenceSpanLinkCreate,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T14, T15: Links evidence region or page to an asserted case fact."""
    return await EvidenceService.create_span_link(case_id, evidence_id, payload, principal, db)


@router.get(
    "/v1/cases/{case_id}/evidence/{evidence_id}/spans",
    response_model=list[EvidenceSpanLinkOut],
    status_code=status.HTTP_200_OK,
)
async def list_evidence_spans(
    case_id: uuid.UUID,
    evidence_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T14, T15: Lists linked spans for an evidence item."""
    return await EvidenceService.get_evidence_spans(case_id, evidence_id, principal, db)


@router.delete(
    "/v1/cases/{case_id}/evidence/{evidence_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_case_evidence(
    case_id: uuid.UUID,
    evidence_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T36: Cascading removal and invalidation of evidence, private files, linked spans and derived assertions."""
    return await EvidenceService.delete_evidence_item(case_id, evidence_id, principal, db)


@router.get(
    "/v1/cases/{case_id}/evidence/{evidence_id}/regions",
    response_model=DocumentParseResult,
    status_code=status.HTTP_200_OK,
)
async def get_evidence_regions(
    case_id: uuid.UUID,
    evidence_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T13, T14: Returns parsed document regions with normalized bounding boxes and quality flags."""
    return await EvidenceService.get_evidence_regions(case_id, evidence_id, principal, db)


@router.post(
    "/v1/uploads/sweep",
    status_code=status.HTTP_200_OK,
)
async def sweep_expired_uploads(
    db: AsyncSession = Depends(get_db_session),
):
    """T11: Sweeps expired upload tokens, releases quota reservations, and cleans up quarantine."""
    swept_count = await EvidenceService.sweep_expired_intents(db)
    return {"swept_count": swept_count}
