import datetime
import hashlib
import secrets
import uuid

from fastapi import HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models import AdminRecord
from app.cases.models import Case, OutboxMessage
from app.core.config import settings
from app.core.security import (
    create_access_jwt,
    csrf_for_session,
    decode_and_verify_jwt,
    generate_session_token,
    hash_session_token,
)
from app.identity.models import (
    ActorRole,
    Consent,
    DeletionRequest,
    Principal,
    UserAccount,
    WebSession,
)
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


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${dk.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, expected_hash = stored_hash.split("$", 1)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
        return secrets.compare_digest(dk.hex(), expected_hash)
    except (ValueError, TypeError, AttributeError):
        return False


class IdentityService:
    @staticmethod
    async def create_or_resume_guest(
        db: AsyncSession,
        request: Request,
        response: Response,
    ) -> GuestSessionResponse:
        """Creates an isolated anonymous principal & session, or resumes existing valid session."""
        existing_cookie = request.cookies.get(settings.SESSION_COOKIE_NAME)
        now = datetime.datetime.now(datetime.UTC)
        principal: Principal | None = None

        if existing_cookie:
            token_hash = hash_session_token(existing_cookie)
            stmt = select(WebSession).where(
                WebSession.session_token_hash == token_hash,
                WebSession.expires_at > now,
                WebSession.revoked_at.is_(None),
            )
            res = await db.execute(stmt)
            web_session = res.scalar_one_or_none()
            if web_session:
                stmt_p = select(Principal).where(
                    Principal.id == web_session.principal_id,
                    Principal.deleted_at.is_(None),
                )
                res_p = await db.execute(stmt_p)
                principal = res_p.scalar_one_or_none()
                if principal:
                    ban = await db.get(AdminRecord, 'ban:'+str(principal.id))
                    if ban and ban.payload.get('banned'):
                        raise HTTPException(403, 'This account is suspended.')
                    web_session.last_seen_at = now
                    await db.commit()

        # If no valid principal resumed, create a new anonymous principal
        if not principal:
            principal = Principal(
                id=uuid.uuid4(),
                kind="anonymous",
                locale="en-BD",
                consent_revision=1,
            )
            db.add(principal)
            await db.flush()

            # Assign default consumer role
            role = ActorRole(
                id=uuid.uuid4(),
                principal_id=principal.id,
                role="consumer",
                grant_origin="guest_bootstrap",
                scope="global",
            )
            db.add(role)
            await db.flush()

        # Generate new session credentials
        raw_session_token = generate_session_token()
        session_hash = hash_session_token(raw_session_token)
        expires_at = now + datetime.timedelta(seconds=settings.SESSION_MAX_AGE_SECONDS)

        session_record = WebSession(
            id=uuid.uuid4(),
            session_token_hash=session_hash,
            principal_id=principal.id,
            expires_at=expires_at,
            last_seen_at=now,
        )
        db.add(session_record)
        await db.commit()

        # Set secure HttpOnly cookie
        response.set_cookie(
            key=settings.SESSION_COOKIE_NAME,
            value=raw_session_token,
            max_age=settings.SESSION_MAX_AGE_SECONDS,
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="lax",
            path="/",
        )

        csrf_token = csrf_for_session(raw_session_token)
        access_jwt = create_access_jwt(principal_id=principal.id, kind=principal.kind, session_id=session_record.id)

        return GuestSessionResponse(
            principal_id=principal.id,
            access_token=access_jwt,
            token_type="bearer",
            expires_in=900,
            csrf_token=csrf_token,
        )

    @staticmethod
    async def upgrade_account(
        principal: Principal,
        req: UpgradeRequest,
        db: AsyncSession,
        request: Request,
    ) -> UpgradeResponse:
        """Upgrades anonymous principal to permanent verified status while preserving cases."""
        principal.kind = "permanent"
        principal.updated_at = datetime.datetime.now(datetime.UTC)
        await db.commit()

        cookie = request.cookies.get(settings.SESSION_COOKIE_NAME)
        bearer = request.headers.get('authorization', '')
        session_id = None
        if bearer.lower().startswith('bearer '):
            session_id = decode_and_verify_jwt(bearer.split(' ', 1)[1]).get('sid')
        elif cookie:
            session_id = await db.scalar(select(WebSession.id).where(
                WebSession.session_token_hash == hash_session_token(cookie), WebSession.principal_id == principal.id))
        new_token = create_access_jwt(
            principal_id=principal.id,
            kind="permanent",
            roles=["consumer"],
            session_id=session_id,
        )
        return UpgradeResponse(
            principal_id=principal.id,
            kind="permanent",
            access_token=new_token,
            message="Account upgraded successfully. All existing cases preserved.",
        )

    @staticmethod
    async def logout_session(
        request: Request,
        response: Response,
        db: AsyncSession,
    ) -> dict:
        """Revokes active session and deletes session cookie."""
        cookie = request.cookies.get(settings.SESSION_COOKIE_NAME)
        if cookie:
            token_hash = hash_session_token(cookie)
            stmt = select(WebSession).where(WebSession.session_token_hash == token_hash)
            res = await db.execute(stmt)
            web_session = res.scalar_one_or_none()
            if web_session:
                web_session.revoked_at = datetime.datetime.now(datetime.UTC)
                await db.commit()

        authorization = request.headers.get('authorization', '')
        if authorization.lower().startswith('bearer '):
            try:
                claims = decode_and_verify_jwt(authorization.split(' ', 1)[1])
                if claims.get('sid'):
                    session = await db.get(WebSession, uuid.UUID(claims['sid']))
                    if session and str(session.principal_id) == claims['sub']:
                        session.revoked_at = datetime.datetime.now(datetime.UTC)
                        await db.commit()
            except (HTTPException, ValueError, KeyError):
                pass  # Expired credentials can still clear a local cookie.

        response.delete_cookie(
            key=settings.SESSION_COOKIE_NAME,
            path="/",
        )
        return {"status": "logged_out"}

    @staticmethod
    async def get_me(principal: Principal, db: AsyncSession) -> PrincipalOut:
        """Retrieves profile and roles for the authenticated principal."""
        stmt = select(ActorRole.role).where(ActorRole.principal_id == principal.id)
        res = await db.execute(stmt)
        roles = [r for r in res.scalars().all()]
        return PrincipalOut(
            id=principal.id,
            kind=principal.kind,
            locale=principal.locale,
            consent_revision=principal.consent_revision,
            created_at=principal.created_at,
            roles=roles if roles else ["consumer"],
        )

    @staticmethod
    async def record_consent(
        principal: Principal,
        data: ConsentCreate,
        db: AsyncSession,
    ) -> ConsentOut:
        """Records affirmative consent for a purpose and policy version."""
        if data.case_id:
            # Verify case ownership
            stmt = select(Case).where(
                Case.id == data.case_id,
                Case.principal_id == principal.id,
            )
            res = await db.execute(stmt)
            if not res.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": {"code": "CASE_NOT_FOUND", "message_key": "case.not_found"}},
                )

        consent = Consent(
            id=uuid.uuid4(),
            principal_id=principal.id,
            case_id=data.case_id,
            purpose=data.purpose,
            policy_version=data.policy_version,
            processor_version=data.processor_version,
            affirmative_action=data.affirmative_action,
        )
        db.add(consent)
        await db.commit()
        await db.refresh(consent)
        return ConsentOut.model_validate(consent, from_attributes=True)

    @staticmethod
    async def request_deletion(
        principal: Principal,
        data: DeletionRequestCreate,
        db: AsyncSession,
    ) -> DeletionRequestOut:
        """Revokes access immediately and queues deletion cleanup."""
        now = datetime.datetime.now(datetime.UTC)
        if data.case_id:
            # Verify ownership
            stmt = select(Case).where(
                Case.id == data.case_id,
                Case.principal_id == principal.id,
            )
            res = await db.execute(stmt)
            case = res.scalar_one_or_none()
            if not case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": {"code": "CASE_NOT_FOUND", "message_key": "case.not_found"}},
                )
            case.lifecycle_status = "deleting"
            case.deleted_at = now

        del_req = DeletionRequest(
            id=uuid.uuid4(),
            principal_id=principal.id,
            case_id=data.case_id,
            scope=data.scope,
            status="access_revoked",
            requested_at=now,
            access_revoked_at=now,
        )
        db.add(del_req)

        # Enqueue outbox deletion event
        outbox = OutboxMessage(
            id=uuid.uuid4(),
            event_type="deletion.requested",
            aggregate_type="case" if data.case_id else "principal",
            aggregate_id=data.case_id or principal.id,
            payload={
                "deletion_request_id": str(del_req.id),
                "scope": data.scope,
                "principal_id": str(principal.id),
                "case_id": str(data.case_id) if data.case_id else None,
            },
        )
        db.add(outbox)
        await db.commit()
        await db.refresh(del_req)
        return DeletionRequestOut.model_validate(del_req, from_attributes=True)

    @staticmethod
    async def register_user(
        req: UserRegisterRequest,
        db: AsyncSession,
        response: Response,
    ) -> AuthUserOut:
        """Registers a new permanent user account."""
        now = datetime.datetime.now(datetime.UTC)
        normalized_email = req.email.strip().lower()

        stmt = select(UserAccount).where(UserAccount.email == normalized_email)
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists. Please sign in instead.",
            )

        principal = Principal(
            id=uuid.uuid4(),
            kind="permanent",
            locale="bn-BD",
            consent_revision=1,
        )
        db.add(principal)
        await db.flush()

        role = ActorRole(
            id=uuid.uuid4(),
            principal_id=principal.id,
            role="consumer",
            grant_origin="user_register",
            scope="global",
        )
        db.add(role)

        user = UserAccount(
            id=uuid.uuid4(),
            principal_id=principal.id,
            email=normalized_email,
            full_name=req.full_name.strip(),
            phone=req.phone.strip() if req.phone else None,
            password_hash=hash_password(req.password),
            is_demo_judge=False,
        )
        db.add(user)

        raw_session_token = generate_session_token()
        session_hash = hash_session_token(raw_session_token)
        expires_at = now + datetime.timedelta(seconds=settings.SESSION_MAX_AGE_SECONDS)

        session_record = WebSession(
            id=uuid.uuid4(),
            session_token_hash=session_hash,
            principal_id=principal.id,
            expires_at=expires_at,
            last_seen_at=now,
        )
        db.add(session_record)
        await db.commit()

        response.set_cookie(
            key=settings.SESSION_COOKIE_NAME,
            value=raw_session_token,
            max_age=settings.SESSION_MAX_AGE_SECONDS,
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="lax",
            path="/",
        )

        access_jwt = create_access_jwt(principal_id=principal.id, kind="permanent", session_id=session_record.id)
        return AuthUserOut(
            logged_in=True,
            principal_id=principal.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            is_demo_judge=False,
            access_token=access_jwt,
            csrf_token=csrf_for_session(raw_session_token),
        )

    @staticmethod
    async def login_user(
        req: UserLoginRequest,
        db: AsyncSession,
        response: Response,
        require_admin: bool = False,
    ) -> AuthUserOut:
        """Logs in an existing user with email and password."""
        now = datetime.datetime.now(datetime.UTC)
        email_clean = req.email.strip().lower()
        stmt = select(UserAccount).where(UserAccount.email == email_clean)
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()

        # On-demand bootstrap for provisioned super admin account
        if (
            not user
            and settings.BOOTSTRAP_ADMIN_EMAIL
            and settings.BOOTSTRAP_ADMIN_PASSWORD
            and email_clean == settings.BOOTSTRAP_ADMIN_EMAIL.strip().lower()
            and secrets.compare_digest(req.password, settings.BOOTSTRAP_ADMIN_PASSWORD)
        ):
            admin_principal = Principal(
                id=uuid.uuid4(),
                kind="permanent",
                locale="en-BD",
                consent_revision=1,
            )
            db.add(admin_principal)
            await db.flush()

            for r_name in ["admin", "reviewer", "publisher", "consumer"]:
                db.add(
                    ActorRole(
                        id=uuid.uuid4(),
                        principal_id=admin_principal.id,
                        role=r_name,
                        grant_origin="bootstrap_seed",
                        scope="global",
                    )
                )

            user = UserAccount(
                id=uuid.uuid4(),
                principal_id=admin_principal.id,
                email=email_clean,
                full_name="Ebarki Administrator",
                password_hash=hash_password(req.password),
                is_demo_judge=False,
            )
            db.add(user)
            await db.commit()

        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password. Please verify and try again.",
            )

        role_stmt = select(ActorRole.role).where(ActorRole.principal_id == user.principal_id)
        role_res = await db.execute(role_stmt)
        user_roles = [r for r in role_res.scalars().all()]

        ban = await db.get(AdminRecord, 'ban:'+str(user.principal_id))
        if ban and ban.payload.get('banned'):
            raise HTTPException(403, 'This account is suspended.')
        if require_admin and not set(user_roles) & {'admin', 'reviewer', 'publisher', 'operator'}:
            raise HTTPException(403, 'This account does not have administrative access.')

        raw_session_token = generate_session_token()
        session_hash = hash_session_token(raw_session_token)
        expires_at = now + datetime.timedelta(seconds=settings.SESSION_MAX_AGE_SECONDS)

        session_record = WebSession(
            id=uuid.uuid4(),
            session_token_hash=session_hash,
            principal_id=user.principal_id,
            expires_at=expires_at,
            last_seen_at=now,
        )
        db.add(session_record)
        await db.commit()

        response.set_cookie(
            key=settings.SESSION_COOKIE_NAME,
            value=raw_session_token,
            max_age=settings.SESSION_MAX_AGE_SECONDS,
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="lax",
            path="/",
        )

        access_jwt = create_access_jwt(principal_id=user.principal_id, kind="permanent", session_id=session_record.id)
        return AuthUserOut(
            logged_in=True,
            principal_id=user.principal_id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            is_demo_judge=user.is_demo_judge,
            roles=user_roles,
            access_token=access_jwt,
            csrf_token=csrf_for_session(raw_session_token),
        )

    @staticmethod
    async def login_judge_demo(
        db: AsyncSession,
        response: Response,
    ) -> AuthUserOut:
        """1-Click Hackathon Judge Demo Login: creates or resumes demo judge account."""
        now = datetime.datetime.now(datetime.UTC)
        # Every judge gets an isolated consumer-only workspace.
        principal = Principal(id=uuid.uuid4(), kind='permanent', locale='en-BD', consent_revision=1)
        db.add(principal)
        await db.flush()
        db.add(ActorRole(id=uuid.uuid4(), principal_id=principal.id, role='consumer',
                         grant_origin='judge_demo_grant', scope='global'))
        user = UserAccount(id=uuid.uuid4(), principal_id=principal.id,
                           email=f'judge-{uuid.uuid4().hex}@demo.ebarki.invalid',
                           full_name='Ebarki demo judge', password_hash=hash_password(secrets.token_urlsafe(32)),
                           is_demo_judge=True)
        db.add(user)
        await db.flush()
        from app.scenarios.sample_evidence import add_sample_payment
        from app.scenarios.service import ScenarioService
        result = await ScenarioService.launch_scenario('scenario_a', principal, db, locale='en-BD')
        case = await db.get(Case, uuid.UUID(result['case_id']))
        case.title = 'An undelivered phone. One payment discrepancy.'
        case.merchant_name = 'Sample Electronics'
        case.incident_date = (datetime.date.today() - datetime.timedelta(days=12)).isoformat()
        case.story_narrative = 'I paid BDT 5,500 for a phone ordered online. The promised delivery date has passed. The phone has not arrived, and the seller has not replied.'
        # Remove metadata-only legacy fixtures from this new isolated sample.
        from sqlalchemy import delete

        from app.evidence.models import EvidenceItem
        await db.execute(delete(EvidenceItem).where(EvidenceItem.case_id == case.id))
        await db.commit()
        await add_sample_payment(case, principal, db)
        from app.operations.connected_records import append_workspace_event
        started_on = datetime.date.fromisoformat(case.incident_date)
        sample_conversation = '\n'.join([
            f'{started_on.isoformat()} Seller: Your phone order is confirmed.',
            f'{(started_on + datetime.timedelta(days=1)).isoformat()} Seller: We will deliver by {(started_on + datetime.timedelta(days=2)).isoformat()}.',
            f'{(started_on + datetime.timedelta(days=7)).isoformat()} Buyer: The phone has not arrived. Please update me.',
        ])
        await append_workspace_event(case, principal, db, 'workspace.source_added', {
            'text': sample_conversation, 'label': 'Fictional sample conversation',
            'source_type': 'pasted_message', 'is_demo': True,
        })
        db.add(Consent(id=uuid.uuid4(), principal_id=principal.id, case_id=case.id,
                       purpose='external_ai_processing', policy_version='ebarki-2026-11',
                       affirmative_action='judge_demo_fictional_records'))
        await db.commit()
        raw_session_token = generate_session_token()
        session_hash = hash_session_token(raw_session_token)
        expires_at = now + datetime.timedelta(seconds=settings.SESSION_MAX_AGE_SECONDS)

        session_record = WebSession(
            id=uuid.uuid4(),
            session_token_hash=session_hash,
            principal_id=user.principal_id,
            expires_at=expires_at,
            last_seen_at=now,
        )
        db.add(session_record)
        await db.commit()

        response.set_cookie(
            key=settings.SESSION_COOKIE_NAME,
            value=raw_session_token,
            max_age=settings.SESSION_MAX_AGE_SECONDS,
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="lax",
            path="/",
        )

        access_jwt = create_access_jwt(principal_id=user.principal_id, kind="permanent", session_id=session_record.id)
        return AuthUserOut(
            logged_in=True,
            principal_id=user.principal_id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            is_demo_judge=True,
            roles=["consumer"],
            demo_case_id=case.id,
            access_token=access_jwt,
            csrf_token=csrf_for_session(raw_session_token),
        )

    @staticmethod
    async def get_current_user_profile(
        principal: Principal,
        db: AsyncSession,
    ) -> AuthUserOut:
        """Returns the logged in user profile if exists, or guest info."""
        stmt = select(UserAccount).where(UserAccount.principal_id == principal.id)
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()

        if user:
            role_stmt = select(ActorRole.role).where(ActorRole.principal_id == user.principal_id)
            role_res = await db.execute(role_stmt)
            user_roles = [r for r in role_res.scalars().all()]
            return AuthUserOut(
                logged_in=True,
                principal_id=principal.id,
                email=user.email,
                full_name=user.full_name,
                phone=user.phone,
                is_demo_judge=user.is_demo_judge,
                roles=user_roles,
            )
        return AuthUserOut(
            logged_in=False,
            principal_id=principal.id,
            email="guest@claimcraft.local",
            full_name="Guest Consumer",
            phone=None,
            is_demo_judge=False,
        )
