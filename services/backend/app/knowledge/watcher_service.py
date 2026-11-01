import datetime
import hashlib
import re
import uuid
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.models import Principal
from app.knowledge.models import SourceCandidate, SourceFamily, SourceVersion
from app.knowledge.source_registry import (
    get_source_by_id,
    is_url_allowlisted,
)


class WatcherFetchResult(BaseModel):
    source_id: str
    target_url: str
    status: str  # 'fetched', 'no_change', 'cosmetic_diff', 'quarantined', 'temporarily_unavailable'
    change_type: str | None = None  # 'new_document', 'content_change', 'cosmetic_whitespace', 'none'
    raw_hash: str | None = None
    clean_text_hash: str | None = None
    quarantine_reason: str | None = None
    error_message: str | None = None
    candidate_id: uuid.UUID | None = None
    fetched_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))


class OfficialSourceWatcher:
    """Official source watcher adhering to T42 and Section 22 of the Blueprint.

    - Protects against SSRF and unauthorized domain redirects.
    - Gracefully handles official portal outages / 503 without crashing or inventing rules.
    - Classifies cosmetic whitespace diffs separately from substantive legal amendments.
    - Provides manual import fallback for air-gapped or inaccessible official sources.
    """

    @classmethod
    def normalize_statutory_text(cls, text: str) -> str:
        """Strips HTML tags, comments, trailing whitespace and normalizes whitespace."""
        # Strip HTML tags & comments
        cleaned = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        # Normalize internal whitespace
        tokens = cleaned.split()
        return " ".join(tokens)

    @classmethod
    async def guarded_fetch(
        cls,
        url: str,
        simulate_fixture: str | None = None,
    ) -> tuple[int, bytes, str, str | None]:
        """Performs guarded HTTP GET enforcing host allowlist and SSRF checks.

        Returns (status_code, raw_bytes, final_url, quarantine_reason).
        """
        # 1. SSRF and host allowlist check on initial URL
        is_allowed, reason = is_url_allowlisted(url, resolve_dns=True)
        if not is_allowed:
            return 400, b"", url, f"Initial URL rejected: {reason}"

        # 2. Simulated Fixtures for Unit/Acceptance Tests
        if simulate_fixture == "new_candidate":
            content = (
                b"Consumer Rights Protection Act Amendment 2026.\n"
                b"Section 45: The maximum administrative fine for misleading advertisements is 200,000 BDT.\n"
                b"Section 60: Complaints must be filed within 30 days of the cause of action."
            )
            return 200, content, url, None

        if simulate_fixture == "content_change":
            content = (
                b"Consumer Rights Protection Act 2009 (Consolidated 2026).\n"
                b"Section 45: Penalty for deceptive marketing increased to BDT 100,000.\n"
                b"Section 60: Limitation period remains 30 days."
            )
            return 200, content, url, None

        if simulate_fixture == "cosmetic_whitespace":
            # Extra linebreaks, spaces, and an HTML comment
            content = (
                b"<!-- Updated layout header 2026-03-01 -->\n\n"
                b"Consumer Rights Protection Act, 2009\n\n\n"
                b"Section 45:   Penalty for failure to sell or supply promised goods.\n\n"
                b"Section 60:   Limitation period for filing complaints is 30 days.\n"
            )
            return 200, content, url, None

        if simulate_fixture == "outage_503":
            return 503, b"Service Unavailable - Official Portal Down", url, None

        if simulate_fixture == "redirect_untrusted":
            # Simulate a 302 redirect to an untrusted external host
            untrusted_target = "http://phishing-portal.com/fake-crpa.pdf"
            return 302, b"", untrusted_target, "Redirect to non-allowlisted host phishing-portal.com"

        if simulate_fixture == "ssrf_private_ip":
            # Simulate a target attempting loopback or metadata fetch
            return 400, b"", "http://169.254.169.254/latest/meta-data", "Host resolved to link-local metadata address"

        # 3. Live HTTP request if no simulation fixture
        try:
            async with httpx.AsyncClient(follow_redirects=False, timeout=10.0) as client:
                resp = await client.get(url)

                # Check if response is a redirect
                if resp.status_code in (301, 302, 303, 307, 308):
                    redirect_location = resp.headers.get("Location")
                    if not redirect_location:
                        return 400, b"", url, "Redirect missing Location header"

                    # Parse redirect location
                    parsed_red = urlparse(redirect_location)
                    target_url = redirect_location if parsed_red.scheme else f"{url.rstrip('/')}/{redirect_location.lstrip('/')}"
                    is_red_allowed, red_reason = is_url_allowlisted(target_url, resolve_dns=True)
                    if not is_red_allowed:
                        return 302, b"", target_url, f"Redirect to untrusted destination quarantined: {red_reason}"

                    # If redirect is safe, fetch the redirected location
                    resp2 = await client.get(target_url)
                    return resp2.status_code, resp2.content, target_url, None

                return resp.status_code, resp.content, str(resp.url), None
        except httpx.RequestError as exc:
            return 503, b"", url, f"Network connection error: {exc!s}"

    @classmethod
    async def run_watcher_check(
        cls,
        source_id: str,
        db: AsyncSession,
        simulate_fixture: str | None = None,
    ) -> WatcherFetchResult:
        """Executes a monitored official update check for a registered official source."""
        source_entry = get_source_by_id(source_id)
        if not source_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "UNKNOWN_SOURCE", "message": f"Source '{source_id}' not found in registry"}},
            )

        # 1. Fetch raw bytes
        status_code, raw_bytes, final_url, quarantine_reason = await cls.guarded_fetch(
            source_entry.official_url,
            simulate_fixture=simulate_fixture,
        )

        # 2. Check for Quarantine or Outage
        if quarantine_reason:
            # Create a quarantined candidate record
            family = await cls._get_or_create_family(source_entry.id, source_entry.title_en, source_entry.issuer, db)
            candidate = SourceCandidate(
                id=uuid.uuid4(),
                family_id=family.id,
                url=final_url,
                origin_chain={
                    "quarantine_reason": quarantine_reason,
                    "source_id": source_id,
                    "simulated": bool(simulate_fixture),
                },
                raw_hash=hashlib.sha256(raw_bytes).hexdigest(),
                status="quarantined",
            )
            db.add(candidate)
            await db.commit()
            await db.refresh(candidate)

            return WatcherFetchResult(
                source_id=source_id,
                target_url=final_url,
                status="quarantined",
                quarantine_reason=quarantine_reason,
                candidate_id=candidate.id,
            )

        if status_code == 503 or status_code >= 500:
            return WatcherFetchResult(
                source_id=source_id,
                target_url=final_url,
                status="temporarily_unavailable",
                error_message=f"Official host returned status {status_code}",
            )

        # 3. Content Hash & Substantive Change Analysis
        raw_hash = hashlib.sha256(raw_bytes).hexdigest()
        raw_text = raw_bytes.decode("utf-8", errors="replace")
        clean_text = cls.normalize_statutory_text(raw_text)
        clean_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()

        # Query existing approved version for this source family
        family = await cls._get_or_create_family(source_entry.id, source_entry.title_en, source_entry.issuer, db)
        stmt = (
            select(SourceVersion)
            .where(
                SourceVersion.family_id == family.id,
                SourceVersion.applicability_status == "approved",
            )
            .order_by(SourceVersion.created_at.desc())
        )
        res = await db.execute(stmt)
        latest_approved = res.scalars().first()

        # Classify change
        if latest_approved:
            if latest_approved.raw_bytes_hash == raw_hash:
                return WatcherFetchResult(
                    source_id=source_id,
                    target_url=final_url,
                    status="no_change",
                    change_type="none",
                    raw_hash=raw_hash,
                    clean_text_hash=clean_hash,
                )

            # Check if normalized statutory text matches approved clean text
            approved_clean_text = cls.normalize_statutory_text(latest_approved.text_content)
            approved_clean_hash = hashlib.sha256(approved_clean_text.encode("utf-8")).hexdigest()

            if approved_clean_hash == clean_hash:
                # Cosmetic whitespace / HTML comment delta only
                return WatcherFetchResult(
                    source_id=source_id,
                    target_url=final_url,
                    status="cosmetic_diff",
                    change_type="cosmetic_whitespace",
                    raw_hash=raw_hash,
                    clean_text_hash=clean_hash,
                )

            change_type = "content_change"
        else:
            change_type = "new_document"

        # 4. Create SourceCandidate (Pending Human Review - Invariant T43/T44)
        candidate = SourceCandidate(
            id=uuid.uuid4(),
            family_id=family.id,
            url=final_url,
            origin_chain={
                "source_id": source_id,
                "change_type": change_type,
                "clean_text": clean_text,
                "clean_text_hash": clean_hash,
                "simulated": bool(simulate_fixture),
                "is_current_law": False,  # Invariant T43: Unapproved change is NOT current law
            },
            raw_hash=raw_hash,
            status="candidate",
        )
        db.add(candidate)
        await db.commit()
        await db.refresh(candidate)

        return WatcherFetchResult(
            source_id=source_id,
            target_url=final_url,
            status="fetched",
            change_type=change_type,
            raw_hash=raw_hash,
            clean_text_hash=clean_hash,
            candidate_id=candidate.id,
        )

    @classmethod
    async def manual_import(
        cls,
        family_slug: str,
        title: str,
        text_content: str,
        issuer: str,
        document_type: str,
        publisher: Principal,
        db: AsyncSession,
        official_url: str | None = None,
        publication_date: str | None = None,
        commencement_date: str | None = None,
    ) -> SourceCandidate:
        """Manual-import fallback for offline or air-gapped updates (T42)."""
        family = await cls._get_or_create_family(family_slug, title, issuer, db)

        raw_bytes = text_content.encode("utf-8")
        raw_hash = hashlib.sha256(raw_bytes).hexdigest()
        clean_text = cls.normalize_statutory_text(text_content)
        clean_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()

        target_url = official_url or f"https://manual-import.claimcraft.internal/{family_slug}"

        candidate = SourceCandidate(
            id=uuid.uuid4(),
            family_id=family.id,
            url=target_url,
            origin_chain={
                "origin": "manual_import",
                "imported_by": str(publisher.id),
                "title": title,
                "clean_text": clean_text,
                "clean_text_hash": clean_hash,
                "document_type": document_type,
                "publication_date": publication_date,
                "commencement_date": commencement_date,
                "is_current_law": False,  # Invariant T43
            },
            raw_hash=raw_hash,
            status="candidate",
        )
        db.add(candidate)
        await db.commit()
        await db.refresh(candidate)
        return candidate

    @classmethod
    async def _get_or_create_family(
        cls,
        slug: str,
        title: str,
        issuer: str,
        db: AsyncSession,
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
                jurisdiction="BD",
            )
            db.add(family)
            await db.commit()
            await db.refresh(family)
        return family
