# Ebarki backend

FastAPI/Pydantic application with SQLAlchemy persistence. Internal package identifiers retain `claimcraft` for compatibility.

[Local setup](../../docs/engineering/LOCAL_DEVELOPMENT.md) · [Architecture](../../docs/engineering/ARCHITECTURE.md) · [API](../../docs/engineering/API_REFERENCE.md) · [AI/data methods](../../docs/engineering/providers.md)

## Modules

| Module | Responsibility |
| --- | --- |
| `core`, `identity` | Configuration, database, ownership, sessions, roles and consent |
| `cases`, `facts` | Original account, case versions, assertions, normalization and review |
| `evidence` | Accepted records, local parsing, source metadata and private access |
| `operations` | Stage receipts, summaries, multimodal reading, connected evidence and replies |
| `retrieval`, `policy` | Active lexical/exact reference lookup and explicit condition evaluation |
| `actions` | Preparation documents, exports, field maps and saved document versions |
| `activity` | Case updates and personal follow-ups |
| `knowledge`, `admin` | Source/release operations, access changes, notices and audit records |
| `community`, `merchants` | Seeded public preview; durability/provenance limitations apply |

The current workspace does not run pretrained E5 inference: its run selects lexical/exact retrieval and disables the legacy dense path. Provider keys and consent gate applicable model work; configuration is not proof of execution.

Use the root task runner for commands. `python scripts/tasks.py backend run alembic upgrade head` applies migrations to a configured fresh database. Existing databases need controlled migration history. Read the setup guide before changing them.

The privileged judge-admin evaluation entry is not environment-gated. Keep evaluation synthetic and isolated. [Current status](../../docs/qa/CURRENT_STATUS.md) and [security reporting](../../SECURITY.md) describe the remaining boundaries.

