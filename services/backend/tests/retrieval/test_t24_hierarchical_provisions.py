import pytest
from httpx import AsyncClient

from app.retrieval.provision_service import ProvisionService


def test_t24_exact_bengali_and_latin_section_lookup():
    """T24: Exact Bengali and Latin section lookup round-trip preserves section, subsection, and aliases."""
    # 1. Latin Section 45 lookup
    res_latin = ProvisionService.lookup_exact_provision("sec:45")
    assert res_latin.match_found is True
    assert res_latin.provision is not None
    assert res_latin.provision.section_number == "45"
    assert res_latin.provision.section_bn == "৪৫"
    assert "প্রতিশ্রুত পণ্য বা সেবা" in res_latin.provision.title_bn
    assert res_latin.provision.citation_handle == "crpa2009:sec:45"

    # 2. Bengali Section 45 lookup
    res_bn = ProvisionService.lookup_exact_provision("ধারা ৪৫")
    assert res_bn.match_found is True
    assert res_bn.provision is not None
    assert res_bn.provision.citation_handle == "crpa2009:sec:45"

    # 3. Subsection 76(4) Latin and Bengali lookup
    res_sub_latin = ProvisionService.lookup_exact_provision("sec:76(4)")
    assert res_sub_latin.match_found is True
    assert res_sub_latin.provision is not None
    assert res_sub_latin.provision.section_number == "76(4)"
    assert res_sub_latin.provision.parent_path == "sec:76"
    assert res_sub_latin.provision.parent_provision is not None
    assert res_sub_latin.provision.parent_provision["citation_handle"] == "crpa2009:sec:76"

    res_sub_bn = ProvisionService.lookup_exact_provision("ধারা ৭৬(৪)")
    assert res_sub_bn.match_found is True
    assert res_sub_bn.provision is not None
    assert res_sub_bn.provision.citation_handle == "crpa2009:sec:76(4)"

    # 4. Section 60 (30 days limitation)
    res_limitation = ProvisionService.lookup_exact_provision("ধারা ৬০")
    assert res_limitation.match_found is True
    assert "৩০ (ত্রিশ) দিন" in res_limitation.provision.canonical_text_bn

    # 5. Section 76 (25% reward)
    res_reward = ProvisionService.lookup_exact_provision("ধারা ৭৬")
    assert res_reward.match_found is True
    assert "২৫ শতাংশ" in res_reward.provision.canonical_text_bn

    # 6. Bangladesh Bank CIPC Stage 1 and 2
    res_stage1 = ProvisionService.lookup_exact_provision("স্তর ১")
    assert res_stage1.match_found is True
    assert res_stage1.provision.citation_handle == "bb_cipc:stage:provider_grievance"

    res_stage2 = ProvisionService.lookup_exact_provision("stage:cipc_escalation")
    assert res_stage2.match_found is True
    assert res_stage2.provision.citation_handle == "bb_cipc:stage:cipc_escalation"


def test_t24_long_bengali_clause_preserves_qualifications():
    """Preserve the actual Section 76(4) exclusion, rather than an invented refund proviso."""
    res = ProvisionService.lookup_exact_provision('sec:76(4)')
    assert res.match_found and res.preserves_qualification
    expected = 'অভিযোগকারী অধিদপ্তরের কোন কর্মকর্তা বা কর্মচারী হইয়া থাকিলে'
    assert expected in res.provision.canonical_text_bn
    assert any(expected in clause for clause in res.provision.qualifications_and_exceptions)
    assert not ProvisionService.lookup_exact_provision('sec:45(2)').match_found


def test_t24_anti_fabrication_never_invents_missing_provisions():
    """T24 Invariant: Non-existent or unapproved sections return match_found=False and are NEVER invented."""
    invalid_queries = [
        "sec:999",
        "sec:45(2)",
        "ধারা ৯৯৯",
        "sec:100",
        "ধারা ১০৫",
        "section:fake_section",
        "ধারা ৩০০(৪)",
    ]
    for q in invalid_queries:
        res = ProvisionService.lookup_exact_provision(q)
        assert res.match_found is False, f"Expected non-existent query '{q}' to return False, but matched!"
        assert res.provision is None


def test_t24_hierarchical_provisions_tree():
    """T24: Hierarchical tree connects parent sections to subsections."""
    tree = ProvisionService.get_provisions_tree("bd_crpa_2009")
    assert len(tree) >= 4  # sec:41, sec:44, sec:45, sec:60, sec:76

    sec45 = next((item for item in tree if item.provision_path == "sec:76"), None)
    assert sec45 is not None
    assert len(sec45.children) >= 1
    assert sec45.children[0].provision_path == "sec:76(4)"


@pytest.mark.asyncio
async def test_t24_retrieval_api_endpoints(client: AsyncClient):
    """T24: Retrieval API endpoints for lookup, handle fetch, and tree."""
    # 1. GET /v1/retrieval/provisions/lookup with valid query
    resp = await client.get("/v1/retrieval/provisions/lookup?q=ধারা%20৪৫")
    assert resp.status_code == 200
    data = resp.json()
    assert data["match_found"] is True
    assert data["provision"]["citation_handle"] == "crpa2009:sec:45"
    assert data["preserves_qualification"] is False  # Section 45 has no invented proviso.

    # 2. GET /v1/retrieval/provisions/lookup with invalid query
    resp_bad = await client.get("/v1/retrieval/provisions/lookup?q=sec:999")
    assert resp_bad.status_code == 200
    bad_data = resp_bad.json()
    assert bad_data["match_found"] is False
    assert bad_data["provision"] is None

    # 3. GET /v1/retrieval/provisions/{citation_handle} valid
    resp_handle = await client.get("/v1/retrieval/provisions/crpa2009:sec:76(4)")
    assert resp_handle.status_code == 200
    handle_data = resp_handle.json()
    assert handle_data["section_number"] == "76(4)"
    assert handle_data["parent_path"] == "sec:76"

    # 4. GET /v1/retrieval/provisions/{citation_handle} invalid -> 404
    resp_404 = await client.get("/v1/retrieval/provisions/non_existent_statute:sec:1")
    assert resp_404.status_code == 404

    # 5. GET /v1/retrieval/sources/{source_id}/provisions
    resp_tree = await client.get("/v1/retrieval/sources/bd_crpa_2009/provisions")
    assert resp_tree.status_code == 200
    tree_data = resp_tree.json()
    assert len(tree_data) >= 4

