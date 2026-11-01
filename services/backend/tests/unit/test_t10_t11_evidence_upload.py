import datetime
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.evidence.models import EvidenceItem
from app.evidence.service import EvidenceService


@pytest.mark.asyncio
async def test_t10_mime_spoofing_and_binary_validation(client: AsyncClient, db_session: AsyncSession):
    """T10: Declared MIME/size bypass, arbitrary path, and object overwrite rejected."""
    # 1. Bootstrap Guest
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Case
    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Test Case for Evidence Vault", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    # 3. Test Path Traversal in declared filename
    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "../../../etc/shadow",
            "declared_mime_type": "image/png",
            "declared_byte_size": 1024,
        },
    )
    assert init_resp.status_code == 201
    intent = init_resp.json()
    intent_id = intent["intent_id"]
    upload_token = intent["upload_token"]

    # Check that original_filename stored in DB is sanitized (no traversal)
    stmt = select(EvidenceItem).where(EvidenceItem.id == uuid.UUID(intent_id))
    item = (await db_session.execute(stmt)).scalar_one()
    assert item.original_filename == "shadow"
    assert ".." not in item.quarantine_path

    # 4. Upload Spoofed Binary (Executable payload masquerading as PNG)
    fake_png_executable = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00This is malware"
    put_resp = await client.put(
        f"/v1/uploads/{intent_id}/raw?token={upload_token}",
        content=fake_png_executable,
        headers={"Content-Type": "application/octet-stream"},
    )
    assert put_resp.status_code == 200

    # 5. Complete Upload -> Server validates actual bytes and rejects executable (T10)
    complete_resp = await client.post(
        f"/v1/uploads/{intent_id}/complete",
        headers=headers,
    )
    assert complete_resp.status_code == 422
    err_detail = complete_resp.json()["detail"]
    assert "Executable binaries are strictly forbidden" in err_detail or "MIME spoof detected" in err_detail

    # Check item status is rejected and quarantine is cleaned up
    await db_session.refresh(item)
    assert item.status == "rejected"
    assert item.quota_reserved_bytes == 0


@pytest.mark.asyncio
async def test_t10_reused_intent_and_successful_accepted_flow(client: AsyncClient, db_session: AsyncSession):
    """T10: Legitimate upload moves to accepted storage; reused upload-completion intent rejected."""
    # 1. Bootstrap & Create Case
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Receipt Upload Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    # 2. Init upload for genuine PDF
    import io
    import pypdf
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buf = io.BytesIO()
    writer.write(buf)
    pdf_bytes = buf.getvalue()

    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "daraz_invoice.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(pdf_bytes),
        },
    )
    assert init_resp.status_code == 201
    intent_data = init_resp.json()
    intent_id = intent_data["intent_id"]
    upload_token = intent_data["upload_token"]

    # 3. Direct upload to quarantine
    put_resp = await client.put(
        f"/v1/uploads/{intent_id}/raw?token={upload_token}",
        content=pdf_bytes,
    )
    assert put_resp.status_code == 200

    # 4. Complete upload
    complete_resp = await client.post(
        f"/v1/uploads/{intent_id}/complete",
        headers=headers,
    )
    assert complete_resp.status_code == 200
    accepted_evidence = complete_resp.json()
    assert accepted_evidence["status"] == "accepted"
    assert accepted_evidence["is_quarantined"] is False
    assert accepted_evidence["declared_mime_type"] == "application/pdf"
    assert accepted_evidence["detected_mime_type"] == "application/pdf"
    assert accepted_evidence["sha256_hash"] is not None
    assert len(accepted_evidence["sha256_hash"]) == 64

    # 5. Invariant T10: Calling complete AGAIN with the same intent -> 409 Conflict
    reused_resp = await client.post(
        f"/v1/uploads/{intent_id}/complete",
        headers=headers,
    )
    assert reused_resp.status_code == 409
    assert "already been consumed" in reused_resp.json()["detail"]

    # 6. Invariant T10: Attempting to overwrite quarantine after consumption -> 409 Conflict
    overwrite_resp = await client.put(
        f"/v1/uploads/{intent_id}/raw?token={upload_token}",
        content=b"%PDF-1.4 Overwrite attempt",
    )
    assert overwrite_resp.status_code == 409


@pytest.mark.asyncio
async def test_t11_upload_token_lifespan_and_sweeper(client: AsyncClient, db_session: AsyncSession):
    """T11: Expired token rejected; quota reservations swept correctly."""
    # 1. Bootstrap & Create Case
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Quota & Expiry Test Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    # 2. Init upload intent
    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "receipt.png",
            "declared_mime_type": "image/png",
            "declared_byte_size": 5000,
        },
    )
    assert init_resp.status_code == 201
    intent = init_resp.json()
    intent_id = intent["intent_id"]
    upload_token = intent["upload_token"]

    # 3. Simulate token expiration by setting token_expires_at in the past
    stmt = select(EvidenceItem).where(EvidenceItem.id == uuid.UUID(intent_id))
    item = (await db_session.execute(stmt)).scalar_one()
    item.token_expires_at = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=10)
    await db_session.commit()

    # 4. Invariant T11: Late write with expired token rejected with 410 Gone
    valid_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    late_put = await client.put(
        f"/v1/uploads/{intent_id}/raw?token={upload_token}",
        content=valid_png,
    )
    assert late_put.status_code == 410
    assert "token has expired" in late_put.json()["detail"].lower()

    # 5. Test sweeper
    sweep_resp = await client.post("/v1/uploads/sweep")
    assert sweep_resp.status_code == 200

    await db_session.refresh(item)
    assert item.status == "quarantine_expired"
    assert item.quota_reserved_bytes == 0


@pytest.mark.asyncio
async def test_t11_case_quota_reservation_limits(client: AsyncClient, db_session: AsyncSession):
    """T11: Enforces item count (20) and aggregate case byte size (100 MB) quota reservations."""
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Quota Limits Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    # 1. Reject single item > 20 MB limit
    over_size_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "huge_file.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": 25 * 1024 * 1024,  # 25 MB
        },
    )
    assert over_size_resp.status_code == 422
    assert "less than or equal" in str(over_size_resp.json()["detail"]).lower() or "maximum" in str(over_size_resp.json()["detail"]).lower()

    # 2. Reserve 5 items of 15 MB each (75 MB total)
    for i in range(5):
        resp = await client.post(
            "/v1/uploads/init",
            headers=headers,
            json={
                "case_id": case_id,
                "declared_filename": f"file_{i}.pdf",
                "declared_mime_type": "application/pdf",
                "declared_byte_size": 15 * 1024 * 1024,
            },
        )
        assert resp.status_code == 201

    # 3. Next 15 MB item (total would be 90 MB) succeeds
    resp_6 = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "file_6.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": 15 * 1024 * 1024,
        },
    )
    assert resp_6.status_code == 201

    # 4. Attempting to add 15 MB more (total would be 105 MB > 100 MB aggregate) -> 429 Too Many Requests
    quota_exceeded_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "overflow.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": 15 * 1024 * 1024,
        },
    )
    assert quota_exceeded_resp.status_code == 429
    assert "quota" in quota_exceeded_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_t01_evidence_tenant_isolation(client: AsyncClient, db_session: AsyncSession):
    """T01: Evidence items and upload intents are strictly private to case owner; cross-tenant access returns 404."""
    # Tenant A
    resp_a = await client.post("/auth/guest")
    token_a = resp_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    case_a = (await client.post(
        "/v1/cases",
        headers=headers_a,
        json={"title": "Tenant A Secret Invoice Case", "jurisdiction": "BD"},
    )).json()

    init_a = (await client.post(
        "/v1/uploads/init",
        headers=headers_a,
        json={
            "case_id": case_a["id"],
            "declared_filename": "private_bank_slip.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": 2048,
        },
    )).json()

    # Tenant B
    client.cookies.clear()
    resp_b = await client.post("/auth/guest")
    token_b = resp_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Tenant B tries to init upload on Tenant A's case -> 404
    b_init = await client.post(
        "/v1/uploads/init",
        headers=headers_b,
        json={
            "case_id": case_a["id"],
            "declared_filename": "malicious.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": 1024,
        },
    )
    assert b_init.status_code == 404

    # Tenant B tries to complete Tenant A's upload intent -> 404
    b_complete = await client.post(
        f"/v1/uploads/{init_a['intent_id']}/complete",
        headers=headers_b,
    )
    assert b_complete.status_code == 404

    # Tenant B tries to list Tenant A's evidence -> 404
    b_list = await client.get(
        f"/v1/cases/{case_a['id']}/evidence",
        headers=headers_b,
    )
    assert b_list.status_code == 404
