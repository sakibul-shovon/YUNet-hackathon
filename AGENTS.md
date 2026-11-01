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
python scripts/tasks.py graphify query "<q>"   # Query codebase knowledge graph to save tokens
python scripts/tasks.py graphify update        # Incremental update knowledge graph
```

## Knowledge Graph & Token-Saving Protocol (graphify)
This project maintains a persistent knowledge graph at `graphify-out/` with AST structural maps, god nodes, community clusters, and cross-file relationships.

**Rules for AI & Coding Agents to Save Context Tokens:**
1. **Always Check the Graph First:**
   - Before executing broad repository grep searches, crawling directories, or reading multiple whole source files to answer codebase questions, consult the knowledge graph:
     - Run `python scripts/tasks.py graphify query "<question>"` (or `graphify query "<question>"`) to fetch a tightly scoped subgraph (~2,000 tokens) covering relevant symbols, lines, and relations.
     - Use `python scripts/tasks.py graphify path "<SymbolA>" "<SymbolB>"` to trace call chains and dependency flows.
     - Use `python scripts/tasks.py graphify explain "<concept>"` to understand focused architectural nodes.
   - Read raw source files **only** for the specific lines/symbols identified by the graph traversal.
2. **Subagents:** Always include this graph-first rule in any delegated subagent prompt that explores code.
3. **Graph Maintenance:**
   - Git post-commit, post-checkout, and post-merge hooks automatically keep the graph up-to-date.
   - When introducing structural or architectural changes, run `python scripts/tasks.py graphify update` to re-extract without LLM cost.
   - `graphify-out/graph.json` diffs in PRs are expected when the graph refreshes.

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

