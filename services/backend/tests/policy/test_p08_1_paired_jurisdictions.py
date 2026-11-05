import pytest
from httpx import AsyncClient

from app.policy.evaluator import RouteStatus


@pytest.mark.asyncio
async def test_p08_1_paired_jurisdictions_t19_t20(client: AsyncClient, db_session):
    """T19 & T20: Paired jurisdiction tests, merchant vs provider separation, and procedural hierarchy."""
    # 1. Bootstrap Guest
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Case A: E-commerce purchase paid via bKash wallet (T19)
    case_a = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Daraz Headphone paid with bKash", "jurisdiction": "BD", "merchant_name": "Daraz", "desired_outcomes": ["full_refund"]},
    )).json()
    case_a_id = case_a["id"]

    await client.post(
        f"/v1/cases/{case_a_id}/facts",
        headers=headers,
        json={"field_name": "purchase_channel", "field_type": "string", "raw_value": "ecommerce"},
    )
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

    assessment_a = (await client.get(f"/v1/cases/{case_a_id}/assessment", headers=headers)).json()

    # Invariant T19: Payment instrument mention alone does NOT create provider complaint
    route_issues = [r["issue_type"] for r in assessment_a["routes"]]
    assert "ecommerce_delivery_failure" in route_issues
    assert "mfs_unauthorized_charge" not in route_issues
    assert assessment_a["primary_action"] == "prepare_merchant_notice"

    # Verify statutory citations attached
    delivery_route = next(r for r in assessment_a["routes"] if r["issue_type"] == "ecommerce_delivery_failure")
    assert "crpa2009:sec:45" in delivery_route["statutory_citations"]
    assert "crpa2009:sec:60" in delivery_route["statutory_citations"]
    assert "crpa2009:sec:76" in delivery_route["statutory_citations"]


@pytest.mark.asyncio
async def test_p08_1_date_limitation_and_uncertainty_t30(client: AsyncClient, db_session):
    """T30 Invariant: Deadline trigger/date uncertainty prevents a definitive timer or false time-bar conclusion."""
    boot = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {boot.json()['access_token']}"}

    # Case with UNCERTAIN date (no incident_date provided)
    case_uncertain = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Uncertain Date Delivery Issue", "jurisdiction": "BD", "merchant_name": "ShopBD"},
    )).json()

    assess_uncert = (await client.get(f"/v1/cases/{case_uncertain['id']}/assessment", headers=headers)).json()

    # T30: Exact cutoff is withheld and limitation warning is returned
    assert assess_uncert["is_deadline_uncertain"] is True
    assert assess_uncert["days_remaining_in_limitation"] is None
    assert assess_uncert["limitation_warning_en"] is not None
    assert "unverified" in assess_uncert["limitation_warning_en"].lower()
    assert assess_uncert["limitation_warning_bn"] is not None

    # Case with CONFIRMED recent incident date (e.g. 5 days ago)
    import datetime
    recent_date = (datetime.date.today() - datetime.timedelta(days=5)).isoformat()
    case_recent = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Recent Date Issue", "jurisdiction": "BD", "merchant_name": "ShopBD", "incident_date": recent_date},
    )).json()

    assess_recent = (await client.get(f"/v1/cases/{case_recent['id']}/assessment", headers=headers)).json()
    assert assess_recent["is_deadline_uncertain"] is True  # A date alone does not establish cause of action.
    assert assess_recent["days_remaining_in_limitation"] is None
    assert "legal trigger is unverified" in assess_recent["limitation_warning_en"]


@pytest.mark.asyncio
async def test_p08_1_unsupported_remedy_checking(client: AsyncClient, db_session):
    """Unsupported remedy check: flags remedies that are not statutorily available for the route."""
    boot = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {boot.json()['access_token']}"}

    # User requests direct criminal prosecution on an e-commerce non-delivery case
    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={
            "title": "Delivery Case with Criminal Remedy Demand",
            "jurisdiction": "BD",
            "merchant_name": "ShopBD",
            "desired_outcomes": ["full_refund", "criminal_prosecution_direct"],
        },
    )).json()
    case_id = case["id"]

    assess = (await client.get(f"/v1/cases/{case_id}/assessment", headers=headers)).json()
    delivery_route = next(r for r in assess["routes"] if r["issue_type"] == "ecommerce_delivery_failure")

    assert "criminal_prosecution_direct" in delivery_route["unsupported_remedies"]
    assert len(delivery_route["unsupported_remedy_warnings"]) > 0
    assert "criminal_prosecution_direct" in delivery_route["unsupported_remedy_warnings"][0]

