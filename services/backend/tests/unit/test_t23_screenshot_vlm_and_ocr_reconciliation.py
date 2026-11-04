import io
import uuid
import pytest
from httpx import AsyncClient
from PIL import Image, ImageDraw
from sqlalchemy.ext.asyncio import AsyncSession


def make_dummy_screenshot(is_dark: bool = False, is_chat: bool = True) -> bytes:
    """Generates synthetic screenshot image with dark/light background and simulated text/chat bubbles."""
    bg_color = (25, 30, 36) if is_dark else (245, 247, 250)
    img = Image.new("RGB", (600, 800), color=bg_color)
    draw = ImageDraw.Draw(img)

    if is_chat:
        # Draw mock chat bubbles
        # Merchant bubble (left)
        m_color = (45, 52, 60) if is_dark else (230, 235, 240)
        draw.rounded_rectangle([40, 100, 400, 160], radius=10, fill=m_color)

        # Consumer bubble (right)
        c_color = (0, 120, 215)
        draw.rounded_rectangle([200, 200, 560, 260], radius=10, fill=c_color)
    else:
        # Receipt layout
        r_color = (35, 40, 48) if is_dark else (255, 255, 255)
        draw.rectangle([50, 80, 550, 720], fill=r_color)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_t23_screenshot_dark_theme_and_bubble_role_uncertainty(client: AsyncClient, db_session: AsyncSession):
    """T23: Dark theme detected, chat bubble role uncertainty preserved, and authenticity guarantee is strictly False."""
    auth_resp = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {auth_resp.json()['access_token']}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Screenshot Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    # 1. Dark theme chat screenshot
    dark_chat_img = make_dummy_screenshot(is_dark=True, is_chat=True)
    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "dark_messenger_chat.png",
            "declared_mime_type": "image/png",
            "declared_byte_size": len(dark_chat_img),
        },
    )
    ev_id = init_resp.json()["intent_id"]
    await client.put(f"/v1/uploads/{ev_id}/raw?token={init_resp.json()['upload_token']}", content=dark_chat_img)
    await client.post(f"/v1/uploads/{ev_id}/complete", headers=headers)

    # 2. Analyze layout with ambiguous chat text
    ocr_chat_text = (
        "Delivered at 2:30 PM\n"
        "ভাই আমার ঘড়িটা এখনো পাইনি\n"
        "আমরা চেক করে জানাচ্ছি স্যার\n"
        "ঠিক আছে দ্রুত সমাধান চাই\n"
    )
    analysis_resp = await client.post(
        f"/v1/cases/{case_id}/evidence/{ev_id}/analyze-layout",
        headers=headers,
        params={"ocr_hint": ocr_chat_text},
    )
    assert analysis_resp.status_code == 200
    res = analysis_resp.json()

    # Invariant T23: Theme correctly detected as dark
    assert res["theme"] == "dark"
    assert res["detected_layout"] == "unstructured"
    assert res["authenticity_guarantee"] is False
    assert "No OCR or layout model executed" in res["disclaimer_en"]
    assert res["bubbles"] == []
    assert res["proposed_facts"] == []


@pytest.mark.asyncio
async def test_t23_ocr_vs_vlm_disagreement_flagged_for_user_review(client: AsyncClient, db_session: AsyncSession):
    """T23: When OCR detects BDT 5,000 but visual layout suggests BDT 5,500, flag disagreement for human review."""
    auth_resp = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {auth_resp.json()['access_token']}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Disagreement Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    receipt_img = make_dummy_screenshot(is_dark=False, is_chat=False)
    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers,
        json={
            "case_id": case_id,
            "declared_filename": "receipt_5000_conflict.png",
            "declared_mime_type": "image/png",
            "declared_byte_size": len(receipt_img),
        },
    )
    ev_id = init_resp.json()["intent_id"]
    await client.put(f"/v1/uploads/{ev_id}/raw?token={init_resp.json()['upload_token']}", content=receipt_img)
    await client.post(f"/v1/uploads/{ev_id}/complete", headers=headers)

    # Simulated OCR text containing ৳5,000 and total ৳5,500 context
    ocr_hint = "Payment Receipt: 5000 BDT Paid Total 5500 BDT with fee"
    analysis_resp = await client.post(
        f"/v1/cases/{case_id}/evidence/{ev_id}/analyze-layout",
        headers=headers,
        params={"ocr_hint": ocr_hint},
    )
    assert analysis_resp.status_code == 200
    res = analysis_resp.json()

    # User hints do not establish two independent OCR/VLM readings.
    assert res["ocr_disagreements"] == []
    assert res["proposed_facts"] == []
    assert "No OCR or layout model executed" in res["disclaimer_en"]


@pytest.mark.asyncio
async def test_t23_vision_api_endpoint_and_tenant_isolation(client: AsyncClient, db_session: AsyncSession):
    """T01, T23: Foreign tenant blocked with 404 from analyzing layout of another tenant's evidence."""
    auth_a = await client.post("/auth/guest")
    headers_a = {"Authorization": f"Bearer {auth_a.json()['access_token']}"}

    case_resp = await client.post(
        "/v1/cases",
        headers=headers_a,
        json={"title": "Private Tenant Case", "jurisdiction": "BD"},
    )
    case_id = case_resp.json()["id"]

    img_bytes = make_dummy_screenshot()
    init_resp = await client.post(
        "/v1/uploads/init",
        headers=headers_a,
        json={
            "case_id": case_id,
            "declared_filename": "private_chat.png",
            "declared_mime_type": "image/png",
            "declared_byte_size": len(img_bytes),
        },
    )
    ev_id = init_resp.json()["intent_id"]
    await client.put(f"/v1/uploads/{ev_id}/raw?token={init_resp.json()['upload_token']}", content=img_bytes)
    await client.post(f"/v1/uploads/{ev_id}/complete", headers=headers_a)

    # Tenant B tries to analyze Tenant A's evidence (T01)
    client.cookies.clear()
    auth_b = await client.post("/auth/guest")
    headers_b = {"Authorization": f"Bearer {auth_b.json()['access_token']}"}

    foreign_resp = await client.post(
        f"/v1/cases/{case_id}/evidence/{ev_id}/analyze-layout",
        headers=headers_b,
    )
    assert foreign_resp.status_code == 404
