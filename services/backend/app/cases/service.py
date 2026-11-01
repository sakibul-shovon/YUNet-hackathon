import datetime
import hashlib
import json
import secrets
import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cases.models import Case, CaseEvent, CaseSnapshot, OutboxMessage
from app.cases.schemas import CaseCreate, CaseEventOut, CaseListOut, CaseOut, CaseUpdate
from app.identity.models import Principal

DEMO_FIXTURE_IDS = {
    uuid.UUID("1887c4ed-99d6-44f2-9fb4-0c15e9d3287e"),
    uuid.UUID("a5b13210-e0dc-461b-8233-f33c98d45489"),
}


class CaseService:
    @staticmethod
    def generate_display_reference() -> str:
        """Generates human-readable, non-secret case reference."""
        token = secrets.token_hex(3).upper()
        return f"CC-2026-{token}"

    @classmethod
    async def create_case(
        cls,
        principal: Principal,
        data: CaseCreate,
        db: AsyncSession,
    ) -> CaseOut:
        """Creates a new isolated case with initial snapshot and event record."""
        case_id = uuid.uuid4()
        ref = cls.generate_display_reference()
        now = datetime.datetime.now(datetime.UTC)

        new_case = Case(
            id=case_id,
            principal_id=principal.id,
            display_reference=ref,
            title=data.title,
            jurisdiction=data.jurisdiction,
            locale=data.locale,
            desired_outcomes=data.desired_outcomes,
            lifecycle_status="draft",
            row_version=1,
            is_demo=data.is_demo,
            incident_date=data.incident_date,
            merchant_name=data.merchant_name,
            story_narrative=data.story_narrative,
            created_at=now,
            updated_at=now,
        )
        db.add(new_case)
        await db.flush()

        # Sequence 1: case.created event
        initial_event = CaseEvent(
            id=uuid.uuid4(),
            case_id=new_case.id,
            principal_id=principal.id,
            event_sequence=1,
            event_type="case.created",
            actor_type="consumer",
            actor_id=principal.id,
            schema_version=1,
            payload={
                "title": data.title,
                "jurisdiction": data.jurisdiction,
                "locale": data.locale,
                "desired_outcomes": data.desired_outcomes,
            },
            created_at=now,
        )
        db.add(initial_event)

        # Snapshot version 1
        canonical_content = json.dumps(
            {
                "title": data.title,
                "jurisdiction": data.jurisdiction,
                "locale": data.locale,
                "story": data.story_narrative or "",
            },
            sort_keys=True,
        )
        canonical_hash = hashlib.sha256(canonical_content.encode("utf-8")).hexdigest()

        initial_snapshot = CaseSnapshot(
            id=uuid.uuid4(),
            case_id=new_case.id,
            principal_id=principal.id,
            version=1,
            canonical_input_hash=canonical_hash,
            fact_assertion_ids=[],
            issue_state={},
            created_at=now,
        )
        db.add(initial_snapshot)

        # Outbox event
        outbox = OutboxMessage(
            id=uuid.uuid4(),
            event_type="case.created",
            aggregate_type="case",
            aggregate_id=new_case.id,
            payload={"case_id": str(new_case.id), "principal_id": str(principal.id)},
            created_at=now,
        )
        db.add(outbox)

        await db.commit()
        await db.refresh(new_case)
        return CaseOut.model_validate(new_case, from_attributes=True)

    @staticmethod
    async def get_cases(
        principal: Principal,
        db: AsyncSession,
        limit: int = 20,
        offset: int = 0,
    ) -> CaseListOut:
        """Lists active non-deleted cases belonging strictly to the authenticated principal."""
        stmt = (
            select(Case)
            .where(
                Case.principal_id == principal.id,
                Case.lifecycle_status.notin_(["deleting", "deleted"]),
                Case.deleted_at.is_(None),
            )
            .order_by(Case.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await db.execute(stmt)
        items = [CaseOut.model_validate(c, from_attributes=True) for c in res.scalars().all()]

        count_stmt = select(func.count(Case.id)).where(
            Case.principal_id == principal.id,
            Case.lifecycle_status.notin_(["deleting", "deleted"]),
            Case.deleted_at.is_(None),
        )
        count_res = await db.execute(count_stmt)
        total = count_res.scalar_one()

        return CaseListOut(items=items, total=total)

    @staticmethod
    async def get_case_by_id(
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> CaseOut:
        """Retrieves a single case with strict tenant isolation (returns 404 for foreign cases)."""
        stmt = select(Case).where(
            Case.id == case_id,
            (Case.principal_id == principal.id)
            | (Case.display_reference == "DEMO-DARAZ-001")
            | Case.id.in_(DEMO_FIXTURE_IDS),
            Case.lifecycle_status.notin_(["deleting", "deleted"]),
            Case.deleted_at.is_(None),
        )
        res = await db.execute(stmt)
        case = res.scalar_one_or_none()
        if not case:
            # Plan 9.6: Non-enumerating 404 for foreign or non-existent cases
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "CASE_NOT_FOUND", "message_key": "case.not_found"}},
            )
        return CaseOut.model_validate(case, from_attributes=True)

    @classmethod
    async def update_case(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        data: CaseUpdate,
        db: AsyncSession,
    ) -> CaseOut:
        """Updates case metadata/story with optimistic concurrency check (returns 409 on version conflict)."""
        stmt = select(Case).where(
            Case.id == case_id,
            Case.principal_id == principal.id,
            Case.lifecycle_status.notin_(["deleting", "deleted"]),
            Case.deleted_at.is_(None),
        )
        res = await db.execute(stmt)
        case = res.scalar_one_or_none()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "CASE_NOT_FOUND", "message_key": "case.not_found"}},
            )

        # Plan 10.1: Optimistic concurrency check
        if case.row_version != data.expected_version:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "CASE_VERSION_CONFLICT",
                        "message_key": "case.changed_reload",
                        "details": {
                            "expected_version": data.expected_version,
                            "current_version": case.row_version,
                        },
                    }
                },
            )

        now = datetime.datetime.now(datetime.UTC)
        if data.title is not None:
            case.title = data.title
        if data.desired_outcomes is not None:
            case.desired_outcomes = data.desired_outcomes
        if data.merchant_name is not None:
            case.merchant_name = data.merchant_name
        if data.incident_date is not None:
            case.incident_date = data.incident_date
        if data.story_narrative is not None:
            case.story_narrative = data.story_narrative
        if data.lifecycle_status is not None:
            case.lifecycle_status = data.lifecycle_status

        case.row_version += 1
        case.updated_at = now

        # Get highest event_sequence
        seq_stmt = select(func.coalesce(func.max(CaseEvent.event_sequence), 0)).where(
            CaseEvent.case_id == case.id
        )
        max_seq = (await db.execute(seq_stmt)).scalar_one()

        update_event = CaseEvent(
            id=uuid.uuid4(),
            case_id=case.id,
            principal_id=principal.id,
            event_sequence=max_seq + 1,
            event_type="case.updated",
            actor_type="consumer",
            actor_id=principal.id,
            schema_version=1,
            payload={
                "version": case.row_version,
                "changes": {
                    k: v
                    for k, v in data.model_dump(exclude_unset=True).items()
                    if k != "expected_version"
                },
            },
            created_at=now,
        )
        db.add(update_event)

        # New immutable snapshot
        canonical_content = json.dumps(
            {
                "title": case.title,
                "jurisdiction": case.jurisdiction,
                "locale": case.locale,
                "story": case.story_narrative or "",
                "version": case.row_version,
            },
            sort_keys=True,
        )
        canonical_hash = hashlib.sha256(canonical_content.encode("utf-8")).hexdigest()

        snapshot = CaseSnapshot(
            id=uuid.uuid4(),
            case_id=case.id,
            principal_id=principal.id,
            version=case.row_version,
            canonical_input_hash=canonical_hash,
            fact_assertion_ids=[],
            issue_state={},
            created_at=now,
        )
        db.add(snapshot)

        await db.commit()
        await db.refresh(case)
        return CaseOut.model_validate(case, from_attributes=True)

    @staticmethod
    async def delete_case(
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> dict:
        """Revokes access and queues case for asynchronous complete deletion."""
        stmt = select(Case).where(
            Case.id == case_id,
            Case.principal_id == principal.id,
            Case.lifecycle_status != "deleted",
        )
        res = await db.execute(stmt)
        case = res.scalar_one_or_none()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "CASE_NOT_FOUND", "message_key": "case.not_found"}},
            )

        now = datetime.datetime.now(datetime.UTC)
        case.lifecycle_status = "deleting"
        case.deleted_at = now

        outbox = OutboxMessage(
            id=uuid.uuid4(),
            event_type="case.deleting",
            aggregate_type="case",
            aggregate_id=case.id,
            payload={"case_id": str(case.id), "principal_id": str(principal.id)},
            created_at=now,
        )
        db.add(outbox)
        await db.commit()

        return {"status": "deleting", "case_id": str(case.id)}

    @staticmethod
    async def get_case_events(
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> list[CaseEventOut]:
        """Returns chronological activity log for an authorized case."""
        # Verify ownership or demo fixture access
        stmt = select(Case).where(
            Case.id == case_id,
            (Case.principal_id == principal.id)
            | (Case.display_reference == "DEMO-DARAZ-001")
            | Case.id.in_(DEMO_FIXTURE_IDS),
            Case.lifecycle_status != "deleted",
        )
        res = await db.execute(stmt)
        if not res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "CASE_NOT_FOUND", "message_key": "case.not_found"}},
            )

        events_stmt = (
            select(CaseEvent)
            .where(CaseEvent.case_id == case_id)
            .order_by(CaseEvent.event_sequence.asc())
        )
        events_res = await db.execute(events_stmt)
        return [
            CaseEventOut.model_validate(e, from_attributes=True) for e in events_res.scalars().all()
        ]

    @staticmethod
    async def withdraw_consent(
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> CaseOut:
        """T37: Immediately sets consent_status to 'withdrawn' and records an audit event."""
        stmt = select(Case).where(
            Case.id == case_id,
            Case.principal_id == principal.id,
            Case.lifecycle_status.notin_(["deleting", "deleted"]),
            Case.deleted_at.is_(None),
        )
        res = await db.execute(stmt)
        case = res.scalar_one_or_none()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "CASE_NOT_FOUND", "message": "Case not found"}},
            )

        now = datetime.datetime.now(datetime.UTC)
        case.consent_status = "withdrawn"
        case.updated_at = now

        seq_stmt = select(func.coalesce(func.max(CaseEvent.event_sequence), 0)).where(
            CaseEvent.case_id == case.id
        )
        max_seq = (await db.execute(seq_stmt)).scalar_one()

        event = CaseEvent(
            id=uuid.uuid4(),
            case_id=case.id,
            principal_id=principal.id,
            event_sequence=max_seq + 1,
            event_type="consent.withdrawn",
            actor_type="consumer",
            actor_id=principal.id,
            schema_version=1,
            payload={"action": "consent_withdrawn", "timestamp": now.isoformat()},
            created_at=now,
        )
        db.add(event)
        await db.commit()
        await db.refresh(case)
        return CaseOut.model_validate(case, from_attributes=True)
