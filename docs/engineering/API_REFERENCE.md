# API orientation

[Architecture](ARCHITECTURE.md) · [Setup](LOCAL_DEVELOPMENT.md) · [Generated OpenAPI](../../packages/contracts/openapi.json)

The generated contract is the full machine-readable reference. The current contract contains **148 canonical HTTP operations**, excluding `/api/` compatibility aliases. This page highlights evaluation paths; it is not a second hand-maintained schema.

## Transport and identity

The browser calls same-origin `/api/v1/...`; the Next.js server proxies to the configured API. Backend canonical routes normally start `/v1/...`, with separate `/auth/...` and health routes. Inspect the contract for exact identifiers, request bodies and responses.

Cookie/session authentication, applicable CSRF/origin checks and server-side ownership/roles apply to writes. A client role label does not authorize an operation. Foreign private resources should not become enumerable merely because an identifier is known.

## Representative operations

| Operation | Canonical route | Purpose |
| --- | --- | --- |
| POST | `/auth/guest` | Start a guest session |
| POST | `/auth/judge-demo` | Create a consumer evaluation workspace |
| POST | `/auth/judge-admin-demo` | Create a deliberately privileged evaluation session; isolated synthetic use only |
| GET | `/v1/cases` | List owned cases |
| POST | `/v1/cases` | Save a consumer account/case |
| POST | `/v1/consents` | Record applicable processing consent |
| POST | `/v1/cases/{case_id}/runs` | Start an asynchronous processing run |
| GET | `/v1/cases/{case_id}/runs/{run_id}` | Inspect run state and results |
| GET | `/v1/cases/{case_id}/runs/{run_id}/events` | Observe server-sent run updates |
| POST | `/v1/cases/{case_id}/runs/{run_id}/cancel` | Request cancellation at supported checkpoints |
| GET | `/v1/cases/{case_id}/connected-records` | Retrieve the connected evidence story |
| POST | `/v1/cases/{case_id}/connected-records/review` | Confirm/dismiss/correct a source-linked moment |
| GET | `/v1/cases/{case_id}/evidence/reconciliation` | Compare the recorded amount and linked payments |
| POST | `/v1/cases/{case_id}/reply-preparations` | Save seller input and prepare reply wording |
| PUT | `/v1/cases/{case_id}/reply-preparations/{reply_id}` | Save reviewed wording |
| POST | `/v1/cases/{case_id}/what-if` | Preview condition changes |
| POST | `/v1/cases/{case_id}/what-if/apply` | Apply a permitted, version-matched change |
| GET | `/v1/cases/{case_id}/documents/history` | List saved document versions |
| GET | `/v1/community/posts` | Read the seeded community preview |
| POST | `/v1/community/posts` | Currently returns 503; new public sharing is unavailable |
| GET | `/health/live` | Process liveness |
| GET | `/health/ready` | Configured readiness probes; not product certification |

Uploads, original file access, source previews, facts, documents/exports, activity, reminders, source administration and releases are detailed in the contract. Administrative endpoints enforce their required server roles. The judge-admin launcher itself is a separate ungated evaluation grant, not evidence that consumer administration is safe to expose publicly.

## Concurrency and errors

Connected mutations and current-document operations use expected versions where defined. On a conflict, refetch the case and review the changed data rather than silently replaying stale output. File validation, consent/provider unavailability and inaccessible records have explicit error paths. Handle the response schema/status for the particular route; not every missing dependency is a 500.

Use only synthetic inputs for API evaluation. Keep cookies, JWTs, provider keys and raw consumer evidence out of issue reports and shell output.

## Inspect and regenerate

With the API running, open `http://127.0.0.1:8000/docs` or `/openapi.json`. The repository copies are [OpenAPI](../../packages/contracts/openapi.json) and [generated TypeScript](../../packages/contracts/src/generated.ts).

```sh
python scripts/tasks.py contracts
```

Regeneration writes contract files. Review the diff together with the relevant implementation/schema changes. A generated endpoint listing proves the interface exists, not that every operation passed a fresh browser journey.
