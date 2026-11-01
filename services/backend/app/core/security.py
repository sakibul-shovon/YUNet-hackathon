import datetime
import hashlib
import secrets
import uuid
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.identity.models import ActorRole, Principal, WebSession

security_bearer = HTTPBearer(auto_error=False)


def hash_session_token(token: str) -> str:
    """Computes SHA-256 hex digest of an opaque session token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_session_token() -> str:
    """Generates a cryptographically strong opaque session token."""
    return secrets.token_urlsafe(32)


def create_access_jwt(
    principal_id: uuid.UUID | str,
    kind: str = "anonymous",
    roles: list[str] | None = None,
    expires_delta: datetime.timedelta | None = None,
) -> str:
    """Generates a signed short-lived access JWT for BFF and API authorization."""
    if expires_delta is None:
        expires_delta = datetime.timedelta(minutes=15)

    now = datetime.datetime.now(datetime.UTC)
    payload: dict[str, Any] = {
        "sub": str(principal_id),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "kind": kind,
        "roles": roles or ["consumer"],
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_and_verify_jwt(token: str) -> dict[str, Any]:
    """Decodes and validates JWT claims against issuer, audience, and expiration."""
    try:
        claims = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_iss": True,
                "verify_exp": True,
            },
        )
        return claims
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "AUTH_TOKEN_EXPIRED",
                    "message_key": "auth.token_expired",
                    "details": {},
                }
            },
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "AUTH_INVALID_ISSUER",
                    "message_key": "auth.invalid_issuer",
                    "details": {},
                }
            },
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "AUTH_INVALID_AUDIENCE",
                    "message_key": "auth.invalid_audience",
                    "details": {},
                }
            },
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "AUTH_TOKEN_INVALID",
                    "message_key": "auth.invalid_token",
                    "details": {},
                }
            },
        )


def verify_csrf_protection(request: Request) -> None:
    """Verifies CSRF token header for state-mutating requests coming through cookie sessions."""
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    # If using Cookie-based session, require X-CSRF-Token or sec-fetch-site check
    cookie_session = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if cookie_session:
        csrf_header = request.headers.get("x-csrf-token")
        if not csrf_header:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "CSRF_TOKEN_MISSING",
                        "message_key": "auth.csrf_missing",
                        "details": {},
                    }
                },
            )


async def get_current_principal(
    request: Request,
    response: Response,
    bearer: HTTPAuthorizationCredentials | None = Depends(security_bearer),
    db: AsyncSession = Depends(get_db_session),
) -> Principal:
    """Authenticates the caller, retrieves the principal, sets tenant context and no-store headers."""
    # Ensure no-store response header on all private authenticated requests
    response.headers["Cache-Control"] = "private, no-store"

    principal_id: uuid.UUID | None = None

    # 1. Bearer JWT takes precedence
    if bearer and bearer.credentials:
        claims = decode_and_verify_jwt(bearer.credentials)
        try:
            principal_id = uuid.UUID(claims["sub"])
        except (ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": {"code": "AUTH_INVALID_SUB", "message_key": "auth.invalid_token"}},
            )
    else:
        # 2. Check opaque session cookie
        session_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
        if session_token:
            verify_csrf_protection(request)
            token_hash = hash_session_token(session_token)
            now = datetime.datetime.now(datetime.UTC)
            stmt = select(WebSession).where(
                WebSession.session_token_hash == token_hash,
                WebSession.expires_at > now,
                WebSession.revoked_at.is_(None),
            )
            res = await db.execute(stmt)
            web_session = res.scalar_one_or_none()
            if web_session:
                principal_id = web_session.principal_id
                # Update last seen
                web_session.last_seen_at = now
                await db.commit()

    if not principal_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "AUTH_REQUIRED",
                    "message_key": "auth.required",
                    "details": {},
                }
            },
        )

    # Fetch principal from DB
    stmt_p = select(Principal).where(Principal.id == principal_id, Principal.deleted_at.is_(None))
    res_p = await db.execute(stmt_p)
    principal = res_p.scalar_one_or_none()

    if not principal:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "PRINCIPAL_NOT_FOUND",
                    "message_key": "auth.principal_not_found",
                    "details": {},
                }
            },
        )

    # Bind tenant context to current session for RLS / tenant checking
    db.info["current_principal_id"] = str(principal.id)
    return principal


async def get_optional_principal(
    request: Request,
    response: Response,
    bearer: HTTPAuthorizationCredentials | None = Depends(security_bearer),
    db: AsyncSession = Depends(get_db_session),
) -> Principal | None:
    """Optionally returns authenticated principal, or None if anonymous / unauthenticated."""
    try:
        return await get_current_principal(request, response, bearer, db)
    except HTTPException:
        return None


def require_role(required_role: str):
    """Enforces specific actor role (e.g., 'reviewer', 'publisher', 'operator')."""

    async def role_checker(
        principal: Principal = Depends(get_current_principal),
        db: AsyncSession = Depends(get_db_session),
    ) -> Principal:
        stmt = select(ActorRole).where(
            ActorRole.principal_id == principal.id,
            ActorRole.role == required_role,
        )
        res = await db.execute(stmt)
        role = res.scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN_ROLE",
                        "message_key": "auth.forbidden_role",
                        "details": {"required_role": required_role},
                    }
                },
            )
        return principal

    return role_checker
