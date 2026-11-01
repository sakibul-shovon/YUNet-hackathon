import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_p06_4_multimodal_facts_same_atomic_store_and_provenance(client: AsyncClient, db_session: AsyncSession):
    """P06.4: Same atomic provenance model for voice, text, and visual facts; zero parallel 'AI case' store."""
    auth_resp = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {auth_resp.json()['access_token']}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Multimodal Provenance Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    # 1. Ingest Voice Fact
    voice_resp = await client.post(
        f"/v1/cases/{case_id}/facts/multimodal",
        headers=headers,
        json={
            "field_name": "delivery_promised_date",
            "field_type": "date",
            "raw_value": "১৮ অক্টোবর ২০২৬",
            "original_text": "১৮ অক্টোবর ডেলিভারি করার কথা ছিল",
            "origin": "voice_transcript",
            "source_type": "voice_transcript_span",
            "locator_meta": {"audio_id": str(uuid.uuid4()), "start_time": 1.2, "end_time": 3.4},
        },
    )
    assert voice_resp.status_code == 201
    voice_data = voice_resp.json()
    assert voice_data["has_conflict"] is False
    assert voice_data["assertion"]["origin"] == "voice_transcript"

    # 2. Ingest Document/Receipt Visual Fact
    doc_resp = await client.post(
        f"/v1/cases/{case_id}/facts/multimodal",
        headers=headers,
        json={
            "field_name": "transaction_amount",
            "field_type": "money",
            "raw_value": "5500 BDT",
            "original_text": "5500 BDT",
            "origin": "document_extraction",
            "source_type": "evidence_span",
            "locator_meta": {"evidence_id": str(uuid.uuid4()), "normalized_box": [0.1, 0.2, 0.4, 0.3]},
        },
    )
    assert doc_resp.status_code == 201
    doc_data = doc_resp.json()
    assert doc_data["assertion"]["origin"] == "document_extraction"

    # 3. Ingest Chat Screenshot Fact
    chat_resp = await client.post(
        f"/v1/cases/{case_id}/facts/multimodal",
        headers=headers,
        json={
            "field_name": "seller_acknowledged_delay",
            "field_type": "boolean",
            "raw_value": True,
            "original_text": "আমরা চেক করে জানাচ্ছি স্যার",
            "origin": "chat_screenshot",
            "source_type": "evidence_span",
            "locator_meta": {"evidence_id": str(uuid.uuid4()), "bubble_id": "bubble_2"},
        },
    )
    assert chat_resp.status_code == 201
    chat_data = chat_resp.json()
    assert chat_data["assertion"]["origin"] == "chat_screenshot"

    # 4. Verify all facts reside directly in standard case facts query (no parallel store)
    all_facts_resp = await client.get(f"/v1/cases/{case_id}/facts", headers=headers)
    assert all_facts_resp.status_code == 200
    facts = all_facts_resp.json()
    assert len(facts) >= 3
    origins = {f["origin"] for f in facts}
    assert "voice_transcript" in origins
    assert "document_extraction" in origins
    assert "chat_screenshot" in origins


@pytest.mark.asyncio
async def test_p06_4_cross_modality_conflict_detection_and_review_routing(client: AsyncClient, db_session: AsyncSession):
    """P06.4: Conflict resolution across modalities; conflicting values flagged for consumer review."""
    auth_resp = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {auth_resp.json()['access_token']}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Cross-Modality Conflict Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    # 1. Voice note asserts ৳5,500
    prop_voice = await client.post(
        f"/v1/cases/{case_id}/facts/multimodal",
        headers=headers,
        json={
            "field_name": "claimed_amount",
            "field_type": "money",
            "raw_value": "৳৫,৫০০",
            "original_text": "৫,৫০০ টাকা অগ্রিম দিয়েছি",
            "origin": "voice_transcript",
            "source_type": "voice_transcript_span",
        },
    )
    assert prop_voice.status_code == 201
    pv_data = prop_voice.json()
    assert pv_data["has_conflict"] is False
    assert pv_data["assertion"]["is_active"] is True

    # 2. Receipt screenshot asserts conflicting ৳5,000
    prop_receipt = await client.post(
        f"/v1/cases/{case_id}/facts/multimodal",
        headers=headers,
        json={
            "field_name": "claimed_amount",
            "field_type": "money",
            "raw_value": "5000 BDT",
            "original_text": "Total 5000 BDT",
            "origin": "document_extraction",
            "source_type": "evidence_span",
        },
    )
    assert prop_receipt.status_code == 201
    pr_data = prop_receipt.json()

    # Invariant P06.4: Conflict detected across modalities
    assert pr_data["has_conflict"] is True
    assert pr_data["conflicting_assertion_id"] == pv_data["assertion"]["id"]
    assert pr_data["assertion"]["is_active"] is False  # Candidate kept inactive pending review
    assert "Conflict detected" in pr_data["conflict_message_en"]
    assert "অমিল পাওয়া গেছে" in pr_data["conflict_message_bn"]

