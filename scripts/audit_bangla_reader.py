"""One fresh Ebarki Bangla vision retry after a real 429; no invented result."""
import asyncio
import json
from pathlib import Path

from audit_final_system import guest, new_case, run, upload


async def main():
    client = await guest()
    base = await new_case(client, 'সম্পূর্ণ কাল্পনিক Ebarki পরীক্ষা। কেটলি পাইনি। রসিদ মিলিয়ে দেখুন।', 'Bangla OCR retry', True)
    status, item = await upload(client, base, 'বাংলা রসিদ.png', 'image/png')
    task = await run(client, base, 'bn')
    reading = next((r for r in task['result'].get('readings', []) if r['filename'] == 'বাংলা রসিদ.png'), {})
    correct = reading.get('model_executed') and any(amount in reading.get('text','') for amount in ['৭,০০০','7,000'])
    result = 'PASS' if correct else 'BLOCKED' if reading.get('provider_status') in [429,503] else 'FAIL'
    report = {'product':'Ebarki', 'test':'Fresh Bangla-image content execution retry', 'result':result,
              'upload_status':status, 'case_id':base.split('/')[-1], 'reading':reading,
              'ground_truth':'BDT 7,000.00; 24 October 2026; PADMA-QA-BN24; fictional merchant',
              'note':'Separate fresh execution, not a rewrite of the earlier rate-limited test.'}
    report['quality_checks'] = {
        'amount': 'PASS' if correct else 'UNVERIFIED',
        'reference': 'PASS' if 'PADMA-QA-BN24' in reading.get('text','') else 'FAIL',
        'merchant_verbatim': 'PASS' if 'কাল্পনিক পদ্মা টেস্ট শপ' in reading.get('text','') else 'FAIL',
    }
    path = Path(__file__).resolve().parents[1]/'docs/qa/evidence/ai-bangla-retry.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(result+': Fresh Bangla vision execution retry')
    await client.aclose()


asyncio.run(main())
