# ClaimCraft BD — Agent Handoff

## Execution Status
- **Completed Phases:**
  - **P00 (Foundation & Compatibility):** 100% COMPLETE & VERIFIED (`9701af14cd10c25e4b6f0b0d0c6a8924da73ff82`)
  - **P01 (Design System & Connected Shell):** 100% COMPLETE & VERIFIED (`5472bb63612157ded81cca5e3fef9763e4ec0f27`)
  - **P02 (Identity, Ownership, Persistence & Secure Sessions):** 100% COMPLETE & VERIFIED (`93189a59d0284126d7216f3a76d5149d45ba47f9` / `e64b0f77ea6bb9d5c316496ec8c79c3143ad45d2`)
  - **P03 (Governed Initial Sources & Deterministic Policy Skeleton):** 100% COMPLETE & VERIFIED (`f0e857c6cd946be984cfd2f8f3e79673db4a6e87`)
  - **P04 (First Text-to-Action Vertical Slice):** 100% COMPLETE & VERIFIED (`de01a45460639bda1bb6dfe2e1769826c31f8375`)
  - **P05 (Secure Evidence Vault & Provenance Graph):** 100% COMPLETE & VERIFIED (`f2b371aa607d1f1fd3261cecb754c0e783fe3600`)
- **Active Phase:** P06 (Guided intake, multimodal timeline & voice note ingestion)
- **Active Task:** P06.1 (Browser recording, safe codec handling, consent and STT adapter)
- **Last Completed Task:** P05.6 (Evidence removal and cascading invalidation/deletion, orphan cleanup)
- **Required Tasks Progress:** 34 / 86 (39.5% complete, 0 blocked)
- **Phase Delivery History:**
  - P00 SHA: `9701af14cd10c25e4b6f0b0d0c6a8924da73ff82` (Verified on `origin/main`)
  - P01 SHA: `5472bb63612157ded81cca5e3fef9763e4ec0f27` (Verified on `origin/main`)
  - P02 SHA: `e64b0f77ea6bb9d5c316496ec8c79c3143ad45d2` (Verified on `origin/main`)
  - P03 SHA: `f0e857c6cd946be984cfd2f8f3e79673db4a6e87` (Verified on `origin/main`)
  - P04 SHA: `de01a45460639bda1bb6dfe2e1769826c31f8375` (Verified on `origin/main`)
  - P05 SHA: `f2b371aa607d1f1fd3261cecb754c0e783fe3600` (Verified on `origin/main`)

## What Works
- **Phase P05 (Secure Evidence Vault & Provenance Graph):**
  - **P05.1 Direct Upload Intent, Quotas, Storage & Verification Flow (T10, T11):** Alembic migration `0004_evidence_vault` creating `evidence_items` table with upgrade/downgrade round-trip verified. Pluggable `LocalStorageBackend` isolating quarantine from accepted storage with unpredictable paths and atomic writes. Magic bytes and file signature validator `mime_validation.py` rejecting spoofed extensions, executables (`MZ`/`ELF`), and script active content. Signed upload tokens (2-hour expiry), quota reservation (max 20 MB/item, max 100 MB aggregate/case, max 20 items/case), single-use enforcement, and token expiry sweeper.
  - **P05.2 Malware/Decoder Limits, Parser Probe & Honest Rejection UX (T12):** Deep parser probe in `app/evidence/parser_probe.py` rejecting pixel/decompression bombs (> 25 megapixels), PDF page bombs (> 50 pages), password-encrypted PDFs, and active script/macro actions (`/JavaScript`, `/JS`, `/Launch`). Scanner outage preserves `quarantined` status with `is_retryable=True` (never silently accepted or deleted). Rejection metadata and bilingual guidance rendered cleanly in `EvidenceItemRejectionBanner.tsx`.
  - **P05.3 Page-Aware Native Document Parser & Coordinate Normalization (T13, T14):** Document parsing engine `DocumentParser` using `pdfplumber` and `reportlab`. Strict unit coordinate normalization `[0.0, 1.0]` with clockwise rotation support (90°, 180°, 270°) and viewport resize invariance. Multicolumn layout detection and column-aware reading order sorting. Critical dispute token tagger for money amounts, dates, and order/trx IDs.
  - **P05.4 Evidence Viewer, Processing Stage, Span-to-Fact Links & Private Previews (T01, T15):** Owner-scoped private preview endpoint (`GET /v1/cases/{id}/evidence/{evidence_id}/preview`) with bounded read leases, strict cache exclusion headers (`Cache-Control: private, no-store, max-age=0, must-revalidate`, `Pragma: no-cache`, `X-Content-Type-Options: nosniff`), and foreign tenant 404 isolation (zero public object URLs). Span-to-fact link association endpoints (`POST/GET /v1/cases/{id}/evidence/{evidence_id}/spans`). Full interactive frontend `EvidenceVaultClient.tsx` in `apps/web/src/app/[locale]/cases/[id]/evidence/page.tsx`.
  - **P05.5 Deterministic Payment Conflict & Multi-Receipt Reconciliation (T21):** Endpoint `GET /v1/cases/{id}/evidence/reconciliation`. Invariant T21 strictly verified: narrated ৳5,500 vs ৳5,000 receipt prompts clarification, unlinked receipts available are not counted until linked, second linked ৳500 delivery receipt reconciles the total to ৳5,500, and duplicate receipts with identical content/hash do not double-count.
  - **P05.6 Cascading Removal, Invalidation & Revival Prevention (T36):** Cascading deletion endpoint `DELETE /v1/cases/{id}/evidence/{evidence_id}`. Deletes files from storage, unlinks spans, increments case `row_version` to invalidate stale assessments, records audit event in `case_events`, marks status `deleted`, and permanently prevents background revival or re-completion.

## Test Evidence
- `python scripts/tasks.py check --scope foundation`: PASSED (1:1 i18n parity across 162 keys, Ruff lint, Next.js production build of 23 pages)
- `python scripts/tasks.py check --scope core`: PASSED (59/59 pytest tests passing across integration, policy, security, and unit suites)
- `python scripts/tasks.py contracts`: PASSED (regenerated OpenAPI schema & TypeScript contracts)

## Next Action
- Stage Phase P05 files (excluding secrets/transients), commit (`feat(P05): complete secure evidence vault, parser probe, coordinate normalization, payment reconciliation, and cascading deletion`), push to `origin main`, verify remote commit SHA, and proceed to Phase P06 (Task P06.1).
