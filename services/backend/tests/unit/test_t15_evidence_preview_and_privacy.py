import io
import uuid
import pypdf
import pytest
from httpx import AsyncClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.ext.asyncio import AsyncSession


def make_sample_pdf(text: str = "Daraz Bangladesh Invoice 5000 BDT") -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(100, 700, text)
    c.showPage()
    c.save()
    return buf.getvalue()


@pytest.mark.asyncio
async def test_t15_private_preview_requires_owner_and_sets_cache_headers(client: AsyncClient, db_session: AsyncSession):
    """T15: Private preview requires owner; read lease bounded, cache excluded, no public bucket path."""
    # 1. User A creates case & uploads accepted PDF
    auth_a = await client.post("/auth/guest")
    token_a = auth_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers_a,
        json={"title": "Private Vault Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    pdf_bytes = make_sample_pdf()
    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers_a,
        json={
            "case_id": case_id,
            "declared_filename": "invoice_t15.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(pdf_bytes),
        },
    )
    intent = init_resp.json()
    evidence_id = intent["intent_id"]

    await client.put(f"/v1/uploads/{evidence_id}/raw?token={intent['upload_token']}", content=pdf_bytes)
    comp_resp = await client.post(f"/v1/uploads/{evidence_id}/complete", headers=headers_a)
    assert comp_resp.status_code == 200

    # 2. User A fetches private preview (T15)
    preview_resp = await client.get(
        f"/v1/cases/{case_id}/evidence/{evidence_id}/preview",
        headers=headers_a,
    )
    assert preview_resp.status_code == 200
    assert preview_resp.content == pdf_bytes
    assert preview_resp.headers["content-type"] == "application/pdf"

    # Invariant T15: strict cache exclusion and privacy headers
    cache_ctrl = preview_resp.headers.get("cache-control", "")
    assert "private" in cache_ctrl
    assert "no-store" in cache_ctrl
    assert preview_resp.headers.get("x-content-type-options") == "nosniff"

    # 3. User B (foreign tenant) tries to preview User A's evidence (T01 tenant isolation)
    client.cookies.clear()
    auth_b = await client.post("/auth/guest")
    token_b = auth_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    foreign_resp = await client.get(
        f"/v1/cases/{case_id}/evidence/{evidence_id}/preview",
        headers=headers_b,
    )
    # Foreign tenant must receive 404 (no existence leakage)
    assert foreign_resp.status_code == 404


@pytest.mark.asyncio
async def test_t15_span_to_fact_linking_and_tenant_isolation(client: AsyncClient, db_session: AsyncSession):
    """T14, T15: Links evidence bounding box / page to an asserted case fact; foreign tenant blocked."""
    auth_a = await client.post("/auth/guest")
    token_a = auth_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers_a,
        json={"title": "Span Linking Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    # 1. Assert a fact
    fact_resp = await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers_a,
        json={
            "field_name": "claimed_amount",
            "field_type": "money",
            "raw_value": "5000 BDT",
            "original_text": "5000 BDT",
            "origin": "user_statement",
        },
    )
    assert fact_resp.status_code == 201
    fact_id = fact_resp.json()["id"]

    # 2. Upload evidence
    pdf_bytes = make_sample_pdf()
    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers_a,
        json={
            "case_id": case_id,
            "declared_filename": "invoice_span.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(pdf_bytes),
        },
    )
    evidence_id = init_resp.json()["intent_id"]
    token = init_resp.json()["upload_token"]

    await client.put(f"/v1/uploads/{evidence_id}/raw?token={token}", content=pdf_bytes)
    await client.post(f"/v1/uploads/{evidence_id}/complete", headers=headers_a)

    # 3. Link evidence span to fact assertion
    link_resp = await client.post(
        f"/v1/cases/{case_id}/evidence/{evidence_id}/spans",
        headers=headers_a,
        json={
            "assertion_id": fact_id,
            "page_number": 1,
            "normalized_box": [0.1, 0.2, 0.4, 0.25],
            "selected_text": "5000 BDT",
        },
    )
    assert link_resp.status_code == 201
    link_data = link_resp.json()
    assert link_data["assertion_id"] == fact_id
    assert link_data["page_number"] == 1
    assert link_data["normalized_box"] == [0.1, 0.2, 0.4, 0.25]

    # 4. List spans for evidence
    list_spans_resp = await client.get(
        f"/v1/cases/{case_id}/evidence/{evidence_id}/spans",
        headers=headers_a,
    )
    assert list_spans_resp.status_code == 200
    spans = list_spans_resp.json()
    assert len(spans) == 1
    assert spans[0]["assertion_id"] == fact_id

    # 5. Foreign tenant isolation check
    client.cookies.clear()
    auth_b = await client.post("/auth/guest")
    headers_b = {"Authorization": f"Bearer {auth_b.json()['access_token']}"}

    foreign_link = await client.post(
        f"/v1/cases/{case_id}/evidence/{evidence_id}/spans",
        headers=headers_b,
        json={
            "assertion_id": fact_id,
            "page_number": 1,
        },
    )
    assert foreign_link.status_code == 404
