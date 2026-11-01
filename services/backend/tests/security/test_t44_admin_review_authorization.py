import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_jwt
from app.identity.models import ActorRole, Principal
from app.knowledge.service import KnowledgeService


@pytest.mark.asyncio
async def test_t44_admin_reviewer_authorization_and_release_build(
    client: AsyncClient,
    db_session: AsyncSession,
):
    """T44: Reviewer/publisher authorization enforced; consumer cannot approve; test-only rules rejected."""
    # 1. Ordinary consumer login
    consumer_res = await client.post("/auth/guest")
    consumer_token = consumer_res.json()["access_token"]
    consumer_headers = {"Authorization": f"Bearer {consumer_token}"}

    # Consumer tries to access admin candidate queue -> 403 FORBIDDEN
    res_forbidden = await client.get("/v1/admin/source-candidates", headers=consumer_headers)
    assert res_forbidden.status_code == 403
    assert res_forbidden.json()["detail"]["error"]["code"] == "FORBIDDEN_ROLE"

    # 2. Setup a user with 'reviewer' role
    reviewer_principal = Principal(id=uuid.uuid4(), kind="permanent", locale="en-BD")
    db_session.add(reviewer_principal)
    await db_session.flush()

    reviewer_role = ActorRole(
        id=uuid.uuid4(),
        principal_id=reviewer_principal.id,
        role="reviewer",
        grant_origin="admin_bootstrap",
        scope="global",
    )
    db_session.add(reviewer_role)
    await db_session.commit()

    reviewer_token = create_access_jwt(
        principal_id=reviewer_principal.id,
        kind="permanent",
        roles=["reviewer"],
    )
    reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}

    # Reviewer CAN access admin candidate queue
    res_candidates = await client.get("/v1/admin/source-candidates", headers=reviewer_headers)
    assert res_candidates.status_code == 200

    # 3. Add a candidate source version
    family = await KnowledgeService.create_source_family(
        slug="dncrp_guidance",
        title="DNCRP Practice Guidelines",
        issuer="DNCRP",
        db=db_session,
    )
    version = await KnowledgeService.create_source_version(
        family_id=family.id,
        version_tag="2026-draft",
        text_content="Guideline regarding merchant refund periods.",
        issuer="DNCRP",
        document_type="procedure_guide",
        applicability_status="candidate",
        db=db_session,
    )

    # Reviewer submits review and approves the version
    review_payload = {
        "scope": "origin_and_procedure",
        "decision": "approved",
        "rationale": "Verified official procedure guideline issued by Director General.",
        "limitations": "Applies to retail e-commerce only.",
    }
    review_res = await client.post(
        f"/v1/admin/source-versions/{version.id}/review",
        json=review_payload,
        headers=reviewer_headers,
    )
    assert review_res.status_code == 200
    assert review_res.json()["decision"] == "approved"

    # 4. Setup a user with 'publisher' role
    publisher_principal = Principal(id=uuid.uuid4(), kind="permanent", locale="en-BD")
    db_session.add(publisher_principal)
    await db_session.flush()

    publisher_role = ActorRole(
        id=uuid.uuid4(),
        principal_id=publisher_principal.id,
        role="publisher",
        grant_origin="admin_bootstrap",
        scope="global",
    )
    db_session.add(publisher_role)
    await db_session.commit()

    publisher_token = create_access_jwt(
        principal_id=publisher_principal.id,
        kind="permanent",
        roles=["publisher"],
    )
    publisher_headers = {"Authorization": f"Bearer {publisher_token}"}

    # 5. Publisher tries to build release with a 'test_only' rule -> 422 REJECTED (T18)
    bad_build_payload = {
        "release_id": "REL-2026-FAIL",
        "release_mode": "procedure_guidance",
        "source_version_ids": [str(version.id)],
        "rules": [
            {
                "rule_id": "experimental_rule_test_only",
                "status": "test_only",
                "issue_type": "refund",
            }
        ],
    }
    res_bad_build = await client.post(
        "/v1/admin/releases/build",
        json=bad_build_payload,
        headers=publisher_headers,
    )
    assert res_bad_build.status_code == 422
    assert res_bad_build.json()["detail"]["error"]["code"] == "TEST_ONLY_RULE_REJECTED"

    # 6. Valid release build succeeds
    valid_build_payload = {
        "release_id": "REL-2026-001",
        "release_mode": "procedure_guidance",
        "source_version_ids": [str(version.id)],
        "rules": [
            {
                "rule_id": "crpa_delivery_failure_v1",
                "status": "active",
                "issue_type": "delivery_failure",
            }
        ],
    }
    res_valid_build = await client.post(
        "/v1/admin/releases/build",
        json=valid_build_payload,
        headers=publisher_headers,
    )
    assert res_valid_build.status_code == 201
    release_data = res_valid_build.json()
    assert release_data["release_id"] == "REL-2026-001"
    assert release_data["is_active"] is False

    # 7. Promote release (atomic pointer swap)
    promote_res = await client.post(
        "/v1/admin/releases/REL-2026-001/promote",
        headers=publisher_headers,
    )
    assert promote_res.status_code == 200
    assert promote_res.json()["is_active"] is True

    # 8. Verify public release endpoint returns active release
    public_res = await client.get("/v1/knowledge/release")
    assert public_res.status_code == 200
    assert public_res.json()["release_id"] == "REL-2026-001"
    assert public_res.json()["is_active"] is True

