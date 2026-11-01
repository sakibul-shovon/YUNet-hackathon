import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_p08_2_issue_crud_and_brand_track_rejection(client: AsyncClient, db_session):
    """P08.2: Issue management CRUD and brand-only false track rejection."""
    boot = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {boot.json()['access_token']}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Multi Item Order", "jurisdiction": "BD", "merchant_name": "Daraz"},
    )).json()
    case_id = case["id"]

    # 1. Create a legitimate issue track: delivery failure
    res_issue = await client.post(
        f"/v1/cases/{case_id}/issues",
        headers=headers,
        json={"canonical_taxonomy": "ecommerce_delivery_failure", "desired_remedy": "full_refund"},
    )
    assert res_issue.status_code == 201
    issue_data = res_issue.json()
    assert issue_data["canonical_taxonomy"] == "ecommerce_delivery_failure"
    assert issue_data["hypothesis_state"] == "hypothesis"
    assert issue_data["active"] is True

    # 2. Brand-only false track rejection: creating an issue track for "brand_reputation"
    res_brand = await client.post(
        f"/v1/cases/{case_id}/issues",
        headers=headers,
        json={"canonical_taxonomy": "brand_reputation"},
    )
    assert res_brand.status_code == 201
    brand_data = res_brand.json()
    assert brand_data["hypothesis_state"] == "rejected"
    assert brand_data["active"] is False
    assert brand_data["rejection_reason"] is not None
    assert "brand reputation" in brand_data["rejection_reason"].lower()


@pytest.mark.asyncio
async def test_p08_2_issue_split_and_merge(client: AsyncClient, db_session):
    """P08.2: User-reviewed issue split and merge operations."""
    boot = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {boot.json()['access_token']}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Order with Multiple Items", "jurisdiction": "BD", "merchant_name": "Daraz"},
    )).json()
    case_id = case["id"]

    # 1. Create initial general issue
    initial_issue = (await client.post(
        f"/v1/cases/{case_id}/issues",
        headers=headers,
        json={"canonical_taxonomy": "ecommerce_delivery_failure", "desired_remedy": "full_refund"},
    )).json()

    # 2. Split into two sub-issues: Item A (delivery failure) and Item B (defective goods)
    split_res = await client.post(
        f"/v1/cases/{case_id}/issues/split",
        headers=headers,
        json={
            "source_issue_id": initial_issue["id"],
            "sub_issues": [
                {"canonical_taxonomy": "ecommerce_delivery_failure", "desired_remedy": "full_refund"},
                {"canonical_taxonomy": "defective_goods", "desired_remedy": "replacement"},
            ],
        },
    )
    assert split_res.status_code == 200
    sub_issues = split_res.json()
    assert len(sub_issues) == 2
    assert sub_issues[0]["canonical_taxonomy"] == "ecommerce_delivery_failure"
    assert sub_issues[1]["canonical_taxonomy"] == "defective_goods"

    # List all issues to verify source is deactivated and sub-issues are active
    all_issues = (await client.get(f"/v1/cases/{case_id}/issues", headers=headers)).json()
    active_issues = [i for i in all_issues if i["active"]]
    assert len(active_issues) == 2

    # 3. Merge sub-issues back
    merge_res = await client.post(
        f"/v1/cases/{case_id}/issues/merge",
        headers=headers,
        json={
            "issue_ids_to_merge": [sub_issues[0]["id"], sub_issues[1]["id"]],
            "target_canonical_taxonomy": "ecommerce_delivery_failure",
            "target_desired_remedy": "full_refund",
        },
    )
    assert merge_res.status_code == 200
    merged = merge_res.json()
    assert merged["canonical_taxonomy"] == "ecommerce_delivery_failure"
    assert merged["active"] is True


@pytest.mark.asyncio
async def test_p08_2_multi_issue_independent_evaluation(client: AsyncClient, db_session):
    """P08.2: Multi-issue assessment evaluates each active issue track independently."""
    boot = await client.post("/auth/guest")
    headers = {"Authorization": f"Bearer {boot.json()['access_token']}"}

    case = (await client.post(
        "/v1/cases",
        headers=headers,
        json={"title": "Multi Issue Case", "jurisdiction": "BD", "merchant_name": "TechStore"},
    )).json()
    case_id = case["id"]

    # Issue 1: Delivery Failure
    i1 = (await client.post(
        f"/v1/cases/{case_id}/issues",
        headers=headers,
        json={"canonical_taxonomy": "ecommerce_delivery_failure", "desired_remedy": "full_refund"},
    )).json()

    # Issue 2: Defective Goods
    i2 = (await client.post(
        f"/v1/cases/{case_id}/issues",
        headers=headers,
        json={"canonical_taxonomy": "defective_goods", "desired_remedy": "replacement"},
    )).json()

    # Add facts
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "goods_delivered", "field_type": "boolean", "raw_value": False, "issue_id": i1["id"]},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "promised_delivery_date_passed", "field_type": "boolean", "raw_value": True, "issue_id": i1["id"]},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "goods_received_defective", "field_type": "boolean", "raw_value": True, "issue_id": i2["id"]},
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        headers=headers,
        json={"field_name": "seller_notified_within_warranty", "field_type": "boolean", "raw_value": True, "issue_id": i2["id"]},
    )

    # Evaluate multi issues
    multi_assess = (await client.get(f"/v1/cases/{case_id}/issues/assessment", headers=headers)).json()
    assert len(multi_assess["independent_paths"]) == 2

    path_taxonomies = [p["canonical_taxonomy"] for p in multi_assess["independent_paths"]]
    assert "ecommerce_delivery_failure" in path_taxonomies
    assert "defective_goods" in path_taxonomies
