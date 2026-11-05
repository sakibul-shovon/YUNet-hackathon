"""Fresh Ebarki BFF OCR checks; preserve the earlier failed evidence unchanged."""
import asyncio
import json
import sys
from pathlib import Path

from audit_final_system import guest, new_case, run, upload

ROOT = Path(__file__).resolve().parents[1]


async def main():
    outcomes = []
    fixtures = [
        ('বাংলা রসিদ.png', 'image/png', ['কাল্পনিক পদ্মা টেস্ট শপ', 'PADMA-QA-BN24', '৭,০০০.০০']),
        ('scanned receipt.pdf', 'application/pdf', ['Fictional Padma Test Shop', 'PADMA-QA-A24', '7,000.00']),
        ('receipt plausible low quality.jpg', 'image/jpeg', ['Fictional Padma Test Shop', 'PADMA-QA-A24', '7,000.00']),
        ('followup/Bangla scan.pdf', 'application/pdf', ['কাল্পনিক পদ্মা টেস্ট শপ', 'PADMA-QA-BN24', '৭,০০০.০০']),
        ('followup/Native and Bangla scan.pdf', 'application/pdf', ['PADMA-QA-A24', 'কাল্পনিক পদ্মা টেস্ট শপ', 'PADMA-QA-BN24']),
    ]
    retry = '--retry-blocked' in sys.argv
    if retry:
        previous = json.loads((ROOT/'docs/qa/evidence/followup-live-ocr.json').read_text(encoding='utf8'))
        blocked = {test['filename'] for test in previous['tests'] if test['result'] == 'BLOCKED'}
        fixtures = [fixture for fixture in fixtures if fixture[0] in blocked]
    for index, (filename, mime, expected) in enumerate(fixtures):
        if retry and index:
            await asyncio.sleep(55)  # Audit-only pacing after observed provider quota limits.
        client = await guest()
        try:
            # No expected amounts/names are supplied in this case narrative or request prompt.
            base = await new_case(client, 'Fictional Ebarki QA only. Please read the record I provide.', 'OCR follow-up', True)
            status, item = await upload(client, base, filename, mime)
            task = await run(client, base, 'bn' if filename.endswith('.png') else 'en')
            reading = next((r for r in task['result'].get('readings', []) if r['filename'] in [filename, Path(filename).name]), {})
            text = reading.get('text', '')
            checks = {value: 'PASS' if value in text else 'FAIL' for value in expected}
            if filename.endswith('Native and Bangla scan.pdf'):
                checks['both pages read'] = 'PASS' if reading.get('pages_read') == [1, 2] and not reading.get('partial') else 'FAIL'
                checks['Bangla scan attributed to page 2'] = 'PASS' if any(line.get('page') == 2 and 'কাল্পনিক পদ্মা' in line['text'] for line in reading.get('lines', [])) else 'FAIL'
                preview = await client.get(base+'/evidence/'+item['id']+'/page-preview?page=2')
                checks['private page-2 preview'] = 'PASS' if preview.status_code == 200 and preview.content.startswith(b'\x89PNG') else 'FAIL'
            executed = bool(reading.get('model_executed') and reading.get('execution_receipt', {}).get('request_id'))
            blocked = reading.get('provider_status') in [429, 503]
            result = 'BLOCKED' if blocked else 'PASS' if executed and all(v == 'PASS' for v in checks.values()) else 'FAIL'
            outcomes.append({'filename': filename, 'upload_status': status, 'case_id': base.split('/')[-1],
                             'result': result, 'content_checks': checks, 'reading': reading})
            print(result+': '+filename, flush=True)
            (ROOT/'docs/qa/evidence'/('followup-ocr-retry.json' if retry else 'followup-live-ocr.json')).write_text(json.dumps({
                'product': 'Ebarki', 'transport': 'Actual Next.js BFF; browser acceptance remains blocked',
                'tests': outcomes}, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
        finally:
            await client.aclose()


asyncio.run(main())
