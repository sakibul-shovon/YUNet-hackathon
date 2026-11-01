import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.facts.service import FactService
from app.identity.models import Principal
from app.policy.engine import ProceduralAssessmentEngine, ProceduralAssessmentOut

router = APIRouter(tags=["Case Procedural Assessment"])


@router.get(
    "/v1/cases/{case_id}/assessment",
    response_model=ProceduralAssessmentOut,
)
async def get_case_assessment(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T19/T20: Computes deterministic procedural assessment, condition traces, NBQ, and next actions."""
    case = await FactService.get_authorized_case(case_id, principal, db)
    return await ProceduralAssessmentEngine.assess_case(case, db)


@router.post(
    "/v1/cases/{case_id}/assess",
    response_model=ProceduralAssessmentOut,
)
async def trigger_case_assessment(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Recomputes procedural assessment against the latest active facts."""
    case = await FactService.get_authorized_case(case_id, principal, db)
    return await ProceduralAssessmentEngine.assess_case(case, db)
