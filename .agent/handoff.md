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

## Cinematic film review cut — 5 November 2026

User-authorized film work is in production/film, separate from P21.1. Read README.bn.md, QUALITY_REPORT.bn.md and FEATURE_INVENTORY.bn.md. Main captioned/clean exports are exactly 240 seconds, 1080p30, 7200 frames; supplementary walkthrough is 144 seconds. Full decode passes, no decode errors; measured -16.02 LUFS/-0.99 dBTP. Acoustic CTC word alignment: 417 words, 69 cues, no overlaps; independent ASR discrepancies retained, five final AAC/PCM timing windows show zero measured lag. Nineteen main and eleven supplementary final-frame samples visually inspected; full human listening/motion sign-off remains unverified.

Real isolated local app/provider calls and fictional evidence were captured; no API result mocks or official submissions. New community posts are unavailable; fictional seeded discussion/comment shown. Reply required user wording correction, preserved honestly. Matrix maps representative scenes for 78 of 125 families, 47 without a scene; grouped-feature completeness is explicitly not claimed. First mux timestamp-scale failure and failed workspace-search capture are retained as evidence. Authoritative renderer is finish.py hybrid with 90kHz-normalized segment streams, not an unverified full Remotion UI render.

Local out/ includes MP4s, caption ZIP, editable-source ZIP, review sheets and hashes. Large generated media, model weights, database/session state and credentials are excluded from Git; source/captions/reports/fictional receipt records are checkpointed. Film servers on 3002/8002 were stopped; original 3000/8000 services were not intentionally changed. Restore-generated Next config/type files was completed. P21.1 and the product release remain unfinished; film delivery does not reverse the prior readiness verdict or deployment deferral.

## Documentation refresh — owner review, no commit authorization

Latest user instruction overrides earlier autonomous checkpoint policy: DO NOT COMMIT OR PUSH WITHOUT EXPLICIT PERMISSION. No commit/push/deployment/upload occurred during this refresh; base HEAD is 2da6400. The owner requested mock app/video/deck links and will supply final URLs later. Keep example.com placeholders visibly labeled and project-links.json consistent.

Read docs/README.md and docs/qa/DOCUMENTATION_REFRESH_REPORT.md. English README, Bangla introduction, original cover, event graphic and five actual fictional-case screenshots are ready. Current features/setup/architecture/API/provider/privacy/admin guides replace stale claims; judge guide, pitch story/checklist and legacy benchmark scope were reconciled. Primary-source research and code/documentation audit are in docs/research/. No repository license was selected. Protected blueprint, event brief and plan were unchanged.

Fresh core run passed 184 backend + 27 web tests with 7 backend warnings, exit 0. Documentation check passed 28 documents, 238 relative targets/anchors and 22 API operations. Local GitHub-like marked/Mermaid previews passed desktop/mobile English, Bangla and architecture; sampled images were visually inspected. These are not published GitHub screenshots or a new product readiness sign-off. Check evidence/documentation-*.json and PNGs.

Source review confirmed the ungated one-click judge-admin route grants global admin/reviewer/publisher/operator roles. Documentation restricts it to isolated synthetic evaluation; product code was not changed. Community/merchant seed data and process-local mutations are preview-only; new public posts remain 503. No E5 model inference, universal zero retention or production readiness is claimed.

An unrelated deletion of tracked ClaimCraft_BD_Conference_Demo_Video.mp4 appeared while work was in progress; its cause is unverified and it was not restored or included in this task. Preserve that deletion and the pre-existing untracked video prompt.txt unless the owner directs otherwise. No staging was performed.

Documentation refresh final code/AST graph update PASS: 4,175 nodes, 10,660 edges, 257 communities. No LLM semantic rebuild claimed. All changes remain unstaged and uncommitted for owner review.

## Urgent pitch PDF and final links

Owner supplied https://www.youtube.com/watch?v=FE5Hs5RiUUw and https://ebarki.165.99.219.253.sslip.io/ . English/Bangla README and pitch docs now use those URLs; presentation points to docs/pitch/Ebarki_AIgnite_2026_Pitch_Deck.pdf. Exactly five 16:9 English PDF pages exported, all rendered and visually inspected, clickable app/video/repo links included. Cover logo spacing fixed. PDF verification is pitch-deck-verification.json. HTTP root redirect to /en returned 200; full hosted journey/video playback were not independently accepted. No upload, commit or push. Original no-commit-without-permission instruction still applies.

## Submission story and public repository cleanup — PUSH AUTHORIZED

The latest user explicitly requested GitHub update/push and removal of unnecessary/video-production files. This supersedes the earlier no-commit instruction for the current cleanup. Commit/push are now authorized. Final paste-ready English story: docs/pitch/DEVPOST_PROJECT_STORY.md; field values/tags/links: DEVPOST_FIELDS.md. Four 3:2 product gallery PNGs are in docs/assets/gallery.

61 video-production files and obsolete root MP4 were removed from the Git index, with the local production directory preserved and ignored. Generated documentation preview PNGs and video prompt.txt are ignored. App source, regression fixtures, protected specs, product screenshots, deck PDF and meaningful audit evidence remain. No history rewrite/force push is authorized or performed. Public docs no longer link to excluded production files. Latest docs check PASS: 30 docs, 233 relative links, 22 API operations. Product code is unchanged, so earlier fresh 211-test core result applies; no new full acceptance claim. Remote receipt must be verified and reported after the authorized push.
