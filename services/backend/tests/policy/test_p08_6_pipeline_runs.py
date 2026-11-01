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

    # 1. Fetch pipeline runs
    res = await client.get(f"/v1/cases/{case_id}/pipeline-runs", headers=headers)
    assert res.status_code == 200
    runs = res.json()
    assert len(runs) >= 1

    run = runs[0]
    assert run["case_id"] == case_id
    assert run["overall_status"] == "verified"

    # Check stages
    stage_names = [s["stage_name"] for s in run["stages"]]
    assert "text_extraction" in stage_names
    assert "layout_detection" in stage_names
    assert "stt_audio" in stage_names
    assert "hybrid_retrieval" in stage_names
    assert "deterministic_policy" in stage_names

    # Check that unused stages are truthfully marked not_applicable (T53)
    audio_stage = next(s for s in run["stages"] if s["stage_name"] == "stt_audio")
    assert audio_stage["status"] == "not_applicable"

    layout_stage = next(s for s in run["stages"] if s["stage_name"] == "layout_detection")
    assert layout_stage["status"] == "not_applicable"

    text_stage = next(s for s in run["stages"] if s["stage_name"] == "text_extraction")
    assert text_stage["status"] == "completed"

    policy_stage = next(s for s in run["stages"] if s["stage_name"] == "deterministic_policy")
    assert policy_stage["status"] == "completed"
    assert "Kleene" in policy_stage["model_or_algorithm"]

    # Check technology inventory
    tech = run["technology_inventory"]
    assert "Kleene" in tech["logic_model"]
    assert "multilingual-e5-small" in tech["embeddings"]
    assert "bm25s" in tech["lexical_search"]

    # 2. Tenant isolation check: foreign user gets 404
    client.cookies.clear()
    foreign_boot = await client.post("/auth/guest")
    foreign_headers = {"Authorization": f"Bearer {foreign_boot.json()['access_token']}"}

    foreign_res = await client.get(f"/v1/cases/{case_id}/pipeline-runs", headers=foreign_headers)
    assert foreign_res.status_code == 404
