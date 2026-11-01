# ClaimCraft BD — Human Procedure-Review Packet

> **Notice:** In compliance with ClaimCraft BD core architectural principles (Section 12.5 & Section 17 P03.5), all automated rule candidates and statutory citations must undergo formal human procedural review by designated legal reviewers before active promotion into a production knowledge release. **No statutory rule is ever auto-promoted without explicit reviewer approval.**

---

## 1. Candidate Sources for Procedural Review

| Source ID | Act / Instrument Title | Official Issuer | Official URL | Document Type | Procedural Scope |
|---|---|---|---|---|---|
| `bd_crpa_2009` | Consumer Rights Protection Act, 2009 (Act No. 26 of 2009) | Legislative and Parliamentary Affairs Division | http://bdlaws.minlaw.gov.bd/act-1014.html | Statute | Reviewed Statutory Guidance |
| `dncrp_ccms_portal` | DNCRP Consumer Complaint Management System (CCMS) | Directorate of National Consumer Rights Protection | https://ccms.dncrp.com/ | Portal Map | Procedure Guidance |
| `bb_cipc_procedure` | BB Customer Interests Protection Centre Procedure | Financial Integrity & Customer Services Dept, BB | https://bb.org.bd/en/index.php/services/cipc_procedure | Procedure Guide | Procedure Guidance |
| `bb_mfs_regulations_2022` | Bangladesh Bank MFS Regulations, 2022 | Payment Systems Department, Bangladesh Bank | https://bb.org.bd/en/index.php/about/financialsystem/mfs | Circular | Procedure Guidance |
| `dncrp_hotline_16121` | National Consumer Rights Dedicated Hotline 16121 | Directorate of National Consumer Rights Protection | http://dncrp.portal.gov.bd/ | Emergency Contact | Emergency Procedure Guidance |

---

## 2. Starter Rule Bundles in Draft Status

The starter rules are stored in strict typed YAML AST format within `knowledge/packs/bd/`:

### 2.1 Shopping: E-Commerce Delivery Failure (`bd.shopping.ecommerce_delivery_failure`)
- **Status:** `draft` (Pending human approval)
- **Dependencies:** `bd_crpa_2009` (Section 45), `dncrp_ccms_portal`
- **Core Condition:**
  ```yaml
  all:
    - eq: { fact: purchase_channel, value: ecommerce }
    - eq: { fact: goods_delivered, value: false }
    - eq: { fact: promised_delivery_date_passed, value: true }
  ```
- **Exclusions:**
  - `refund_already_issued == true`
  - `order_cancelled_by_buyer_before_dispatch == true`
- **Actions:** `prepare_merchant_notice`, `prepare_dncrp_complaint`

### 2.2 Shopping: Defective / Non-Conforming Goods (`bd.shopping.defective_goods`)
- **Status:** `draft` (Pending human approval)
- **Dependencies:** `bd_crpa_2009` (Section 41, 44), `dncrp_ccms_portal`
- **Core Condition:**
  ```yaml
  all:
    - eq: { fact: goods_received_defective, value: true }
    - eq: { fact: seller_notified_within_warranty, value: true }
  ```
- **Exclusions:**
  - `user_inflicted_damage == true`
- **Actions:** `prepare_merchant_replacement_request`, `prepare_dncrp_complaint`

### 2.3 Finance: MFS Unauthorized Transaction (`bd.finance.mfs_unauthorized_charge`)
- **Status:** `draft` (Pending human approval)
- **Dependencies:** `bb_cipc_procedure`, `bb_mfs_regulations_2022`
- **Core Condition:**
  ```yaml
  all:
    - eq: { fact: payment_instrument_kind, value: mfs_wallet }
    - eq: { fact: transaction_unauthorized, value: true }
    - eq: { fact: provider_ticket_filed, value: true }
  ```
- **Exclusions:**
  - `otp_pin_voluntarily_shared_to_fraudster == true`
- **Actions:** `prepare_provider_formal_letter`, `prepare_bb_cipc_escalation`

### 2.4 Safety: Hazardous Consumer Product (`bd.safety.hazardous_product`)
- **Status:** `draft` (Pending human approval)
- **Dependencies:** `bd_crpa_2009` (Section 41), `dncrp_hotline_16121`
- **Core Condition:**
  ```yaml
  all:
    - eq: { fact: product_presents_immediate_hazard, value: true }
  ```
- **Actions:** `call_dncrp_hotline_16121`, `preserve_hazardous_sample`

---

## 3. Human Reviewer Verification Checklist

Before promoting candidate rules to an active knowledge release, the assigned reviewer must verify:
- [ ] Statutory text authenticity: Section citations match the exact gazette or Ministry of Law publication.
- [ ] Limitation periods: Strict 30-day CRPA 2009 limitation period is enforced where applicable.
- [ ] Kleene 3-valued logic integrity: Missing facts must evaluate strictly to `UNKNOWN`, never defaulting to `FALSE`.
- [ ] No fake verified flags: Sources must reflect verified upstream hashes, not prose assertions.
- [ ] Separation of powers: Consumer guidance never promises penalties, rewards, or specific judicial rulings.

---

## 4. Promotion Authorization Protocol

1. **Step 1 (Reviewer Role):** Submit formal review via `POST /v1/admin/source-versions/{id}/review` with reviewer identity and scope.
2. **Step 2 (Publisher Role):** Construct candidate manifest via `POST /v1/admin/releases/build`. Ensure `test_only` rules are absent.
3. **Step 3 (Publisher Role):** Promote active release pointer atomically via `POST /v1/admin/releases/{id}/promote`.
