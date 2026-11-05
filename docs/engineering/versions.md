# Toolchain and dependency register

Observed locally on **5 November 2026**. Package constraints, lockfile resolutions and an installed environment are different things. Use the committed lockfiles when reproducing the project; this table is an observed snapshot, not a claim that these are the newest releases.

## Runtimes

| Tool | Project requirement / observed version |
| --- | --- |
| Backend Python | Declared >=3.11; task-runner-selected interpreter **3.12.15** |
| Shell Python | Host doctor reported **3.15.2**; this differs from the selected backend environment |
| Node.js | Declared >=20; host **24.20.0** |
| pnpm | `packageManager` **12.16.1** |
| uv | Host **0.13.5** |

## Observed application packages

| Layer | Package | Installed version |
| --- | --- | --- |
| Web | Next.js | 15.5.28 |
| Web | React | 19.3.1 |
| Web | next-intl | 3.26.5 |
| Web | TypeScript | 5.9.3 |
| Web | Tailwind CSS | 3.4.19 |
| Web tests | Vitest | 5.1.0 |
| API | FastAPI | 0.162.0 |
| Validation | Pydantic | 2.14.2 |
| Persistence | SQLAlchemy | 2.1.8 |
| Migrations | Alembic | 1.20.1 |
| Backend tests | pytest | 9.2.0 |
| Lint | Ruff | 0.17.3 |
| PDF | pypdf / pypdfium2 | 6.21.4 / 5.14.0 |
| HTTP | httpx | 0.28.1 |

The former register mixed candidate AI services with implemented behavior and listed stale installed versions. This snapshot was refreshed by reading package metadata through the task runner.

## Reproduction sources

- [Root package manifest](../../package.json) and [web manifest](../../apps/web/package.json)
- [pnpm lockfile](../../pnpm-lock.yaml)
- [Backend manifest](../../services/backend/pyproject.toml) and [uv lockfile](../../services/backend/uv.lock)
- [Provider methods](providers.md): configuration defaults and observed calls


```sh
python scripts/tasks.py doctor
python scripts/tasks.py bootstrap
```

The task runner can prefer an existing Windows backend environment. Confirm that environment's metadata when diagnosing a mismatch; bootstrap success alone does not prove it is the interpreter later selected for tests.
