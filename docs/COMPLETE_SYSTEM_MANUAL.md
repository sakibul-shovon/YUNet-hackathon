# ClaimCraft BD — Complete Engineering & Architecture Manual

## Table of Contents
1. [Architecture Overview & System Principles](#1-architecture-overview--system-principles)
2. [Data Plane & Multi-Tenant Isolation](#2-data-plane--multi-tenant-isolation)
3. [Multimodal Evidence Extraction & Ingestion Pipeline](#3-multimodal-evidence-extraction--ingestion-pipeline)
4. [Deterministic 3-Valued Kleene Policy AST Engine](#4-deterministic-3-valued-kleene-policy-ast-engine)
5. [Active-Learning Next-Best Question (NBQ) Heuristics](#5-active-learning-next-best-question-nbq-heuristics)
6. [Action Studio & Statutory Document Synthesis](#6-action-studio--statutory-document-synthesis)
7. [Merchant Scam Radar & Intelligence Architecture](#7-merchant-scam-radar--intelligence-architecture)
8. [Super Admin Command Center & Operations](#8-super-admin-command-center--operations)
9. [API Interface Reference & BFF Proxy Patterns](#9-api-interface-reference--bff-proxy-patterns)
10. [Automated Verification & Operational Playbooks](#10-automated-verification--operational-playbooks)

---

## 1. Architecture Overview & System Principles

ClaimCraft BD is designed as a hybrid deterministic-agentic copilot for consumer dispute resolution in Bangladesh. 

### Core Architectural Principles
- **No Hallucinated Legal Remedies:** Under no circumstances does an unconstrained LLM output statutory citations or declare case admissibility. Legal eligibility is decided strictly by a deterministic Abstract Syntax Tree (AST) evaluator implementing Kleene 3-valued propositional logic.
- **Strict Grounding:** Every name, transaction ID, money amount, and timeline referenced in generated legal documents must originate from either verified physical evidence (OCR receipts) or user-stated admissions.
- **Tenant Isolation:** Cases and evidence are strictly partitioned by cryptographic principal IDs. Foreign case queries return non-enumerating HTTP 404 responses.
- **Bilingual First-Class Citizen:** Both English and Bengali (বাংলা) are first-class languages across all UI surfaces, error responses, legal notifications, and question prompts.

---

## 2. Data Plane & Multi-Tenant Isolation

### Principal & Session Model
The identity system supports three tiers of authenticated principals:
1. **Anonymous Guest Principals:** Instantiated automatically upon landing on the application. A cryptographically random `principal_id` and short-lived JWT are provisioned along with an `HttpOnly` secure cookie.
2. **Permanent Registered Users:** Full accounts with email, hashed passwords (using PBKDF2 with SHA-256 and unique salt), and multi-role assignments (`consumer`, `reviewer`, `publisher`, `admin`).
3. **Judge Demo Sessions:** One-click pre-seeded evaluation principals with pre-loaded realistic scenarios.

```
+------------------------------------------------------------------------+
|                               PRINCIPAL                                |
|  - id: UUID (Primary Key)                                              |
|  - kind: anonymous | permanent                                         |
|  - locale: bn-BD | en-BD                                               |
+------------------------------------------------------------------------+
                               |
                               | 1:N
                               v
+------------------------------------------------------------------------+
|                                 CASE                                   |
|  - id: UUID (Primary Key)                                              |
|  - principal_id: UUID (Foreign Key -> Principal)                       |
|  - display_reference: CC-YYYY-XXXX                                     |
|  - lifecycle_status: draft | intake | active | resolved | escalated     |
|  - incident_date: Date                                                 |
|  - category: e_commerce | mfs | electronics | retail | services        |
+------------------------------------------------------------------------+
```

### Authorization Invariant
Any database query for case facts, evidence blobs, action drafts, or procedural assessments filters strictly on `Case.principal_id == current_principal.id`, except for global synthetic test fixtures mapped to `DEMO_FIXTURE_IDS` which allow shared read-only evaluation.

---

## 3. Multimodal Evidence Extraction & Ingestion Pipeline

### Audio Voice Intake
1. **Capture:** Browser Web Audio API captures audio input (WAV/WebM) at 16kHz mono.
2. **Transcription:** Dispatched to Google Speech-to-Text / Gemini Multimodal API with language hints for colloquial Bangla and code-switched Banglish.
3. **Entity Extraction:** Narrative transcript is processed to extract candidate facts:
   - Incident dates and purchase timelines.
   - Merchant names, Facebook page handles, contact numbers.
   - Monetary figures paid, payment channel (bKash, Nagad, Cash-on-Delivery).
   - Defect taxonomy (non-delivery, wrong item, counterfeit, adulterated, refused warranty).

### Vision & Document OCR
1. **Document Vault:** Securely stores uploaded image blobs (PNG, JPEG, PDF) with SHA-256 content addressing.
2. **Visual Parsing:** Gemini Vision extracts invoice headers, line items, VAT registration / BIN numbers, courier tracking numbers, and transaction IDs.
3. **Bi-Directional Reconciliation:**
   - Compares user-stated transaction amounts with extracted receipt numbers.
   - When conflicting numbers appear, the system creates a low-confidence fact entry and queues a Next-Best Question (NBQ) to prompt the consumer for explicit clarification.

---

## 4. Deterministic 3-Valued Kleene Policy AST Engine

Legal statutes cannot be evaluated using traditional binary Boolean logic (`TRUE` / `FALSE`) when material facts are unknown or pending evidence. ClaimCraft BD models statutory rules using **Strong Kleene 3-Valued Logic** ($K_3$), where truth values are $\mathcal{T} = \{\text{TRUE}, \text{FALSE}, \text{UNKNOWN}\}$.

### Truth Tables

#### Conjunction ($\land$)
| $\land$ | TRUE | UNKNOWN | FALSE |
|---|---|---|---|
| **TRUE** | TRUE | UNKNOWN | FALSE |
| **UNKNOWN** | UNKNOWN | UNKNOWN | FALSE |
| **FALSE** | FALSE | FALSE | FALSE |

#### Disjunction ($\lor$)
| $\lor$ | TRUE | UNKNOWN | FALSE |
|---|---|---|---|
| **TRUE** | TRUE | TRUE | TRUE |
| **UNKNOWN** | TRUE | UNKNOWN | UNKNOWN |
| **FALSE** | TRUE | UNKNOWN | FALSE |

### Statutory Rules Implemented in Policy Engine

| Rule ID | Statutory Reference | Title | Core Conditions |
|---|---|---|---|
| `DNCRP_SEC_45_NON_DELIVERY` | CRPA 2009 Sec 45 | Failure to Deliver Promised Goods | `payment_made == TRUE` $\land$ `goods_delivered == FALSE` $\land$ `promised_deadline_elapsed == TRUE` $\land$ `within_30_days == TRUE` |
| `DNCRP_SEC_51_COUNTERFEIT` | CRPA 2009 Sec 51 | Deceptive Representation & Fake Goods | `counterfeit_detected == TRUE` $\land$ `original_promised == TRUE` $\land$ `within_30_days == TRUE` |
| `DNCRP_SEC_52_ADULTERATED` | CRPA 2009 Sec 52 | Adulterated / Hazardous Food & Goods | `adulteration_evidence == TRUE` $\land$ `health_risk_present == TRUE` |
| `DNCRP_SEC_53_SERVICE_DEFECT` | CRPA 2009 Sec 53 | Defective Service / Negligence | `service_agreement_exists == TRUE` $\land$ `gross_deficiency == TRUE` |
| `DIGITAL_COMMERCE_2021_REFUND` | E-Commerce Guideline 2021 Sec 4 | 72-Hour Mandatory Refund | `order_cancelled == TRUE` $\land$ `advance_payment_held == TRUE` $\land$ `refund_period_exceeded == TRUE` |
| `PENAL_CODE_420_FRAUD` | Penal Code 1860 Sec 420 | Fraudulent Cheating & Deception | `seller_unreachable == TRUE` $\land$ `dishonest_inducement == TRUE` $\land$ `no_business_license == TRUE` |

---

## 5. Active-Learning Next-Best Question (NBQ) Heuristics

When policy evaluation yields `UNKNOWN` for one or more high-priority statutory paths, the NBQ engine calculates the optimal question to present next.

### Mathematical Formulation
For each missing fact $f \in \mathcal{F}_{\text{unknown}}$, its priority score $\mathcal{S}(f)$ is computed as:

$$\mathcal{S}(f) = w_{\text{statutory}} \cdot \mathcal{C}(f) + w_{\text{limitation}} \cdot \mathcal{L}(f) + w_{\text{impact}} \cdot \mathcal{I}(f)$$

Where:
- $\mathcal{C}(f)$ is the number of currently blocked statutory routes that depend directly on $f$.
- $\mathcal{L}(f)$ is the proximity weight to the 30-day statutory limitation deadline (higher weight as days remaining decrease).
- $\mathcal{I}(f)$ is the information gain across the policy decision forest.

Consumers can either answer directly (with inline validation) or skip the question without breaking the evaluation pipeline.

---

## 6. Action Studio & Statutory Document Synthesis

Once a route evaluates to `supported`, ClaimCraft BD unlocks corresponding procedural actions in the **Action Studio**:

### 1. 72-Hour Pre-Action Demand Notice
- Formatted as a formal legal notice addressed directly to the merchant management.
- Cites specific sections of the Consumer Rights Protection Act 2009 and warns of formal DNCRP complaint filing if the dispute is not cured within 72 hours.
- Exportable via:
  - **WhatsApp Direct Message** (URI encoded with Markdown bold formatting).
  - **Email Template** (Pre-filled Subject and Body).
  - **Printable / Copyable Plaintext Notice**.

### 2. Official DNCRP Schedule-1 Statutory Petition
- Formatted in accordance with Form 1 of the Consumer Rights Protection Rules.
- Itemized sections:
  1. Complainant Identification & National ID / Contact Details.
  2. Opposite Party (Respondent / Merchant) Information.
  3. Chronological Statement of Incident Facts.
  4. Material Evidence Annexures List (Invoices, MFS TrxIDs, Courier Delivery Slips).
  5. Statutory Violations Charged (e.g. Sections 45, 51).
  6. Requested Prayers & Reliefs:
     - 100% Monetary Refund of Disputed Amount.
     - Compensation for Physical/Mental Harassment.
     - Section 76(4) entitlement to 25% of any administrative fine levied.

---

## 7. Merchant Scam Radar & Intelligence Architecture

The **Merchant Risk Radar** runs background risk assessment pipelines against verified dispute history:
- **Heuristic Metrics:**
  - Ratio of Non-Delivery disputes to total reported orders.
  - Disconnected contact numbers and fake BIN registrations.
  - Social media sentiment reports and scam community grievances.
- **Risk Classification:**
  - `0 - 25%`: Verified / Safe Merchant.
  - `26 - 60%`: Medium Risk / Operational Delays.
  - `61 - 85%`: High Risk / Frequent Delivery Failures.
  - `86 - 100%`: Blacklisted / Confirmed Fraud Syndicate.

The Radar search interface provides instant debounced querying against real database merchant records without relying on static mock objects.

---

## 8. Super Admin Command Center & Operations

Accessible at `/en/admin`, the Super Admin portal provides comprehensive management tools:
- **Executive Metrics:** Real-time dispute volume, statutory route distributions, and resolution ratios.
- **Administrative Dispute Override:** Ability to transition disputes into `active`, `resolved`, `escalated`, or `fraudulent` states with required written justifications and immutable SHA-256 audit logging.
- **Statutory Candidate Watcher:** Workflow for legal council to review incoming statutory amendments, gazettes, or regulatory guidelines before publishing them to the policy AST ruleset.
- **Merchant Blacklist Controls:** Direct administrative toggle of merchant risk percentages, verification badges, and public scam warnings.
- **Public Alert Broadcaster:** Ability to publish platform-wide emergency warning banners regarding fraudulent e-commerce entities.

---

## 9. API Interface Reference & BFF Proxy Patterns

All API requests pass through the Next.js BFF proxy `/api/v1/[...path]` which manages session propagation, CORS headers, and correlation tracking.

### Core Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/guest` | Initializes or resumes an anonymous guest principal session. |
| `POST` | `/api/v1/auth/login` | Authenticates permanent or administrative users. |
| `GET` | `/api/v1/cases` | Lists cases belonging to the authenticated tenant. |
| `POST` | `/api/v1/cases` | Creates a new consumer dispute case. |
| `GET` | `/api/v1/cases/{id}` | Retrieves case details (with 404 tenant isolation). |
| `GET` | `/api/v1/cases/{id}/assessment` | Computes deterministic procedural assessment and condition trace. |
| `POST` | `/api/v1/cases/{id}/nbq/answer` | Submits answers to active-learning Next-Best Questions. |
| `POST` | `/api/v1/cases/{id}/actions/generate` | Synthesizes demand notice and DNCRP Schedule-1 petition. |
| `GET` | `/api/v1/merchants/intelligence` | Searches merchant database for risk profiles. |
| `GET` | `/api/v1/admin/stats` | Returns platform-wide operations metrics (Admin only). |

---

## 10. Automated Verification & Operational Playbooks

### Running Health Diagnostics
```bash
python scripts/tasks.py doctor
```
Verifies node versions, pnpm, uv, Python environment, and SQLite database connectivity.

### Running Test Verification Suites
```bash
# Foundation: Linters, Bilingual i18n parity, Next.js build
python scripts/tasks.py check --scope foundation

# Core: 134 automated unit and integration tests
python scripts/tasks.py check --scope core
```

### Knowledge Graph Maintenance
```bash
# Query knowledge graph (saves context tokens)
python scripts/tasks.py graphify query "How are consumer remedies calculated?"

# Rebuild graph after code modifications
python scripts/tasks.py graphify update
```
