import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_p08_5_safety_hazard_priority_t32(client: AsyncClient, db_session):
    """T32 Invariant: Product safety hazard question is prioritized above billing/shipping questions."""
    boot = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {boot.json()['access_token']}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Exploding Charger Incident", "jurisdiction": "BD", "merchant_name": "GadgetShop"},
    )).json()
    case_id = case["id"]

    # Initial assessment without answers
    assess = (await client.get(f"/v1/cases/{case_id}/assessment", headers=headers)).json()
    nbq = assess["next_best_question"]

    # Invariant T32: Safety question MUST take top priority
    assert nbq is not None
    assert nbq["priority"] == "safety"
    assert nbq["fact_field"] == "product_presents_immediate_hazard"
    assert "16121" in nbq["relevance_rationale"]


@pytest.mark.asyncio
async def test_p08_5_strict_otp_pin_prohibition_t32(client: AsyncClient, db_session):
    """T32 Invariant: Strictly forbids requesting or collecting OTP, PIN, passwords, or CVV."""
    boot = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {boot.json()['access_token']}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "MFS Issue", "jurisdiction": "BD"},
    )).json()
    case_id = case["id"]

    # Attempting to answer NBQ with an OTP or PIN field MUST be rejected with HTTP 400
    res_otp = await client.post(
        f"/v1/cases/{case_id}/nbq/answer",
        headers=headers,
        json={"question_key": "nbq_pin", "fact_field": "user_mfs_pin", "value": "1234"},
    )
    assert res_otp.status_code == 400
    assert "strictly prohibited" in res_otp.json()["detail"].lower()

    # Attempting to apply what-if with an OTP override MUST be rejected
    res_sim = await client.post(
        f"/v1/cases/{case_id}/what-if",
        headers=headers,
        json={"overrides": {"customer_otp_code": "889911"}},
    )
    assert res_sim.status_code == 400
    assert "prohibited credential" in res_sim.json()["detail"].lower()


@pytest.mark.asyncio
async def test_p08_5_nbq_skip_preserves_unknown_t32(client: AsyncClient, db_session):
    """T32 Invariant: Skipping a question preserves UNKNOWN status (never coerced to false)

    and ensures the question is not repetitively prompted.
    """
    boot = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {boot.json()['access_token']}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "E-commerce Case", "jurisdiction": "BD", "merchant_name": "Daraz"},
    )).json()
    case_id = case["id"]

    # Get first NBQ
    assess_1 = (await client.get(f"/v1/cases/{case_id}/assessment", headers=headers)).json()
    q1 = assess_1["next_best_question"]
    assert q1 is not None

    # Skip question
    assess_2 = (await client.post(
        f"/v1/cases/{case_id}/nbq/skip",
        headers=headers,
        json={"question_key": q1["question_key"], "fact_field": q1["fact_field"]},
    )).json()

    # Verify that skipped question is NOT repeated!
    q2 = assess_2["next_best_question"]
    if q2 is not None:
        assert q2["question_key"] != q1["question_key"]
        assert q2["fact_field"] != q1["fact_field"]

    # Verify that facts database does NOT have a false assertion created for the skipped question
    facts = (await client.get(f"/v1/cases/{case_id}/facts", headers=headers)).json()
    assert not any(f["field_name"] == q1["fact_field"] for f in facts)
