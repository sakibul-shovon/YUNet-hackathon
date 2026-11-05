# ADR-111: Ebarki follow-up integrity boundaries

Status: implemented locally; release/browser/qualified legal approval are separate gates. Date: 5 November 2026.

The follow-up found four concealed failures: administrative state was process-local, issued JWTs outlived logout, runtime schema auto-creation hid missing migrations, and canonical reference data contained an invented legal subsection. Image-only PDFs also lacked a real reading path.

Administrative records and action receipts now persist in SQL tables. Bans revoke sessions and are checked at authentication/login. Role replacement flushes deletions before overlapping inserts, within the same transaction as its audit receipt. Public notices expose active records only; authorized management can edit or disable them. No tamper-proof database claim is made.

New access tokens carry a persisted session ID. Production authentication requires it and checks revocation/expiry. Direct helper-issued sessionless tokens remain a development/testing compatibility path, never a production session substitute. Cookie CSRF uses a session-bound HMAC; browser origin guards cover mutating/session routes. Client roles never authorize a server operation.

Production applies Alembic migrations before startup; it no longer silently creates missing tables. Migrations 0006/0007 cover admin state and earlier omitted users, runs, documents and consent state. Readiness tests real database/storage access. Configured disk storage and explicit legacy-vault compatibility have path bounds. Fresh SQLite/local restart proof does not establish hosted volume durability, PostgreSQL RLS or backup recovery.

Image preparation removes blank margins and keeps an inverse coordinate transform. Scanned/hybrid PDF reading reuses the serialized PDFium renderer, sends at most five image-only pages per attempt after consent and records actual per-page provider acknowledgements. Partial/errors remain visible. Successful version-matched readings may be cached; failed/partial readings are retryable. Provider quotas and model errors require honest unavailable/manual-review states.

Primary Bangla law excerpts are compared to recorded official pages. English and procedure text are unofficial summaries. The nonexistent 45(2), invented refund proviso and unsupported delay/filing-window claims are removed. Actual 76(4) supplies a real hierarchy/qualification regression. The legacy drawer consumes the same backend corpus. Dated link observations expire and unconfirmed destinations retain official-guide fallbacks. Source comparison is not a qualified human review or an official filing receipt.

See [the follow-up evidence report](../qa/EBARKI_STABILIZATION_FOLLOWUP.md) for exact scopes, failures, retries and limitations. Public deployment/final package work is deferred by the user.
