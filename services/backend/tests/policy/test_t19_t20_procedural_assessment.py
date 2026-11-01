import pytest
from httpx import AsyncClient

from app.policy.evaluator import RouteStatus


@pytest.mark.asyncio
async def test_t19_seller_nondelivery_vs_provider_conduct(client: AsyncClient, db_session):
    """T19: Seller non-delivery + payment instrument does not create provider-failure complaint; provider conduct can create one."""
    # 1. Bootstrap Guest
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Case A: E-Commerce Seller Delivery Failure where customer paid via bKash wallet
    case_a = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Daraz Order paid via bKash", "jurisdiction": "BD", "merchant_name": "Daraz", "desired_outcomes": ["full_refund"]},
    )).json()
    case_a_id = case_a["id"]

    # Add facts: purchase channel is ecommerce, goods not delivered, paid with mfs_wallet
    await client.post(
        f"/v1/cases/{case_a_id}/facts",
        headers=headers,
        json={"field_name": "goods_delivered", "field_type": "boolean", "raw_value": False},
    )
    await client.post(
        f"/v1/cases/{case_a_id}/facts",
        headers=headers,
        json={"field_name": "promised_delivery_date_passed", "field_type": "boolean", "raw_value": True},
    )
    await client.post(
        f"/v1/cases/{case_a_id}/facts",
        headers=headers,
        json={"field_name": "payment_instrument_kind", "field_type": "string", "raw_value": "mfs_wallet"},
    )
    await client.post(
        f"/v1/cases/{case_a_id}/facts",
        headers=headers,
        json={"field_name": "refund_already_issued", "field_type": "boolean", "raw_value": False},
    )
    await client.post(
        f"/v1/cases/{case_a_id}/facts",
        headers=headers,
        json={"field_name": "order_cancelled_by_buyer_before_dispatch", "field_type": "boolean", "raw_value": False},
    )

    # Assess Case A
    assessment_a = (await client.get(f"/v1/cases/{case_a_id}/assessment", headers=headers)).json()

    # T19 Invariant Check:
    # 1. Route must be against seller (ecommerce_delivery_failure)
    # 2. bKash payment instrument mention alone MUST NOT trigger mfs_unauthorized_charge route!
    route_issues = [r["issue_type"] for r in assessment_a["routes"]]
    assert "ecommerce_delivery_failure" in route_issues
    assert "mfs_unauthorized_charge" not in route_issues
    assert assessment_a["primary_action"] == "prepare_merchant_notice"

    # 3. Case B: Provider conduct (unauthorized deduction)
    case_b = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "bKash Unauthorized Charge", "jurisdiction": "BD", "desired_outcomes": ["full_refund"]},
    )).json()
    case_b_id = case_b["id"]

    await client.post(
        f"/v1/cases/{case_b_id}/facts",
        headers=headers,
        json={"field_name": "payment_instrument_kind", "field_type": "string", "raw_value": "mfs_wallet"},
    )
    await client.post(
        f"/v1/cases/{case_b_id}/facts",
        headers=headers,
        json={"field_name": "transaction_unauthorized", "field_type": "boolean", "raw_value": True},
    )

    assessment_b = (await client.get(f"/v1/cases/{case_b_id}/assessment", headers=headers)).json()
    route_issues_b = [r["issue_type"] for r in assessment_b["routes"]]
    assert "mfs_unauthorized_charge" in route_issues_b


@pytest.mark.asyncio
async def test_t20_provider_stage_hierarchy_and_nbq(client: AsyncClient, db_session):
    """T20: Provider-stage/exclusion/authorization ambiguity yields reviewed next step or clarification; no automatic regulator acceptance."""
    # 1. Bootstrap Guest
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Case: Unauthorized transaction reported, but no provider ticket filed yet
    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "MFS Disputed Transaction", "jurisdiction": "BD", "desired_outcomes": ["full_refund"]},
    )).json()
    case_id = case["id"]

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

    # 3. Assess Case before filing provider ticket
    res_1 = (await client.get(f"/v1/cases/{case_id}/assessment", headers=headers)).json()

    # T20 Invariant: Must mandate Stage 1 grievance to provider first, NOT BB escalation
    assert res_1["overall_status"] == "ready_for_provider_ticket"
    assert res_1["primary_action"] == "prepare_provider_formal_letter"

    # NBQ should ask if provider ticket is filed
    assert res_1["next_best_question"] is not None
    assert res_1["next_best_question"]["fact_field"] == "provider_ticket_filed"

    # 4. Consumer files ticket with provider and marks it True
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "provider_ticket_filed", "field_type": "boolean", "raw_value": True},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "otp_pin_voluntarily_shared_to_fraudster", "field_type": "boolean", "raw_value": False},
    )

    # 5. Re-assess Case after provider ticket filed
    res_2 = (await client.post(f"/v1/cases/{case_id}/assess", headers=headers)).json()

    # T20 Invariant: Unlocks Stage 2 escalation to Bangladesh Bank CIPC
    assert res_2["overall_status"] == "ready_for_bb_escalation"
    assert res_2["primary_action"] == "prepare_bb_cipc_escalation"
    assert any(c["id"] == "bb_cipc_procedure" for c in res_2["source_cards"])

    # 6. Tenant Isolation: foreign user cannot view assessment
    client.cookies.clear()
    foreign_boot = await client.post("/auth/guest")
    foreign_headers = {"Authorization": f"Bearer {foreign_boot.json()['access_token']}"}

    foreign_res = await client.get(f"/v1/cases/{case_id}/assessment", headers=foreign_headers)
    assert foreign_res.status_code == 404

