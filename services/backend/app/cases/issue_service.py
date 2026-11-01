import datetime
import uuid
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cases.models import CaseEvent, IssueTrack
from app.facts.models import FactAssertion
from app.facts.service import FactService
from app.identity.models import Principal
from app.policy.engine import ProceduralAssessmentEngine

# Non-actionable brand tracks (P08.2)
NON_ACTIONABLE_BRAND_TAXONOMIES = {
    "brand_reputation",
    "brand_complaint",
    "general_dissatisfaction",
    "seller_criticism",
    "corporate_governance_complaint",
}


class IssueTrackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    canonical_taxonomy: str
    hypothesis_state: str  # 'hypothesis', 'confirmed', 'rejected', 'split', 'merged'
    user_review: str | None = None
    desired_remedy: str | None = None
    rejection_reason: str | None = None
    active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class IssueCreate(BaseModel):
    canonical_taxonomy: str = Field(..., min_length=2, max_length=128)
    desired_remedy: str | None = None


class SubIssueData(BaseModel):
    canonical_taxonomy: str
    desired_remedy: str | None = None
    assigned_fact_ids: list[uuid.UUID] = Field(default_factory=list)


class IssueSplitRequest(BaseModel):
    source_issue_id: uuid.UUID
    sub_issues: list[SubIssueData] = Field(..., min_length=2)


class IssueMergeRequest(BaseModel):
    issue_ids_to_merge: list[uuid.UUID] = Field(..., min_length=2)
    target_canonical_taxonomy: str
    target_desired_remedy: str | None = None


class IssueReviewRequest(BaseModel):
    user_review: str = Field(..., pattern="^(accepted|corrected|rejected|unsure)$")
    desired_remedy: str | None = None
    corrected_taxonomy: str | None = None


class MultiIssueAssessmentOut(BaseModel):
    case_id: uuid.UUID
    issue_tracks: list[IssueTrackOut]
    independent_paths: list[dict[str, Any]]


class IssueService:
    """P08.2: User-reviewed issue split/merge, brand-only false track rejection,

    and multi-issue decomposition with independent remedy and stage dependencies.
    """

    @classmethod
    async def list_issues(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> list[IssueTrackOut]:
        case = await FactService.get_authorized_case(case_id, principal, db)
        stmt = (
            select(IssueTrack)
            .where(IssueTrack.case_id == case.id)
            .order_by(IssueTrack.created_at.asc())
        )
        res = await db.execute(stmt)
        issues = res.scalars().all()
        return [IssueTrackOut.model_validate(i) for i in issues]

    @classmethod
    async def create_issue(
        cls,
        case_id: uuid.UUID,
        data: IssueCreate,
        principal: Principal,
        db: AsyncSession,
    ) -> IssueTrackOut:
        case = await FactService.get_authorized_case(case_id, principal, db)
        now = datetime.datetime.now(datetime.UTC)

        # Check for brand-only false track rejection (P08.2)
        is_brand_track = data.canonical_taxonomy.lower() in NON_ACTIONABLE_BRAND_TAXONOMIES
        hypothesis_state = "rejected" if is_brand_track else "hypothesis"
        user_review = "rejected" if is_brand_track else None
        rejection_reason = (
            "Brand reputation grievances or generalized dissatisfaction without specific "
            "statutory non-delivery, product defect, or unauthorized debit cannot form an actionable legal track (P08.2)."
            if is_brand_track else None
        )

        issue = IssueTrack(
            id=uuid.uuid4(),
            case_id=case.id,
            principal_id=principal.id,
            canonical_taxonomy=data.canonical_taxonomy,
            hypothesis_state=hypothesis_state,
            user_review=user_review,
            desired_remedy=data.desired_remedy,
            active=not is_brand_track,
            created_at=now,
            updated_at=now,
        )
        db.add(issue)

        # Get next event sequence
        from sqlalchemy import func
        seq_stmt = select(func.coalesce(func.max(CaseEvent.event_sequence), 0)).where(
            CaseEvent.case_id == case.id
        )
        max_seq = (await db.execute(seq_stmt)).scalar_one()
        next_seq = max_seq + 1

        # Record case event
        event = CaseEvent(
            id=uuid.uuid4(),
            case_id=case.id,
            principal_id=principal.id,
            event_sequence=next_seq,
            event_type="issue.created",
            actor_type="consumer",
            actor_id=principal.id,
            schema_version=1,
            payload={
                "issue_id": str(issue.id),
                "taxonomy": data.canonical_taxonomy,
                "is_brand_track_rejected": is_brand_track,
            },
            created_at=now,
        )
        db.add(event)
        await db.commit()
        await db.refresh(issue)

        out = IssueTrackOut.model_validate(issue)
        out.rejection_reason = rejection_reason
        return out

    @classmethod
    async def split_issue(
        cls,
        case_id: uuid.UUID,
        data: IssueSplitRequest,
        principal: Principal,
        db: AsyncSession,
    ) -> list[IssueTrackOut]:
        case = await FactService.get_authorized_case(case_id, principal, db)
        now = datetime.datetime.now(datetime.UTC)

        # 1. Fetch source issue
        source_stmt = select(IssueTrack).where(
            IssueTrack.id == data.source_issue_id,
            IssueTrack.case_id == case.id,
        )
        res = await db.execute(source_stmt)
        source_issue = res.scalar_one_or_none()
        if not source_issue or not source_issue.active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active source issue track to split was not found.",
            )

        # 2. Deactivate source issue
        source_issue.active = False
        source_issue.hypothesis_state = "split"
        source_issue.updated_at = now

        # 3. Create sub issues
        created_sub_issues: list[IssueTrack] = []
        for sub in data.sub_issues:
            new_issue = IssueTrack(
                id=uuid.uuid4(),
                case_id=case.id,
                principal_id=principal.id,
                canonical_taxonomy=sub.canonical_taxonomy,
                hypothesis_state="hypothesis",
                desired_remedy=sub.desired_remedy or source_issue.desired_remedy,
                active=True,
                created_at=now,
                updated_at=now,
            )
            db.add(new_issue)
            created_sub_issues.append(new_issue)
            await db.flush()

            # Assign associated facts if any
            if sub.assigned_fact_ids:
                stmt_facts = select(FactAssertion).where(
                    FactAssertion.id.in_(sub.assigned_fact_ids),
                    FactAssertion.case_id == case.id,
                )
                facts_res = await db.execute(stmt_facts)
                for f in facts_res.scalars().all():
                    f.issue_id = new_issue.id

        await db.commit()
        for i in created_sub_issues:
            await db.refresh(i)

        return [IssueTrackOut.model_validate(i) for i in created_sub_issues]

    @classmethod
    async def merge_issues(
        cls,
        case_id: uuid.UUID,
        data: IssueMergeRequest,
        principal: Principal,
        db: AsyncSession,
    ) -> IssueTrackOut:
        case = await FactService.get_authorized_case(case_id, principal, db)
        now = datetime.datetime.now(datetime.UTC)

        # Fetch source issues
        stmt = select(IssueTrack).where(
            IssueTrack.id.in_(data.issue_ids_to_merge),
            IssueTrack.case_id == case.id,
            IssueTrack.active.is_(True),
        )
        res = await db.execute(stmt)
        sources = res.scalars().all()
        if len(sources) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must specify at least 2 active issues belonging to this case to merge.",
            )

        # Deactivate sources
        for s in sources:
            s.active = False
            s.hypothesis_state = "merged"
            s.updated_at = now

        # Create target merged issue
        merged_issue = IssueTrack(
            id=uuid.uuid4(),
            case_id=case.id,
            principal_id=principal.id,
            canonical_taxonomy=data.target_canonical_taxonomy,
            hypothesis_state="hypothesis",
            desired_remedy=data.target_desired_remedy,
            active=True,
            created_at=now,
            updated_at=now,
        )
        db.add(merged_issue)
        await db.flush()

        # Reassign facts from merged issues to new issue
        stmt_facts = select(FactAssertion).where(
            FactAssertion.issue_id.in_(data.issue_ids_to_merge),
            FactAssertion.case_id == case.id,
        )
        facts_res = await db.execute(stmt_facts)
        for f in facts_res.scalars().all():
            f.issue_id = merged_issue.id

        await db.commit()
        await db.refresh(merged_issue)
        return IssueTrackOut.model_validate(merged_issue)

    @classmethod
    async def review_issue(
        cls,
        case_id: uuid.UUID,
        issue_id: uuid.UUID,
        data: IssueReviewRequest,
        principal: Principal,
        db: AsyncSession,
    ) -> IssueTrackOut:
        case = await FactService.get_authorized_case(case_id, principal, db)
        stmt = select(IssueTrack).where(
            IssueTrack.id == issue_id,
            IssueTrack.case_id == case.id,
        )
        res = await db.execute(stmt)
        issue = res.scalar_one_or_none()
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue track not found.")

        now = datetime.datetime.now(datetime.UTC)
        issue.user_review = data.user_review
        if data.user_review == "accepted":
            issue.hypothesis_state = "confirmed"
        elif data.user_review == "rejected":
            issue.hypothesis_state = "rejected"
            issue.active = False
        elif data.user_review == "corrected" and data.corrected_taxonomy:
            issue.canonical_taxonomy = data.corrected_taxonomy
            issue.hypothesis_state = "confirmed"

        if data.desired_remedy:
            issue.desired_remedy = data.desired_remedy

        issue.updated_at = now
        await db.commit()
        await db.refresh(issue)
        return IssueTrackOut.model_validate(issue)

    @classmethod
    async def assess_multi_issues(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> MultiIssueAssessmentOut:
        """Evaluates each active issue track independently, preserving distinct remedies,

        allowed actions, and procedural pathways per track.
        """
        case = await FactService.get_authorized_case(case_id, principal, db)
        stmt_issues = select(IssueTrack).where(
            IssueTrack.case_id == case.id,
        ).order_by(IssueTrack.created_at.asc())
        issues_res = await db.execute(stmt_issues)
        all_issues = issues_res.scalars().all()

        # Fetch case facts
        stmt_facts = select(FactAssertion).where(
            FactAssertion.case_id == case.id,
            FactAssertion.is_active.is_(True),
        )
        facts_res = await db.execute(stmt_facts)
        assertions = facts_res.scalars().all()

        rules = ProceduralAssessmentEngine.load_starter_rules()
        independent_paths: list[dict[str, Any]] = []

        active_issues = [i for i in all_issues if i.active]

        for issue in active_issues:
            # Gather facts relevant to this issue (issue-scoped or unassigned case-wide facts)
            issue_facts = [
                a for a in assertions
                if a.issue_id == issue.id or a.issue_id is None
            ]
            facts_dict = ProceduralAssessmentEngine.extract_facts_from_db_records(issue_facts, case)

            # Evaluate matching rule for issue's taxonomy
            target_rules = [r for r in rules if r.issue_type == issue.canonical_taxonomy]
            if not target_rules:
                target_rules = rules  # Fallback to evaluating all starter rules

            routes_out, _ = ProceduralAssessmentEngine.evaluate_all_rules(
                target_rules,
                facts_dict,
                desired_outcomes=[issue.desired_remedy] if issue.desired_remedy else case.desired_outcomes,
            )

            matching_routes = [r for r in routes_out if r.issue_type == issue.canonical_taxonomy]
            primary_route = matching_routes[0] if matching_routes else (routes_out[0] if routes_out else None)

            independent_paths.append({
                "issue_id": str(issue.id),
                "canonical_taxonomy": issue.canonical_taxonomy,
                "hypothesis_state": issue.hypothesis_state,
                "desired_remedy": issue.desired_remedy,
                "evaluated_route": primary_route.model_dump() if primary_route else None,
                "all_applicable_routes": [r.model_dump() for r in routes_out],
            })

        return MultiIssueAssessmentOut(
            case_id=case.id,
            issue_tracks=[IssueTrackOut.model_validate(i) for i in all_issues],
            independent_paths=independent_paths,
        )
