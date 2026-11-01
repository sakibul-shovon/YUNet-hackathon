import os
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
SAMPLES_DIR = os.path.join(REPO_ROOT, "demo", "specs", "samples")


@pytest.mark.asyncio
async def test_p06_6_complete_multimodal_combination_to_downstream_pipeline(client: AsyncClient, db_session: AsyncSession):
    """P06.6: End-to-end multi-modality combination (Text + Voice + Screenshot)

    propagating downstream through Facts, Assessment, Action DAG, Document AST,
    Multi-format Export (P09), and Living Case Timeline updates (P10).
    """
    # 1. Authenticate guest principal
    auth_resp = await client.post("/auth/guest")
    assert auth_resp.status_code == 200
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Initialize Case with text narrative (Modality 1: Text)
    narrative_text = "I ordered an electronic device for 5,500 BDT from TechZone BD but received nothing."
    case_payload = {
        "title": "TechZone Undelivered Electronics",
        "jurisdiction": "BD",
        "merchant_name": "TechZone BD",
        "incident_date": "2026-10-18",
        "desired_outcomes": ["full_refund"],
        "story_narrative": narrative_text,
    }
    case_resp = await client.post("/v1/cases", headers=headers, json=case_payload)
    assert case_resp.status_code == 201
    case_id = case_resp.json()["id"]

    # 3. Transcribe Voice Note (Modality 2: Audio)
    voice_sample = os.path.join(SAMPLES_DIR, "sample_voice_ecommerce.webm")
    with open(voice_sample, "rb") as f:
        voice_bytes = f.read()

    files = {"audio_file": ("sample_voice_ecommerce.webm", voice_bytes, "audio/webm")}
    data = {"consent_granted": "true", "language_hint": "bn"}
    trans_resp = await client.post(f"/v1/cases/{case_id}/audio/transcribe", headers=headers, files=files, data=data)
    assert trans_resp.status_code == 200
    trans_data = trans_resp.json()
    assert trans_data["consent_recorded"] is True

    # Ingest multimodal voice fact assertion
    voice_fact = {
        "field_name": "amount_paid",
        "field_type": "money",
        "raw_value": "5500 BDT",
        "original_text": "৫,৫০০ টাকা",
        "origin": "voice_transcript",
        "source_type": "voice_transcript_span",
        "locator_meta": {"duration_seconds": trans_data["duration_seconds"]},
    }
    await client.post(f"/v1/cases/{case_id}/facts/multimodal", headers=headers, json=voice_fact)

    # 4. Upload & Attach Screenshot (Modality 3: Image / Vision)
    chat_sample = os.path.join(SAMPLES_DIR, "sample_chat_light.png")
    with open(chat_sample, "rb") as f:
        img_bytes = f.read()

    upload_init = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "sample_chat_light.png",
            "declared_mime_type": "image/png",
            "declared_byte_size": len(img_bytes),
        },
    )
    assert upload_init.status_code == 201
    intent = upload_init.json()
    intent_id = intent["intent_id"]
    upload_token = intent["upload_token"]

    put_resp = await client.put(
        f"/v1/uploads/{intent_id}/raw?token={upload_token}",
        content=img_bytes,
        headers={"Content-Type": "application/octet-stream"},
    )
    assert put_resp.status_code == 200

    complete_resp = await client.post(
        f"/v1/uploads/{intent_id}/complete",
        headers=headers,
    )
    assert complete_resp.status_code == 200

    # 5. Populate procedural facts
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "goods_delivered", "field_type": "boolean", "raw_value": False},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "promised_delivery_date_passed", "field_type": "boolean", "raw_value": True},
    )

    # 6. Verify Assessment & Action DAG (Phase P08 & P09.1)
    dag_res = await client.get(f"/v1/cases/{case_id}/actions/dag", headers=headers)
    assert dag_res.status_code == 200
    dag_data = dag_res.json()
    assert dag_data["primary_action_id"] == "prepare_dncrp_complaint"

    # 7. Generate Editable Document AST with sentence provenance (Phase P09.2)
    ast_res = await client.get(f"/v1/cases/{case_id}/documents/ast?locale=en", headers=headers)
    assert ast_res.status_code == 200
    ast_data = ast_res.json()
    assert ast_data["lifecycle_state"] == "unsubmitted_draft"
    assert ast_data["is_filed"] is False

    # 8. Multi-format Document Export (Phase P09.4 & T27)
    export_res = await client.post(f"/v1/cases/{case_id}/export/markdown?locale=en", headers=headers)
    assert export_res.status_code == 200
    export_data = export_res.json()
    assert export_data["is_filed"] is False  # Invariant T27: export never files case
    assert len(export_data["sha256_hash"]) == 64

    # 9. Living Case Timeline Update (Phase P10.1 & T38)
    curr_case = (await client.get(f"/v1/cases/{case_id}", headers=headers)).json()
    update_res = await client.post(
        f"/v1/cases/{case_id}/activity/updates",
        headers=headers,
        json={
            "update_type": "portal_submission",
            "authority_or_channel": "dncrp_ccms",
            "description": "Filed complaint directly on CCMS portal with receipt attached.",
            "reference_number": "CCMS-2026-99120",
            "expected_version": curr_case["row_version"],
        },
    )
    assert update_res.status_code == 201
    update_event = update_res.json()
    assert update_event["origin"] == "user_reported"
    assert update_event["reference_number"] == "CCMS-2026-99120"

    # 10. Verify Personal Reminder Flow (Phase P10.4 & T40)
    rem_res = await client.post(
        f"/v1/cases/{case_id}/reminders",
        headers=headers,
        json={
            "reminder_title": "Check CCMS hearing status",
            "remind_at": "2026-11-12T10:00:00Z",
            "category": "portal_check",
        },
    )
    assert rem_res.status_code == 201
    reminder = rem_res.json()
    assert reminder["is_legal_caution"] is False

    del_rem = await client.delete(f"/v1/cases/{case_id}/reminders/{reminder['id']}", headers=headers)
    assert del_rem.status_code == 204
