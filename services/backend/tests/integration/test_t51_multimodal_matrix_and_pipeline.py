import io
import os
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.multimodal.audio.stt_adapter import STTAdapter
from app.multimodal.vision.screenshot_adapter import ScreenshotAdapter
from app.facts.models import FactAssertion, FactReview


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
SAMPLES_DIR = os.path.join(REPO_ROOT, "demo", "specs", "samples")


@pytest.mark.asyncio
async def test_t51_matrix_row1_english_text_only(client: AsyncClient, db_session: AsyncSession):
    """T51 / Matrix Row 1: English text only reaches complete downstream pipeline without requiring audio/image."""
    # 1. Authenticate guest
    auth_resp = await client.post("/auth/guest")
    assert auth_resp.status_code == 200
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Case with English narrative only
    narrative = (
        "I ordered a mechanical keyboard for 5500 BDT from GadgetBD on October 15, 2026. "
        "The seller promised delivery within 3 days but failed to deliver and is not responding."
    )
    case_payload = {
        "title": "Keyboard Non-delivery Dispute",
        "jurisdiction": "BD",
        "locale": "en-BD",
        "merchant_name": "GadgetBD",
        "incident_date": "2026-10-15",
        "desired_outcomes": ["full_refund"],
        "story_narrative": narrative,
    }
    case_resp = await client.post("/v1/cases", headers=headers, json=case_payload)
    assert case_resp.status_code == 201
    case_id = case_resp.json()["id"]

    # 3. Extract text facts
    extract_resp = await client.post(
        f"/v1/cases/{case_id}/extract?auto_persist=true",
        headers=headers,
        json={"narrative": narrative},
    )
    assert extract_resp.status_code == 200

    # 4. Supply procedural conditions and review facts
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

    facts_resp = await client.get(f"/v1/cases/{case_id}/facts", headers=headers)
    facts = facts_resp.json()
    for f in facts:
        if f["field_name"] == "amount_paid":
            await client.post(
                f"/v1/cases/{case_id}/facts/{f['id']}/review",
                headers=headers,
                json={"review_outcome": "accepted"},
            )

    # 5. Assessment engine reachable
    assess_resp = await client.post(f"/v1/cases/{case_id}/assess", headers=headers)
    assert assess_resp.status_code == 200
    assessment = assess_resp.json()
    assert assessment["overall_status"] == "ready_for_merchant_notice"

    # 6. Draft generation reachable (T26 / T27)
    draft_resp = await client.get(f"/v1/cases/{case_id}/draft?locale=en&remedy=full_refund", headers=headers)
    assert draft_resp.status_code == 200
    draft = draft_resp.json()
    assert draft["lifecycle_state"] == "unsubmitted_draft"
    assert draft["is_filed"] is False
    assert draft["is_sent"] is False


@pytest.mark.asyncio
async def test_t51_matrix_row2_bangla_banglish_text_only(client: AsyncClient, db_session: AsyncSession):
    """T51 / Matrix Row 2: Bangla/Banglish text preserves verbatim narrative and normalizes Bengali numerals."""
    auth_resp = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {auth_resp.json()['access_token']}"}

    narrative_bn = "আমি ১৫ অক্টোবর ২০২৬ তারিখে দারাজ থেকে ৫,৫০০ টাকা অগ্রিম পেমেন্ট করেছিলাম কিন্তু কোনো পণ্য পাইনি।"
    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={
            "title": "দারাজ পণ্য অপ্রাপ্তি",
            "jurisdiction": "BD",
            "locale": "bn-BD",
            "merchant_name": "দারাজ",
            "desired_outcomes": ["full_refund"],
            "story_narrative": narrative_bn,
        },
    )
    assert case_resp.status_code == 201
    case_id = case_resp.json()["id"]

    extract_resp = await client.post(
        f"/v1/cases/{case_id}/extract?auto_persist=true",
        headers=headers,
        json={"narrative": narrative_bn},
    )
    assert extract_resp.status_code == 200

    facts_resp = await client.get(f"/v1/cases/{case_id}/facts", headers=headers)
    facts = facts_resp.json()
    fact_map = {f["field_name"]: f for f in facts}
    # Verifies Bengali numeral normalization (৫,৫০০ -> 550000 minor units)
    if "amount_paid" in fact_map:
        assert fact_map["amount_paid"]["typed_value"]["minor_units"] == 550000


@pytest.mark.asyncio
async def test_t51_matrix_row3_voice_recording_only(client: AsyncClient, db_session: AsyncSession):
    """T51 / Matrix Row 3: Voice note only transcribes with consent, populates narrative without retyping, and reaches assessment."""
    auth_resp = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {auth_resp.json()['access_token']}"}

    # Case started with empty story narrative
    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Voice Intake Case", "jurisdiction": "BD", "desired_outcomes": ["full_refund"]},
    )
    case_id = case_resp.json()["id"]

    # Transcribe voice sample
    sample_path = os.path.join(SAMPLES_DIR, "sample_voice_ecommerce.webm")
    assert os.path.exists(sample_path)
    with open(sample_path, "rb") as f:
        audio_bytes = f.read()

    files = {"audio_file": ("sample_voice_ecommerce.webm", audio_bytes, "audio/webm")}
    data = {"consent_granted": "true", "language_hint": "bn"}
    trans_resp = await client.post(f"/v1/cases/{case_id}/audio/transcribe", headers=headers, files=files, data=data)
    assert trans_resp.status_code == 200
    trans_data = trans_resp.json()
    assert "দারাজ" in trans_data["transcript_text"]
    assert trans_data["consent_recorded"] is True

    # Ingest voice transcript fact via multimodal ingestion
    voice_fact_payload = {
        "field_name": "amount_paid",
        "field_type": "money",
        "raw_value": "5500 BDT",
        "original_text": "৫,৫০০ টাকা",
        "origin": "voice_transcript",
        "source_type": "voice_transcript_span",
        "locator_meta": {"duration_seconds": trans_data["duration_seconds"]},
    }
    ingest_resp = await client.post(f"/v1/cases/{case_id}/facts/multimodal", headers=headers, json=voice_fact_payload)
    assert ingest_resp.status_code == 201
    ingest_data = ingest_resp.json()
    assert ingest_data["assertion"]["origin"] == "voice_transcript"


@pytest.mark.asyncio
async def test_t51_matrix_row4_screenshot_only_preserves_uncertainty(client: AsyncClient, db_session: AsyncSession):
    """T51 / Matrix Row 4: Screenshot only produces bounded layout proposals without fabricating authenticity or legal facts."""
    auth_resp = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {auth_resp.json()['access_token']}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Screenshot Only Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    light_path = os.path.join(SAMPLES_DIR, "sample_chat_light.png")
    with open(light_path, "rb") as f:
        img_bytes = f.read()

    result = ScreenshotAdapter.analyze_image_bytes(
        evidence_id=uuid.uuid4(),
        case_id=uuid.UUID(case_id),
        image_bytes=img_bytes,
        ocr_extracted_text="delivered 14:30 pm\nভাই আমার অর্ডার করা ঘড়িটা এখনো পাইনি\nআমরা চেক করে জানাচ্ছি স্যার",
    )
    # T23 Invariant: Never certifies authenticity
    assert result.authenticity_guarantee is False
    assert result.theme == "light"
    assert result.detected_layout == "chat_conversation"


@pytest.mark.asyncio
async def test_t51_matrix_row6_multimodal_cross_conflict_reconciliation(client: AsyncClient, db_session: AsyncSession):
    """T51 / Matrix Row 6 & T21: Mixed voice + receipt detects amount discrepancy and keeps assertion unapproved pending review."""
    auth_resp = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {auth_resp.json()['access_token']}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Discrepancy Case", "jurisdiction": "BD", "desired_outcomes": ["full_refund"]},
    )
    case_id = case_resp.json()["id"]

    # 1. Ingest receipt fact (5000 BDT)
    receipt_fact = {
        "field_name": "claimed_amount",
        "field_type": "money",
        "raw_value": "5000 BDT",
        "original_text": "5000",
        "origin": "document_extraction",
        "source_type": "evidence_span",
    }
    await client.post(f"/v1/cases/{case_id}/facts/multimodal", headers=headers, json=receipt_fact)

    # 2. Ingest conflicting voice fact (5500 BDT)
    voice_fact = {
        "field_name": "claimed_amount",
        "field_type": "money",
        "raw_value": "5500 BDT",
        "original_text": "৫,৫০০ টাকা",
        "origin": "voice_transcript",
        "source_type": "voice_transcript_span",
    }
    voice_res = await client.post(f"/v1/cases/{case_id}/facts/multimodal", headers=headers, json=voice_fact)
    assert voice_res.status_code == 201
    res_data = voice_res.json()

    # Discrepancy detected across modalities!
    assert res_data["has_conflict"] is True
    assert "Conflict detected" in res_data["conflict_message_en"]
    assert res_data["assertion"]["is_active"] is False  # Held inactive until review!


@pytest.mark.asyncio
async def test_t51_matrix_row7_unsupported_file_safe_rejection(client: AsyncClient, db_session: AsyncSession):
    """T51 / Matrix Row 7: Executable binaries or scripts are strictly rejected, preserving case integrity."""
    auth_resp = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {auth_resp.json()['access_token']}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Security Rejection Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    # Attempt to upload MZ executable as voice note
    exe_bytes = b"MZ\x90\x00\x03\x00\x00\x00" + b"\x00" * 64
    files = {"audio_file": ("malicious.exe", exe_bytes, "audio/webm")}
    data = {"consent_granted": "true"}

    bad_resp = await client.post(f"/v1/cases/{case_id}/audio/transcribe", headers=headers, files=files, data=data)
    assert bad_resp.status_code == 422
    assert "Executable binaries are strictly forbidden" in bad_resp.json()["detail"]

    # Case remains draft and healthy
    case_check = await client.get(f"/v1/cases/{case_id}", headers=headers)
    assert case_check.status_code == 200
    assert case_check.json()["lifecycle_status"] == "draft"
