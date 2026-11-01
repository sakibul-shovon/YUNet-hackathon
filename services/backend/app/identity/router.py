import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.identity.models import DeletionRequest, Principal
from app.identity.schemas import (
    AuthUserOut,
    ConsentCreate,
    ConsentOut,
    DeletionRequestCreate,
    DeletionRequestOut,
    GuestSessionResponse,
    PrincipalOut,
    UpgradeRequest,
    UpgradeResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.identity.service import IdentityService

router = APIRouter(tags=["Identity & Sessions"])


@router.post("/auth/guest", response_model=GuestSessionResponse)
@router.post("/v1/auth/guest", response_model=GuestSessionResponse)
async def auth_guest(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
):
    """Initializes or resumes an isolated anonymous guest session with HttpOnly cookie & JWT."""
    return await IdentityService.create_or_resume_guest(db, request, response)


@router.post("/auth/upgrade", response_model=UpgradeResponse)
@router.post("/v1/auth/upgrade", response_model=UpgradeResponse)
async def auth_upgrade(
    req: UpgradeRequest,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Upgrades an anonymous guest account to a permanent verified account, retaining cases."""
    return await IdentityService.upgrade_account(principal, req, db)


@router.post("/auth/register", response_model=AuthUserOut, status_code=status.HTTP_201_CREATED)
@router.post("/v1/auth/register", response_model=AuthUserOut, status_code=status.HTTP_201_CREATED)
async def auth_register(
    req: UserRegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
):
    """Registers a new permanent user with email, password, and name."""
    return await IdentityService.register_user(req, db, response)


@router.post("/auth/login", response_model=AuthUserOut)
@router.post("/v1/auth/login", response_model=AuthUserOut)
async def auth_login(
    req: UserLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
):
    """Logs in an existing user with email and password."""
    return await IdentityService.login_user(req, db, response)


@router.post("/auth/judge-demo", response_model=AuthUserOut)
@router.post("/v1/auth/judge-demo", response_model=AuthUserOut)
async def auth_judge_demo(
    response: Response,
    db: AsyncSession = Depends(get_db_session),
):
    """1-Click Hackathon Judge Demo Login: creates or logs into demo judge account with pre-seeded cases."""
    return await IdentityService.login_judge_demo(db, response)


@router.get("/auth/me", response_model=AuthUserOut)
@router.get("/v1/auth/me", response_model=AuthUserOut)
async def get_auth_user(
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Returns current logged-in user profile, or guest fallback."""
    return await IdentityService.get_current_user_profile(principal, db)


@router.post("/auth/logout")
@router.post("/v1/auth/logout")
async def auth_logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
):
    """Terminates the current session and clears session cookie."""
    return await IdentityService.logout_session(request, response, db)


@router.get("/v1/me", response_model=PrincipalOut)
async def get_me(
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Returns authenticated principal profile and roles with Cache-Control: private, no-store."""
    return await IdentityService.get_me(principal, db)


@router.post("/v1/consents", response_model=ConsentOut, status_code=status.HTTP_201_CREATED)
async def record_consent(
    data: ConsentCreate,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Records affirmative user consent for processing purposes."""
    return await IdentityService.record_consent(principal, data, db)


@router.post(
    "/v1/deletions", response_model=DeletionRequestOut, status_code=status.HTTP_202_ACCEPTED
)
async def request_deletion(
    data: DeletionRequestCreate,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Revokes access immediately and schedules complete background deletion."""
    return await IdentityService.request_deletion(principal, data, db)


@router.get("/v1/deletions/{id}", response_model=DeletionRequestOut)
async def get_deletion_status(
    id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves non-content status of an active or completed deletion request."""
    stmt = select(DeletionRequest).where(
        DeletionRequest.id == id,
        DeletionRequest.principal_id == principal.id,
    )
    res = await db.execute(stmt)
    del_req = res.scalar_one_or_none()
    if not del_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "DELETION_NOT_FOUND", "message_key": "deletion.not_found"}},
        )
    return DeletionRequestOut.model_validate(del_req, from_attributes=True)
