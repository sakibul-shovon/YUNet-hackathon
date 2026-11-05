import datetime
import hashlib
import json
import uuid
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models import AdminAuditEntry, AdminRecord
from app.cases.models import Case, CaseEvent
from app.community.service import COMMUNITY_POSTS_STORE
from app.identity.models import ActorRole, UserAccount, WebSession
from app.knowledge.models import SourceCandidate
from app.merchants.service import KNOWN_OFFENDER_REGISTRY


class AdminService:
    @staticmethod
    async def state(db, key, default=None):
        record = await db.get(AdminRecord, key)
        return record.payload if record else (default or {})

    @staticmethod
    async def save_state(db, key, payload):
        record = await db.get(AdminRecord, key)
        if record is None:
            db.add(AdminRecord(key=key, payload=payload))
        else:
            record.payload = payload
            record.updated_at = datetime.datetime.now(datetime.UTC)

    @staticmethod
    async def record_audit(db, admin_email, action, target, details):
        entry = {'id': str(uuid.uuid4()), 'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
                 'admin_email': admin_email, 'action': action, 'target': target, 'details': details}
        entry['hash'] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
        db.add(AdminAuditEntry(id=entry['id'], payload=entry))

    @classmethod
    async def get_overview_stats(cls, db: AsyncSession) -> dict[str, Any]:
        # Case metrics from DB
        stmt_cases = select(Case)
        res_cases = await db.execute(stmt_cases)
        cases = list(res_cases.scalars().all())

        total_cases = len(cases)
        active_cases = sum(1 for c in cases if c.lifecycle_status in ("draft", "active", "escalated"))
        resolved_cases = sum(1 for c in cases if c.lifecycle_status == "resolved")
        dismissed_cases = sum(1 for c in cases if c.lifecycle_status in ("dismissed", "closed", "fraudulent"))

        # Recorded disputed amounts only. Resolution status is not payment proof.
        from app.facts.models import FactAssertion
        amount_rows = list((await db.scalars(select(FactAssertion).where(
            FactAssertion.case_id.in_([case.id for case in cases if case.deleted_at is None]),
            FactAssertion.is_active.is_(True), FactAssertion.field_name == 'amount_paid',
        ).order_by(FactAssertion.created_at.desc()))).all())
        seen = set()
        total_minor = 0
        for fact in amount_rows:
            if fact.case_id not in seen and isinstance(fact.typed_value, dict):
                total_minor += int(fact.typed_value.get('minor_units', 0))
                seen.add(fact.case_id)
        total_disputed_bdt = total_minor / 100
        total_recovered_bdt = None  # No verified recovered-payment dataset exists.

        # User metrics
        stmt_users = select(UserAccount)
        res_users = await db.execute(stmt_users)
        users = list(res_users.scalars().all())

        # Statutory reviews pending
        stmt_candidates = select(SourceCandidate).where(SourceCandidate.status == "LEGAL_REVIEW_REQUIRED")
        res_cand = await db.execute(stmt_candidates)
        pending_statutory = len(list(res_cand.scalars().all()))

        return {
            "metrics": {
                "total_cases": total_cases,
                "active_cases": active_cases,
                "resolved_cases": resolved_cases,
                "dismissed_cases": dismissed_cases,
                "total_disputed_bdt": total_disputed_bdt,
                "total_recovered_bdt": total_recovered_bdt,
                "total_registered_users": len(users),
                "banned_users": sum(bool(record.payload.get('banned')) for record in (await db.scalars(select(AdminRecord).where(AdminRecord.key.like('ban:%')))).all()),
                "pending_statutory_reviews": pending_statutory,
                "total_merchants_tracked": len(await cls.list_merchants(db)),
                "community_grievances_count": len(COMMUNITY_POSTS_STORE),
            },
            "resolution_paths_distribution": {},
            "system_health": {
                "api_gateway": "This request was handled; uptime not measured",
                "database_engine": "Query completed; authorization enforced by application",
                "multimodal_ocr": "Consent-scoped reader; check per-run receipt",
                "voice_stt": "Consent-scoped reader; check per-run receipt",
                "active_statutory_release": "Not verified by this endpoint",
                "admin_persistence": "Database-backed alerts, overrides, bans and action receipts",
            },
        }

    @classmethod
    async def list_cases(cls, db: AsyncSession, search: str = "", status_filter: str = "") -> list[dict[str, Any]]:
        stmt = select(Case).order_by(Case.created_at.desc())
        res = await db.execute(stmt)
        cases = list(res.scalars().all())

        results = []
        for c in cases:
            if status_filter and c.lifecycle_status != status_filter:
                continue
            if search:
                s_lower = search.lower()
                matches = (
                    s_lower in (c.title or "").lower()
                    or s_lower in (c.merchant_name or "").lower()
                    or s_lower in (c.display_reference or "").lower()
                )
                if not matches:
                    continue

            results.append({
                "id": str(c.id),
                "display_reference": c.display_reference,
                "title": c.title,
                "merchant_name": c.merchant_name or "Unknown Seller",
                "lifecycle_status": c.lifecycle_status,
                "locale": c.locale,
                "created_at": c.created_at.isoformat() if c.created_at else "",
                "is_demo": c.is_demo,
                "story_snippet": (c.story_narrative or "")[:120] + "...",
            })
        return results

    @classmethod
    async def override_case_status(
        cls,
        case_id: uuid.UUID,
        new_status: str,
        admin_notes: str,
        admin_email: str,
        db: AsyncSession,
    ) -> dict[str, Any]:
        stmt = select(Case).where(Case.id == case_id)
        res = await db.execute(stmt)
        case = res.scalar_one_or_none()
        if not case:
            return {"error": "Case not found"}

        old_status = case.lifecycle_status
        case.lifecycle_status = new_status
        case.row_version += 1
        case.updated_at = datetime.datetime.now(datetime.UTC)

        # Log event in CaseEvent
        evt = CaseEvent(
            id=uuid.uuid4(),
            case_id=case.id,
            principal_id=case.principal_id,
            event_sequence=int(await db.scalar(select(func.coalesce(func.max(CaseEvent.event_sequence), 0)).where(CaseEvent.case_id == case.id))) + 1,
            actor_type='admin',
            event_type="ADMIN_STATUS_OVERRIDE",
            payload={
                "old_status": old_status,
                "new_status": new_status,
                "admin_notes": admin_notes,
                "admin_email": admin_email,
            },
        )
        db.add(evt)

        await cls.record_audit(db,
            admin_email=admin_email,
            action="OVERRIDE_CASE_STATUS",
            target=f"Case {case.display_reference or str(case.id)[:8]}",
            details=f"Changed status from '{old_status}' to '{new_status}'. Note: {admin_notes}",
        )
        await db.commit()
        return {"success": True, "case_id": str(case.id), "new_status": new_status}

    @classmethod
    async def list_users(cls, db: AsyncSession) -> list[dict[str, Any]]:
        stmt = select(UserAccount).order_by(UserAccount.created_at.desc())
        res = await db.execute(stmt)
        users = list(res.scalars().all())

        out = []
        for u in users:
            stmt_roles = select(ActorRole.role).where(ActorRole.principal_id == u.principal_id)
            res_roles = await db.execute(stmt_roles)
            roles = list(res_roles.scalars().all())

            is_banned = bool((await cls.state(db, 'ban:'+str(u.principal_id))).get('banned'))
            out.append({
                "id": str(u.id),
                "principal_id": str(u.principal_id),
                "email": u.email,
                "full_name": u.full_name,
                "phone": u.phone or "N/A",
                "is_demo_judge": u.is_demo_judge,
                "is_banned": is_banned,
                "roles": roles if roles else ["consumer"],
                "created_at": u.created_at.isoformat() if u.created_at else "",
            })
        return out

    @classmethod
    async def toggle_user_ban(cls, user_id: str, admin_email: str, db: AsyncSession) -> dict[str, Any]:
        stmt = select(UserAccount).where(UserAccount.id == uuid.UUID(user_id))
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user:
            return {"error": "User not found"}

        if str(user.principal_id) == admin_email:
            raise HTTPException(400, 'You cannot ban your current administrative account.')
        state = await cls.state(db, 'ban:'+str(user.principal_id))
        is_banned = not bool(state.get('banned'))
        await cls.save_state(db, 'ban:'+str(user.principal_id), {'banned': is_banned})
        action = 'BAN_USER' if is_banned else 'UNBAN_USER'
        if is_banned:
            await db.execute(update(WebSession).where(WebSession.principal_id == user.principal_id,
                WebSession.revoked_at.is_(None)).values(revoked_at=datetime.datetime.now(datetime.UTC)))

        await cls.record_audit(db,
            admin_email=admin_email,
            action=action,
            target=f"User {user.email}",
            details=f"Administrative account status changed to {'BANNED' if is_banned else 'ACTIVE'}",
        )
        await db.commit()
        return {"success": True, "user_id": user_id, "is_banned": is_banned}

    @classmethod
    async def update_user_roles(
        cls, user_id: str, new_roles: list[str], admin_email: str, db: AsyncSession
    ) -> dict[str, Any]:
        stmt = select(UserAccount).where(UserAccount.id == uuid.UUID(user_id))
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user:
            return {"error": "User not found"}

        permitted = {'admin', 'reviewer', 'publisher', 'operator', 'consumer'}
        if not new_roles or len(set(new_roles)) != len(new_roles) or not set(new_roles) <= permitted:
            raise HTTPException(422, 'Choose unique supported roles.')
        if user.is_demo_judge and set(new_roles) != {'consumer'}:
            raise HTTPException(400, 'Judge demo accounts retain consumer-only access.')
        if str(user.principal_id) == admin_email and 'admin' not in new_roles:
            raise HTTPException(400, 'You cannot remove your own administrative access.')

        # Delete existing roles
        stmt_del = select(ActorRole).where(ActorRole.principal_id == user.principal_id)
        res_del = await db.execute(stmt_del)
        for r in res_del.scalars().all():
            await db.delete(r)
        # Flush removals before inserting overlapping roles; SQLAlchemy can
        # otherwise insert first and violate the principal/role/scope key.
        await db.flush()

        # Add new roles
        for r_name in new_roles:
            role = ActorRole(
                id=uuid.uuid4(),
                principal_id=user.principal_id,
                role=r_name,
                grant_origin="admin_promotion",
                scope="global",
            )
            db.add(role)

        await cls.record_audit(db,
            admin_email=admin_email,
            action="UPDATE_USER_ROLES",
            target=f"User {user.email}",
            details=f"Assigned roles: {', '.join(new_roles)}",
        )
        await db.commit()
        return {"success": True, "user_id": user_id, "roles": new_roles}

    @classmethod
    async def list_merchants(cls, db):
        overrides = {r.key.removeprefix('merchant:'): r.payload for r in (await db.scalars(select(AdminRecord).where(AdminRecord.key.like('merchant:%')))).all() if isinstance(r.payload, dict)}
        results = []
        for slug, m in KNOWN_OFFENDER_REGISTRY.items():
            override = overrides.get(slug, {})
            is_blacklisted = override.get("is_blacklisted", m.get("is_blacklisted", False))
            is_verified = override.get("is_verified", m.get("is_verified", False))
            risk_percent = override.get("risk_percent", m.get("risk_percent", 50))
            status_label = "BLACKLISTED" if is_blacklisted else "VERIFIED" if is_verified else f"RISK {risk_percent}%"
            results.append({
                "id": slug,
                "slug": slug,
                "merchant_name": m["merchant_name"],
                "status": status_label,
                "platform": m.get("platform", "Online"),
                "category": m.get("category", "E-Commerce"),
                "risk_percent": risk_percent,
                "is_blacklisted": is_blacklisted,
                "is_verified": is_verified,
                "complaint_count": m.get("complaint_count", 0),
                "total_disputed_bdt": m.get("total_disputed_bdt", 0),
                "admin_note": override.get("admin_note", ""),
                "source": "curated_radar",
            })
        for slug, payload in overrides.items():
            if slug not in KNOWN_OFFENDER_REGISTRY:
                results.append({
                    "id": slug,
                    "slug": slug,
                    "merchant_name": slug.replace('-', ' ').title(),
                    "status": "CUSTOM_OVERRIDE",
                    "source": "administrative_record",
                    **payload,
                })
        return results

    @classmethod
    async def update_merchant_risk(cls, slug, is_blacklisted, is_verified, risk_percent, admin_note, admin_email, db):
        payload = {'is_blacklisted': is_blacklisted, 'is_verified': is_verified,
                   'risk_percent': risk_percent, 'admin_note': admin_note}
        await cls.save_state(db, 'merchant:'+slug, payload)
        await cls.record_audit(db, admin_email, 'UPDATE_MERCHANT_RISK', slug, admin_note)
        await db.commit()
        return {'success': True, 'slug': slug, 'override': payload}

    @classmethod
    async def list_community_posts(cls, db):
        overrides = {r.key.removeprefix('community_post:'): r.payload for r in (await db.scalars(select(AdminRecord).where(AdminRecord.key.like('community_post:%')))).all() if isinstance(r.payload, dict)}
        results = []
        for p in COMMUNITY_POSTS_STORE:
            override = overrides.get(p["id"], {})
            is_pinned = override.get("is_pinned", p.get("is_pinned", False))
            is_hidden = override.get("is_hidden", p.get("is_hidden", False))
            status_label = "PINNED" if is_pinned else "HIDDEN" if is_hidden else "ACTIVE"
            results.append({
                "id": p["id"],
                "title": p["title"],
                "status": status_label,
                "author_name": p["author_name"],
                "category": p["category"],
                "merchant_name": p.get("merchant_name", "—"),
                "disputed_amount_bdt": p.get("disputed_amount_bdt", 0),
                "me_too_count": p.get("me_too_count", 0),
                "comments_count": len(p.get("comments", [])),
                "is_pinned": is_pinned,
                "is_hidden": is_hidden,
                "created_at": p.get("created_at", "Recently"),
            })
        return results

    @classmethod
    async def moderate_community_post(cls, post_id, action, admin_email, db):
        target_post = None
        for p in COMMUNITY_POSTS_STORE:
            if p["id"] == post_id:
                target_post = p
                break
        if not target_post:
            raise HTTPException(404, f'Community post {post_id} not found to moderate.')

        key = f"community_post:{post_id}"
        existing = (await cls.state(db, key)) or {}
        if action == "pin":
            existing["is_pinned"] = True
            target_post["is_pinned"] = True
        elif action == "unpin":
            existing["is_pinned"] = False
            target_post["is_pinned"] = False
        elif action == "hide":
            existing["is_hidden"] = True
            target_post["is_hidden"] = True
        elif action == "unhide":
            existing["is_hidden"] = False
            target_post["is_hidden"] = False
        elif action == "dismiss_reports":
            existing["report_count"] = 0
            target_post["report_count"] = 0
        else:
            raise HTTPException(422, f"Unsupported action: {action}")

        await cls.save_state(db, key, existing)
        await cls.record_audit(db, admin_email, 'MODERATE_COMMUNITY_POST', post_id, f"Action: {action}")
        await db.commit()
        return {"success": True, "post_id": post_id, "action": action, "post_state": existing}

    @classmethod
    async def list_alerts(cls, db, active_only=True):
        records = list((await db.scalars(select(AdminRecord).where(AdminRecord.key.like('alert:%'))
                                        .order_by(AdminRecord.updated_at.desc()))).all())
        return [record.payload for record in records if not active_only or record.payload.get('active')]

    @classmethod
    async def create_or_toggle_alert(cls, title, title_en, severity, message, active, admin_email, db):
        alert = {'id': 'alert-'+uuid.uuid4().hex, 'title': title, 'title_en': title_en,
                 'severity': severity, 'active': active, 'message': message,
                 'created_at': datetime.datetime.now(datetime.UTC).isoformat()}
        await cls.save_state(db, alert['id'].replace('alert-', 'alert:', 1), alert)
        await cls.record_audit(db, admin_email, 'CREATE_PLATFORM_ALERT', alert['id'],
                               f'Severity: {severity}; active: {active}')
        await db.commit()
        return {'success': True, 'alert': alert}

    @classmethod
    async def update_alert(cls, alert_id, payload, admin_email, db):
        key = alert_id.replace('alert-', 'alert:', 1)
        existing = await cls.state(db, key)
        if not existing or existing.get('id') != alert_id:
            raise HTTPException(404, 'Notice not found.')
        alert = {**existing, **payload}
        await cls.save_state(db, key, alert)
        await cls.record_audit(db, admin_email, 'UPDATE_PLATFORM_ALERT', alert_id,
                               f"Active: {alert['active']}")
        await db.commit()
        return {'success': True, 'alert': alert}

    @classmethod
    async def get_audit_logs(cls, db):
        records = (await db.scalars(select(AdminAuditEntry).order_by(AdminAuditEntry.created_at.desc()).limit(200))).all()
        return [{**record.payload, 'id': record.id} for record in records]
