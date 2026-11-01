# ClaimCraft BD — Agent Handoff

## Execution Status
- **Completed Phases:**
  - **P00 (Foundation & Compatibility):** 100% COMPLETE & VERIFIED (`9701af14cd10c25e4b6f0b0d0c6a8924da73ff82`)
  - **P01 (Design System & Connected Shell):** 100% COMPLETE & VERIFIED (`5472bb63612157ded81cca5e3fef9763e4ec0f27`)
  - **P02 (Identity, Ownership, Persistence & Secure Sessions):** 100% COMPLETE & VERIFIED (`93189a59d0284126d7216f3a76d5149d45ba47f9` / `e64b0f77ea6bb9d5c316496ec8c79c3143ad45d2`)
  - **P03 (Governed Initial Sources & Deterministic Policy Skeleton):** 100% COMPLETE & READY TO PUSH
- **Active Phase:** P04 (First text-to-action vertical slice)
- **Active Task:** P04.1 (Fact/assertion/review/issue/snapshot tables and typed normalization)
- **Last Completed Task:** P03.5 (Prepare shopping/finance/safety starter candidates, exact dependencies and source cards)
- **Required Tasks Progress:** 22 / 86 (25.6% complete, 0 blocked)
- **Phase Delivery History:**
  - P00 SHA: `9701af14cd10c25e4b6f0b0d0c6a8924da73ff82` (Verified on `origin/main`)
  - P01 SHA: `5472bb63612157ded81cca5e3fef9763e4ec0f27` (Verified on `origin/main`)
  - P02 SHA: `e64b0f77ea6bb9d5c316496ec8c79c3143ad45d2` (Verified on `origin/main`)
  - P03 SHA: Pending push

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
  - 11 core tables (`principals`, `web_sessions`, `actor_roles`, `cases`, `case_snapshots`, `issue_tracks`, `case_events`, `external_references`, `consents`, `deletion_requests`, `outbox`) created. Alembic migration `0001_initial` verified for both upgrade and downgrade round-trips. PostgreSQL RLS policies defined.
  - Opaque HttpOnly BFF cookie session management with SHA-256 token hashing, anonymous guest bootstrap (`/auth/guest`), short-lived HS256 access JWTs (15 min), CSRF protection, and mandatory `Cache-Control: private, no-store` response headers.
  - Case CRUD with optimistic locking (`row_version`), 409 conflict handling, account upgrade, and deletion immediate access revocation.
  - Tests T01, T02, T03, T04, P02.4, and P02.5 passing.
- **Phase P03 (Governed Initial Sources & Deterministic Policy Skeleton):**
  - **P03.1 Governed Source Registry & SSRF Prevention:** Host allowlist (`OFFICIAL_HOST_ALLOWLIST`) enforcing official government domains (`bdlaws.minlaw.gov.bd`, `dncrp.gov.bd`, `bb.org.bd`, etc.) and blocking private/link-local/cloud-metadata networks (SSRF prevention). Initial candidate registry with 7 sources (CRPA 2009, CCMS portal, DNCRP portal, BB CIPC procedure, BB MFS regulations 2022, BTRC complaint guidelines, DNCRP hotline 16121). All labeled observed/candidate with zero inherited fake "verified" flags.
  - **P03.2 Temporal Knowledge Schema & Migration:** Tables for `source_families`, `source_candidates`, `source_versions`, `source_provisions`, `source_approvals`, `knowledge_releases`, and `retrieval_chunks`. Alembic migration `0002_knowledge_sources_and_releases` verified. Immutable snapshot text/byte SHA-256 hash round-trip. Candidate sources excluded from approved search (Test T16 passing).
  - **P03.3 Typed Policy AST & Kleene 3-Valued Logic:** Typed Pydantic AST with operators (`AllNode`, `AnyNode`, `NotNode`, `EqNode`, `InNode`, `ExistsNode`, `DateCompareNode`, `MoneyCompareNode`, `SourceApprovedNode`, `ReviewAcceptedNode`). Three-valued evaluator enforces Kleene logic truth tables, missing facts strictly evaluate to `UNKNOWN` (never false/0), exclusion processing (TRUE -> `EXCLUDED`, UNKNOWN -> `NEEDS_FACTS`), and source-health caution overlays. Security injection keywords (`eval`, `exec`, `__import__`) and `test_only` rules rejected for live promotion (Tests T17 & T18 passing).
  - **P03.4 Admin Review Authorization & Release Manifest Builder:** Endpoints for reviewer review submission (`POST /v1/admin/source-versions/{id}/review`), publisher release build (`POST /v1/admin/releases/build`), atomic release promotion (`POST /v1/admin/releases/{id}/promote`), and release disabling. Role authorization strictly verified: consumer cannot review/approve (403), reviewer can inspect/review, publisher can build/promote, and `test_only` rules rejected with 422 (Test T44 passing).
  - **P03.5 Starter Candidates, Source Cards & Review Packet:** Starter rule bundles in YAML AST for shopping (`ecommerce_delivery_failure.yaml`, `defective_goods.yaml`), finance (`mfs_unauthorized_charge.yaml`), and safety (`product_safety_hazard.yaml`). Official source cards (`bd_crpa_2009.md`, `dncrp_ccms.md`, `bb_cipc.md`, `bb_mfs_2022.md`, `dncrp_hotline_16121.md`) and human procedure-review packet (`docs/knowledge/human_procedure_review_packet.md`) prepared. Unit tests pass (Test P03.5).

## Test Evidence
- `python scripts/tasks.py check --scope foundation`: PASSED (1:1 i18n parity across 154 keys, Ruff lint, Next.js production build)
- `python scripts/tasks.py check --scope core`: PASSED (27/27 pytest tests passing)

## Next Action
- Commit Phase P03, push to `origin main`, verify remote commit SHA, and proceed immediately to Phase P04 (Task P04.1).
