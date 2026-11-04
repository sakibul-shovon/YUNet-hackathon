"""Exercise the actual web BFF with fictional records. Never prints credentials or tokens.

Run through: python scripts/tasks.py backend run python ../../scripts/verify_live_ai.py
The development stack must already be running. This calls configured live AI providers.
"""
import asyncio
import json
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:3000/api/v1'
REPORT = ROOT / '.agent' / 'live-ai-report.json'
results = []


def record(name, passed, **details):
    results.append({'check': name, 'passed': bool(passed), **details})
    print(f'{"PASS" if passed else "FAIL"}: {name}', flush=True)


async def main():
    async with httpx.AsyncClient(base_url=BASE, timeout=100) as client:
        async def request(method, path, **kwargs):
            response = await client.request(method, path, **kwargs)
            # No response body / URL in errors: upload URLs contain one-use tokens.
            if response.status_code >= 400:
                raise RuntimeError(f'API status {response.status_code}')
            return response

        guest = (await request('POST', '/auth/guest')).json()
        client.headers['Authorization'] = f'Bearer {guest["access_token"]}'
        case = (await request('POST', '/cases', json={
            'title': 'Ebarki live QA / fictional order', 'merchant_name': 'Fictional QA Electronics',
            'story_narrative': 'I paid BDT 5,500 for a phone on 2026-10-20. The seller promised delivery on 2026-10-22. The phone has not arrived. These are fictional test records.',
            'incident_date': '2026-10-20',
        })).json()
        base = f'/cases/{case["id"]}'
        await request('POST', '/consents', json={'case_id': case['id'], 'purpose': 'external_ai_processing',
            'policy_version': '1.0', 'affirmative_action': 'live_qa_fictional_records_only'})

        async def version():
            return (await request('GET', base)).json()['row_version']

        async def run(locale):
            task = (await request('POST', base+'/runs', json={
                'operation': 'resolve', 'locale': locale, 'expected_version': await version(),
            })).json()
            deadline = time.monotonic()+180
            while time.monotonic() < deadline:
                task = (await request('GET', base+'/runs/'+task['id'])).json()
                if task['status'] in {'completed', 'needs_review', 'failed', 'cancelled'}:
                    break
                await asyncio.sleep(1)
            record(f'{locale} real run stages', task['status'] in {'completed', 'needs_review'},
                   status=task['status'], stages=len(task.get('stages', [])))
            return task

        async def upload(name, mime):
            data = (ROOT/'demo/specs/samples'/name).read_bytes()
            intent = (await request('POST', '/uploads/init', json={'case_id': case['id'],
                'declared_filename': name, 'declared_mime_type': mime, 'declared_byte_size': len(data)})).json()
            await request('PUT', '/uploads/'+intent['intent_id']+'/raw',
                          params={'token': intent['upload_token']}, content=data,
                          headers={'Content-Type': mime})
            item = (await request('POST', '/uploads/'+intent['intent_id']+'/complete')).json()
            record('accepted '+mime, item['status'] == 'accepted')
            return item

        await upload('ebarki_qa_receipt.png', 'image/png')
        await upload('ebarki_qa_voice.wav', 'audio/wav')
        for locale in ['en', 'bn']:
            task = await run(locale)
            summary = task.get('result', {}).get('understanding', {})
            record(locale+' model summary', summary.get('model_executed'), method=summary.get('method'),
                   text=summary.get('summary', ''))
            if locale == 'en':
                readings = task.get('result', {}).get('readings', [])
                for mime, method, expected in [('image/', 'groq_vision', '5,000'), ('audio/', 'groq_transcription', '5,500')]:
                    reading = next((r for r in readings if r.get('mime_type', '').startswith(mime)), {})
                    record(method, reading.get('model_executed') and reading.get('method') == method
                           and expected in reading.get('text', ''), text=reading.get('text', ''),
                           segments=len(reading.get('lines', [])), reason=reading.get('reason'),
                           provider_status=reading.get('provider_status'))
        data = (await request('GET', base+'/connected-records')).json()
        source = next((s for s in data['sources'] if s['method'] == 'groq_vision'), None)
        moment = next((m for m in data['timeline'] if source and m['source_id'] == source['id']
                       and m['kind'] == 'payment'), None)
        if moment:
            await request('POST', base+'/connected-records/review', json={'item_id': moment['id'],
                          'outcome': 'confirmed', 'expected_version': data['case_version']})
        record('source-linked image human review', bool(moment), has_box=bool(moment and moment.get('box')))
        ledger = (await request('GET', base+'/evidence/reconciliation')).json()
        record('receipt ledger detects actual 500 taka gap', ledger.get('linked_evidence_total_minor_units') == 500000
               and ledger.get('discrepancy_minor_units') == 50000,
               linked_minor=ledger.get('linked_evidence_total_minor_units'), gap_minor=ledger.get('discrepancy_minor_units'))

        for locale in ['en', 'bn']:
            chat = (await request('POST', '/copilot/chat', json={
                'case_id': case['id'], 'locale': locale,
                'message': 'What information should I check next?' if locale == 'en' else 'এখন কোন তথ্যগুলো মিলিয়ে দেখব?',
            })).json()
            record(locale+' copilot model explanation', chat.get('mode') == 'model_explanation',
                   mode=chat.get('mode'), text=chat.get('reply_'+locale))
            reply = (await request('POST', base+'/reply-preparations', json={
                'message': 'Please wait. We are checking your delivery with the courier.',
                'locale': locale, 'expected_version': await version(),
            })).json()
            record(locale+' model reply preparation', reply.get('model_executed') and not reply.get('is_sent'),
                   method=reply.get('method'), text=reply.get('draft'))

        preview = (await request('POST', base+'/what-if', json={'overrides': {'goods_delivered': True}})).json()
        record('what-if conditions with immutable baseline', bool(preview.get('baseline_routes'))
               and preview.get('case_version') == await version(), route_count=len(preview.get('route_diff', [])))
        for locale in ['en', 'bn']:
            doc = (await request('GET', base+'/documents/ast', params={'locale': locale})).json()
            pdf = await request('POST', base+'/export/pdf', params={'locale': locale,
                'document_id': doc['document_id'], 'expected_case_version': doc['case_version'],
                'expected_revision': doc['revision']})
            record(locale+' current reviewed PDF export', pdf.content.startswith(b'%PDF'), bytes=len(pdf.content))
        handoff = (await request('GET', base+'/filing-handoff')).json()
        record('guided official handoff', handoff.get('is_submitted') is False
               and handoff.get('official_destination_url') == 'https://dncrp.com/')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as error:
        record('live suite completed', False, error_type=type(error).__name__,
               status=str(error) if isinstance(error, RuntimeError) else 'See server diagnostics')
    REPORT.write_text(json.dumps({'tested_on': '2026-11-05', 'transport': 'Next.js web BFF',
        'data': 'fictional QA records only', 'results': results}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Report: {REPORT.relative_to(ROOT)}', flush=True)
    raise SystemExit(0 if results and all(r['passed'] for r in results) else 1)
