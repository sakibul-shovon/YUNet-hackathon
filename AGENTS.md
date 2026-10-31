# ClaimCraft BD — Agent Working Guidelines

## Mission & Boundary
ClaimCraft BD is a Bangladesh-first consumer resolution copilot.
- **Goal:** Help consumers understand their rights, organize dispute evidence, assess viable procedural paths, and prepare structured complaints/requests.
- **Integrity Rule:** Never fabricate legal advice, statutory citations, official portal submissions, or provider resolutions.
- **Privacy Rule:** Protect personal consumer data; separate private case memory from public knowledge planes; enforce owner-based tenant isolation.

## Key Developer Commands
Always use the Python task runner `scripts/tasks.py` for consistent cross-platform execution:
```bash
python scripts/tasks.py status                 # Validate task ledger & display progress
python scripts/tasks.py doctor                 # Check local toolchain & provider capabilities
python scripts/tasks.py bootstrap              # Install dependencies (pnpm + uv)
python scripts/tasks.py dev                    # Run local web and API services
python scripts/tasks.py check --scope foundation # Run lint & typecheck
python scripts/tasks.py check --scope core       # Run test suites
python scripts/tasks.py contracts              # Regenerate OpenAPI & TypeScript client
```

## Execution Protocol
1. Consult `.agent/state.json` and `.agent/handoff.md` to identify the active task.
2. Follow `plan.md` specifications and acceptance criteria.
3. Keep changes incremental, modular, and well-tested.
4. After completing each phase (e.g., P00, P01, ...):
   - Ensure all acceptance tests and exit checks pass.
   - Stage relevant files, excluding any secrets or transient build artifacts.
   - Commit with a standard descriptive commit message (`feat(PXX): ...`).
   - Push to the designated GitHub branch and verify remote receipt.
   - Update `.agent/state.json` and `.agent/handoff.md`.
