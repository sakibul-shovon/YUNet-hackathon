"""User-visible workspace contracts: honest execution, private history, lasting edits."""
import io
import uuid
import zipfile

import pytest
from PIL import Image
from pypdf import PdfReader


async def own_case(client, **values):
    boot = (await client.post('/auth/guest')).json()
    headers = {'Authorization': f'Bearer {boot["access_token"]}'}
    response = await client.post('/v1/cases', headers=headers, json={
        'title': 'Ebarki sample purchase', 'merchant_name': 'Sample shop',
        'story_narrative': 'I paid 5500 taka for a phone. The goods were not delivered.', **values,
    })
    assert response.status_code == 201, response.text
    return response.json(), headers


@pytest.mark.asyncio
async def test_runs_execute_record_real_methods_and_replay_without_reexecution(client):
    case, headers = await own_case(client)
    base = f'/v1/cases/{case["id"]}'
    assert (await client.get(base+'/runs', headers=headers)).json() == []
    started = await client.post(base+'/runs', headers=headers, json={'operation':'extract','locale':'bn'})
    assert started.status_code == 202
    run = (await client.get(base+'/runs/'+started.json()['id'], headers=headers)).json()
    assert run['status'] == 'needs_review', run
    assert run['stages'][0]['method'] == 'deterministic_pattern_extractor'
    assert run['stages'][0]['duration_ms'] >= 0
    assert run['result']['proposed_facts'] > 0
    facts = (await client.get(base+'/facts', headers=headers)).json()
    assert facts and all(f['review_outcome'] is None for f in facts)
    replay = (await client.get(base+'/runs/'+run['id'], headers=headers)).json()
    assert replay == run
    events = await client.get(base+'/runs/'+run['id']+'/events', headers=headers)
    assert events.headers['content-type'].startswith('text/event-stream')
    assert 'event: run' in events.text and run['id'] in events.text


@pytest.mark.asyncio
async def test_document_edits_survive_reload_and_export_and_clear_inherited_support(client):
    case, headers = await own_case(client)
    base = f'/v1/cases/{case["id"]}'
    await client.post(base+'/facts',headers=headers,json={
        'field_name':'incident_date','field_type':'date','raw_value':'2026-10-30'})
    doc = (await client.get(base+'/documents/ast?locale=bn',headers=headers)).json()
    edited = await client.post(base+'/documents/edit',headers=headers,json={
        'document_type':doc['document_type'],'locale':'bn','expected_revision':doc['revision'],
        'section_id':doc['sections'][0]['section_id'],
        'sentence_id':doc['sections'][0]['sentences'][0]['sentence_id'],
        'new_text':'আমি মূল রসিদের তথ্য মিলিয়ে দেখেছি। <script>alert(1)</script>',
    })
    assert edited.status_code == 200, edited.text
    latest = edited.json()
    assert latest['revision'] == doc['revision']+1 and latest['locale']=='bn'
    sentence = latest['sections'][0]['sentences'][0]
    assert sentence['supporting_fact_id'] is None and sentence['supporting_citation'] is None
    assert sentence['is_user_edited'] and sentence['statement_type']=='user_allegation'
    assert (await client.get(base+'/documents/ast?locale=bn',headers=headers)).json() == latest
    stale = await client.post(base+'/documents/edit',headers=headers,json={
        'document_type':doc['document_type'],'locale':'bn','expected_revision':doc['revision'],
        'section_id':doc['sections'][0]['section_id'],
        'sentence_id':doc['sections'][0]['sentences'][0]['sentence_id'],'new_text':'stale',
    })
    assert stale.status_code == 409
    exported = (await client.post(base+'/export/html?locale=bn',headers=headers)).json()
    assert '<script>' not in exported['content'] and '&lt;script&gt;' in exported['content']
    assert 'Ebarki' in exported['content'] and not exported['is_filed']
    history = (await client.get(base+'/documents/history',headers=headers)).json()
    assert len(history) == 2
    old = (await client.get(base+'/documents/versions/'+str(doc['document_id']),headers=headers)).json()
    assert old['revision']==1


@pytest.mark.asyncio
async def test_bangla_pdf_and_zip_are_real_downloads_and_never_submit(client):
    case, headers = await own_case(client, title='পণ্য না পাওয়ার অভিযোগ')
    base = f'/v1/cases/{case["id"]}'
    response = await client.post(base+'/export/pdf?locale=bn',headers=headers)
    assert response.status_code == 200, response.text[:300]
    assert response.content.startswith(b'%PDF')
    pdf = PdfReader(io.BytesIO(response.content))
    assert len(pdf.pages)>=1 and pdf.metadata.author=='Ebarki'
    assert 'no-store' in response.headers['cache-control']
    bundle = await client.post(base+'/export/zip?locale=bn&include_originals=false',headers=headers)
    assert bundle.status_code == 200
    with zipfile.ZipFile(io.BytesIO(bundle.content)) as archive:
        assert set(archive.namelist())=={'Ebarki-draft.pdf','Ebarki-draft.md'}
    assert (await client.get(base,headers=headers)).json()['lifecycle_status']==case['lifecycle_status']


@pytest.mark.asyncio
async def test_run_document_and_assistant_access_is_owner_scoped(client):
    case, headers = await own_case(client)
    base = f'/v1/cases/{case["id"]}'
    run = (await client.post(base+'/runs',headers=headers,json={'operation':'assess'})).json()
    doc = (await client.get(base+'/documents/ast',headers=headers)).json()
    client.cookies.clear()
    foreign = (await client.post('/auth/guest')).json()
    other = {'Authorization':f'Bearer {foreign["access_token"]}'}
    for path in ['/runs','/runs/'+run['id'],'/runs/'+run['id']+'/events',
                 '/documents/ast','/documents/history','/documents/versions/'+doc['document_id']]:
        assert (await client.get(base+path,headers=other)).status_code==404
    assert (await client.post(base+'/runs/'+run['id']+'/cancel',headers=other)).status_code==404
    assert (await client.post(base+'/export/pdf',headers=other)).status_code==404
    assert (await client.post('/v1/copilot/chat',headers=other,json={
        'message':'Summarize this case','case_id':case['id']})).status_code==404


@pytest.mark.asyncio
async def test_cancelled_run_does_not_execute_and_corrected_review_is_visible(client, db_session):
    from app.identity.models import Principal
    from app.operations.runs import RunRequest, create_run, execute_run
    from conftest import TestSessionLocal
    case, headers = await own_case(client)
    principal = await db_session.get(Principal,uuid.UUID(case['principal_id']))
    run = await create_run(uuid.UUID(case['id']),RunRequest(),principal,db_session)
    run.cancel_requested=True
    await db_session.commit()
    await execute_run(run.id,TestSessionLocal)
    base=f'/v1/cases/{case["id"]}'
    result=(await client.get(base+'/runs/'+str(run.id),headers=headers)).json()
    assert result['status']=='cancelled' and result['stages']==[]
    fact=(await client.post(base+'/facts',headers=headers,json={
        'field_name':'amount_paid','field_type':'money','raw_value':'5500'})).json()
    review=await client.post(base+'/facts/'+fact['id']+'/review',headers=headers,json={
        'review_outcome':'corrected','corrected_value':'5000'})
    assert review.status_code==200,review.text
    active=(await client.get(base+'/facts',headers=headers)).json()
    assert active[0]['review_outcome']=='corrected'
    await client.post(base+'/consent/withdraw',headers=headers)
    assert (await client.post(base+'/runs',headers=headers,json={'operation':'assess'})).status_code==403
