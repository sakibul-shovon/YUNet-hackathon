# Ebarki administration guide

The visible administrator entry is `/en/admin/login` or `/bn/admin/login`. Server-side role checks protect administrative APIs. Consumer and judge sessions must receive 403 for administrative resources.

There are no documented default administrator credentials. Provisioning requires explicit server configuration through `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD`; keep values in ignored server configuration, never in this guide, client code, screenshots or commits. Do not grant roles merely to make a release audit pass.

Administration includes case/user management and knowledge-source candidate/review/release operations. Source release approval requires a real authorized review record. Creating or importing a candidate is not approval of current law. Role-sensitive operations and source workflows have regression coverage; a full privileged browser acceptance test was not completed in the final audit.

Case counts and recorded disputed amounts come from stored data. Recovered payment totals, uptime, OCR readiness and route distributions are not invented. Merchant/public-community data currently starts empty. Public community publishing is unavailable pending durable storage/moderation.

Administrative alerts, merchant overrides and the audit display include process-local state that can reset when the service restarts. Treat them as runtime controls, not a durable compliance ledger. The current statistics response discloses this limitation. Persistent source governance records and case events are separate database-backed features.

Use the [issue ledger](qa/EBARKI_ISSUE_LEDGER.md) and [feature matrix](qa/EBARKI_FEATURE_TEST_MATRIX.md) for tested boundaries. The current release verdict is **NOT READY**; this guide makes no claim of complete production administration or statutory sign-off.
