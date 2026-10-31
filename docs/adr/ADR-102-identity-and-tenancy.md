# ADR-102: Identity, Anonymous Sandbox and Tenant Isolation

## Context
Consumers in Bangladesh experiencing retail or service disputes need immediate assistance without cumbersome registration barriers. However, personal dispute details, financial amounts, and receipts must remain strictly private.

## Decision
1. **Anonymous First:** Every new visitor receives an anonymous `principal_id` and secure session token via HTTP-only cookie.
2. **Account Upgrade:** Users can upgrade to a verified account at any time without losing created cases.
3. **Tenant Scoping:** All database queries for private cases, evidence, facts, and drafts enforce `principal_id` and `case_id` ownership checks. Guessed UUIDs yield 404 or 403 without data leakage.

## Consequences
- Frictionless onboarding with robust privacy guarantees.
- Zero cross-tenant data exposure.

## Replacement Conditions
If federated authentication (e.g. Google OAuth or Gov SSO) is integrated, the principal model cleanly binds external identities to the existing `principals` table.
