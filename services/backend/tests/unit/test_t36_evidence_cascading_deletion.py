import io
import uuid
import pytest
from httpx import AsyncClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.ext.asyncio import AsyncSession


def make_pdf(filename_token: str = "deleteme") -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(100, 700, f"Deletable document: {filename_token}")
    c.drawString(100, 660, "Amount: 1000 BDT")
    c.showPage()
    c.save()
    return buf.getvalue()


@pytest.mark.asyncio
async def test_t36_evidence_deletion_purges_files_and_invalidates_spans(client: AsyncClient, db_session: AsyncSession):
    """T36: Evidence deletion removes private derivatives, purged storage, unlinks spans, bumps case version, and prevents revival."""
    # 1. Setup case & assert fact
    auth_resp = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {auth_resp.json()['access_token']}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Deletion Test Case", "jurisdiction": "BD"},
    )
    case_data = case_resp.json()
    case_id = case_data["id"]
    initial_version = case_data["row_version"]

    fact_resp = await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={
            "field_name": "claimed_amount",
            "field_type": "money",
            "raw_value": "1000 BDT",
            "original_text": "1000 BDT",
            "origin": "user_statement",
        },
    )
    fact_id = fact_resp.json()["id"]

    # 2. Upload evidence item
    pdf_bytes = make_pdf("purge_candidate")
    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "to_be_deleted.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(pdf_bytes),
        },
    )
    evidence_id = init_resp.json()["intent_id"]
    token = init_resp.json()["upload_token"]

    await client.put(f"/v1/uploads/{evidence_id}/raw?token={token}", content=pdf_bytes)
    await client.post(f"/v1/uploads/{evidence_id}/complete", headers=headers)

    # 3. Link evidence to fact
    await client.post(
        f"/v1/cases/{case_id}/evidence/{evidence_id}/spans",
        headers=headers,
        json={"assertion_id": fact_id, "page_number": 1, "selected_text": "1000 BDT"},
    )

    # Verify link exists
    spans_before = await client.get(f"/v1/cases/{case_id}/evidence/{evidence_id}/spans", headers=headers)
    assert len(spans_before.json()) == 1

    # Verify preview works
    preview_before = await client.get(f"/v1/cases/{case_id}/evidence/{evidence_id}/preview", headers=headers)
    assert preview_before.status_code == 200

    # 4. Perform cascading deletion (T36)
    del_resp = await client.delete(f"/v1/cases/{case_id}/evidence/{evidence_id}", headers=headers)
    assert del_resp.status_code == 200
    del_data = del_resp.json()
    assert del_data["status"] == "deleted"
    assert del_data["deleted_links_count"] == 1
    assert del_data["case_version"] > initial_version

    # 5. Invariant T36 Verification:
    # A. Evidence details return 404
    ev_get = await client.get(f"/v1/cases/{case_id}/evidence/{evidence_id}", headers=headers)
    assert ev_get.status_code == 404

    # B. Preview returns 404
    preview_after = await client.get(f"/v1/cases/{case_id}/evidence/{evidence_id}/preview", headers=headers)
    assert preview_after.status_code == 404

    # C. Linked spans are completely removed
    spans_after = await client.get(f"/v1/cases/{case_id}/evidence/{evidence_id}/spans", headers=headers)
    assert len(spans_after.json()) == 0

    # D. Re-completing or reviving the deleted evidence is rejected
    revive_resp = await client.post(f"/v1/uploads/{evidence_id}/complete", headers=headers)
    assert revive_resp.status_code in (404, 409, 422)
