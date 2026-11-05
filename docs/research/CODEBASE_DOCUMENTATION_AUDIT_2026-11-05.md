# Codebase-to-documentation audit

Snapshot reviewed at Git HEAD `2da6400` on **5 November 2026**, before these uncommitted documentation edits. No application implementation is changed by this refresh.

## Method

Read `.agent/state.json` and handoff, queried the existing 4,081-node knowledge graph, then inspected relevant frontend/backend symbols and current manifests. Compared the README, judge/admin guides, provider register, manual, pitch copy, protected event brief and retained QA evidence. Used package metadata and `doctor` for current toolchain observations. External research is [registered separately](DOCUMENTATION_RESEARCH_2026-11-05.bn.md).

## Findings and resolution

| Finding | Implementation/evidence | Documentation response |
| --- | --- | --- |
| New workstream/canvas features under-described | `AgentWorkspace.tsx`, connected records/reply/workbench services; film captures | Current feature guide, judge route and screenshots |
| Legacy judge guide overclaimed widgets, dispatch and guarantees | Current entry/workspace source and independent audit differ | Replace instructions; show actual controls and boundaries |
| Provider register presented candidate Google paths as primary runtime | `core/config.py`, `operations/record_reader.py`, `understanding.py` | Groq observed path, optional Gemini and non-model methods distinguished |
| E5/“true dense” language did not describe observed inference | `runs.py:264–271` disables dense; `e5_adapter.py` hashes tokens | Explicit active lexical/exact retrieval; no pretrained E5 inference claim |
| Seeded public preview contradicted older empty/unavailable docs | `community/service.py`, `community/router.py`, `merchants/service.py` | Seeded feed/lookup and process-local mutations documented; post creation still 503 |
| Preview records are not verified real-world intelligence | Seed content references real brands and unverified example metrics | Documentation labels and public-data deployment gap; fictional screenshot dataset |
| Judge-admin access is intentionally privileged and ungated | `identity/router.py:90–97`, `identity/service.py:599–651` | Separate consumer/admin entry; synthetic-only deployment boundary |
| Old privacy/provider promises lacked evidence | Local storage/config and retained audit findings | No universal zero retention, encryption-at-rest, purge or tamper-proof claim |
| Toolchain table was stale | Installed metadata: SQLAlchemy 2.1.8, next-intl 3.26.5, TypeScript 5.9.3, Tailwind 3.4.19 | Observed versions separated from constraints and lockfiles |
| Manual repeated superseded architecture and statutory claims | Old manual vs ADR-110/111 and current providers | Replace with maintained task-oriented references; history remains in Git |
| Browser “blocked” status was treated as timeless | Later film captured real local consumer/admin/community interactions | Preserve chronological scope; no claim of comprehensive device/AT acceptance |
| Public URLs absent | Earlier deployment deferral; owner requested mock links in this task | Explicit `example.com` placeholders and central link register |
| Event graphic already available; origin not certified | Existing 2105×747 asset and earlier provenance report | Reuse unchanged, event link, credits and exact-file caveat |
| Repository-wide license absent | Root tree inspection | Do not add a license or license badge without owner choice |

## Source groups inspected

- UI: entry/session routes, workstream/source views, administration and workspace modules.
- API: identity/admin/community routes, reader/run/workbench/reply services, config/database and migration setup.
- Retrieval: active run call, hybrid retriever and deterministic legacy embedding adapter.
- Delivery: task runner commands, root/web/backend manifests, generated OpenAPI, CI and infrastructure scaffolding.
- Evidence: independent audit/follow-up, actual provider receipts, film capture/media/alignment manifests.

## Claims intentionally not added

No verified real-user traction, recovered-funds totals, legal win rate, universal Bangla accuracy, complete accessibility compliance, official affiliation, deployed backup guarantee or production-ready verdict. Test count is not a customer outcome. A source symbol or visible button is not full acceptance.

## Scope and authorization

The owner requested professional documentation, research and placeholder links, and explicitly prohibited commits without permission. Documentation files, fictional visual assets and verification tooling may be edited locally. No commit, push, deployment, upload or message to an organizer is authorized by this refresh.

The original product blueprint, event brief and `plan.md` remain unchanged. The unrelated `video prompt.txt` is preserved.
