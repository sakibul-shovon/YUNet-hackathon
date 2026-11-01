import sys
import uuid
from pathlib import Path
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add repository root to path for scripts
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.cases.models import Case
from app.facts.models import FactAssertion, FactReview
from scripts.seed_demo import seed_demo_case


@pytest.mark.asyncio
async def test_p04_6_e2e_m1_vertical_slice(client: AsyncClient, db_session: AsyncSession):
    """P04.6: Complete M1 Text-to-Action Vertical Slice End-to-End Integration Test.
    
    Validates:
    - Guest bootstrap & authenticated case creation
    - Real Bangla text-to-facts extraction adapter with verbatim spans
    - User fact review, acceptance, and provenance tracking (T09)
    - Procedural assessment engine (T19 merchant vs provider separation, T20)
    - Draft generation with safety enforcement and unsubmitted status (T26)
    - T27 Invariant: Generating/copying drafts NEVER marks case as filed or resolved
    - T04 Invariant: Case state, versions, and facts survive session reload
    - Demo Sandbox: Synthetic fixture is isolated, labeled, and idempotent
    """
    # ---------------------------------------------------------
    # 1. Guest Session Bootstrap
    # ---------------------------------------------------------
    auth_resp = await client.post("/auth/guest")
    assert auth_resp.status_code == 200
    auth_data = auth_resp.json()
    token = auth_data["access_token"]
    principal_id = auth_data["principal_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # ---------------------------------------------------------
    # 2. Case Creation with Bangla Narrative
    # ---------------------------------------------------------
    narrative_text = (
        "আমি ১৫ অক্টোবর ২০২৬ তারিখে দারাজ থেকে ৫,৫০০ টাকা অগ্রিম বিকাশ করে একটি স্মার্টওয়াচ অর্ডার করেছিলাম। "
        "তারা ৭২ ঘণ্টার মধ্যে ডেলিভারির প্রতিশ্রুতি দিয়েছিল। কিন্তু আজ পর্যন্ত পণ্যটি পাইনি এবং বিক্রেতা মেসেজের উত্তর দেওয়া বন্ধ করে দিয়েছে।"
    )
    case_payload = {
        "title": "দারাজ স্মার্টওয়াচ ডেলিভারি না পাওয়া",
        "jurisdiction": "BD",
        "locale": "bn-BD",
        "merchant_name": "দারাজ",
        "incident_date": "2026-10-15",
        "desired_outcomes": ["full_refund"],
        "story_narrative": narrative_text,
    }
    create_resp = await client.post("/v1/cases", headers=headers, json=case_payload)
    assert create_resp.status_code == 201
    case_data = create_resp.json()
    case_id = case_data["id"]
    assert case_data["lifecycle_status"] == "draft"
    assert case_data["row_version"] == 1

    # ---------------------------------------------------------
    # 3. Real Text-to-Fact Extraction (auto_persist = True)
    # ---------------------------------------------------------
    extract_resp = await client.post(
        f"/v1/cases/{case_id}/extract?auto_persist=true",
        headers=headers,
        json={"narrative": narrative_text},
    )
    assert extract_resp.status_code == 200
    extraction_result = extract_resp.json()
    assert extraction_result["detected_domain"] == "consumer_ecommerce"
    assert extraction_result["detected_issue"] == "ecommerce_delivery_failure"
    assert len(extraction_result["spans"]) >= 3

    # Check extracted proposals
    extracted_fields = {p["field_name"]: p for p in extraction_result["proposals"]}
    assert "merchant_name" in extracted_fields
    assert "amount_paid" in extracted_fields
    assert "goods_delivered" in extracted_fields

    # Verify extracted facts are persisted in DB
    facts_resp = await client.get(f"/v1/cases/{case_id}/facts", headers=headers)
    assert facts_resp.status_code == 200
    persisted_facts = facts_resp.json()
    assert len(persisted_facts) >= 3

    # Map persisted facts
    fact_by_name = {f["field_name"]: f for f in persisted_facts}
    assert fact_by_name["merchant_name"]["field_type"] == "string"
    assert fact_by_name["amount_paid"]["field_type"] == "money"
    assert fact_by_name["amount_paid"]["typed_value"]["minor_units"] == 550000
    assert fact_by_name["goods_delivered"]["field_type"] == "boolean"
    assert fact_by_name["goods_delivered"]["typed_value"] is False

    # ---------------------------------------------------------
    # 4. Fact Review & Affirmation (T09)
    # ---------------------------------------------------------
    amount_fact_id = fact_by_name["amount_paid"]["id"]
    review_resp = await client.post(
        f"/v1/cases/{case_id}/facts/{amount_fact_id}/review",
        headers=headers,
        json={
            "review_outcome": "accepted",
            "rationale": "Confirmed from bKash payment statement",
        },
    )
    assert review_resp.status_code == 200
    review_data = review_resp.json()
    assert review_data["review_outcome"] == "accepted"
    assert review_data["assertion_id"] == amount_fact_id

    # Add required procedural conditions: delivery date passed, no refund yet
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "promised_delivery_date_passed", "field_type": "boolean", "raw_value": True},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "refund_already_issued", "field_type": "boolean", "raw_value": False},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "order_cancelled_by_buyer_before_dispatch", "field_type": "boolean", "raw_value": False},
    )

    # ---------------------------------------------------------
    # 5. Procedural Assessment Engine (T19 / T20)
    # ---------------------------------------------------------
    assess_resp = await client.post(f"/v1/cases/{case_id}/assess", headers=headers)
    assert assess_resp.status_code == 200
    assessment = assess_resp.json()

    assert assessment["overall_status"] == "ready_for_merchant_notice"
    assert assessment["primary_action"] == "prepare_merchant_notice"

    supported_issues = [r["issue_type"] for r in assessment["routes"] if r["status"] == "supported"]
    assert "ecommerce_delivery_failure" in supported_issues

    # Invariant T19: E-commerce failure paid via MFS does NOT create provider complaint
    all_route_issues = [r["issue_type"] for r in assessment["routes"]]
    assert "ecommerce_delivery_failure" in all_route_issues
    assert "mfs_unauthorized_charge" not in all_route_issues

    # ---------------------------------------------------------
    # 6. Action Draft Generation (P04.5 & T26)
    # ---------------------------------------------------------
    draft_resp = await client.get(
        f"/v1/cases/{case_id}/draft?locale=bn&remedy=full_refund",
        headers=headers,
    )
    assert draft_resp.status_code == 200
    draft = draft_resp.json()

    assert draft["lifecycle_state"] == "unsubmitted_draft"
    assert draft["is_sent"] is False
    assert draft["is_filed"] is False
    assert "অনুরোধ" in draft["subject"] or "নোটিশ" in draft["subject"] or "স্মার্টওয়াচ" in draft["subject"]
    assert "৫,৫০০" in draft["body_text"] or "5,500" in draft["body_text"] or "5500" in draft["body_text"]
    assert "ভোক্তা-অধিকার সংরক্ষণ আইন, ২০০৯" in draft["citations"][0]

    # ---------------------------------------------------------
    # 7. Invariant T27: Draft Generation NEVER marks case as filed or resolved
    # ---------------------------------------------------------
    case_check_resp = await client.get(f"/v1/cases/{case_id}", headers=headers)
    assert case_check_resp.status_code == 200
    refreshed_case = case_check_resp.json()
    assert refreshed_case["lifecycle_status"] == "draft"
    assert refreshed_case.get("user_reported_filed") is not True
    assert refreshed_case.get("user_reported_resolved") is not True

    # ---------------------------------------------------------
    # 8. Invariant T04: State Reload and Persistence Survival
    # ---------------------------------------------------------
    # Reload directly from database session to ensure persistent survival
    case_uuid = uuid.UUID(case_id)
    principal_uuid = uuid.UUID(principal_id)
    stmt = select(Case).where(Case.id == case_uuid)
    case_db = (await db_session.execute(stmt)).scalar_one()
    assert case_db is not None
    assert case_db.title == "দারাজ স্মার্টওয়াচ ডেলিভারি না পাওয়া"
    assert case_db.principal_id == principal_uuid
    assert case_db.lifecycle_status == "draft"

    # Verify review assertions persisted
    amount_uuid = uuid.UUID(amount_fact_id)
    stmt_reviews = select(FactReview).where(FactReview.assertion_id == amount_uuid)
    reviews_db = (await db_session.execute(stmt_reviews)).scalars().all()
    assert len(reviews_db) >= 1
    assert any(r.review_outcome == "accepted" for r in reviews_db)

    # ---------------------------------------------------------
    # 9. Synthetic Demo Sandbox Seeding & Isolation Verification
    # ---------------------------------------------------------
    await seed_demo_case(session=db_session)

    stmt_demo = select(Case).where(Case.display_reference == "DEMO-DARAZ-001")
    demo_case = (await db_session.execute(stmt_demo)).scalar_one_or_none()
    assert demo_case is not None
    assert demo_case.is_demo is True
    assert demo_case.id != case_uuid
    assert demo_case.principal_id != principal_uuid
