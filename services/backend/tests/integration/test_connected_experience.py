import io
import uuid
from types import SimpleNamespace

import httpx
import pytest
from PIL import Image, ImageDraw

from app.core.config import settings
from app.operations.connected_records import chronology, source_date
from app.operations.record_reader import read_evidence


async def guest_case(client):
    client.cookies.clear()
    guest = (await client.post('/auth/guest')).json()
    headers = {'Authorization': f'Bearer {guest["access_token"]}'}
    case = (await client.post('/v1/cases', headers=headers, json={
        'title': 'My undelivered order', 'story_narrative': 'I paid BDT 5,500. The phone has not arrived.',
        'merchant_name': 'Example seller',
    })).json()
    return case, headers


@pytest.mark.asyncio
async def test_connected_story_links_real_pdf_and_private_page_preview(client):
    judge = (await client.post('/v1/auth/judge-demo')).json()
    headers = {'Authorization': f'Bearer {judge["access_token"]}'}
    base = f'/v1/cases/{judge["demo_case_id"]}'
    started = await client.post(base+'/runs', headers=headers, json={'operation': 'resolve'})
    assert started.status_code == 202
    records = await client.get(base+'/connected-records', headers=headers)
    assert records.status_code == 200 and 'no-store' in records.headers['cache-control']
    data = records.json()
    pdf = next(source for source in data['sources'] if source['method'] == 'native_pdf')
    assert '5,000' in pdf['text'] and pdf['lines']
    assert not pdf['model_executed']
    moment = next(item for item in data['timeline'] if item['source_id'] == pdf['id'] and item['kind'] == 'payment')
    assert moment['box'] and moment['page'] == 1 and moment['review'] == 'proposed'
    assert any(item['kind'] == 'promise' for item in data['timeline'])
    image = await client.get(base+f'/evidence/{pdf["id"]}/page-preview?page=1', headers=headers)
    assert image.status_code == 200 and image.headers['content-type'] == 'image/png'
    assert image.content.startswith(b'\x89PNG')
    with Image.open(io.BytesIO(image.content)) as rendered:
        assert rendered.width > 300 and rendered.height > 300
    assert (await client.get(base+f'/evidence/{pdf["id"]}/page-preview?page=999', headers=headers)).status_code == 404


@pytest.mark.asyncio
async def test_reviewed_moments_survive_reload_and_ground_new_draft_versions(client):
    case, headers = await guest_case(client)
    base = f'/v1/cases/{case["id"]}'
    source = await client.post(base+'/connected-records/sources', headers=headers, json={
        'text': '21 October Seller: We will deliver the phone tomorrow.',
        'label': 'My conversation', 'expected_version': case['row_version'],
    })
    assert source.status_code == 201
    data = (await client.get(base+'/connected-records', headers=headers)).json()
    moment = next(item for item in data['timeline'] if item['source_id'] == source.json()['id'])
    assert moment['occurred_on'] is None  # No guessed year or relative-date resolution.
    old = (await client.get(base+'/documents/ast?locale=en', headers=headers)).json()
    review = await client.post(base+'/connected-records/review', headers=headers, json={
        'item_id': moment['id'], 'outcome': 'confirmed', 'corrected_date': '2026-10-21',
        'expected_version': data['case_version'],
    })
    assert review.status_code == 200
    after = (await client.get(base+'/connected-records', headers=headers)).json()
    current = next(item for item in after['timeline'] if item['id'] == moment['id'])
    assert current['review'] == 'confirmed' and current['date_origin'] == 'user_correction'
    assert current['occurred_on'] == '2026-10-21' and current['quote'] == moment['quote']
    assert after['document']['is_stale']
    stale = await client.post(base+'/export/pdf', headers=headers, params={
        'document_id': old['document_id'], 'expected_case_version': old['case_version'],
    })
    assert stale.status_code == 409
    document = (await client.get(base+'/documents/ast?locale=en', headers=headers)).json()
    section = next(section for section in document['sections'] if section['section_id'] == 'reviewed_chronology')
    sentence = section['sentences'][0]
    assert sentence['supporting_record']['source_id'] == source.json()['id']
    assert sentence['statement_type'] == 'user_allegation'
    edited = (await client.post(base+'/documents/edit', headers=headers, json={
        'document_type': 'dncrp_ccms_complaint', 'locale': 'en', 'section_id': section['section_id'],
        'sentence_id': sentence['sentence_id'], 'new_text': 'My updated wording.', 'expected_revision': document['revision'],
    })).json()
    edited_sentence = next(section for section in edited['sections'] if section['section_id'] == 'reviewed_chronology')['sentences'][0]
    assert edited_sentence['supporting_record'] is None and edited_sentence['is_user_edited']
    assert (await client.get(base+'/documents/versions/'+old['document_id'], headers=headers)).json() == old


@pytest.mark.asyncio
async def test_replies_are_persisted_editable_and_never_sent(client):
    case, headers = await guest_case(client)
    base = f'/v1/cases/{case["id"]}'
    response = await client.post(base+'/reply-preparations', headers=headers, json={
        'message': 'The seal was opened. Please read our return policy.', 'locale': 'bn',
        'expected_version': case['row_version'],
    })
    assert response.status_code == 201, response.text
    reply = response.json()
    assert not reply['is_sent'] and reply['requires_review'] and reply['questions']
    assert reply['source_id']
    saved = (await client.get(base+'/reply-preparations', headers=headers)).json()
    assert saved[0]['id'] == reply['id'] and saved[0]['draft'] == reply['draft']
    edited = await client.put(base+'/reply-preparations/'+reply['id'], headers=headers,
        json={'draft': 'Please share the original return terms in writing.', 'expected_version': reply['case_version']})
    assert edited.status_code == 200 and edited.json()['user_edited']
    saved = (await client.get(base+'/reply-preparations', headers=headers)).json()
    assert saved[0]['draft'] == edited.json()['draft'] and not saved[0]['is_sent']
    assert len(saved) == 1
    records = (await client.get(base+'/connected-records', headers=headers)).json()
    assert any(source['id'] == reply['source_id'] for source in records['sources'])


@pytest.mark.asyncio
async def test_private_workbench_never_leaks_to_another_principal(client):
    case, owner = await guest_case(client)
    base = f'/v1/cases/{case["id"]}'
    reply = (await client.post(base+'/reply-preparations', headers=owner,
        json={'message': 'Please check the original order.', 'expected_version': case['row_version']})).json()
    _, stranger = await guest_case(client)
    for path in ['/connected-records', '/reply-preparations', '/filing-handoff']:
        assert (await client.get(base+path, headers=stranger)).status_code == 404
    assert (await client.post(base+'/connected-records/sources', headers=stranger,
        json={'text': 'Some private content.', 'expected_version': 1})).status_code == 404
    assert (await client.put(base+'/reply-preparations/'+reply['id'], headers=stranger,
        json={'draft': 'Unauthorized update.', 'expected_version': 1})).status_code == 404


@pytest.mark.asyncio
async def test_handoff_has_missing_fields_and_no_submission_claim(client):
    case, headers = await guest_case(client)
    response = await client.get(f'/v1/cases/{case["id"]}/filing-handoff', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data['official_destination_url'] == 'https://dncrp.com/'
    assert data['is_submitted'] is False
    assert any(field['required'] and not field['prepared_value'] for field in data['fields'])
    assert 'password' not in ' '.join(field['field_key'] for field in data['fields'])


@pytest.mark.asyncio
async def test_change_preview_uses_version_guard_and_preserves_poisha(client):
    case, headers = await guest_case(client)
    base = f'/v1/cases/{case["id"]}'
    preview = (await client.post(base+'/what-if', headers=headers, json={'overrides': {'amount_paid': 550025}})).json()
    assert preview['case_version'] == case['row_version']
    assert (await client.get(base, headers=headers)).json()['row_version'] == case['row_version']
    applied = await client.post(base+'/what-if/apply', headers=headers, json={
        'overrides': {'amount_paid': 550025}, 'expected_version': preview['case_version'],
    })
    assert applied.status_code == 200
    assert applied.json()[0]['typed_value']['minor_units'] == 550025
    stale = await client.post(base+'/what-if/apply', headers=headers, json={
        'overrides': {'goods_delivered': True}, 'expected_version': preview['case_version'],
    })
    assert stale.status_code == 409
    facts = (await client.get(base+'/facts', headers=headers)).json()
    assert facts[0]['review_outcome'] == 'accepted'


def test_dates_and_chronology_do_not_invent_missing_context():
    assert source_date('২১ অক্টোবর ২০২৬ Seller: Hello') == '2026-10-21'
    assert source_date('21 October: tomorrow morning') is None
    assert source_date('2026-02-31') is None
    items = chronology([{'id': 'source', 'method': 'pasted_message', 'text': 'Seller: We will deliver tomorrow.'}])
    assert items[0]['occurred_on'] is None and items[0]['requires_date_review']
    assert items[0]['review'] == 'proposed'


@pytest.mark.asyncio
async def test_visual_reading_requires_consent_and_keeps_proposed_coordinates(monkeypatch):
    from app.operations import record_reader

    calls = []
    class Client:
        def __init__(self, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return None
        async def post(self, url, **kwargs):
            calls.append(kwargs)
            return httpx.Response(200, json={'candidates': [{'content': {'parts': [{'text': '{"lines":[{"text":"BDT 5,000","box":[100,200,500,260]}]}'}]}}]}, request=httpx.Request('POST', url))
    item = SimpleNamespace(id=uuid.uuid4(), detected_mime_type='image/png', original_filename='untrusted_999999.png', declared_mime_type='image/png', accepted_path='test', sha256_hash='actual-digest')
    monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test-key')
    monkeypatch.setattr(settings, 'GEMINI_RECORD_READER_MODEL', 'test-vision-model')
    buffer = io.BytesIO()
    image = Image.new('RGB', (400, 400), 'white')
    ImageDraw.Draw(image).rectangle((80, 100, 319, 299), fill='black')
    image.save(buffer, format='PNG')
    monkeypatch.setattr(record_reader, 'get_storage_backend', lambda: SimpleNamespace(read_accepted=lambda path: buffer.getvalue()))
    monkeypatch.setattr(record_reader.httpx, 'AsyncClient', Client)
    denied = await read_evidence(item, False)
    assert denied['method'] == 'manual_required' and not calls
    result = await read_evidence(item, True)
    assert result['model_executed'] and result['text'] == 'BDT 5,000'
    assert result['lines'][0]['box'] == pytest.approx([.212, .314, .5, .3512])
    assert '999999' not in result['text']
    assert calls[0]['json']['contents'][0]['parts'][1]['inline_data']['mime_type'] == 'image/png'


@pytest.mark.asyncio
async def test_reading_reuse_preserves_review_and_removal_purges_derivatives(client, monkeypatch):
    from app.operations import runs
    case, headers = await guest_case(client)
    base = f'/v1/cases/{case["id"]}'
    await client.post(base+'/facts', headers=headers, json={'field_name': 'amount_paid',
        'field_type': 'money', 'raw_value': 'BDT 5,500.25'})
    await client.post('/v1/consents', headers=headers, json={'case_id': case['id'],
        'purpose': 'external_ai_processing', 'policy_version': '1.0', 'affirmative_action': 'test'})
    buffer = io.BytesIO()
    Image.new('RGB', (400, 400), 'white').save(buffer, format='PNG')
    data = buffer.getvalue()
    intent = (await client.post('/v1/uploads/init', headers=headers, json={'case_id': case['id'],
        'declared_filename': 'untrusted_999999.png', 'declared_mime_type': 'image/png',
        'declared_byte_size': len(data)})).json()
    await client.put(f'/v1/uploads/{intent["intent_id"]}/raw?token={intent["upload_token"]}', content=data)
    assert (await client.post(f'/v1/uploads/{intent["intent_id"]}/complete', headers=headers)).json()['status'] == 'accepted'
    calls = []
    async def mock_read(item, consent):
        assert consent
        calls.append(item.id)
        return {'id': str(item.id), 'sha256': item.sha256_hash, 'filename': item.original_filename,
            'mime_type': 'image/png', 'method': 'groq_vision', 'model_executed': True, 'reader_version': 2,
            'text': 'Paid BDT 5,000.25', 'lines': [{'text': 'Paid BDT 5,000.25', 'page': 1, 'box': [.1, .2, .8, .3]}]}
    monkeypatch.setattr(runs, 'read_evidence', mock_read)
    await client.post(base+'/runs', headers=headers, json={'operation': 'resolve'})
    records = (await client.get(base+'/connected-records', headers=headers)).json()
    moment = next(m for m in records['timeline'] if m['source_id'] == intent['intent_id'])
    assert (await client.post(base+'/connected-records/review', headers=headers, json={
        'item_id': moment['id'], 'outcome': 'confirmed', 'expected_version': records['case_version']})).status_code == 200
    await client.post(base+'/runs', headers=headers, json={'operation': 'resolve'})
    again = (await client.get(base+'/connected-records', headers=headers)).json()
    assert len(calls) == 1
    assert next(m for m in again['timeline'] if m['id'] == moment['id'])['review'] == 'confirmed'
    ledger = (await client.get(base+'/evidence/reconciliation', headers=headers)).json()
    assert ledger['linked_evidence_total_minor_units'] == 500025
    assert ledger['discrepancy_minor_units'] == 50000
    assert (await client.delete(base+'/evidence/'+intent['intent_id'], headers=headers)).status_code == 200
    for run in (await client.get(base+'/runs', headers=headers)).json():
        assert not any(r['id'] == intent['intent_id'] for r in run['result'].get('readings', []))
    after = (await client.get(base+'/connected-records', headers=headers)).json()
    assert not any(s['id'] == intent['intent_id'] for s in after['sources'])
