import io
import uuid

import pytest
from pypdf import PdfReader

from app.evidence.document_parser import DocumentParser


@pytest.mark.asyncio
async def test_judge_workspaces_are_isolated_and_have_real_evidence(client):
    first = (await client.post('/v1/auth/judge-demo')).json()
    assert first['roles'] == ['consumer']
    case_id = first['demo_case_id']
    headers = {'Authorization': f'Bearer {first["access_token"]}'}
    base = f'/v1/cases/{case_id}'
    files = (await client.get(base+'/evidence', headers=headers)).json()
    assert len(files) == 1 and files[0]['declared_mime_type'] == 'application/pdf'
    preview = await client.get(base+'/evidence/'+files[0]['id']+'/preview', headers=headers)
    assert '5,000' in ''.join(page.extract_text() for page in PdfReader(io.BytesIO(preview.content)).pages)
    assert 'FICTIONAL' in ''.join(page.extract_text() for page in PdfReader(io.BytesIO(preview.content)).pages)
    before = (await client.get(base+'/evidence/reconciliation', headers=headers)).json()
    assert before['discrepancy_minor_units'] == 50000
    started = await client.post(base+'/runs', headers=headers, json={'operation':'resolve','locale':'en'})
    assert started.status_code == 202
    run = (await client.get(base+'/runs/'+started.json()['id'], headers=headers)).json()
    assert run['status'] == 'needs_review', run
    assert [s['stage_name'] for s in run['stages']] == ['case_understanding','text_extraction','evidence_review','payment_reconciliation','source_retrieval','procedural_assessment']
    assert run['result']['reconciliation']['discrepancy_minor_units'] == 50000
    assert all(event['id'] for event in run['events'])
    assert len({event['id'] for event in run['events']}) == len(run['events'])
    assert run['events'][-1]['type']=='input.required'
    assert (await client.post(base+'/sample-payment', headers=headers)).status_code == 200
    assert (await client.post(base+'/sample-payment', headers=headers)).status_code == 200
    after = (await client.get(base+'/evidence/reconciliation', headers=headers)).json()
    assert after['linked_evidence_total_minor_units']==550000 and after['is_reconciled']
    assert len((await client.get(base+'/evidence', headers=headers)).json())==2
    facts=(await client.get(base+'/facts', headers=headers)).json()
    amount=next(f for f in facts if f['field_name']=='amount_paid')
    lens=await client.get(base+'/facts/'+amount['id']+'/provenance', headers=headers)
    assert 'no-store' in lens.headers['cache-control']
    assert len(lens.json()['links'])>=2
    assert all(link['evidence']['id'] for link in lens.json()['links'])
    client.cookies.clear()
    second=(await client.post('/v1/auth/judge-demo')).json()
    assert first['principal_id'] != second['principal_id']
    assert first['demo_case_id'] != second['demo_case_id']
    other={'Authorization': f'Bearer {second["access_token"]}'}
    assert (await client.get(base+'/facts/'+amount['id']+'/provenance', headers=other)).status_code==404
    assert (await client.post(base+'/sample-payment', headers=other)).status_code==404


@pytest.mark.asyncio
async def test_real_case_cannot_add_sample_evidence_and_stale_runs_are_rejected(client):
    boot=(await client.post('/auth/guest')).json()
    headers={'Authorization': f'Bearer {boot["access_token"]}'}
    case=(await client.post('/v1/cases',headers=headers,json={'title':'My actual order','story_narrative':'The order did not arrive.'})).json()
    base=f'/v1/cases/{case["id"]}'
    assert (await client.post(base+'/sample-payment',headers=headers)).status_code==404
    response=await client.post(base+'/runs',headers=headers,json={'operation':'resolve','expected_version':case['row_version']+1})
    assert response.status_code==409


@pytest.mark.asyncio
async def test_draft_run_creates_a_saved_reviewable_artifact(client):
    boot=(await client.post('/auth/guest')).json()
    headers={'Authorization': f'Bearer {boot["access_token"]}'}
    case=(await client.post('/v1/cases',headers=headers,json={'title':'Draft my request','story_narrative':'The order has not arrived.'})).json()
    base=f'/v1/cases/{case["id"]}'
    started=await client.post(base+'/runs',headers=headers,json={'operation':'draft','locale':'bn'})
    run=(await client.get(base+'/runs/'+started.json()['id'],headers=headers)).json()
    assert run['status']=='completed'
    document=run['result']['document']
    assert document['locale']=='bn' and not document['is_filed']
    saved=(await client.get(base+'/documents/versions/'+document['document_id'],headers=headers)).json()
    assert saved==document


def test_image_metadata_never_becomes_a_payment_finding():
    from PIL import Image

    image = io.BytesIO()
    Image.new('RGB', (120, 240), 'white').save(image, format='PNG')
    parsed = DocumentParser.parse_image_bytes(uuid.uuid4(), image.getvalue(), 'bkash_trxid_5000.png')
    assert parsed.regions == []
    assert not parsed.ocr_applied and not parsed.has_native_text
    assert parsed.full_text == ''
    assert 'IMAGE_REQUIRES_MANUAL_REVIEW' in parsed.quality_flags


@pytest.mark.asyncio
async def test_a_cancelled_run_does_not_start_any_tool(client, db_session):
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from app.identity.models import Principal
    from app.operations.runs import RunRequest, create_run, execute_run

    boot = (await client.post('/auth/guest')).json()
    headers = {'Authorization': f'Bearer {boot["access_token"]}'}
    case = (await client.post('/v1/cases', headers=headers, json={'title': 'Stop before processing', 'story_narrative': 'My order has not arrived.'})).json()
    principal = await db_session.get(Principal, uuid.UUID(boot['principal_id']))
    run = await create_run(uuid.UUID(case['id']), RunRequest(operation='resolve'), principal, db_session)
    cancelled = await client.post(f'/v1/cases/{case["id"]}/runs/{run.id}/cancel', headers=headers)
    assert cancelled.json()['cancel_requested']
    await execute_run(run.id, async_sessionmaker(db_session.bind, expire_on_commit=False))
    result = (await client.get(f'/v1/cases/{case["id"]}/runs/{run.id}', headers=headers)).json()
    assert result['status'] == 'cancelled'
    assert result['stages'] == []


@pytest.mark.asyncio
async def test_failed_tools_are_visible_and_the_case_can_be_retried(client, monkeypatch):
    from app.extraction.adapter import CaseExtractor

    boot = (await client.post('/auth/guest')).json()
    headers = {'Authorization': f'Bearer {boot["access_token"]}'}
    case = (await client.post('/v1/cases', headers=headers, json={'title': 'A retryable case', 'story_narrative': 'My order has not arrived.'})).json()
    base = f'/v1/cases/{case["id"]}/runs'
    with monkeypatch.context() as patch:
        def fail(_story):
            raise ValueError('test tool failure')
        patch.setattr(CaseExtractor, 'propose', fail)
        started = await client.post(base, headers=headers, json={'operation': 'resolve'})
        run = (await client.get(base+'/'+started.json()['id'], headers=headers)).json()
        assert run['status'] == 'failed' and run['error_code'] == 'operation_failed'
        assert run['stages'][-1]['status'] == 'failed'
    retry = await client.post(base, headers=headers, json={'operation': 'resolve'})
    result = (await client.get(base+'/'+retry.json()['id'], headers=headers)).json()
    assert result['status'] == 'needs_review'


@pytest.mark.asyncio
async def test_interrupted_runs_expire_without_losing_case_work(client, db_session):
    import datetime

    from app.identity.models import Principal
    from app.operations.runs import RunRequest, create_run

    boot = (await client.post('/auth/guest')).json()
    headers = {'Authorization': f'Bearer {boot["access_token"]}'}
    case = (await client.post('/v1/cases', headers=headers, json={'title': 'Recover interrupted work', 'story_narrative': 'The order has not arrived.'})).json()
    principal = await db_session.get(Principal, uuid.UUID(boot['principal_id']))
    run = await create_run(uuid.UUID(case['id']), RunRequest(operation='resolve'), principal, db_session)
    run.created_at = datetime.datetime.now(datetime.UTC)-datetime.timedelta(minutes=16)
    await db_session.commit()
    base = f'/v1/cases/{case["id"]}/runs'
    recovered = (await client.get(base, headers=headers)).json()[0]
    assert recovered['status'] == 'failed'
    assert recovered['error_code'] == 'operation_interrupted'
    restarted = await client.post(base, headers=headers, json={'operation': 'resolve'})
    assert restarted.status_code == 202
    assert (await client.get(base+'/'+restarted.json()['id'], headers=headers)).json()['status'] == 'needs_review'
