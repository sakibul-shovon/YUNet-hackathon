import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_principal, require_role
from app.identity.models import Principal
from app.knowledge.admin_service import AdminKnowledgeService
from app.knowledge.models import KnowledgeRelease, SourceProvision
from app.knowledge.reassessment_service import ReassessmentQueueService
from app.knowledge.schemas import (
    CandidateDiffOut,
    CaseReassessmentResult,
    KnowledgeReleaseOut,
    ManualImportRequest,
    ReassessmentQueueResult,
    ReleaseBuildRequest,
    ReleaseRollbackRequest,
    ReviewResultOut,
    ReviewSubmission,
    SourceCandidateOut,
    SourceHealthResponse,
    SourceProvisionOut,
    WatcherCheckRequest,
    WatcherCheckResponse,
)
from app.knowledge.watcher_service import OfficialSourceWatcher

router = APIRouter(tags=["Knowledge & Sources"])


# --- Public Knowledge Endpoints ---


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
            detail={
                "error": {
                    "code": "NO_ACTIVE_RELEASE",
                    "message": "No active knowledge release configured",
                }
            },
        )
    return KnowledgeReleaseOut.model_validate(active, from_attributes=True)


@router.get("/v1/knowledge/source-health", response_model=SourceHealthResponse)
async def get_source_health(
    db: AsyncSession = Depends(get_db_session),
):
    """Public transparency endpoint returning monitored source health and active release ID."""
    return await AdminKnowledgeService.get_source_health(db)


# --- Case Reassessment Endpoint (Owner Scoped) ---


@router.post("/v1/cases/{case_id}/reassess", response_model=CaseReassessmentResult)
async def reassess_case(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Owner scoped: re-evaluates case against active release and generates semantic decision diff (T39, T45)."""
    return await ReassessmentQueueService.reassess_case(case_id, principal, db)


# --- Privileged Reviewer & Publisher Endpoints ---


@router.post(
    "/v1/admin/watchers/check",
    response_model=WatcherCheckResponse,
)
async def run_watcher_check(
    req: WatcherCheckRequest,
    reviewer: Principal = Depends(require_role("reviewer")),
    db: AsyncSession = Depends(get_db_session),
):
    """Reviewer only: executes a monitored source check with SSRF and redirect protection (T42)."""
    res = await OfficialSourceWatcher.run_watcher_check(
        source_id=req.source_id,
        db=db,
        simulate_fixture=req.simulate_fixture,
    )
    return WatcherCheckResponse(
        source_id=res.source_id,
        target_url=res.target_url,
        status=res.status,
        change_type=res.change_type,
        raw_hash=res.raw_hash,
        clean_text_hash=res.clean_text_hash,
        quarantine_reason=res.quarantine_reason,
        error_message=res.error_message,
        candidate_id=res.candidate_id,
        fetched_at=res.fetched_at,
    )


@router.post(
    "/v1/admin/sources/manual-import",
    response_model=SourceCandidateOut,
    status_code=status.HTTP_201_CREATED,
)
async def manual_source_import(
    req: ManualImportRequest,
    reviewer: Principal = Depends(require_role("reviewer")),
    db: AsyncSession = Depends(get_db_session),
):
    """Reviewer only: manual-import fallback for offline or air-gapped updates (T42)."""
    candidate = await OfficialSourceWatcher.manual_import(
        family_slug=req.family_slug,
        title=req.title,
        text_content=req.text_content,
        issuer=req.issuer,
        document_type=req.document_type,
        publisher=reviewer,
        db=db,
        official_url=req.official_url,
        publication_date=req.publication_date,
        commencement_date=req.commencement_date,
    )
    return SourceCandidateOut.model_validate(candidate, from_attributes=True)


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


@router.get(
    "/v1/admin/source-candidates/{id}/diff",
    response_model=CandidateDiffOut,
    dependencies=[Depends(require_role("reviewer"))],
)
async def get_candidate_diff(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Reviewer only: section-aware diff and candidate impact proposal (T43)."""
    return await AdminKnowledgeService.get_candidate_diff(id, db)


@router.post(
    "/v1/admin/source-candidates/{id}/approve",
    response_model=ReviewResultOut,
)
async def approve_candidate(
    id: uuid.UUID,
    submission: ReviewSubmission,
    reviewer: Principal = Depends(require_role("reviewer")),
    db: AsyncSession = Depends(get_db_session),
):
    """Reviewer only: scoped human approval promoting candidate into approved SourceVersion (T44)."""
    return await AdminKnowledgeService.approve_candidate(id, reviewer, submission, db)


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
    """Reviewer only: records explicit named review scope and promotes candidate version to approved."""
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
    """Publisher only: constructs an immutable release manifest; rejects test_only rules (T18, T45)."""
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
    """Publisher only: performs atomic active release pointer swap (T45)."""
    return await AdminKnowledgeService.promote_release(id, publisher, db)


@router.post(
    "/v1/admin/releases/{id}/rollback",
    response_model=KnowledgeReleaseOut,
)
async def rollback_release(
    id: str,
    req: ReleaseRollbackRequest,
    publisher: Principal = Depends(require_role("publisher")),
    db: AsyncSession = Depends(get_db_session),
):
    """Publisher only: atomically rolls back active release to target approved release manifest (T45)."""
    return await AdminKnowledgeService.rollback_release(req.target_release_id, publisher, db)


@router.post(
    "/v1/admin/releases/{id}/disable",
    response_model=KnowledgeReleaseOut,
)
async def disable_release(
    id: str,
    operator: Principal = Depends(require_role("publisher")),
    db: AsyncSession = Depends(get_db_session),
):
    """Publisher only: disables active release in an emergency (T45)."""
    return await AdminKnowledgeService.disable_release(id, operator, db)


@router.post(
    "/v1/admin/releases/{id}/flag-impacted-cases",
    response_model=ReassessmentQueueResult,
)
async def flag_impacted_cases(
    id: str,
    publisher: Principal = Depends(require_role("publisher")),
    db: AsyncSession = Depends(get_db_session),
):
    """Publisher only: scans open cases and flags only those dependent on modified rules (T39, T45)."""
    return await ReassessmentQueueService.detect_and_flag_impacted_cases(id, db)
