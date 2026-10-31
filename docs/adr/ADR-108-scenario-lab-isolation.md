# ADR-108: Scenario Lab and Public Demo Isolation

## Context
Judges, reviewers, and new consumers need to explore ClaimCraft BD using realistic synthetic scenarios without exposing real private dispute records or polluting production data.

## Decision
1. **Isolated Demo Tenants:** Synthetic demo runs execute through the real production pipeline but are flagged with `is_demo = true` and assigned isolated temporary session IDs.
2. **Deterministic Seed Packs:** Eight realistic synthetic dispute scenarios covering shopping, payment gateways, counterfeit medicine, telecom, and airline disputes.
3. **No Cross-Contamination:** Demo data is never indexed into public knowledge bases or mixed with authentic consumer records.

