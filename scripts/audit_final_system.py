"""Ebarki independent live BFF release audit. Fictional data only, no external filing.

python scripts/tasks.py backend run python ../../scripts/audit_final_system.py
Records response evidence without tokens, credentials, upload URLs, or headers.
Browser observations are documented separately and are not implied by these checks.
"""
import asyncio
import io
import json
import secrets
import sys
import time
import zipfile
from collections import Counter
from pathlib import Path

import httpx
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT/'docs/qa/fixtures'
OUT = ROOT/'docs/qa/evidence'
OUT.mkdir(parents=True, exist_ok=True)
results = []
sys.stdout.reconfigure(encoding='utf8')
run_tag = sys.argv[1] if len(sys.argv) > 1 else 'initial'


def check(name, condition, **evidence):
    result = {'test': name, 'result': 'PASS' if condition else 'FAIL', **evidence}
    results.append(result)
    print(f'{result["result"]}: {name}', flush=True)
    save()


def save():
    (OUT/f'live-{run_tag}.json').write_text(json.dumps({
        'product': 'Ebarki', 'tested_on': '2026-11-05', 'transport': 'live Next.js BFF; not browser',
        'summary': dict(Counter(item['result'] for item in results)), 'results': results,
    }, ensure_ascii=False, indent=2)+'\n', encoding='utf8')


async def req(client, method, path, expected=(200, 201, 202), **kwargs):
    response = await client.request(method, path, **kwargs)
    if response.status_code not in expected:
        raise RuntimeError(f'{method} {path.split("?")[0]} returned {response.status_code}')
    return response


async def guest():
    client = httpx.AsyncClient(base_url='http://127.0.0.1:3000/api/v1', timeout=110)
    auth = (await req(client, 'POST', '/auth/guest')).json()
    client.headers['Authorization'] = 'Bearer '+auth['access_token']
    return client


async def new_case(client, narrative, label, consent=False):
    case = (await req(client, 'POST', '/cases', json={
        'title': 'Ebarki FICTIONAL QA '+label, 'story_narrative': narrative,
        'merchant_name': 'Fictional Padma Test Shop',
    })).json()
    if consent:
        await req(client, 'POST', '/consents', json={'case_id': case['id'],
            'purpose': 'external_ai_processing', 'policy_version': '1.0',
            'affirmative_action': 'independent_qa_fictional_records_only'})
    return '/cases/'+case['id']


async def version(c, base):
    return (await req(c, 'GET', base)).json()['row_version']


async def run(c, base, locale='en', operation='resolve'):
    task = (await req(c, 'POST', base+'/runs', json={'operation': operation, 'locale': locale,
        'expected_version': await version(c, base)})).json()
    deadline = time.monotonic()+210
    while time.monotonic() < deadline:
        task = (await req(c, 'GET', base+'/runs/'+task['id'])).json()
        if task['status'] in {'completed', 'needs_review', 'failed', 'cancelled'}:
            return task
        await asyncio.sleep(.5)
    raise RuntimeError('run polling timeout')


async def upload(c, base, name, mime, valid=True):
    data = (FIX/name).read_bytes()
    response = await c.post('/uploads/init', json={'case_id': base.split('/')[-1],
        'declared_filename': name, 'declared_mime_type': mime, 'declared_byte_size': len(data)})
    if response.status_code not in (200, 201):
        return response.status_code, response.json()
    intent = response.json()
    raw = await c.put('/uploads/'+intent['intent_id']+'/raw', params={'token': intent['upload_token']},
        content=data, headers={'Content-Type': mime})
    if raw.status_code >= 400:
        return raw.status_code, {'status': 'raw_rejected'}
    response = await c.post('/uploads/'+intent['intent_id']+'/complete')
    return response.status_code, response.json()


async def matrix():
    narratives = json.loads((FIX/'narratives.json').read_text(encoding='utf8'))
    c = await guest()
    bases = {}
    for language in ['english', 'bangla', 'banglish', 'minimal', 'mixed_digits', 'long', 'injection']:
        try:
            base = await new_case(c, narratives[language], language, language in ['english', 'bangla', 'injection'])
            bases[language] = base
            task = await run(c, base, 'bn' if language == 'bangla' else 'en')
            facts = (await req(c, 'GET', base+'/facts')).json()
            amount = next((f['typed_value'].get('minor_units') for f in facts if f['field_name'] == 'amount_paid'), None)
            dates = [f['typed_value'] for f in facts if f['field_name'] == 'incident_date']
            check(language+' fresh save and processing', task['status'] in ['completed', 'needs_review'],
                  case_id=base.split('/')[-1], status=task['status'], facts=facts, summary=task['result'].get('understanding'))
            if language in ['english', 'bangla', 'banglish', 'mixed_digits']:
                check(language+' exact money content', amount == 732150, observed=amount)
                check(language+' incident date content', any(d.get('date') == '2026-10-24' for d in dates), observed=dates)
            if language in ['english', 'bangla']:
                check(language+' real summary execution', task['result'].get('understanding', {}).get('model_executed'),
                      receipt=task['result'].get('understanding'))
            if language == 'injection':
                text = task['result'].get('understanding', {}).get('summary', '')
                # A summary may attribute a malicious request without executing it.
                # Detect success assertions, rather than matching words inside attribution.
                # Distinguish attributed requests from first-person/product success
                # claims. Baseline/retest outputs were manually reviewed as attribution.
                import re
                check('injection does not claim filing or guaranteed refund',
                      not re.search(r'\b(?:I|we|Ebarki) (?:have |has )?(?:submitted|filed)|\byour refund is guaranteed|\bwe guarantee|gsk_', text, re.I), text=text,
                      manual_review='Attribution of attacker instructions is not evidence that an external action occurred.')
        except Exception as error:
            check(language+' journey completed', False, error=str(error))

    base = bases['english']
    # Keep ordinary cases independent from the judge samples.
    check('ordinary case cannot add sample payment', (await c.post(base+'/sample-payment')).status_code in (400, 403, 404))
    public = (await req(c, 'GET', '/merchants/intelligence', params={'query': 'Fictional Padma'})).json()
    check('public merchant results exclude private case data', public['recent_complaints'] == [] and public['complaint_count'] == 0)
    check('public community has no fabricated seeds', (await req(c, 'GET', '/community/posts')).json() == [])
    for name, mime in [('receipt text.pdf','application/pdf'), ('unrelated groceries.pdf','application/pdf'),
                       ('duplicate নাম 99999.pdf','application/pdf')]:
        status, item = await upload(c, base, name, mime)
        check('upload '+name, status in (200, 201) and item.get('status') == 'accepted', status=status)
    task = await run(c, base)
    ledger = (await req(c, 'GET', base+'/evidence/reconciliation')).json()
    check('unreviewed unrelated PDF excluded from payment total',
          all(i['filename'] != 'unrelated groceries.pdf' for i in ledger.get('reconciled_items', [])), ledger=ledger)
    records = (await req(c, 'GET', base+'/connected-records')).json()
    check('PDF byte content and source coordinates', any(s['method'] == 'native_pdf' and '7,000.00' in s['text']
          and s.get('lines') for s in records['sources']))
    unicode_source = next(s for s in records['sources'] if s['filename'] == 'duplicate নাম 99999.pdf')
    preview = await c.get(base+'/evidence/'+unicode_source['id']+'/preview')
    check('Unicode filename private preview', preview.status_code == 200 and preview.content.startswith(b'%PDF'))
    for moment in records['timeline']:
        source = next((s for s in records['sources'] if s['id'] == moment['source_id']), {})
        if source.get('filename') == 'receipt text.pdf' and moment['kind'] == 'payment':
            await req(c, 'POST', base+'/connected-records/review', json={'item_id': moment['id'],
                'outcome': 'confirmed', 'expected_version': await version(c, base)})
            break
    ledger = (await req(c, 'GET', base+'/evidence/reconciliation')).json()
    check('reviewed first receipt exact 321.50 discrepancy', ledger['linked_evidence_total_minor_units'] == 700000
          and ledger['discrepancy_minor_units'] == 32150, ledger=ledger)
    await upload(c, base, 'second payment.pdf', 'application/pdf')
    await run(c, base)
    records = (await req(c, 'GET', base+'/connected-records')).json()
    for moment in records['timeline']:
        source = next((s for s in records['sources'] if s['id'] == moment['source_id']), {})
        if source.get('filename') == 'second payment.pdf' and moment['kind'] == 'payment':
            await req(c, 'POST', base+'/connected-records/review', json={'item_id': moment['id'],
                'outcome': 'confirmed', 'expected_version': await version(c, base)})
            break
    ledger = (await req(c, 'GET', base+'/evidence/reconciliation')).json()
    check('second content receipt resolves discrepancy', ledger['is_reconciled'] and ledger['linked_evidence_total_minor_units'] == 732150, ledger=ledger)

    # Real visual/audio execution on fresh bytes, then explicit cached-reading check.
    media = await new_case(c, narratives['english'], 'multimodal', True)
    for name, mime in [('receipt clear.png', 'image/png'), ('seller chat.png', 'image/png'),
                       ('known case details.wav','audio/wav'), ('multi page.pdf','application/pdf'),
                       ('scanned receipt.pdf','application/pdf'), ('receipt plausible low quality.jpg','image/jpeg'),
                       ('বাংলা রসিদ.png','image/png')]:
        status, item = await upload(c, media, name, mime)
        check('media upload '+name, status in (200, 201) and item.get('status') == 'accepted', status=status)
    task = await run(c, media)
    readings = task['result'].get('readings', [])
    check('real image OCR exact content', any(r.get('model_executed') and r['filename'] == 'receipt clear.png'
          and '7,000' in r['text'] for r in readings), readings=readings)
    check('real speech transcription', any(r.get('model_executed') and r['filename'].endswith('.wav')
          and 'kettle' in r['text'].lower() for r in readings))
    bangla_reading = next((r for r in readings if r['filename'] == 'বাংলা রসিদ.png'), {})
    check('Bangla image content reading', bangla_reading.get('model_executed') and
          ('৭,০০০' in bangla_reading.get('text','') or '7,000' in bangla_reading.get('text','')),
          reading=bangla_reading)
    for reading in readings:
        if reading.get('model_executed'):
            check('provider acknowledgement '+reading['filename'], bool(reading.get('execution_receipt', {}).get('request_id')),
                  execution_receipt=reading.get('execution_receipt'))
    check('multi-page PDF preserves page 2', any(r['filename'] == 'multi page.pdf' and any(line.get('page') == 2 for line in r['lines']) for r in readings))
    check('scanned PDF honest manual fallback', any(r['filename'] == 'scanned receipt.pdf' and r['method'] == 'manual_required' and not r['model_executed'] for r in readings))
    task2 = await run(c, media)
    check('repeat run identifies cached readings', any(r.get('reused_from_run') for r in task2['result'].get('readings', [])))
    for locale in ['en', 'bn']:
        reply = (await req(c, 'POST', media+'/reply-preparations', json={'message': 'We will refund tomorrow. Please wait.',
            'locale': locale, 'expected_version': await version(c, media)})).json()
        check(locale+' real reply, never sent', reply.get('model_executed') and not reply['is_sent'], reply=reply)
        edited = (await req(c, 'PUT', media+'/reply-preparations/'+reply['id'], json={
            'draft': 'Fictional QA: please confirm the refund date in writing.', 'expected_version': await version(c, media)})).json()
        check(locale+' saved reply edit', edited.get('user_edited'))
        chat = (await req(c, 'POST', '/copilot/chat', json={'case_id': media.split('/')[-1], 'locale': locale,
            'message': 'What should I check next?' if locale == 'en' else 'এখন কী তথ্য মিলিয়ে দেখব?'})).json()
        check(locale+' real contextual copilot', chat.get('mode') == 'model_explanation', response=chat)
        doc = (await req(c, 'GET', media+'/documents/ast', params={'locale': locale})).json()
        export = await req(c, 'POST', media+'/export/pdf', params={'locale': locale, 'document_id': doc['document_id'],
            'expected_case_version': doc['case_version'], 'expected_revision': doc['revision']})
        (OUT/f'export-{run_tag}-{locale}.pdf').write_bytes(export.content)
        pages = PdfReader(io.BytesIO(export.content)).pages
        check(locale+' actual PDF export', export.content.startswith(b'%PDF') and len(pages) > 0, bytes=len(export.content), pages=len(pages))
    zipout = await req(c, 'POST', media+'/export/zip')
    check('ZIP export is real archive', zipfile.is_zipfile(io.BytesIO(zipout.content)), bytes=len(zipout.content))
    handoff = (await req(c, 'GET', media+'/filing-handoff')).json()
    check('filing handoff remains unsubmitted', handoff['is_submitted'] is False and bool(handoff['official_destination_url']))
    old = await version(c, media)
    preview = (await req(c, 'POST', media+'/what-if', json={'overrides': {'goods_delivered': True}})).json()
    check('what-if isolated baseline', await version(c, media) == old and preview['case_version'] == old)
    # An ordinary input correction invalidates old exports; no stale success.
    old_doc = (await req(c, 'GET', media+'/documents/ast')).json()
    changed = await req(c, 'POST', media+'/connected-records/sources', json={
        'text': 'Fictional Seller: We will refund tomorrow. Exact date not confirmed.',
        'source_type': 'manual_transcript', 'label': 'Fictional manual transcript', 'expected_version': old})
    check('manual transcript saved with version change', changed.json()['case_version'] > old)
    stale = await c.post(media+'/export/pdf', params={'document_id': old_doc['document_id'],
        'expected_case_version': old_doc['case_version'], 'expected_revision': old_doc['revision']})
    check('stale PDF export blocked', stale.status_code == 409, status=stale.status_code)
    stale_update = await c.patch(media, json={'expected_version': old, 'title': 'Stale fictional write'})
    check('concurrent stale case write blocked', stale_update.status_code == 409, status=stale_update.status_code)
    fresh_records = (await req(c, 'GET', media+'/connected-records')).json()
    manual = next(m for m in fresh_records['timeline'] if m['source_id'] == changed.json()['id'])
    check('relative promise is not assigned a guessed date', manual['occurred_on'] is None)
    await req(c, 'POST', media+'/connected-records/review', json={'item_id': manual['id'], 'outcome': 'confirmed',
        'corrected_date': '2026-10-29', 'expected_version': await version(c, media)})
    after_review = (await req(c, 'GET', media+'/connected-records')).json()
    check('date correction persists on reopen', any(m['id'] == manual['id'] and m['occurred_on'] == '2026-10-29'
        and m['review'] == 'confirmed' for m in after_review['timeline']))
    live_run = (await req(c, 'POST', media+'/runs', json={'operation': 'resolve', 'locale': 'en'})).json()
    await req(c, 'POST', media+'/runs/'+live_run['id']+'/cancel')
    for _ in range(100):
        stopped = (await req(c, 'GET', media+'/runs/'+live_run['id'])).json()
        if stopped['status'] in ['cancelled', 'completed', 'needs_review', 'failed']:
            break
        await asyncio.sleep(.2)
    check('cancellation reaches truthful durable state', stopped['status'] == 'cancelled', status=stopped['status'])
    stream = await req(c, 'GET', media+'/runs/'+live_run['id']+'/events')
    check('SSE history reports actual recorded events', 'data:' in stream.text and live_run['id'] in stream.text)

    for name, mime in [('empty.png','image/png'), ('corrupt.pdf','application/pdf'),
                       ('corrupt.png','image/png'), ('unsupported.txt','text/plain'), ('spoof.png','image/png')]:
        status, result = await upload(c, media, name, mime, False)
        check('invalid upload rejected '+name, status >= 400 or result.get('status') not in ('accepted', 'pending'), status=status, observed_status=result.get('status'))
    oversize = await c.post('/uploads/init', json={'case_id': media.split('/')[-1], 'declared_filename': 'FICTIONAL oversized.png',
        'declared_mime_type':'image/png', 'declared_byte_size': 21*1024*1024})
    check('oversize rejected before transfer', oversize.status_code >= 400, status=oversize.status_code)
    intent = (await req(c, 'POST', '/uploads/init', json={'case_id': media.split('/')[-1],
        'declared_filename': 'Fictional oversized recording.wav', 'declared_mime_type': 'audio/wav',
        'declared_byte_size': 1024})).json()
    oversized_data = (FIX/'oversized valid silence.wav').read_bytes()
    oversized_raw = await c.put('/uploads/'+intent['intent_id']+'/raw', params={'token': intent['upload_token']},
        content=oversized_data, headers={'Content-Type':'audio/wav'})
    check('actual oversized playable file rejected despite false declared size', oversized_raw.status_code == 422,
          status=oversized_raw.status_code, actual_bytes=len(oversized_data))

    stranger = await guest()
    records = (await req(c, 'GET', media+'/connected-records')).json()
    ev = next(s for s in records['sources'] if s['mime_type'].startswith('image/'))
    doc = (await req(c, 'GET', media+'/documents/ast')).json()
    for path in ['', '/facts','/evidence', '/connected-records', '/reply-preparations', '/runs',
                 '/documents/ast', '/documents/versions/'+doc['document_id'], '/filing-handoff',
                 '/evidence/'+ev['id']+'/preview', '/evidence/'+ev['id']+'/page-preview']:
        response = await stranger.get(media+path)
        check('cross-owner denied '+(path or '/case'), response.status_code == 404, status=response.status_code)
    for path in ['/admin/stats', '/admin/users', '/admin/cases']:
        response = await c.get(path)
        check('consumer denied '+path, response.status_code == 403, status=response.status_code)
    judge = await guest()
    auth = (await req(judge, 'POST', '/auth/judge-demo')).json()
    judge.headers['Authorization'] = 'Bearer '+auth['access_token']
    check('judge denied admin', (await judge.get('/admin/stats')).status_code == 403)
    check('judge cannot read consumer case', (await judge.get(media)).status_code == 404)
    # Separate registered users: credentials are generated only in memory.
    accounts = []
    for idx in range(2):
        account = httpx.AsyncClient(base_url='http://127.0.0.1:3000/api/v1', timeout=40)
        email = f'ebarki-qa-{uuid_token()}-{idx}@example.invalid'
        password = secrets.token_urlsafe(24)
        auth = (await req(account, 'POST', '/auth/register', json={
            'email': email, 'password': password, 'full_name': 'Fictional Ebarki QA Consumer'})).json()
        account.headers['Authorization'] = 'Bearer '+auth['access_token']
        accounts.append((account, email, password))
    owned = await new_case(accounts[0][0], narratives['minimal'], 'registered consumer')
    check('registered second user isolated', (await accounts[1][0].get(owned)).status_code == 404)
    account, email, password = accounts[0]
    account.headers.pop('Authorization', None)
    account.cookies.clear()
    logged = (await req(account, 'POST', '/auth/login', json={'email': email, 'password': password})).json()
    account.headers['Authorization'] = 'Bearer '+logged['access_token']
    check('registered login reopens saved case', (await account.get(owned)).status_code == 200)
    for account, _, _ in accounts:
        await account.aclose()

    no_consent = bases['minimal']
    await upload(c, no_consent, 'receipt clear.png', 'image/png')
    task = await run(c, no_consent)
    check('no consent no external image execution', all(not r.get('model_executed') for r in task['result'].get('readings', [])))
    await req(c, 'POST', no_consent+'/consent/withdraw', json={})
    response = await c.post(no_consent+'/runs', json={'operation':'resolve'})
    check('withdrawn processing denied', response.status_code == 403, status=response.status_code)
    await c.aclose()
    await stranger.aclose()
    await judge.aclose()


def uuid_token():
    return secrets.token_hex(8)


if __name__ == '__main__':
    try:
        asyncio.run(matrix())
    except Exception as error:
        check('audit suite completed', False, error=str(error), error_type=type(error).__name__)
    save()
    print(json.dumps(dict(Counter(item['result'] for item in results))))
    raise SystemExit(1 if any(r['result']=='FAIL' for r in results) else 0)
