import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.cases.issue_service import (
    IssueCreate,
    IssueMergeRequest,
    IssueReviewRequest,
    IssueService,
    IssueSplitRequest,
    IssueTrackOut,
    MultiIssueAssessmentOut,
)
from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.identity.models import Principal

router = APIRouter(tags=["Case Issue Tracks"])


@router.get(
    "/v1/cases/{case_id}/issues",
    response_model=list[IssueTrackOut],
)
async def list_case_issues(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P08.2: Lists all active and historical issue tracks for a case."""
    return await IssueService.list_issues(case_id, principal, db)


@router.post(
    "/v1/cases/{case_id}/issues",
    response_model=IssueTrackOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_case_issue(
    case_id: uuid.UUID,
    payload: IssueCreate,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P08.2: Creates a new issue track; rejects brand-only false tracks without statutory basis."""
    return await IssueService.create_issue(case_id, payload, principal, db)


@router.post(
    "/v1/cases/{case_id}/issues/split",
    response_model=list[IssueTrackOut],
    status_code=status.HTTP_200_OK,
)
async def split_case_issue(
    case_id: uuid.UUID,
    payload: IssueSplitRequest,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P08.2: Splits an issue track into distinct sub-issues (e.g. non-delivery of Item A vs defect in Item B)."""
    return await IssueService.split_issue(case_id, payload, principal, db)


@router.post(
    "/v1/cases/{case_id}/issues/merge",
    response_model=IssueTrackOut,
    status_code=status.HTTP_200_OK,
)
async def merge_case_issues(
    case_id: uuid.UUID,
    payload: IssueMergeRequest,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P08.2: Merges multiple related issues into one consolidated issue track."""
    return await IssueService.merge_issues(case_id, payload, principal, db)


@router.patch(
    "/v1/cases/{case_id}/issues/{issue_id}",
    response_model=IssueTrackOut,
)
async def review_case_issue(
    case_id: uuid.UUID,
    issue_id: uuid.UUID,
    payload: IssueReviewRequest,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P08.2: Reviews or corrects an issue track (accepted, corrected, rejected, unsure)."""
    return await IssueService.review_issue(case_id, issue_id, payload, principal, db)


@router.get(
    "/v1/cases/{case_id}/issues/assessment",
    response_model=MultiIssueAssessmentOut,
)
async def get_multi_issue_assessment(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P08.2: Evaluates each active issue track independently with distinct remedies and routes."""
    return await IssueService.assess_multi_issues(case_id, principal, db)
