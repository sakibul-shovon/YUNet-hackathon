import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.models import Principal


@pytest.fixture
async def judge_a(client: AsyncClient, db_session: AsyncSession) -> tuple[AsyncClient, Principal, dict[str, str]]:
    client.cookies.clear()
    res = await client.post("/auth/guest")
    data = res.json()
    token = data["access_token"]
    principal_id = uuid.UUID(data["principal_id"])
    principal = Principal(id=principal_id, kind="ephemeral", locale="en-BD")
    headers = {"Authorization": f"Bearer {token}"}
    return client, principal, headers


@pytest.fixture
async def judge_b(client: AsyncClient, db_session: AsyncSession) -> tuple[AsyncClient, Principal, dict[str, str]]:
    client.cookies.clear()
    res = await client.post("/auth/guest")
    data = res.json()
    token = data["access_token"]
    principal_id = uuid.UUID(data["principal_id"])
    principal = Principal(id=principal_id, kind="ephemeral", locale="en-BD")
    headers = {"Authorization": f"Bearer {token}"}
    return client, principal, headers


@pytest.mark.asyncio
async def test_p14_2_eight_scenarios_catalogue_and_featured_quick_starts(client: AsyncClient):
    """P14.2: Catalogue contains exactly 8 scenarios with 3 featured quick starts (A, B, H)."""
    res = await client.get("/v1/scenarios")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 8

    letters = {s["scenario_letter"] for s in data}
    assert letters == {"A", "B", "C", "D", "E", "F", "G", "H"}

    featured = [s["scenario_letter"] for s in data if s["is_featured"]]
    assert set(featured) == {"A", "B", "H"}


@pytest.mark.asyncio
async def test_p14_2_judge_sandbox_isolation_and_no_mutation_sharing_t52(
    judge_a: tuple[AsyncClient, Principal, dict[str, str]],
    judge_b: tuple[AsyncClient, Principal, dict[str, str]],
    client: AsyncClient,
):
    """P14.2 (T52): Concurrent judges running the same scenario get isolated cases; mutations never leak."""
    _, _, headers_a = judge_a
    _, _, headers_b = judge_b

    # 1. Judge A launches Scenario A
    res_a = await client.post("/v1/scenarios/scenario_a/launch", headers=headers_a)
    assert res_a.status_code == 201
    case_a_id = res_a.json()["case_id"]

    # 2. Judge B launches Scenario A
    res_b = await client.post("/v1/scenarios/scenario_a/launch", headers=headers_b)
    assert res_b.status_code == 201
    case_b_id = res_b.json()["case_id"]

    # Strict isolation: Case IDs must be different
    assert case_a_id != case_b_id

    # Cross-tenant privacy: Judge B cannot read Judge A's case
    cross_read = await client.get(f"/v1/cases/{case_a_id}", headers=headers_b)
    assert cross_read.status_code == 404

    # 3. Judge A mutates Case A
    patch_res = await client.patch(
        f"/v1/cases/{case_a_id}",
        json={"expected_version": 1, "title": "Mutated by Judge A"},
        headers=headers_a,
    )
    assert patch_res.status_code == 200

    # 4. Verify Judge B's case is completely untouched
    case_b = (await client.get(f"/v1/cases/{case_b_id}", headers=headers_b)).json()
    assert case_b["title"] != "Mutated by Judge A"
    assert case_b["row_version"] == 1

    # 5. Reset Case A back to baseline
    reset_res = await client.post(f"/v1/scenarios/{case_a_id}/reset", headers=headers_a)
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] == "reset_successful"
