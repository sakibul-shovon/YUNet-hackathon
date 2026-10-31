# ADR-105: Release and Index Atomicity

## Context
Legal provisions and regulatory procedures change over time. If a user prepares a case while an amendment is being published, vector embeddings, lexical BM25 indexes, and rule ASTs must not become mismatched or corrupted.

## Decision
1. **Immutable Releases:** Legal packs and indexed provisions are compiled into immutable, versioned release manifests with cryptographic checksums.
2. **Version Pinning:** A case is evaluated against an explicit pinned knowledge release ID.
3. **Atomic Pointer Promotion:** New knowledge releases are activated via atomic pointer updates; older versions remain readable for historical case reassessment.

## Consequences
- Guaranteed consistency between retrieved text, citation spans, and policy rules.
- Instant rollback capability without database reindexing downtime.

