# AI providers, methods and data handling

[Documentation](../README.md) · [Architecture](ARCHITECTURE.md) · [Privacy](../PRIVACY_AND_SAFETY.md)

Snapshot: **5 November 2026**. Model identifiers below are configuration defaults and observed local methods. They are not a claim of availability for every provider account or deployment.

## Current workspace methods

| Purpose | Method / configuration | Runtime boundary |
| --- | --- | --- |
| Situation summary, contextual assistance and reply wording | Groq; `GROQ_MODEL=openai/gpt-oss-120b` | Server key, applicable case consent, actual request and review |
| Image/scanned-page reading | Groq; `GROQ_VISION_MODEL=qwen/qwen3.8-27b` | Proposed text/regions; original coordinates approximated after image preparation |
| Speech transcription | Groq; `GROQ_TRANSCRIBE_MODEL=whisper-large-v3` | Recording, transcript/segments and original playback; human checking required |
| Optional alternate visual reader | `GEMINI_API_KEY` plus `GEMINI_RECORD_READER_MODEL` | Optional branch; not the observed primary reader in this evaluation |
| Native PDF | Local parser and page-coordinate extraction | No model inference claim |
| References | BM25/lexical retrieval plus exact lookup | Active workspace sets `dense_enabled=False` |
| Facts, payment comparison and conditions | Deterministic extraction/normalization, source links and explicit rules | These stages are not all LLM calls |

Source: `app/core/config.py`, `app/operations/understanding.py`, `record_reader.py`, `visual_reader.py`, `reply_preparation.py`, `runs.py` and `app/copilot/service.py` under `services/backend/`.

## What is sent outside the application

| Operation | Potential payload |
| --- | --- |
| Summary / assistance | Narrative and bounded relevant case context |
| Reply | Seller message and relevant buyer/case information |
| Vision | Prepared image or rendered image-only PDF page |
| Speech | Recording bytes and transcription parameters |

No API key belongs in browser code. A user must review the information they permit the system to process. Local source inspection does not prove that every future integration follows the same bounds.

## Reader limits and failure behavior

- Native PDF output is bounded; the current reader retains at most 240 grouped source lines and an 18,000-character text excerpt.
- Vision processes at most **five image-only pages per PDF attempt**. Hybrid PDFs preserve native text separately; unread pages/partial results remain visible.
- Image preparation maps proposed coordinates back to the original. A highlight is an approximate reading aid, not evidence authentication.
- Missing consent/key, unreadable input, provider errors and quotas return explicit review/unavailable/partial states. Failed or partial readings can be retried.
- Cached readings retain the original method/provider receipt and reuse provenance. A cached result is not a fresh inference request.
- The original account or manual inspection is available where supported. No reader should invent text from a filename.

## Execution evidence

[Connected-AI receipts](../qa/connected-ai-live-2026-11-05.json), [follow-up OCR/retry evidence](../qa/EBARKI_STABILIZATION_FOLLOWUP.md) record actual fictional runs. Successful content checks and real quota failures coexist.

A provider acknowledgement records a method/model and request/response details where available. It proves execution, not accuracy, legal correctness, a paid plan or a retention setting. `doctor` checks configuration only.

## Integrations that must not be overclaimed

Google Cloud STT settings and historical Gemini references exist; they are not evidence that the observed speech path used Google STT. The legacy `E5EmbeddingAdapter` generates deterministic hashed vectors rather than pretrained E5 inference. The active workspace uses lexical/exact retrieval. Redis/Celery/Supabase-related example settings do not establish deployed services.

## Retention and terms

This repository does not establish a provider contract, paid tier, training opt-out or zero-retention setting. Verify the configured account and applicable terms before processing real consumer data. The local filesystem backend is not proof of encryption at rest or an automatic 24-hour audio purge. Consent withdrawal cannot revoke data already dispatched outside the application.

## Development assistance

AI coding/documentation assistance was used during the project. Commits and execution receipts distinguish implementation from claims; no hand-written-only claim is made. A complete per-tool generation ledger is not available.
