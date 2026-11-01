import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.cases.models import ExternalReference


@pytest.mark.asyncio
async def test_p10_1_user_reported_update_and_origin_tracking_t38(client: AsyncClient, db_session):
    """P10.1 & T38: Records user-reported updates with origin visibility and no fake official status."""
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Smart Watch Dispute", "jurisdiction": "BD", "merchant_name": "WatchHub BD", "desired_outcomes": ["full_refund"]},
    )).json()
    case_id = case["id"]
    assert case["row_version"] == 1

    # 1. Post user-reported portal submission update (T38)
    update_payload = {
        "update_type": "portal_submission",
        "authority_or_channel": "dncrp_ccms",
        "description": "I submitted the online complaint on DNCRP CCMS portal.",
        "reference_number": "DNCRP-2026-DH-77123",
        "expected_version": 1,
    }
    res = await client.post(
        f"/v1/cases/{case_id}/activity/updates",
        headers=headers,
        json=update_payload,
    )
    assert res.status_code == 201
    event = res.json()

    assert event["event_type"] == "user_reported_update"
    assert event["origin"] == "user_reported"  # Invariant T38: Never fake official
    assert event["reference_number"] == "DNCRP-2026-DH-77123"

    # Verify ExternalReference stored in DB has origin="user_reported"
    stmt = select(ExternalReference).where(ExternalReference.case_id == uuid.UUID(case_id))
    db_res = await db_session.execute(stmt)
    ext_ref = db_res.scalar_one_or_none()
    assert ext_ref is not None
    assert ext_ref.origin == "user_reported"
    assert ext_ref.encrypted_reference == "DNCRP-2026-DH-77123"

    # Verify timeline endpoint returns the event
    timeline_res = await client.get(f"/v1/cases/{case_id}/activity/timeline", headers=headers)
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    assert len(timeline) >= 1
    assert any(e["reference_number"] == "DNCRP-2026-DH-77123" for e in timeline)


@pytest.mark.asyncio
async def test_p10_2_semantic_decision_diff_and_snapshots_t39(client: AsyncClient, db_session):
    """P10.2 & T39: Semantic decision diff and snapshot tracking on external milestone updates."""
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Wallet Uncharged Dispute", "jurisdiction": "BD", "merchant_name": "PayDirect", "desired_outcomes": ["full_refund"]},
    )).json()
    case_id = case["id"]

    # Baseline MFS facts: unauthorized debit without stage 1 ticket
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

    # Initial assessment: provider dispute is primary
    initial_dag = (await client.get(f"/v1/cases/{case_id}/actions/dag", headers=headers)).json()
    assert initial_dag["primary_action_id"] == "prepare_provider_formal_letter"

    case_current = (await client.get(f"/v1/cases/{case_id}", headers=headers)).json()
    curr_version = case_current["row_version"]

    # Now user records Stage 1 provider response/ticket update
    update_payload = {
        "update_type": "seller_response",
        "authority_or_channel": "merchant_direct",
        "description": "Provider issued formal ticket and failed to resolve within SLA.",
        "reference_number": "TKT-2026-9900",
        "additional_facts": {
            "provider_ticket_filed": True,
            "provider_ticket_number": "TKT-2026-9900",
        },
        "expected_version": curr_version,
    }
    update_res = await client.post(
        f"/v1/cases/{case_id}/activity/updates",
        headers=headers,
        json=update_payload,
    )
    assert update_res.status_code == 201
    update_data = update_res.json()

    # Invariant T39: Semantic decision diff
    diff = update_data["decision_diff"]
    assert diff is not None
    assert diff["is_decision_changed"] is True
    assert diff["prior_primary_action"] == "prepare_provider_formal_letter"
    assert diff["new_primary_action"] == "prepare_bb_cipc_escalation"

    # Route transition verified
    changed_issues = [c["issue_type"] for c in diff["changed_routes"]]
    assert "mfs_unauthorized_charge" in changed_issues

    # Verify snapshots endpoint
    snapshots_res = await client.get(f"/v1/cases/{case_id}/snapshots", headers=headers)
    assert snapshots_res.status_code == 200
    snapshots = snapshots_res.json()
    assert len(snapshots) >= 1
    assert snapshots[0]["version"] > 1
    assert len(snapshots[0]["canonical_input_hash"]) == 64


@pytest.mark.asyncio
async def test_p10_4_personal_reminders_and_cancellation_t40(client: AsyncClient, db_session):
    """P10.4 & T40: User personal reminders with timezone-safe semantics distinct from legal caution."""
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Reminder Test Case", "jurisdiction": "BD", "desired_outcomes": ["full_refund"]},
    )).json()
    case_id = case["id"]

    # 1. Create reminder
    reminder_payload = {
        "reminder_title": "Call seller for replacement tracking number",
        "remind_at": "2026-11-08T09:00:00Z",
        "category": "personal_follow_up",
        "notes": "Seller promised courier tracking code by Sunday.",
    }
    res = await client.post(
        f"/v1/cases/{case_id}/reminders",
        headers=headers,
        json=reminder_payload,
    )
    assert res.status_code == 201
    reminder = res.json()

    assert reminder["reminder_title"] == reminder_payload["reminder_title"]
    assert reminder["remind_at"] == reminder_payload["remind_at"]
    assert reminder["is_legal_caution"] is False  # Invariant T40: Personal timer != statutory caution
    assert "CRPA 2009 Section 60" in reminder["disclaimer_notice"]
    reminder_id = reminder["id"]

    # 2. List reminders
    list_res = await client.get(f"/v1/cases/{case_id}/reminders", headers=headers)
    assert list_res.status_code == 200
    reminders = list_res.json()
    assert len(reminders) == 1
    assert reminders[0]["id"] == reminder_id

    # 3. Cancel reminder
    del_res = await client.delete(f"/v1/cases/{case_id}/reminders/{reminder_id}", headers=headers)
    assert del_res.status_code == 204

    # 4. List again: must be empty
    list_res2 = await client.get(f"/v1/cases/{case_id}/reminders", headers=headers)
    assert list_res2.status_code == 200
    assert len(list_res2.json()) == 0


@pytest.mark.asyncio
async def test_p10_5_stale_tab_optimistic_concurrency_t41(client: AsyncClient, db_session):
    """P10.5 & T41: Rejects stale browser tab submissions with 409 Conflict."""
    boot = await client.post("/auth/guest")
    token = boot.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Concurrency Case", "jurisdiction": "BD", "desired_outcomes": ["full_refund"]},
    )).json()
    case_id = case["id"]

    # Stale version: pass expected_version = 999
    update_payload = {
        "update_type": "seller_response",
        "authority_or_channel": "merchant_direct",
        "description": "Seller called me.",
        "expected_version": 999,  # Stale tab!
    }
    res = await client.post(
        f"/v1/cases/{case_id}/activity/updates",
        headers=headers,
        json=update_payload,
    )
    # Must fail with 409 Conflict per Invariant T41
    assert res.status_code == 409
    assert "Stale tab update rejected" in res.json()["detail"]

