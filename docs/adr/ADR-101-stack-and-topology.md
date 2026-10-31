# ADR-101: System Stack, Topology and Ownership Boundaries

## Context
ClaimCraft BD requires a resilient, accessible, and high-performance architecture capable of handling bilingual consumer dispute intake, multimodal extraction, deterministic policy evaluation, and complaint drafting.

## Decision
We select a modular monolithic topology:
1. **Frontend / BFF:** Next.js 15 App Router with strict TypeScript, Tailwind CSS, and `next-intl`. The Next.js server serves as a constrained Backend-For-Frontend (BFF), managing secure HTTP-only session cookies and same-origin API proxying.
2. **Backend Engine:** Python 3.12+ with FastAPI, Pydantic v2, and SQLAlchemy 2.
3. **Database & Storage:** PostgreSQL with pgvector for official legal provision embeddings; private storage buckets for file quarantine and accepted evidence.
4. **Task Execution:** Async worker queues (Celery + Redis) with a transactional outbox in PostgreSQL.

## Consequences
- Single canonical OpenAPI contract bridges web and backend.
- Minimizes distributed system complexity (no Kafka, Neo4j, or unneeded microservices).
- Strict separation between the browser, BFF, API services, and asynchronous workers.

## Replacement Conditions
If worker throughput requires specialized scaling, individual queues can be deployed as independent worker groups without altering core service interfaces.
