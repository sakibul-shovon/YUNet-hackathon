"""Isolated local production-mode restart/security test; no public deployment."""
import hashlib
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT/'services/backend/data'/('qa-production-'+secrets.token_hex(6))
WORK.mkdir(parents=True)
PORT = 8017
URL = f'http://127.0.0.1:{PORT}'
checks = []
admin_email = 'fictional-admin-'+secrets.token_hex(5)+'@qa.invalid'
admin_password = secrets.token_urlsafe(28)
consumer_password = secrets.token_urlsafe(28)
consumer_email = 'fictional-consumer-'+secrets.token_hex(5)+'@qa.invalid'
environment = {**os.environ, 'APP_ENV': 'production',
    'APP_SECRET_KEY': secrets.token_urlsafe(48), 'JWT_SECRET_KEY': secrets.token_urlsafe(48),
    'DATABASE_URL': 'sqlite+aiosqlite:///'+str((WORK/'audit.db').resolve()).replace('\\', '/'),
    'LOCAL_STORAGE_DIR': str((WORK/'vault').resolve()),
    'BOOTSTRAP_ADMIN_EMAIL': admin_email, 'BOOTSTRAP_ADMIN_PASSWORD': admin_password,
    'GROQ_API_KEY': '', 'GEMINI_API_KEY': '',
}


def check(name, condition):
    checks.append({'test': name, 'result': 'PASS' if condition else 'FAIL'})
    print(checks[-1]['result']+': '+name, flush=True)
    (ROOT/'docs/qa/evidence/followup-production-mode.json').write_text(json.dumps({
        'product': 'Ebarki', 'scope': 'Local APP_ENV=production, SQLite and configured disk vault; real process restart. No public TLS/PostgreSQL/backup claims.',
        'checks': checks}, indent=2)+'\n', encoding='utf8')


def start():
    log = (WORK/'api.log').open('ab')
    process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', str(PORT)],
        cwd=ROOT/'services/backend', env=environment, stdout=log, stderr=log,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    log.close()
    for _ in range(100):
        try:
            if httpx.get(URL+'/health/live', timeout=1).status_code == 200:
                return process
        except httpx.HTTPError:
            pass
        if process.poll() is not None:
            raise RuntimeError('Isolated production API startup failed; inspect ignored local log.')
        time.sleep(.2)
    raise RuntimeError('Isolated production API startup timed out.')


def stop(process):
    process.terminate()
    process.wait(timeout=15)


def auth(data):
    return {'Authorization': 'Bearer '+data['access_token']}


try:
    unexpected = start()
except RuntimeError:
    check('production startup refuses an unmigrated database',
          'Ebarki production database migrations must be applied before startup.' in (WORK/'api.log').read_text(encoding='utf8'))
else:
    stop(unexpected)
    check('production startup refuses an unmigrated database', False)
migration = subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'],
    cwd=ROOT/'services/backend', env=environment, capture_output=True)
check('production schema migration succeeds', migration.returncode == 0)
if migration.returncode:
    raise RuntimeError('Isolated migration failed.')
process = start()
try:
    with httpx.Client(base_url=URL, timeout=20) as consumer, httpx.Client(base_url=URL, timeout=20) as admin:
        registration = consumer.post('/v1/auth/register', json={'email': consumer_email,
            'password': consumer_password, 'full_name': 'Fictional production QA consumer'})
        check('production registration succeeds', registration.status_code == 201)
        credentials = registration.json()
        cookie = registration.headers.get('set-cookie', '')
        check('production cookie Secure HttpOnly SameSite and path', all(part in cookie for part in ['Secure', 'HttpOnly', 'SameSite=lax', 'Path=/']))
        check('authentication response is private no-store', registration.headers.get('cache-control') == 'private, no-store')
        headers = auth(credentials)
        denied = consumer.post('/v1/auth/admin-login', json={'email': consumer_email, 'password': consumer_password})
        check('consumer admin entry rejected before setting a session', denied.status_code == 403 and 'set-cookie' not in denied.headers)
        login = admin.post('/v1/auth/admin-login', json={'email': admin_email, 'password': admin_password})
        check('configured synthetic administrator login', login.status_code == 200)
        admin_headers = auth(login.json())
        check('consumer admin API isolation', consumer.get('/v1/admin/users', headers=headers).status_code == 403)
        case = consumer.post('/v1/cases', headers=headers, json={'title': 'Ebarki FICTIONAL restart QA',
            'story_narrative': 'No real transaction. This case checks durable storage.'}).json()
        case_path = '/v1/cases/'+case['id']
        data = (ROOT/'docs/qa/fixtures/receipt text.pdf').read_bytes()
        intent = consumer.post('/v1/uploads/init', headers=headers, json={'case_id': case['id'],
            'declared_filename': 'Fictional receipt.pdf', 'declared_mime_type': 'application/pdf', 'declared_byte_size': len(data)}).json()
        consumer.put('/v1/uploads/'+intent['intent_id']+'/raw', params={'token': intent['upload_token']}, headers=headers, content=data)
        evidence = consumer.post('/v1/uploads/'+intent['intent_id']+'/complete', headers=headers).json()
        check('configured disk vault receives accepted evidence', any((WORK/'vault/accepted').glob('*')))
        alert = admin.post('/v1/admin/alerts', headers=admin_headers, json={'title': 'FICTIONAL QA only',
            'title_en': 'FICTIONAL QA only', 'severity': 'info', 'message': 'Local synthetic restart test.', 'active': True}).json()
        # In this isolated database only, ban our owned consumer, then restart the process.
        user = next(user for user in admin.get('/v1/admin/users', headers=admin_headers).json() if user['principal_id'] == credentials['principal_id'])
        promoted = admin.post('/v1/admin/users/'+user['id']+'/roles', headers=admin_headers,
                              json={'roles': ['consumer', 'reviewer']})
        check('authorized synthetic reviewer-role assignment', promoted.status_code == 200)
        banned = admin.post('/v1/admin/users/'+user['id']+'/toggle-ban', headers=admin_headers)
        check('synthetic user ban committed', banned.status_code == 200 and banned.json()['is_banned'])
        stop(process)
        process = start()
        check('administrator session survives real process restart', admin.get('/v1/auth/me', headers=admin_headers).status_code == 200)
        check('public active alert survives restart', any(item['id'] == alert['alert']['id'] for item in consumer.get('/v1/admin/alerts').json()))
        check('administrative audit survives restart', any(item['action'] == 'BAN_USER' for item in admin.get('/v1/admin/audit-logs', headers=admin_headers).json()))
        check('suspension survives restart and blocks login', consumer.post('/v1/auth/login', json={'email': consumer_email, 'password': consumer_password}).status_code == 403)
        check('old banned session remains rejected', consumer.get('/v1/auth/me', headers=headers).status_code in {401, 403})
        admin.post('/v1/admin/users/'+user['id']+'/toggle-ban', headers=admin_headers)
        check('unban requires a new login', consumer.get('/v1/auth/me', headers=headers).status_code == 401)
        relogin = consumer.post('/v1/auth/login', json={'email': consumer_email, 'password': consumer_password})
        headers = auth(relogin.json())
        check('assigned reviewer role persists across restart', 'reviewer' in relogin.json()['roles'])
        check('private case survives restart', consumer.get(case_path, headers=headers).json()['title'] == case['title'])
        preview = consumer.get(case_path+'/evidence/'+evidence['id']+'/preview', headers=headers)
        check('private evidence bytes survive restart', preview.status_code == 200 and hashlib.sha256(preview.content).digest() == hashlib.sha256(data).digest())
        consumer.post('/v1/auth/logout', headers=headers)
        check('logout immediately revokes production bearer token', consumer.get('/v1/auth/me', headers=headers).status_code == 401)
        check('cross-origin login blocked', consumer.post('/v1/auth/login', headers={'Origin': 'https://untrusted.invalid'},
            json={'email': consumer_email, 'password': consumer_password}).status_code == 403)
finally:
    stop(process)

raise SystemExit(1 if any(item['result'] == 'FAIL' for item in checks) else 0)
