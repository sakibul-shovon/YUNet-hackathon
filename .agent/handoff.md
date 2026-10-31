# ClaimCraft BD — Agent Handoff

## Execution Status
- **Completed Phases:**
  - **P00 (Foundation & Compatibility):** 100% COMPLETE & VERIFIED (`9701af14cd10c25e4b6f0b0d0c6a8924da73ff82`)
  - **P01 (Design System & Connected Shell):** 100% COMPLETE & VERIFIED (`5472bb63612157ded81cca5e3fef9763e4ec0f27`)
  - **P02 (Identity, Ownership, Persistence & Secure Sessions):** 100% COMPLETE & READY TO PUSH
- **Active Phase:** P03 (Governed initial sources and deterministic policy skeleton)
- **Active Task:** P03.1 (Create source registry from blueprint, official host allowlist, feed metadata and actual check results)
- **Last Completed Task:** P02.6 (Generated TS client and real UI integration for list/intake/overview)
- **Required Tasks Progress:** 17 / 86 (19.8% complete, 0 blocked)
- **Phase Delivery History:**
  - P00 SHA: `9701af14cd10c25e4b6f0b0d0c6a8924da73ff82` (Verified on `origin/main`)
  - P01 SHA: `5472bb63612157ded81cca5e3fef9763e4ec0f27` (Verified on `origin/main`)
  - P02 SHA: Verified after push below

## What Works
- **Phase P00 (Foundation & Compatibility):**
  - Modular FastAPI backend with live health endpoints (`/health/live`, `/health/ready`).
  - Next.js 15 BFF web application with TypeScript, Tailwind CSS, and `next-intl`.
  - Pinned lockfiles (`uv.lock`, `pnpm-lock.yaml`), container specs, CI workflows, and task runner `scripts/tasks.py`.
  - Architectural decisions ADR-101 through ADR-109 documented.
  - Reproducible OpenAPI schema and TypeScript contract generator.
- **Phase P01 (Design System & Connected Experience Shell):**
  - Section 5 Design Tokens in `globals.css` with verified WCAG 2.2 AA contrast ratios in both light (default) and dark themes.
  - Accessible UI primitives: `Button`, `Card`, `Badge`, `Input`, `Textarea`, `EmptyState`, `LoadingState`, `ErrorState`, `ThemeToggle`, `LanguageToggle`.
  - Complete SaaS Landing Page with 8 structured sections, interactive product composition preview, and honest event sticker slot.
  - Five Connected Case Views (`Overview`, `Evidence`, `Paths`, `Actions`, `Activity`) + `Intake`, `Fact Review`, `Cases List`, and `Scenario Gallery`.
  - 100% Bilingual parity verified across 154 message keys via `scripts/verify_i18n.py`.
  - Automated T49 & T50 test suites passing via pytest in `tests/unit/test_t49_t50_bilingual_themes.py`.
- **Phase P02 (Identity, Ownership, Persistence & Secure Sessions):**
  - **P02.1 Database & RLS:** 11 core tables (`principals`, `web_sessions`, `actor_roles`, `cases`, `case_snapshots`, `issue_tracks`, `case_events`, `external_references`, `consents`, `deletion_requests`, `outbox`) created. Alembic migration `0001_initial` verified for both upgrade and downgrade round-trips. PostgreSQL RLS policies defined.
  - **P02.2 Opaque Sessions & Auth:** Opaque HttpOnly BFF cookie session management with SHA-256 token hashing, anonymous guest bootstrap (`/auth/guest`), short-lived HS256 access JWTs (15 min), CSRF protection, and mandatory `Cache-Control: private, no-store` response headers.
  - **P02.3 Case CRUD & Concurrency:** Case creation, list, detail, update, and soft deletion. Strict tenant isolation (non-enumerating 404 for foreign or deleted cases). Optimistic locking via `row_version` with `409 CASE_VERSION_CONFLICT` on stale edits. Immutable snapshot versioning and chronological audit events.
  - **P02.4 Account Upgrade:** Account upgrade (`/auth/upgrade`) converts anonymous guest to permanent verified principal while preserving existing case ownership and data.
  - **P02.5 Consent & Immediate Access Revocation:** Versioned consent tracking (`/v1/consents`). Deletion requests (`/v1/deletions`) immediately revoke case access (`access_revoked_at`), set lifecycle status to `deleting`, and enqueue outbox cleanup tasks.
  - **P02.6 TS Client & Web UI Integration:** `@claimcraft/contracts` regenerated via `python scripts/tasks.py contracts`. Next.js `IntakeForm.tsx` and `cases/page.tsx` wired to backend endpoints with fallback protection.
  - **Behavior Tests T01–T04 Verified:**
    - T01: Cross-tenant isolation (foreign cases return 404, random UUIDs return 404).
    - T02: Token signature/issuer/audience/expiry validation and role escalation protection.
    - T03: Connection pool tenant context hygiene.
    - T04: Story, remedy, outcomes durability, optimistic concurrency 409 conflict handling, and activity timeline.

## Test Evidence
- `python scripts/tasks.py check --scope foundation`: PASSED (i18n parity, Ruff lint, Next.js production build)
- `python scripts/tasks.py check --scope core`: PASSED (13/13 tests passing)

## Exact Command to Resume Tomorrow
```bash
python scripts/tasks.py status
# Then continue with Phase P03.1:
# "P03.1: Create source registry from blueprint, official host allowlist, feed metadata and actual check results"
```
