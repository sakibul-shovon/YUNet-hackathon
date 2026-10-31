# ClaimCraft BD — Provider Capabilities, Terms & Data Handling Register

Prepared in compliance with plan.md Section 7.1, Section 15.3, and P00.4.

## 1. Primary AI Reasoning & Extraction (Google Gemini)
- **Observed Candidate Model:** `gemini-3.8-flash` (via Google GenAI Python SDK `google-genai`).
- **Backup / Ambiguous Case Candidate:** Documented stronger model (e.g. `gemini-2.5-pro` or equivalent), disabled by default to control cost/latency.
- **Structured Outputs:** Utilizes schema-constrained outputs (`response_schema` with Pydantic) to enforce typed JSON AST without conversational deviation.
- **Terms & Data Handling (Section 7.1 & 15.3):**
  - Paid tier configuration ensures customer data is not used for provider model training.
  - Pilot target: Adult consumers (18+) with affirmative eligibility check.
  - Zero-retention and confidentiality boundaries: Prompts and uploaded attachments are strictly tenant-isolated and scrubbed of raw PII where possible.
  - Fallback: When `GEMINI_API_KEY` is not present, the system defaults to deterministic template-based extraction and rule-based evaluation. It NEVER fakes live provider success.

## 2. Speech-to-Text (STT)
- **Primary Service:** Google Cloud Speech-to-Text V2.
- **Language & Model:** Bengali (`bn-BD`) using `chirp_2` architecture in region `asia-southeast1`.
- **Audio Privacy:** Audio recordings are stored in temporary quarantine, processed to obtain transcripts, and deleted within 24 hours unless explicit retention is chosen by the user.
- **Fallback:** Browser-native Web Speech API or manual keyboard transcription.

## 3. Storage & Evidence Quarantine
- **Architecture:** Multi-tier storage isolation:
  - `quarantine/`: Temporary incoming uploads before virus/MIME validation.
  - `evidence/`: Accepted encrypted evidence documents and verified derivatives.
  - `exports/`: Generated PDF/ZIP complaint artifacts for client download.
  - `policy/`: Immutable public official regulatory documents and release manifests.
- **Security Invariant:** Private evidence objects are scoped to `principal_id` and `case_id`. No public bucket URLs are ever issued for private dispute evidence.

## 4. Vector & Lexical Knowledge Bases
- **Dense Embeddings:** Local `intfloat/multilingual-e5-small` (384-dimension vector, running on CPU/GPU without third-party network exfiltration).
- **Lexical BM25:** `bm25s` persisted release snapshots with custom Bengali Unicode tokenization.
- **Database:** PostgreSQL with `pgvector` extension for approved official statute/regulation chunks.

