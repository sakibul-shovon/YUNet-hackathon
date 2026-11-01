import datetime
import os
import uuid
import pytest
from httpx import AsyncClient
from unittest.mock import patch

from app.multimodal.audio.stt_adapter import STTAdapter
from app.multimodal.vision.screenshot_adapter import ScreenshotAdapter
from app.evidence.models import EvidenceItem
from app.cases.models import Case
from app.identity.models import Principal


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
SAMPLES_DIR = os.path.join(REPO_ROOT, "demo", "specs", "samples")


@pytest.mark.asyncio
async def test_committed_audio_samples_recall_and_timestamps():
    """P06.5 / T22: Reproducible keyword recall, timestamp attribution, and uncertainty flags on committed samples."""
    case_id = uuid.uuid4()
    ecommerce_sample_path = os.path.join(SAMPLES_DIR, "sample_voice_ecommerce.webm")
    assert os.path.exists(ecommerce_sample_path), f"Sample not found: {ecommerce_sample_path}"

    with open(ecommerce_sample_path, "rb") as f:
        audio_bytes = f.read()

    # 1. E-commerce sample
    res = await STTAdapter.transcribe_audio_bytes(
        case_id=case_id,
        audio_bytes=audio_bytes,
        declared_mime="audio/webm",
        consent_granted=True,
    )

    assert res.language in ("bn", "mixed")
    assert "দারাজ" in res.transcript_text
    assert "৫,৫০০" in res.transcript_text or "5500" in res.transcript_text
    assert res.consent_recorded is True
    assert len(res.words) > 0

    # Monotonic timestamps
    prev_end = 0.0
    for w in res.words:
        assert w.start_time >= prev_end - 0.01
        assert w.end_time >= w.start_time
        prev_end = w.end_time

    # Critical amount/date uncertainty flags (T22 invariant)
    reasons = [u.reason for u in res.uncertain_spans]
    assert "critical_amount_requires_review" in reasons
    assert any("5500" in u.span or "৫,৫০০" in u.span for u in res.uncertain_spans)

    # 2. Finance sample
    finance_sample_path = os.path.join(SAMPLES_DIR, "sample_voice_finance.webm")
    assert os.path.exists(finance_sample_path)
    with open(finance_sample_path, "rb") as f:
        finance_bytes = f.read()

    res_fin = await STTAdapter.transcribe_audio_bytes(
        case_id=case_id,
        audio_bytes=finance_bytes,
        declared_mime="audio/webm",
        consent_granted=True,
    )
    assert "বিকাশ" in res_fin.transcript_text
    assert any("2400" in u.span or "২,৪০০" in u.span for u in res_fin.uncertain_spans)


def test_committed_vision_samples_theme_and_layout():
    """P06.5 / T23: Vision layout analysis, dark/light theme detection, and authenticity guarantee prevention."""
    case_id = uuid.uuid4()
    evidence_id = uuid.uuid4()

    # 1. Light chat screenshot
    light_path = os.path.join(SAMPLES_DIR, "sample_chat_light.png")
    assert os.path.exists(light_path)
    with open(light_path, "rb") as f:
        light_bytes = f.read()

    res_light = ScreenshotAdapter.analyze_image_bytes(
        evidence_id=evidence_id,
        case_id=case_id,
        image_bytes=light_bytes,
        ocr_extracted_text="delivered 14:30 pm\nভাই আমার অর্ডার করা ঘড়িটা এখনো পাইনি\nআমরা চেক করে জানাচ্ছি স্যার",
    )
    assert res_light.theme == "light"
    assert res_light.authenticity_guarantee is False
    assert res_light.detected_layout == "chat_conversation"
    assert len(res_light.bubbles) >= 2
    # Check that speaker role confidence is preserved without false certainty
    for b in res_light.bubbles:
        assert b.speaker_role_confidence <= 0.90

    # 2. Dark chat screenshot
    dark_path = os.path.join(SAMPLES_DIR, "sample_chat_dark.png")
    assert os.path.exists(dark_path)
    with open(dark_path, "rb") as f:
        dark_bytes = f.read()

    res_dark = ScreenshotAdapter.analyze_image_bytes(
        evidence_id=evidence_id,
        case_id=case_id,
        image_bytes=dark_bytes,
        ocr_extracted_text="ডেলিভারি কবে হবে?",
    )
    assert res_dark.theme == "dark"
    assert res_dark.authenticity_guarantee is False


@pytest.mark.asyncio
async def test_provider_failure_resilience_fallback():
    """P06.5: Provider failure resilience: simulated API outage gracefully falls back to deterministic local STT."""
    case_id = uuid.uuid4()
    ecommerce_sample_path = os.path.join(SAMPLES_DIR, "sample_voice_ecommerce.webm")
    with open(ecommerce_sample_path, "rb") as f:
        audio_bytes = f.read()

    # Simulate external API 503 error
    with patch("httpx.AsyncClient.post", side_effect=Exception("503 Service Unavailable")):
        res = await STTAdapter.transcribe_audio_bytes(
            case_id=case_id,
            audio_bytes=audio_bytes,
            declared_mime="audio/webm",
            consent_granted=True,
        )
        # Verify fallback produced a working transcript without crashing
        assert res.transcript_text != ""
        assert res.consent_recorded is True
        assert len(res.words) > 0


@pytest.mark.asyncio
async def test_cascading_privacy_cleanup_t37(client: AsyncClient, db_session):
    """P06.5 / T36 / T37: Audio files and transcripts are safely purged on deletion request."""
    # 1. Create a guest session
    auth_resp = await client.post("/auth/guest")
    assert auth_resp.status_code == 200
    token = auth_resp.json()["access_token"]
    principal_id = auth_resp.json()["principal_id"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 2. Create case
    case_resp = await client.post(
        "/v1/cases",
        json={"title": "Voice Cleanup Case", "disputed_amount": 5500.0, "currency": "BDT"},
        headers=auth_headers,
    )
    assert case_resp.status_code == 201
    case_id = case_resp.json()["id"]

    # 3. Create audio evidence item
    evidence_id = uuid.uuid4()
    quarantine_file = f"quarantine_{evidence_id.hex}.webm"
    storage_dir = os.path.abspath("storage/evidence/quarantine")
    os.makedirs(storage_dir, exist_ok=True)
    full_path = os.path.join(storage_dir, quarantine_file)
    with open(full_path, "wb") as f:
        f.write(b"\x1a\x45\xdf\xa3dummy_audio_data")

    now = datetime.datetime.now(datetime.UTC)
    evidence = EvidenceItem(
        id=evidence_id,
        case_id=uuid.UUID(case_id),
        principal_id=uuid.UUID(principal_id),
        declared_mime_type="audio/webm",
        original_filename="voice_memo.webm",
        byte_size=24,
        quarantine_path=full_path,
        upload_token=uuid.uuid4().hex,
        intent_consumed=True,
        token_expires_at=now + datetime.timedelta(hours=2),
        status="quarantined",
    )
    db_session.add(evidence)
    await db_session.commit()

    assert os.path.exists(full_path)

    # 4. Request audio deletion via endpoint
    del_resp = await client.delete(
        f"/v1/cases/{case_id}/audio/{evidence_id}",
        headers=auth_headers,
    )
    assert del_resp.status_code == 200
    data = del_resp.json()
    assert data["status"] == "deleted"
    assert data["audio_id"] == str(evidence_id)

    # 5. Verify physical file is purged from disk (T36/T37)
    assert not os.path.exists(full_path)
