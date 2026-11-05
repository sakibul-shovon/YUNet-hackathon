# Privacy, safety and review boundaries

[Documentation](README.md) · [Providers](engineering/providers.md) · [Current status](qa/CURRENT_STATUS.md)

Ebarki supports consumer preparation. It does not establish fault, authenticate evidence, provide a guaranteed legal conclusion, send a seller message or submit an official complaint.

## Private case data

Cases, facts, records, runs and drafts use application-level ownership checks. Original files are served through authorized case operations. Public references and community/merchant preview stores are separate from private case records.

Administrative operations have broader roles. In particular, the current one-click judge-admin launcher deliberately grants global privileges and has no environment gate. It must remain in an isolated synthetic evaluation environment until restricted for general deployment. Do not put real consumer records in a publicly accessible demonstration instance with that path enabled.

Sessions use server-checked persisted state, revocation and cookie/origin/CSRF protections in the implemented flow. These controls have scoped local tests; they are not a hosted security certification. PostgreSQL/RLS, backup recovery, hosted volume durability and a full security review remain unverified.

## External processing

Applicable consent gates external AI work. Depending on the operation, the app may send a case narrative/context, image or rendered scanned page, recording, or seller-message context to the configured provider. Local native-PDF parsing and deterministic comparisons do not themselves require a model call.

Use only records the consumer is entitled to process. Avoid uploading banking passwords, PINs, OTPs, full card secrets or unnecessary identity information. The local implementation does not establish universal automatic PII removal or provider zero retention. See [the provider/data register](engineering/providers.md).

## Human review is part of the product

An extracted amount can be wrong. A source can be irrelevant. A date can be uncertain. Model wording can reverse the speaker's intent. The user should inspect originals, confirm source links, correct information and review any prepared text before use.

References and rule traces help explain a possible route. Primary-text comparisons do not replace qualified legal review. The app does not promise admissibility, compensation, successful filing or a particular outcome.

## Public preview data

Community and merchant stores contain seeded examples, some referencing real brands. They must not be presented as independently verified allegations, real recovered-money metrics or a statistical risk model. Community comments/reactions are process-local, and new post creation is disabled. A production public-sharing service needs reviewed provenance, durable moderation, consent and abuse controls.

Documentation screenshots use a separate fictional evaluation dataset. No private case is automatically published by running a case workflow.

## Deletion and retention

Consent withdrawal and deletion workflows exist. Evidence deletion includes cleanup of related derived readings/source-bearing saved documents in the implemented path. Deletion cannot revoke a copy already downloaded or prove deletion by an external provider. No automatic 24-hour purge or universal encryption-at-rest guarantee is claimed.

## Reporting concerns

Follow [SECURITY.md](../SECURITY.md) for a potential vulnerability. For an inaccurate model reading or procedural text, keep a minimal synthetic reproducer, the operation/method, and a sanitized receipt. Do not post a real consumer's identifiers, evidence, cookies or credentials in a public issue.
