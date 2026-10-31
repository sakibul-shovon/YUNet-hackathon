# ADR-106: PDF Parsing, Licensing and Bengali Typography Rendering

## Context
PDF processing involves two distinct challenges:
1. Parsing incoming Bengali and English receipts/documents with spatial coordinates.
2. Generating high-fidelity official complaint PDFs with complex Bengali script conjuncts (যুক্তাক্ষর).
3. Licensing constraints: PyMuPDF is licensed under AGPL-3.0, which imposes copyleft restrictions on the broader application.

## Decision
1. **Parser Selection:** Use `pdfplumber` and `pypdfium2` (permissive Apache/BSD licenses) alongside Tesseract 5 (`ben` + `eng`) for local OCR.
2. **PDF Generation:** Use headless Chromium (via Playwright) rendering controlled HTML/CSS templates with bundled open-source Bengali fonts (Hind Siliguri / Kalpurush).
3. **No AGPL Dependency:** PyMuPDF is excluded from the default production dependency tree.

## Consequences
- Compliant software licensing without AGPL encumbrance.
- Proper HarfBuzz-backed Bengali font rendering in output complaint documents.
