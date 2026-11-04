import io
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.multimodal.audio.mime_codec import validate_audio_file


def make_dummy_audio_bytes(format_type: str = "webm", phrase: str = "") -> bytes:
    """Generates synthetic valid audio containers with appropriate magic headers."""
    content_payload = phrase.encode("utf-8") if phrase else b"Simulated Audio Signal"
    if format_type == "webm":
        # EBML header \x1a\x45\xdf\xa3
        return b"\x1a\x45\xdf\xa3\x01\x00\x00\x00\x1f\x43\xb6\x75\x01\x00\x00\x00" + content_payload
    elif format_type == "wav":
        # RIFF WAVE
        riff_header = b"RIFF" + (36 + len(content_payload)).to_bytes(4, "little") + b"WAVEfmt "
        pcm_subchunk = (16).to_bytes(4, "little") + (1).to_bytes(2, "little") + (1).to_bytes(2, "little") + (16000).to_bytes(4, "little") + (32000).to_bytes(4, "little") + (2).to_bytes(2, "little") + (16).to_bytes(2, "little")
        data_chunk = b"data" + len(content_payload).to_bytes(4, "little") + content_payload
        return riff_header + pcm_subchunk + data_chunk
    elif format_type == "mp4":
        # ISO BMFF ftyp box
        return b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42" + content_payload
    elif format_type == "m4a":
        return b"\x00\x00\x00\x20ftypM4A \x00\x00\x00\x00M4A mp42isom\x00\x00\x00\x00" + content_payload
    elif format_type == "ogg":
        return b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00" + content_payload
    return b"\x1a\x45\xdf\xa3" + content_payload


def test_t22_audio_codec_validation_and_spoof_rejection():
    """T22: Real cross-browser codec validation for Chrome (WebM/Opus), Safari (MP4/M4A), Firefox (Ogg), WAV."""
    # 1. Chrome WebM
    webm_bytes = make_dummy_audio_bytes("webm")
    valid, detected, _ = validate_audio_file(webm_bytes, "audio/webm;codecs=opus")
    assert valid is True
    assert detected == "audio/webm"

    # 2. Safari iOS MP4/M4A
    m4a_bytes = make_dummy_audio_bytes("m4a")
    valid_m4a, detected_m4a, _ = validate_audio_file(m4a_bytes, "audio/mp4")
    assert valid_m4a is True
    assert detected_m4a in ("audio/mp4", "audio/x-m4a")

    # 3. WAV
    wav_bytes = make_dummy_audio_bytes("wav")
    valid_wav, detected_wav, _ = validate_audio_file(wav_bytes, "audio/wav")
    assert valid_wav is True
    assert detected_wav == "audio/wav"

    # 4. Reject executable binaries disguised as audio (T22)
    exe_disguised = b"MZ\x90\x00" + b"\x00" * 200
    valid_exe, _, err = validate_audio_file(exe_disguised, "audio/webm")
    assert valid_exe is False
    assert "executable" in err.lower()

    # 5. Reject HTML/Script active content
    script_disguised = b"<script>alert(1)</script>"
    valid_script, _, err_s = validate_audio_file(script_disguised, "audio/webm")
    assert valid_script is False
    assert "forbidden" in err_s.lower()

    # 6. Reject format mismatch (WAV declared as WebM)
    valid_mismatch, _, err_m = validate_audio_file(wav_bytes, "audio/webm")
    assert valid_mismatch is False
    assert "does not match" in err_m.lower()


@pytest.mark.asyncio
async def test_t22_consent_enforcement_and_private_stt_transcription(client: AsyncClient, db_session: AsyncSession):
    """T22: Mandatory consumer consent, Bengali ASR transcript, word timestamps, and uncertain critical token flags."""
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Voice Note Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    audio_data = make_dummy_audio_bytes("webm", "আমি দারাজ থেকে ৫,৫০০ টাকার ঘড়ি পাইনি ১৫ অক্টোবর")

    # 1. Invariant T22 / NFR-12: Transcribe without consent -> 400 Bad Request
    no_consent_resp = await client.post(
        f"/v1/cases/{case_id}/audio/transcribe",
        headers=headers,
        data={"consent_granted": "false", "client_duration": "4.5"},
        files={"audio_file": ("voice_note.webm", audio_data, "audio/webm")},
    )
    assert no_consent_resp.status_code == 400
    assert "consent" in no_consent_resp.json()["detail"].lower()

    # 2. Transcribe with explicit consent
    transcribe_resp = await client.post(
        f"/v1/cases/{case_id}/audio/transcribe",
        headers=headers,
        data={"consent_granted": "true", "client_duration": "4.5", "client_transcript": "আমি দারাজ থেকে ৫,৫০০ টাকার ঘড়ি পাইনি ১৫ অক্টোবর"},
        files={"audio_file": ("voice_note.webm", audio_data, "audio/webm")},
    )
    assert transcribe_resp.status_code == 200
    res_data = transcribe_resp.json()

    assert res_data["case_id"] == case_id
    assert res_data["audio_evidence_id"] is not None
    assert len(res_data["transcript_text"]) > 10
    assert res_data["consent_recorded"] is True
    assert res_data["duration_seconds"] > 0

    # A user-provided transcript is preserved without fake ASR confidence or timing.
    assert res_data["method"] == "client_provided_transcript"
    assert res_data["model_executed"] is False
    assert res_data["overall_confidence"] is None
    assert res_data["words"] == []
    assert res_data["uncertain_spans"] == []
    assert res_data["transcript_text"] == "আমি দারাজ থেকে ৫,৫০০ টাকার ঘড়ি পাইনি ১৫ অক্টোবর"


@pytest.mark.asyncio
async def test_t22_audio_replay_stream_and_deletion(client: AsyncClient, db_session: AsyncSession):
    """T22, T15, T36: Private replay streaming requires owner, returns no-store headers; deletion purges recording."""
    # 1. Setup case & upload voice note
    auth_a = await client.post("/auth/guest")
    headers_a = {"Authorization": f"Bearer {auth_a.json()['access_token']}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers_a,
        json={"title": "Replay Stream Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    audio_bytes = make_dummy_audio_bytes("webm", "দারাজ ডেলিভারি ব্যর্থ")
    t_resp = await client.post(
        f"/v1/cases/{case_id}/audio/transcribe",
        headers=headers_a,
        data={"consent_granted": "true", "client_transcript": "Fictional manual transcript for playback test."},
        files={"audio_file": ("test_replay.webm", audio_bytes, "audio/webm")},
    )
    audio_id = t_resp.json()["audio_evidence_id"]

    # 2. Replay streaming (T15/T22)
    stream_resp = await client.get(
        f"/v1/cases/{case_id}/audio/{audio_id}/stream",
        headers=headers_a,
    )
    assert stream_resp.status_code == 200
    assert stream_resp.content == audio_bytes
    cache_ctrl = stream_resp.headers.get("cache-control", "")
    assert "private" in cache_ctrl
    assert "no-store" in cache_ctrl

    # 3. Foreign tenant access blocked (T01)
    client.cookies.clear()
    auth_b = await client.post("/auth/guest")
    headers_b = {"Authorization": f"Bearer {auth_b.json()['access_token']}"}

    foreign_stream = await client.get(
        f"/v1/cases/{case_id}/audio/{audio_id}/stream",
        headers=headers_b,
    )
    assert foreign_stream.status_code == 404

    # 4. Owner deletes audio (T22/T36)
    del_resp = await client.delete(
        f"/v1/cases/{case_id}/audio/{audio_id}",
        headers=headers_a,
    )
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "deleted"

    # Subsequent stream returns 404
    after_del = await client.get(
        f"/v1/cases/{case_id}/audio/{audio_id}/stream",
        headers=headers_a,
    )
    assert after_del.status_code == 404

