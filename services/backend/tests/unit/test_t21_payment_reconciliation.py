import io
import uuid
import pytest
from httpx import AsyncClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.ext.asyncio import AsyncSession


def make_pdf_with_amount(amount_text: str, filename_token: str = "receipt") -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(100, 700, f"Daraz Receipt {filename_token}")
    c.drawString(100, 660, f"Paid: {amount_text}")
    c.drawString(100, 620, "Date: 15/10/2026")
    c.showPage()
    c.save()
    return buf.getvalue()


@pytest.mark.asyncio
async def test_t21_payment_conflict_and_multi_receipt_resolution(client: AsyncClient, db_session: AsyncSession):
    """T21: ৳5,500 narration vs ৳5,000 receipt prompts clarification; second linked ৳500 resolves total; duplicate/unrelated receipt does not."""
    # 1. User sets up case with ৳5,500 narrated claim
    auth_resp = await client.post("/auth/guest")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Reconciliation Test Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    fact_resp = await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={
            "field_name": "claimed_amount",
            "field_type": "money",
            "raw_value": "৳৫,৫০০",
            "original_text": "৳৫,৫০০",
            "origin": "user_statement",
        },
    )
    assert fact_resp.status_code == 201
    fact_id = fact_resp.json()["id"]

    # 2. Upload Receipt 1 (৳5,000)
    pdf_5000 = make_pdf_with_amount("5000 BDT", "main_goods")
    init_1 = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "receipt_5000.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(pdf_5000),
        },
    )
    ev_1_id = init_1.json()["intent_id"]
    await client.put(f"/v1/uploads/{ev_1_id}/raw?token={init_1.json()['upload_token']}", content=pdf_5000)
    await client.post(f"/v1/uploads/{ev_1_id}/complete", headers=headers)

    # Link Receipt 1 to the fact
    await client.post(
        f"/v1/cases/{case_id}/evidence/{ev_1_id}/spans",
        headers=headers,
        json={"assertion_id": fact_id, "page_number": 1, "selected_text": "5000 BDT"},
    )

    # 3. Check reconciliation with only Receipt 1 linked (T21 Invariant: Discrepancy detected)
    recon_1 = await client.get(f"/v1/cases/{case_id}/evidence/reconciliation", headers=headers)
    assert recon_1.status_code == 200
    r1_data = recon_1.json()

    assert r1_data["narrated_amount_minor_units"] == 550000
    assert r1_data["linked_evidence_total_minor_units"] == 500000
    assert r1_data["discrepancy_minor_units"] == 50000  # ৳500 discrepancy
    assert r1_data["is_reconciled"] is False
    assert r1_data["status"] == "discrepancy"
    assert "৳5,500" in r1_data["prompt_bn"] or "5,500" in r1_data["prompt_bn"] or "5,500" in r1_data["prompt_en"]

    # 4. Upload Receipt 2 (৳500 delivery charge) and Unrelated Receipt (৳12,000)
    pdf_500 = make_pdf_with_amount("500 BDT", "delivery_fee")
    init_2 = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "receipt_500.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(pdf_500),
        },
    )
    ev_2_id = init_2.json()["intent_id"]
    await client.put(f"/v1/uploads/{ev_2_id}/raw?token={init_2.json()['upload_token']}", content=pdf_500)
    await client.post(f"/v1/uploads/{ev_2_id}/complete", headers=headers)

    pdf_unrelated = make_pdf_with_amount("12000 BDT", "other_merchant")
    init_unrelated = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "receipt_unrelated.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(pdf_unrelated),
        },
    )
    ev_unrel_id = init_unrelated.json()["intent_id"]
    await client.put(f"/v1/uploads/{ev_unrel_id}/raw?token={init_unrelated.json()['upload_token']}", content=pdf_unrelated)
    await client.post(f"/v1/uploads/{ev_unrel_id}/complete", headers=headers)

    # Before linking Receipt 2: Check unlinked items available (T21 Invariant: Unrelated receipt not counted)
    recon_unlinked = await client.get(f"/v1/cases/{case_id}/evidence/reconciliation", headers=headers)
    assert recon_unlinked.status_code == 200
    ru_data = recon_unlinked.json()
    assert ru_data["is_reconciled"] is False
    assert ru_data["status"] == "unlinked_evidence_available"
    assert len(ru_data["unlinked_items"]) == 2  # Receipt 2 and unrelated receipt
    # Total linked is STILL 500000 minor units because unlinked receipts are not counted
    assert ru_data["linked_evidence_total_minor_units"] == 500000

    # 5. Link Receipt 2 (৳500)
    await client.post(
        f"/v1/cases/{case_id}/evidence/{ev_2_id}/spans",
        headers=headers,
        json={"assertion_id": fact_id, "page_number": 1, "selected_text": "500 BDT"},
    )

    # 6. Re-check reconciliation (T21 Invariant: Now exactly reconciles to ৳5,500!)
    recon_final = await client.get(f"/v1/cases/{case_id}/evidence/reconciliation", headers=headers)
    assert recon_final.status_code == 200
    rf_data = recon_final.json()

    assert rf_data["narrated_amount_minor_units"] == 550000
    assert rf_data["linked_evidence_total_minor_units"] == 550000
    assert rf_data["discrepancy_minor_units"] == 0
    assert rf_data["is_reconciled"] is True
    assert rf_data["status"] == "reconciled"


@pytest.mark.asyncio
async def test_t21_duplicate_receipt_exclusion(client: AsyncClient, db_session: AsyncSession):
    """T21: Duplicate receipt content with identical hash does not double-count in reconciliation."""
    auth_resp = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {auth_resp.json()['access_token']}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Duplicate Receipt Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    fact_resp = await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={
            "field_name": "claimed_amount",
            "field_type": "money",
            "raw_value": "5000 BDT",
            "original_text": "5000 BDT",
            "origin": "user_statement",
        },
    )
    fact_id = fact_resp.json()["id"]

    pdf_bytes = make_pdf_with_amount("5000 BDT", "identical")

    # Upload receipt first time
    init_1 = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "invoice_dup1.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(pdf_bytes),
        },
    )
    ev_1_id = init_1.json()["intent_id"]
    await client.put(f"/v1/uploads/{ev_1_id}/raw?token={init_1.json()['upload_token']}", content=pdf_bytes)
    await client.post(f"/v1/uploads/{ev_1_id}/complete", headers=headers)

    # Upload identical receipt second time
    init_2 = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "invoice_dup2.pdf",
            "declared_mime_type": "application/pdf",
            "declared_byte_size": len(pdf_bytes),
        },
    )
    ev_2_id = init_2.json()["intent_id"]
    await client.put(f"/v1/uploads/{ev_2_id}/raw?token={init_2.json()['upload_token']}", content=pdf_bytes)
    await client.post(f"/v1/uploads/{ev_2_id}/complete", headers=headers)

    # Link both to the same fact
    await client.post(
        f"/v1/cases/{case_id}/evidence/{ev_1_id}/spans",
        headers=headers,
        json={"assertion_id": fact_id, "page_number": 1},
    )
    await client.post(
        f"/v1/cases/{case_id}/evidence/{ev_2_id}/spans",
        headers=headers,
        json={"assertion_id": fact_id, "page_number": 1},
    )

    recon = await client.get(f"/v1/cases/{case_id}/evidence/reconciliation", headers=headers)
    assert recon.status_code == 200
    r_data = recon.json()

    # The duplicate should be flagged and NOT double-counted (still 500,000, not 1,000,000)
    assert r_data["linked_evidence_total_minor_units"] == 500000
    assert r_data["is_reconciled"] is True
    duplicate_items = [i for i in r_data["reconciled_items"] if i["is_duplicate"]]
    assert len(duplicate_items) == 1
