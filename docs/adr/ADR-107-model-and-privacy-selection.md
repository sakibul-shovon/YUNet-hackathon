# ADR-107: Model Selection, Privacy and Zero-Training Boundaries

## Context
Handling consumer receipts, transaction logs, and dispute narratives involves personally identifiable information (PII). Cloud AI services must uphold strict non-retention agreements.

## Decision
1. **Primary Model:** Google Gemini (`gemini-3.8-flash`) via the Google GenAI Python SDK.
2. **Paid API Guarantee:** Only paid tier endpoints are utilized in production to prevent user inputs from being retained or used for foundation model fine-tuning.
3. **Structured Outputs:** All LLM extraction calls use strict JSON schema parameters (`response_schema`).
4. **Synthetic Fallback:** In development/testing environments without API keys, deterministic mocks and synthetic datasets are used.

## Consequences
- Data protection compliance under emerging personal data regulations.
- Bounded token spend and low latency.
