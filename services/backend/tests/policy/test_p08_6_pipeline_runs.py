import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_p08_6_pipeline_runs_and_receipts_t53(client: AsyncClient, db_session):
    """P08.6 & T53: Processing details reflect actual durable stage/channel/version state without fabricated metrics."""
    boot = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {boot.json()['access_token']}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Receipt Transparency Case", "jurisdiction": "BD", "story_narrative": "I ordered an earphone but it never arrived."},
    )).json()
    case_id = case["id"]

    # Reading a case must not manufacture execution receipts.
    res = await client.get(f"/v1/cases/{case_id}/pipeline-runs", headers=headers)
    assert res.json() == []
    started = await client.post(f"/v1/cases/{case_id}/runs", headers=headers,
                                json={"operation": "assess"})
    assert started.status_code == 202
    runs = (await client.get(f"/v1/cases/{case_id}/pipeline-runs", headers=headers)).json()
    assert len(runs) == 1
    run = runs[0]
    assert run["pipeline_id"] == started.json()["id"]
    assert run["overall_status"] == "completed"
    assert [stage["stage_name"] for stage in run["stages"]] == ["source_retrieval", "procedural_assessment"]
    assert all(stage["duration_ms"] >= 0 for stage in run["stages"])
    assert run["technology_inventory"]["dense_model_executed"] == "false"
    again = (await client.get(f"/v1/cases/{case_id}/pipeline-runs", headers=headers)).json()
    assert again == runs

    # 2. Tenant isolation check: foreign user gets 404
    client.cookies.clear()
    foreign_boot = await client.post("/auth/guest")
    foreign_headers = {"Authorization": f"Bearer {foreign_boot.json()['access_token']}"}

    foreign_res = await client.get(f"/v1/cases/{case_id}/pipeline-runs", headers=foreign_headers)
    assert foreign_res.status_code == 404

