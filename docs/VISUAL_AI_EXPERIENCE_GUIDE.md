# EbarKi (এবার কি?) — Visual AI-Native Components Documentation
## Interactive HUD Gauge, Forensic OCR Canvas, Reasoning Trace & Generative Notice Studio

---

## 1. Overview of Implemented Visual AI Features

To move ClaimCraft BD from a backend-heavy technical system into a kinetic, visually stunning AI-native application, four bespoke components were engineered and embedded directly into the primary dispute workflows:

```
                      ┌──────────────────────────────────────────────────┐
                      │    CLAIMCRAFT BD — VISUAL AI ARCHITECTURE        │
                      └──────────────────────────────────────────────────┘
                                                │
         ┌──────────────────┬───────────────────┼───────────────────┬──────────────────┐
         ▼                  ▼                   ▼                   ▼                  ▼
    Viability HUD      AI Reasoning       Document OCR        Generative Legal     Super Admin
    Circular Gauge     Trace Accordion    Grounding Canvas    Notice Studio        Command Center
```

---

## 2. Component Specifications

### 1. Live "AI Case Viability HUD" (`ViabilityHUDGauge.tsx`)
- **File Path:** [`apps/web/src/components/ai/ViabilityHUDGauge.tsx`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/apps/web/src/components/ai/ViabilityHUDGauge.tsx)
- **Embedded In:** [`DynamicCaseOverview.tsx`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/apps/web/src/components/cases/DynamicCaseOverview.tsx)
- **Visual Capabilities:**
  - **Animated Circular SVG Arc:** Uses `strokeDashoffset` transition with spring easing to animate from `0%` to `92%`.
  - **Real-Time Factor Breakdown:** Evidentiary Completeness (98%), Statutory Compliance (100%), Optimal Remedial Pathway (DNCRP Directorate).
  - **Interactive Scenario Simulation:** The **"Simulate Lost Receipt"** button toggles a counterfactual simulation: the HUD physically recalibrates down to **`45%`** with amber warning styling and a badge (`-47% Evidentiary Gap`).

### 2. Kinetic "AI Reasoning & Thinking" Trace (`AIReasoningTrace.tsx`)
- **File Path:** [`apps/web/src/components/ai/AIReasoningTrace.tsx`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/apps/web/src/components/ai/AIReasoningTrace.tsx)
- **Embedded In:** [`DynamicCaseOverview.tsx`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/apps/web/src/components/cases/DynamicCaseOverview.tsx)
- **Visual Capabilities:**
  - Collapsible glassmorphism drawer styled with subtle emerald ambient lighting.
  - Monospace execution timer: `✦ AI Procedural Reasoning & Deterministic Trace • 412ms`.
  - Step-by-step audit sequence across 4 statutory gates with elapsed millisecond durations and statutory citations (e.g. *Section 45 & 60 of Consumer Rights Protection Act 2009*).

### 3. Interactive Multimodal Document OCR Canvas (`DocumentGroundingCanvas.tsx`)
- **File Path:** [`apps/web/src/components/ai/DocumentGroundingCanvas.tsx`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/apps/web/src/components/ai/DocumentGroundingCanvas.tsx)
- **Embedded In:** [`EvidenceVaultClient.tsx`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/apps/web/src/components/cases/EvidenceVaultClient.tsx)
- **Visual Capabilities:**
  - **Dual-Pane Split Layout:** Extracted structured tokens on the left, high-fidelity document canvas on the right.
  - **Bidirectional Cross-Hover Spotlight:** Hovering over any entity (e.g. `Amount: BDT 3,200.00` or `TrxID: BL9X882KZP`) spotlights the exact pixel coordinates on the document canvas with an animated emerald laser ring and glowing tooltip.
  - **Laser Grid Switch:** Toggle button to activate or deactivate the visual OCR bounding box grid.

### 4. Generative Legal Demand Notice Studio (`DemandNoticeStudio.tsx`)
- **File Path:** [`apps/web/src/components/ai/DemandNoticeStudio.tsx`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/apps/web/src/components/ai/DemandNoticeStudio.tsx)
- **Embedded In:** [`ActionDraftViewer.tsx`](file:///c:/Users/sakib/OneDrive/Desktop/ostad%20hacakathon/apps/web/src/components/cases/ActionDraftViewer.tsx)
- **Visual Capabilities:**
  - **Strategic Tone Switcher:** 3 modes (`Formal Statutory`, `Strict & Urgent`, `Amicable Negotiation`).
  - **Fluid Typewriter Streaming:** Switching tone triggers an asynchronous typewriter text-generation effect with a blinking terminal cursor.
  - **Pre-Action Legal Safeguards:** Embedded statutory compliance notes and 1-click clipboard / signed PDF export.

---

## 3. Live Verification URLs

| View | Live Local URL |
|---|---|
| **Case Overview (HUD & Reasoning)** | [`http://localhost:3000/en/cases/c5cdeb10-e5db-43c6-9e52-d28aaf457f48`](http://localhost:3000/en/cases/c5cdeb10-e5db-43c6-9e52-d28aaf457f48) |
| **Evidence Vault (Interactive OCR Canvas)** | [`http://localhost:3000/en/cases/c5cdeb10-e5db-43c6-9e52-d28aaf457f48/evidence`](http://localhost:3000/en/cases/c5cdeb10-e5db-43c6-9e52-d28aaf457f48/evidence) |
| **Action Studio (Typewriter Notice)** | [`http://localhost:3000/en/cases/c5cdeb10-e5db-43c6-9e52-d28aaf457f48/actions`](http://localhost:3000/en/cases/c5cdeb10-e5db-43c6-9e52-d28aaf457f48/actions) |
| **Super Admin Command Center** | [`http://localhost:3000/en/admin`](http://localhost:3000/en/admin) |

