# Ebarki

**The next step, made clear.**

A Bangladesh-first consumer resolution copilot that helps people organize dispute evidence, review material facts, understand possible procedural routes, and prepare their next action.

Built by **Sakibul Islam Shovon** for Ostad Presents YUNet AIgnite Buildathon 2026.

## Design review

The new landing page is the first approved implementation milestone. The rest of the application retains its existing design while the landing is reviewed.

- [Complete design and implementation plan](docs/EBARKI_DESIGN_PLAN.md)
- English landing: `http://localhost:3000/en`
- Bangla landing: `http://localhost:3000/bn`
- The interactive landing sample uses fictional browser-local data. It does not run live AI, assess a real dispute, or submit a complaint.

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
- Deterministic three-valued procedural condition evaluation.
- Next-best questions and isolated what-if comparisons.
- Editable preparation materials and official-channel checklists.
- Case activity, follow-ups, and decision changes.
- Merchant intelligence, community experiences, and source administration.

Supported depth differs by domain. Source code includes development adapters and fallback behavior; a library or model label does not establish that the capability has been exercised. Check configuration and real run evidence before making deployment claims. The current export API provides HTML and Markdown; server-generated PDF is a separately planned capability.

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

Historic source specifications are retained for traceability. Application-wide presentation and identifier migration remain outside the landing-review milestone.
