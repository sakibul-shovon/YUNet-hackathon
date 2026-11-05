"""Ebarki release checks that do not need browser input; never prints secrets."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'services/backend'))
from app.core.config import Settings, settings

OUT = ROOT/'docs/qa/evidence'
OUT.mkdir(parents=True, exist_ok=True)
checks = []


def record(test, result, **details):
    checks.append({'test': test, 'result': result, **details})
    print(result+': '+test, flush=True)


configured = [getattr(settings, field) for field in ['GROQ_API_KEY','GEMINI_API_KEY','APP_SECRET_KEY','JWT_SECRET_KEY','BOOTSTRAP_ADMIN_PASSWORD']
              if getattr(settings, field) and getattr(settings, field) != Settings.model_fields[field].default]
paths = {ROOT/path for path in subprocess.check_output(
    ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode('utf8').split('\0') if path}
paths.update(path for directory in [ROOT/'docs/qa', ROOT/'apps/web/.next-check/static'] if directory.exists()
             for path in directory.rglob('*') if path.is_file())
paths.update(path for directory in (ROOT/'apps/web').glob('.next*/static')
             for path in directory.rglob('*') if path.is_file())
leaks = []
checked_paths = 0
for path in paths:
    if not path.is_file() or path.stat().st_size > 35*1024*1024:
        continue
    raw = path.read_bytes()
    checked_paths += 1
    if any(value.encode() in raw for value in configured):
        leaks.append(str(path.relative_to(ROOT)))
record('configured secrets absent from tracked files, QA artifacts and built client assets',
       'FAIL' if leaks else 'PASS', matches=leaks, files_checked=checked_paths)

fixture_mismatches = []
index_mismatches = []
indexed = 0
fixture_count = 0
for manifest_path in (ROOT/'docs/qa/fixtures').rglob('GROUND_TRUTH.json'):
    manifest = json.loads(manifest_path.read_text(encoding='utf8'))
    for name, ground_truth in manifest['files'].items():
        fixture = manifest_path.parent/name
        fixture_count += 1
        if hashlib.sha256(fixture.read_bytes()).hexdigest() != ground_truth['sha256']:
            fixture_mismatches.append(name)
        relative = fixture.relative_to(ROOT).as_posix()
        staged = subprocess.run(['git', 'cat-file', 'blob', ':'+relative], cwd=ROOT,
                                capture_output=True, check=False)
        if staged.returncode == 0:
            indexed += 1
            if staged.stdout != fixture.read_bytes():
                index_mismatches.append(name)
record('fixture files match recorded ground-truth hashes',
       'FAIL' if fixture_mismatches else 'PASS', mismatches=fixture_mismatches,
       files_checked=fixture_count)
record('Git preserves indexed fixture bytes without newline conversion',
       'FAIL' if index_mismatches else 'PASS', mismatches=index_mismatches,
       files_checked=indexed, note='Oversized PCM recording is intentionally ignored by Git.')

with httpx.Client(timeout=40) as client:
    if '--followup' in sys.argv:
        for language in ['en', 'bn']:
            for route in ['login', 'admin/login']:
                response = client.get(f'http://127.0.0.1:3000/{language}/{route}')
                valid = response.status_code == 200 and all(marker in response.text for marker in [
                    'ag-access-options', 'ag-access-judge-prominent', f'href="/{language}/login"', f'href="/{language}/admin/login"'])
                record(language+'/'+route+' access choices in server-rendered HTML', 'PASS' if valid else 'FAIL',
                       note='HTML structure only; native rendered interaction remains BLOCKED.')
            response = client.get(f'http://127.0.0.1:3000/{language}/cases')
            record(language+' workspace near-top sticker in HTML',
                   'PASS' if response.status_code == 200 and 'ui-event-sticker' in response.text else 'FAIL',
                   note='Source/HTML positioning; fresh rendered mobile/desktop verification remains BLOCKED.')
    for language in ([] if '--final-only' in sys.argv else ['en','bn']):
        for route in ['', '/how-it-works','/technology','/sources','/limitations','/privacy','/help',
                      '/merchants','/community','/scenarios','/login','/register','/admin/login','/settings','/cases/new']:
            response = client.get('http://127.0.0.1:3000/'+language+route)
            record(language+(route or '/ landing')+' HTTP route', 'PASS' if response.status_code == 200 else 'FAIL',
                   status=response.status_code, note='HTTP rendering only; does not prove browser interactions')
    schema = client.get('http://127.0.0.1:8000/openapi.json').json()
    inventory = [{'path': path, 'methods': list(methods),
                  'tags': sorted({tag for spec in methods.values() for tag in spec.get('tags',[])})}
                 for path, methods in schema['paths'].items() if path.startswith('/v1/')]
    (OUT/'api-route-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf8')
    committed = json.loads((ROOT/'packages/contracts/openapi.json').read_text(encoding='utf8'))
    record('generated OpenAPI matches running API', 'PASS' if schema == committed else 'FAIL')
record('public HTTPS deployment', 'UNVERIFIED', reason='Deferred by user for the follow-up; not tested here.')
(OUT/('followup-environment-validation.json' if '--followup' in sys.argv else 'final-environment-validation.json' if '--final-only' in sys.argv else 'environment-validation.json')).write_text(json.dumps(checks,indent=2)+'\n',encoding='utf8')
print('Checked '+str(len(checks))+' environment/route conditions.')
raise SystemExit(1 if any(check['result'] == 'FAIL' for check in checks) else 0)
