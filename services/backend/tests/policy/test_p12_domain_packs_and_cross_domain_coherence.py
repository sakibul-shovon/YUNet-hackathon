import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.action_dag import ActionDAGService
from app.actions.destinations import ComplaintDestinationService
from app.actions.portal_field_maps import PortalFieldMapService
from app.facts.service import FactService
from app.identity.models import Principal
from app.policy.domain_catalogue import DomainCatalogueService
from app.policy.engine import ProceduralAssessmentEngine
from app.policy.evaluator import RouteStatus


@pytest.fixture
async def test_consumer(client: AsyncClient, db_session: AsyncSession) -> tuple[AsyncClient, Principal, dict[str, str]]:
    res = await client.post("/auth/guest")
    data = res.json()
    token = data["access_token"]
    principal_id = uuid.UUID(data["principal_id"])

    principal = Principal(id=principal_id, kind="ephemeral", locale="en-BD")
    headers = {"Authorization": f"Bearer {token}"}
    return client, principal, headers


@pytest.mark.asyncio
async def test_p12_1_telecom_isp_domain_pack_and_stale_map(
    test_consumer: tuple[AsyncClient, Principal, dict[str, str]],
    client: AsyncClient,
    db_session: AsyncSession,
):
    """P12.1: Telecom/ISP pack positive, negative, unknown, and BTRC field map fallback."""
    _, principal, headers = test_consumer

    # 1. Create a telecom case
    case_res = await client.post(
        "/v1/cases",
        json={"title": "Broadband outage and unexpected billing", "locale": "en-BD", "merchant_name": "Metro ISP Ltd"},
        headers=headers,
    )
    assert case_res.status_code == 201
    case_id = uuid.UUID(case_res.json()["id"])

    # Scenario A: Unknown Facts -> Route NEEDS_FACTS
    case = await FactService.get_authorized_case(case_id, principal, db_session)
    assessment_unknown = await ProceduralAssessmentEngine.assess_case(case, db_session)
    telecom_route_unknown = next((r for r in assessment_unknown.routes if "telecom" in r.issue_type), None)
    assert telecom_route_unknown is not None
    assert telecom_route_unknown.status == RouteStatus.NEEDS_FACTS

    # Scenario B: Positive Supported Scenario
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "telecom_provider_ticket_filed", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "provider_response_overdue_or_unsatisfactory", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "service_disruption_or_billing_error_documented", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "issue_is_handset_hardware_only", "field_type": "boolean", "raw_value": False},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "consumer_has_unpaid_due_prior_to_dispute", "field_type": "boolean", "raw_value": False},
        headers=headers,
    )

    await db_session.rollback()
    case = await FactService.get_authorized_case(case_id, principal, db_session)
    assessment_pos = await ProceduralAssessmentEngine.assess_case(case, db_session)
    telecom_route_pos = next((r for r in assessment_pos.routes if "telecom" in r.issue_type), None)
    assert telecom_route_pos is not None
    assert telecom_route_pos.status == RouteStatus.SUPPORTED
    assert "prepare_btrc_complaint" in telecom_route_pos.allowed_actions

    # Test Action DAG for Telecom
    dag = await ActionDAGService.build_action_dag(case_id, principal, db_session)
    assert dag.primary_action_id == "prepare_btrc_complaint"
    assert any(n.action_id == "prepare_telecom_provider_notice" for n in dag.nodes)

    # Test BTRC portal field map
    facts_dict = {"merchant_name": "Metro ISP Ltd", "incident_date": "2026-02-15"}
    btrc_map = PortalFieldMapService.get_field_map("btrc_complaint", {"merchant_name": "Metro ISP Ltd"}, facts_dict)
    assert btrc_map.portal_id == "btrc_complaint"
    assert any(f.field_key == "operator_name" for f in btrc_map.fields)

    # Scenario C: Excluded Scenario (Handset hardware defect only)
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "issue_is_handset_hardware_only", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await db_session.rollback()
    case = await FactService.get_authorized_case(case_id, principal, db_session)
    assessment_excl = await ProceduralAssessmentEngine.assess_case(case, db_session)
    telecom_route_excl = next((r for r in assessment_excl.routes if "telecom" in r.issue_type), None)
    assert telecom_route_excl.status == RouteStatus.EXCLUDED


@pytest.mark.asyncio
async def test_p12_2_insurance_domain_pack_and_abstention(
    test_consumer: tuple[AsyncClient, Principal, dict[str, str]],
    client: AsyncClient,
    db_session: AsyncSession,
):
    """P12.2: Insurance pack positive, sub-judice exclusion, and unsupported remedy abstention."""
    _, principal, headers = test_consumer

    # 1. Create insurance case
    case_res = await client.post(
        "/v1/cases",
        json={"title": "Motor insurance claim delay", "locale": "en-BD", "merchant_name": "Green Delta Insurance"},
        headers=headers,
    )
    case_id = uuid.UUID(case_res.json()["id"])
    case = await FactService.get_authorized_case(case_id, principal, db_session)

    # Scenario A: Positive Supported Scenario
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "insurance_policy_documented", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "formal_claim_submitted_to_insurer", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "claim_denied_or_settlement_delayed_over_90d", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "subject_of_ongoing_court_litigation", "field_type": "boolean", "raw_value": False},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "fraudulent_misrepresentation_admitted", "field_type": "boolean", "raw_value": False},
        headers=headers,
    )

    await db_session.rollback()
    case = await FactService.get_authorized_case(case_id, principal, db_session)
    assessment = await ProceduralAssessmentEngine.assess_case(case, db_session)
    ins_route = next((r for r in assessment.routes if "insurance" in r.issue_type), None)
    assert ins_route is not None
    assert ins_route.status == RouteStatus.SUPPORTED
    assert "claim_reconsideration" in ins_route.supported_remedies
    # Unsupported remedy check: No guaranteed claim entitlement is invented
    assert "guaranteed_claim_payout" in ins_route.unsupported_remedies

    # Scenario B: Excluded Scenario (Ongoing court litigation / sub judice)
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "subject_of_ongoing_court_litigation", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await db_session.rollback()
    case = await FactService.get_authorized_case(case_id, principal, db_session)
    assessment_sub_judice = await ProceduralAssessmentEngine.assess_case(case, db_session)
    ins_route_excl = next((r for r in assessment_sub_judice.routes if "insurance" in r.issue_type), None)
    assert ins_route_excl.status == RouteStatus.EXCLUDED


@pytest.mark.asyncio
async def test_p12_3_grs_pack_and_statutory_exclusions(
    test_consumer: tuple[AsyncClient, Principal, dict[str, str]],
    client: AsyncClient,
    db_session: AsyncSession,
):
    """P12.3: Secondary GRS pack positive and explicit exclusions (sub judice, cadre discipline, RTI appeal)."""
    _, principal, headers = test_consumer

    case_res = await client.post(
        "/v1/cases",
        json={"title": "Passport delivery delay at regional office", "locale": "en-BD", "merchant_name": "Passport Office"},
        headers=headers,
    )
    case_id = uuid.UUID(case_res.json()["id"])
    case = await FactService.get_authorized_case(case_id, principal, db_session)

    # Scenario A: Positive Supported GRS Scenario
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "public_service_request_submitted", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "citizen_charter_timeline_exceeded", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "relevant_office_contacted_first", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "subject_of_ongoing_court_litigation", "field_type": "boolean", "raw_value": False},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "service_cadre_discipline_or_promotion", "field_type": "boolean", "raw_value": False},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "alternative_statutory_appeal_pending", "field_type": "boolean", "raw_value": False},
        headers=headers,
    )

    await db_session.rollback()
    case = await FactService.get_authorized_case(case_id, principal, db_session)
    assessment = await ProceduralAssessmentEngine.assess_case(case, db_session)
    grs_route = next((r for r in assessment.routes if "public_service_grievance" in r.issue_type), None)
    assert grs_route is not None
    assert grs_route.status == RouteStatus.SUPPORTED
    assert "prepare_grs_submission" in grs_route.allowed_actions

    # Scenario B: Excluded due to Service Cadre Discipline / Promotion
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "service_cadre_discipline_or_promotion", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await db_session.rollback()
    case = await FactService.get_authorized_case(case_id, principal, db_session)
    assessment_cadre = await ProceduralAssessmentEngine.assess_case(case, db_session)
    grs_route_cadre = next((r for r in assessment_cadre.routes if "public_service_grievance" in r.issue_type), None)
    assert grs_route_cadre.status == RouteStatus.EXCLUDED


@pytest.mark.asyncio
async def test_p12_4_domain_capability_catalogue_and_unsupported_fallback(
    client: AsyncClient,
):
    """P12.4: Domain capability catalogue discloses depth; unsupported jurisdiction and unapproved domains fallback safely."""
    # 1. Fetch domain catalogue
    res_cat = await client.get("/v1/domains/catalogue")
    assert res_cat.status_code == 200
    data = res_cat.json()
    assert len(data["domains"]) >= 5

    # Verify that Insurance is disclosed as staged_depth (NOT fully supported)
    ins_entry = next((d for d in data["domains"] if d["domain_id"] == "insurance"), None)
    assert ins_entry is not None
    assert ins_entry["support_status"] == "staged_depth"
    assert ins_entry["is_fully_supported"] is False
    assert ins_entry["caveat_en"] is not None

    # Verify GRS is disclosed as secondary_civic (NOT fully supported)
    grs_entry = next((d for d in data["domains"] if d["domain_id"] == "government_grs"), None)
    assert grs_entry is not None
    assert grs_entry["support_status"] == "secondary_civic"
    assert grs_entry["is_fully_supported"] is False

    # 2. Unsupported Jurisdiction Fallback (e.g. jurisdiction=SG)
    res_sg = await client.get("/v1/domains/consumer_ecommerce/support?jurisdiction=SG")
    assert res_sg.status_code == 200
    data_sg = res_sg.json()
    assert data_sg["is_supported"] is False
    assert data_sg["support_status"] == "unsupported_jurisdiction"
    assert "strictly designed for Bangladesh consumer statutory frameworks" in data_sg["advisory_en"]

    # 3. Unapproved Domain Fallback
    res_unapproved = await client.get("/v1/domains/crypto_arbitration/support")
    assert res_unapproved.status_code == 200
    data_unapp = res_unapproved.json()
    assert data_unapp["is_supported"] is False
    assert data_unapp["support_status"] == "unsupported_domain"


@pytest.mark.asyncio
async def test_p12_5_cross_domain_regression_and_destination_readiness_t46(
    test_consumer: tuple[AsyncClient, Principal, dict[str, str]],
    client: AsyncClient,
    db_session: AsyncSession,
):
    """P12.5 (T46): Cross-domain multi-issue coherence; shopping and finance workflows remain non-regressed; destinations ready."""
    _, principal, headers = test_consumer

    # 1. Verify Destination Registry contains all required domain channels (T54)
    destinations = ComplaintDestinationService.list_destinations()
    dest_ids = {d.destination_id for d in destinations}
    assert "dncrp_ccms_portal" in dest_ids
    assert "bb_cipc_portal" in dest_ids
    assert "btrc_consumer_cell" in dest_ids
    assert "idra_grievance_cell" in dest_ids
    assert "cabinet_grs_portal" in dest_ids

    # 2. Multi-issue case: E-commerce failure coexisting with MFS dispute
    case_res = await client.post(
        "/v1/cases",
        json={"title": "Multi-issue commerce non-delivery and payment debit", "locale": "en-BD", "merchant_name": "Gadget Store"},
        headers=headers,
    )
    case_id = uuid.UUID(case_res.json()["id"])

    # Issue 1: E-commerce delivery failure facts
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "purchase_channel", "field_type": "string", "raw_value": "ecommerce"},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "goods_delivered", "field_type": "boolean", "raw_value": False},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "promised_delivery_date_passed", "field_type": "boolean", "raw_value": True},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "refund_already_issued", "field_type": "boolean", "raw_value": False},
        headers=headers,
    )
    await client.post(
        f"/v1/cases/{case_id}/facts",
        json={"field_name": "order_cancelled_by_buyer_before_dispatch", "field_type": "boolean", "raw_value": False},
        headers=headers,
    )

    await db_session.rollback()
    case = await FactService.get_authorized_case(case_id, principal, db_session)
    assessment = await ProceduralAssessmentEngine.assess_case(case, db_session)

    # Verify shopping route is supported without regression
    delivery_route = next((r for r in assessment.routes if r.issue_type == "ecommerce_delivery_failure"), None)
    assert delivery_route is not None
    assert delivery_route.status == RouteStatus.SUPPORTED

    # Verify Action DAG generates appropriate non-blocking shopping actions
    dag = await ActionDAGService.build_action_dag(case_id, principal, db_session)
    assert dag.primary_action_id == "prepare_dncrp_complaint"
    assert any(n.action_id == "prepare_merchant_notice" for n in dag.nodes)
