# GitHub Copilot Instructions — ClaimCraft BD

## Token-Saving Knowledge Graph (graphify)
This project contains an indexed knowledge graph located in `graphify-out/` generated with `graphify`.

When investigating codebase structure, symbol locations, cross-module dependencies, or architectural flows:
1. Prefer querying the graph (`python scripts/tasks.py graphify query "<question>"`) instead of loading or searching multiple entire files into context.
2. Use `python scripts/tasks.py graphify path "<Symbol1>" "<Symbol2>"` to trace call paths.
3. Use `python scripts/tasks.py graphify explain "<symbol>"` for symbol definitions.
4. Open only the specific files and line numbers pinpointed by the graph traversal.

