import pytest
from httpx import AsyncClient

from app.actions.draft_generator import DraftRequestGenerator


def test_t26_threat_and_false_claim_rejection():
    """T26: Draft lacks unsupported threats/guilt/guaranteed refund; violent threats and false claims rejected."""
    # 1. Threat keywords rejected
    with pytest.raises(ValueError, match="aggressive threat or extortion"):
        DraftRequestGenerator.validate_safety_and_tone("I will shut down your business if you don't refund immediately!")

    with pytest.raises(ValueError, match="aggressive threat or extortion"):
        DraftRequestGenerator.validate_safety_and_tone("তোমাকে জেলে ঢুকিয়ে দেব টাকা না দিলে!")

    # 2. False claim of official filing rejected
    with pytest.raises(ValueError, match="Falsely claims official filing"):
        DraftRequestGenerator.validate_safety_and_tone("This case has been officially filed by ClaimCraft in magistrate court.")


def test_t26_draft_generation_invariants():
    """T26: Legitimate draft is factual, respectful, and strictly retains unsubmitted state."""
    facts = {
        "amount_paid": 550000,  # 5,500 BDT
        "merchant_name": "Daraz Bangladesh",
        "incident_date": "2026-10-15",
        "goods_delivered": False,
    }

    # English draft
    draft_en = DraftRequestGenerator.generate_draft(
        case_title="Non-delivery of Smartphone",
        merchant_name="Daraz Bangladesh",
        facts=facts,
        locale="en",
        remedy="full_refund",
    )
    assert draft_en.lifecycle_state == "unsubmitted_draft"
    assert draft_en.is_sent is False
    assert draft_en.is_filed is False
    assert "৳ 5,500.00 BDT" in draft_en.body_text
    assert "Daraz Bangladesh" in draft_en.recipient
    assert "Consumers' Right Protection Act, 2009" in draft_en.citations[0]
    assert "UNSUBMITTED DRAFT" in draft_en.unsubmitted_banner_notice_en

    # Bangla draft
    draft_bn = DraftRequestGenerator.generate_draft(
        case_title="স্মার্টফোন ডেলিভারি না পাওয়া",
        merchant_name="দারাজ বাংলাদেশ",
        facts=facts,
        locale="bn",
        remedy="full_refund",
    )
    assert draft_bn.lifecycle_state == "unsubmitted_draft"
    assert draft_bn.is_sent is False
    assert draft_bn.is_filed is False
    assert "ভোক্তা-অধিকার সংরক্ষণ আইন, ২০০৯" in draft_bn.body_text
    assert "অননুমোদিত খসড়া" in draft_bn.unsubmitted_banner_notice_bn


@pytest.mark.asyncio
async def test_t26_draft_api_endpoint_and_tenant_isolation(client: AsyncClient, db_session):
    """P04.5 / T26: Integration test for draft retrieval API with unsubmitted status."""
    # 1. Bootstrap Guest
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Case with Facts
    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Smart Watch Order", "merchant_name": "Chaldal", "jurisdiction": "BD", "desired_outcomes": ["full_refund"]},
    )).json()
    case_id = case["id"]

    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "amount_paid", "field_type": "money", "raw_value": "৩,০০০ টাকা"},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "goods_delivered", "field_type": "boolean", "raw_value": False},
    )

    # 3. Retrieve English Draft
    res_en = await client.get(f"/v1/cases/{case_id}/draft?locale=en", headers=headers)
    assert res_en.status_code == 200
    data_en = res_en.json()
    assert data_en["lifecycle_state"] == "unsubmitted_draft"
    assert data_en["is_sent"] is False
    assert data_en["is_filed"] is False
    assert "Chaldal" in data_en["recipient"]

    # 4. Retrieve Bangla Draft
    res_bn = await client.get(f"/v1/cases/{case_id}/draft?locale=bn", headers=headers)
    assert res_bn.status_code == 200
    data_bn = res_bn.json()
    assert data_bn["locale"] == "bn"

    # 5. Tenant Isolation: foreign tenant receives 404
    client.cookies.clear()
    foreign_boot = await client.post("/auth/guest")
    foreign_headers = {"Authorization": f"Bearer {foreign_boot.json()['access_token']}"}

    foreign_draft = await client.get(f"/v1/cases/{case_id}/draft", headers=foreign_headers)
    assert foreign_draft.status_code == 404
