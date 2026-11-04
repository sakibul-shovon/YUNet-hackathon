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
