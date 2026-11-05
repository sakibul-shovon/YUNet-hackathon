# Ebarki documentation

**Current implementation reference · 5 November 2026**

Start with the [project README](../README.md). This index separates evaluation, practical instructions, technical reference and design history.

## Choose a reading path

| Your goal | Read |
| --- | --- |
| Understand the product in one minute | [README](../README.md) · [বাংলা](../README.bn.md) |
| Fill in Devpost | [Ready-to-paste story](pitch/DEVPOST_PROJECT_STORY.md) · [Field-by-field values](pitch/DEVPOST_FIELDS.md) |
| Evaluate a working flow | [Judge walkthrough](pitch/judge_quickstart.md) |
| Understand current features | [Feature guide](product/FEATURES.md) |
| Run the project | [Local development](engineering/LOCAL_DEVELOPMENT.md) |
| Inspect the engineering | [Architecture](engineering/ARCHITECTURE.md) · [API](engineering/API_REFERENCE.md) |
| Understand AI and external processing | [Provider register](engineering/providers.md) |
| Operate the evaluation system | [Administration](ADMIN_PORTAL_GUIDE.md) |
| Check evidence and limitations | [Current status](qa/CURRENT_STATUS.md) · [Privacy and safety](PRIVACY_AND_SAFETY.md) |
| Prepare the hackathon entry | [Submission checklist](pitch/SUBMISSION_CHECKLIST.md) · [Submission story](pitch/devpost_submission.md) · [Five-slide content](pitch/deck_slides.md) |
| Present the product | [Demo guide](pitch/demo_script.md) · [Public demo](https://www.youtube.com/watch?v=FE5Hs5RiUUw) |
| Contribute | [Contribution guide](../CONTRIBUTING.md) · [Security reporting](../SECURITY.md) |

## Engineering reference

- [Observed dependency versions](engineering/versions.md)
- [Generated OpenAPI](../packages/contracts/openapi.json) and [TypeScript contracts](../packages/contracts/src/generated.ts)
- [Architecture decisions](adr/ADR-111-ebarki-sessions-admin-media-and-reference-integrity.md): session revocation, administration, scanned documents and source integrity
- [Earlier integrity decision](adr/ADR-110-ebarki-release-audit-integrity.md): historical context, including behavior later changed by the seeded preview
- [Code knowledge graph](../graphify-out/GRAPH_REPORT.md): navigation aid, not execution evidence

## Evidence chronology

The [independent audit](qa/EBARKI_FINAL_SYSTEM_AUDIT.md), [stabilization follow-up](qa/EBARKI_STABILIZATION_FOLLOWUP.md) and later recorded product demonstrations describe different checkpoints. Read [current status](qa/CURRENT_STATUS.md) for reconciliation. An older result saying “empty merchant data” or “no privileged browser capture” does not describe every later change.

Keep original failure/retry evidence. A later successful call does not erase a quota failure, and a source-code change does not retrospectively turn an old browser check into a pass.

## Plans and historical material

[Product blueprint](ClaimCraft_BD_Master_Product_Blueprint_v4.1_Knowledge_AI_Engineering.md), [execution plan](../plan.md), [design plan](EBARKI_DESIGN_PLAN.md), [agentic direction](EBARKI_AGENTIC_EXPERIENCE_V2.md) and the [original event brief](hacakthon%20details.txt) retain design intent and history. They are not feature-completion certificates. The public product name is **Ebarki**; compatibility identifiers still use **ClaimCraft BD**.

## Documentation research and maintenance

- [Research and recommended strategy, বাংলা](research/DOCUMENTATION_RESEARCH_2026-11-05.bn.md)
- [Code/documentation audit](research/CODEBASE_DOCUMENTATION_AUDIT_2026-11-05.md)
- [Asset provenance and credits](assets/README.md)
- [Documentation verification and preview images](qa/DOCUMENTATION_REFRESH_REPORT.md)

Maintain implementation claims with a source file, a dated test/receipt or an explicitly labeled limitation. Update the feature guide and current status when behavior changes. The app/video URLs are now supplied and the five-slide PDF is exported; test final access and complete submission separately.

Run the local documentation check through the task runner:

```sh
python scripts/tasks.py backend run python ../../scripts/check_docs.py
```

It checks current relative links/anchors, filename case, SVG syntax, representative API routes and declared placeholders. It does not certify external URL availability or product readiness.
