# Ebarki release audit integrity decisions

Date: 5 November 2026. Accepted within the requested release-stabilization scope.

The independent audit found private cases in an unauthenticated merchant search, fabricated public merchant/community records, automatic receipt relevance assumptions, and legacy media adapters returning invented observations. These violate the existing owner-isolation and integrity requirements.

- Merchant endpoints expose an empty reviewed-public-data state. They never query private cases. A future public dataset needs explicit sharing consent, provenance and moderation. No schema/database migration is necessary for this removal.
- Community publishing/reactions/comments return 503 until durable storage and moderation exist. Public seed stories and testimonials are removed. The UI explicitly describes the unavailable capability.
- Every case, including historic fixed demo IDs, requires its owner. Judge/scenario launchers create separate owned workspaces.
- Reading a PDF never establishes payment relevance. Explicit source confirmation or a manual link is required. Excluding/reopening a timeline finding removes its ledger contribution.
- Legacy audio compatibility accepts only an explicitly provided transcript. It returns no invented word times or confidence; without a transcript it returns 503 and directs users to the actual workspace reader. `AudioTranscriptOut.overall_confidence` is nullable and adds `method`/`model_executed`. Copilot responses add an optional provider acknowledgement receipt. Contracts are regenerated. Existing consumers can continue reading the original fields.
- The image-layout compatibility endpoint reports image-color inspection only, with no invented roles, boxes, amounts or model disagreement. Actual vision uses the consent-scoped record reader.
- Provider acknowledgements record provider, model, response status and request ID when provided. They contain no credentials. Cached readings retain their original receipt and identify the reused run in data and UI.
- Evidence deletion purges attached transcripts, quotes and source-bearing saved document versions. Privacy deletion is an explicit exception to immutable version retention; unrelated versions remain. Downloaded copies cannot be revoked. The changes use existing tables and require no migration.
- Production startup rejects the published development signing keys. Local development remains supported; production deployment configuration still needs independent verification.
- Preparation template v2 preserves consumer allegations and requests without automatically asserting fault, missed deadlines, non-receipt of refunds or legal refund entitlements. Superseded templates cannot be exported as current. The additive `template_version` field is in regenerated contracts; saved JSON content needs no database-column migration.
- PDF Bengali paragraphs use the full [Noto Sans Bengali font from Google Fonts](https://github.com/google/fonts/tree/main/ofl/notosansbengali), instantiated at normal width/weight, with its OFL license retained. The old script-only subset lacked punctuation; mixing shaping-font fragments also caused incorrect glyph mapping. The complete paragraph now uses one font with coverage for both scripts and punctuation.

Historical tests expecting invented transcripts, proportional timestamps or synthetic VLM findings are replaced with explicit manual-input and truthful-unavailable assertions, plus separate genuine-provider evidence. No failing test is skipped.
