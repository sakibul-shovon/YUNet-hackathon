import datetime
import hashlib
import json
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.models import Principal
from app.knowledge.models import KnowledgeRelease, SourceVersion
from app.knowledge.schemas import (
    KnowledgeReleaseOut,
    ReleaseBuildRequest,
    ReviewResultOut,
    ReviewSubmission,
    SourceCandidateOut,
)
from app.knowledge.service import KnowledgeService


class AdminKnowledgeService:
    @staticmethod
    async def list_source_candidates(db: AsyncSession) -> list[SourceCandidateOut]:
        """Lists all unreviewed candidate source versions."""
        stmt = (
            select(SourceVersion)
            .where(SourceVersion.applicability_status == "candidate")
            .order_by(SourceVersion.created_at.desc())
        )
        res = await db.execute(stmt)
        return [
            SourceCandidateOut(
                id=v.id,
                family_id=v.family_id,
                version_tag=v.version_tag,
                issuer=v.issuer,
                document_type=v.document_type,
                applicability_status=v.applicability_status,
                clean_text_hash=v.clean_text_hash,
                created_at=v.created_at,
            )
            for v in res.scalars().all()
        ]

    @staticmethod
    async def review_source_version(
        version_id: uuid.UUID,
        reviewer: Principal,
        submission: ReviewSubmission,
        db: AsyncSession,
    ) -> ReviewResultOut:
        """Records named human review and scope. Upgrades candidate to approved."""
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
        """Validates all components and constructs an immutable release manifest.

        Rejects test_only rules (T18) and unapproved source versions.
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
        """Performs atomic active release pointer swap."""
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
    async def disable_release(
        release_id: str,
        publisher: Principal,
        db: AsyncSession,
    ) -> KnowledgeReleaseOut:
        """Applies emergency disable overlay."""
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

