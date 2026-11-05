# Local development and configuration

[Documentation](../README.md) · [Versions](versions.md) · [Provider behavior](providers.md)

## Prerequisites

Python 3.12 is the exercised backend interpreter; the package declares Python >=3.11. Use Node.js >=20, pnpm **12.16.1**, uv and Git. The observed host had Node 24.20.0 and uv 0.13.5. [Versions](versions.md) distinguishes package constraints from installed versions.

## Fresh clone

```sh
git clone https://github.com/sakibul-shovon/YUNet-hackathon.git
cd YUNet-hackathon
python scripts/tasks.py bootstrap
python scripts/tasks.py doctor
python scripts/tasks.py dev --no-reload
```

The web app opens at `http://localhost:3000/en` or `/bn`; FastAPI at `http://127.0.0.1:8000`, with `/docs` and `/openapi.json`.

The development command terminates listeners on ports 3000/8000 and clears `apps/web/.next` before launching. Use it when you intend to own those development ports. `--no-reload` keeps the API stable for provider demos. Ctrl+C stops the launched stack.

Development defaults to SQLite and local storage. Fresh development startup creates its schema. Production is stricter and requires migrated tables. Do not apply fresh-database instructions blindly to an existing valuable database.

## Server configuration

The backend runs with `services/backend` as its working directory and loads `.env` there. Environment variables take precedence. The root [example](../../.env.example) is a reference containing both current and historical integration settings; copying it unchanged selects PostgreSQL rather than the native SQLite default.

For a new local configuration, create **`services/backend/.env`** with only the values you need:

```dotenv
APP_ENV=development
DATABASE_URL=sqlite+aiosqlite:///./local_dev.db
LOCAL_STORAGE_DIR=./storage
FRONTEND_ORIGIN=http://localhost:3000
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# Optional, server-side provider configuration
GROQ_API_KEY=replace-with-your-own-key
GROQ_MODEL=openai/gpt-oss-120b
GROQ_VISION_MODEL=qwen/qwen3.8-27b
GROQ_TRANSCRIBE_MODEL=whisper-large-v3
```

Omit `GROQ_API_KEY` when using local/manual paths; do not leave a fake key enabled and expect inference to work. Never copy actual secrets into documentation, screenshots, browser code or Git.

The web BFF uses `BACKEND_API_URL` server-side. For a non-default API, set it in the web process environment or **`apps/web/.env.local`**. Do not give it a `NEXT_PUBLIC_` prefix. Restart after changing server configuration.

## Optional administrator setup

For a controlled local operator account, configure `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD` on the server before its first login. Use `/en/admin/login` or `/bn/admin/login`. There is no documented shared production password.

The separate **Judge Admin 1-Click** entry grants real global roles without operator credentials. It is for synthetic evaluation only and is not currently environment-gated. [Administration](../ADMIN_PORTAL_GUIDE.md) explains this distinction.

## Database migrations and production-mode testing

For a **fresh, disposable database** with the intended connection configured:

```sh
python scripts/tasks.py backend run alembic upgrade head
```

The migration head is `0007_workspace_persistence`. An existing database created without Alembic history needs schema inspection and a controlled baseline; do not blindly stamp, downgrade or delete it.

Production mode requires separately configured `APP_SECRET_KEY` and `JWT_SECRET_KEY`, each at least 32 characters and different from the published development defaults. Configure correct origins, secure transport and durable storage. These settings alone do not make the current demo endpoints or public-data stores production-ready.

`infra/compose.yaml` is deployment scaffolding with development example values. Its existence is not a tested production recipe. Hosted PostgreSQL, RLS, backups and persistent volumes need independent acceptance.

## Common tasks

| Goal | Command |
| --- | --- |
| Check tools/provider configuration | `python scripts/tasks.py doctor` |
| Check task state/source-document integrity | `python scripts/tasks.py status` |
| Start only the web app | `python scripts/tasks.py web dev` |
| Lint, translations, build and typecheck | `python scripts/tasks.py check --scope foundation` |
| Backend and web tests | `python scripts/tasks.py check --scope core` |
| Regenerate API contracts | `python scripts/tasks.py contracts` |
| Query code relationships | `python scripts/tasks.py graphify query "How does source review affect payment reconciliation?"` |

Foundation uses `.next-check` to avoid the development build directory. Next.js may update generated type/config files during builds; inspect those changes before including them in a patch.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| AI summary absent | Server key/model, applicable case consent and actual run receipt; doctor checks configuration only |
| OCR/transcription unavailable | File quality/type, consent, provider quota and reader error; keep the original for manual review |
| API unreachable | BFF backend URL and API listener; avoid mixing `localhost` origins unexpectedly |
| Production startup refuses schema | Correct database URL, migration history and actual table/column parity |
| Login succeeds but admin action is forbidden | Correct server-assigned role and session; consumer Judge Demo has no administrative role |
| Community changes vanish | Current comments/reactions are process-local preview data |
| Windows backend interpreter differs | Task runner prefers `%LOCALAPPDATA%/claimcraft-venv/Scripts/python.exe` when present; inspect its version/dependencies |

A fresh clone setup was source-reviewed during this documentation refresh; dependencies were not reinstalled into a clean machine. Existing test and process receipts are scoped in [current status](../qa/CURRENT_STATUS.md).
