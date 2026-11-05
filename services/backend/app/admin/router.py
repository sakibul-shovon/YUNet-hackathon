import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.service import AdminService
from app.core.database import get_db_session
from app.core.security import require_role
from app.identity.models import Principal
from app.knowledge.admin_service import AdminKnowledgeService

router = APIRouter(prefix="/v1/admin", tags=["Super Admin & Platform Operations"])

# --- Request Schemas ---
class CaseOverrideRequest(BaseModel):
    new_status: Literal['active', 'resolved', 'escalated', 'dismissed', 'fraudulent']
    admin_notes: str = Field("", description="Reason and administrative justification")

class UserRoleUpdateRequest(BaseModel):
    roles: list[Literal['admin', 'reviewer', 'publisher', 'operator', 'consumer']] = Field(min_length=1, max_length=5)

class MerchantOverrideRequest(BaseModel):
    is_blacklisted: bool
    is_verified: bool
    risk_percent: int = Field(ge=0, le=100)
    admin_note: str

class CommunityModerateRequest(BaseModel):
    action: Literal['pin', 'unpin', 'hide', 'unhide', 'dismiss_reports']

class AlertCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    title_en: str = Field(min_length=1, max_length=240)
    severity: Literal['info', 'warning', 'critical'] = 'warning'
    message: str = Field(min_length=1, max_length=2000)
    active: bool = True


# --- Endpoints ---

@router.get("/stats")
async def get_admin_stats(
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Returns platform-wide executive metrics, health checks, and resolution statistics."""
    return await AdminService.get_overview_stats(db)


@router.get("/cases")
async def list_admin_cases(
    search: str = Query("", description="Search by title, reference, or merchant"),
    status_filter: str = Query("", description="Filter by lifecycle status"),
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Returns master list of all consumer cases with search and status filtering."""
    return await AdminService.list_cases(db, search=search, status_filter=status_filter)


@router.post("/cases/{case_id}/override")
async def override_case(
    case_id: uuid.UUID,
    req: CaseOverrideRequest,
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Administrative status override for dispute lifecycle with immutable audit trace."""
    res = await AdminService.override_case_status(
        case_id=case_id,
        new_status=req.new_status,
        admin_notes=req.admin_notes,
        admin_email=str(admin.id),
        db=db,
    )
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@router.get("/users")
async def list_admin_users(
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Returns all registered user accounts with roles and ban status."""
    return await AdminService.list_users(db)


@router.post("/users/{user_id}/toggle-ban")
async def toggle_ban(
    user_id: str,
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Toggles ban and deactivation status for a consumer or suspicious user."""
    res = await AdminService.toggle_user_ban(user_id=user_id, admin_email=str(admin.id), db=db)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@router.post("/users/{user_id}/roles")
async def update_roles(
    user_id: str,
    req: UserRoleUpdateRequest,
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Promotes or alters administrative roles (admin, reviewer, publisher, operator)."""
    res = await AdminService.update_user_roles(
        user_id=user_id, new_roles=req.roles, admin_email=str(admin.id), db=db
    )
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@router.get("/merchants")
async def list_admin_merchants(
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Returns all tracked merchants, scam probabilities, and blacklist statuses."""
    return await AdminService.list_merchants(db)


@router.post("/merchants/{slug}/override")
async def override_merchant(
    slug: str,
    req: MerchantOverrideRequest,
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Overrides merchant scam risk, blacklist status, and verification badge."""
    return await AdminService.update_merchant_risk(
        db=db,
        slug=slug,
        is_blacklisted=req.is_blacklisted,
        is_verified=req.is_verified,
        risk_percent=req.risk_percent,
        admin_note=req.admin_note,
        admin_email=str(admin.id),
    )


@router.get("/community/posts")
async def list_admin_community_posts(
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Returns community grievances with moderation flags and report counts."""
    return await AdminService.list_community_posts(db)


@router.post("/community/posts/{post_id}/moderate")
async def moderate_post(
    post_id: str,
    req: CommunityModerateRequest,
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Moderates community post: pin, hide, unhide, or dismiss reports."""
    return await AdminService.moderate_community_post(
        db=db,
        post_id=post_id, action=req.action, admin_email=str(admin.id)
    )


@router.get("/alerts")
async def get_alerts(db: AsyncSession = Depends(get_db_session)):
    """Public endpoint to fetch active consumer warning banners."""
    return await AdminService.list_alerts(db)


@router.post("/alerts")
async def create_alert(
    req: AlertCreateRequest,
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Creates a new broadcast alert banner across Ebarki."""
    return await AdminService.create_or_toggle_alert(
        db=db,
        title=req.title,
        title_en=req.title_en,
        severity=req.severity,
        message=req.message,
        active=req.active,
        admin_email=str(admin.id),
    )


@router.get('/alerts/manage')
async def manage_alerts(admin: Principal = Depends(require_role('admin')),
                        db: AsyncSession = Depends(get_db_session)):
    return await AdminService.list_alerts(db, active_only=False)


@router.post('/alerts/{alert_id}/update')
async def update_alert(alert_id: str, req: AlertCreateRequest,
                       admin: Principal = Depends(require_role('admin')),
                       db: AsyncSession = Depends(get_db_session)):
    return await AdminService.update_alert(alert_id, req.model_dump(), str(admin.id), db)


@router.get("/audit-logs")
async def get_audit_logs(
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Returns database-backed administrative action receipts with SHA-256 content hashes."""
    return await AdminService.get_audit_logs(db)


# --- Statutory Candidate Endpoints for Admin UI ---
@router.get("/statutory/candidates")
async def list_statutory_candidates(
    admin: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists legal source watcher candidates pending human review."""
    return await AdminKnowledgeService.list_source_candidates(db)
