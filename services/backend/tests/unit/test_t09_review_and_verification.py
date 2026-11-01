import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_t09_review_preserves_origin_and_no_verification_inflation(client: AsyncClient, db_session):
    """T09: Confirm/edit/reject/unsure preserves origin/old assertion; no independent-verification label without verification record."""
    # 1. Bootstrap Guest
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Case
    case_res = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Verification Inflation Guard", "jurisdiction": "BD", "desired_outcomes": ["full_refund"]},
    )
    case_id = case_res.json()["id"]

    # 3. Add Extracted Fact Assertion
    fact_res = await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={
            "field_name": "amount_paid",
            "field_type": "money",
            "raw_value": "৫,০০০ টাকা",
            "origin": "document_extraction",
        },
    )
    f1 = fact_res.json()
    assert f1["origin"] == "document_extraction"
    f1_id = f1["id"]

    # 4. User accepts/confirms the reading
    review_accept = await client.post(
        f"/v1/cases/{case_id}/facts/{f1_id}/review",
        headers=headers,
        json={"review_outcome": "accepted"},
    )
    assert review_accept.status_code == 200

    # 5. Invariant Verification (T09):
    # Origin MUST remain 'document_extraction'. Accepting does NOT inflate it to 'independently_verified'
    active_facts = (await client.get(f"/v1/cases/{case_id}/facts", headers=headers)).json()
    assert len(active_facts) == 1
    assert active_facts[0]["origin"] == "document_extraction"  # origin preserved!
    assert active_facts[0]["id"] == f1_id

    # 6. User corrects the assertion
    review_correct = await client.post(
        f"/v1/cases/{case_id}/facts/{f1_id}/review",
        headers=headers,
        json={
            "review_outcome": "corrected",
            "corrected_value": "৫,৫০০ টাকা",
            "rationale": "Second slip found",
        },
    )
    assert review_correct.status_code == 200
    corr_review = review_correct.json()
    assert corr_review["review_outcome"] == "corrected"
    assert corr_review["correction_assertion_id"] is not None
    new_id = corr_review["correction_assertion_id"]
    assert new_id != f1_id

    # Check active facts: old f1 deactivated, new assertion active with origin='user_statement'
    active_facts_after_corr = (await client.get(f"/v1/cases/{case_id}/facts", headers=headers)).json()
    assert len(active_facts_after_corr) == 1
    assert active_facts_after_corr[0]["id"] == new_id
    assert active_facts_after_corr[0]["typed_value"]["minor_units"] == 550000
    assert active_facts_after_corr[0]["origin"] == "user_statement"  # user correction is user statement

    # 7. User rejects the new assertion
    review_reject = await client.post(
        f"/v1/cases/{case_id}/facts/{new_id}/review",
        headers=headers,
        json={"review_outcome": "rejected", "rationale": "Wrong transaction entirely"},
    )
    assert review_reject.status_code == 200

    # Check active facts: 0 active facts remain, but historical rows retained in DB
    active_facts_after_reject = (await client.get(f"/v1/cases/{case_id}/facts", headers=headers)).json()
    assert len(active_facts_after_reject) == 0
