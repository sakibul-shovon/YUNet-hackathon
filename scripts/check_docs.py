"""Check the current judge/developer documentation without changing application state."""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]
FILES=[
    'README.md','README.bn.md','CONTRIBUTING.md','SECURITY.md','docs/README.md',
    'docs/product/FEATURES.md','docs/engineering/ARCHITECTURE.md',
    'docs/engineering/LOCAL_DEVELOPMENT.md','docs/engineering/API_REFERENCE.md',
    'docs/engineering/providers.md','docs/engineering/versions.md',
    'docs/ADMIN_PORTAL_GUIDE.md','docs/COMPLETE_SYSTEM_MANUAL.md',
    'docs/PRIVACY_AND_SAFETY.md','docs/assets/README.md','docs/qa/CURRENT_STATUS.md',
    'docs/pitch/judge_quickstart.md','docs/pitch/devpost_submission.md',
    'docs/pitch/demo_script.md','docs/pitch/deck_slides.md',
    'docs/pitch/SUBMISSION_CHECKLIST.md',
    'docs/pitch/DEVPOST_PROJECT_STORY.md','docs/pitch/DEVPOST_FIELDS.md',
    'docs/research/DOCUMENTATION_RESEARCH_2026-11-05.bn.md',
    'docs/research/CODEBASE_DOCUMENTATION_AUDIT_2026-11-05.md',
    'services/backend/README.md','docs/EBARKI_CONNECTED_EXPERIENCE.md',
    'docs/benchmarks/retrieval_ablation_benchmark_report.md',
    'docs/benchmarks/multimodal_provider_benchmark_report.md',
    'docs/qa/DOCUMENTATION_REFRESH_REPORT.md',
]
errors=[];links=0;external=set();images=0
def slug(text):
    text=re.sub('<[^>]+>','',text).lower().strip()
    text=re.sub(r'[^\w\- ]','',text)
    return text.replace(' ','-')

for name in FILES:
    p=ROOT/name
    if not p.is_file():errors.append(name+': missing document');continue
    raw=p.read_text(encoding='utf-8-sig')
    if raw.count('```')%2:errors.append(name+': unbalanced fenced code')
    text=re.sub(r'```[\s\S]*?```','',raw)
    targets=re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)',text)
    targets+=re.findall(r'(?:href|src)="([^"]+)"',text)
    for target in targets:
        target=target.strip('<>');parsed=urlsplit(target)
        if parsed.scheme in {'https','http','mailto'}:
            external.add(target);continue
        if parsed.scheme:errors.append(name+': unexpected link scheme '+target);continue
        links+=1
        path=(p.parent/unquote(parsed.path)).resolve() if parsed.path else p
        if not path.is_relative_to(ROOT):errors.append(name+': link escapes repository '+target);continue
        if not path.exists():errors.append(name+': missing target '+target);continue
        relative=path.relative_to(ROOT);current=ROOT
        for part in relative.parts:
            names={child.name for child in current.iterdir()}
            if part not in names:errors.append(name+': target case mismatch '+target);break
            current=current/part
        if parsed.fragment and path.suffix=='.md':
            headings={slug(h) for h in re.findall(r'^#{1,6}\s+(.+)$',path.read_text(encoding='utf-8-sig'),re.M)}
            explicit=set(re.findall(r'(?:id|name)="([^"]+)"',path.read_text(encoding='utf-8-sig')))
            if unquote(parsed.fragment) not in headings|explicit:errors.append(name+': missing anchor '+target)
    for tag in re.findall(r'<img\b[^>]*>',text):
        images+=1
        if not re.search(r'alt="[^"]+"',tag):errors.append(name+': image lacks descriptive alt')

for p in (ROOT/'docs/assets').rglob('*.svg'):
    try:ET.parse(p)
    except ET.ParseError as e:errors.append(str(p)+': '+str(e))

contract=json.loads((ROOT/'packages/contracts/openapi.json').read_text(encoding='utf-8'))
operations={(method.upper(),path) for path,methods in contract['paths'].items() for method in methods if method in {'get','post','put','patch','delete'}}
api=(ROOT/'docs/engineering/API_REFERENCE.md').read_text(encoding='utf-8')
documented=re.findall(r'^\| (GET|POST|PUT|PATCH|DELETE) \| `([^`]+)`',api,re.M)
for operation in documented:
    if tuple(operation) not in operations:errors.append('API route absent from generated contract: '+' '.join(operation))

register=json.loads((ROOT/'docs/pitch/project-links.json').read_text(encoding='utf-8'))
placeholders={k:v['url'] for k,v in register.items() if isinstance(v,dict) and v.get('placeholder')}
for key,url in placeholders.items():
    if urlsplit(url).hostname!='example.com':errors.append('Unexpected placeholder domain: '+key)
    if register[key].get('public_access_verified'):errors.append('Placeholder marked publicly verified: '+key)

result={'checked_on':'2026-11-05','documents':len(FILES),'relative_links_checked':links,
        'html_images_with_alt':images,'unique_external_urls':len(external),
        'documented_api_operations_checked':len(documented),'intentional_placeholders':placeholders,
        'errors':errors,'result':'PASS' if not errors else 'FAIL',
        'scope':'Local paths, anchors, case, SVG XML, API route presence and placeholder labels; not external availability or full product acceptance.'}
report=ROOT/'docs/qa/evidence/documentation-links-2026-11-05.json'
report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(bool(errors))
