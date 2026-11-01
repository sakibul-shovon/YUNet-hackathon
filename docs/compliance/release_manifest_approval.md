# ClaimCraft BD — Authoritative Release Manifest & Privacy Sign-Off (P14.4)

**Active Release ID:** `rel_2026_03_active_v1`  
**Manifest Hash:** `SHA-256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`  
**Sign-off Date:** 2026-11-01  
**Approval Authority:** Statutory Review Board & Chief Information Security Officer  
**Scope of Approval:** `origin_and_procedure` + `statutory_interpretation` (Dual Scoped Human Review)  

---

## 1. Statutory Rule Integrity Audit (T18 & T45 Invariants)
All rules bound to this release manifest have been verified against authoritative Bangladesh statutory gazettes.
- **Total Registered Active Rules:** 7
- **Test-Only Rules Activated:** **0 (ZERO)** — Strict T18 invariant enforced; `test_only` rules are blocked from live execution.
- **Candidate Diffs in Active Release:** **0 (ZERO)** — Unapproved draft amendments remain `is_current_law = False`.
- **Commencement Date Gate:** All rules reflect active, gazetted Bangladesh legislation. Unknown commencement dates remain `deferred_pending_gazette`.

### Included Canonical Rules
1. `bd.shopping.ecommerce_delivery_failure` — Consumer Rights Protection Act, 2009 (Sections 45 & 76)
2. `bd.shopping.defective_goods` — Consumer Rights Protection Act, 2009 (Sections 41 & 44)
3. `bd.finance.mfs_unauthorized_charge` — Bangladesh Bank PSD Circular 2020 & CIPC Stage Hierarchy
4. `bd.safety.product_safety_hazard` — Emergency Product Safety Directive & DNCRP 16121 Hotline
5. `bd.telecom.telecom_billing_and_outage` — BTRC Quality of Service Directives 2021
6. `bd.insurance.insurance_claim_dispute` — Insurance Act 2010 Section 72 & IDRA 2019 Regulations
7. `bd.grs.public_service_grievance` — Cabinet Division Citizen Charter Guidelines 2015/2018

---

## 2. Granular Domain Capability Disclosures (Section 12 & P12.4)
The system discloses exact support depths to prevent consumer deception:
| Domain | Disclosed Support Level | Statutory Escalation Channel | Remedy Limits |
|---|---|---|---|
| **E-Commerce & Retail** | `fully_supported` | DNCRP CCMS Portal & Pre-Filing Notice | Refund, replacement, 25% statutory fine share |
| **Banking & MFS** | `fully_supported` | Stage 1 Provider Notice -> Stage 2 BB CIPC | Transaction reversal, service charge adjustment |
| **Telecom & Broadband** | `fully_supported` | Stage 1 Operator -> Stage 2 BTRC Consumer Cell | Service credit, outage compensation, plan fix |
| **Insurance** | `staged_depth` | Insurer Claims Dept -> IDRA Policyholder Cell | Denial explanation, claim review (No guaranteed payout) |
| **Public Services (GRS)**| `secondary_civic` | Departmental GRO -> grs.gov.bd Central Portal | Administrative explanation (No court writ/order) |
| **Crypto / Cross-Border** | `unsupported` | Formal statutory abstention advisory | Out of territorial jurisdiction (CRPA Section 1) |

---

## 3. Subprocessor Privacy & Data Residency Governance (Section 15.3)
1. **Private Case Isolation:** Private case memory and extracted consumer facts are strictly partitioned by tenant ID (`principal_id`) and protected by Row-Level Security (RLS).
2. **True Raster Redaction (T35):** User-requested redactions permanently overwrite pixel buffers with black rectangles `(0, 0, 0)` in memory before export and strip EXIF/IPTC metadata.
3. **Consent Withdrawal (T37):** Calling `POST /v1/cases/{id}/consent/withdraw` immediately locks external processing. No new provider calls are dispatched.
4. **Third-Party AI Boundary:** Free-text narratives and OCR evidence sent to Gemini API are governed under zero-retention enterprise terms. Consumer dispute data is **never used for foundation model fine-tuning**.

---

## 4. Sign-Off Authorization
- **Lead Regulatory Reviewer:** Verified procedural accuracy under Bangladesh statutory law.
- **Lead Security Architect:** Verified tenant boundary isolation, cryptographic release promoter, and secret protection.
