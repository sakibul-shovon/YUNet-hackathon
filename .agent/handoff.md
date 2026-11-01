# ClaimCraft BD — Agent Handoff

## Execution Status
- **Completed Phases:**
  - **P00 (Foundation & Compatibility):** 100% COMPLETE & VERIFIED (`9701af14cd10c25e4b6f0b0d0c6a8924da73ff82`)
  - **P01 (Design System & Connected Shell):** 100% COMPLETE & VERIFIED (`5472bb63612157ded81cca5e3fef9763e4ec0f27`)
  - **P02 (Identity, Ownership, Persistence & Secure Sessions):** 100% COMPLETE & VERIFIED (`e64b0f77ea6bb9d5c316496ec8c79c3143ad45d2`)
  - **P03 (Governed Initial Sources & Deterministic Policy Skeleton):** 100% COMPLETE & VERIFIED (`f0e857c6cd946be984cfd2f8f3e79673db4a6e87`)
  - **P04 (First Text-to-Action Vertical Slice):** 100% COMPLETE & VERIFIED (`de01a45460639bda1bb6dfe2e1769826c31f8375`)
  - **P05 (Secure Evidence Vault & Provenance Graph):** 100% COMPLETE & VERIFIED (`f2b371aa607d1f1fd3261cecb754c0e783fe3600`)
  - **P06 (Multimodal Case Compiler):** 100% COMPLETE & VERIFIED (`3014eff5edc0b7248e3a960f611d9c061b99f382`)
  - **P07 (Genuine Hybrid Retrieval & Exact Citations):** 100% COMPLETE & VERIFIED (`1129970e554268f7fe2ffe8575009fa6450b1a5b`)
  - **P08 (Complete Proof-to-Path and Multi-Issue Reasoning):** 100% COMPLETE & VERIFIED (`5779d8e7dc492bd7c13041eea11bed3b40f5c8dd`)
  - **P09 (Action Studio, Filing Companion and Export):** 100% COMPLETE & VERIFIED
- **Active Phase:** P10 (Living Case, follow-up and decision changes)
- **Active Task:** P10.1 (User-reported response/submission/outcome update UI and private references)
- **Last Completed Task:** P09.7 (Implement official complaint destination cards, direct public references and link-health fallback)
- **Required Tasks Progress:** 58 / 86 (67.4% complete, 0 blocked)
- **Phase Delivery History:**
  - P00 SHA: `9701af14cd10c25e4b6f0b0d0c6a8924da73ff82` (Verified on `origin/main`)
  - P01 SHA: `5472bb63612157ded81cca5e3fef9763e4ec0f27` (Verified on `origin/main`)
  - P02 SHA: `e64b0f77ea6bb9d5c316496ec8c79c3143ad45d2` (Verified on `origin/main`)
  - P03 SHA: `f0e857c6cd946be984cfd2f8f3e79673db4a6e87` (Verified on `origin/main`)
  - P04 SHA: `de01a45460639bda1bb6dfe2e1769826c31f8375` (Verified on `origin/main`)
  - P05 SHA: `f2b371aa607d1f1fd3261cecb754c0e783fe3600` (Verified on `origin/main`)
  - P06 SHA: `3014eff5edc0b7248e3a960f611d9c061b99f382` (Verified on `origin/main`)
  - P07 SHA: `1129970e554268f7fe2ffe8575009fa6450b1a5b` (Verified on `origin/main`)
  - P08 SHA: `5779d8e7dc492bd7c13041eea11bed3b40f5c8dd` (Verified on `origin/main`)
  - P09 SHA: *(Pending commit & push)*

## What Works
- **Phase P09 (Action Studio, Filing Companion and Export):**
  - **P09.1 Action DAG & One Primary Next Action UI:**
    - `services/backend/app/actions/action_dag.py`: Action DAG service enforcing dependency resolution, mandatory Stage 1 provider grievance before Central Bank escalation (T20), and non-forced optional seller messages for DNCRP CCMS complaints.
    - Status transitions: `ready`, `blocked`, `optional`, `completed`.
  - **P09.2 Editable Document AST & Sentence Verification (T26, T29):**
    - `services/backend/app/actions/document_ast.py`: Generates structured document AST with sentence-level source provenance.
    - Statement types: `reviewed_fact` (verified evidence), `user_allegation` (unverified claim), `statutory_basis` (legal citations).
    - T29 Invariant: Material edits by consumer via `/v1/cases/{case_id}/documents/edit` are classified as `user_allegation` and clear verified provenance links.
    - T26 Invariant: Document lifecycle strictly remains `unsubmitted_draft`; `is_filed` and `is_sent` remain False.
  - **P09.3 Versioned Portal Field Maps & Stale-Map Fallback (T33):**
    - `services/backend/app/actions/portal_field_maps.py`: Versioned field maps for DNCRP CCMS (`dncrp_ccms`) and Bangladesh Bank CIPC (`bb_cipc`).
    - BDT currency transformations, evidence notes, and stale-map fallback.
    - T33 Invariant: Zero credentials, passwords, or CAPTCHA automation requested or exposed.
  - **P09.4 Multi-Format Document Export & Downloads (T27, T34):**
    - `services/backend/app/actions/export_service.py`: Generates Markdown and HTML exports with cryptographic SHA-256 provenance hash.
    - Prominent unsubmitted draft disclaimer in English and Bangla.
    - T27 Invariant: Export or download never marks `lifecycle_status` as `filed`.
  - **P09.5 Attachment Privacy Review & True Raster Redaction (T35):**
    - `POST /v1/cases/{case_id}/evidence/{evidence_id}/redact`: Permanently draws solid black opaque boxes directly over image pixel buffers and strips all EXIF metadata.
    - Irreversible pixel destruction verified by buffer analysis.
  - **P09.6 Full Prepare/Export to Official Portal Journey (T27, T33):**
    - Consumer can review facts, edit draft, copy per-field values, export document, and access official government portals with clear unsubmitted boundaries.
  - **P09.7 Official Complaint Destination Cards & Link Health (T54):**
    - `services/backend/app/actions/destinations.py`: Verified registry of official dispute destinations (`dncrp_ccms_portal`, `bb_cipc_portal`, `dncrp_hotline_16121`).
    - Link health monitoring (`healthy` vs `linked_unconfirmed`) with verified email and phone fallback routes.
  - **Action Studio Web UI:**
    - `apps/web/src/components/actions/ActionStudioClient.tsx`: Interactive multi-tab studio integrated directly into `/[locale]/cases/[id]/actions`.
    - Bilingual parity across 187 keys with 100% English and Bangla parity.

## Test Evidence
- `python scripts/tasks.py check --scope foundation`: PASSED (1:1 i18n parity verified across 187 message keys, Ruff lint clean, Next.js build clean across 23 routes).
- `python scripts/tasks.py check --scope core`: PASSED (106/106 pytest tests passing across actions, integration, multimodal, policy, retrieval, security, and unit suites).
- `python scripts/tasks.py contracts`: PASSED (OpenAPI schema & TypeScript contracts updated and verified).

## Next Action
- Stage Phase P09 deliverables, commit (`feat(P09): complete action studio, editable document AST, filing companion, multi-format export, and destination cards`), push to GitHub `origin main`, verify remote commit receipt, and immediately proceed with Phase P10 (Living Case, follow-up and decision changes).
