import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import require_role
from app.identity.models import Principal
from app.knowledge.admin_service import AdminKnowledgeService
from app.knowledge.models import KnowledgeRelease, SourceProvision
from app.knowledge.schemas import (
    KnowledgeReleaseOut,
    ReleaseBuildRequest,
    ReviewResultOut,
    ReviewSubmission,
    SourceCandidateOut,
    SourceProvisionOut,
)

router = APIRouter(tags=["Knowledge & Sources"])


@router.get("/v1/sources/{id}", response_model=SourceProvisionOut)
async def get_source_provision(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves an approved public statutory or procedural provision."""
    stmt = select(SourceProvision).where(SourceProvision.id == id)
    res = await db.execute(stmt)
    prov = res.scalar_one_or_none()
    if not prov:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PROVISION_NOT_FOUND", "message": "Provision not found"}},
        )
    return SourceProvisionOut.model_validate(prov, from_attributes=True)


@router.get("/v1/knowledge/release", response_model=KnowledgeReleaseOut)
async def get_active_release(
    db: AsyncSession = Depends(get_db_session),
):
    """Returns metadata and manifest hash for the active compatible knowledge release."""
    stmt = select(KnowledgeRelease).where(KnowledgeRelease.is_active.is_(True))
    res = await db.execute(stmt)
    active = res.scalar_one_or_none()
    if not active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NO_ACTIVE_RELEASE", "message": "No active knowledge release configured"}},
        )
    return KnowledgeReleaseOut.model_validate(active, from_attributes=True)


# --- Privileged Reviewer & Publisher Endpoints ---


@router.get(
    "/v1/admin/source-candidates",
    response_model=list[SourceCandidateOut],
    dependencies=[Depends(require_role("reviewer"))],
)
async def list_source_candidates(
    db: AsyncSession = Depends(get_db_session),
):
    """Reviewer only: inspect discovered and unapproved candidate source versions."""
    return await AdminKnowledgeService.list_source_candidates(db)


@router.post(
    "/v1/admin/source-versions/{id}/review",
    response_model=ReviewResultOut,
)
async def review_source_version(
    id: uuid.UUID,
    submission: ReviewSubmission,
    reviewer: Principal = Depends(require_role("reviewer")),
    db: AsyncSession = Depends(get_db_session),
):
    """Reviewer only: records explicit named review scope and promotes candidate to approved."""
    return await AdminKnowledgeService.review_source_version(id, reviewer, submission, db)


@router.post(
    "/v1/admin/releases/build",
    response_model=KnowledgeReleaseOut,
    status_code=status.HTTP_201_CREATED,
)
async def build_release(
    req: ReleaseBuildRequest,
    publisher: Principal = Depends(require_role("publisher")),
    db: AsyncSession = Depends(get_db_session),
):
    """Publisher only: constructs an immutable release manifest; rejects test_only rules (T18)."""
    return await AdminKnowledgeService.build_release(req, publisher, db)


@router.post(
    "/v1/admin/releases/{id}/promote",
    response_model=KnowledgeReleaseOut,
)
async def promote_release(
    id: str,
    publisher: Principal = Depends(require_role("publisher")),
    db: AsyncSession = Depends(get_db_session),
):
    """Publisher only: performs atomic active release pointer swap."""
    return await AdminKnowledgeService.promote_release(id, publisher, db)


@router.post(
    "/v1/admin/releases/{id}/disable",
    response_model=KnowledgeReleaseOut,
)
async def disable_release(
    id: str,
    operator: Principal = Depends(require_role("publisher")),
    db: AsyncSession = Depends(get_db_session),
):
    """Publisher only: disables active release in an emergency."""
    return await AdminKnowledgeService.disable_release(id, operator, db)
