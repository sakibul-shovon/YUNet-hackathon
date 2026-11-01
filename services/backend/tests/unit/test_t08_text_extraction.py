import pytest
from httpx import AsyncClient
from pydantic import ValidationError

from app.extraction.adapter import CaseExtractor
from app.extraction.schemas import FactProposal, FactProposalSet, TextSpan


def test_t08_bangla_text_extraction():
    """T08: Bangla narrative extraction extracts merchant, amount, date, and status with verbatim spans."""
    narrative = (
        "আমি দারাজ থেকে ৫,৫০০ টাকার একটি ঘড়ি অর্ডার করেছিলাম ১৫ অক্টোবর ২০২৬ তারিখে। "
        "কিন্তু এখনও পণ্য পাইনি।"
    )
    result = CaseExtractor.propose(narrative)
    assert result.detected_domain == "consumer_ecommerce"
    assert result.detected_issue == "ecommerce_delivery_failure"
    assert len(result.spans) >= 4

    prop_map = {p.field_name: p for p in result.proposals}
    assert "merchant_name" in prop_map
    assert prop_map["merchant_name"].raw_value == "দারাজ"

    assert "amount_paid" in prop_map
    assert prop_map["amount_paid"].raw_value == 550000  # 5,500 BDT in minor units

    assert "incident_date" in prop_map
    assert prop_map["incident_date"].raw_value == "2026-10-15"

    assert "goods_delivered" in prop_map
    assert prop_map["goods_delivered"].raw_value is False

    # Check span references
    valid_ids = {s.span_id for s in result.spans}
    for p in result.proposals:
        for s_id in p.span_ids:
            assert s_id in valid_ids


def test_t08_banglish_and_english_extraction():
    """T08: Banglish and English extraction."""
    # Banglish
    banglish = "Daraz theke 5500 tk product order korsilam kintu delivery pai nai"
    res_bn = CaseExtractor.propose(banglish)
    prop_map_bn = {p.field_name: p for p in res_bn.proposals}
    assert prop_map_bn["merchant_name"].raw_value == "Daraz"
    assert prop_map_bn["amount_paid"].raw_value == 550000
    assert prop_map_bn["goods_delivered"].raw_value is False

    # English defective
    english = "I ordered broken headphones from Evaly for 2500 BDT, they arrived defective and damaged."
    res_en = CaseExtractor.propose(english)
    assert res_en.detected_issue == "defective_goods"
    prop_map_en = {p.field_name: p for p in res_en.proposals}
    assert prop_map_en["goods_received_defective"].raw_value is True


def test_t08_extra_fields_and_foreign_span_ids_rejected():
    """T08: Extra model fields, foreign/unknown span IDs, invalid enums and malformed schema rejected."""
    valid_span = TextSpan(span_id="span_0", text="daraz", start_offset=0, end_offset=5)

    # 1. Foreign span ID rejection
    with pytest.raises(ValidationError, match="Foreign or unknown span ID"):
        FactProposalSet(
            detected_domain="consumer_ecommerce",
            detected_issue="ecommerce_delivery_failure",
            spans=[valid_span],
            proposals=[
                FactProposal(
                    field_name="merchant_name",
                    field_type="string",
                    raw_value="daraz",
                    original_text="daraz",
                    span_ids=["span_999"],  # Foreign span ID!
                )
            ],
        )

    # 2. Extra model fields rejected
    with pytest.raises(ValidationError):
        FactProposal(
            field_name="merchant_name",
            field_type="string",
            raw_value="daraz",
            original_text="daraz",
            span_ids=[],
            extra_injected_payload="forbidden",  # Extra field
        )

    # 3. Invalid field enum rejected
    with pytest.raises(ValidationError, match="not in allowed schema taxonomy"):
        FactProposal(
            field_name="unauthorized_custom_field",
            field_type="string",
            raw_value="val",
            original_text="val",
            span_ids=[],
        )

    # 4. Bounded repair cleans up malformed raw dictionary
    malformed_raw = {
        "detected_domain": "invalid_domain",
        "detected_issue": "invalid_issue",
        "proposals": [
            {
                "field_name": "amount_paid",
                "field_type": "money",
                "raw_value": 500000,
                "original_text": "5000",
                "span_ids": ["span_0", "span_foreign_fake"],
            },
            {
                "field_name": "injected_field",
                "field_type": "string",
                "raw_value": "drop_me",
            },
        ],
    }
    repaired = CaseExtractor.repair_and_validate(malformed_raw, allowed_spans=[valid_span])
    assert repaired.detected_domain == "consumer_ecommerce"  # fallback default
    assert repaired.detected_issue == "ecommerce_delivery_failure"  # fallback default
    assert len(repaired.proposals) == 1
    assert repaired.proposals[0].field_name == "amount_paid"
    assert repaired.proposals[0].span_ids == ["span_0"]  # foreign span dropped


@pytest.mark.asyncio
async def test_t08_extract_endpoint_and_auto_persist(client: AsyncClient, db_session):
    """P04.2 / T08: Integration test for extraction API endpoint and auto-persistence."""
    # 1. Bootstrap Guest User
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Case with Story Narrative
    narrative = "আমি দারাজ থেকে ৫,৫০০ টাকার ঘড়ি অর্ডার করেছিলাম কিন্তু পণ্য পাইনি।"
    case_res = await client.post(
        "/v1/cases",
        headers=headers,
        json={
            "title": "Daraz Delivery Failure",
            "jurisdiction": "BD",
            "desired_outcomes": ["full_refund"],
            "story_narrative": narrative,
        },
    )
    case_id = case_res.json()["id"]

    # 3. Call Extract Endpoint with auto_persist=True
    extract_res = await client.post(
        f"/v1/cases/{case_id}/extract?auto_persist=true",
        headers=headers,
    )
    assert extract_res.status_code == 200
    ext_data = extract_res.json()
    assert ext_data["detected_issue"] == "ecommerce_delivery_failure"
    assert len(ext_data["proposals"]) >= 2

    # 4. Verify Assertions were automatically persisted in DB
    facts_res = await client.get(f"/v1/cases/{case_id}/facts", headers=headers)
    assert facts_res.status_code == 200
    facts = facts_res.json()
    field_names = {f["field_name"] for f in facts}
    assert "amount_paid" in field_names
    assert "goods_delivered" in field_names

    # 5. Tenant Isolation: foreign user cannot extract
    client.cookies.clear()
    foreign_boot = await client.post("/auth/guest")
    foreign_headers = {"Authorization": f"Bearer {foreign_boot.json()['access_token']}"}

    foreign_extract = await client.post(
        f"/v1/cases/{case_id}/extract",
        headers=foreign_headers,
    )
    assert foreign_extract.status_code == 404
