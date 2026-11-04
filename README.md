# Ebarki

**The next step, made clear.**

A Bangladesh-first consumer resolution copilot that helps people organize dispute evidence, review material facts, understand possible procedural routes, and prepare their next action.

Built by **Sakibul Islam Shovon** for Ostad Presents YUNet AIgnite Buildathon 2026.

## Agent workspace

Ebarki now uses a shared English/Bangla agent workspace. A live workstream shows executed tasks beside a case canvas for records, facts, possible next steps, what-if comparisons, saved drafts, and activity.

- [Complete design and implementation plan](docs/EBARKI_DESIGN_PLAN.md)
- [Agentic Experience V2 direction](docs/EBARKI_AGENTIC_EXPERIENCE_V2.md)
- [Connected AI features, implementation, privacy and live verification](docs/EBARKI_CONNECTED_EXPERIENCE.md)
- English landing: `http://localhost:3000/en`
- Bangla landing: `http://localhost:3000/bn`
- The interactive landing sample uses fictional browser-local data. It does not run live AI, assess a real dispute, or submit a complaint.
- **Judge Demo** on the landing and login pages opens a fresh, isolated English workspace with actual fictional PDF receipts. Add the second sample receipt to reconcile the 500 taka difference, inspect linked sources, then prepare a saved draft.
- Consumer login: `/en/login`. Administrative login: `/en/admin/login`. Administrative permissions are enforced by the API. To provision a new administrator, set `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD` on the server before its first login. Credentials are never supplied by the new login UI.

## Run locally

Prerequisites: Python, Node.js, pnpm, and uv. Use the repository task runner for cross-platform commands.

```sh
python scripts/tasks.py bootstrap
python scripts/tasks.py dev
```

To run only the frontend for landing-page review:

```sh
python scripts/tasks.py web dev
```

The frontend serves port 3000. The API serves port 8000. Set provider credentials and storage configuration through local environment files; never commit secrets.

## Product capabilities

- English/Bangla interfaces and English, Bangla, or Banglish narrative intake.
- Optional evidence and voice workflows, subject to actual configured processing capabilities.
- Material-fact review, source attribution, and conflict reconciliation.
- Connected evidence story with original-source highlights, image reading, timestamped audio transcripts, and persisted human review.
- Seller reply preparation with editable model wording and clear review requirements.
- Guided filing handoff with prepared fields and a reviewed, version-checked PDF.
- Deterministic three-valued procedural condition evaluation.
- Next-best questions and isolated what-if comparisons.
- Editable preparation materials and official-channel checklists.
- Case activity, follow-ups, and decision changes.
- Source administration. Merchant research has an honest empty public-data state; public community sharing is currently unavailable pending durable storage and moderation.

Supported depth differs by domain. The workspace uses real persisted operation receipts and native PDF extraction, linked-payment comparisons, reference retrieval, and procedural checks. Optional Groq situation summaries require a configured key and explicit case consent; without them, the original account is shown. Images remain available for manual inspection when no real text reader is available. Historical development adapters elsewhere in the repository are not evidence of deployed model inference. Saved bilingual documents can be exported as PDF, HTML, Markdown, or an evidence ZIP. Downloading does not submit them.

## Architecture

```text
Next.js / React / TypeScript / next-intl
                ↓ same-origin API proxy
FastAPI / Pydantic / SQLAlchemy
                ↓
Identity · Cases · Evidence · Facts · Retrieval · Policy · Actions
                ↓
Owner-scoped persistence and evidence storage
```

The landing uses a scoped design system, self-hosted fonts, custom SVG/CSS illustrations, GSAP, and Motion for React. Both themes and reduced-motion behavior are included.

## Verification

```sh
python scripts/tasks.py status
python scripts/tasks.py doctor
python scripts/tasks.py check --scope foundation
python scripts/tasks.py check --scope core
python scripts/tasks.py contracts
python scripts/tasks.py graphify query "How does evidence connect to an assessment?"
```

Foundation checks use `.next-check`, separate from the active `.next` development directory. The generated build directory is ignored.

## Boundaries

Ebarki helps prepare and explain. It does not guarantee a refund, establish guilt, authenticate a screenshot, or claim government affiliation. Preparing or downloading material does not submit it. Users review facts and complete external actions themselves.

Private case records must remain isolated by owner and separate from public reference material. Never request banking passwords, PINs, OTPs, or card secrets.

## Repository map

- `apps/web`: frontend and landing feature.
- `services/backend`: domain services and API.
- `packages/contracts`: generated API contracts.
- `docs/EBARKI_DESIGN_PLAN.md`: approved direction and roadmap.
- `docs/COMPLETE_SYSTEM_MANUAL.md`: historical engineering reference; verify capability claims against source.
- `.agent`: task state and implementation handoff.
- `scripts/tasks.py`: development and verification entry point.

Historic source specifications and internal compatibility identifiers are retained for traceability. The current interface uses the Ebarki name and shared light/dark design tokens.

The independent [final system audit](docs/qa/EBARKI_FINAL_SYSTEM_AUDIT.md) supersedes historical readiness claims. The release verdict is **NOT READY** until the documented deployment, browser acceptance, and source-review gaps are closed. Provider acknowledgements verify actual calls, not output correctness. Complaint templates express the consumer's account and request; they do not establish fault or legal entitlement.
