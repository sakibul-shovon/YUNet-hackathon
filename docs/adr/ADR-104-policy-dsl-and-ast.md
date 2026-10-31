# ADR-104: Policy AST and Deterministic Three-Valued Evaluator

## Context
Consumer disputes under Bangladeshi laws (such as the Consumer Rights Protection Act, 2009) depend on strict statutory conditions (e.g. 30-day complaint filing window, commercial buyer exclusions, receipt requirements). LLMs cannot be trusted to calculate statutory eligibility or exclusions via free-form text.

## Decision
1. **Typed AST:** Regulatory and procedural rules are encoded in reviewed YAML domain packs and compiled into a typed Abstract Syntax Tree (AST).
2. **Three-Valued Logic:** Conditions evaluate to `TRUE`, `FALSE`, or `UNKNOWN` (Kleene logic).
3. **Deterministic Evaluation:** The evaluation engine calculates route eligibility, exclusions, and Next Best Questions (NBQ) deterministically. The LLM only explains or drafts based on evaluated AST outcomes.

## Consequences
- 100% reproducible decision traces.
- Elimination of hallucinated legal requirements or fabricated statutory deadlines.

