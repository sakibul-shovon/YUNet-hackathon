import datetime
import hashlib
import json
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.models import Principal
from app.knowledge.diff_service import SectionAwareDiffService
from app.knowledge.models import (
    KnowledgeRelease,
    SourceApproval,
    SourceCandidate,
    SourceFamily,
    SourceProvision,
    SourceVersion,
)
from app.knowledge.schemas import (
    CandidateDiffOut,
    KnowledgeReleaseOut,
    ReleaseBuildRequest,
    ReviewResultOut,
    ReviewSubmission,
    SourceCandidateOut,
    SourceHealthItem,
    SourceHealthResponse,
)
from app.knowledge.service import KnowledgeService
from app.knowledge.source_registry import get_source_registry


class AdminKnowledgeService:
    @staticmethod
    async def list_source_candidates(db: AsyncSession) -> list[SourceCandidateOut]:
        """Lists all unreviewed candidate source versions and candidate watcher records."""
        # Query candidates from source_candidates table
        stmt_cand = select(SourceCandidate).order_by(SourceCandidate.fetched_at.desc())
        res_cand = await db.execute(stmt_cand)
        candidates = list(res_cand.scalars().all())

        return [
            SourceCandidateOut(
                id=c.id,
                family_id=c.family_id,
                url=c.url,
                status=c.status,
                raw_hash=c.raw_hash,
                origin_chain=c.origin_chain,
                fetched_at=c.fetched_at,
            )
            for c in candidates
        ]

    @staticmethod
    async def get_candidate_diff(
        candidate_id: uuid.UUID,
        db: AsyncSession,
    ) -> CandidateDiffOut:
        """Computes section-aware legal diff and proposed downstream impact for a candidate (T43)."""
        stmt = select(SourceCandidate).where(SourceCandidate.id == candidate_id)
        res = await db.execute(stmt)
        candidate = res.scalar_one_or_none()
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "CANDIDATE_NOT_FOUND", "message": f"Candidate '{candidate_id}' not found"}},
            )

        # Get family slug
        family_stmt = select(SourceFamily).where(SourceFamily.id == candidate.family_id)
        f_res = await db.execute(family_stmt)
        family = f_res.scalar_one_or_none()
        family_slug = family.slug if family else "unknown"

        # Find current active approved version
        v_stmt = (
            select(SourceVersion)
            .where(
                SourceVersion.family_id == candidate.family_id,
                SourceVersion.applicability_status == "approved",
            )
            .order_by(SourceVersion.created_at.desc())
        )
        v_res = await db.execute(v_stmt)
        approved_version = v_res.scalars().first()

        approved_provisions: list[SourceProvision] = []
        if approved_version:
            p_stmt = select(SourceProvision).where(SourceProvision.source_version_id == approved_version.id)
            p_res = await db.execute(p_stmt)
            approved_provisions = list(p_res.scalars().all())

        # Extract text from candidate
        origin = candidate.origin_chain or {}
        raw_text = origin.get("clean_text") or ""
        pub_date = origin.get("publication_date")
        comm_date = origin.get("commencement_date")

        candidate_provisions = SectionAwareDiffService.parse_provisions(raw_text)

        impact = SectionAwareDiffService.compute_diff(
            candidate_id=candidate.id,
            family_slug=family_slug,
            candidate_provisions=candidate_provisions,
            approved_provisions=approved_provisions,
            publication_date=pub_date,
            commencement_date=comm_date,
            candidate_raw_text=raw_text,
        )

        return CandidateDiffOut(
            candidate_id=impact.candidate_id,
            family_slug=impact.family_slug,
            is_current_law=impact.is_current_law,
            publication_date=impact.publication_date,
            commencement_date=impact.commencement_date,
            commencement_status=impact.commencement_status,
            has_transitional_clauses=impact.has_transitional_clauses,
            transitional_notes=impact.transitional_notes,
            impacted_rules=impact.impacted_rules,
            impacted_domains=impact.impacted_domains,
            provision_diffs=[d.model_dump() for d in impact.provision_diffs],
            added_count=impact.added_count,
            modified_count=impact.modified_count,
            repealed_count=impact.repealed_count,
            unchanged_count=impact.unchanged_count,
        )

    @staticmethod
    async def approve_candidate(
        candidate_id: uuid.UUID,
        reviewer: Principal,
        submission: ReviewSubmission,
        db: AsyncSession,
    ) -> ReviewResultOut:
        """Records named human review and promotes a candidate into an approved SourceVersion with provisions (T44)."""
        stmt = select(SourceCandidate).where(SourceCandidate.id == candidate_id)
        res = await db.execute(stmt)
        candidate = res.scalar_one_or_none()
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "CANDIDATE_NOT_FOUND", "message": f"Candidate '{candidate_id}' not found"}},
            )

        # Get family
        f_stmt = select(SourceFamily).where(SourceFamily.id == candidate.family_id)
        f_res = await db.execute(f_stmt)
        family = f_res.scalar_one_or_none()

        origin = candidate.origin_chain or {}
        clean_text = origin.get("clean_text") or ""
        clean_hash = origin.get("clean_text_hash") or candidate.raw_hash

        reviewer_name = f"Reviewer-{str(reviewer.id)[:8]}"

        if submission.decision == "approved":
            # Create new approved SourceVersion
            version_tag = f"reviewed-{datetime.datetime.now(datetime.UTC).strftime('%Y%m%d%H%M')}"
            version = SourceVersion(
                id=uuid.uuid4(),
                family_id=candidate.family_id,
                version_tag=version_tag,
                raw_bytes_hash=candidate.raw_hash,
                text_content=clean_text,
                clean_text_hash=clean_hash,
                issuer=family.issuer if family else "Government Authority",
                document_type=origin.get("document_type") or "statute",
                publication_date=origin.get("publication_date"),
                commencement_date=origin.get("commencement_date"),
                applicability_status="approved",
            )
            db.add(version)
            await db.flush()

            # Parse and insert provisions
            provisions = SectionAwareDiffService.parse_provisions(clean_text)
            for p in provisions:
                sp = SourceProvision(
                    id=uuid.uuid4(),
                    source_version_id=version.id,
                    provision_path=p.provision_path,
                    title=p.title,
                    text_content=p.text_content,
                    normalized_text=p.normalized_text,
                )
                db.add(sp)

            # Record SourceApproval
            approval = SourceApproval(
                id=uuid.uuid4(),
                source_version_id=version.id,
                reviewer_id=reviewer.id,
                reviewer_name=reviewer_name,
                scope=submission.scope,
                rationale=submission.rationale,
                limitations=submission.limitations,
                decision="approved",
            )
            db.add(approval)

            candidate.status = "approved"
            await db.commit()
            await db.refresh(approval)

            return ReviewResultOut(
                id=approval.id,
                source_version_id=version.id,
                reviewer_name=approval.reviewer_name,
                scope=approval.scope,
                decision=approval.decision,
                approved_at=approval.approved_at,
            )
        else:
            # Rejection
            candidate.status = "rejected"
            await db.commit()
            return ReviewResultOut(
                id=uuid.uuid4(),
                source_version_id=candidate.id,
                reviewer_name=reviewer_name,
                scope=submission.scope,
                decision="rejected",
                approved_at=datetime.datetime.now(datetime.UTC),
            )

    @staticmethod
    async def review_source_version(
        version_id: uuid.UUID,
        reviewer: Principal,
        submission: ReviewSubmission,
        db: AsyncSession,
    ) -> ReviewResultOut:
        """Records named human review and scope. Upgrades candidate SourceVersion to approved."""
        stmt = select(SourceVersion).where(SourceVersion.id == version_id)
        res = await db.execute(stmt)
        version = res.scalar_one_or_none()
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "SOURCE_VERSION_NOT_FOUND", "message": "Source version not found"}},
            )

        reviewer_name = f"Reviewer-{str(reviewer.id)[:8]}"
        approval = await KnowledgeService.approve_source_version(
            version_id=version_id,
            reviewer_id=reviewer.id,
            reviewer_name=reviewer_name,
            scope=submission.scope,
            rationale=submission.rationale,
            limitations=submission.limitations,
            decision=submission.decision,
            db=db,
        )

        return ReviewResultOut(
            id=approval.id,
            source_version_id=approval.source_version_id,
            reviewer_name=approval.reviewer_name,
            scope=approval.scope,
            decision=approval.decision,
            approved_at=approval.approved_at,
        )

    @staticmethod
    async def build_release(
        req: ReleaseBuildRequest,
        publisher: Principal,
        db: AsyncSession,
    ) -> KnowledgeReleaseOut:
        """Validates all components and constructs an immutable release manifest (T18, T45).

        Rejects test_only rules and unapproved source versions.
        """
        # 1. T18: Reject any test_only rule from compilation
        for r in req.rules:
            if r.get("status") == "test_only":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "error": {
                            "code": "TEST_ONLY_RULE_REJECTED",
                            "message": f"Rule '{r.get('rule_id')}' is marked test_only and cannot compile into live release.",
                        }
                    },
                )

        # 2. Check that all source versions exist and are approved
        if req.source_version_ids:
            stmt = select(SourceVersion).where(SourceVersion.id.in_(req.source_version_ids))
            res = await db.execute(stmt)
            versions = {v.id: v for v in res.scalars().all()}

            for sv_id in req.source_version_ids:
                v = versions.get(sv_id)
                if not v:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail={"error": {"code": "SOURCE_VERSION_MISSING", "message": f"Source version {sv_id} not found."}},
                    )
                if v.applicability_status != "approved":
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail={"error": {"code": "UNAPPROVED_SOURCE_VERSION", "message": f"Source version {sv_id} is not approved."}},
                    )

        # 3. Canonical Manifest Hash
        manifest = {
            "release_id": req.release_id,
            "release_mode": req.release_mode,
            "sources": [str(x) for x in req.source_version_ids],
            "rules": req.rules,
            "portal_maps": req.portal_maps,
            "lexical_index_hash": req.lexical_index_hash or "bm25-default-hash",
            "dense_index_model": req.dense_index_model or "multilingual-e5-small",
            "built_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "builder": str(publisher.id),
        }
        canonical_str = json.dumps(manifest, sort_keys=True)
        manifest_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        release = KnowledgeRelease(
            id=uuid.uuid4(),
            release_id=req.release_id,
            release_mode=req.release_mode,
            manifest_hash=manifest_hash,
            manifest_data=manifest,
            is_active=False,
        )
        db.add(release)
        await db.commit()
        await db.refresh(release)

        return KnowledgeReleaseOut.model_validate(release, from_attributes=True)

    @staticmethod
    async def promote_release(
        release_id: str,
        publisher: Principal,
        db: AsyncSession,
    ) -> KnowledgeReleaseOut:
        """Performs atomic active release pointer swap (T45)."""
        stmt = select(KnowledgeRelease).where(KnowledgeRelease.release_id == release_id)
        res = await db.execute(stmt)
        release = res.scalar_one_or_none()
        if not release:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "RELEASE_NOT_FOUND", "message": "Release not found"}},
            )

        now = datetime.datetime.now(datetime.UTC)

        # Unset currently active releases for same mode
        await db.execute(
            update(KnowledgeRelease)
            .where(KnowledgeRelease.release_mode == release.release_mode)
            .values(is_active=False)
        )

        # Atomic pointer swap to this release
        release.is_active = True
        release.promoted_at = now
        await db.commit()
        await db.refresh(release)

        return KnowledgeReleaseOut.model_validate(release, from_attributes=True)

    @staticmethod
    async def rollback_release(
        target_release_id: str,
        publisher: Principal,
        db: AsyncSession,
    ) -> KnowledgeReleaseOut:
        """Atomically rolls back the active release to a prior approved release manifest (T45).

        Never mixes dense, lexical, rule, and form versions.
        """
        stmt = select(KnowledgeRelease).where(KnowledgeRelease.release_id == target_release_id)
        res = await db.execute(stmt)
        target = res.scalar_one_or_none()
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "TARGET_RELEASE_NOT_FOUND", "message": f"Rollback target '{target_release_id}' not found"}},
            )

        # Deactivate all releases of this mode
        await db.execute(
            update(KnowledgeRelease)
            .where(KnowledgeRelease.release_mode == target.release_mode)
            .values(is_active=False)
        )

        # Promote target release
        target.is_active = True
        target.promoted_at = datetime.datetime.now(datetime.UTC)
        await db.commit()
        await db.refresh(target)

        return KnowledgeReleaseOut.model_validate(target, from_attributes=True)

    @staticmethod
    async def disable_release(
        release_id: str,
        publisher: Principal,
        db: AsyncSession,
    ) -> KnowledgeReleaseOut:
        """Applies emergency disable overlay (T45)."""
        stmt = select(KnowledgeRelease).where(KnowledgeRelease.release_id == release_id)
        res = await db.execute(stmt)
        release = res.scalar_one_or_none()
        if not release:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "RELEASE_NOT_FOUND", "message": "Release not found"}},
            )

        release.is_active = False
        await db.commit()
        await db.refresh(release)
        return KnowledgeReleaseOut.model_validate(release, from_attributes=True)

    @staticmethod
    async def get_source_health(db: AsyncSession) -> SourceHealthResponse:
        """Returns health status of registered official sources and current active release."""
        # 1. Active Release
        rel_stmt = select(KnowledgeRelease).where(KnowledgeRelease.is_active.is_(True))
        rel_res = await db.execute(rel_stmt)
        active_rel = rel_res.scalar_one_or_none()

        active_id = active_rel.release_id if active_rel else None
        active_mode = active_rel.release_mode if active_rel else None
        active_hash = active_rel.manifest_hash if active_rel else None

        # 2. Registered sources
        sources = get_source_registry()
        health_items = [
            SourceHealthItem(
                source_id=s.id,
                title_en=s.title_en,
                title_bn=s.title_bn,
                official_url=s.official_url,
                document_type=s.document_type,
                status=s.status,
                health_status=s.health_status,
                procedural_scope=s.procedural_scope,
                is_authoritative_for_penalties=s.is_authoritative_for_penalties,
                notice=s.notes,
            )
            for s in sources
        ]

        return SourceHealthResponse(
            active_release_id=active_id,
            active_release_mode=active_mode,
            active_manifest_hash=active_hash,
            sources=health_items,
        )
