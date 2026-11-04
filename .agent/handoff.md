# Ebarki agent handoff

Updated: 5 November 2026, Asia/Dhaka. Active task P21.1 remains **IN_PROGRESS**. Independent audit verdict: **NOT READY**.

Read `docs/qa/EBARKI_FINAL_SYSTEM_AUDIT.md`, `EBARKI_FEATURE_TEST_MATRIX.md`, `EBARKI_ISSUE_LEDGER.md`, `docs/qa/evidence/validation-summary.json` and ADR-110 before further release claims. The protected plan, blueprint and hackathon source document are unchanged.

## Stabilization completed

Owner checks now include historic fixed demo IDs. Public merchant search no longer reads private cases or invents statistics. Fabricated community/admin seeds are removed; public community writes are explicitly unavailable pending durable storage/moderation. Legacy audio/layout adapters no longer fabricate observations. Real image/audio processing remains consent-scoped in Evidence story.

Payment relevance requires explicit review/linking. Unrelated PDFs stay out; duplicate suppression and exclude/reopen behavior are tested. ISO incident dates, original date metadata, decimal money, Unicode preview headers and source derivative deletion were repaired. Production startup rejects published development signing keys.

Provider acknowledgements and cache markers are recorded. Reply edits have honest provenance labels. Preparation template v2 expresses reported accounts and requests without automatic legal entitlements; old templates cannot export as current. Full OFL Bengali font and single-font shaping fixed visible PDF punctuation failures. All final English/Bangla export pages were rendered and visually inspected.

Prior release-board/CISO approval assertions and the empty-content manifest hash were unsupported. `docs/compliance/release_manifest_approval.md` now explicitly says UNVERIFIED. Do not substitute old task statuses for actual qualified review. Submission/deck Markdown and administrator documentation now describe Ebarki truthfully.

## Exact current checks

- Core: **171 passed, 7 warnings**, exit 0.
- Foundation: i18n **223 keys**, Ruff, production build/typecheck passed, exit 0, using fresh `EBARKI_NEXT_DIST_DIR=.next-audit-check` through `python scripts/tasks.py check --scope foundation`.
- Intermediate check builds failed from generated type/cache interference and OneDrive `EINVAL readlink`. Automatic review rejected deleting the old transient cache. A fresh ignored build directory succeeded without deletion.
- Contracts regenerated; running OpenAPI parity passed.
- Code graph refreshed: 3,808 nodes, 9,665 edges, 249 communities. The graphify PDF extra is unavailable; fixture PDF verification used the backend/rendering tools separately.
- Final live BFF suite: **89 PASS / 1 FAIL**, with the failed condition blocked by real provider HTTP 429. Separate fresh Bangla OCR execution and amount/reference checks passed, but exact merchant text failed. Keep both results.
- Thirty public language/route HTTP responses passed. This is not browser acceptance.
- Configured secret-value scan: no matches in 632 tracked/QA/client-asset files at the recorded checkpoint.
- Fixture integrity: all 20 local hashes and all 19 indexed fixture byte comparisons pass. Git attributes preserve media and narrative bytes across checkout.
- Actual 20-file fixture manifest includes native/multipage/scanned PDFs, real image pixels, a playable 26.6s speech WAV, Unicode duplicates, corrupt/empty/unsupported inputs, and a valid oversized PCM recording generated locally and ignored by Git.

## Browser evidence and blocker

A fresh native Chrome incognito session created a new English case, selected a real PDF, granted test-only consent, processed the case, inspected source/summary, generated a buyer reply, edited/saved/reloaded it, switched language and displayed selected light/dark/Bangla/mobile layouts. A 412px viewport was emulation, not a physical device.

The browser host was unavailable. Native control later detected concurrent input/mismatched screenshot targeting. On resume the original window was gone; Chrome was reopened, but Computer Use explicitly stopped because the current Windows browser URL could not be established confidently. No more UI calls were made. Full draft/export/handoff, all input methods, mobile/keyboard/AT parity and privileged admin browser acceptance remain BLOCKED/UNVERIFIED.

## Remaining release gates

Verify an actual public HTTPS deployment and production persistence/cookies/CORS/worker recovery; obtain real source/legal review; finish the remaining browser matrix with supported tooling; check exact OCR names and degraded-image retry UX; verify the final <=5-slide exported deck, sticker provenance and submission fields. Scanned-PDF OCR, semantic duplicate detection and optional Gemini/dense inference are not verified capabilities. Administrative runtime-only stores remain a disclosed limitation.

Provider keys remain only in ignored server configuration. Never print or commit them. The tested Groq models are `openai/gpt-oss-120b`, `qwen/qwen3.8-27b` and `whisper-large-v3`. No real records, seller messages, payments or government submissions were used. Ebarki does not submit complaints automatically.

Use the Python task runner and graph-first protocol. Local development: `python scripts/tasks.py dev --no-reload`. Preserve the audit's failed evidence as well as passes. The stabilization checkpoint is intended for origin/main; its actual commit and remote receipt are recorded in Git history and the delivery response. Keep P21.1 in progress until the open release gates close.
