import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_t04_case_crud_persistence_and_version_conflict(client: AsyncClient, db_session: AsyncSession):
    """T04: Story, remedy, outcomes survive reload; stale PATCH gets 409 CASE_VERSION_CONFLICT."""
    # 1. Authenticate guest
    auth_res = await client.post("/auth/guest")
    assert auth_res.status_code == 200
    token = auth_res.json()["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}

    # 2. Create case with story narrative and desired outcomes
    create_payload = {
        "title": "Faulty Smartphone Delivery",
        "jurisdiction": "BD",
        "locale": "en-BD",
        "desired_outcomes": ["replacement", "compensation_for_delay"],
        "merchant_name": "ElectroTech BD",
        "incident_date": "2026-10-15",
        "story_narrative": "Received a phone with a defective screen on October 15. The seller refused warranty exchange.",
    }
    create_res = await client.post("/v1/cases", json=create_payload, headers=auth_header)
    assert create_res.status_code == 201
    case_data = create_res.json()
    case_id = case_data["id"]
    assert case_data["row_version"] == 1
    assert case_data["story_narrative"] == create_payload["story_narrative"]
    assert case_data["desired_outcomes"] == create_payload["desired_outcomes"]
    assert case_data["display_reference"].startswith("CC-2026-")

    # 3. Reload/Retrieve case and verify durability
    get_res = await client.get(f"/v1/cases/{case_id}", headers=auth_header)
    assert get_res.status_code == 200
    reloaded = get_res.json()
    assert reloaded["id"] == case_id
    assert reloaded["row_version"] == 1
    assert reloaded["story_narrative"] == create_payload["story_narrative"]
    assert reloaded["merchant_name"] == "ElectroTech BD"

    # 4. Successful update with matching expected_version (1 -> 2)
    update_payload_1 = {
        "expected_version": 1,
        "title": "Faulty Smartphone Delivery - Updated",
        "story_narrative": "Updated: Seller promised inspection by Oct 18 but stopped replying.",
    }
    patch_res_1 = await client.patch(f"/v1/cases/{case_id}", json=update_payload_1, headers=auth_header)
    assert patch_res_1.status_code == 200
    updated_1 = patch_res_1.json()
    assert updated_1["row_version"] == 2
    assert updated_1["story_narrative"] == update_payload_1["story_narrative"]

    # 5. Concurrency conflict: A second concurrent update attempts using stale version 1
    stale_update_payload = {
        "expected_version": 1,  # Stale! Current version is 2
        "title": "Concurrent edit attempt with stale version",
    }
    conflict_res = await client.patch(f"/v1/cases/{case_id}", json=stale_update_payload, headers=auth_header)
    assert conflict_res.status_code == 409
    error_detail = conflict_res.json()["detail"]["error"]
    assert error_detail["code"] == "CASE_VERSION_CONFLICT"
    assert error_detail["message_key"] == "case.changed_reload"
    assert error_detail["details"]["expected_version"] == 1
    assert error_detail["details"]["current_version"] == 2

    # 6. Retry with correct expected_version (2 -> 3)
    valid_update_payload = {
        "expected_version": 2,
        "desired_outcomes": ["full_refund"],
    }
    patch_res_2 = await client.patch(f"/v1/cases/{case_id}", json=valid_update_payload, headers=auth_header)
    assert patch_res_2.status_code == 200
    updated_2 = patch_res_2.json()
    assert updated_2["row_version"] == 3
    assert updated_2["desired_outcomes"] == ["full_refund"]

    # 7. Verify chronological activity log (case.created + two case.updated events)
    act_res = await client.get(f"/v1/cases/{case_id}/activity", headers=auth_header)
    assert act_res.status_code == 200
    events = act_res.json()
    assert len(events) >= 3
    assert events[0]["event_sequence"] == 1
    assert events[0]["event_type"] == "case.created"
    assert events[1]["event_sequence"] == 2
    assert events[1]["event_type"] == "case.updated"
    assert events[2]["event_sequence"] == 3
    assert events[2]["event_type"] == "case.updated"

