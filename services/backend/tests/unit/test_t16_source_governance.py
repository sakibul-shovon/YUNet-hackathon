import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.knowledge.service import KnowledgeService


@pytest.mark.asyncio
async def test_t16_source_hash_roundtrip_and_candidate_exclusion(db_session: AsyncSession):
    """T16: Candidate/unapproved source absent from authoritative output; exact hash round-trip."""
    # 1. Create a source family
    family = await KnowledgeService.create_source_family(
        slug="crpa_2009",
        title="Consumer Rights Protection Act 2009",
        issuer="Ministry of Law",
        db=db_session,
    )
    assert family.slug == "crpa_2009"

    # 2. Add an unapproved candidate source version
    original_text = (
        "ধারা ৪৫: মিথ্যা বিজ্ঞাপন দ্বারা ক্রেতা সাধারণকে প্রতারিত করিলে তিনি অন্যূন "
        "এক বৎসর কারাদণ্ড বা অনধিক দুই লক্ষ টাকা অর্থদণ্ড বা উভয় দণ্ডে দণ্ডিত হইবেন।"
    )
    version = await KnowledgeService.create_source_version(
        family_id=family.id,
        version_tag="2009-enacted",
        text_content=original_text,
        issuer="Bangladesh Government Press",
        document_type="statute",
        publication_date="2009-04-06",
        commencement_date="2009-04-06",
        applicability_status="candidate",  # Unapproved candidate
        db=db_session,
    )

    # 3. Verify exact SHA-256 hash round-trip
    computed_hash = KnowledgeService.compute_sha256(original_text.strip())
    assert version.clean_text_hash == computed_hash
    assert version.raw_bytes_hash == computed_hash
    assert version.applicability_status == "candidate"

    # 4. Add provision under candidate version
    prov = await KnowledgeService.add_provision(
        source_version_id=version.id,
        provision_path="sec:45",
        title="মিথ্যা বিজ্ঞাপন দ্বারা প্রতারণার দণ্ড",
        text_content=original_text,
        db=db_session,
    )
    assert prov.provision_path == "sec:45"

    # 5. T16 INVARIANT: Candidate provisions MUST NOT appear in authoritative search!
    approved_results_before = await KnowledgeService.query_approved_provisions(
        db=db_session,
        query="মিথ্যা বিজ্ঞাপন",
    )
    assert len(approved_results_before) == 0, "Candidate source leaked into approved search!"

    # 6. Explicit human review and approval
    reviewer_id = uuid.uuid4()
    approval = await KnowledgeService.approve_source_version(
        version_id=version.id,
        reviewer_id=reviewer_id,
        reviewer_name="Barrister S. Rahman",
        scope="statutory_interpretation",
        rationale="Verified against Bangladesh Gazette extraordinary publication dated 6 April 2009.",
        limitations="Applies to consumer commerce within Bangladesh territory.",
        decision="approved",
        db=db_session,
    )
    assert approval.decision == "approved"
    assert approval.scope == "statutory_interpretation"

    # 7. Now the approved provision is discoverable in authoritative search
    approved_results_after = await KnowledgeService.query_approved_provisions(
        db=db_session,
        query="মিথ্যা বিজ্ঞাপন",
    )
    assert len(approved_results_after) == 1
    assert approved_results_after[0].provision_path == "sec:45"
    assert "মিথ্যা বিজ্ঞাপন" in approved_results_after[0].normalized_text

