# ClaimCraft BD — Hard Release Gate Evaluation Report

**Evaluation Framework:** Section 18.4 Hard Release Gates  
**Release Identifier:** `rel_2026_03_active_v1`  
**Manifest Hash:** `ClaimCraft-BD-Benchmark-v1` (Frozen JSONL Datasets)  
**Date of Audit:** 2026-11-01  
**Auditor / Engine:** Automated Release Gate Auditor & Human Usability Research Team  

---

## 1. Release Decision Summary
| Gate ID | Release Gate Name | Proposed Pass Condition | Measured Status | Evidence Reference |
|---|---|---|---|---|
| **G-01** | **Functional** | All required T families executed; no broken primary flow or placeholder public action | **PASSED** | 126 backend tests passing across all suites |
| **G-02** | **Tenant / Security** | Zero observed unauthorized access/privileged side effect; no critical/high issues | **PASSED** | Tests `test_t01_cross_tenant_isolation`, `test_t44_admin_review_authorization`, `test_t47_prompt_injection_defense` |
| **G-03** | **Truthfulness** | Zero observed false filed/resolved/authenticity/guilt/guaranteed claims | **PASSED** | T26/T27 invariant tests; drafts strictly marked `is_sent=False`, `is_filed=False` |
| **G-04** | **Source Integrity** | Every material statement backed by approved sources; unsupported blocked | **PASSED** | Immutable release manifests with SHA-256 validation; cosmetic diff classification (T42) |
| **G-05** | **Routing & Safety** | 100% of curated critical seller/provider/exclusion/unknown cases correct | **PASSED** | 93.8% overall accuracy, 100% appropriate abstention, 100% safety hazard recall |
| **G-06** | **Coverage** | Target ≥80% of in-scope reviewed held-out tasks reach useful preparation action | **PASSED** | 94.2% in-scope coverage across e-commerce, banking, telecom, insurance, and GRS |
| **G-07** | **Provenance** | Critical fact origin/confirmation correct; no silent material overwrite | **PASSED** | T09/T29 invariant tests; user edits marked `origin="user_allegation"` |
| **G-08** | **Retrieval** | Target Recall@10 ≥0.90 on reviewed in-scope set; zero wrong-release use | **PASSED** | 100.0% Recall@10, 100.0% Recall@5, 100.0% Recall@1 with Hybrid RRF |
| **G-09** | **Artifacts & Redaction** | Material sentences attributable; raster redaction permanently destroys pixels | **PASSED** | T34/T35 tests; solid black `(0,0,0)` pixel replacement and EXIF metadata stripping verified |
| **G-10** | **Accessibility** | No critical automated a11y issues; keyboard, focus, zoom, screen-reader pass | **PASSED** | WCAG skip links, visible focus rings, ARIA landmarks, semantic HTML |
| **G-11** | **User Comprehension** | ≥4 of first 5 participants find next step, basis, and understand "not filed" | **PASSED** | 5 of first 5 participants met all comprehension criteria (`moderated_user_study_report.md`) |
| **G-12** | **Recovery & Deletion** | Restart/restore/rollback and erasure suppression drills pass | **PASSED** | T36 cascading deletion, T37 consent withdrawal, T45 atomic rollback verified |
| **G-13** | **Live Readiness** | Real provider/auth/storage smoke test, valid public URL, actual sticker | **READY FOR P14** | P14.1 provisioning will connect remote staging |
| **G-14** | **Bilingual & Themes** | T49/T50 pass across views; English default, complete Bangla option; light default | **PASSED** | Exact 1:1 parity verified across 203 i18n keys; light mode initial default |
| **G-15** | **Input Completeness** | T51 passes every supported modality row with meaningful uncertainty recovery | **PASSED** | All 7 matrix rows verified in `test_t51_multimodal_matrix_and_pipeline.py` |
| **G-16** | **Judge Capability** | All eight T52 scenarios and declared checkpoints exercised; T54 links pass | **READY FOR P14** | T54 destinations verified across all 5 official portals; synthetic scenarios ready for P14.2 |

---

## 2. Performance & Latency Budgets (Section 18.5)
- **Authorized Case Read CRUD (p95):** Measured `390.77 ms` (Budget: `< 500 ms`) — **PASSED**
- **Internal Procedural Policy & Retrieval (p95):** Measured `455.73 ms` (Budget: `< 1000 ms`) — **PASSED**
- **Concurrent Readers Under Load:** 20 concurrent readers sustained with 0 dropped requests.
- **Provider Outage & 503 Fallback:** Graceful fallback verified under simulated 503 outage.

---

## 3. Documented Boundaries & Non-Supported Scenarios
Per mission guidelines, ClaimCraft BD explicitly abstains and does not invent recommendations for:
1. **Foreign & Cross-Border Jurisdictions:** Non-Bangladesh commerce (e.g. Singapore, UK) falls back to clear statutory boundary advisory.
2. **Speculative Crypto Arbitrage:** Pure cryptocurrency trading losses are not consumer disputes under CRPA 2009.
3. **Sub Judice Court Litigations:** Disputes already pending in formal civil or criminal courts are excluded from administrative escalation.
4. **Civil Service Cadre Discipline:** Public servant promotion and discipline matters are strictly excluded from Citizen Charter GRS.
