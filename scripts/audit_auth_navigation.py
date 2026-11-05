"""Ebarki live local BFF auth checks. Does not claim browser interaction coverage."""
import json
import re
import secrets
import subprocess
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'services/backend'))
from app.core.config import settings

BASE = 'http://localhost:3000'
checks = []


def check(name, condition):
    checks.append({'test': name, 'result': 'PASS' if condition else 'FAIL'})
    print(checks[-1]['result']+': '+name, flush=True)


def bearer(data):
    return {'Authorization': 'Bearer '+data['access_token']}


password = secrets.token_urlsafe(24)
email = 'fictional-auth-'+secrets.token_hex(6)+'@qa.invalid'
with httpx.Client(base_url=BASE, timeout=90, headers={'Origin': BASE}) as consumer, httpx.Client(base_url=BASE, timeout=90, headers={'Origin': BASE}) as admin:
    for locale in ['en', 'bn']:
        for path in ['login', 'admin/login', 'admin']:
            response = consumer.get(f'/{locale}/{path}')
            check(f'{locale}/{path} server route renders session-check state', response.status_code == 200 and 'ui-loading' in response.text)
    registration = consumer.post('/api/v1/auth/register', json={'email': email, 'password': password, 'full_name': 'FICTIONAL Ebarki Auth QA'})
    check('BFF synthetic consumer registration', registration.status_code == 201)
    consumer_session = registration.json()
    headers = bearer(consumer_session)
    check('BFF signed-in consumer profile', consumer.get('/api/v1/auth/me', headers=headers).json().get('logged_in') is True)
    denied = consumer.post('/api/v1/auth/admin-login', json={'email': email, 'password': password})
    check('BFF consumer staff login denied without replacing cookie', denied.status_code == 403 and 'set-cookie' not in denied.headers)
    check('BFF consumer cannot read admin stats', consumer.get('/api/v1/admin/stats', headers=headers).status_code == 403)
    created = consumer.post('/api/v1/cases', headers=headers, json={'title': 'Ebarki FICTIONAL auth regression', 'story_narrative': 'Synthetic session-persistence check. No real purchase or personal record.'})
    check('BFF new synthetic case creation', created.status_code == 201)
    case_id = created.json().get('id')
    logout = consumer.post('/api/v1/auth/logout', headers=headers)
    check('BFF consumer logout clears cookie', logout.status_code == 200 and 'Max-Age=0' in logout.headers.get('set-cookie', ''))
    check('BFF logged-out consumer JWT rejected', consumer.get('/api/v1/auth/me', headers=headers).status_code == 401)
    check('BFF logged-out consumer private case rejected', consumer.get(f'/api/v1/cases/{case_id}', headers=headers).status_code == 401)
    relogin = consumer.post('/api/v1/auth/login', json={'email': email, 'password': password})
    check('BFF consumer can log in again', relogin.status_code == 200)
    headers = bearer(relogin.json())
    reopened = consumer.get(f'/api/v1/cases/{case_id}', headers=headers)
    check('BFF owned case persists after logout and relogin', reopened.status_code == 200 and reopened.json().get('title') == 'Ebarki FICTIONAL auth regression')
    consumer.post('/api/v1/auth/logout', headers=headers)

    historical = subprocess.check_output(['git', 'show', '33c59b3:apps/web/src/features/workspace/Account.tsx'], cwd=ROOT, text=True, encoding='utf8')
    match = re.search(r"auth/login['\"],\s*\{\s*email:\s*['\"]([^'\"]+)['\"],\s*password:\s*['\"]([^'\"]+)['\"]", historical)
    if match:
        old = admin.post('/api/v1/auth/admin-login', json={'email': match[1], 'password': match[2]})
        check('BFF historical exposed admin password rejected', old.status_code == 401)
    login = admin.post('/api/v1/auth/admin-login', json={'email': settings.BOOTSTRAP_ADMIN_EMAIL, 'password': settings.BOOTSTRAP_ADMIN_PASSWORD})
    check('BFF privately configured administrator login', login.status_code == 200)
    if login.status_code == 200:
        credentials = login.json(); admin_headers = bearer(credentials)
        check('BFF authenticated administrator has admin role', 'admin' in credentials.get('roles', []))
        check('BFF administrator cookie resolves signed-in profile', admin.get('/api/v1/auth/me').json().get('logged_in') is True)
        stats = admin.get('/api/v1/admin/stats', headers=admin_headers)
        check('BFF administrator stats endpoint serves actual metrics', stats.status_code == 200 and isinstance(stats.json().get('metrics', {}).get('total_cases'), int))
        check('BFF administrator users panel authorized', admin.get('/api/v1/admin/users', headers=admin_headers).status_code == 200)
        check('BFF administrator logout succeeds', admin.post('/api/v1/auth/logout', headers=admin_headers).status_code == 200)
        check('BFF logged-out admin JWT rejected', admin.get('/api/v1/admin/stats', headers=admin_headers).status_code == 401)

receipt = {'product': 'Ebarki', 'scope': 'Local live Next BFF + FastAPI HTTP, synthetic consumer and repaired local administrator; not browser acceptance.', 'credential_values_recorded': False, 'checks': checks}
(ROOT/'docs/qa/evidence/auth-live-bff.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
raise SystemExit(1 if any(item['result'] == 'FAIL' for item in checks) else 0)
