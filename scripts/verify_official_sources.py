"""Read-only Ebarki official source/destination checks. Never submits a form."""
import asyncio
import datetime
import hashlib
import json
import re
import sys
from html import unescape
from pathlib import Path

import httpx

URLS = {
    'consumer_act': 'https://bdlaws.minlaw.gov.bd/act-print-1014.html',
    'insurance_act': 'https://bdlaws.minlaw.gov.bd/act-print-1037.html',
    'dncrp_authority': 'https://dncrp.gov.bd/',
    'dncrp_complaint': 'https://dncrp.com/',
    'bb_guide': 'https://www.bb.org.bd/en/index.php/services/cipc_procedure',
    'bb_complaint': 'https://cms.bb.org.bd/ords/f?p=107%3A133%3A',
    'btrc_complaint': 'https://crm.btrc.gov.bd/',
    'idra_government_form': 'https://idra.portal.gov.bd/pages/web-forms/6922d3c181fc96cef9e9bf15',
    'idra_complaint': 'https://cms.idra.org.bd/grievence-form',
    'grs': 'https://www.grs.gov.bd/',
    'hackathon_rules': 'https://yunet-aignite26.devpost.com/rules',
}


async def main():
    async with httpx.AsyncClient(timeout=22, follow_redirects=True) as client:
        async def inspect(name, url):
            try:
                response = await client.get(url)
                title = re.search(r'<title[^>]*>(.*?)</title>', response.text, re.I | re.S)
                text = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', response.text, flags=re.S | re.I)
                text = unescape(re.sub('<[^>]+>', ' ', text))
                text = re.sub(r'\s+', ' ', text).strip()
                blocked = any(marker in text.lower() for marker in ['just a moment', 'enable javascript and cookies', 'checking your browser', 'access denied'])
                result = 'PASS' if response.status_code == 200 and not blocked else 'BLOCKED' if blocked or response.status_code in [403, 429, 503] else 'FAIL'
                details = {'id': name, 'url': url, 'final_url': str(response.url), 'http_status': response.status_code,
                    'result': result, 'title': unescape(title.group(1)).strip() if title else None,
                    'response_sha256': hashlib.sha256(response.content).hexdigest(),
                    'note': 'Read-only HTTP observation; does not verify successful filing, credentials, availability later, or legal applicability.'}
                # Minimal material-section extracts for source comparison, never a fabricated transcription.
                if name in ['consumer_act', 'insurance_act'] and result == 'PASS':
                    label = 'অভিযোগ দায়েরের সময়সীমা' if name == 'consumer_act' else 'বিলম্বে দাবী পরিশোধের সুদ'
                    start = text.find(label)
                    if name == 'consumer_act' and start < 0:
                        section = re.search(r'৬০[৷।.]', text)
                        start = section.start() if section else -1
                    details['material_section_observed'] = text[start:start+620] if start >= 0 else 'Section heading not located automatically.'
                    if name == 'consumer_act':
                        details['material_sections'] = {}
                        for number in [41, 44, 45, 60, 76]:
                            digits = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')
                            begin = re.search(r'(?<![০-৯])'+str(number).translate(digits)+r'[৷।.]', text)
                            end = re.search(r'(?<![০-৯])'+str(number+1).translate(digits)+r'[৷।.]', text[begin.end():]) if begin else None
                            if begin and end:
                                fragment = text[begin.start():begin.end()+end.start()].strip()
                                terminal = max(fragment.rfind('।'), fragment.rfind('৷'))
                                details['material_sections'][str(number)] = fragment[:terminal+1]
                print(result+': '+name, flush=True)
                return details
            except httpx.HTTPError as error:
                print('BLOCKED: '+name, flush=True)
                return {'id': name, 'url': url, 'result': 'BLOCKED', 'reason': type(error).__name__}
        selected = {name: url for name, url in URLS.items() if '--laws-only' not in sys.argv or name.endswith('_act')}
        findings = await asyncio.gather(*(inspect(name, url) for name, url in selected.items()))
    target = Path(__file__).resolve().parents[1]/'docs/qa/evidence'/('followup-laws.json' if '--laws-only' in sys.argv else 'followup-official-links.json')
    target.write_text(json.dumps({'product': 'Ebarki', 'checked_at': datetime.datetime.now(datetime.UTC).isoformat(),
        'checks': findings}, ensure_ascii=False, indent=2)+'\n', encoding='utf8')


asyncio.run(main())
