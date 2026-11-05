# Administration and privileged evaluation

[Documentation](README.md) · [Feature guide](product/FEATURES.md) · [Current status](qa/CURRENT_STATUS.md)

## Two different evaluation entries

| Entry | Access |
| --- | --- |
| Consumer **Judge Demo** | Fresh fictional consumer case; no automatic administrative role |
| **Judge Admin 1-Click** on `/en/admin/login` | Fresh privileged evaluation identity with global `admin`, `reviewer`, `publisher`, `operator` roles |

The administrative launcher issues real roles and records `JUDGE_ADMIN_EVALUATION_SESSION_STARTED`. Its current handler has **no environment gate**. Use a separate synthetic-only evaluation instance. Before general public use, restrict or remove this entry and verify the resulting authorization behavior. A UI button being labeled “judge” is not an authorization restriction.

Operator login remains available at `/en/admin/login` or `/bn/admin/login`. Provision a controlled account using server-only `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD` before first login. No shared production password is documented here.

## The nine panes

| Pane | Available surface | What to verify |
| --- | --- | --- |
| Overview | Stored metrics | Distinguish real case data from synthetic seed/example values |
| Cases | Inspect cases and status overrides | Reason, target case and audit receipt |
| People & access | Role changes and suspension/restoration | Server authorization; suspension revokes sessions; restored users log in again |
| Merchants | Seeded records and review overrides | Seed data is not verified merchant intelligence |
| Moderation | Pin/unpin/hide/unhide and report actions | Public preview storage is not a fully durable moderation service |
| Notices | Create, inspect, edit and disable | Correct language/severity, public active state and receipt |
| Audit trail | Operation receipts and record inspection | Actor, action, target and timestamp; content hashes are not tamper-proof storage |
| Source review | Candidates, imports, checks, differences and review decisions | Source provenance, scope, rationale and a real reviewer decision |
| Knowledge release | Build/promote/disable/rollback and impacted-case controls | Correct candidate/release, authorization and version semantics |

Some operations require a reason or confirmation. Inspect the values before confirming. Creating a candidate or building a release is not qualified approval of current law.

## Safe demonstration

1. Open a separate browser session on the isolated evaluation instance.
2. Use Judge Admin 1-Click and inspect the recorded login receipt.
3. Review the panes. Use a clearly fictional notice for a write demonstration.
4. Confirm the notice and locate its creation in Audit trail.
5. Avoid changing real users, real merchant reputations, actual legal approvals or the active source release for a demo.

The recorded demonstration shows all nine panes and a genuine fictional notice/audit action. That does not establish full browser acceptance for every administrative mutation or release transition.

## Persistence and deployment

Administrative records, bans, notices and action receipts have SQL-backed paths. Community comments/reactions and seeded public stores remain process-local. Do not conflate these layers.

For a fresh database, apply `python scripts/tasks.py backend run alembic upgrade head`; current head `0007_workspace_persistence`. Existing unversioned databases need controlled baselining. Configure the local vault path and verify the actual deployment volume, PostgreSQL/RLS, backups, origins, TLS and privileged evaluation gate separately.

[Privacy](PRIVACY_AND_SAFETY.md), [ADR-111](adr/ADR-111-ebarki-sessions-admin-media-and-reference-integrity.md) and [the follow-up report](qa/EBARKI_STABILIZATION_FOLLOWUP.md) record the tested boundaries.
