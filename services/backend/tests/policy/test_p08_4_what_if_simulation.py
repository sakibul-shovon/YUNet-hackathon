import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_p08_4_what_if_zero_persistence_t31(client: AsyncClient, db_session):
    """T31 Invariant: What-If simulation has ZERO persistent database side effects.

    Facts and row versions must not change during simulation.
    """
    boot = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {boot.json()['access_token']}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "MFS Dispute Case", "jurisdiction": "BD"},
    )).json()
    case_id = case["id"]

    # Initial facts: unauthorized charge but no provider ticket filed
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "payment_instrument_kind", "field_type": "string", "raw_value": "mfs_wallet"},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "transaction_unauthorized", "field_type": "boolean", "raw_value": True},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "otp_pin_voluntarily_shared_to_fraudster", "field_type": "boolean", "raw_value": False},
    )

    # Count existing facts and check case row version
    facts_before = (await client.get(f"/v1/cases/{case_id}/facts", headers=headers)).json()
    case_before = (await client.get(f"/v1/cases/{case_id}", headers=headers)).json()
    assert len(facts_before) == 3

    # 1. Relevant Counterfactual: What if provider_ticket_filed == True?
    sim_res = await client.post(
        f"/v1/cases/{case_id}/what-if",
        headers=headers,
        json={"overrides": {"provider_ticket_filed": True}},
    )
    assert sim_res.status_code == 200
    sim_data = sim_res.json()

    assert sim_data["is_material_change"] is True
    # Invariant T31: Verify route shifted
    diff = sim_data["route_diff"]
    mfs_diff = next(d for d in diff if d["issue_type"] == "mfs_unauthorized_charge")
    assert mfs_diff["baseline_status"] == "needs_facts"
    assert mfs_diff["simulated_status"] == "supported"
    assert mfs_diff["changed"] is True

    # Invariant T31 Check: Verify ZERO persistent DB mutations!
    facts_after = (await client.get(f"/v1/cases/{case_id}/facts", headers=headers)).json()
    case_after = (await client.get(f"/v1/cases/{case_id}", headers=headers)).json()
    assert len(facts_after) == len(facts_before)
    assert case_after["row_version"] == case_before["row_version"]

    # 2. Irrelevant Counterfactual: Changing an unrelated field
    sim_irrelevant = await client.post(
        f"/v1/cases/{case_id}/what-if",
        headers=headers,
        json={"overrides": {"unrelated_customer_note": "I called twice"}},
    )
    assert sim_irrelevant.status_code == 200
    irrel_data = sim_irrelevant.json()
    assert irrel_data["is_material_change"] is False

    # 3. Explicit Apply Workflow: user decides to adopt the what-if fact into their case
    apply_res = await client.post(
        f"/v1/cases/{case_id}/what-if/apply",
        headers=headers,
        json={"overrides": {"provider_ticket_filed": True}},
    )
    assert apply_res.status_code == 200
    assert len(apply_res.json()) == 1
    assert apply_res.json()[0]["field_name"] == "provider_ticket_filed"

    # Now verify that the fact is genuinely saved in DB
    facts_after_apply = (await client.get(f"/v1/cases/{case_id}/facts", headers=headers)).json()
    assert len(facts_after_apply) == 4
