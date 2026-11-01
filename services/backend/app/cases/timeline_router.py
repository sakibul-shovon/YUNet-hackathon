import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.cases.timeline_service import (
    CaseSnapshotOut,
    ExternalUpdateCreate,
    ReminderCreate,
    ReminderOut,
    TimelineEventOut,
    TimelineService,
)
from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.identity.models import Principal

router = APIRouter(tags=["Case Living Timeline, Updates, Diff & Reminders"])


@router.post(
    "/v1/cases/{case_id}/activity/updates",
    response_model=TimelineEventOut,
    status_code=status.HTTP_201_CREATED,
)
async def record_case_external_update(
    case_id: uuid.UUID,
    payload: ExternalUpdateCreate,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P10.1 & T38: Records user-reported external milestone, update, or response. Emits semantic decision diff."""
    return await TimelineService.record_user_update(case_id, payload, principal, db)


@router.get(
    "/v1/cases/{case_id}/activity/timeline",
    response_model=list[TimelineEventOut],
)
async def get_case_timeline(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P10.1 & T38: Returns chronological case activity timeline with origin visibility."""
    return await TimelineService.get_case_timeline(case_id, principal, db)


@router.get(
    "/v1/cases/{case_id}/snapshots",
    response_model=list[CaseSnapshotOut],
)
async def list_case_snapshots(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P10.2 & T39: Lists versioned immutable snapshots for the case."""
    return await TimelineService.get_case_snapshots(case_id, principal, db)


@router.post(
    "/v1/cases/{case_id}/reminders",
    response_model=ReminderOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_case_reminder(
    case_id: uuid.UUID,
    payload: ReminderCreate,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P10.4 & T40: Sets personal reminder with user-selected follow-up time."""
    return await TimelineService.create_reminder(case_id, payload, principal, db)


@router.get(
    "/v1/cases/{case_id}/reminders",
    response_model=list[ReminderOut],
)
async def list_case_reminders(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P10.4 & T40: Lists active reminders for a case."""
    return await TimelineService.list_reminders(case_id, principal, db)


@router.delete(
    "/v1/cases/{case_id}/reminders/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_case_reminder(
    case_id: uuid.UUID,
    reminder_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P10.4 & T40: Cancels a personal reminder."""
    await TimelineService.cancel_reminder(case_id, reminder_id, principal, db)

