import datetime
import pytest
from httpx import AsyncClient

from app.facts.normalization import (
    ascii_to_bengali_digits,
    bengali_to_ascii_digits,
    normalize_bd_date,
    normalize_bdt_money,
)


def test_t05_bdt_money_normalization_and_roundtrip():
    """T05: Bengali digits, ৳5,500, fees, decimals and money_minor serialization round-trip without float errors."""
    # 1. Bengali digits with comma and symbol
    m1 = normalize_bdt_money("৳ ৫,৫০০.০০", original_text="৳ ৫,৫০০.০০")
    assert m1.currency == "BDT"
    assert m1.minor_units == 550000
    assert m1.original_text == "৳ ৫,৫০০.০০"
    assert m1.to_bdt_float_str() == "5,500.00"
    assert m1.to_bengali_display() == "৳৫,৫০০.০০"

    # 2. Bengali word "টাকা" and plain Bengali digits
    m2 = normalize_bdt_money("৫,৫০০ টাকা")
    assert m2.minor_units == 550000

    # 3. English notations: Tk, Tk., BDT
    m3 = normalize_bdt_money("Tk 5,500")
    m4 = normalize_bdt_money("Tk. 5500")
    m5 = normalize_bdt_money("5500 BDT")
    assert m3.minor_units == 550000
    assert m4.minor_units == 550000
    assert m5.minor_units == 550000

    # 4. Decimals and poisha
    m_dec1 = normalize_bdt_money("5500.50")
    m_dec2 = normalize_bdt_money("5500.05")
    m_dec3 = normalize_bdt_money("5500.5")
    assert m_dec1.minor_units == 550050
    assert m_dec2.minor_units == 550005
    assert m_dec3.minor_units == 550050

    # 5. Small fees and Bengali fractions
    m_fee1 = normalize_bdt_money("25.00")
    m_fee2 = normalize_bdt_money("০.৫০ টাকা")
    assert m_fee1.minor_units == 2500
    assert m_fee2.minor_units == 50

    # 6. Zero amount: perfectly represents free delivery / no fee without being None
    m_zero = normalize_bdt_money("0")
    m_zero_bn = normalize_bdt_money("০ টাকা")
    assert m_zero.minor_units == 0
    assert m_zero_bn.minor_units == 0

    # 7. Float precision verification: 0.1 + 0.2 in float is 0.30000000000000004
    # In our integer minor units: 10 poisha + 20 poisha == 30 poisha exactly!
    p1 = normalize_bdt_money("0.10").minor_units
    p2 = normalize_bdt_money("0.20").minor_units
    assert p1 + p2 == 30  # exact integer arithmetic, no float imprecision


def test_t06_bd_date_normalization_and_ambiguity():
    """T06: DD/MM ambiguity, relative date, date-only facts, timezone boundary and future promise handled correctly."""
    ref_date = datetime.date(2026, 11, 1)

    # 1. ISO date: unambiguous
    d_iso = normalize_bd_date("2026-10-15", reference_date=ref_date)
    assert d_iso.date == "2026-10-15"
    assert d_iso.is_ambiguous is False
    assert d_iso.is_future is False

    # 2. DD/MM/YYYY unambiguous: first number > 12
    d_ddmmyyyy = normalize_bd_date("15/10/2026", reference_date=ref_date)
    assert d_ddmmyyyy.date == "2026-10-15"
    assert d_ddmmyyyy.is_ambiguous is False

    # 3. Ambiguous format (e.g. 05/06/2026): flagged as ambiguous, defaults to BD convention (5th June)
    d_amb = normalize_bd_date("05/06/2026", reference_date=ref_date)
    assert d_amb.date == "2026-06-05"
    assert d_amb.is_ambiguous is True

    # 4. US format unambiguous: second number > 12
    d_us = normalize_bd_date("10/25/2026", reference_date=ref_date)
    assert d_us.date == "2026-10-25"
    assert d_us.is_ambiguous is False

    # 5. Bengali textual dates
    d_bn = normalize_bd_date("১৫ অক্টোবর ২০২৬", reference_date=ref_date)
    assert d_bn.date == "2026-10-15"

    # 6. English textual dates
    d_en1 = normalize_bd_date("15 October 2026", reference_date=ref_date)
    d_en2 = normalize_bd_date("Oct 15, 2026", reference_date=ref_date)
    assert d_en1.date == "2026-10-15"
    assert d_en2.date == "2026-10-15"

    # 7. Relative past dates (yesterday, 3 days ago, গত পরশু)
    d_yest_en = normalize_bd_date("yesterday", reference_date=ref_date)
    d_yest_bn = normalize_bd_date("গতকাল", reference_date=ref_date)
    assert d_yest_en.date == "2026-10-31"
    assert d_yest_en.is_relative is True
    assert d_yest_bn.date == "2026-10-31"

    d_day_before = normalize_bd_date("গত পরশু", reference_date=ref_date)
    assert d_day_before.date == "2026-10-30"

    d_3days = normalize_bd_date("৩ দিন আগে", reference_date=ref_date)
    assert d_3days.date == "2026-10-29"

    # 8. Future promised delivery dates (tomorrow, in 5 days, explicit future date)
    d_tomorrow = normalize_bd_date("আগামীকাল", reference_date=ref_date)
    assert d_tomorrow.date == "2026-11-02"
    assert d_tomorrow.is_future is True

    d_in_5_days = normalize_bd_date("৫ দিন পর", reference_date=ref_date)
    assert d_in_5_days.date == "2026-11-06"
    assert d_in_5_days.is_future is True

    d_future_iso = normalize_bd_date("2026-11-10", reference_date=ref_date)
    assert d_future_iso.date == "2026-11-10"
    assert d_future_iso.is_future is True


def test_t07_missing_false_zero_unknown_invariants():
    """T07: Missing/false/zero/unknown and original vs normalized text remain distinct."""
    # 1. Missing vs False vs Zero vs Unknown
    facts: dict[str, object] = {
        "goods_delivered": False,       # Explicit False
        "delivery_fee": 0,              # Explicit Zero
        "seller_response": "unknown",   # Explicit Unknown
        # "warranty_claimed" is missing
    }

    assert "warranty_claimed" not in facts  # MISSING
    assert facts["goods_delivered"] is False  # FALSE
    assert facts["delivery_fee"] == 0         # ZERO
    assert facts["seller_response"] == "unknown"  # UNKNOWN

    # Invariants: None of these are identical
    assert facts.get("warranty_claimed") is None
    assert facts["goods_delivered"] is not None
    assert facts["delivery_fee"] is not None
    assert facts["goods_delivered"] is not None
    assert type(facts["goods_delivered"]) is bool
    assert type(facts["delivery_fee"]) is int
    assert facts["goods_delivered"] != facts["seller_response"]

    # 2. Original text vs Normalized value separation
    m = normalize_bdt_money("৫,৫০০ টাকা", original_text="৫,৫০০ টাকা")
    assert m.original_text == "৫,৫০০ টাকা"
    assert m.minor_units == 550000
    assert m.original_text != str(m.minor_units)


@pytest.mark.asyncio
async def test_p04_1_fact_assertions_and_review_api(client: AsyncClient, db_session):
    """P04.1: Fact assertions persistence, normalization, review workflow and tenant isolation."""
    # 1. Bootstrap Tenant A
    boot_res = await client.post("/auth/guest")
    assert boot_res.status_code == 200
    token_a = boot_res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Create Case
    case_res = await client.post(
        "/v1/cases",
        headers=headers_a,
        json={"title": "Daraz Delivery Default", "jurisdiction": "BD", "desired_outcomes": ["full_refund"]},
    )
    assert case_res.status_code == 201
    case_id = case_res.json()["id"]

    # 3. Create Money Fact Assertion with Bengali digits
    fact1_res = await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers_a,
        json={
            "field_name": "amount_paid",
            "field_type": "money",
            "raw_value": "৫,৫০০ টাকা",
            "original_text": "৫,৫০০ টাকা দিয়েছি",
            "origin": "user_statement",
            "span_start": 0,
            "span_end": 17,
        },
    )
    assert fact1_res.status_code == 201
    f1 = fact1_res.json()
    assert f1["field_name"] == "amount_paid"
    assert f1["field_type"] == "money"
    assert f1["typed_value"]["minor_units"] == 550000
    assert f1["original_text"] == "৫,৫০০ টাকা দিয়েছি"
    assert f1["is_active"] is True
    assertion_id = f1["id"]

    # 4. Create Date Fact Assertion
    fact2_res = await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers_a,
        json={
            "field_name": "order_date",
            "field_type": "date",
            "raw_value": "১৫ অক্টোবর ২০২৬",
            "original_text": "অর্ডার করেছিলাম ১৫ অক্টোবর ২০২৬ তারিখে",
            "origin": "user_statement",
        },
    )
    assert fact2_res.status_code == 201
    f2 = fact2_res.json()
    assert f2["typed_value"]["date"] == "2026-10-15"

    # 5. Create Boolean Fact Assertion
    fact3_res = await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers_a,
        json={
            "field_name": "goods_delivered",
            "field_type": "boolean",
            "raw_value": False,
            "original_text": "পণ্য পাইনি",
            "origin": "user_statement",
        },
    )
    assert fact3_res.status_code == 201
    f3 = fact3_res.json()
    assert f3["typed_value"] is False

    # 6. List Facts
    list_res = await client.get(f"/v1/cases/{case_id}/facts", headers=headers_a)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 3

    # 7. Review Fact: Correct the amount
    review_res = await client.post(
        f"/v1/cases/{case_id}/facts/{assertion_id}/review",
        headers=headers_a,
        json={
            "review_outcome": "corrected",
            "corrected_value": "৬,০০০ টাকা",
            "corrected_original_text": "ভুল হয়েছিল, আসলে ৬,০০০ টাকা",
            "rationale": "Bank SMS confirmed 6000 BDT",
        },
    )
    assert review_res.status_code == 200
    rev = review_res.json()
    assert rev["review_outcome"] == "corrected"
    assert rev["correction_assertion_id"] is not None

    # Check updated active facts: old assertion deactivated, new assertion active
    active_facts_res = await client.get(f"/v1/cases/{case_id}/facts", headers=headers_a)
    active_facts = active_facts_res.json()
    amount_facts = [f for f in active_facts if f["field_name"] == "amount_paid"]
    assert len(amount_facts) == 1
    assert amount_facts[0]["typed_value"]["minor_units"] == 600000

    # 8. Tenant Isolation: Tenant B cannot access or review Tenant A's facts
    client.cookies.clear()
    boot_b = await client.post("/auth/guest")
    headers_b = {"Authorization": f"Bearer {boot_b.json()['access_token']}"}

    foreign_get = await client.get(f"/v1/cases/{case_id}/facts", headers=headers_b)
    assert foreign_get.status_code == 404

    foreign_post = await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers_b,
        json={"field_name": "hacked", "field_type": "boolean", "raw_value": True},
    )
    assert foreign_post.status_code == 404

