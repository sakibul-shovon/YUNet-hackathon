import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.facts.schemas import (
    FactAssertionCreate,
    FactAssertionOut,
    FactReviewOut,
    FactReviewSubmission,
)
from app.facts.service import FactService
from app.identity.models import Principal

router = APIRouter(tags=["Case Facts & Normalization"])


@router.get(
    "/v1/cases/{case_id}/facts",
    response_model=list[FactAssertionOut],
)
async def list_case_facts(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves all active factual assertions for the authorized case."""
    return await FactService.get_assertions(case_id, principal, db)


@router.post(
    "/v1/cases/{case_id}/facts",
    response_model=FactAssertionOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_case_fact(
    case_id: uuid.UUID,
    payload: FactAssertionCreate,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Creates a normalized factual assertion (money/date/boolean/string) bound to the case."""
    return await FactService.create_assertion(case_id, payload, principal, db)


@router.post(
    "/v1/cases/{case_id}/facts/{assertion_id}/review",
    response_model=FactReviewOut,
)
async def review_case_fact(
    case_id: uuid.UUID,
    assertion_id: uuid.UUID,
    submission: FactReviewSubmission,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Submits user review (accept/correct/reject/unsure) for an extracted or asserted fact."""
    return await FactService.review_assertion(case_id, assertion_id, submission, principal, db)
