# ClaimCraft BD — Screen Layout & Responsive Hierarchy

Prepared per plan.md Section 5.2 and Section 5.3.

## 1. Desktop Layout Hierarchy (1024px – 1440px)
```text
TOP: [Shield] ClaimCraft BD | Event Badge | [My Cases] [Scenarios] | [EN/বাংলা] [Theme] | [Start Case CTA]
──────────────────────────────────────────────────────────────────────────────────────────────────────────
NAV TABS: Overview  |  Evidence  |  Paths  |  Actions  |  Activity
──────────────────────────────────────────────────────────────────────────────────────────────────────────
MAIN AREA (66% Width)                         CONTEXT SIDEBAR (33% Width)
┌─────────────────────────────────────────┐   ┌─────────────────────────────────────────┐
│ ONE NEXT STEP CARD                      │   │ CASE SUMMARY                            │
│ Clarify amount (৳5,500 vs ৳5,000)       │   │ Disputed sum, date, merchant            │
│ [Add 2nd receipt] [Correct amount]      │   └─────────────────────────────────────────┘
├─────────────────────────────────────────┤   ┌─────────────────────────────────────────┐
│ WHAT HAPPENED TIMELINE                  │   │ DESIRED REMEDY                          │
│ 15 Oct Order -> Payment -> Blocked      │   │ Full refund (৳5,500)                    │
├─────────────────────────────────────────┤   └─────────────────────────────────────────┘
│ FACTS NEEDING REVIEW                    │   ┌─────────────────────────────────────────┐
│ Material assertions requiring user veto │   │ RELEVANT AUTHORITIES                    │
├─────────────────────────────────────────┤   │ DNCRP s.45, s.76                        │
│ ACTION SHORTCUTS                        │   └─────────────────────────────────────────┘
└─────────────────────────────────────────┘
```

## 2. Mobile Responsive Layout (360px – 768px)
- **Top Header:** Collapses navigation links into responsive icons; brand and language/theme toggles remain accessible.
- **Navigation Tabs:** Horizontal swipeable/scrollable pill strip without clipping focus rings.
- **Main & Context Stacking:** The 2/3 Main View displays first; Context Sidebar stacks below to prioritize user action.
- **Minimum Touch Targets:** Buttons, radio options, and tab pills enforce at least 44px height and width for accessibility.
- **Evidence Canvas:** Panning and zooming are bounded within the evidence container to prevent horizontal page overflow at 360px width.

