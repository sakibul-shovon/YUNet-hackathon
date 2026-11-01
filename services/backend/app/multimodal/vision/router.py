import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.evidence.models import EvidenceItem
from app.evidence.storage import get_storage_backend
from app.facts.service import FactService
from app.identity.models import Principal
from app.multimodal.vision.schemas import ScreenshotAnalysisResult
from app.multimodal.vision.screenshot_adapter import ScreenshotAdapter

router = APIRouter(tags=["Multimodal Vision & Screenshots"])


@router.post(
    "/v1/cases/{case_id}/evidence/{evidence_id}/analyze-layout",
    response_model=ScreenshotAnalysisResult,
    status_code=status.HTTP_200_OK,
)
async def analyze_screenshot_layout(
    case_id: uuid.UUID,
    evidence_id: uuid.UUID,
    ocr_hint: str = "",
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T23: Inspects chat/receipt screenshot layout, detects theme, preserves bubble uncertainty, and flags OCR disagreements."""
    await FactService.get_authorized_case(case_id, principal, db)

    stmt = select(EvidenceItem).where(
        EvidenceItem.id == evidence_id,
        EvidenceItem.case_id == case_id,
        EvidenceItem.status == "accepted",
    )
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item or not item.accepted_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accepted evidence item not found.",
        )

    storage = get_storage_backend()
    data = storage.read_accepted(item.accepted_path)

    return ScreenshotAdapter.analyze_image_bytes(
        evidence_id=evidence_id,
        case_id=case_id,
        image_bytes=data,
        ocr_extracted_text=ocr_hint,
    )

