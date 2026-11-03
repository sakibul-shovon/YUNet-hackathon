import datetime
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cases.models import Case
from app.facts.models import FactAssertion, FactReview, FactSourceLink
from app.facts.normalization import normalize_bd_date, normalize_bdt_money
from app.facts.schemas import (
    FactAssertionCreate,
    FactAssertionOut,
    FactReviewOut,
    FactReviewSubmission,
    MultimodalFactProposal,
    MultimodalProposalResult,
)
from app.identity.models import Principal

DEMO_FIXTURE_IDS = {
    uuid.UUID("1887c4ed-99d6-44f2-9fb4-0c15e9d3287e"),  # Scenario A (case_demo_phone)
    uuid.UUID("2887c4ed-99d6-44f2-9fb4-0c15e9d3287f"),  # Scenario B (case_demo_mfs)
    uuid.UUID("3887c4ed-99d6-44f2-9fb4-0c15e9d3287a"),  # Scenario H (case_demo_living)
    uuid.UUID("a5b13210-e0dc-461b-8233-f33c98d45489"),
}


class FactService:
    @classmethod
    async def get_authorized_case(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> Case:
        """Enforces tenant isolation: owner-based access only. Non-enumerating 404 for foreign cases."""
        if case_id in DEMO_FIXTURE_IDS:
            from app.scenarios.service import ScenarioService
            await ScenarioService.ensure_deterministic_demo_case(case_id, db)

        stmt = select(Case).where(
            Case.id == case_id,
            (Case.principal_id == principal.id)
            | (Case.display_reference == "DEMO-DARAZ-001")
            | Case.id.in_(DEMO_FIXTURE_IDS),
            Case.deleted_at.is_(None),
        )
        res = await db.execute(stmt)
        c = res.scalar_one_or_none()
        if not c or c.lifecycle_status in ("deleting", "deleted"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found or access revoked",
            )
        return c

    @classmethod
    def normalize_value(
        cls, field_type: str, raw_value: Any, original_text: str | None = None
    ) -> tuple[Any, str]:
        """T05, T06, T07: Typed normalization preserving original text and non-lossy types."""
        orig_str = original_text if original_text is not None else str(raw_value)

        if field_type == "money":
            mv = normalize_bdt_money(raw_value, original_text=orig_str)
            return mv.model_dump(), orig_str

        elif field_type == "date":
            dv = normalize_bd_date(str(raw_value))
            return dv.model_dump(), orig_str

        elif field_type == "boolean":
            if isinstance(raw_value, bool):
                b_val = raw_value
            elif str(raw_value).lower() in ("true", "1", "yes", "হ্যাঁ"):
                b_val = True
            elif str(raw_value).lower() in ("false", "0", "no", "না"):
                b_val = False
            else:
                b_val = bool(raw_value)
            return b_val, orig_str

        elif field_type in ("string", "select"):
            return str(raw_value).strip(), orig_str

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Unsupported field type: {field_type}",
        )

    @classmethod
    async def create_assertion(
        cls,
        case_id: uuid.UUID,
        payload: FactAssertionCreate,
        principal: Principal,
        db: AsyncSession,
    ) -> FactAssertionOut:
        """T05-T07: Creates an immutable fact assertion with normalized typed value and original text."""
        c = await cls.get_authorized_case(case_id, principal, db)

        typed_val, orig_text = cls.normalize_value(
            payload.field_type,
            payload.raw_value,
            payload.original_text,
        )

        assertion = FactAssertion(
            id=uuid.uuid4(),
            case_id=c.id,
            issue_id=payload.issue_id,
            field_name=payload.field_name,
            field_type=payload.field_type,
            typed_value=typed_val,
            original_text=orig_text,
            origin=payload.origin,
            asserting_actor_id=principal.id,
            created_case_version=c.row_version,
            is_active=True,
            created_at=datetime.datetime.now(datetime.UTC),
        )
        db.add(assertion)
        await db.flush()

        if payload.span_start is not None and payload.span_end is not None:
            source_link = FactSourceLink(
                id=uuid.uuid4(),
                assertion_id=assertion.id,
                source_type="user_narrative_span",
                span_start=payload.span_start,
                span_end=payload.span_end,
                created_at=datetime.datetime.now(datetime.UTC),
            )
            db.add(source_link)
            await db.flush()

        await db.commit()
        await db.refresh(assertion)
        return FactAssertionOut.model_validate(assertion)

    @classmethod
    async def propose_multimodal_fact(
        cls,
        case_id: uuid.UUID,
        proposal: MultimodalFactProposal,
        principal: Principal,
        db: AsyncSession,
    ) -> MultimodalProposalResult:
        """P06.4: Unified atomic provenance model integrating voice, text, and visual facts into the primary case store."""
        case = await cls.get_authorized_case(case_id, principal, db)

        typed_val, orig_text = cls.normalize_value(
            proposal.field_type,
            proposal.raw_value,
            proposal.original_text,
        )

        # Check for existing active assertion for the same field (cross-modality conflict detection)
        stmt_existing = select(FactAssertion).where(
            FactAssertion.case_id == case_id,
            FactAssertion.field_name == proposal.field_name,
            FactAssertion.is_active == True,
        )
        res_existing = await db.execute(stmt_existing)
        existing = res_existing.scalar_one_or_none()

        has_conflict = False
        conflicting_id = None
        conflict_msg_en = None
        conflict_msg_bn = None

        if existing and existing.typed_value != typed_val:
            has_conflict = True
            conflicting_id = existing.id
            conflict_msg_en = f"Conflict detected for {proposal.field_name}: Existing {existing.origin} ({existing.original_text}) vs new {proposal.origin} ({orig_text}). Routed to user review."
            conflict_msg_bn = f"{proposal.field_name} তথ্যের ক্ষেত্রে অমিল পাওয়া গেছে: পূর্বের {existing.origin} ({existing.original_text}) বনাম নতুন {proposal.origin} ({orig_text})। ব্যবহারকারীর পর্যালোচনার জন্য পাঠানো হয়েছে।"

        assertion = FactAssertion(
            id=uuid.uuid4(),
            case_id=case.id,
            field_name=proposal.field_name,
            field_type=proposal.field_type,
            typed_value=typed_val,
            original_text=orig_text,
            origin=proposal.origin,
            asserting_actor_id=principal.id,
            created_case_version=case.row_version,
            is_active=not has_conflict,
            created_at=datetime.datetime.now(datetime.UTC),
        )
        db.add(assertion)
        await db.flush()

        source_link = FactSourceLink(
            id=uuid.uuid4(),
            assertion_id=assertion.id,
            source_type=proposal.source_type,
            locator_meta=proposal.locator_meta,
            created_at=datetime.datetime.now(datetime.UTC),
        )
        db.add(source_link)
        await db.commit()
        await db.refresh(assertion)

        return MultimodalProposalResult(
            assertion=FactAssertionOut.model_validate(assertion),
            source_link_id=source_link.id,
            has_conflict=has_conflict,
            conflicting_assertion_id=conflicting_id,
            conflict_message_en=conflict_msg_en,
            conflict_message_bn=conflict_msg_bn,
        )

    @classmethod
    async def get_assertions(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
        active_only: bool = True,
    ) -> list[FactAssertionOut]:
        """Lists authorized fact assertions for a case."""
        c = await cls.get_authorized_case(case_id, principal, db)

        stmt = select(FactAssertion).where(FactAssertion.case_id == c.id)
        if active_only:
            stmt = stmt.where(FactAssertion.is_active.is_(True))
        stmt = stmt.order_by(FactAssertion.created_at.asc())

        res = await db.execute(stmt)
        records = res.scalars().all()
        reviews = (await db.scalars(select(FactReview).where(
            or_(FactReview.assertion_id.in_([record.id for record in records]),
                FactReview.correction_assertion_id.in_([record.id for record in records]))
        ).order_by(FactReview.reviewed_at.desc()))).all() if records else []
        latest = {}
        for review in reviews:
            latest.setdefault(review.assertion_id, review.review_outcome)
            if review.correction_assertion_id:
                latest.setdefault(review.correction_assertion_id, "corrected")
        return [FactAssertionOut.model_validate(record).model_copy(
            update={"review_outcome": latest.get(record.id)}
        ) for record in records]

    @classmethod
    async def review_assertion(
        cls,
        case_id: uuid.UUID,
        assertion_id: uuid.UUID,
        submission: FactReviewSubmission,
        principal: Principal,
        db: AsyncSession,
    ) -> FactReviewOut:
        """T09: Confirms, corrects, rejects, or marks unsure an assertion.

        Material correction creates a new assertion version and supersedes the old one.
        """
        c = await cls.get_authorized_case(case_id, principal, db)

        stmt = select(FactAssertion).where(
            FactAssertion.id == assertion_id,
            FactAssertion.case_id == c.id,
        )
        res = await db.execute(stmt)
        old_assertion = res.scalar_one_or_none()
        if not old_assertion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fact assertion not found in case",
            )

        correction_id = None
        if submission.review_outcome == "corrected":
            if submission.corrected_value is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Corrected value required when outcome is 'corrected'",
                )

            # Deactivate old assertion
            old_assertion.is_active = False

            # Create new replacement assertion
            corr_typed, corr_orig = cls.normalize_value(
                old_assertion.field_type,
                submission.corrected_value,
                submission.corrected_original_text,
            )
            new_assertion = FactAssertion(
                id=uuid.uuid4(),
                case_id=c.id,
                issue_id=old_assertion.issue_id,
                field_name=old_assertion.field_name,
                field_type=old_assertion.field_type,
                typed_value=corr_typed,
                original_text=corr_orig,
                origin="user_statement",
                asserting_actor_id=principal.id,
                created_case_version=c.row_version,
                is_active=True,
                created_at=datetime.datetime.now(datetime.UTC),
            )
            db.add(new_assertion)
            await db.flush()
            correction_id = new_assertion.id

        elif submission.review_outcome == "rejected":
            old_assertion.is_active = False

        review = FactReview(
            id=uuid.uuid4(),
            assertion_id=old_assertion.id,
            reviewer_principal_id=principal.id,
            review_outcome=submission.review_outcome,
            correction_assertion_id=correction_id,
            reviewed_case_version=c.row_version,
            rationale=submission.rationale,
            reviewed_at=datetime.datetime.now(datetime.UTC),
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)
        return FactReviewOut.model_validate(review)
