import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_jwt
from app.identity.models import ActorRole, Principal
from app.knowledge.diff_service import SectionAwareDiffService
from app.knowledge.service import KnowledgeService


@pytest.fixture
async def reviewer_client(client: AsyncClient, db_session: AsyncSession) -> tuple[AsyncClient, Principal, dict[str, str]]:
    principal = Principal(id=uuid.uuid4(), kind="permanent", locale="en-BD")
    db_session.add(principal)
    await db_session.flush()

    role = ActorRole(
        id=uuid.uuid4(),
        principal_id=principal.id,
        role="reviewer",
        grant_origin="admin_bootstrap",
        scope="global",
    )
    db_session.add(role)
    await db_session.commit()

    token = create_access_jwt(principal_id=principal.id, kind="permanent", roles=["reviewer"])
    headers = {"Authorization": f"Bearer {token}"}
    return client, principal, headers


@pytest.fixture
async def publisher_client(client: AsyncClient, db_session: AsyncSession) -> tuple[AsyncClient, Principal, dict[str, str]]:
    principal = Principal(id=uuid.uuid4(), kind="permanent", locale="en-BD")
    db_session.add(principal)
    await db_session.flush()

    role = ActorRole(
        id=uuid.uuid4(),
        principal_id=principal.id,
        role="publisher",
        grant_origin="admin_bootstrap",
        scope="global",
    )
    db_session.add(role)
    await db_session.commit()

    token = create_access_jwt(principal_id=principal.id, kind="permanent", roles=["publisher"])
    headers = {"Authorization": f"Bearer {token}"}
    return client, principal, headers


@pytest.mark.asyncio
async def test_p11_1_official_watchers_and_manual_import_t42(
    reviewer_client: tuple[AsyncClient, Principal, dict[str, str]],
    client: AsyncClient,
    db_session: AsyncSession,
):
    """P11.1 (T42): Test official watchers with SSRF protection, redirect quarantine, outage fallback, cosmetic diffs, and manual import."""
    _, _, reviewer_headers = reviewer_client

    # 1. Watcher check: New Candidate Discovered
    res_new = await client.post(
        "/v1/admin/watchers/check",
        json={"source_id": "bd_crpa_2009", "simulate_fixture": "new_candidate"},
        headers=reviewer_headers,
    )
    assert res_new.status_code == 200
    data_new = res_new.json()
    assert data_new["status"] == "fetched"
    assert data_new["change_type"] in ("new_document", "content_change")
    assert data_new["candidate_id"] is not None

    # 2. Watcher check: Substantive Content Change
    res_change = await client.post(
        "/v1/admin/watchers/check",
        json={"source_id": "bd_crpa_2009", "simulate_fixture": "content_change"},
        headers=reviewer_headers,
    )
    assert res_change.status_code == 200
    data_change = res_change.json()
    assert data_change["status"] == "fetched"
    assert data_change["candidate_id"] is not None

    # 3. Watcher check: Cosmetic Whitespace / Comment Delta
    # First, approve a baseline version so the watcher can compare against it
    family = await KnowledgeService.create_source_family(
        slug="bd_crpa_2009",
        title="Consumer Rights Protection Act 2009",
        issuer="Ministry of Law",
        db=db_session,
    )
    baseline_text = (
        "Consumer Rights Protection Act, 2009\n"
        "Section 45: Penalty for failure to sell or supply promised goods.\n"
        "Section 60: Limitation period for filing complaints is 30 days."
    )
    await KnowledgeService.create_source_version(
        family_id=family.id,
        version_tag="2009-enacted",
        text_content=baseline_text,
        issuer="Ministry of Law",
        document_type="statute",
        applicability_status="approved",
        db=db_session,
    )

    res_cosmetic = await client.post(
        "/v1/admin/watchers/check",
        json={"source_id": "bd_crpa_2009", "simulate_fixture": "cosmetic_whitespace"},
        headers=reviewer_headers,
    )
    assert res_cosmetic.status_code == 200
    data_cosmetic = res_cosmetic.json()
    assert data_cosmetic["status"] == "cosmetic_diff"
    assert data_cosmetic["change_type"] == "cosmetic_whitespace"

    # 4. Watcher check: Outage / HTTP 503 Fallback
    res_outage = await client.post(
        "/v1/admin/watchers/check",
        json={"source_id": "bd_crpa_2009", "simulate_fixture": "outage_503"},
        headers=reviewer_headers,
    )
    assert res_outage.status_code == 200
    data_outage = res_outage.json()
    assert data_outage["status"] == "temporarily_unavailable"
    assert "Official host returned status 503" in data_outage["error_message"]

    # 5. Watcher check: Redirect to Untrusted Destination Quarantined
    res_redirect = await client.post(
        "/v1/admin/watchers/check",
        json={"source_id": "bd_crpa_2009", "simulate_fixture": "redirect_untrusted"},
        headers=reviewer_headers,
    )
    assert res_redirect.status_code == 200
    data_redirect = res_redirect.json()
    assert data_redirect["status"] == "quarantined"
    assert "Redirect to non-allowlisted host" in data_redirect["quarantine_reason"]

    # 6. Watcher check: SSRF Protection against link-local metadata address
    res_ssrf = await client.post(
        "/v1/admin/watchers/check",
        json={"source_id": "bd_crpa_2009", "simulate_fixture": "ssrf_private_ip"},
        headers=reviewer_headers,
    )
    assert res_ssrf.status_code == 200
    data_ssrf = res_ssrf.json()
    assert data_ssrf["status"] == "quarantined"

    # 7. Manual-import fallback endpoint (air-gapped / offline ingestion)
    manual_payload = {
        "family_slug": "bd_crpa_2009",
        "title": "Consumer Rights Protection Act 2009 Official Gazette",
        "text_content": (
            "Section 45: Fine for deceptive advertisements is BDT 100,000.\n"
            "Section 60: Complaints must be filed within 30 days."
        ),
        "issuer": "Ministry of Law",
        "document_type": "statute",
        "publication_date": "2009-04-06",
        "commencement_date": "2009-04-06",
    }
    res_manual = await client.post(
        "/v1/admin/sources/manual-import",
        json=manual_payload,
        headers=reviewer_headers,
    )
    assert res_manual.status_code == 201
    manual_cand = res_manual.json()
    assert manual_cand["status"] == "candidate"
    assert manual_cand["origin_chain"]["origin"] == "manual_import"


@pytest.mark.asyncio
async def test_p11_2_section_aware_diff_and_commencement_t43(
    reviewer_client: tuple[AsyncClient, Principal, dict[str, str]],
    client: AsyncClient,
    db_session: AsyncSession,
):
    """P11.2 (T43): Test section-aware diff, candidate impact proposal, and commencement date safety."""
    _, _, reviewer_headers = reviewer_client

    # 1. Setup approved baseline with sections 45 and 60
    family = await KnowledgeService.create_source_family(
        slug="bd_crpa_test_diff",
        title="CRPA 2009 Diff Test",
        issuer="Ministry of Law",
        db=db_session,
    )
    baseline_version = await KnowledgeService.create_source_version(
        family_id=family.id,
        version_tag="2009-orig",
        text_content="CRPA baseline",
        issuer="Ministry of Law",
        document_type="statute",
        applicability_status="approved",
        db=db_session,
    )
    await KnowledgeService.add_provision(
        source_version_id=baseline_version.id,
        provision_path="sec:45",
        title="Section 45: Penalty for not selling promised goods",
        text_content="Any person who fails to sell promised goods shall be punished with fine not exceeding 50,000 taka.",
        db=db_session,
    )
    await KnowledgeService.add_provision(
        source_version_id=baseline_version.id,
        provision_path="sec:60",
        title="Section 60: Limitation period",
        text_content="Complaint must be submitted within 30 days from the cause of action.",
        db=db_session,
    )

    # 2. Ingest candidate via manual import:
    # - Section 45 is modified (fine increased to 200,000)
    # - Section 60 is unchanged
    # - Section 76 is newly added
    # - Commencement date is deferred by gazette notification
    candidate_text = (
        "Section 45: Any person who fails to sell promised goods shall be punished with fine not exceeding 200,000 taka.\n"
        "Section 60: Complaint must be submitted within 30 days from the cause of action.\n"
        "Section 76: Any consumer may file a complaint with the Director General and receive 25% of the penalty.\n"
        "This Act shall come into force on such date as the Government may, by notification in the official Gazette, appoint."
    )
    manual_res = await client.post(
        "/v1/admin/sources/manual-import",
        json={
            "family_slug": "bd_crpa_test_diff",
            "title": "CRPA Amendment 2026",
            "text_content": candidate_text,
            "issuer": "Ministry of Law",
            "document_type": "statute",
            "publication_date": "2026-03-01",
            "commencement_date": None,  # Deferred!
        },
        headers=reviewer_headers,
    )
    assert manual_res.status_code == 201
    candidate_id = manual_res.json()["id"]

    # 3. Call Section Diff Endpoint
    diff_res = await client.get(
        f"/v1/admin/source-candidates/{candidate_id}/diff",
        headers=reviewer_headers,
    )
    assert diff_res.status_code == 200
    diff_data = diff_res.json()

    # Invariant T43: Unapproved change is strictly NOT current law
    assert diff_data["is_current_law"] is False

    # Invariant T43: Unknown / deferred commencement date remains deferred and NEVER defaults to today
    assert diff_data["commencement_date"] is None
    assert diff_data["commencement_status"] == "deferred_pending_gazette"

    # Verify provision-level diff counts
    assert diff_data["added_count"] == 1  # Section 76 added
    assert diff_data["modified_count"] == 1  # Section 45 modified
    assert diff_data["unchanged_count"] == 1  # Section 60 unchanged

    # Verify impacted rules are proposed
    assert "R-CRPA-S45-MISLEADING-PRICE" in diff_data["impacted_rules"]
    assert "R-CRPA-S76-REWARD-25PCT" in diff_data["impacted_rules"]
    assert "consumer_ecommerce" in diff_data["impacted_domains"]


@pytest.mark.asyncio
async def test_p11_3_scoped_approval_and_consumer_veto_t44(
    reviewer_client: tuple[AsyncClient, Principal, dict[str, str]],
    client: AsyncClient,
    db_session: AsyncSession,
):
    """P11.3 (T44): Reviewer scoped approval promotes candidate; consumer/model is forbidden."""
    _, _, reviewer_headers = reviewer_client

    # 1. Ingest candidate
    manual_res = await client.post(
        "/v1/admin/sources/manual-import",
        json={
            "family_slug": "dncrp_ccms_portal",
            "title": "DNCRP CCMS Portal Procedure 2026",
            "text_content": "Section 1: Online complaints require National ID and proof of purchase.",
            "issuer": "DNCRP",
            "document_type": "procedure_guide",
            "publication_date": "2026-01-15",
            "commencement_date": "2026-01-15",
        },
        headers=reviewer_headers,
    )
    candidate_id = manual_res.json()["id"]

    # 2. Consumer attempt to approve -> 403 FORBIDDEN
    guest_res = await client.post("/auth/guest")
    consumer_token = guest_res.json()["access_token"]
    consumer_headers = {"Authorization": f"Bearer {consumer_token}"}

    res_veto = await client.post(
        f"/v1/admin/source-candidates/{candidate_id}/approve",
        json={
            "scope": "origin_and_procedure",
            "decision": "approved",
            "rationale": "Consumer self-service approving rules.",
        },
        headers=consumer_headers,
    )
    assert res_veto.status_code == 403

    # 3. Unauthenticated attempt -> 401 UNAUTHORIZED
    client.cookies.clear()
    res_unauth = await client.post(
        f"/v1/admin/source-candidates/{candidate_id}/approve",
        json={
            "scope": "origin_and_procedure",
            "decision": "approved",
            "rationale": "No authentication.",
        },
    )
    assert res_unauth.status_code == 401

    # 4. Reviewer scoped approval succeeds
    res_approve = await client.post(
        f"/v1/admin/source-candidates/{candidate_id}/approve",
        json={
            "scope": "origin_and_procedure",
            "decision": "approved",
            "rationale": "Verified procedure instructions against CCMS portal documentation.",
            "limitations": "Applies to CCMS web submission portal only.",
        },
        headers=reviewer_headers,
    )
    assert res_approve.status_code == 200
    approval_data = res_approve.json()
    assert approval_data["decision"] == "approved"
    assert approval_data["scope"] == "origin_and_procedure"


@pytest.mark.asyncio
async def test_p11_4_release_builder_atomic_promotion_and_rollback_t45(
    publisher_client: tuple[AsyncClient, Principal, dict[str, str]],
    client: AsyncClient,
    db_session: AsyncSession,
):
    """P11.4 (T45): Immutable release builder, atomic pointer swap, instant rollback, and emergency disable."""
    _, _, publisher_headers = publisher_client

    # 1. Setup approved source versions
    family = await KnowledgeService.create_source_family(
        slug="crpa_release_test",
        title="CRPA Release Test Family",
        issuer="Ministry of Law",
        db=db_session,
    )
    v1 = await KnowledgeService.create_source_version(
        family_id=family.id,
        version_tag="v1-stable",
        text_content="CRPA v1 text",
        issuer="Ministry of Law",
        document_type="statute",
        applicability_status="approved",
        db=db_session,
    )
    v2 = await KnowledgeService.create_source_version(
        family_id=family.id,
        version_tag="v2-amended",
        text_content="CRPA v2 text",
        issuer="Ministry of Law",
        document_type="statute",
        applicability_status="approved",
        db=db_session,
    )

    # 2. Build Release 1
    rel1_payload = {
        "release_id": "rel_2026_01_v1",
        "release_mode": "procedure_guidance",
        "source_version_ids": [str(v1.id)],
        "rules": [{"rule_id": "rule_v1", "status": "active"}],
        "lexical_index_hash": "lexical_hash_v1",
        "dense_index_model": "multilingual-e5-small",
    }
    b1_res = await client.post("/v1/admin/releases/build", json=rel1_payload, headers=publisher_headers)
    assert b1_res.status_code == 201
    assert b1_res.json()["is_active"] is False

    # 3. Promote Release 1 (Atomic Pointer Swap)
    p1_res = await client.post("/v1/admin/releases/rel_2026_01_v1/promote", headers=publisher_headers)
    assert p1_res.status_code == 200
    assert p1_res.json()["is_active"] is True

    # Verify public release matches Release 1
    pub1 = await client.get("/v1/knowledge/release")
    assert pub1.status_code == 200
    assert pub1.json()["release_id"] == "rel_2026_01_v1"

    # 4. Build Release 2
    rel2_payload = {
        "release_id": "rel_2026_02_v2",
        "release_mode": "procedure_guidance",
        "source_version_ids": [str(v2.id)],
        "rules": [{"rule_id": "rule_v2", "status": "active"}],
        "lexical_index_hash": "lexical_hash_v2",
        "dense_index_model": "multilingual-e5-small",
    }
    b2_res = await client.post("/v1/admin/releases/build", json=rel2_payload, headers=publisher_headers)
    assert b2_res.status_code == 201

    # Promote Release 2
    p2_res = await client.post("/v1/admin/releases/rel_2026_02_v2/promote", headers=publisher_headers)
    assert p2_res.status_code == 200
    assert p2_res.json()["is_active"] is True

    # Verify public release now matches Release 2
    pub2 = await client.get("/v1/knowledge/release")
    assert pub2.json()["release_id"] == "rel_2026_02_v2"

    # 5. Rollback from Release 2 to Release 1 (T45: Never mixes versions)
    rollback_res = await client.post(
        "/v1/admin/releases/rel_2026_02_v2/rollback",
        json={"target_release_id": "rel_2026_01_v1", "rationale": "Rollback due to downstream reconciliation review"},
        headers=publisher_headers,
    )
    assert rollback_res.status_code == 200
    assert rollback_res.json()["release_id"] == "rel_2026_01_v1"
    assert rollback_res.json()["is_active"] is True

    # Verify public release is restored to Release 1
    pub_rb = await client.get("/v1/knowledge/release")
    assert pub_rb.json()["release_id"] == "rel_2026_01_v1"

    # 6. Emergency Disable Overlay
    dis_res = await client.post("/v1/admin/releases/rel_2026_01_v1/disable", headers=publisher_headers)
    assert dis_res.status_code == 200
    assert dis_res.json()["is_active"] is False

    # After emergency disable, no active release is returned
    pub_dis = await client.get("/v1/knowledge/release")
    assert pub_dis.status_code == 404
    assert pub_dis.json()["detail"]["error"]["code"] == "NO_ACTIVE_RELEASE"


@pytest.mark.asyncio
async def test_p11_5_impacted_case_reassessment_queue_and_source_health_t39_t45(
    publisher_client: tuple[AsyncClient, Principal, dict[str, str]],
    client: AsyncClient,
    db_session: AsyncSession,
):
    """P11.5 (T39, T45): Only dependent cases are flagged; historical interpretations retained; on-demand reassessment with diff."""
    _, _, publisher_headers = publisher_client

    # 1. Create a consumer with an e-commerce pricing deception case (dependent on Section 45)
    guest_res = await client.post("/auth/guest")
    consumer_token = guest_res.json()["access_token"]
    consumer_headers = {"Authorization": f"Bearer {consumer_token}"}

    case_res1 = await client.post(
        "/v1/cases",
        json={"title": "Pricing deception dispute", "locale": "en-BD"},
        headers=consumer_headers,
    )
    case_id1 = case_res1.json()["id"]

    # Add an issue track for pricing deception
    await client.post(
        f"/v1/cases/{case_id1}/issues",
        json={"canonical_taxonomy": "pricing_deception", "desired_remedy": "refund"},
        headers=consumer_headers,
    )

    # 2. Create another case with an UNRELATED issue (e.g. telecom outage)
    case_res2 = await client.post(
        "/v1/cases",
        json={"title": "Internet connectivity dispute", "locale": "en-BD"},
        headers=consumer_headers,
    )
    case_id2 = case_res2.json()["id"]

    await client.post(
        f"/v1/cases/{case_id2}/issues",
        json={"canonical_taxonomy": "billing_dispute", "desired_remedy": "service_credit"},
        headers=consumer_headers,
    )

    # 3. Build & promote a release updating Section 45 rules only
    family = await KnowledgeService.create_source_family(
        slug="crpa_sec45_update",
        title="CRPA Sec 45 Family",
        issuer="Ministry of Law",
        db=db_session,
    )
    v = await KnowledgeService.create_source_version(
        family_id=family.id,
        version_tag="v_sec45_mod",
        text_content="Section 45 modified text",
        issuer="Ministry of Law",
        document_type="statute",
        applicability_status="approved",
        db=db_session,
    )

    build_res = await client.post(
        "/v1/admin/releases/build",
        json={
            "release_id": "rel_sec45_2026",
            "release_mode": "procedure_guidance",
            "source_version_ids": [str(v.id)],
            "rules": [{"rule_id": "R-CRPA-S45-MISLEADING-PRICE", "status": "active"}],
        },
        headers=publisher_headers,
    )
    assert build_res.status_code == 201

    await client.post("/v1/admin/releases/rel_sec45_2026/promote", headers=publisher_headers)

    # 4. Trigger Impacted Case Flagging
    flag_res = await client.post(
        "/v1/admin/releases/rel_sec45_2026/flag-impacted-cases",
        headers=publisher_headers,
    )
    assert flag_res.status_code == 200
    flag_data = flag_res.json()

    # Invariant T39/T45: ONLY dependent case 1 is flagged; case 2 is NOT flagged!
    assert case_id1 in flag_data["flagged_case_ids"]
    assert case_id2 not in flag_data["flagged_case_ids"]

    # 5. Verify Timeline of Case 1 contains non-destructive notice
    timeline_res = await client.get(
        f"/v1/cases/{case_id1}/activity/timeline",
        headers=consumer_headers,
    )
    assert timeline_res.status_code == 200
    events = timeline_res.json()
    flagged_event = next((e for e in events if e["event_type"] == "source_update_flagged"), None)
    assert flagged_event is not None
    assert "rel_sec45_2026" in flagged_event["description"]

    # 6. Consumer triggers on-demand reassessment
    reassess_res = await client.post(
        f"/v1/cases/{case_id1}/reassess",
        headers=consumer_headers,
    )
    assert reassess_res.status_code == 200
    reassess_data = reassess_res.json()
    assert reassess_data["case_id"] == case_id1
    assert reassess_data["release_id"] == "rel_sec45_2026"
    assert "decision_diff" in reassess_data

    # 7. Check public source-health endpoint
    health_res = await client.get("/v1/knowledge/source-health")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert health_data["active_release_id"] == "rel_sec45_2026"
    assert len(health_data["sources"]) > 0
    crpa_source = next((s for s in health_data["sources"] if s["source_id"] == "bd_crpa_2009"), None)
    assert crpa_source is not None
    assert crpa_source["health_status"] == "current_check_passed"
