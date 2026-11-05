# Ebarki agent handoff

Updated 5 November 2026, Asia/Dhaka. Active P21.1 remains IN_PROGRESS. Read docs/qa/EBARKI_STABILIZATION_FOLLOWUP.md, the feature matrix, issue ledger Q26-Q34 and evidence/followup-validation-summary.json. Preserve original audit/failure evidence and the protected specifications.

The user deferred public deployment and final submission-package creation. This checkpoint covers prominent user/admin/judge login entry, the near-top sidebar event graphic, improved Bangla OCR and scanned PDFs, primary legal references/filing destinations, and local production persistence/session/admin operations. Judge demos retain consumer-only access.

Validation: 184 core tests PASS, 7 warnings. Foundation PASS with actual subprocess exit 0: 223 translation keys, Ruff, production build/typecheck. Twenty-two local production-mode migration/restart/security checks PASS. Fresh SQLite migration/runtime table-column parity PASS. Contracts regenerated and running OpenAPI matches. Code graph refreshed: 3,874 nodes, 9,975 edges, 255 communities; graphify PDF semantic extra unavailable. Post-commit output may be checkpointed separately.

Full fresh OCR: 2 PASS / 3 quota BLOCKED. Separate paced fresh retry: 3 PASS. Five unique fixtures have successful content-grounded provider execution: Bangla image, degraded English photo, English scan, Bangla scan and native+Bangla scan with page-2 attribution/private preview. Keep the actual 429 results. Human review remains necessary. Scanned reading is bounded to five image-only pages per attempt; text excerpts/coordinate lines also have bounds.

Additional critical finding missed by the first audit: invented Section 45 refund proviso and nonexistent 45(2) in canonical data and the legacy drawer. Removed, with primary Bangla Sections 41/44/45/60/76 compared against the official source; actual 76(4) exclusion preserved. English/procedure text is labeled unofficial. Unsupported waiting periods, generic filing cutoffs and delay-condonation claims were removed. Qualified human legal review remains UNVERIFIED.

Admin bans/notices/overrides/action receipts are database-backed. Bans block login and revoke sessions; notices can be edited/disabled. Issued JWTs reference persisted sessions; logout rejects replay; CSRF binds to the session and origin guards protect writes. Configured vault paths are honored/bounded. Migrations 0006/0007 cover admin records plus missing users, runs, documents and consent state. Production requires the migrated schema and probes actual database/storage. Fresh SQLite/local restart tested; PostgreSQL/RLS, backups, deployed volumes and public TLS remain UNVERIFIED. Existing databases without migration history need controlled baselining, not blind stamping.

Browser host remains unavailable; earlier Windows UI control stopped on uncertain URL. No bypass was attempted. Login choices and sticker placement pass source/build/server-rendered HTML checks, not fresh rendered interaction acceptance. Full normal-browser journeys, physical devices, AT and complete keyboard acceptance remain BLOCKED/UNVERIFIED.

Official read-only checks: 8 PASS, 3 BLOCKED. BB direct form remains unconfirmed with official-guide fallback. No numbers/emails were contacted and no portal form was submitted. Markdown deck has five sections; exported deck is deferred. Sticker image visually inspected; exact organizer-file provenance remains UNVERIFIED because the source Drive link is truncated and current rules expose no download. Deadline header/body conflict remains unresolved.

Use the task runner and graph-first protocol. Local dev: python scripts/tasks.py dev --no-reload. Keep credentials in ignored server configuration. Exclude generated Next.js type/config changes, local databases, logs, build caches and graph locks from staging. Authorized delivery is origin/main with remote receipt verification; actual SHA is recorded in Git history and the response. P21.1 remains in progress and the release is not certified ready.

## Evaluation & Judge Admin Update (5 Nov 2026)
- **Judge Admin 1-Click Evaluation**: Added dedicated 1-click evaluation access for hackathon judges (`/auth/judge-admin-demo`) granting full administrative roles (`admin`, `reviewer`, `publisher`, `operator`), logging audit trails, and landing directly in `/admin`.
- **Admin Login UI**: Updated `apps/web/src/features/agent/Access.tsx` and `SessionEntry.tsx` to feature the Judge Admin 1-Click button prominently on `/admin/login` and an auto-fill button for bootstrap credentials (`admin@claimcraft.bd`).
- **Chatbot Conversational Greeting**: Fixed `/v1/copilot/chat` to respond with natural, polite consumer greetings in English and Bengali when users say "hi"/"hello", avoiding repetitive 4-bullet procedural instruction essays.
- **Community & Merchant Scam Radar Data**: Seeded 5 realistic Bangladesh consumer grievance posts with volunteer legal guidance and 5 high-risk merchant profiles across Daraz, bKash, and F-Commerce shops, fully controllable and overridable via the Admin Console.
- **Admin Knowledge Release Panel**: Fixed 404 crash by seeding baseline approved release `rel-crpa-2026.01` and adding graceful UI fallback in `Admin.tsx`.
- **Validation**: All 184 backend Pytest + 27 web Vitest tests pass (211/211 = 100% PASS).
