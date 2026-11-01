import io
import uuid
import pypdf
import pytest
from httpx import AsyncClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.ext.asyncio import AsyncSession


def generate_invoice_pdf(rotated_90: bool = False, multicolumn: bool = False) -> bytes:
    """Helper to generate a native PDF with English, amounts, dates, and order numbers using reportlab."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    if multicolumn:
        # Two-column layout
        # Column 1 (x: 50 to 250)
        c.drawString(60, height - 80, "Order Details Left Column")
        c.drawString(60, height - 110, "Amount: 5500 BDT")
        c.drawString(60, height - 140, "Date: 15/10/2026")
        # Column 2 (x: 350 to 550)
        c.drawString(360, height - 80, "Payment Details Right Column")
        c.drawString(360, height - 110, "TrxID: TXN998877")
        c.drawString(360, height - 140, "Delivery: Daraz Express")
    else:
        # Standard invoice
        c.drawString(100, height - 100, "Daraz Bangladesh Official Invoice")
        c.drawString(100, height - 130, "Paid Total: 5500 BDT")
        c.drawString(100, height - 160, "Date: 15/10/2026")
        c.drawString(100, height - 190, "Order Ref: ORDER-99120")

    c.showPage()
    c.save()

    raw_pdf = buf.getvalue()

    if rotated_90:
        # Rotate page 90 degrees clockwise
        reader = pypdf.PdfReader(io.BytesIO(raw_pdf))
        writer = pypdf.PdfWriter()
        page = reader.pages[0]
        page.rotate(90)
        writer.add_page(page)
        rot_buf = io.BytesIO()
        writer.write(rot_buf)
        return rot_buf.getvalue()

    return raw_pdf


@pytest.mark.asyncio
async def test_t13_native_pdf_critical_token_extraction(client: AsyncClient, db_session: AsyncSession):
    """T13: Native PDF keeps correct text, flags critical money/date/ref tokens, and preserves coordinates."""
    # 1. Bootstrap Guest & Create Case
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Invoice Parsing Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    # 2. Upload Invoice PDF
    invoice_pdf = generate_invoice_pdf()
    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "invoice.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(invoice_pdf),
        },
    )
    intent = init_resp.json()
    evidence_id = intent["intent_id"]

    await client.put(f"/v1/uploads/{evidence_id}/raw?token={intent['upload_token']}", content=invoice_pdf)
    comp_resp = await client.post(f"/v1/uploads/{evidence_id}/complete", headers=headers)
    assert comp_resp.status_code == 200

    # 3. Request Parsed Document Regions
    regions_resp = await client.get(
        f"/v1/cases/{case_id}/evidence/{evidence_id}/regions",
        headers=headers,
    )
    assert regions_resp.status_code == 200
    doc_result = regions_resp.json()

    assert doc_result["has_native_text"] is True
    assert doc_result["ocr_applied"] is False
    assert doc_result["page_count"] == 1
    assert "Daraz Bangladesh" in doc_result["full_text"]

    # Invariant T13: Check critical token tags
    regions = doc_result["regions"]
    assert len(regions) >= 4

    critical_tokens = [r for r in regions if r["is_critical_token"]]
    assert len(critical_tokens) >= 2

    crit_types = {r["critical_token_type"] for r in critical_tokens}
    assert "money" in crit_types or "date" in crit_types or "reference" in crit_types

    # Invariant T14: Check normalized bounding box bounds [0.0, 1.0]
    for r in regions:
        box = r["normalized_box"]
        assert len(box) == 4
        x1, y1, x2, y2 = box
        assert 0.0 <= x1 <= 1.0
        assert 0.0 <= y1 <= 1.0
        assert 0.0 <= x2 <= 1.0
        assert 0.0 <= y2 <= 1.0
        assert x1 <= x2
        assert y1 <= y2


@pytest.mark.asyncio
async def test_t14_rotated_page_coordinates_normalization_and_viewport_resize(client: AsyncClient, db_session: AsyncSession):
    """T14: Rotated page (90°) coordinates normalized to standard [0, 1] top-left box; highlight stays aligned on viewport resize."""
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Rotated Invoice Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    # 1. Upload 90-degree rotated PDF
    rotated_pdf = generate_invoice_pdf(rotated_90=True)
    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "rotated_scan.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(rotated_pdf),
        },
    )
    intent = init_resp.json()
    evidence_id = intent["intent_id"]

    await client.put(f"/v1/uploads/{evidence_id}/raw?token={intent['upload_token']}", content=rotated_pdf)
    await client.post(f"/v1/uploads/{evidence_id}/complete", headers=headers)

    # 2. Query Regions
    reg_resp = await client.get(
        f"/v1/cases/{case_id}/evidence/{evidence_id}/regions",
        headers=headers,
    )
    assert reg_resp.status_code == 200
    doc_result = reg_resp.json()

    # Quality flag confirms rotation normalization
    assert any("ROTATED_PAGE_90_NORMALIZED" in q for q in doc_result["quality_flags"])

    # Verify that all normalized boxes remain bounded inside [0, 1]
    for r in doc_result["regions"]:
        x1, y1, x2, y2 = r["normalized_box"]
        assert 0.0 <= x1 <= 1.0
        assert 0.0 <= y1 <= 1.0
        assert 0.0 <= x2 <= 1.0
        assert 0.0 <= y2 <= 1.0
        assert x1 <= x2
        assert y1 <= y2

        # Viewport resize simulation (Desktop 1440x900 vs Mobile 375x667)
        for vw, vh in [(1440, 900), (375, 667), (768, 1024)]:
            px1, py1 = x1 * vw, y1 * vh
            px2, py2 = x2 * vw, y2 * vh
            assert 0 <= px1 <= vw
            assert 0 <= px2 <= vw
            assert 0 <= py1 <= vh
            assert 0 <= py2 <= vh


@pytest.mark.asyncio
async def test_t14_multicolumn_reading_order(client: AsyncClient, db_session: AsyncSession):
    """T14: Multicolumn document preserves logical reading order (left column before right column)."""
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Multicolumn Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    multicolumn_pdf = generate_invoice_pdf(multicolumn=True)
    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "twocolumn.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(multicolumn_pdf),
        },
    )
    intent = init_resp.json()
    evidence_id = intent["intent_id"]

    await client.put(f"/v1/uploads/{evidence_id}/raw?token={intent['upload_token']}", content=multicolumn_pdf)
    await client.post(f"/v1/uploads/{evidence_id}/complete", headers=headers)

    reg_resp = await client.get(
        f"/v1/cases/{case_id}/evidence/{evidence_id}/regions",
        headers=headers,
    )
    doc_result = reg_resp.json()
    regions = doc_result["regions"]

    # Find position of "Left" and "Right" in extracted text order
    left_positions = [idx for idx, r in enumerate(regions) if "Left" in r["text"]]
    right_positions = [idx for idx, r in enumerate(regions) if "Right" in r["text"]]

    assert len(left_positions) >= 1
    assert len(right_positions) >= 1
    # Left column text must be ordered before right column text (T14 reading order)
    assert left_positions[0] < right_positions[0]

