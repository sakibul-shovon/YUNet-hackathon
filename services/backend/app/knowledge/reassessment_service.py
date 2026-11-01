import datetime
import hashlib
import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.action_dag import ActionDAGService
from app.cases.models import Case, CaseEvent, CaseSnapshot, IssueTrack
from app.identity.models import Principal
from app.knowledge.models import KnowledgeRelease
from app.knowledge.schemas import CaseReassessmentResult, ReassessmentQueueResult
from app.policy.engine import ProceduralAssessmentEngine


class ReassessmentQueueService:
    """Manages impacted-case reassessment queues and safe non-destructive updates (T39, T45).

    - Only cases dependent on modified rules or provisions are flagged.
    - Historical case snapshots and interpretations are retained without silent overwriting.
    - User/consumer can view the explicit semantic diff between old and new guidance.
    """

    @classmethod
    async def detect_and_flag_impacted_cases(
        cls,
        release_id: str,
        db: AsyncSession,
        override_affected_rules: list[str] | None = None,
    ) -> ReassessmentQueueResult:
        """Flags open cases whose issue tracks depend on newly modified or added statutory rules."""
        # 1. Fetch release manifest
        stmt = select(KnowledgeRelease).where(KnowledgeRelease.release_id == release_id)
        res = await db.execute(stmt)
        release = res.scalar_one_or_none()
        if not release:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "RELEASE_NOT_FOUND", "message": f"Release '{release_id}' not found"}},
            )

        manifest = release.manifest_data or {}
        impacted_rules = override_affected_rules or manifest.get("impacted_rules") or []
        if not impacted_rules:
            # Check rules in manifest
            rules = manifest.get("rules", [])
            impacted_rules = [r.get("rule_id") for r in rules if r.get("rule_id")]

        if not impacted_rules:
            # Default to checking if any rule was updated
            impacted_rules = ["R-CRPA-S45-MISLEADING-PRICE", "R-CRPA-S60-LIMITATION-30D"]

        # 2. Query all active or draft cases
        case_stmt = select(Case).where(
            Case.lifecycle_status.in_(["draft", "active"]),
            Case.deleted_at.is_(None),
        )
        case_res = await db.execute(case_stmt)
        active_cases = list(case_res.scalars().all())

        flagged_case_ids: list[uuid.UUID] = []

        # 3. Evaluate each case's dependencies
        for case in active_cases:
            # Check issue tracks
            issue_stmt = select(IssueTrack).where(
                IssueTrack.case_id == case.id,
                IssueTrack.hypothesis_state != "rejected",
            )
            issue_res = await db.execute(issue_stmt)
            tracks = list(issue_res.scalars().all())

            is_dependent = False
            for track in tracks:
                issue_type = (track.canonical_taxonomy or "").lower()
                # Check if issue matches modified rule domains
                if (
                    any(r in ["R-CRPA-S45-MISLEADING-PRICE", "R-CRPA-S45-OVERCHARGING", "R-CRPA-S60-LIMITATION-30D"] for r in impacted_rules)
                    and issue_type in ["pricing_deception", "delivery_failure", "damaged_goods", "counterfeit_fake"]
                ):
                    is_dependent = True
                    break
                if (
                    any(r == "R-BB-CIPC-STAGE1-MANDATORY" for r in impacted_rules)
                    and issue_type in ["unauthorized_transaction", "mfs_fraud"]
                ):
                    is_dependent = True
                    break
                if (
                    any(r == "R-BTRC-STAGE1-MANDATORY" for r in impacted_rules)
                    and issue_type in ["billing_dispute", "service_outage"]
                ):
                    is_dependent = True
                    break

            # If dependent, flag the case with an auditable timeline notification
            if is_dependent:
                flagged_case_ids.append(case.id)

                # Check max event sequence
                max_seq_res = await db.execute(
                    select(func.coalesce(func.max(CaseEvent.event_sequence), 0)).where(CaseEvent.case_id == case.id)
                )
                seq = (max_seq_res.scalar() or 0) + 1

                event = CaseEvent(
                    id=uuid.uuid4(),
                    case_id=case.id,
                    principal_id=case.principal_id,
                    event_sequence=seq,
                    event_type="source_update_flagged",
                    actor_type="system",
                    payload={
                        "title": f"Official Source Update ({release_id})",
                        "description": f"Official provisions updated in release {release_id}. Reassessment available.",
                        "release_id": release_id,
                        "impacted_rules": impacted_rules,
                        "notice": f"Official provisions updated in release {release_id}. Reassessment available.",
                        "origin": "system_event",
                        "flagged_at": datetime.datetime.now(datetime.UTC).isoformat(),
                    },
                )
                db.add(event)

        await db.commit()

        return ReassessmentQueueResult(
            release_id=release_id,
            impacted_cases_count=len(flagged_case_ids),
            flagged_case_ids=flagged_case_ids,
            affected_rules=impacted_rules,
        )

    @classmethod
    async def reassess_case(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> CaseReassessmentResult:
        """Executes explicit on-demand reassessment against the active knowledge release.

        Generates semantic decision diff and preserves immutable historical snapshots.
        """
        # 1. Fetch case with ownership check
        stmt = select(Case).where(Case.id == case_id)
        res = await db.execute(stmt)
        case = res.scalar_one_or_none()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found"}},
            )

        if case.principal_id != principal.id and principal.kind != "system":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "CASE_NOT_FOUND", "message": "Case not found"}},
            )

        # 2. Get active release
        rel_stmt = select(KnowledgeRelease).where(KnowledgeRelease.is_active.is_(True))
        rel_res = await db.execute(rel_stmt)
        active_rel = rel_res.scalar_one_or_none()
        active_release_id = active_rel.release_id if active_rel else "unknown"

        # 3. Retrieve prior snapshot to identify prior primary action
        snap_stmt = (
            select(CaseSnapshot)
            .where(CaseSnapshot.case_id == case.id)
            .order_by(CaseSnapshot.version.desc())
        )
        snap_res = await db.execute(snap_stmt)
        latest_snapshot = snap_res.scalars().first()

        prior_primary_action = None
        if latest_snapshot and latest_snapshot.issue_state:
            prior_primary_action = latest_snapshot.issue_state.get("primary_action") or latest_snapshot.issue_state.get("primary_action_id")

        # 4. Assess case under current active rules
        assessment = await ProceduralAssessmentEngine.assess_case(case=case, db=db)

        # 5. Build Action DAG under current rules
        dag = await ActionDAGService.build_action_dag(case_id=case.id, principal=principal, db=db)
        new_primary_action = dag.primary_action_id

        has_changed = prior_primary_action != new_primary_action

        # 6. Construct semantic decision diff
        decision_diff = {
            "prior_primary_action": prior_primary_action,
            "new_primary_action": new_primary_action,
            "has_route_change": has_changed,
            "routes_status": {r.route_id: r.status.value for r in assessment.routes},
            "active_release_id": active_release_id,
        }

        # 7. Create new immutable CaseSnapshot (incrementing version)
        next_version = (latest_snapshot.version + 1) if latest_snapshot else 1
        snapshot_issue_state = {
            "version": next_version,
            "reassessed_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "release_id": active_release_id,
            "primary_action": new_primary_action,
            "assessment_summary": {
                "routes_count": len(assessment.routes),
                "supported_count": sum(1 for r in assessment.routes if r.status.value == "supported"),
            },
        }

        canonical_hash = hashlib.sha256(f"{case.id}:{new_primary_action}:{next_version}:{active_release_id}".encode()).hexdigest()

        new_snapshot = CaseSnapshot(
            id=uuid.uuid4(),
            case_id=case.id,
            principal_id=case.principal_id,
            version=next_version,
            canonical_input_hash=canonical_hash,
            fact_assertion_ids=[],
            issue_state=snapshot_issue_state,
        )
        db.add(new_snapshot)

        # 8. Record timeline event
        max_seq_res = await db.execute(
            select(func.coalesce(func.max(CaseEvent.event_sequence), 0)).where(CaseEvent.case_id == case.id)
        )
        seq = (max_seq_res.scalar() or 0) + 1

        event = CaseEvent(
            id=uuid.uuid4(),
            case_id=case.id,
            principal_id=principal.id,
            event_sequence=seq,
            event_type="case_reassessed",
            actor_type="consumer",
            payload={
                "release_id": active_release_id,
                "snapshot_version": next_version,
                "prior_primary_action": prior_primary_action,
                "new_primary_action": new_primary_action,
                "decision_diff": decision_diff,
            },
        )
        db.add(event)
        await db.commit()

        return CaseReassessmentResult(
            case_id=case.id,
            reassessed_at=datetime.datetime.now(datetime.UTC),
            release_id=active_release_id,
            has_changed=has_changed,
            prior_primary_action=prior_primary_action,
            new_primary_action=new_primary_action,
            decision_diff=decision_diff,
        )
