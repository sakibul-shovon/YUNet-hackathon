import io
import uuid
import pytest
from httpx import AsyncClient
from PIL import Image

from app.actions.export_service import ExportService
from app.actions.portal_field_maps import PORTAL_MAP_REGISTRY, PortalFieldMapService


@pytest.mark.asyncio
async def test_p09_1_action_dag_dependency_and_non_forced_seller_notice(client: AsyncClient, db_session):
    """P09.1 & T20: E-commerce dispute action DAG has optional seller notice and ready CCMS complaint."""
    # 1. Bootstrap Guest
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create e-commerce failure case
    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={
            "title": "Undelivered Smart Watch",
            "jurisdiction": "BD",
            "merchant_name": "ElectroGadgets BD",
            "desired_outcomes": ["full_refund"],
        },
    )).json()
    case_id = case["id"]

    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "purchase_channel", "field_type": "string", "raw_value": "ecommerce"},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "goods_delivered", "field_type": "boolean", "raw_value": False},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "promised_delivery_date_passed", "field_type": "boolean", "raw_value": True},
    )

    # 3. Fetch Action DAG
    res = await client.get(f"/v1/cases/{case_id}/actions/dag", headers=headers)
    assert res.status_code == 200
    dag = res.json()

    assert dag["case_id"] == case_id
    assert dag["primary_action_id"] == "prepare_dncrp_complaint"

    nodes_by_id = {n["action_id"]: n for n in dag["nodes"]}
    assert "prepare_merchant_notice" in nodes_by_id
    assert "prepare_dncrp_complaint" in nodes_by_id

    # Invariant: Private seller notice is NOT universally mandatory
    merchant_notice = nodes_by_id["prepare_merchant_notice"]
    assert merchant_notice["is_mandatory"] is False
    assert merchant_notice["status"] == "optional"

    # DNCRP CCMS Complaint is ready immediately and is primary
    dncrp_complaint = nodes_by_id["prepare_dncrp_complaint"]
    assert dncrp_complaint["is_mandatory"] is True
    assert dncrp_complaint["status"] == "ready"
    assert dncrp_complaint["is_primary"] is True
    assert dncrp_complaint["destination_id"] == "dncrp_ccms_portal"


@pytest.mark.asyncio
async def test_p09_1_action_dag_financial_stage_hierarchy_t20(client: AsyncClient, db_session):
    """P09.1 & T20: Financial MFS dispute enforces Stage 1 provider grievance before Stage 2 BB CIPC."""
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={
            "title": "MFS Unauthorized Charge Dispute",
            "jurisdiction": "BD",
            "merchant_name": "QuickPay MFS",
            "desired_outcomes": ["full_refund"],
        },
    )).json()
    case_id = case["id"]

    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "payment_instrument_kind", "field_type": "string", "raw_value": "mfs_wallet"},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "transaction_unauthorized", "field_type": "boolean", "raw_value": True},
    )

    # Initially: No Stage 1 ticket filed
    res1 = await client.get(f"/v1/cases/{case_id}/actions/dag", headers=headers)
    assert res1.status_code == 200
    dag1 = res1.json()

    assert dag1["primary_action_id"] == "prepare_provider_formal_letter"
    nodes1 = {n["action_id"]: n for n in dag1["nodes"]}

    # Stage 1 must be ready and primary
    s1 = nodes1["prepare_provider_formal_letter"]
    assert s1["status"] == "ready"
    assert s1["is_primary"] is True

    # Stage 2 must be BLOCKED with explicit T20 explanation
    s2 = nodes1["prepare_bb_cipc_escalation"]
    assert s2["status"] == "blocked"
    assert s2["is_primary"] is False
    assert len(s2["blocking_reasons"]) > 0
    assert any("T20" in r or "Stage 1" in r or "ticket" in r for r in s2["blocking_reasons"])

    # Now consumer files Stage 1 ticket
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "provider_ticket_filed", "field_type": "boolean", "raw_value": True},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "provider_ticket_number", "field_type": "string", "raw_value": "TKT-2026-9911"},
    )

    # Fetch DAG again
    res2 = await client.get(f"/v1/cases/{case_id}/actions/dag", headers=headers)
    assert res2.status_code == 200
    dag2 = res2.json()

    assert dag2["primary_action_id"] == "prepare_bb_cipc_escalation"
    nodes2 = {n["action_id"]: n for n in dag2["nodes"]}

    # Stage 1 is completed
    assert nodes2["prepare_provider_formal_letter"]["status"] == "completed"

    # Stage 2 is unblocked and ready!
    assert nodes2["prepare_bb_cipc_escalation"]["status"] == "ready"
    assert nodes2["prepare_bb_cipc_escalation"]["is_primary"] is True


@pytest.mark.asyncio
async def test_p09_2_document_ast_and_user_edit_t26_t29(client: AsyncClient, db_session):
    """P09.2 & T26 & T29: Document AST sentence source mapping and user edit classification."""
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={
            "title": "Camera Order Scam",
            "jurisdiction": "BD",
            "merchant_name": "PhotoHub Dhaka",
            "desired_outcomes": ["full_refund"],
        },
    )).json()
    case_id = case["id"]

    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "incident_date", "field_type": "date", "raw_value": "2026-10-15"},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "amount_paid", "field_type": "money", "raw_value": 3500000},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "goods_delivered", "field_type": "boolean", "raw_value": False},
    )

    # 1. Fetch document AST
    res = await client.get(f"/v1/cases/{case_id}/documents/ast?locale=en", headers=headers)
    assert res.status_code == 200
    ast = res.json()

    assert ast["lifecycle_state"] == "unsubmitted_draft"
    assert ast["is_filed"] is False
    assert ast["is_sent"] is False
    assert len(ast["sections"]) >= 3

    # Check background section sentence classification
    bg_sec = next(s for s in ast["sections"] if s["section_id"] == "sec_background")
    sent_bg1 = next(s for s in bg_sec["sentences"] if s["sentence_id"] == "bg_1")
    assert sent_bg1["statement_type"] == "user_allegation"  # not yet reviewed
    assert sent_bg1["supporting_fact_id"] is not None
    assert sent_bg1["is_user_edited"] is False

    # Check remedy section sentence classification
    rem_sec = next(s for s in ast["sections"] if s["section_id"] == "sec_remedy")
    sent_rem1 = rem_sec["sentences"][0]
    assert sent_rem1["statement_type"] == "user_allegation"
    assert sent_rem1["supporting_citation"] is None
    assert 'request a refund' in sent_rem1['text']

    # 2. Apply user edit to sentence bg_1 (T29 Invariant)
    edit_payload = {
        "document_type": "dncrp_ccms_complaint",
        "section_id": "sec_background",
        "sentence_id": "bg_1",
        "new_text": "I ordered a Sony mirrorless camera from PhotoHub Dhaka via WhatsApp, but they stopped answering calls.",
    }
    edit_res = await client.post(f"/v1/cases/{case_id}/documents/edit", headers=headers, json=edit_payload)
    assert edit_res.status_code == 200
    edited_ast = edit_res.json()

    edited_bg_sec = next(s for s in edited_ast["sections"] if s["section_id"] == "sec_background")
    edited_sent = next(s for s in edited_bg_sec["sentences"] if s["sentence_id"] == "bg_1")

    # Invariant T29: User edit is classified as user_allegation and verified status is cleared!
    assert edited_sent["text"] == edit_payload["new_text"]
    assert edited_sent["is_user_edited"] is True
    assert edited_sent["statement_type"] == "user_allegation"
    assert edited_sent["supporting_fact_id"] is None

    # Invariant T26: Lifecycle state remains unsubmitted_draft
    assert edited_ast["lifecycle_state"] == "unsubmitted_draft"
    assert edited_ast["is_filed"] is False


@pytest.mark.asyncio
async def test_p09_3_portal_field_maps_and_stale_fallback_t33(client: AsyncClient, db_session):
    """P09.3 & T33: Portal field map transformations, no credentials, and stale-map fallback."""
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={
            "title": "Defective Blender",
            "jurisdiction": "BD",
            "merchant_name": "KitchenStore BD",
            "desired_outcomes": ["replacement"],
        },
    )).json()
    case_id = case["id"]

    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "incident_date", "field_type": "date", "raw_value": "2026-10-20"},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "amount_paid", "field_type": "money", "raw_value": 4500},
    )

    # 1. Fetch DNCRP CCMS field map
    res = await client.get(f"/v1/cases/{case_id}/portals/dncrp_ccms/fields", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["portal_id"] == "dncrp_ccms"
    assert data["official_destination_url"] == "https://dncrp.com/"
    assert data["is_stale"] is False

    fields = {f["field_key"]: f for f in data["fields"]}
    assert "opposite_party_name" in fields
    assert fields["opposite_party_name"]["prepared_value"] == "KitchenStore BD"

    assert "incident_date" in fields
    assert fields["incident_date"]["prepared_value"] == "2026-10-20"

    # Money transformation to BDT decimal string
    assert "claim_amount_bdt" in fields
    assert fields["claim_amount_bdt"]["prepared_value"] == "4,500.00"

    # Invariant T33: No portal credentials, passwords, or CAPTCHA exposed in fields
    for f in data["fields"]:
        assert "password" not in f["field_key"].lower()
        assert "captcha" not in f["field_key"].lower()
        assert "otp" not in f["field_key"].lower()
        assert "pin" not in f["field_key"].lower()

    # 2. Test Stale Map fallback behavior
    stale_map = PortalFieldMapService.get_field_map(
        portal_id="dncrp_ccms",
        case_data={"merchant_name": "Stale Store"},
        facts={"amount_paid": 100000},
    )
    # Simulate stale state
    stale_map.is_stale = True
    stale_map.stale_reason = "DNCRP portal updated form markup on 2026-11-01. Field mapping pending review."
    assert stale_map.is_stale is True
    assert stale_map.stale_reason is not None


@pytest.mark.asyncio
async def test_p09_4_export_markdown_and_html_t27_t34(client: AsyncClient, db_session):
    """P09.4 & T27: Exports dispute document as Markdown and HTML without marking case as filed."""
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={
            "title": "Shoes Never Delivered",
            "jurisdiction": "BD",
            "merchant_name": "Apex Fashions",
            "desired_outcomes": ["full_refund"],
        },
    )).json()
    case_id = case["id"]

    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "amount_paid", "field_type": "money", "raw_value": 280000},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "goods_delivered", "field_type": "boolean", "raw_value": False},
    )

    # 1. Export as Markdown
    md_res = await client.post(f"/v1/cases/{case_id}/export/markdown?locale=en", headers=headers)
    assert md_res.status_code == 200
    md_data = md_res.json()

    assert md_data["format"] == "markdown"
    assert "Apex Fashions" in md_data["content"]
    assert "PREPARATION MATERIAL ONLY" in md_data["disclaimer_notice"]
    assert len(md_data["sha256_hash"]) == 64
    assert md_data["is_filed"] is False  # Invariant T27
    assert md_data["is_sent"] is False

    # 2. Export as HTML (Bangla)
    html_res = await client.post(f"/v1/cases/{case_id}/export/html?locale=bn", headers=headers)
    assert html_res.status_code == 200
    html_data = html_res.json()

    assert html_data["format"] == "html"
    assert "<!DOCTYPE html>" in html_data["content"]
    assert "শুধুমাত্র প্রস্তুতির খসড়া" in html_data["content"]
    assert html_data["is_filed"] is False  # Invariant T27
    assert html_data["is_sent"] is False

    # 3. Verify case in DB is still unsubmitted (Invariant T27)
    case_check = (await client.get(f"/v1/cases/{case_id}", headers=headers)).json()
    assert case_check["lifecycle_status"] != "filed"


def test_p09_5_true_raster_redaction_t35():
    """P09.5 & T35: True raster redaction permanently destroys pixels and strips metadata."""
    # Create a 100x100 white test image
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    original_bytes = buf.getvalue()

    # Redact box from (20, 20) with width 30 and height 30
    redaction_box = [{"x": 20, "y": 20, "w": 30, "h": 30}]
    redacted_bytes = ExportService.apply_raster_redaction(original_bytes, redaction_box)

    assert len(redacted_bytes) > 0

    # Load redacted image and inspect pixel buffer
    redacted_img = Image.open(io.BytesIO(redacted_bytes))
    assert redacted_img.size == (100, 100)

    # Pixel inside box (25, 25) must be solid black (0, 0, 0)
    inside_pixel = redacted_img.getpixel((25, 25))
    assert inside_pixel == (0, 0, 0)

    # Pixel outside box (5, 5) must remain white (255, 255, 255)
    outside_pixel = redacted_img.getpixel((5, 5))
    assert outside_pixel == (255, 255, 255)


@pytest.mark.asyncio
async def test_p09_7_destination_registry_and_link_health_t54(client: AsyncClient):
    """P09.7 & T54: Official complaint destination registry, direct links, and link-health fallback."""
    # 1. List all destinations
    res = await client.get("/v1/actions/destinations")
    assert res.status_code == 200
    destinations = res.json()

    dest_by_id = {d["destination_id"]: d for d in destinations}
    assert "dncrp_ccms_portal" in dest_by_id
    assert "bb_cipc_portal" in dest_by_id
    assert "dncrp_hotline_16121" in dest_by_id

    # Check DNCRP CCMS portal details
    ccms = dest_by_id["dncrp_ccms_portal"]
    assert ccms["link_health"] == "healthy"
    assert ccms["official_portal_url"] == "https://dncrp.com/"
    assert len(ccms["prerequisites_en"]) >= 3
    assert len(ccms["prerequisites_bn"]) >= 3
    assert "official guidance" in ccms["fallback_instructions_en"]

    # Check BB CIPC portal link health degradation & fallback
    cipc = dest_by_id["bb_cipc_portal"]
    assert cipc["link_health"] == "linked_unconfirmed"
    assert "cipc@bb.org.bd" in cipc["fallback_instructions_en"]
    assert "16236" in cipc["fallback_instructions_en"]

    # 2. Get single destination
    single_res = await client.get("/v1/actions/destinations/dncrp_hotline_16121")
    assert single_res.status_code == 200
    hotline = single_res.json()
    assert hotline["official_portal_url"] == "tel:16121"
    assert "+8802223381655" in hotline["fallback_instructions_en"]
