# Current evaluation status

[Documentation](../README.md) · [Feature guide](../product/FEATURES.md) · [Submission checklist](../pitch/SUBMISSION_CHECKLIST.md)

Snapshot: **5 November 2026**. Ebarki is a working local hackathon evaluation build. The earlier independent release verdict remains **NOT READY** until its remaining gates and subsequent findings are resolved. Documentation polish does not change that verdict.

Submission-link update: the builder supplied the [live app](https://ebarki.165.99.219.253.sslip.io/) and [YouTube demo](https://www.youtube.com/watch?v=FE5Hs5RiUUw). The app root redirects to `/en` and returns HTTP 200. The [five-slide PDF](../pitch/Ebarki_AIgnite_2026_Pitch_Deck.pdf) has been exported. This does not certify a complete deployed journey or video playback.

## Evidence by scope

| Scope | Recorded result | Evidence / interpretation |
| --- | --- | --- |
| Automated core | Fresh refresh run: 184 backend + 27 web tests PASS; 7 backend warnings | [Actual command output](evidence/documentation-core-2026-11-05.txt); not a blanket acceptance score |
| Foundation | Recorded PASS: lint, key parity, build/typecheck | [Follow-up summary](evidence/followup-validation-summary.json) |
| Local production-mode | 22 PASS | [Restart/session/admin evidence](evidence/followup-production-mode.json); SQLite/local vault scope |
| Fresh migration parity | Recorded PASS | [Schema evidence](evidence/followup-migration-schema.json) |
| External AI | Genuine summary, image, speech, reply and scan calls | [Connected receipts](connected-ai-live-2026-11-05.json) and [follow-up](EBARKI_STABILIZATION_FOLLOWUP.md) |
| Fresh OCR | Initial 2 PASS / 3 quota BLOCKED; paced retry 3 PASS | Five distinct fixtures eventually executed; failures retained; not an accuracy population benchmark |
| Official links | Recorded 8 PASS / 3 BLOCKED | [Link observations](evidence/followup-official-links.json); dated observation, not permanent availability |
| Browser capture | Later local consumer, media, community and admin interactions captured | [Public recorded demo](https://www.youtube.com/watch?v=FE5Hs5RiUUw) and [product screenshots](../assets/README.md); selected states do not establish complete browser acceptance |

For the original independent checks, see [audit](EBARKI_FINAL_SYSTEM_AUDIT.md), [feature matrix](EBARKI_FEATURE_TEST_MATRIX.md) and [issue ledger](EBARKI_ISSUE_LEDGER.md). They retain historical failures and should not be silently rewritten as if every later check existed then.

## Changes since the earlier audit

- The agent workstream/canvas now connects records, source review, payment comparison, reply preparation and filing handoff.
- Sessions, bans, administrative records/notices and action receipts gained database-backed paths; missing migrations were addressed.
- Bangla image and bounded scanned/hybrid-PDF reading have actual provider evidence.
- Consumer Judge Demo and privileged Judge Admin evaluation are now separate entries.
- Community/merchant seed data and process-local comment/reaction behavior were reintroduced. Older statements that every public operation is unavailable or starts empty are no longer current.
- The film exercised actual browser interactions that were unavailable in the earlier audit. Its sampled/captured paths do not close all browser acceptance gaps.

## Remaining work

| Priority | Gap | What would close it |
| --- | --- | --- |
| Before a general consumer deployment | Ungated one-click global judge-admin grant | Restrict/remove the route, isolate synthetic evaluation and test authorization in the deployed topology |
| Before public-data claims | Seed records are not reviewed allegations/risk evidence; process-local stores | Reviewed provenance/labels, consent, durable storage and moderation/abuse acceptance |
| Before submission handoff | App/video URLs supplied, five-slide PDF exported; full access/submission remains to be checked | Test app/video anonymously and upload the PDF to the official submission |
| Before readiness claim | Comprehensive browser, device, keyboard and assistive-technology acceptance incomplete | Recorded journeys on supported browsers/devices with failures resolved |
| Before procedural sign-off | Qualified legal/source review unverified | Authorized qualified review of the actual corpus, summaries, conditions and preparation outputs |
| Before hosted durability claim | PostgreSQL/RLS, volume replacement and backups unverified | Deployment-specific isolation, restart and restore tests |
| Before strong AI quality claim | Quotas, Bangla/code-switch variability and wording errors remain | Broader representative ground truth, measured error analysis and review/recovery checks |

## How to interpret a pass

A test pass validates its assertion and environment. A route existing does not prove its UX. A successful provider response does not prove correct extraction. A recorded model ID does not prove a deployed embedding model. A source comparison is not a legal approval. A video frame can show a control without proving every mutation behind it.

No real-user adoption, recovered funds, legal success rate, uptime SLA or universal security/accessibility guarantee is reported.

## Reproduce checks

```sh
python scripts/tasks.py doctor
python scripts/tasks.py check --scope foundation
python scripts/tasks.py check --scope core
```

Use synthetic records. [Setup](../engineering/LOCAL_DEVELOPMENT.md) explains environment selection and side effects. Documentation-only link/render checks are recorded in the [refresh validation report](DOCUMENTATION_REFRESH_REPORT.md); they do not change product readiness.
