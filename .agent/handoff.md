# ClaimCraft BD — Agent Handoff

## Execution Status
- **Completed Phases:**
  - **P00 (Foundation & Compatibility):** 100% COMPLETE & VERIFIED (`9701af14cd10c25e4b6f0b0d0c6a8924da73ff82`)
  - **P01 (Design System & Connected Shell):** 100% COMPLETE & VERIFIED (`5472bb63612157ded81cca5e3fef9763e4ec0f27`)
  - **P02 (Identity, Ownership, Persistence & Secure Sessions):** 100% COMPLETE & VERIFIED (`93189a59d0284126d7216f3a76d5149d45ba47f9` / `e64b0f77ea6bb9d5c316496ec8c79c3143ad45d2`)
  - **P03 (Governed Initial Sources & Deterministic Policy Skeleton):** 100% COMPLETE & VERIFIED (`f0e857c6cd946be984cfd2f8f3e79673db4a6e87`)
  - **P04 (First Text-to-Action Vertical Slice):** 100% COMPLETE & VERIFIED (`de01a45460639bda1bb6dfe2e1769826c31f8375`)
  - **P05 (Secure Evidence Vault & Provenance Graph):** 100% COMPLETE & VERIFIED (`f2b371aa607d1f1fd3261cecb754c0e783fe3600`)
  - **P06 (Multimodal Case Compiler):** 100% COMPLETE & VERIFIED (`3014eff5edc0b7248e3a960f611d9c061b99f382`)
  - **P07 (Genuine Hybrid Retrieval & Exact Citations):** 100% COMPLETE & VERIFIED
- **Active Phase:** P08 (Complete Proof-to-Path and multi-issue reasoning)
- **Active Task:** P08.1 (Complete shopping/finance/safety rule packs with explicit unknown/exclusion/date handling)
- **Last Completed Task:** P07.6 (Retrieval ablations and labeled query report; integrate full pipeline in workspace)
- **Required Tasks Progress:** 45 / 86 (52.3% complete, 0 blocked)
- **Phase Delivery History:**
  - P00 SHA: `9701af14cd10c25e4b6f0b0d0c6a8924da73ff82` (Verified on `origin/main`)
  - P01 SHA: `5472bb63612157ded81cca5e3fef9763e4ec0f27` (Verified on `origin/main`)
  - P02 SHA: `e64b0f77ea6bb9d5c316496ec8c79c3143ad45d2` (Verified on `origin/main`)
  - P03 SHA: `f0e857c6cd946be984cfd2f8f3e79673db4a6e87` (Verified on `origin/main`)
  - P04 SHA: `de01a45460639bda1bb6dfe2e1769826c31f8375` (Verified on `origin/main`)
  - P05 SHA: `f2b371aa607d1f1fd3261cecb754c0e783fe3600` (Verified on `origin/main`)
  - P06 SHA: `3014eff5edc0b7248e3a960f611d9c061b99f382` (Verified on `origin/main`)

## What Works
- **Phase P07 (Genuine Hybrid Retrieval & Exact Supported Citations):**
  - **P07.1 Hierarchical Provision Chunks & Exact-ID Round-Trip (T24):**
    - `services/backend/app/retrieval/provisions_data.py`: Canonical governed provisions for CRPA 2009 (Sections 41, 44, 45, 45(2), 60, 76) and Bangladesh Bank CIPC procedure (Stage 1 and 2).
    - `services/backend/app/retrieval/provision_service.py`: Exact section lookup supporting Bengali and Latin numerals and aliases (`ধারা ৪৫`, `sec:45`, `ধারা ৪৫(২)`, `sec:45(2)`, `ধারা ৬০`, `ধারা ৭৬`, `স্তর ১`, `স্তর ২`).
    - Long Bengali legal clauses preserve qualifications and exceptions verbatim ("তবে শর্ত থাকে যে, কোনো অনিবার্য কারণবশত বা যুক্তিসঙ্গত কারণে সরবরাহ সম্ভব না হইলে অনতিবিলম্বে ক্রেতাকে সমুদয় অর্থ ফেরত প্রদান করিতে হইবে।").
    - Invariant T24 strictly verified: non-existent sections (`sec:999`, `ধারা ৯৯৯`, `sec:100`) return `match_found=False` without hallucinating or inventing missing provisions.
  - **P07.2 Pinned E5 Embedding Adapter & Pre-Ranking Filtering (T25):**
    - `services/backend/app/retrieval/e5_adapter.py`: Pinned `intfloat/multilingual-e5-small` with 384 dimensions and strict `query: ` and `passage: ` prefix formatting.
    - Invariant T25: Allowed-ID masks and temporal validity intervals (`effective_from <= date_context < effective_to`) are applied **before** top-k cosine ranking, preventing obsolete or candidate provisions from crowding out applicable current law.
  - **P07.3 Bengali-Aware BM25s Tokenizer & Snapshot Persistence (T25):**
    - `services/backend/app/retrieval/bm25_adapter.py`: NFC normalization; tokenizes Unicode letters including Bengali combining marks (hasanta, vowel signs) without splitting; retains negation words (`না`, `নাই`, `নহে`, `নয়`, `not`, `no`); preserves compound section aliases (`45(2)`, `৪৫(২)`, `sec:45(2)`).
    - Safe from English stopword damage.
    - Deterministic snapshot save and reload verified with manifest SHA-256 hash.
  - **P07.4 Reciprocal Rank Fusion (RRF) & Deterministic Assembly (T25):**
    - `services/backend/app/retrieval/hybrid_retriever.py`: Fuses exact section match (rank 0 boost), dense cosine ranks, and BM25 lexical ranks using `RRF(d) = sum(1 / (60 + rank_i(d)))`. Deduplicated by unique citation handle.
  - **P07.5 Citation & Statement Validator (T28, T29) & Interactive Source Drawer:**
    - `services/backend/app/retrieval/citation_validator.py`: Strictly validates citation existence and temporal applicability; blocks output on non-existent (`CITATION_NON_EXISTENT`) or repealed (`CITATION_OUTDATED_OR_REPEALED`) provisions.
    - `apps/web/src/components/sources/StatutorySourceDrawer.tsx`: Interactive client component with section search, copy citation handle, qualification badges, and official gazette links embedded in `/[locale]/sources`.
  - **P07.6 Labeled Query Ablation Report & API Integration:**
    - `docs/benchmarks/retrieval_ablation_benchmark_report.md`: Documented 12-query benchmark verifying 100% exact recall, 0% hallucination on negative queries, and honest reporting of degraded mode when a channel is disabled.
    - Endpoints: `GET /v1/retrieval/provisions/lookup`, `GET /v1/retrieval/provisions/{citation_handle}`, `GET /v1/retrieval/sources/{source_id}/provisions`, `POST /v1/retrieval/search`, and `POST /v1/retrieval/citations/validate`.

## Test Evidence
- `python scripts/tasks.py check --scope foundation`: PASSED (1:1 i18n parity, Ruff lint clean, Next.js build clean across 23 static & dynamic routes).
- `python scripts/tasks.py check --scope core`: PASSED (88/88 pytest tests passing across integration, multimodal, policy, retrieval, security, and unit suites).
- `python scripts/tasks.py contracts`: PASSED (OpenAPI schema & TypeScript contracts updated and verified).

## Next Action
- Stage Phase P07 deliverables, commit (`feat(P07): complete genuine hybrid retrieval with E5 embeddings, Bengali BM25s tokenizer, RRF fusion, and citation validator`), push to GitHub `origin main`, verify remote commit receipt, and immediately begin Phase P08 (Task P08.1: Complete shopping/finance/safety rule packs with explicit unknown/exclusion/date handling).
