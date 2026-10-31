# ClaimCraft BD Backend Service

FastAPI modular application powering ClaimCraft BD.

## Modules:
- `core`: Shared value types, settings, security primitives.
- `identity`: Principals, web sessions, actor roles.
- `cases`: Case aggregates, lifecycle, versioning, snapshots.
- `evidence`: File upload quarantine, accepted evidence, span tracking.
- `extraction`: Multimodal extraction adapters (text, OCR, VLM, STT).
- `facts`: Factual assertions, user review records, conflict resolution.
- `knowledge`: Official corpus, provisions, approvals, release manifests.
- `retrieval`: Dense (E5) + lexical (BM25s) hybrid search with RRF.
- `policy`: Deterministic AST evaluation, rule engine, counterfactuals.
- `actions`: Next Best Question (NBQ), action graphs, portal field mappings.
- `artifacts`: Complaint document AST, templating, PDF export.
- `activity`: Case timeline, living case updates, decision diffs.
- `operations`: Outbox dispatcher, job leases, telemetry, deletion sweep.
