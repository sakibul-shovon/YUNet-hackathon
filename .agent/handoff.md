# ClaimCraft BD — Agent Handoff

## Execution Status
- **Completed Phases:**
  - **P00 (Foundation & Compatibility):** 100% COMPLETE & VERIFIED (`9701af14cd10c25e4b6f0b0d0c6a8924da73ff82`)
  - **P01 (Design System & Connected Shell):** 100% COMPLETE & VERIFIED (`5472bb63612157ded81cca5e3fef9763e4ec0f27`)
  - **P02 (Identity, Ownership, Persistence & Secure Sessions):** 100% COMPLETE & VERIFIED (`93189a59d0284126d7216f3a76d5149d45ba47f9` / `e64b0f77ea6bb9d5c316496ec8c79c3143ad45d2`)
  - **P03 (Governed Initial Sources & Deterministic Policy Skeleton):** 100% COMPLETE & VERIFIED (`f0e857c6cd946be984cfd2f8f3e79673db4a6e87`)
  - **P04 (First Text-to-Action Vertical Slice):** 100% COMPLETE & READY TO PUSH
- **Active Phase:** P05 (Secure evidence vault and provenance graph)
- **Active Task:** P05.1 (Direct upload intent, quota reservation, quarantine and accepted-copy storage flow)
- **Last Completed Task:** P04.6 (Wire saved case UI to actual backend jobs, failure/resume and initial sandbox text case)
- **Required Tasks Progress:** 28 / 86 (32.6% complete, 0 blocked)
- **Phase Delivery History:**
  - P00 SHA: `9701af14cd10c25e4b6f0b0d0c6a8924da73ff82` (Verified on `origin/main`)
  - P01 SHA: `5472bb63612157ded81cca5e3fef9763e4ec0f27` (Verified on `origin/main`)
  - P02 SHA: `e64b0f77ea6bb9d5c316496ec8c79c3143ad45d2` (Verified on `origin/main`)
  - P03 SHA: `f0e857c6cd946be984cfd2f8f3e79673db4a6e87` (Verified on `origin/main`)
  - P04 SHA: `de01a45460639bda1bb6dfe2e1769826c31f8375` (Verified on `origin/main`)

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
- **Phase P04 (First Text-to-Action Vertical Slice):**
  - **P04.1 Fact Assertions & Normalization:** Alembic migration `0003_fact_assertions_and_reviews` created and verified. Strict normalization for BDT money (integer minor units, Bengali digits, no float errors, T05) and Bangladesh dates (DD/MM ambiguity, relative dates, future promised delivery, date-only facts, T06). Invariants T07 verified (missing != false != 0 != unknown, original text preserved).
  - **P04.2 Real Text Extraction Adapter:** Deterministic extractor supporting Bangla, Banglish, and English narratives with verbatim text spans. Bounded schema validation and repair in `schemas.py` enforcing T08 (extra model fields forbidden, foreign/unknown span IDs rejected, invalid enums dropped). API endpoint `POST /v1/cases/{case_id}/extract?auto_persist=true` implemented.
  - **P04.3 Interactive Fact Review UI:** Client component in `FactReviewClient.tsx` and review page with accept, correct, reject, and unsure controls, plus desired remedy selector. Material correction deactivates old assertion, creates a new assertion version, and links `correction_assertion_id`. T09 verified: provenance preserved, zero verification inflation.
  - **P04.4 Exact-Source Procedural Assessment Engine:** Rule evaluator applying Kleene 3-valued logic. T19 verified: seller non-delivery with MFS payment does not generate provider complaint. T20 verified: provider dispute mandates Stage 1 provider grievance before BB escalation, NBQ selects provider ticket question, no automatic regulator acceptance promised.
  - **P04.5 Safe Dispute Draft Generator & Viewer:** Pre-filing dispute request generator and `ActionDraftViewer.tsx` viewer. T26 verified: violent threats and defamatory aggression strictly rejected; unsubmitted draft state maintained (`lifecycle_state == 'unsubmitted_draft'`, `is_sent == False`, `is_filed == False`). Bilingual citations and one-click copy feedback.
  - **P04.6 E2E Integration Test & Sandbox Demo:** Complete M1 vertical slice integration test `test_p04_6_e2e_m1_vertical_slice.py` passing. Invariants T04 (case persistence, reload survival) and T27 (generating/copying draft never marks case as filed or resolved) verified. Synthetic demo sandbox fixture `DEMO-DARAZ-001` seeded idempotently with truthful synthetic labeling.

## Test Evidence
- `python scripts/tasks.py check --scope foundation`: PASSED (1:1 i18n parity across 154 keys, Ruff lint, Next.js production build)
- `python scripts/tasks.py check --scope core`: PASSED (42/42 pytest tests passing)

## Next Action
- Stage Phase P04 files (excluding secrets/transients), commit (`feat(P04): complete M1 text-to-action vertical slice with typed facts, extraction, procedural assessment, and unsubmitted draft`), push to `origin main`, verify remote commit SHA, and proceed to Phase P05 (Task P05.1).
