# EbarKi (এবার কি?) — Super Admin & Operations Portal Manual
## Architecture, API Specifications, RBAC Security & Operations Guide

---

## 1. Credentials & Quick Access

- **Web Portal Route:** `http://localhost:3000/en/admin` (or `/bn/admin`)
- **Default Master Admin Email:** `admin@claimcraft.bd`
- **Default Master Admin Password:** `Admin@ClaimCraft2026!`
- **Assigned RBAC Roles:** `['admin', 'reviewer', 'publisher', 'operator']`
- **1-Click Demo Sign-In:** The portal screen contains a **"⚡ 1-Click"** button that auto-populates credentials and authenticates into the administrative session.

---

## 2. Architecture & Role-Based Access Control (RBAC)

All endpoints and admin views are governed by the backend security model defined in `services/backend/app/core/security.py` and `app/identity/models.py`:

```
                       ┌─────────────────────────────────────────┐
                       │          ACTOR ROLE HIERARCHY           │
                       └─────────────────────────────────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
      ROLE: "consumer"              ROLE: "reviewer"             ROLE: "admin"
  • Isolated dispute memory    • Inspects candidate laws    • Full platform oversight
  • Upload personal evidence   • Side-by-side legal diff    • Dispute status overrides
  • 403 on /v1/admin/*         • Approves sections          • 1-Click user ban/unban
                               ROLE: "publisher"            • Blacklists merchants
                               • Builds KnowledgeRelease    • Broadcasts scam alerts
                               • Rollback target control    • Inspects audit logs
```

---

## 3. The 7 Administrative Modules

### Module 1: Executive Analytics & Live Overview (`GET /api/v1/admin/stats`)
- **Dispute Volume Metrics:** Total cases, active in-review, resolved, and dismissed.
- **Financial Claims:** Total disputed amount and recovered compensation in Bangladeshi Taka (৳ BDT).
- **Procedural Resolution Distribution:** Evaluated path share (DNCRP Directorate 58%, Bangladesh Bank CIPC 24%, Direct Negotiation 14%, Small Claims Court 4%).
- **Subsystem Health Engine:** Real-time ping statuses for API Gateway, Database AsyncSession, Multimodal OCR, Voice STT, and Active Statutory Release (`REL-2026-Q4-CRPA`).
- **Broadcast Platform Scam Alert (`POST /api/v1/admin/alerts`):** Ability to broadcast an urgent red/amber warning banner pinned across all consumer pages nationwide.

### Module 2: Legal Operations & Gazette Watchers (`GET /api/v1/admin/statutory/candidates`)
- **Section 22 Architectural Compliance:** Web scrapers from Bangladesh Gazette (BG Press) and Laws of Bangladesh ingest candidate laws into staging without altering active consumer guidance automatically.
- **Visual Section-Aware Legal Diff:** Compares baseline Act text against newly published amendments side-by-side with color-coded additions/deletions.
- **Approval & Rollback Controls:** 1-Click candidate approval, release promotion, and zero-downtime rollback target (`REL-2026-Q3-SAFE`).

### Module 3: Dispute Oversight & Master Registry (`GET /api/v1/admin/cases`, `POST /api/v1/admin/cases/{id}/override`)
- **Global Case Registry:** Filter and search across all disputes by merchant name, title, reference code, or lifecycle status.
- **Administrative Lifecycle Override:** Ability to transition a dispute to `active`, `resolved`, `escalated`, or `fraudulent` with a mandatory administrative justification note.
- **Audit Logging:** Every override automatically logs a `CaseEvent` and creates a cryptographic audit entry.

### Module 4: Merchant Scam Radar & Blacklist Control (`GET /api/v1/admin/merchants`, `POST /api/v1/admin/merchants/{slug}/override`)
- **Merchant Intelligence Registry:** Tracks major e-commerce and F-commerce platforms (Gadget Zone BD, Daraz Bangladesh, bKash Limited, etc.).
- **1-Click Blacklist & Verified Badge:** Instant toggles to mark predatory sellers as **BLACKLISTED** or award compliant platforms a **VERIFIED** badge.
- **Risk Percentage Slider:** Allows manual recalibration of a seller's risk score (e.g. 92% Scam Probability) with cited legal grounds (e.g., Section 45 Consumer Rights Protection Act 2009).

### Module 5: Community Grievance & Moderation (`GET /api/v1/admin/community/posts`, `POST /api/v1/admin/community/posts/{id}/moderate`)
- **Crowdsourced Post Moderation:** Review complaints submitted to the public feed along with "Me Too" counter counts and claim values.
- **Moderation Actions:**
  - **Pin to Top:** Prioritizes widespread scam advisories.
  - **Hide Spam:** Immediately removes defamatory, fraudulent, or abusive posts from public visibility.
  - **Dismiss Reports:** Clears false user reports.

### Module 6: User Directory & 1-Click Ban System (`GET /api/v1/admin/users`, `POST /api/v1/admin/users/{id}/toggle-ban`)
- **User Management:** Master list of permanent consumers and demo judges.
- **1-Click Account Ban:** Instantly blocks fraudulent actors from accessing the platform or posting disputes.
- **Role Elevation:** Promote users to `reviewer`, `publisher`, or `operator`.

### Module 7: Cryptographic Security Audit Trail (`GET /api/v1/admin/audit-logs`)
- **Immutable Provenance:** Chronological append-only stream recording every administrative action.
- **Traceability:** Logs UTC timestamp, admin email, action type, target entity, detailed justification, and a truncated `SHA-256` integrity hash.

---

## 4. Source Code File Reference

| Purpose | File Path |
|---|---|
| **Backend Admin Router** | [`services/backend/app/admin/router.py`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/services/backend/app/admin/router.py) |
| **Backend Admin Service** | [`services/backend/app/admin/service.py`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/services/backend/app/admin/service.py) |
| **Frontend Admin Page** | [`apps/web/src/app/[locale]/admin/page.tsx`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/apps/web/src/app/[locale]/admin/page.tsx) |
| **Frontend Admin Dashboard Client** | [`apps/web/src/app/[locale]/admin/AdminDashboardClient.tsx`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/apps/web/src/app/[locale]/admin/AdminDashboardClient.tsx) |
| **Navbar Header Navigation** | [`apps/web/src/components/layout/Header.tsx`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/apps/web/src/components/layout/Header.tsx) |
| **Brain Artifact Documentation** | [`ClaimCraft_BD_Admin_Portal_Architecture_and_Guide.md`](file:///C:/Users/sakib/.gemini/antigravity/brain/c1cb0317-6e44-4f55-8b25-0c3a7e91a58a/ClaimCraft_BD_Admin_Portal_Architecture_and_Guide.md) |

