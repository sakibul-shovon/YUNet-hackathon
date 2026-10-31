# ClaimCraft BD — Pinned Toolchain & Dependency Register

Prepared as required by plan.md Section 7 & Section 8.

## Runtime & Toolchain Versions
| Tool / Runtime | Pinned Version / Constraint | Verified Host Version | Status |
|---|---|---|---|
| Python | `>=3.11` (Target: 3.12) | 3.11 / 3.15 | Verified via uv |
| uv | `>=0.13` | 0.13.5 | Pinned tool |
| Node.js | `>=20.0.0` (LTS) | 24.20.0 | Verified |
| pnpm | `12.16.1` | 12.16.1 | Lockfile pinned |

## Application Stack
| Layer | Package / Technology | Version | Location |
|---|---|---|---|
| Web Framework | Next.js | `15.5.28` (App Router) | `apps/web` |
| UI Library | React / React DOM | `19.3.1` | `apps/web` |
| Styling | Tailwind CSS | `3.4.17` / PostCSS `8.5.1` | `apps/web` |
| Internationalization | next-intl | `3.26.3` | `apps/web` |
| Icons | Lucide React | `0.474.0` | `apps/web` |
| Validation | Zod | `3.24.1` | `apps/web` |
| Form State | React Hook Form | `7.54.2` | `apps/web` |
| API Framework | FastAPI | `0.162.0` | `services/backend` |
| Schema Validation | Pydantic v2 | `2.14.2` | `services/backend` |
| Database ORM | SQLAlchemy | `2.1.6` | `services/backend` |
| DB Migrations | Alembic | `1.20.1` | `services/backend` |
| PostgreSQL Client | psycopg / psycopg-binary | `3.3.6` | `services/backend` |
| Testing | pytest / pytest-asyncio | `9.2.0` / `1.4.1` | `services/backend` |
| Linter / Formatter | ruff | `0.17.3` | `services/backend` |

## AI & Multimodal Providers (Section 7)
- **Primary LLM/VLM candidate:** Google Gemini (`gemini-3.8-flash`) via Google GenAI SDK.
- **Speech-to-Text:** Google Cloud STT V2 (`bn-BD` with `chirp_2` model in `asia-southeast1`).
- **Dense Embeddings:** `intfloat/multilingual-e5-small` (384-dimensional).
- **Lexical Search:** `bm25s` with Bengali-aware tokenization.
