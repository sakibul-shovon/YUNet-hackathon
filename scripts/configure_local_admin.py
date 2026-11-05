"""Provision missing LOCAL Ebarki bootstrap configuration without printing credentials."""
import asyncio
import json
import secrets
import sys
import re
import subprocess
import datetime
from pathlib import Path

from sqlalchemy import func, select, update

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'services/backend'))
from app.core.config import settings
from app.core.database import async_session_factory
from app.identity.models import ActorRole, UserAccount, WebSession
from app.identity.service import hash_password, verify_password
from app.admin.service import AdminService


def save_private_configuration(email, password):
    environment_file = ROOT/'services/backend/.env'
    lines = environment_file.read_text(encoding='utf8').splitlines() if environment_file.exists() else []
    for name, value in [('BOOTSTRAP_ADMIN_EMAIL', email), ('BOOTSTRAP_ADMIN_PASSWORD', password)]:
        replacement = f'{name}={value}'
        if any(line.startswith(name+'=') for line in lines):
            lines = [replacement if line.startswith(name+'=') else line for line in lines]
        else:
            lines.append(replacement)
    environment_file.write_text('\n'.join(lines)+'\n', encoding='utf8')
    private_file = ROOT/'services/backend/data/local-admin-access.txt'
    private_file.parent.mkdir(parents=True, exist_ok=True)
    private_file.write_text('Ebarki LOCAL administrator access. Never commit or share this file.\n'
                           f'Email: {email}\nPassword: {password}\n', encoding='utf8')
    return {'bootstrap_configured': True, 'restart_required': True,
            'credential_file': str(private_file.relative_to(ROOT)), 'credential_values_printed': False}


async def main():
    async with async_session_factory() as database:
        administrators = await database.scalar(select(func.count()).select_from(ActorRole).where(ActorRole.role == 'admin'))
    result = {'product': 'Ebarki', 'existing_admin_role_count': administrators,
              'bootstrap_configured': bool(settings.BOOTSTRAP_ADMIN_EMAIL and settings.BOOTSTRAP_ADMIN_PASSWORD)}
    if '--rotate-exposed-default' in sys.argv:
        if settings.APP_ENV != 'development':
            raise SystemExit('Local administrator repair is limited to development.')
        # Fixed historical revision: never reset an arbitrary administrator account.
        historical = subprocess.check_output(['git', 'show', '33c59b3:apps/web/src/features/workspace/Account.tsx'], cwd=ROOT, text=True, encoding='utf8')
        match = re.search(r"auth/login['\"],\s*\{\s*email:\s*['\"]([^'\"]+)['\"],\s*password:\s*['\"]([^'\"]+)['\"]", historical)
        if not match:
            raise SystemExit('Historical exposed credential could not be identified; no account changed.')
        async with async_session_factory() as database:
            account = await database.scalar(select(UserAccount).join(ActorRole, ActorRole.principal_id == UserAccount.principal_id).where(ActorRole.role == 'admin', UserAccount.email == match[1]))
            if account and verify_password(match[2], account.password_hash):
                password = secrets.token_urlsafe(32)
                # Save recovery details before the database transaction is committed.
                result.update(save_private_configuration(account.email, password))
                account.password_hash = hash_password(password)
                await database.execute(update(WebSession).where(WebSession.principal_id == account.principal_id, WebSession.revoked_at.is_(None)).values(revoked_at=datetime.datetime.now(datetime.UTC)))
                await AdminService.record_audit(database, 'local-security-repair', 'rotate_exposed_default', str(account.principal_id), {'reason': 'Removed legacy client-embedded password', 'sessions_revoked': True})
                await database.commit()
                result['exposed_default_rotated'] = True
            else:
                result['exposed_default_rotated'] = False
    if '--configure' in sys.argv and not administrators and not result['bootstrap_configured']:
        if settings.APP_ENV != 'development':
            raise SystemExit('Local administrator setup is limited to development.')
        email = settings.BOOTSTRAP_ADMIN_EMAIL or 'admin@ebarki.local'
        password = settings.BOOTSTRAP_ADMIN_PASSWORD or secrets.token_urlsafe(32)
        result.update(save_private_configuration(email, password))
    print(json.dumps(result))


asyncio.run(main())
