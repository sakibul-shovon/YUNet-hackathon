# ADR-103: Orthogonal Fact Model and Assertion Provenance

## Context
AI multimodal extraction (OCR, ASR, vision) is inherently probabilistic and may misinterpret blurry receipts, Bengali handwriting, or spoken dialects. Treating model output as authoritative truth would mislead consumers and compromise legal submissions.

## Decision
1. **Three-Tier Separation:**
   - Raw input & evidence spans (read-only, immutable).
   - Machine proposals with bounded confidence and source coordinates.
   - User-reviewed factual assertions (confirmed, corrected, or marked unknown).
2. **Immutable Snapshots:** Every policy evaluation and drafted artifact binds to an explicit immutable snapshot of reviewed assertions.
3. **Attribution:** Every material fact retains its origin (narrative span, receipt coordinate, voice timestamp, or manual entry).

## Consequences
- High transparency: user has complete veto and correction power.
- Model proposals are never confused with verified statutory facts.

