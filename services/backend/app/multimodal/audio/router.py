import datetime
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.evidence.models import EvidenceItem
from app.evidence.storage import get_storage_backend
from app.facts.service import FactService
from app.identity.models import Principal
from app.multimodal.audio.schemas import AudioTranscriptOut
from app.multimodal.audio.stt_adapter import STTAdapter

router = APIRouter(tags=["Multimodal Audio & Voice Notes"])


@router.post(
    "/v1/cases/{case_id}/audio/transcribe",
    response_model=AudioTranscriptOut,
    status_code=status.HTTP_200_OK,
)
async def transcribe_case_audio(
    case_id: uuid.UUID,
    audio_file: UploadFile = File(..., description="Recorded audio payload"),
    consent_granted: bool = Form(..., description="Explicit consumer consent for voice processing"),
    language_hint: str = Form("auto", description="Optional language hint: bn-BD, en-BD, auto"),
    client_duration: float = Form(0.0, description="Client measured duration in seconds"),
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T22: Ingests voice note, validates container & codec, enforces consent, and transcribes speech to text with uncertainty tags."""
    # 1. Enforce explicit consumer consent (T22 / NFR-12)
    if not consent_granted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Explicit consumer consent is mandatory before processing voice recordings.",
        )

    # 2. Authorize case ownership (T01)
    await FactService.get_authorized_case(case_id, principal, db)

    # 3. Read audio bytes
    audio_bytes = await audio_file.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded audio file is empty.",
        )

    # 4. Save audio recording in evidence vault storage
    now = datetime.datetime.now(datetime.UTC)
    storage = get_storage_backend()
    storage_key = f"audio_{uuid.uuid4().hex[:12]}_{Path(audio_file.filename or 'note.webm').name}"
    q_path = storage.save_quarantine(storage_key, audio_bytes)
    acc_path, sha_hash, actual_size = storage.promote_to_accepted(q_path, storage_key)

    ev_item = EvidenceItem(
        case_id=case_id,
        principal_id=principal.id,
        storage_kind="local_disk",
        quarantine_path=q_path,
        accepted_path=acc_path,
        original_filename=audio_file.filename or "voice_note.webm",
        declared_mime_type=audio_file.content_type or "audio/webm",
        detected_mime_type=audio_file.content_type or "audio/webm",
        byte_size=actual_size,
        quota_reserved_bytes=actual_size,
        sha256_hash=sha_hash,
        upload_token=uuid.uuid4().hex,
        token_expires_at=now + datetime.timedelta(hours=2),
        intent_consumed=True,
        status="accepted",
        is_quarantined=False,
    )
    db.add(ev_item)
    await db.commit()
    await db.refresh(ev_item)

    # 4. Transcribe audio
    return await STTAdapter.transcribe_audio_bytes(
        case_id=case_id,
        audio_bytes=audio_bytes,
        declared_mime=audio_file.content_type or "audio/webm",
        consent_granted=consent_granted,
        language_hint=language_hint,
        audio_evidence_id=ev_item.id,
        duration_seconds=client_duration,
    )


@router.get(
    "/v1/cases/{case_id}/audio/{audio_id}/stream",
    status_code=status.HTTP_200_OK,
)
async def stream_audio_recording(
    case_id: uuid.UUID,
    audio_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T15, T22: Private playback stream for case owner with strict cache exclusion."""
    await FactService.get_authorized_case(case_id, principal, db)

    stmt = select(EvidenceItem).where(
        EvidenceItem.id == audio_id,
        EvidenceItem.case_id == case_id,
        EvidenceItem.status == "accepted",
    )
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item or not item.accepted_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio evidence recording not found.",
        )

    storage = get_storage_backend()
    data = storage.read_accepted(item.accepted_path)

    headers = {
        "Cache-Control": "private, no-store, max-age=0, must-revalidate",
        "Pragma": "no-cache",
        "X-Content-Type-Options": "nosniff",
        "Content-Disposition": f'inline; filename="{item.original_filename}"',
    }
    return Response(
        content=data,
        media_type=item.detected_mime_type or item.declared_mime_type,
        headers=headers,
    )


@router.delete(
    "/v1/cases/{case_id}/audio/{audio_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_audio_recording(
    case_id: uuid.UUID,
    audio_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T22, T36: Purges private audio recording from storage and marks item deleted."""
    await FactService.get_authorized_case(case_id, principal, db)

    stmt = select(EvidenceItem).where(
        EvidenceItem.id == audio_id,
        EvidenceItem.case_id == case_id,
    )
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item or item.status == "deleted":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio evidence not found.",
        )

    storage = get_storage_backend()
    if item.quarantine_path:
        storage.delete_quarantine(item.quarantine_path)
    if item.accepted_path:
        storage.delete_accepted(item.accepted_path)

    item.status = "deleted"
    item.accepted_path = None
    item.quota_reserved_bytes = 0
    await db.commit()

    return {"status": "deleted", "audio_id": str(audio_id)}
