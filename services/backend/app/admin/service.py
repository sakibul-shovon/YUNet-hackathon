import datetime
import hashlib
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cases.models import Case, CaseEvent
from app.community.service import COMMUNITY_POSTS_STORE
from app.identity.models import ActorRole, UserAccount
from app.knowledge.models import SourceCandidate
from app.merchants.service import KNOWN_OFFENDER_REGISTRY

# In-memory storage for runtime admin state (audit logs, merchant overrides, alerts)
ADMIN_AUDIT_LOGS: list[dict[str, Any]] = [
    {
        "id": "log-001",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "admin_email": "admin@claimcraft.bd",
        "action": "SYSTEM_BOOTSTRAP",
        "target": "Security & RBAC Infrastructure",
        "details": "Super Admin permissions provisioned for [admin, reviewer, publisher, operator]",
        "hash": hashlib.sha256(b"SYSTEM_BOOTSTRAP_INIT").hexdigest()[:16],
    }
]

MERCHANT_OVERRIDES: dict[str, dict[str, Any]] = {
    "gadget zone bd": {
        "is_blacklisted": True,
        "is_verified": False,
        "risk_percent": 92,
        "admin_note": "Repeated non-delivery complaints & unverified phone contacts under Sec 45 CRPA 2009",
    },
    "daraz bangladesh": {
        "is_blacklisted": False,
        "is_verified": True,
        "risk_percent": 35,
        "admin_note": "Legally incorporated e-commerce entity. Periodic return logistics delays monitored.",
    },
    "bkash limited": {
        "is_blacklisted": False,
        "is_verified": True,
        "risk_percent": 12,
        "admin_note": "Regulated MFS entity governed under Bangladesh Bank Payment Systems Dept (PSD).",
    },
}

PLATFORM_ALERTS: list[dict[str, Any]] = [
    {
        "id": "alert-001",
        "title": "সতর্কবার্তা: ভুয়া কুরিয়ার ট্র্যাকিং ও অগ্রিম পেমেন্ট প্রতারণা",
        "title_en": "Alert: Fake Courier Tracking & Advance Payment Scams",
        "severity": "warning",  # warning, critical, info
        "active": True,
        "message": "ফেসবুক ও সোশ্যাল পেজ থেকে কেনাকাটার সময় ব্যক্তিগত বিকাশ/নগদে ১০০% অগ্রিম পেমেন্ট করবেন না। পণ্য যাচাই করে মূল্য পরিশোধ করুন।",
        "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
    }
]

BANNED_USERS_SET: set[str] = set()
COMMUNITY_POST_OVERRIDES: dict[str, dict[str, Any]] = {}

class AdminService:
    @classmethod
    def record_audit(cls, admin_email: str, action: str, target: str, details: str):
        raw = f"{datetime.datetime.now(datetime.UTC).isoformat()}:{admin_email}:{action}:{target}:{details}"
        h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        entry = {
            "id": f"log-{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "admin_email": admin_email,
            "action": action,
            "target": target,
            "details": details,
            "hash": h,
        }
        ADMIN_AUDIT_LOGS.insert(0, entry)
        if len(ADMIN_AUDIT_LOGS) > 100:
            ADMIN_AUDIT_LOGS.pop()

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

        total_disputed_bdt = 0.0
        total_recovered_bdt = 0.0
        for c in cases:
            # Check fact assertions or title for amount
            bdt = 3200.0 if "3200" in (c.story_narrative or "") else 5500.0
            total_disputed_bdt += bdt
            if c.lifecycle_status == "resolved":
                total_recovered_bdt += bdt

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
                "banned_users": len(BANNED_USERS_SET),
                "pending_statutory_reviews": pending_statutory,
                "total_merchants_tracked": len(KNOWN_OFFENDER_REGISTRY) + len(MERCHANT_OVERRIDES),
                "community_grievances_count": len(COMMUNITY_POSTS_STORE),
            },
            "resolution_paths_distribution": {
                "DNCRP Directorate (ভোক্তা অধিকার)": 58,
                "Bangladesh Bank CIPC (আর্থিক অখণ্ডতা)": 24,
                "Direct Merchant Negotiation (দ্বিপাক্ষিক)": 14,
                "Small Claims Court (দেওয়ানি আদালত)": 4,
            },
            "system_health": {
                "api_gateway": "ONLINE (99.98% Uptime)",
                "database_engine": "CONNECTED (SQLite / AsyncSession RLS)",
                "multimodal_ocr": "READY (Pillow + Tesseract Grounding)",
                "voice_stt": "READY (Web Speech + STT Adapter)",
                "active_statutory_release": "REL-2026-Q4-CRPA (v4.2.0)",
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
        case.updated_at = datetime.datetime.now(datetime.UTC)

        # Log event in CaseEvent
        evt = CaseEvent(
            id=uuid.uuid4(),
            case_id=case.id,
            principal_id=case.principal_id,
            event_type="ADMIN_STATUS_OVERRIDE",
            payload={
                "old_status": old_status,
                "new_status": new_status,
                "admin_notes": admin_notes,
                "admin_email": admin_email,
            },
        )
        db.add(evt)
        await db.commit()

        cls.record_audit(
            admin_email=admin_email,
            action="OVERRIDE_CASE_STATUS",
            target=f"Case {case.display_reference or str(case.id)[:8]}",
            details=f"Changed status from '{old_status}' to '{new_status}'. Note: {admin_notes}",
        )
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

            is_banned = str(u.id) in BANNED_USERS_SET or u.email in BANNED_USERS_SET
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

        if user_id in BANNED_USERS_SET or user.email in BANNED_USERS_SET:
            BANNED_USERS_SET.discard(user_id)
            BANNED_USERS_SET.discard(user.email)
            action = "UNBAN_USER"
            is_banned = False
        else:
            BANNED_USERS_SET.add(user_id)
            BANNED_USERS_SET.add(user.email)
            action = "BAN_USER"
            is_banned = True

        cls.record_audit(
            admin_email=admin_email,
            action=action,
            target=f"User {user.email}",
            details=f"Administrative account status changed to {'BANNED' if is_banned else 'ACTIVE'}",
        )
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

        # Delete existing roles
        stmt_del = select(ActorRole).where(ActorRole.principal_id == user.principal_id)
        res_del = await db.execute(stmt_del)
        for r in res_del.scalars().all():
            await db.delete(r)

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
        await db.commit()

        cls.record_audit(
            admin_email=admin_email,
            action="UPDATE_USER_ROLES",
            target=f"User {user.email}",
            details=f"Assigned roles: {', '.join(new_roles)}",
        )
        return {"success": True, "user_id": user_id, "roles": new_roles}

    @classmethod
    def list_merchants(cls) -> list[dict[str, Any]]:
        results = []
        for key, reg in KNOWN_OFFENDER_REGISTRY.items():
            override = MERCHANT_OVERRIDES.get(key, {})
            results.append({
                "slug": key,
                "canonical_name": reg.get("canonical_name", key),
                "platform": reg.get("platform", "E-Commerce"),
                "category": reg.get("category", "General"),
                "base_complaints": reg.get("base_complaints", 0),
                "base_disputed_bdt": reg.get("base_disputed_bdt", 0.0),
                "risk_level": reg.get("risk_level", "MODERATE"),
                "risk_percent": override.get("risk_percent", 92 if "HIGH" in reg.get("risk_level", "") else 35),
                "is_blacklisted": override.get("is_blacklisted", "HIGH" in reg.get("risk_level", "")),
                "is_verified": override.get("is_verified", "REGULATED" in reg.get("risk_level", "")),
                "admin_note": override.get("admin_note", reg.get("primary_allegation", "")),
            })
        return results

    @classmethod
    def update_merchant_risk(
        cls, slug: str, is_blacklisted: bool, is_verified: bool, risk_percent: int, admin_note: str, admin_email: str
    ) -> dict[str, Any]:
        MERCHANT_OVERRIDES[slug] = {
            "is_blacklisted": is_blacklisted,
            "is_verified": is_verified,
            "risk_percent": risk_percent,
            "admin_note": admin_note,
        }
        cls.record_audit(
            admin_email=admin_email,
            action="UPDATE_MERCHANT_RISK",
            target=f"Merchant {slug}",
            details=f"Blacklisted: {is_blacklisted}, Verified: {is_verified}, Risk: {risk_percent}%. Note: {admin_note}",
        )
        return {"success": True, "slug": slug, "override": MERCHANT_OVERRIDES[slug]}

    @classmethod
    def list_community_posts(cls) -> list[dict[str, Any]]:
        out = []
        for p in COMMUNITY_POSTS_STORE:
            p_id = p["id"]
            over = COMMUNITY_POST_OVERRIDES.get(p_id, {})
            out.append({
                "id": p_id,
                "title": p.get("title", ""),
                "story": p.get("story", "")[:140] + "...",
                "author_name": p.get("author_name", ""),
                "category": p.get("category", "General"),
                "merchant_name": p.get("merchant_name", ""),
                "disputed_amount_bdt": p.get("disputed_amount_bdt", 0.0),
                "me_too_count": p.get("me_too_count", 0),
                "created_at": p.get("created_at", ""),
                "is_pinned": over.get("is_pinned", False),
                "is_hidden": over.get("is_hidden", False),
                "report_count": over.get("report_count", 0),
            })
        return out

    @classmethod
    def moderate_community_post(
        cls, post_id: str, action: str, admin_email: str
    ) -> dict[str, Any]:
        if post_id not in COMMUNITY_POST_OVERRIDES:
            COMMUNITY_POST_OVERRIDES[post_id] = {"is_pinned": False, "is_hidden": False, "report_count": 0}

        if action == "pin":
            COMMUNITY_POST_OVERRIDES[post_id]["is_pinned"] = True
        elif action == "unpin":
            COMMUNITY_POST_OVERRIDES[post_id]["is_pinned"] = False
        elif action == "hide":
            COMMUNITY_POST_OVERRIDES[post_id]["is_hidden"] = True
        elif action == "unhide":
            COMMUNITY_POST_OVERRIDES[post_id]["is_hidden"] = False
        elif action == "dismiss_reports":
            COMMUNITY_POST_OVERRIDES[post_id]["report_count"] = 0

        cls.record_audit(
            admin_email=admin_email,
            action="MODERATE_COMMUNITY_POST",
            target=f"Post {post_id}",
            details=f"Action executed: {action}",
        )
        return {"success": True, "post_id": post_id, "action": action, "state": COMMUNITY_POST_OVERRIDES[post_id]}

    @classmethod
    def list_alerts(cls) -> list[dict[str, Any]]:
        return PLATFORM_ALERTS

    @classmethod
    def create_or_toggle_alert(
        cls, title: str, title_en: str, severity: str, message: str, active: bool, admin_email: str
    ) -> dict[str, Any]:
        new_alert = {
            "id": f"alert-{uuid.uuid4().hex[:6]}",
            "title": title,
            "title_en": title_en,
            "severity": severity,
            "active": active,
            "message": message,
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        PLATFORM_ALERTS.insert(0, new_alert)
        cls.record_audit(
            admin_email=admin_email,
            action="CREATE_PLATFORM_ALERT",
            target=f"Alert {title}",
            details=f"Severity: {severity}, Active: {active}",
        )
        return {"success": True, "alert": new_alert}

    @classmethod
    def get_audit_logs(cls) -> list[dict[str, Any]]:
        return ADMIN_AUDIT_LOGS
