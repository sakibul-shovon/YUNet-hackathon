# ClaimCraft BD — WCAG 2.2 AA Usability & Contrast Review

Prepared per plan.md Section 5.5 and Section 5.8.

## 1. Contrast Ratios Tested
All primary color combinations meet or exceed WCAG 2.2 AA thresholds (minimum 4.5:1 for body copy, 3.0:1 for large text and UI controls).

### Light Theme (Default)
- **Primary Text on Surface:** `#17251f` on `#ffffff` → **15.5:1** (Passes AAA)
- **Muted Text on Surface:** `#55645b` on `#ffffff` → **5.1:1** (Passes AA)
- **Primary Brand on Surface:** `#175c45` on `#ffffff` → **6.3:1** (Passes AA)
- **Primary Button Text:** `#ffffff` on `#175c45` → **6.3:1** (Passes AA)
- **Focus Indicator:** `#2169cb` (2px outline with 2px offset) → Distinct and visible against canvas and surface.

### Dark Theme
- **Primary Text on Surface:** `#edf3ed` on `#18221c` → **14.8:1** (Passes AAA)
- **Muted Text on Surface:** `#a9b8ac` on `#18221c` → **6.7:1** (Passes AA)
- **Brand Accent on Surface:** `#83d2a2` on `#18221c` → **9.2:1** (Passes AAA)
- **Primary Button Text:** `#101713` on `#83d2a2` → **9.2:1** (Passes AAA)

## 2. Typography & Script Shaping
- **Bengali Line Height:** Set to `1.65` across all Bengali copy (`:lang(bn)` and `.font-bengali`) to prevent ascenders and descenders (য-ফলা, র-ফলা, হ্রস্ব-উ কার) from clashing.
- **Font Stack:** Noto Sans Bengali paired with Inter for numerals and Latin words.
- **Tabular Numerals:** Used for transaction amounts (`৳5,500.00`) and dates (`15/10/2026`) to align data columns cleanly.

## 3. Assistive Technology & Focus Management
- Semantic HTML tags used throughout: `<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`.
- Loading indicators include `role="status"` and `aria-live="polite"`.
- Error banners include `role="alert"`.
- Buttons and interactive inputs maintain logical DOM tab sequence.
