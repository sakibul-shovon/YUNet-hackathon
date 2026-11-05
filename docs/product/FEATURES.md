# Product capabilities

[Documentation](../README.md) · [Judge walkthrough](../pitch/judge_quickstart.md)

Implementation snapshot: **5 November 2026**. “Implemented” describes a code path; independent test coverage and complete end-to-end acceptance are separate. See [current status](../qa/CURRENT_STATUS.md).

## The consumer journey

| Capability | Current behavior | Important boundary |
| --- | --- | --- |
| Entry and accounts | Guest start, registration/login, owned case list and consumer judge demo | A judge consumer session is distinct from privileged judge-admin evaluation |
| Story intake | English, Bangla or Banglish account; optional context and files | The original account remains user-reported information |
| Language and appearance | English/Bangla UI, light/dark/system preferences | No claim of complete translation or assistive-technology acceptance |
| Agent workspace | Work plan beside a case canvas; processing stages, history and receipts | Model, parser and rule stages are labeled separately |
| Material facts | Review, correction, uncertainty and manual information | Accepted information is a review decision, not independent authentication |
| Evidence story | Payments, messages and promises linked to original sources | Source confirmation controls relevance; reading alone does not prove payment relevance |
| Reconciliation | Compare the recorded amount with explicitly linked receipts | A difference is a request for review, not a fraud finding |
| Possible paths | Reference-backed condition traces and next questions | Rules evaluate recorded facts; they do not issue legal determinations |
| What-if | Preview a changed fact and compare conditions; version-guarded adoption path | A preview stays separate from the saved case until an explicit change |
| Replies | Save a seller message, prepare wording, edit and save the response | AI wording must be checked; no automatic dispatch |
| Documents | Purpose/language selection, source support, saved versions and reviewed export | PDF/HTML/Markdown/ZIP paths exist; not every variant has fresh browser acceptance |
| Filing preparation | Suggested fields, review checkboxes, copying and official-channel links | The user signs in to external services and submits personally |
| Living case | Activity, user-reported external updates and personal follow-ups | A reported outcome is not an independently verified provider resolution |
| Data controls | Consent choices, withdrawal and deletion workflows | Downloaded copies and external-provider retention cannot be revoked by the local app |

## Multimodal evidence

| Input | Processing | What the reviewer sees |
| --- | --- | --- |
| Native PDF | Local extraction and page coordinates | Original page, text and linked passage |
| Image | Consented configured vision model | Original image, proposed text/regions and review needs |
| Scanned / hybrid PDF | Native text plus vision on at most five image-only pages per attempt | Page attribution; partial/unread pages and failure reasons |
| Audio | Consented configured speech model | Original playback, waveform and timestamped transcript |
| Pasted message | Attributed user-supplied source | Message text beside the resulting reply preparation |
| No usable reader | Original retained for inspection; manual input where supported | Explicit unavailable/manual-review state |

Model availability, file quality, page limits and quotas affect results. [Provider behavior and data flow](../engineering/providers.md) describe the actual implementation.

## Community and merchant preview

Community currently has a seeded feed, category filtering, discussions, comments and “Me too” reactions. New public-post creation returns **503**. Comments and reactions mutate process-local data and can be lost on restart. They are not a durable community service.

The merchant module has seeded records and lookup/detail views. Those records are demonstration content, including entries referring to real brands; they are not independently verified allegations, a risk model or operational complaint statistics. The documentation screenshots use a separate fictional dataset. An empty lookup is not a safety recommendation.

Private cases are not automatically published to either surface. A production public dataset requires explicit provenance, consent, moderation and durable storage.

## Administrative experience

The nine panes are **Overview**, **Cases**, **People & access**, **Merchants**, **Moderation**, **Notices**, **Audit trail**, **Source review** and **Knowledge release**.

They expose case-status overrides, role/access changes, merchant review controls, moderation actions, notices, source candidate review/import and knowledge-release operations. Several administrative records and audit receipts are SQL-backed; the public community/merchant preview still has separate process-local foundations. Do not infer full public-data durability from the administrative audit table.

The one-click administrative evaluation entry creates global `admin`, `reviewer`, `publisher` and `operator` roles. It is a deliberate privileged demo path, not a consumer login. There is no environment gate in its current handler. See the [operator guide](../ADMIN_PORTAL_GUIDE.md) before exposing an instance.

## Scenarios and demonstrable scope

Eight isolated synthetic scenarios exist. The flagship phone-order case is the most extensively demonstrated story: payment discrepancy → source review → second receipt → possible path → reply/draft → preparation download.

Other domain packs cover banking/MFS, purchases, services, telecom, insurance and safety-related cases with differing depth. Neither the existence of a scenario nor a configured domain pack proves complete provider execution or qualified procedural review for that domain.

The [system test matrix](../qa/EBARKI_FEATURE_TEST_MATRIX.md) records scoped acceptance. A visible control or selected screenshot does not prove complete functional acceptance.

## Source anchors

| Area | Implementation |
| --- | --- |
| Workspace and source inspection | `apps/web/src/features/agent/AgentWorkspace.tsx`, `EvidenceLens.tsx` |
| Narrative/case views | `apps/web/src/features/workspace/Cases.tsx` |
| Processing and readers | `services/backend/app/operations/runs.py`, `record_reader.py`, `visual_reader.py` |
| Connected records/replies | `services/backend/app/operations/connected_records.py`, `reply_preparation.py` |
| Community/merchant preview | `services/backend/app/community/`, `services/backend/app/merchants/` |
| Administration | `apps/web/src/features/workspace/Admin.tsx`, `services/backend/app/admin/` |

## Next implementation priorities

Gate privileged evaluation access; replace misleading seeded public data before public use; complete durable community/moderation; finish device/keyboard/accessibility acceptance; obtain qualified source review; verify hosted persistence and recovery. These are roadmap items, not completed features.
