# Ebarki final system audit

Audit date: 5 November 2026, Asia/Dhaka. **Release verdict: NOT READY.**

This is the initial audit checkpoint. Read the [stabilization follow-up](EBARKI_STABILIZATION_FOLLOWUP.md) for subsequent fixes and current validation. It found an additional fabricated legal subsection and migration gaps that this initial checkpoint missed. Earlier failed results remain historical evidence, not current capability claims.

This is an independent examination of the current local implementation, with fixes and regression evidence. It is not a certification of the hosted product, legal correctness, universal accessibility, or every input path. Prior completion statuses and live-check summaries were treated as leads, not proof.

## Scope and evidence

The audit consulted the root AGENTS.md, task state/handoff, protected execution plan, README, approved Ebarki experience specification, connected-feature documentation, hackathon source document, relevant ADRs, current routes, APIs, source and tests. Graph queries preceded targeted source inspection. The protected specifications were not rewritten. Existing graph-output changes were present at the start and were preserved as generated project state.

The actual system is a Next.js/React bilingual application, a same-origin web BFF, FastAPI, SQLAlchemy, local SQLite and owner-scoped local evidence storage. Groq is configured server-side. Gemini is unavailable in this environment. Background case runs use FastAPI background tasks with persisted receipts, SSE and polling; this audit does not establish a durable distributed worker deployment.

Evidence is deliberately separated:

- [Feature/test matrix](EBARKI_FEATURE_TEST_MATRIX.md): live, fictional-demo, optional and incomplete features, with explicit test scope.
- [Issue ledger](EBARKI_ISSUE_LEDGER.md): reproduction, root cause, fixes, regressions and open limitations.
- [Fixture pack](fixtures/README.md) and [ground truth](fixtures/GROUND_TRUTH.json): actual PDFs/images/PCM speech, exact amounts/dates/messages and hashes.
- [Initial live baseline](evidence/live-baseline.json), [expanded retest](evidence/live-retest.json), and [final live run](evidence/live-final.json): real Next.js BFF responses from separate fictional cases.
- [Core validation](evidence/core-validation.txt), [successful foundation validation](evidence/foundation-fresh-validation.txt), and [environment validation](evidence/environment-validation.json): exact command results. Failed intermediate builds are retained separately.
- [API route inventory](evidence/api-route-inventory.json): actual running routes, excluding duplicate proxy aliases.
- PDF exports and rendered pages in [evidence/](evidence/) provide inspectable artifact evidence. Native Chrome screenshots were observed in the tool transcript; no claim is made that screenshot files were saved from that tool.

## What actually worked

Fresh, independent fictional cases were created with English, natural Bangla, Banglish, mixed digits, minimal information, long Unicode input and an adversarial narrative. API checks went through the running Next.js BFF, not only an in-memory test client. Money normalization preserved 732,150 poisha, including Bangla/mixed digits and decimals. The ISO-date extraction defect was reproduced and fixed.

A new incognito Chrome session completed the ordinary English intake, optional date left empty, genuine PDF selection through the native picker, save/consent, processing, source inspection, case-specific briefing, reply generation, editing, saving and reloading. The observed case was `a3e83ca2-ad02-486d-b688-23bdf5d3cf57`; its older incorrect date was visible before the extraction fix. Later fresh BFF cases verified the fix. This audit does not claim that previously saved incorrect facts are automatically corrected.

Browser observations also covered language continuity into the same Bangla case, decimal-taka display, desktop light/dark styling, Bangla shaping, and the collapsed workstream/mobile dock at an emulated 412px viewport. The viewport was Chrome device emulation, not a physical Pixel device. Reply edits persisted after reload and were labeled as the user's edited wording after the attribution fix.

API and integration checks exercised genuine PNG/JPEG/PDF/WAV ingestion, multipage native text and coordinates, pasted/manual text, date confirmation, source review/reopen/exclusion, two-payment reconciliation, exact-file duplicates, unrelated records, version guards, stale PDF rejection, reply edits, PDF/ZIP exports, filing preparation, cancellation, terminal SSE history, consent denial/withdrawal, private previews, and cross-owner rejection. Separate generated registered accounts verified login/reopening and isolation; their credentials were never written to the reports.

## Real AI execution

| Feature | Actual path/model | Evidence and limits |
|---|---|---|
| Situation summary, English/Bangla | `/cases/{id}/runs` → `understanding.py` → Groq `openai/gpt-oss-120b` | Real case-specific summaries and provider acknowledgements. Original-account fallback is explicitly labeled. |
| Image OCR | Consent-scoped `record_reader.py` → Groq `qwen/qwen3.8-27b` | Real clear receipt and seller-chat pixels produced matching amounts/text and proposed boxes. Boxes remain model proposals. Lower-quality/Bangla coverage was rate-limited in the final full run. |
| Audio transcription | Actual WAV upload → Groq `whisper-large-v3` | Real segment times and transcript. A general currency glossary improved the earlier “thakar/poise har” output to “7,321 taka and 50 poisha”; no expected amount was supplied in the request prompt. |
| Contextual explanation | `/copilot/chat` → Groq `openai/gpt-oss-120b` | English/Bangla real responses; no legal source context is falsely claimed. Browser ask-box interaction remains unverified. |
| Buyer reply wording | `/reply-preparations` → Groq `openai/gpt-oss-120b` | English/Bangla BFF executions; an English generated reply reached the browser, was edited and reopened. Nothing was sent. |

Provider receipts contain provider/model/status/request ID when acknowledged, not secret headers. Cached readings retain the original receipt and identify the reused run. UI labels distinguish previous readings from new calls. Native PDF extraction, pattern extraction, lexical retrieval, three-valued rules and document templates are deterministic operations, not live model reasoning. There are no verified hidden multi-agent executions.

The adversarial summary outputs attributed malicious requests to the input author; they did not establish an actual filing, guarantee or credential disclosure. Early substring-based audit assertions produced false positives for that attribution. Raw failing outputs are retained, and the final assertion distinguishes product/first-person action claims from quoted requests. This is a corrected test oracle, not evidence that arbitrary prompt injection is solved.

Invalid credentials/rate-limit/server-error handling has deterministic regression coverage. Live vision actually returned HTTP 429 and produced `manual_required`, rather than fabricated OCR. Timeout, malformed response, interrupted-run recovery and provider-specific coverage are identified individually in the matrix; untested failure combinations are not passed.

## Material failures and stabilization

The audit found unauthenticated merchant search reading private cases, legacy global-demo authorization exceptions, fabricated merchant/community/admin data, legacy fake audio and VLM output, automatic inclusion of unrelated receipts, wrong incident dates, Unicode preview header failures, incomplete derivative deletion, misleading draft legal conclusions and insufficient Bengali font coverage.

Fixes enforce owner checks, remove invented public data, require explicit payment review/linking, purge source derivatives, reject development signing keys in production, preserve money/date semantics, record provider acknowledgements and label cache/edit origins. Drafts now express the consumer's account/request without automatic statutory entitlements. Old template versions are retired and cannot silently export as current. PDF rendering now uses a full Bengali font with Latin punctuation in a single shaped paragraph. See [ADR-110](../adr/ADR-110-ebarki-release-audit-integrity.md).

Historical tests that expected decoded binary speech markers, proportional word timestamps, invented VLM disagreements or automatic refund entitlements were corrected to test the integrity requirement. None was skipped to obtain a green suite. New regressions cover actual source relevance, owner isolation, date extraction, deletion, Unicode headers, truthful errors, administrative metrics and preparation wording.

## Remaining dummy/incomplete behavior

- Landing illustrations remain deliberately fictional and browser-local, with visible no-live-AI labels. They are isolated from consumer cases. Full interaction of all three illustrations was not independently completed in the browser.
- Merchant research is an honest empty public-data state. Private disputes never populate it. Community publishing/reactions/comments are unavailable (503) pending durable storage/moderation; invented seed people, testimonials and legal advice are removed.
- Legacy layout analysis reports image-color inspection only; no OCR, roles, boxes or money are invented. Legacy audio accepts an explicitly provided transcript or returns unavailable. Real media processing is in Evidence story.
- Scanned/image-only PDF OCR is not implemented. Original preview and manual transcript remain available. It must not be marketed as verified scanned-PDF OCR.
- Administrative alerts/overrides/audit display still include process-local state. The statistics response says it resets on restart. Recovered-money totals and route distributions are not invented. Production administration needs further durability and browser acceptance.
- Dense/model retrieval and optional Gemini paths are not verified production inference. The current normal run uses lexical retrieval.

## Blocking release gaps

1. **Browser completion BLOCKED.** The browser access host was unavailable. Native Chrome initially worked, then concurrent input and mismatched screenshot targeting interrupted coverage. After resume, the original window was gone; Chrome was reopened, but Computer Use explicitly stopped because it could not determine the Windows browser URL confidently enough to enforce policy. No further UI calls were made after that stop. Draft/export/handoff clicks, all input methods, complete mobile flows and administrator screens remain unverified through the browser.
2. **Hosted deployment UNVERIFIED.** Only localhost was tested. There is no independently verified public HTTPS application URL, production persistence, cookie/CORS behavior, worker recovery, backup recovery or external judge access in this audit.
3. **Source/legal review UNVERIFIED.** Tests establish procedural implementation and citation structure, not correctness of every current legal rule, official destination, deadline or claimed prior human review. Historical sign-off documents are not substituted for actual reviewer evidence. The audit makes no legal determination.
4. **Submission materials incomplete.** Unsupported claims were removed from submission copy and five-slide Markdown content. A final exported deck, genuine sticker provenance and eligibility/submission fields still need verification. The official rules require a public app and at most five slides. The earlier release approval file asserted unverified review-board/CISO sign-off and used the SHA-256 of empty content; it has been replaced by an explicit unverified status record. The [official page](https://yunet-aignite26.devpost.com/rules) shows inconsistent deadline times between header and body; this was not silently resolved.
5. **Unverified environments.** Physical devices, screen readers, full keyboard-only navigation, reduced-motion rendering, quantitative contrast/performance and actual Bangla microphone speech were not tested. No WCAG compliance claim is justified.

## Exact validation and verdict

Final numeric results are recorded in `evidence/validation-summary.json` and the command/response files above. The initial expanded BFF baseline had 68 PASS / 4 FAIL (date and receipt integrity). The expanded retest had 86 PASS / 1 automated false-positive injection assertion. The final full BFF run had 89 PASS / 1 FAIL, with the latter caused by HTTP 429 preventing Bangla-image execution; treat that input's accuracy as BLOCKED, never as passed. A separate fresh retry executed successfully and read the amount/reference; it misread the merchant wording. Exact merchant OCR is FAIL, requiring human correction. See evidence/ai-bangla-retry.json.

Core regression reached **171 passed, 7 warnings**. Foundation initially passed, then a concurrent development restart removed Next.js generated type files during another build. That failed intermediate command is retained. A subsequent reused-cache build hit a OneDrive readlink error. Automatic review rejected cache deletion, so a fresh, ignored .next-audit-check directory was used without deletion; its production build/typecheck/lint/i18n checks passed (foundation-fresh-validation.txt). Contract generation succeeded; running-schema parity is checked independently. These technical checks supplement browser coverage and cannot establish release readiness alone.

The task-runner code graph refresh completed with **3,808 nodes, 9,665 edges and 249 communities**. Its separate graphify environment lacks the PDF extraction extra, so this refresh proves AST/code updates, not new semantic analysis of the fixture PDFs. See [graph update log](evidence/graph-update.txt).

Packaging verification matches all **20 fixture hashes** against their known ground truth and all **19 indexed fixture files** against their original bytes. Git attributes prevent Windows newline conversion from changing the fixtures. The valid oversized recording remains reproducible locally and excluded from Git. The final configured-secret-value scan found no matches in **632 files**; this is the recorded scope, not a guarantee about every possible secret.

**NOT READY** is justified by the unverified public deployment, incomplete browser acceptance and source/submission review gaps. The local implementation is materially safer and has genuine AI execution evidence, but an independent judge still needs a fully verified hosted, usable journey. P21.1 must remain in progress.
