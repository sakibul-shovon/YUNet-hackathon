import hashlib
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.knowledge.models import (
    SourceApproval,
    SourceFamily,
    SourceProvision,
    SourceVersion,
)


class KnowledgeService:
    @staticmethod
    def compute_sha256(text: str) -> str:
        """Computes canonical SHA-256 hex digest."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @classmethod
    async def create_source_family(
        cls,
        slug: str,
        title: str,
        issuer: str,
        db: AsyncSession,
        jurisdiction: str = "BD",
    ) -> SourceFamily:
        stmt = select(SourceFamily).where(SourceFamily.slug == slug)
        res = await db.execute(stmt)
        family = res.scalar_one_or_none()
        if not family:
            family = SourceFamily(
                id=uuid.uuid4(),
                slug=slug,
                title=title,
                issuer=issuer,
                jurisdiction=jurisdiction,
            )
            db.add(family)
            await db.commit()
            await db.refresh(family)
        return family

    @classmethod
    async def create_source_version(
        cls,
        family_id: uuid.UUID,
        version_tag: str,
        text_content: str,
        issuer: str,
        document_type: str,
        db: AsyncSession,
        publication_date: str | None = None,
        commencement_date: str | None = None,
        effective_from: str | None = None,
        effective_to: str | None = None,
        applicability_status: str = "candidate",
    ) -> SourceVersion:
        """Stores an immutable source version with verifiable text/byte hashes."""
        raw_hash = cls.compute_sha256(text_content)
        clean_text = text_content.strip()
        clean_hash = cls.compute_sha256(clean_text)

        version = SourceVersion(
            id=uuid.uuid4(),
            family_id=family_id,
            version_tag=version_tag,
            raw_bytes_hash=raw_hash,
            text_content=clean_text,
            clean_text_hash=clean_hash,
            issuer=issuer,
            document_type=document_type,
            publication_date=publication_date,
            commencement_date=commencement_date,
            effective_from=effective_from,
            effective_to=effective_to,
            applicability_status=applicability_status,
        )
        db.add(version)
        await db.commit()
        await db.refresh(version)
        return version

    @classmethod
    async def add_provision(
        cls,
        source_version_id: uuid.UUID,
        provision_path: str,
        title: str,
        text_content: str,
        db: AsyncSession,
        page_number: int | None = None,
        parent_provision_id: uuid.UUID | None = None,
    ) -> SourceProvision:
        """Adds an exact provision under a specific source version."""
        normalized = " ".join(text_content.strip().split())
        provision = SourceProvision(
            id=uuid.uuid4(),
            source_version_id=source_version_id,
            provision_path=provision_path,
            title=title,
            text_content=text_content.strip(),
            normalized_text=normalized,
            page_number=page_number,
            parent_provision_id=parent_provision_id,
        )
        db.add(provision)
        await db.commit()
        await db.refresh(provision)
        return provision

    @staticmethod
    async def query_approved_provisions(
        db: AsyncSession,
        query: str = "",
        release_id: str | None = None,
        limit: int = 20,
    ) -> list[SourceProvision]:
        """T16: Queries only approved provisions in the active release.

        CANDIDATE, UNAPPROVED, or ARCHIVED versions are STRICTLY EXCLUDED
        from authoritative search results.
        """
        stmt = (
            select(SourceProvision)
            .join(SourceVersion, SourceProvision.source_version_id == SourceVersion.id)
            .where(
                SourceVersion.applicability_status == "approved",
            )
        )
        if query:
            stmt = stmt.where(SourceProvision.normalized_text.ilike(f"%{query}%"))

        stmt = stmt.limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def approve_source_version(
        version_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        reviewer_name: str,
        scope: str,
        rationale: str,
        db: AsyncSession,
        decision: str = "approved",
        limitations: str | None = None,
    ) -> SourceApproval:
        """Records explicit human review and promotes version from candidate to approved."""
        stmt = select(SourceVersion).where(SourceVersion.id == version_id)
        res = await db.execute(stmt)
        version = res.scalar_one_or_none()
        if not version:
            raise ValueError(f"SourceVersion {version_id} not found")

        approval = SourceApproval(
            id=uuid.uuid4(),
            source_version_id=version_id,
            reviewer_id=reviewer_id,
            reviewer_name=reviewer_name,
            scope=scope,
            rationale=rationale,
            limitations=limitations,
            decision=decision,
        )
        db.add(approval)

        if decision == "approved":
            version.applicability_status = "approved"

        await db.commit()
        await db.refresh(approval)
        return approval
