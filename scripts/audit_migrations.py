"""Compare a fresh migrated database with Ebarki's actual runtime schema."""
import asyncio
import json
import os
import secrets
import subprocess
import sys
from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'services/backend'))
from app.core.database import Base
from app.main import app  # noqa: F401 - registers the actual application's model metadata

WORK = ROOT/'services/backend/data'/('qa-schema-'+secrets.token_hex(6))
WORK.mkdir(parents=True)
url = 'sqlite+aiosqlite:///'+str((WORK/'migrations.db').resolve()).replace('\\', '/')
environment = {**os.environ, 'DATABASE_URL': url}
completed = subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'],
    cwd=ROOT/'services/backend', env=environment, capture_output=True)


async def main():
    engine = create_async_engine(url)
    async with engine.connect() as connection:
        def compare(sync):
            inspector = inspect(sync)
            tables = set(inspector.get_table_names())
            missing_tables = sorted(set(Base.metadata.tables)-tables)
            missing_columns = {}
            for name, table in Base.metadata.tables.items():
                if name in tables:
                    missing = set(table.columns.keys())-{column['name'] for column in inspector.get_columns(name)}
                    if missing:
                        missing_columns[name] = sorted(missing)
            return missing_tables, missing_columns
        tables, columns = await connection.run_sync(compare)
    await engine.dispose()
    result = {'product': 'Ebarki', 'scope': 'Fresh local SQLite Alembic upgrade vs runtime table/column presence; not PostgreSQL RLS or backup verification.',
              'migration_exit_code': completed.returncode, 'missing_tables': tables, 'missing_columns': columns,
              'result': 'PASS' if completed.returncode == 0 and not tables and not columns else 'FAIL'}
    (ROOT/'docs/qa/evidence/followup-migration-schema.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8')
    print(json.dumps(result))
    raise SystemExit(0 if result['result'] == 'PASS' else 1)


asyncio.run(main())
