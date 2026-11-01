import io
import uuid
from PIL import Image
import pypdf
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.evidence.models import EvidenceItem


def create_test_pdf(page_count: int = 1, password: str | None = None, with_js: bool = False) -> bytes:
    """Helper to synthesize test PDFs with specific page counts, passwords, or script tags."""
    writer = pypdf.PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=72, height=72)

    if password:
        writer.encrypt(password)

    buf = io.BytesIO()
    writer.write(buf)
    pdf_bytes = buf.getvalue()

    if with_js:
        # Inject JavaScript dictionary
        pdf_bytes += b"\n/Names << /JavaScript 12 0 R >>\n/JS (app.alert('Malware');)"

    return pdf_bytes


def create_test_image(width: int, height: int, fmt: str = "PNG") -> bytes:
    """Helper to synthesize test images of specific pixel dimensions."""
    img = Image.new("RGB", (width, height), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_t12_pixel_bomb_rejection(client: AsyncClient, db_session: AsyncSession):
    """T12: Images exceeding 25 megapixels (e.g. 6000x5000 = 30 MP) are rejected as pixel bombs."""
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_resp = await client.post("/v1/cases", headers=headers, json={"title": "Pixel Bomb Test Case", "jurisdiction": "BD"})
    case_id = case_resp.json()["id"]

    # 1. Synthesize 30 Megapixel Image (6,000 x 5,000)
    pixel_bomb_data = create_test_image(6000, 5000, fmt="PNG")

    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "huge_canvas.png",
            "declared_mime_type": "image/png",
            "declared_byte_size": len(pixel_bomb_data),
        },
    )
    assert init_resp.status_code == 201
    intent = init_resp.json()

    # 2. Upload raw bytes to quarantine
    await client.put(f"/v1/uploads/{intent['intent_id']}/raw?token={intent['upload_token']}", content=pixel_bomb_data)

    # 3. Complete Upload -> Probe catches pixel bomb (> 25 MP) -> 422 Unprocessable Entity
    complete_resp = await client.post(f"/v1/uploads/{intent['intent_id']}/complete", headers=headers)
    assert complete_resp.status_code == 422
    data = complete_resp.json()
    detail = data["detail"]
    assert detail["code"] == "PIXEL_BOMB"
    assert detail["retryable"] is False
    assert "25 megapixel" in detail["message"].lower()

    # Verify item status is rejected and quarantine released
    stmt = select(EvidenceItem).where(EvidenceItem.id == uuid.UUID(intent["intent_id"]))
    item = (await db_session.execute(stmt)).scalar_one()
    assert item.status == "rejected"
    assert item.rejection_code == "PIXEL_BOMB"
    assert item.is_retryable is False
    assert item.quota_reserved_bytes == 0


@pytest.mark.asyncio
async def test_t12_pdf_page_bomb_rejection(client: AsyncClient, db_session: AsyncSession):
    """T12: PDF documents exceeding 50 pages (e.g. 52 pages) are rejected."""
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_resp = await client.post("/v1/cases", headers=headers, json={"title": "Page Bomb Test Case", "jurisdiction": "BD"})
    case_id = case_resp.json()["id"]

    # 1. Synthesize 52-page PDF
    page_bomb_data = create_test_pdf(page_count=52)

    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "massive_catalog.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(page_bomb_data),
        },
    )
    assert init_resp.status_code == 201
    intent = init_resp.json()

    # 2. Upload to quarantine
    await client.put(f"/v1/uploads/{intent['intent_id']}/raw?token={intent['upload_token']}", content=page_bomb_data)

    # 3. Complete Upload -> Probe catches page limit (> 50 pages) -> 422
    complete_resp = await client.post(f"/v1/uploads/{intent['intent_id']}/complete", headers=headers)
    assert complete_resp.status_code == 422
    detail = complete_resp.json()["detail"]
    assert detail["code"] == "PDF_PAGE_LIMIT"
    assert detail["retryable"] is False
    assert "50-page" in detail["message"] or "52 pages" in detail["message"]

    stmt = select(EvidenceItem).where(EvidenceItem.id == uuid.UUID(intent["intent_id"]))
    item = (await db_session.execute(stmt)).scalar_one()
    assert item.status == "rejected"
    assert item.rejection_code == "PDF_PAGE_LIMIT"


@pytest.mark.asyncio
async def test_t12_encrypted_pdf_and_active_javascript_rejection(client: AsyncClient, db_session: AsyncSession):
    """T12: Encrypted/password-protected PDFs and PDFs with active script macros are rejected."""
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_resp = await client.post("/v1/cases", headers=headers, json={"title": "Security Rejection Case", "jurisdiction": "BD"})
    case_id = case_resp.json()["id"]

    # --- Test A: Password-Protected PDF ---
    encrypted_pdf = create_test_pdf(page_count=1, password="secret_password_123")
    init_a = (await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "locked_statement.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(encrypted_pdf),
        },
    )).json()

    await client.put(f"/v1/uploads/{init_a['intent_id']}/raw?token={init_a['upload_token']}", content=encrypted_pdf)
    comp_a = await client.post(f"/v1/uploads/{init_a['intent_id']}/complete", headers=headers)
    assert comp_a.status_code == 422
    assert comp_a.json()["detail"]["code"] == "PDF_ENCRYPTED"

    # --- Test B: Active JavaScript in PDF ---
    js_pdf = create_test_pdf(page_count=1, with_js=True)
    init_b = (await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "macro_script.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(js_pdf),
        },
    )).json()

    await client.put(f"/v1/uploads/{init_b['intent_id']}/raw?token={init_b['upload_token']}", content=js_pdf)
    comp_b = await client.post(f"/v1/uploads/{init_b['intent_id']}/complete", headers=headers)
    assert comp_b.status_code == 422
    assert comp_b.json()["detail"]["code"] == "ACTIVE_CONTENT_DETECTED"


@pytest.mark.asyncio
async def test_t12_scanner_outage_stays_quarantined_and_retryable(client: AsyncClient, db_session: AsyncSession):
    """T12: Scanner outage/timeout leaves file quarantined with retryable status; never silently promotes to accepted."""
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_resp = await client.post("/v1/cases", headers=headers, json={"title": "Scanner Outage Case", "jurisdiction": "BD"})
    case_id = case_resp.json()["id"]

    valid_pdf = create_test_pdf(page_count=1)
    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "valid_bill.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(valid_pdf),
        },
    )
    intent = init_resp.json()

    await client.put(f"/v1/uploads/{intent['intent_id']}/raw?token={intent['upload_token']}", content=valid_pdf)

    # Complete upload with header simulating scanner outage
    headers_with_outage = {**headers, "X-Simulate-Scanner-Outage": "true"}
    complete_resp = await client.post(
        f"/v1/uploads/{intent['intent_id']}/complete",
        headers=headers_with_outage,
    )
    assert complete_resp.status_code == 503
    detail = complete_resp.json()["detail"]
    assert detail["code"] == "SCANNER_OUTAGE"
    assert detail["retryable"] is True

    # Invariant T12 Check: Item MUST remain quarantined, NOT accepted
    stmt = select(EvidenceItem).where(EvidenceItem.id == uuid.UUID(intent["intent_id"]))
    item = (await db_session.execute(stmt)).scalar_one()
    assert item.status == "quarantined"
    assert item.is_quarantined is True
    assert item.accepted_path is None
    assert item.is_retryable is True
    assert item.rejection_code == "SCANNER_OUTAGE"

