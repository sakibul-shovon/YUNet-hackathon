import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.cases.schemas import CaseCreate, CaseEventOut, CaseListOut, CaseOut, CaseUpdate
from app.cases.service import CaseService
from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.identity.models import Principal

router = APIRouter(tags=["Cases"])


@router.post("/v1/cases", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
async def create_case(
    data: CaseCreate,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Creates a new case owned by the authenticated principal."""
    return await CaseService.create_case(principal, data, db)


@router.get("/v1/cases", response_model=CaseListOut)
async def list_cases(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists non-deleted cases belonging to the calling principal."""
    return await CaseService.get_cases(principal, db, limit=limit, offset=offset)


@router.get("/v1/cases/{id}", response_model=CaseOut)
async def get_case(
    id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Fetches case details with strict tenant isolation (returns 404 for foreign cases)."""
    return await CaseService.get_case_by_id(id, principal, db)


@router.patch("/v1/cases/{id}", response_model=CaseOut)
async def update_case(
    id: uuid.UUID,
    data: CaseUpdate,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Updates case fields with optimistic concurrency check (returns 409 on version conflict)."""
    return await CaseService.update_case(id, principal, data, db)


@router.delete("/v1/cases/{id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_case(
    id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Revokes access and queues case for complete asynchronous deletion."""
    return await CaseService.delete_case(id, principal, db)


@router.get("/v1/cases/{id}/activity", response_model=list[CaseEventOut])
async def get_case_activity(
    id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves chronological activity log and history for an authorized case."""
    return await CaseService.get_case_events(id, principal, db)
