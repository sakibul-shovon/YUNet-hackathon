# Security reporting and evaluation scope

Ebarki is a hackathon evaluation build. No supported production release, response SLA or bug-bounty program is declared.

## Report a concern

Use GitHub's private **Report a vulnerability** option if it is available on this repository. Its availability has not been verified. If private reporting is unavailable, contact the maintainer through an existing trusted private channel. You may open a public issue asking to arrange private contact, but do not include exploit instructions, consumer data, credentials, cookies or private case identifiers there.

The maintainer is [Sakibul Islam Shovon](https://github.com/sakibul-shovon). This file does not invent an email address or claim a private inbox has been configured.

A useful private report describes the affected component/version, security impact and a minimal synthetic reproducer. Test only instances and data you own or are authorized to evaluate. Avoid accessing other consumers' cases or making administrative changes to a shared environment.

## Known evaluation boundary

The current one-click judge-admin route intentionally issues global administrative roles and is not environment-gated. Use it only on isolated synthetic evaluation instances. It must be restricted or removed before a general consumer deployment. Administrative roles are broader than ordinary case ownership.

Community/merchant content is seeded preview data; some interactions are process-local. Application ownership/session checks and local restart tests do not establish deployed PostgreSQL/RLS, backup recovery or a comprehensive security audit.

[Privacy and data flow](docs/PRIVACY_AND_SAFETY.md) · [Current status](docs/qa/CURRENT_STATUS.md) · [Administrative access](docs/ADMIN_PORTAL_GUIDE.md)
