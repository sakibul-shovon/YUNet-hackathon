import datetime
import hashlib
import json
import uuid
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.action_dag import ActionDAGService
from app.cases.models import CaseEvent, CaseReminder, CaseSnapshot, ExternalReference
from app.facts.models import FactAssertion
from app.facts.service import FactService
from app.identity.models import Principal
from app.policy.engine import ProceduralAssessmentEngine


class ExternalUpdateCreate(BaseModel):
    update_type: str  # 'seller_response', 'portal_submission', 'hearing_notice', 'settlement_reached'
    authority_or_channel: str  # e.g., 'merchant_direct', 'dncrp_ccms', 'bb_cipc'
    description: str
    reference_number: str | None = None
    outcome_status: str | None = None  # 'agreed', 'refused', 'under_review', 'resolved'
    additional_facts: dict[str, Any] = Field(default_factory=dict)
    expected_version: int = Field(..., description="Mandatory expected row_version for optimistic concurrency (T41)")


class SemanticDecisionDiff(BaseModel):
    prior_version: int
    new_version: int
    prior_primary_action: str
    new_primary_action: str
    is_decision_changed: bool
    changed_routes: list[dict[str, Any]] = Field(default_factory=list)
    unchanged_routes: list[str] = Field(default_factory=list)
    changed_actions: list[str] = Field(default_factory=list)
    unchanged_actions: list[str] = Field(default_factory=list)


class TimelineEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    event_sequence: int
    event_type: str
    actor_type: str
    origin: str  # 'user_reported', 'official_receipt', 'system_event'
    title: str
    description: str
    reference_number: str | None = None
    created_at: str
    decision_diff: SemanticDecisionDiff | None = None


class CaseSnapshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    version: int
    canonical_input_hash: str
    issue_state: dict[str, Any]
    created_at: str


class ReminderCreate(BaseModel):
    reminder_title: str
    remind_at: str  # ISO 8601 UTC
    category: str = "personal_follow_up"  # 'personal_follow_up', 'seller_response_sla', 'portal_check'
    notes: str | None = None


class ReminderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    reminder_title: str
    remind_at: str
    category: str
    notes: str | None = None
    is_completed: bool
    is_legal_caution: bool = False  # T40 Invariant: personal timer is distinct from statutory caution
    disclaimer_notice: str = (
        "Personal reminder for tracking convenience only. "
        "Does not alter or guarantee statutory limitation periods under CRPA 2009 Section 60 (T40)."
    )
    created_at: str


class TimelineService:
    """P10.1 & P10.2: Living Case timeline, user-reported updates,

    semantic decision diffs (T38, T39) and reminders (T40).
    """

    @classmethod
    async def record_user_update(
        cls,
        case_id: uuid.UUID,
        payload: ExternalUpdateCreate,
        principal: Principal,
        db: AsyncSession,
    ) -> TimelineEventOut:
        case = await FactService.get_authorized_case(case_id, principal, db)

        # 1. Stale Tab Race Prevention (T41)
        if case.row_version != payload.expected_version:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Stale tab update rejected: case has been updated (expected version {payload.expected_version}, current {case.row_version}). Please refresh.",
            )

        # 2. Capture Prior Assessment Snapshot
        prior_assessment = await ProceduralAssessmentEngine.assess_case(case, db)
        prior_dag = await ActionDAGService.build_action_dag(case_id, principal, db)
        prior_version = case.row_version

        # 3. Invariant T38: User-reported external reference
        ref_record = None
        if payload.reference_number:
            ref_record = ExternalReference(
                case_id=case.id,
                principal_id=principal.id,
                authority_or_channel=payload.authority_or_channel,
                encrypted_reference=payload.reference_number,
                origin="user_reported",  # T38: Explicitly marked user_reported, never fake official
                reported_event_date=datetime.date.today().isoformat(),
            )
            db.add(ref_record)

        # 4. Apply Additional Facts if present
        for k, v in payload.additional_facts.items():
            f_type = "boolean" if isinstance(v, bool) else ("number" if isinstance(v, (int, float)) else "string")
            existing_f = await db.execute(
                select(FactAssertion).where(
                    FactAssertion.case_id == case.id,
                    FactAssertion.field_name == k,
                    FactAssertion.is_active.is_(True),
                )
            )
            f_row = existing_f.scalar_one_or_none()
            if f_row:
                f_row.is_active = False

            new_assertion = FactAssertion(
                case_id=case.id,
                field_name=k,
                field_type=f_type,
                typed_value=v,
                original_text=str(v),
                origin="user_statement",
                asserting_actor_id=principal.id,
                created_case_version=case.row_version,
                is_active=True,
            )
            db.add(new_assertion)

        await db.flush()

        # 5. Capture New Assessment and Semantic Decision Diff (T39)
        new_assessment = await ProceduralAssessmentEngine.assess_case(case, db)
        new_dag = await ActionDAGService.build_action_dag(case_id, principal, db)
        new_version = prior_version + 1

        # Calculate semantic diff
        prior_routes = {r.issue_type: r for r in prior_assessment.routes}
        new_routes = {r.issue_type: r for r in new_assessment.routes}

        changed_routes = []
        unchanged_routes = []
        for issue_type, new_r in new_routes.items():
            old_r = prior_routes.get(issue_type)
            if not old_r or old_r.status != new_r.status or old_r.reasons != new_r.reasons:
                changed_routes.append({
                    "issue_type": issue_type,
                    "old_status": old_r.status if old_r else None,
                    "new_status": new_r.status,
                })
            else:
                unchanged_routes.append(issue_type)

        prior_actions = {n.action_id: n for n in prior_dag.nodes}
        new_actions = {n.action_id: n for n in new_dag.nodes}

        changed_actions = []
        unchanged_actions = []
        for action_id, new_act in new_actions.items():
            old_act = prior_actions.get(action_id)
            if not old_act or old_act.status != new_act.status or old_act.is_primary != new_act.is_primary:
                changed_actions.append(action_id)
            else:
                unchanged_actions.append(action_id)

        is_decision_changed = (
            prior_dag.primary_action_id != new_dag.primary_action_id or
            len(changed_routes) > 0 or
            len(changed_actions) > 0
        )

        diff = SemanticDecisionDiff(
            prior_version=prior_version,
            new_version=new_version,
            prior_primary_action=prior_dag.primary_action_id,
            new_primary_action=new_dag.primary_action_id,
            is_decision_changed=is_decision_changed,
            changed_routes=changed_routes,
            unchanged_routes=unchanged_routes,
            changed_actions=changed_actions,
            unchanged_actions=unchanged_actions,
        )

        # 6. Save Immutable Snapshot
        stmt_f = select(FactAssertion.id).where(FactAssertion.case_id == case.id, FactAssertion.is_active.is_(True))
        res_f = await db.execute(stmt_f)
        fact_ids = [str(fid) for fid in res_f.scalars().all()]

        canonical_hash = hashlib.sha256(
            json.dumps({"facts": fact_ids, "version": new_version}, sort_keys=True).encode()
        ).hexdigest()

        snapshot = CaseSnapshot(
            case_id=case.id,
            principal_id=principal.id,
            version=new_version,
            canonical_input_hash=canonical_hash,
            fact_assertion_ids=fact_ids,
            issue_state={
                "primary_action": new_assessment.primary_action,
                "routes": [r.model_dump() for r in new_assessment.routes],
            },
        )
        db.add(snapshot)

        # 7. Record Case Event
        seq_stmt = select(func.coalesce(func.max(CaseEvent.event_sequence), 0)).where(CaseEvent.case_id == case.id)
        next_seq = (await db.scalar(seq_stmt)) + 1

        event_payload = {
            "title": f"External Update: {payload.update_type.replace('_', ' ').title()}",
            "description": payload.description,
            "authority_or_channel": payload.authority_or_channel,
            "reference_number": payload.reference_number,
            "origin": "user_reported",
            "decision_diff": diff.model_dump(),
        }

        event = CaseEvent(
            case_id=case.id,
            principal_id=principal.id,
            event_sequence=next_seq,
            event_type="user_reported_update",
            actor_type="consumer",
            schema_version=1,
            payload=event_payload,
        )
        db.add(event)

        # Bump row version
        case.row_version = new_version
        await db.commit()
        await db.refresh(event)

        return TimelineEventOut(
            id=event.id,
            case_id=case.id,
            event_sequence=event.event_sequence,
            event_type=event.event_type,
            actor_type=event.actor_type,
            origin="user_reported",
            title=event_payload["title"],
            description=event_payload["description"],
            reference_number=event_payload.get("reference_number"),
            created_at=event.created_at.isoformat(),
            decision_diff=diff,
        )

    @classmethod
    async def get_case_timeline(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> list[TimelineEventOut]:
        case = await FactService.get_authorized_case(case_id, principal, db)

        stmt = select(CaseEvent).where(CaseEvent.case_id == case.id).order_by(CaseEvent.event_sequence.desc())
        res = await db.execute(stmt)
        events = res.scalars().all()

        timeline: list[TimelineEventOut] = []
        for e in events:
            p = e.payload or {}
            diff_dict = p.get("decision_diff")
            diff_obj = SemanticDecisionDiff(**diff_dict) if diff_dict else None

            timeline.append(TimelineEventOut(
                id=e.id,
                case_id=e.case_id,
                event_sequence=e.event_sequence,
                event_type=e.event_type,
                actor_type=e.actor_type,
                origin=p.get("origin", "system_event"),
                title=p.get("title", e.event_type.replace("_", " ").title()),
                description=p.get("description", ""),
                reference_number=p.get("reference_number"),
                created_at=e.created_at.isoformat(),
                decision_diff=diff_obj,
            ))

        return timeline

    @classmethod
    async def get_case_snapshots(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> list[CaseSnapshotOut]:
        case = await FactService.get_authorized_case(case_id, principal, db)

        stmt = select(CaseSnapshot).where(CaseSnapshot.case_id == case.id).order_by(CaseSnapshot.version.desc())
        res = await db.execute(stmt)
        snapshots = res.scalars().all()

        return [
            CaseSnapshotOut(
                id=s.id,
                case_id=s.case_id,
                version=s.version,
                canonical_input_hash=s.canonical_input_hash,
                issue_state=s.issue_state,
                created_at=s.created_at.isoformat(),
            )
            for s in snapshots
        ]

    @classmethod
    async def create_reminder(
        cls,
        case_id: uuid.UUID,
        payload: ReminderCreate,
        principal: Principal,
        db: AsyncSession,
    ) -> ReminderOut:
        """P10.4 & T40: User-selected follow-up reminders with timezone-safe scheduling."""
        case = await FactService.get_authorized_case(case_id, principal, db)

        reminder = CaseReminder(
            case_id=case.id,
            principal_id=principal.id,
            reminder_title=payload.reminder_title,
            remind_at=payload.remind_at,
            category=payload.category,
            notes=payload.notes,
            is_completed=False,
        )
        db.add(reminder)
        await db.commit()
        await db.refresh(reminder)

        return ReminderOut(
            id=reminder.id,
            case_id=reminder.case_id,
            reminder_title=reminder.reminder_title,
            remind_at=reminder.remind_at,
            category=reminder.category,
            notes=reminder.notes,
            is_completed=reminder.is_completed,
            is_legal_caution=False,
            created_at=reminder.created_at.isoformat(),
        )

    @classmethod
    async def list_reminders(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> list[ReminderOut]:
        case = await FactService.get_authorized_case(case_id, principal, db)

        stmt = select(CaseReminder).where(
            CaseReminder.case_id == case.id,
            CaseReminder.is_completed.is_(False),
        ).order_by(CaseReminder.created_at.desc())
        res = await db.execute(stmt)
        reminders = res.scalars().all()

        return [
            ReminderOut(
                id=r.id,
                case_id=r.case_id,
                reminder_title=r.reminder_title,
                remind_at=r.remind_at,
                category=r.category,
                notes=r.notes,
                is_completed=r.is_completed,
                is_legal_caution=False,
                created_at=r.created_at.isoformat(),
            )
            for r in reminders
        ]

    @classmethod
    async def cancel_reminder(
        cls,
        case_id: uuid.UUID,
        reminder_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> None:
        case = await FactService.get_authorized_case(case_id, principal, db)

        stmt = select(CaseReminder).where(
            CaseReminder.id == reminder_id,
            CaseReminder.case_id == case.id,
        )
        res = await db.execute(stmt)
        reminder = res.scalar_one_or_none()
        if not reminder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found.")

        await db.delete(reminder)
        await db.commit()
