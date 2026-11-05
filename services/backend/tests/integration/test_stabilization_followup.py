"""Ebarki release follow-up: real rendering, session security and durable operations."""
import datetime
import io
import json
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image
from pypdf import PdfReader, PdfWriter

from app.admin.models import AdminRecord
from app.admin.service import AdminService
from app.core.config import settings
from app.core.security import decode_and_verify_jwt
from app.evidence.storage import LocalDiskStorageBackend
from app.identity.models import ActorRole
from app.operations import record_reader
from app.operations.visual_reader import prepare_image, render_pdf_page

FIXTURES = Path(__file__).resolve().parents[4] / 'docs/qa/fixtures'


async def account(client, label):
    payload = {'email': f'{label}-{uuid.uuid4().hex}@fictional.invalid',
               'password': 'Fictional-password-246!', 'full_name': 'Fictional Ebarki QA'}
    response = await client.post('/v1/auth/register', json=payload)
    assert response.status_code == 201
    data = response.json()
    return payload, data, {'Authorization': 'Bearer '+data['access_token']}


@pytest.mark.asyncio
async def test_bearer_logout_revokes_session_and_rejects_replay(client):
    _, data, headers = await account(client, 'logout')
    assert decode_and_verify_jwt(data['access_token'])['sid']
    assert (await client.get('/v1/auth/me', headers=headers)).status_code == 200
    assert (await client.post('/v1/auth/logout', headers=headers)).status_code == 200
    assert (await client.get('/v1/auth/me', headers=headers)).status_code == 401


@pytest.mark.asyncio
async def test_cookie_csrf_is_session_bound_and_origins_guard_login(client):
    guest = await client.post('/v1/auth/guest')
    token = guest.json()['csrf_token']
    body = {'title': 'Fictional cookie integrity check'}
    assert (await client.post('/v1/cases', json=body, headers={'X-CSRF-Token': 'anything'})).status_code == 403
    assert (await client.post('/v1/cases', json=body, headers={'X-CSRF-Token': token})).status_code == 201
    guest2 = await client.post('/v1/auth/guest')
    assert guest2.json()['csrf_token'] != token
    assert (await client.post('/v1/cases', json=body, headers={'X-CSRF-Token': token})).status_code == 403
    assert (await client.post('/v1/auth/guest', headers={'Origin': 'https://attacker.invalid'})).status_code == 403
    assert (await client.post('/v1/auth/login', headers={'Origin': 'null'}, json={'email': 'fake@fictional.invalid', 'password': 'fictional'})).status_code == 403
    assert guest.headers['cache-control'] == 'private, no-store'


@pytest.mark.asyncio
async def test_admin_entry_rejects_consumers_before_creating_cookie(client):
    payload, _data, _ = await account(client, 'consumer')
    client.cookies.clear()
    rejected = await client.post('/v1/auth/admin-login', json=payload)
    assert rejected.status_code == 403 and 'set-cookie' not in rejected.headers
    assert (await client.post('/v1/auth/login', json=payload)).status_code == 200


@pytest.mark.asyncio
async def test_durable_ban_revokes_access_and_unban_does_not_restore_old_session(client, db_session):
    payload, data, headers = await account(client, 'suspend')
    users = await AdminService.list_users(db_session)
    user = next(user for user in users if user['principal_id'] == str(data['principal_id']))
    result = await AdminService.toggle_user_ban(user['id'], 'fictional-reviewer', db_session)
    assert result['is_banned']
    assert (await db_session.get(AdminRecord, 'ban:'+str(data['principal_id']))).payload['banned']
    assert (await client.get('/v1/auth/me', headers=headers)).status_code in {401, 403}
    assert (await client.post('/v1/auth/login', json=payload)).status_code == 403
    await AdminService.toggle_user_ban(user['id'], 'fictional-reviewer', db_session)
    assert (await client.get('/v1/auth/me', headers=headers)).status_code == 401
    assert (await client.post('/v1/auth/login', json=payload)).status_code == 200


@pytest.mark.asyncio
async def test_alerts_audit_and_validation_are_durable_and_role_protected(client, db_session):
    _, data, headers = await account(client, 'admin')
    db_session.add(ActorRole(id=uuid.uuid4(), principal_id=uuid.UUID(data['principal_id']),
                            role='admin', grant_origin='synthetic_test', scope='global'))
    await db_session.commit()
    alert = {'title': 'Fictional QA alert', 'title_en': 'Fictional QA alert', 'message': 'Synthetic only', 'severity': 'info', 'active': False}
    assert (await client.post('/v1/admin/alerts', headers=headers, json=alert)).status_code == 200
    assert (await client.get('/v1/admin/alerts')).json() == []
    assert (await AdminService.list_alerts(db_session, active_only=False))[0]['title'] == alert['title']
    manage = (await client.get('/v1/admin/alerts/manage', headers=headers)).json()
    activated = await client.post('/v1/admin/alerts/'+manage[0]['id']+'/update', headers=headers,
                                   json={**alert, 'active': True})
    assert activated.status_code == 200
    assert len((await client.get('/v1/admin/alerts')).json()) == 1
    audit = (await client.get('/v1/admin/audit-logs', headers=headers)).json()
    assert audit[0]['action'] == 'UPDATE_PLATFORM_ALERT' and len(audit[0]['hash']) == 64
    assert (await client.post('/v1/admin/cases/'+str(uuid.uuid4())+'/override', headers=headers,
                              json={'new_status': 'invented_success'})).status_code == 422
    assert (await client.post('/v1/admin/merchants/fictional/override', headers=headers,
        json={'is_verified': False, 'is_blacklisted': False, 'risk_percent': 900, 'admin_note': 'fictional'})).status_code == 422
    # Unknown moderation targets must not produce success receipts.
    assert (await client.post('/v1/admin/community/posts/unknown/moderate', headers=headers, json={'action': 'hide'})).status_code == 404


def test_real_scan_render_and_margin_preparation():
    original = (FIXTURES/'scanned receipt.pdf').read_bytes()
    raster = render_pdf_page(original, 0)
    image, mapping = prepare_image(raster)
    with Image.open(io.BytesIO(image)) as rendered:
        assert rendered.width > 300 and rendered.height > 500
    assert mapping[2] > 0 and mapping[3] > 0  # Actual blank border was removed.


@pytest.mark.asyncio
async def test_scanned_pdf_consent_pages_and_partial_failures(monkeypatch):
    scan = PdfReader(FIXTURES/'scanned receipt.pdf')
    writer = PdfWriter()
    for _ in range(7):
        writer.add_page(scan.pages[0])
    buffer = io.BytesIO()
    writer.write(buffer)
    storage = SimpleNamespace(read_accepted=lambda path: buffer.getvalue())
    monkeypatch.setattr(record_reader, 'get_storage_backend', lambda: storage)
    monkeypatch.setattr(record_reader, 'vision_available', lambda: True)
    item = SimpleNamespace(id=uuid.uuid4(), detected_mime_type='application/pdf',
        original_filename='unhelpful 999999.pdf', sha256_hash='synthetic', accepted_path='ignored')
    calls = []

    async def visual(data, coordinates, page=1):
        calls.append(page)
        return {'lines': [{'text': 'Controlled provider double, not real OCR', 'page': page, 'box': None}],
                'method': 'groq_vision', 'model': 'test-double',
                'execution_receipt': {'provider': 'unit-double', 'request_id': 'unit-test'}}

    monkeypatch.setattr(record_reader, 'read_visual', visual)
    denied = await record_reader.read_evidence(item, False)
    assert denied['reason'] == 'external_consent_required' and not calls
    reading = await record_reader.read_evidence(item, True)
    assert calls == [1, 2, 3, 4, 5]
    assert reading['partial'] and reading['unread_pages'] == [6, 7]
    assert reading['reason'] == 'pdf_page_limit' and len(reading['execution_receipts']) == 5
    assert {line['page'] for line in reading['lines']} == {1, 2, 3, 4, 5}


def test_vault_rejects_paths_outside_configured_area(tmp_path):
    vault = LocalDiskStorageBackend(tmp_path/'vault')
    other = tmp_path/'unrelated.txt'
    other.write_text('Fictional unrelated file')
    with pytest.raises(PermissionError):
        vault.read_accepted(str(other))
    with pytest.raises(PermissionError):
        vault.delete_accepted(str(other))
    assert other.read_text() == 'Fictional unrelated file'


def test_curated_law_text_matches_primary_observation_and_rejects_fake_subsection():
    from app.retrieval.provision_service import ProvisionService
    observation = json.loads((FIXTURES.parent/'evidence/followup-laws.json').read_text(encoding='utf8'))
    sections = observation['checks'][0]['material_sections']
    for number, expected in sections.items():
        result = ProvisionService.lookup_exact_provision('crpa2009:sec:'+number)
        assert result.match_found and result.provision.canonical_text_bn == expected
        assert result.provision.official_url == observation['checks'][0]['url']
    assert not ProvisionService.lookup_exact_provision('crpa2009:sec:45(2)').match_found
    assert not ProvisionService.lookup_exact_provision('ধারা ৪৫(২)').match_found
    section = ProvisionService.lookup_exact_provision('sec:76(4)').provision
    assert 'কর্মকর্তা বা কর্মচারী' in section.qualifications_and_exceptions[0]


def test_source_check_dates_expire_and_deadline_does_not_invent_extension(monkeypatch):
    from app.knowledge import source_registry
    from app.policy.engine import ProceduralAssessmentEngine
    stale = source_registry.INITIAL_SOURCE_REGISTRY[0].model_copy(update={
        'last_checked_at': datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC),
        'health_status': 'current_check_passed'})
    monkeypatch.setattr(source_registry, 'INITIAL_SOURCE_REGISTRY', [stale])
    assert source_registry.get_source_by_id(stale.id).health_status == 'check_overdue'
    date = (datetime.datetime.now(datetime.UTC).date()-datetime.timedelta(days=50)).isoformat()
    en, _bn, remaining, uncertain = ProceduralAssessmentEngine.calculate_statutory_limitation({}, date)
    assert remaining is None and uncertain and 'assume an extension' in en
    assert 'condonation' not in en.lower()


def test_filing_preparation_rejects_unknown_channel_and_keeps_zero_amount():
    from app.actions.destinations import ComplaintDestinationService
    from app.actions.portal_field_maps import PortalFieldMapService
    with pytest.raises(ValueError):
        PortalFieldMapService.get_field_map('invented_channel', {}, {})
    prepared = PortalFieldMapService.get_field_map('dncrp_ccms', {}, {'amount_paid': 0})
    amount = next(field for field in prepared.fields if field.fact_source == 'amount_paid')
    assert amount.prepared_value == '0.00'
    for channel, destination in [('btrc_complaint', 'btrc_consumer_cell'), ('idra_grievance', 'idra_grievance_cell')]:
        assert PortalFieldMapService.get_field_map(channel, {}, {}).official_destination_url == ComplaintDestinationService.get_destination(destination).official_portal_url


@pytest.mark.asyncio
async def test_readiness_rejects_an_unconfigured_storage_adapter(client, monkeypatch):
    monkeypatch.setattr(settings, 'STORAGE_BACKEND', 'unconfigured-adapter')
    response = await client.get('/health/ready')
    assert response.status_code == 503
    assert response.json()['status'] == 'not_ready'


@pytest.mark.asyncio
async def test_role_changes_are_server_enforced_and_prevent_self_lockout_or_judge_privilege(client, db_session):
    _, admin, admin_headers = await account(client, 'role-admin')
    db_session.add(ActorRole(id=uuid.uuid4(), principal_id=uuid.UUID(admin['principal_id']),
                            role='admin', grant_origin='synthetic_test', scope='global'))
    await db_session.commit()
    _, consumer, consumer_headers = await account(client, 'role-consumer')
    users = (await client.get('/v1/admin/users', headers=admin_headers)).json()
    target = next(user for user in users if user['principal_id'] == consumer['principal_id'])
    own = next(user for user in users if user['principal_id'] == admin['principal_id'])
    route = '/v1/admin/users/'+target['id']+'/roles'
    assert (await client.post(route, headers=consumer_headers, json={'roles': ['admin']})).status_code == 403
    assert (await client.post(route, headers=admin_headers, json={'roles': ['consumer', 'reviewer']})).status_code == 200
    assert (await client.get('/v1/admin/source-candidates', headers=consumer_headers)).status_code == 200
    assert (await client.get('/v1/admin/users', headers=consumer_headers)).status_code == 403
    assert (await client.post(route, headers=admin_headers, json={'roles': ['consumer']})).status_code == 200
    assert (await client.get('/v1/admin/source-candidates', headers=consumer_headers)).status_code == 403
    assert (await client.post('/v1/admin/users/'+own['id']+'/roles', headers=admin_headers,
                              json={'roles': ['consumer']})).status_code == 400
    judge = (await client.post('/v1/auth/judge-demo')).json()
    users = (await client.get('/v1/admin/users', headers=admin_headers)).json()
    target = next(user for user in users if user['principal_id'] == judge['principal_id'])
    assert (await client.post('/v1/admin/users/'+target['id']+'/roles', headers=admin_headers,
                              json={'roles': ['consumer', 'admin']})).status_code == 400
