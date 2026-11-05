# Ebarki audit evidence

All case content is fictional. Tokens, generated account credentials, upload URLs and provider authorization headers are excluded.

- `live-baseline.json`: initial complete independent BFF run, 68 PASS / 4 FAIL.
- `live-retest.json`: expanded run after integrity fixes; an automated injection substring assertion is an attributed-request false positive documented in the audit.
- `live-final.json` / `live-final-console.txt`: final complete live BFF run, 89 PASS / 1 FAIL; Bangla OCR was blocked by provider HTTP 429 in that run.
- `ai-bangla-retry.json`: separate fresh provider execution succeeded for amount/reference, but exact merchant text differs from the fixture. This is not perfect OCR.
- `export-final-en.pdf`, `export-final-bn.pdf` and `verified-final-*-page*.png`: current preparation-template exports and rendered pages.
- `export-baseline-*`, `export-retest-*`, `render-*`, `final-draft-bn-page1.png`: earlier artifacts retained to show defects and intermediate states. They are not current approved output; early Bengali PDFs have visible glyph defects.
- `core-validation.txt`: latest full backend regression, including deterministic failure/authorization checks. Tests use isolated provider doubles where appropriate; live-provider proof comes from separate JSON receipts.
- `foundation-validation.txt`, `foundation-final-validation.txt`: failed intermediate builds (generated-type/cache interference and OneDrive readlink respectively).
- `foundation-fresh-validation.txt`: successful production build/typecheck/i18n/lint in a fresh directory through the task runner.
- `environment-validation.json`: 30 public language/route HTTP responses, configured-value secret scan and running OpenAPI parity. HTTP route success does not prove browser interaction.
- `final-environment-validation.json`: final fresh-build/client secret scan and schema parity.
- `api-route-inventory.json`: actual primary API routes and tags, including compatibility and administrative routes.
- `validation-summary.json`: final counts, scopes, limitations and release verdict.
- `graph-update.txt`: completed code/AST refresh; PDF semantic extraction unavailable in the separate graphify environment.

Native browser screenshots were displayed and visually inspected in the computer-use transcript. They were not exported as local screenshot files. The browser tool later stopped on Windows URL validation, so remaining native UI acceptance is blocked. No physical-device, screen-reader, government filing, seller message or payment evidence is claimed.

## Ebarki stabilization follow-up

- `followup-live-ocr.json`: five fresh cases; two PASS, three quota BLOCKED. `followup-ocr-retry.json`: three separate fresh paced retries PASS, including Bangla scan and page-2 hybrid PDF attribution/preview. Earlier `followup-ocr-baseline.json` retains the first renderer failure.
- `followup-core-verified.json/.txt`: final 184 PASS / 7 warnings, actual process exit 0; `followup-core-validation.txt` is the earlier 183-test checkpoint. `followup-core-baseline.txt` retains intermediate failed integration/oracle assumptions; it is not the final result.
- `followup-foundation-verified.json/.txt`: actual process exit 0 and successful production build/typecheck/i18n/lint. `followup-foundation-validation.txt` retains the earlier PowerShell wrapper ambiguity despite the task runner success marker.
- `followup-production-mode.json`: 22 PASS on a migrated, isolated local production-mode API, including process restart. The earlier baseline's preview failure was a wrong test URL, corrected without changing persistence behavior.
- `followup-migration-schema.json`: fresh SQLite migration matches runtime table/column presence. The baseline records the three missing tables and consent column before migration 0007.
- `followup-laws.json`: captured primary-law sections, timestamps and response hashes. `followup-official-links.json`: eight read-only page observations PASS, three connection/timeout BLOCKED. These are not qualified legal approvals or filing receipts.
- `followup-submission-requirements.json`: official rule observations, local graphic hash/dimensions, five Markdown slide sections and explicit deferred/unverified artifact states.
- `followup-environment-validation.json`: current schema parity, configured-value scan, original/additional fixture integrity, and login/sidebar server-rendered HTML. HTML is not browser acceptance.
- `followup-graph-verified.json/.txt`: actual graph refresh exit and AST update. The graphify environment still lacks its PDF semantic extraction extra; actual PDF testing used the application/runtime tools.

`followup-role-baseline.json` retains the additional failed positive role-assignment checks. A transactional flush-order bug was fixed; promotion/demotion and restart persistence now pass.
