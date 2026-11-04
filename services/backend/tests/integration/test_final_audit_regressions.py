"""Ebarki release defects: privacy, source grounding, genuine failures and review."""
import io
import uuid
from pathlib import Path

import httpx
import pytest

from app.core.config import Settings, settings
from app.extraction.adapter import CaseExtractor
from app.operations.understanding import understand_situation

FIXTURES = Path(__file__).resolve().parents[4]/'docs/qa/fixtures'


async def setup_case(client):
    client.cookies.clear()
    auth = (await client.post('/auth/guest')).json()
    headers = {'Authorization': 'Bearer '+auth['access_token']}
    case = (await client.post('/v1/cases', headers=headers, json={
        'title': 'Ebarki fictional QA kettle', 'merchant_name': 'Fictional Padma Test Shop',
        'story_narrative': 'Fictional QA. Paid BDT 7,321.50 on 2026-10-24. Product not delivered.',
    })).json()
    return '/v1/cases/'+case['id'], headers


async def upload(client, base, headers, name):
    data = (FIXTURES/name).read_bytes()
    intent = (await client.post('/v1/uploads/init', headers=headers, json={
        'case_id': base.split('/')[-1], 'declared_filename': name,
        'declared_mime_type': 'application/pdf', 'declared_byte_size': len(data),
    })).json()
    await client.put('/v1/uploads/'+intent['intent_id']+'/raw', headers=headers,
                     params={'token': intent['upload_token']}, content=data)
    response = await client.post('/v1/uploads/'+intent['intent_id']+'/complete', headers=headers)
    assert response.status_code == 200
    return response.json()


async def records(client, base, headers):
    return (await client.get(base+'/connected-records', headers=headers)).json()


@pytest.mark.asyncio
async def test_unrelated_pdf_stays_out_until_human_review_and_reopen_removes_it(client):
    base, owner = await setup_case(client)
    await upload(client, base, owner, 'unrelated groceries.pdf')
    await upload(client, base, owner, 'receipt text.pdf')
    await upload(client, base, owner, 'duplicate নাম 99999.pdf')
    await client.post(base+'/runs', headers=owner, json={'operation': 'resolve'})
    ledger = (await client.get(base+'/evidence/reconciliation', headers=owner)).json()
    assert ledger['linked_evidence_total_minor_units'] == 0
    data = await records(client, base, owner)
    source = next(s for s in data['sources'] if s['filename'] == 'receipt text.pdf')
    moment = next(m for m in data['timeline'] if m['source_id'] == source['id'] and m['kind'] == 'payment')
    for outcome, expected in [('confirmed', 700000), ('proposed', 0), ('confirmed', 700000), ('dismissed', 0)]:
        data = await records(client, base, owner)
        review = await client.post(base+'/connected-records/review', headers=owner, json={
            'item_id': moment['id'], 'outcome': outcome, 'expected_version': data['case_version']})
        assert review.status_code == 200
        ledger = (await client.get(base+'/evidence/reconciliation', headers=owner)).json()
        assert ledger['linked_evidence_total_minor_units'] == expected
        assert all(i['filename'] != 'unrelated groceries.pdf' for i in ledger['reconciled_items'])


@pytest.mark.asyncio
async def test_merchant_public_endpoint_never_exposes_private_case(client):
    base, owner = await setup_case(client)
    client.cookies.clear()
    data = (await client.get('/v1/merchants/intelligence?query=Fictional')).json()
    assert data['recent_complaints'] == [] and data['complaint_count'] == 0
    assert base.split('/')[-1] not in str(data)
    assert data['total_disputed_bdt'] == 0 and not data['is_known_offender']
    radar = (await client.get('/v1/merchants/radar')).json()
    assert radar['top_offenders'] == [] and radar['total_tracked_merchants'] == 0
    assert (await client.get('/v1/community/posts')).json() == []
    public = await client.post('/v1/community/posts', json={
        'title': 'Fictional test', 'story': 'Fictional content', 'category': 'Retail',
        'merchant_name': 'Fictional', 'disputed_amount_bdt': 1})
    assert public.status_code == 503


@pytest.mark.asyncio
async def test_legacy_global_demo_ids_do_not_bypass_owner_checks(client):
    _, stranger = await setup_case(client)
    base = '/v1/cases/1887c4ed-99d6-44f2-9fb4-0c15e9d3287e'
    for suffix in ['', '/facts', '/evidence', '/activity']:
        assert (await client.get(base+suffix, headers=stranger)).status_code == 404


@pytest.mark.parametrize('text,expected', [
    ('Fictional paid on 2026-10-24. Seller will refund tomorrow.', '2026-10-24'),
    ('Fictional paid on ২৪/১০/২০২৬.', '2026-10-24'),
    ('Fictional seller will refund tomorrow.', None),
])
def test_date_extraction_does_not_reinterpret_refund_promise_as_incident(text, expected):
    dates = [p for p in CaseExtractor.propose(text).proposals if p.field_name == 'incident_date']
    assert ([p.raw_value for p in dates] == [expected]) if expected else not dates


@pytest.mark.asyncio
async def test_unicode_preview_and_derivative_deletion(client):
    base, owner = await setup_case(client)
    file = await upload(client, base, owner, 'duplicate নাম 99999.pdf')
    preview = await client.get(base+'/evidence/'+file['id']+'/preview', headers=owner)
    assert preview.status_code == 200 and preview.content.startswith(b'%PDF')
    assert 'filename*=UTF-8' in preview.headers['content-disposition']
    source = await client.post(base+'/connected-records/sources', headers=owner, json={
        'text': 'Fictional Seller: We will refund tomorrow PRIVATE_QA_DERIVATIVE.',
        'label': 'Fictional transcript', 'source_type': 'manual_transcript', 'evidence_id': file['id'],
        'expected_version': (await records(client, base, owner))['case_version']})
    assert source.status_code == 201
    data = await records(client, base, owner)
    moment = next(m for m in data['timeline'] if m['source_id'] == source.json()['id'])
    await client.post(base+'/connected-records/review', headers=owner, json={
        'item_id': moment['id'], 'outcome': 'confirmed', 'expected_version': data['case_version']})
    doc = (await client.get(base+'/documents/ast', headers=owner)).json()
    assert 'PRIVATE_QA_DERIVATIVE' in str(doc)
    assert (await client.delete(base+'/evidence/'+file['id'], headers=owner)).status_code == 200
    assert (await client.get(base+'/evidence/'+file['id']+'/preview', headers=owner)).status_code == 404
    assert (await client.get(base+'/documents/versions/'+doc['document_id'], headers=owner)).status_code == 404
    events = (await client.get(base+'/activity', headers=owner)).json()
    assert 'PRIVATE_QA_DERIVATIVE' not in str(events)
    assert 'PRIVATE_QA_DERIVATIVE' not in str(await records(client, base, owner))


@pytest.mark.parametrize('status', [401, 429, 500])
@pytest.mark.asyncio
async def test_real_summary_provider_errors_are_truthful(monkeypatch, status):
    monkeypatch.setattr(settings, 'GROQ_API_KEY', 'fictional-test-key-not-a-credential')
    class Client:
        def __init__(self, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def post(self, url, **kwargs):
            return httpx.Response(status, request=httpx.Request('POST', url), json={})
    monkeypatch.setattr('app.operations.understanding.httpx.AsyncClient', Client)
    out = await understand_situation('Fictional paid BDT 432.10.', 'en')
    assert not out['model_executed'] and out['provider_unavailable']
    assert out['summary'] == 'Fictional paid BDT 432.10.'


def test_production_rejects_published_development_signing_keys():
    with pytest.raises(ValueError, match='production requires'):
        Settings(APP_ENV='production', _env_file=None)


@pytest.mark.asyncio
async def test_admin_metrics_do_not_estimate_money_or_invent_health(client, db_session):
    from app.admin.service import AdminService
    base, owner = await setup_case(client)
    await client.post(base+'/facts', headers=owner, json={
        'field_name': 'amount_paid', 'field_type': 'money', 'raw_value': 'BDT 7321.50'})
    stats = await AdminService.get_overview_stats(db_session)
    assert stats['metrics']['total_disputed_bdt'] == 7321.50
    assert stats['metrics']['total_recovered_bdt'] is None
    assert stats['resolution_paths_distribution'] == {}
    assert '99.98' not in str(stats) and 'Tesseract' not in str(stats)
    result = await AdminService.override_case_status(uuid.UUID(base.split('/')[-1]), 'active',
        'Fictional administrative QA only.', 'fictional-admin@example.invalid', db_session)
    assert result['success']
    events = (await client.get(base+'/activity', headers=owner)).json()
    assert events[-1]['event_type'] == 'ADMIN_STATUS_OVERRIDE'
    assert len({event['event_sequence'] for event in events}) == len(events)


@pytest.mark.asyncio
async def test_minimal_draft_has_no_invented_transaction_or_entitlement(client):
    base, owner = await setup_case(client)
    doc = (await client.get(base+'/documents/ast', headers=owner)).json()
    assert doc['template_version'] == 2
    assert not any(s['statement_type'] == 'statutory_basis' or s['supporting_citation']
                   for section in doc['sections'] for s in section['sentences'])
    assert all(s['statement_type'] != 'reviewed_fact' for section in doc['sections'] for s in section['sentences'])
    wording = ' '.join(s['text'] for section in doc['sections'] for s in section['sentences'])
    assert '2026-10-24' in wording
    assert 'unilaterally breached' not in wording and 'Immediate full reimbursement' not in wording


@pytest.mark.asyncio
async def test_retired_document_cannot_be_reused_as_current(client, db_session):
    from sqlalchemy import select
    from app.actions.document_store import PreparedDocument
    base, owner = await setup_case(client)
    before = (await client.get(base+'/documents/ast', headers=owner)).json()
    row = await db_session.scalar(select(PreparedDocument).where(PreparedDocument.id == uuid.UUID(before['document_id'])))
    row.content = {key: value for key, value in row.content.items() if key != 'template_version'}
    await db_session.commit()
    assert (await client.get(base+'/documents/versions/'+before['document_id'], headers=owner)).status_code == 409
    fresh = (await client.get(base+'/documents/ast', headers=owner)).json()
    assert fresh['document_id'] != before['document_id'] and fresh['template_version'] == 2


@pytest.mark.parametrize('failure', ['timeout', 'malformed'])
@pytest.mark.asyncio
async def test_summary_timeout_or_malformed_response_keeps_original(monkeypatch, failure):
    monkeypatch.setattr(settings, 'GROQ_API_KEY', 'fictional-test-key-not-a-credential')
    class Client:
        def __init__(self, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def post(self, url, **kwargs):
            if failure == 'timeout':
                raise httpx.ReadTimeout('Synthetic timeout')
            return httpx.Response(200, request=httpx.Request('POST', url),
                                  json={'choices':[{'message':{'content':'not JSON'}}]})
    monkeypatch.setattr('app.operations.understanding.httpx.AsyncClient', Client)
    original = 'Fictional paid BDT 432.10.'
    out = await understand_situation(original, 'bn')
    assert out['summary'] == original and not out['model_executed'] and out['provider_unavailable']
