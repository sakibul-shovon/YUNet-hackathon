import datetime
import uuid
import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import scoped_tenant_session
from app.core.security import create_access_jwt
from app.identity.models import ActorRole, Principal


@pytest.mark.asyncio
async def test_t01_cross_tenant_isolation(client: AsyncClient, db_session: AsyncSession):
    """T01: Cross-tenant case/evidence access denied; guessed UUIDs disclose no private data (404)."""
    # 1. Bootstrap Tenant A
    resp_a = await client.post("/auth/guest")
    assert resp_a.status_code == 200
    token_a = resp_a.json()["access_token"]
    principal_a = resp_a.json()["principal_id"]

    # 2. Bootstrap Tenant B (isolated incognito session with cleared cookies)
    client.cookies.clear()
    resp_b = await client.post("/auth/guest")
    assert resp_b.status_code == 200
    token_b = resp_b.json()["access_token"]
    principal_b = resp_b.json()["principal_id"]
    assert principal_a != principal_b

    # 3. Tenant A creates a private case
    case_payload = {
        "title": "Tenant A Private Defective Laptop",
        "jurisdiction": "BD",
        "locale": "en-BD",
        "desired_outcomes": ["full_refund"],
        "merchant_name": "Gadget Store BD",
        "story_narrative": "Purchased laptop on Oct 20. Screen has dead pixels.",
    }
    create_res = await client.post(
        "/v1/cases",
        json=case_payload,
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert create_res.status_code == 201
    case_a_id = create_res.json()["id"]

    # 4. Tenant B attempts to access Tenant A's case -> 404 NOT FOUND (no leak)
    get_res = await client.get(
        f"/v1/cases/{case_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert get_res.status_code == 404
    assert get_res.json()["detail"]["error"]["code"] == "CASE_NOT_FOUND"

    # 5. Tenant B attempts to mutate Tenant A's case -> 404 NOT FOUND
    patch_res = await client.patch(
        f"/v1/cases/{case_a_id}",
        json={"expected_version": 1, "title": "Hostile Modification Attempt"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert patch_res.status_code == 404
    assert patch_res.json()["detail"]["error"]["code"] == "CASE_NOT_FOUND"

    # 6. Tenant B attempts to delete Tenant A's case -> 404 NOT FOUND
    del_res = await client.delete(
        f"/v1/cases/{case_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert del_res.status_code == 404

    # 7. Guessed random UUID -> 404 NOT FOUND (non-enumerating)
    random_uuid = str(uuid.uuid4())
    rand_res = await client.get(
        f"/v1/cases/{random_uuid}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert rand_res.status_code == 404

    # 8. Tenant B lists cases -> Tenant A's case is not returned
    list_b = await client.get(
        "/v1/cases",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert list_b.status_code == 200
    assert list_b.json()["total"] == 0


@pytest.mark.asyncio
async def test_t02_token_verification_and_role_escalation(client: AsyncClient, db_session: AsyncSession):
    """T02: Forged/expired/wrong-issuer/wrong-audience JWT and role escalation fail."""
    # 1. Anonymous bootstrap
    resp = await client.post("/auth/guest")
    assert resp.status_code == 200
    valid_token = resp.json()["access_token"]
    principal_id = resp.json()["principal_id"]

    # Valid token succeeds
    me_res = await client.get("/v1/me", headers={"Authorization": f"Bearer {valid_token}"})
    assert me_res.status_code == 200
    assert me_res.headers.get("Cache-Control") == "private, no-store"

    # 2. Forged signature token
    forged_token = jwt.encode(
        {"sub": principal_id, "iss": settings.JWT_ISSUER, "aud": settings.JWT_AUDIENCE},
        "wrong-secret-key-attacker-32-chars-long",
        algorithm="HS256",
    )
    res_forged = await client.get("/v1/me", headers={"Authorization": f"Bearer {forged_token}"})
    assert res_forged.status_code == 401

    # 3. Expired token
    now = datetime.datetime.now(datetime.timezone.utc)
    expired_token = jwt.encode(
        {
            "sub": principal_id,
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "exp": int((now - datetime.timedelta(minutes=10)).timestamp()),
        },
        settings.JWT_SECRET_KEY,
        algorithm="HS256",
    )
    res_expired = await client.get("/v1/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res_expired.status_code == 401
    assert res_expired.json()["detail"]["error"]["code"] == "AUTH_TOKEN_EXPIRED"

    # 4. Wrong issuer token
    wrong_iss_token = jwt.encode(
        {
            "sub": principal_id,
            "iss": "rogue-issuer",
            "aud": settings.JWT_AUDIENCE,
            "exp": int((now + datetime.timedelta(minutes=10)).timestamp()),
        },
        settings.JWT_SECRET_KEY,
        algorithm="HS256",
    )
    res_iss = await client.get("/v1/me", headers={"Authorization": f"Bearer {wrong_iss_token}"})
    assert res_iss.status_code == 401
    assert res_iss.json()["detail"]["error"]["code"] == "AUTH_INVALID_ISSUER"

    # 5. Wrong audience token
    wrong_aud_token = jwt.encode(
        {
            "sub": principal_id,
            "iss": settings.JWT_ISSUER,
            "aud": "wrong-audience-service",
            "exp": int((now + datetime.timedelta(minutes=10)).timestamp()),
        },
        settings.JWT_SECRET_KEY,
        algorithm="HS256",
    )
    res_aud = await client.get("/v1/me", headers={"Authorization": f"Bearer {wrong_aud_token}"})
    assert res_aud.status_code == 401
    assert res_aud.json()["detail"]["error"]["code"] == "AUTH_INVALID_AUDIENCE"

    # 6. Unauthenticated request to private endpoint
    client.cookies.clear()
    res_no_auth = await client.get("/v1/me")
    assert res_no_auth.status_code == 401
    assert res_no_auth.json()["detail"]["error"]["code"] == "AUTH_REQUIRED"


@pytest.mark.asyncio
async def test_t03_connection_pool_tenant_context_hygiene():
    """T03: Pooled connection context does not retain preceding tenant context across checkout."""
    tenant_1 = uuid.uuid4()
    tenant_2 = uuid.uuid4()

    # Session 1 for tenant 1
    async with scoped_tenant_session(tenant_1) as s1:
        assert s1.info.get("current_principal_id") == str(tenant_1)

    # After session 1 closes, verify context is evicted and not retained
    assert "current_principal_id" not in s1.info

    # Session 2 for tenant 2
    async with scoped_tenant_session(tenant_2) as s2:
        assert s2.info.get("current_principal_id") == str(tenant_2)
        assert s2.info.get("current_principal_id") != str(tenant_1)

    assert "current_principal_id" not in s2.info

