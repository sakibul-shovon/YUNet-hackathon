# Ebarki administration guide

The visible administrator entry is `/en/admin/login` or `/bn/admin/login`. Server-side role checks protect administrative APIs. Consumer and judge sessions must receive 403 for administrative resources.

There are no documented default administrator credentials. Provisioning requires explicit server configuration through `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD`; keep values in ignored server configuration, never in this guide, client code, screenshots or commits. Do not grant roles merely to make a release audit pass.

Administration includes case/user management and knowledge-source candidate/review/release operations. Source release approval requires a real authorized review record. Creating or importing a candidate is not approval of current law. Role-sensitive operations and source workflows have regression coverage; a full privileged browser acceptance test was not completed in the final audit.

Case counts and recorded disputed amounts come from stored data. Recovered payment totals, uptime, OCR readiness and route distributions are not invented. Merchant/public-community data currently starts empty. Public community publishing is unavailable pending durable storage/moderation.

Administrative bans, notices, merchant overrides and action receipts are now database-backed. Suspensions revoke sessions and block login; unbanning requires a new login. Authorized administrators can edit/disable notices, while public responses contain active notices only. Role and status inputs are validated. Content hashes on audit receipts do not establish tamper-proof storage against database administrators.

Apply the schema before production startup with `python scripts/tasks.py backend run alembic upgrade head`. The current head is `0007_workspace_persistence`. Production startup refuses missing runtime tables/columns, and readiness probes the database and configured local vault. Set `LOCAL_STORAGE_DIR` to the intended durable volume; a local path alone does not prove that a hosted volume survives replacement. Fresh SQLite migrations and a real local production-mode restart were tested. PostgreSQL/RLS, backups and hosted storage remain unverified. Existing databases without migration history require schema inventory and a controlled baseline; do not blindly stamp or downgrade them.

Use the [stabilization follow-up](qa/EBARKI_STABILIZATION_FOLLOWUP.md), [issue ledger](qa/EBARKI_ISSUE_LEDGER.md) and [feature matrix](qa/EBARKI_FEATURE_TEST_MATRIX.md) for tested boundaries. Public deployment and final submission packaging are deferred by the user. This guide makes no claim of complete browser acceptance or qualified statutory sign-off.
