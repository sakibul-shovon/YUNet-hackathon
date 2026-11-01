import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_p02_4_account_upgrade_preserves_cases(client: AsyncClient, db_session: AsyncSession):
    """P02.4: Upgrading anonymous principal to permanent preserves ownership of existing cases."""
    # 1. Bootstrap anonymous guest
    guest_res = await client.post("/auth/guest")
    assert guest_res.status_code == 200
    guest_data = guest_res.json()
    token = guest_data["access_token"]
    principal_id = guest_data["principal_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify initial kind is anonymous
    me_1 = await client.get("/v1/me", headers=headers)
    assert me_1.status_code == 200
    assert me_1.json()["kind"] == "anonymous"

    # 2. Create a case under anonymous identity
    case_res = await client.post(
        "/v1/cases",
        json={"title": "Pre-Upgrade Anonymous Dispute", "desired_outcomes": ["full_refund"]},
        headers=headers,
    )
    assert case_res.status_code == 201
    case_id = case_res.json()["id"]

    # 3. Perform account upgrade
    upgrade_res = await client.post(
        "/auth/upgrade",
        json={"verified_user_id": "supabase-usr-123", "verified_email": "consumer@example.com"},
        headers=headers,
    )
    assert upgrade_res.status_code == 200
    upgraded_data = upgrade_res.json()
    assert upgraded_data["principal_id"] == principal_id
    assert upgraded_data["kind"] == "permanent"
    new_token = upgraded_data["access_token"]
    upgraded_headers = {"Authorization": f"Bearer {new_token}"}

    # 4. Verify /v1/me reflects permanent status
    me_2 = await client.get("/v1/me", headers=upgraded_headers)
    assert me_2.status_code == 200
    assert me_2.json()["kind"] == "permanent"

    # 5. Verify the existing case is still fully accessible and owned by same principal
    case_reloaded = await client.get(f"/v1/cases/{case_id}", headers=upgraded_headers)
    assert case_reloaded.status_code == 200
    assert case_reloaded.json()["title"] == "Pre-Upgrade Anonymous Dispute"


@pytest.mark.asyncio
async def test_p02_5_consent_and_deletion_revocation(client: AsyncClient, db_session: AsyncSession):
    """P02.5: Recording consent, and deletion immediately revoking case access."""
    # 1. Bootstrap guest
    auth_res = await client.post("/auth/guest")
    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Record consent
    consent_res = await client.post(
        "/v1/consents",
        json={
            "purpose": "ai_processing",
            "policy_version": "2026-v1.0",
            "affirmative_action": "checked_intake_modal",
        },
        headers=headers,
    )
    assert consent_res.status_code == 201
    assert consent_res.json()["purpose"] == "ai_processing"

    # 3. Create case
    case_res = await client.post(
        "/v1/cases",
        json={"title": "Dispute To Be Deleted"},
        headers=headers,
    )
    assert case_res.status_code == 201
    case_id = case_res.json()["id"]

    # 4. Request deletion of the case
    del_res = await client.post(
        "/v1/deletions",
        json={"case_id": case_id, "scope": "case"},
        headers=headers,
    )
    assert del_res.status_code == 202
    del_data = del_res.json()
    assert del_data["status"] == "access_revoked"
    del_id = del_data["id"]

    # 5. Check deletion request status
    status_res = await client.get(f"/v1/deletions/{del_id}", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "access_revoked"

    # 6. Verify case is immediately inaccessible via standard API (returns 404)
    case_check = await client.get(f"/v1/cases/{case_id}", headers=headers)
    assert case_check.status_code == 404

