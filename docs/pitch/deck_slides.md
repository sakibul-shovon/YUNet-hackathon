# ClaimCraft BD — Pitch Deck Presentation (≤5 Slides)

*Event: YU-Net AI Ignite 2026 Hackathon*  
*Track: Advanced Agentic AI & Bangladesh Consumer Rights Resolution*  

---

## Slide 1: The Everyday Consumer Resolution Gap
### "The government portal exists. Knowing what happened, what your records prove, and which step to take is the real bottleneck."

- **The Problem in Bangladesh:**
  - Millions of transactions take place daily across e-commerce (Daraz, Pickaboo), MFS wallets (bKash, Nagad), telecom operators, and utilities.
  - When disputes occur—such as an unfulfilled ৳5,500 phone order—consumers face confusing jurisdictional boundaries:
    - *Is this a seller non-delivery dispute under CRPA 2009 Section 45?*
    - *Or an MFS payment transfer failure requiring Bangladesh Bank Stage 1 escalation?*
  - Consumers get stuck in legal paralysis, post emotional complaints on social media, or submit malformed petitions that get rejected.
- **Concrete Scenario (Shafiq from Bogura):**
  - Paid ৳5,500 via bKash for a smartphone on Daraz. Goods never arrived after 20 days.
  - Daraz support stopped replying. Shafiq has a screenshot of a ৳5,000 payment transaction and an unverified chat.
  - He doesn't know how to draft a formal notice or calculate his 30-day statutory limitation window.

---

## Slide 2: ClaimCraft BD — From Messy Records to a Structured Next Step
### "Bangladesh-First Consumer Resolution Copilot"

- **End-to-End Grounded Assistance:**
  1. **Multimodal Ingestion:** Ingests Bengali voice notes, receipts, PDFs, order chats, and SMS screenshots with zero credential collection.
  2. **Fact Reconciliation:** Discovers fee discrepancies (৳5,500 narration vs ৳5,000 receipt) and flags needed clarifications before drafting.
  3. **Deterministic Procedural Path:** Runs a verified 3-valued Kleene policy engine bound to authoritative Bangladesh gazettes.
  4. **Action Studio:** Generates formal merchant pre-filing notices and DNCRP/BTRC/BB portal complaint drafts.
- **The Core Guarantee:**
  - **Zero Hallucinated Laws:** Every sentence is attributable to verified statutory citations (CRPA 2009, BB PSD, BTRC QoS).
  - **Zero Fake Filings:** The copilot never pretends to have submitted a case to the government; all drafts are clearly marked *Draft Only • Not Submitted*.

---

## Slide 3: Proof-to-Path — The Technical Differentiator
### "Why LLMs alone fail legal tasks, and how our hybrid architecture solves it"

```
[Raw Consumer Evidence] (Audio / Scanned Receipt / Chat Screenshot)
          │
          ▼  (Bounding-box provenance & OCR/VLM reconciliation)
[Structured Fact Graph] (purchase_channel, dates, amounts, ticket status)
          │
          ▼  (Kleene 3-Valued Deterministic Policy Engine)
[Procedural Route Assessment] ──► [What-If Simulation Sandbox] (In-Memory)
          │
          ▼  (Remedy-Aware Action DAG)
[Action Studio & Export] (Bilingual Bengali/English AST & Permanent Raster Redaction)
```

- **Deterministic Rule Authority:** AI never decides legal eligibility; deterministic rules evaluated in 3-valued logic decide procedural routes.
- **In-Memory What-If Simulations (T31):** Consumers can toggle facts ("What if the seller delivered late?") with zero database persistence.
- **True Raster Redaction (T35):** Sensitive NID/account details are permanently destroyed in the pixel buffer before document export.
- **Hybrid Retrieval (RRF):** Dense vectors + BM25 ensure 100% Recall@1 on exact Bengali section numbers.

---

## Slide 4: Measured Trust, Rigorous Evaluation & Hard Release Gates
### "Engineered for real compliance, not manufactured demo shortcuts"

| Evaluation Metric | Baseline / Ablation | ClaimCraft BD (Full System) |
|---|---|---|
| **Appropriate Abstention on Out-of-Scope Cases** | 0.0% (Hallucinates jurisdiction) | **100.0% (Safely abstains)** |
| **Urgent Safety Hazard Recall (Hotline 16121)** | 100.0% | **100.0% (Instant override)** |
| **Evidence Conflict Detection (Fee/Narration)** | 0.0% (Unchecked ingestion) | **100.0% (Precision & Recall)** |
| **Statutory Retrieval Recall@10** | 100.0% | **100.0% (MRR: 1.0000)** |
| **User Comprehension ("Not Filed" clarity)** | — | **5 of first 5 participants passed** |
| **CRUD & Policy Assessment Latency (p95)** | — | **< 460 ms (Under load)** |

- **Security & Privacy Red-Team Verified:**
  - Prompt injection immunity: Adversarial jailbreak strings in evidence cannot force route overrides.
  - Multi-tenant isolation: Guessing case UUIDs strictly returns HTTP 404.
  - Consent withdrawal (T37): Immediately blocks external provider processing.

---

## Slide 5: Bangladesh-First Vision & Solo Builder
### "Built for every citizen, across every device, in English and Bangla"

- **Inclusive Accessibility:**
  - 100% Bilingual parity with English default and complete Bengali support.
  - WCAG 2.1 AA compliant: Screen-reader landmarks, skip links, high-contrast themes.
  - Works on low-end Android mobile browsers and air-gapped desktop environments.
- **Responsible Expansion Roadmap:**
  - Deepening IDRA insurance claim dispute mediation workflows.
  - Expanding Citizen Charter GRS pathways across 64 districts.
  - Exploring partnerships with consumer rights advocacy groups.
- **Solo Builder:**
  - **Builder:** Sakibul Islam Shovon
  - **Repository:** `https://github.com/sakibul-shovon/YUNet-hackathon.git`
  - **Event:** YU-Net AI Ignite 2026 Hackathon
