# Ebarki — Connected AI Experience

Implementation and live-provider verification: 5 November 2026.

## Product decision

Intelligence becomes visible through connected work: **original record → proposed finding → human review → usable preparation**. The case workspace keeps the live workstream beside the object being reviewed. English and Bangla share this interaction model.

The primary canvas contains Briefing, Evidence story, Change preview, Prepare a reply, Draft, and Next steps. Facts, the original evidence vault, Filing handoff, and Activity remain available through More views. Stage receipts can open the relevant canvas. Automatic following stops when the person chooses a view.

## What shipped

| Feature | User experience | Actual behavior |
| --- | --- | --- |
| Evidence story | Select a payment, promise, or message; see its original source beside it | Source-linked candidate chronology from actual record text; explicit dates only; no guessed years or resolved relative dates |
| Source inspection | Highlighted PDF/image regions, original message lines, audio playback and clickable transcript segments | Private PDF page rasterization; native PDF coordinates; model-proposed image boxes; actual speech segment timestamps |
| Human review | Confirm, correct the date, exclude, or reopen a finding | Owner-scoped durable case events; confirmed chronology can ground a new document version |
| Image reading | See extracted lines with an AI-read label and review requirement | Groq vision reads the real image bytes after case consent; unavailable processing leads to manual inspection/transcription |
| Audio workflow | Original audio, decoded waveform, timestamped transcript, editable manual alternative | Groq Whisper reads the actual uploaded recording; browser voice typing is a separate optional speech-service feature |
| Change preview | Current answer versus assumption, route before/after, changed condition traces and references | Existing three-valued policy engine runs on an isolated override; applying requires confirmation and a current version |
| Reply preparation | Seller's message, available case details, missing questions, editable reply paper | Bounded model wording or a clearly identified neutral template; saved versions and edits; never sent automatically |
| Filing handoff | Review fields → take reviewed PDF → open official destination | Per-field copy and review controls; missing information stays visible; case/document/revision guards protect downloads |
| Connected draft | Follow a sentence back to its reviewed record, fact, or reference | Immutable saved document versions; editing a sentence removes its inherited source claim |
| Live workstream | Real stage progress, timings, stop control, history, useful outcomes | Persisted operation receipts and SSE updates with polling recovery; cancellation at durable checkpoints |
| Public demonstration | Three interactive examples for evidence, change effects, and reply preparation | Clearly labeled fictional browser-local illustrations; each opens the corresponding real isolated judge workspace |

The judge route creates an isolated consumer session with fictional PDFs and an attributed fictional conversation. Its consent applies only to those sample records. It does not grant administrator access or consent for a user's other cases. Consumer and administrator access have distinct visible entry points. New administrators require explicit server bootstrap credentials.

## UI and interaction

- Warm light surfaces and separately tuned dark tokens; teal identifies active work, amber identifies a source selection or review need.
- Document paper, a connected event rail, before/after comparisons, and an editable reply each have their own layout. They are not interchangeable feature cards.
- Body copy uses readable sizes and generous line height. New compact metadata is at least 12 px; interactive controls use visible labels and keyboard focus.
- A narrow canvas changes the evidence rail to a horizontal selection path above its source. The original file remains usable independently of successful AI reading.
- Stage changes, source selection, and appearance transitions use short motion to explain state. Reduced-motion preferences suppress nonessential effects. There is no sound or fake activity timer.
- Bangla uses respectful, direct phrasing: “নথি”, “তথ্য মিলিয়ে দেখুন”, “খসড়া”, “কী করতে পারেন”. English receives equal care.
- AI activity describes tools and inspectable outcomes. It does not expose hidden chain-of-thought or invent internal specialist agents.

## Real AI versus deterministic work

| Operation | Implementation | Fallback / limit |
| --- | --- | --- |
| Situation summary | Groq `openai/gpt-oss-120b`, bounded JSON | Original account, explicitly not a model summary |
| Contextual copilot | Same configured text model | Labeled workflow guide; case information requires consent |
| Reply wording | Same configured text model; buyer-to-seller perspective | Reviewable neutral template; no legal determinations or sending |
| Image text and approximate boxes | Groq `qwen/qwen3.8-27b` | Original image plus manual transcript; reading limit 8 MB |
| Uploaded audio transcription | Groq `whisper-large-v3`, actual segment times | Original audio plus manual transcript; 20 MB file limit |
| PDF text and page image | Native parser and PDFium | Open original PDF if a page cannot be rendered; scanned PDFs are not silently treated as readable text |
| Narrative facts | Deterministic pattern proposals | User review required; not advertised as model extraction |
| Chronology | Deterministic classification of source lines | Proposed events; unrecognized context stays in the original source |
| Payment comparison | Normalized integer poisha and linked receipts | A model-read image amount enters the comparison only after human confirmation |
| Reference retrieval | Lexical lookup with exact references | No claim that the development embedding adapter ran an inference model |
| Procedural assessment and what-if | Deterministic three-valued conditions | Unknown information remains unknown; no win percentages |
| Complaint draft and PDF | Source-linked templates and genuine export | Preparation only; no official submission or resolution claim |

Successful readings of the same evidence ID and SHA-256 are reused across runs. This avoids repeated charges and preserves the identity of reviewed quotations. Provenance keeps the original reading method and records the run it was reused from. A file hash identifies the same bytes; it does not authenticate a receipt or certify it for court.

Legacy multimodal adapters elsewhere in the repository are compatibility/development code. They are not the processing path used by this connected workspace, and their presence is not evidence of deployed inference.

## Privacy, versions, and integrity

- Provider credentials stay in server environment configuration. No browser key, token in documentation, or committed `.env` file.
- External processing requires case-specific affirmative consent. Withdrawn processing consent blocks new runs and case copilot dispatch.
- Images and recordings are sent to the configured reader only through the server. Browser voice typing discloses that the browser's speech service may process audio online; saving its text requires user review.
- Private source, reply, preview, and handoff endpoints verify ownership. Responses use private/no-store caching where appropriate.
- Source additions, reviews, fact changes, and evidence removal advance the case version. Stale comparisons and reviewed downloads are rejected instead of silently applying to changed information.
- Evidence deletion removes its stored OCR/transcript readings from run results and hides its derived sources. Historical user document versions and review audit records follow the existing private retention/deletion lifecycle; deleting a file does not secretly rewrite a previously saved document.
- OCR can misread names and digits; image boxes are approximate model proposals. A human confirmation means reviewed by that user, not independent verification.
- No courier interception, predicted compensation, guaranteed refund, fake testimonials, fabricated official receipt, or automatic filing was introduced.

## Implementation map

Frontend: `apps/web/src/features/agent/` contains `EvidenceStory`, `RecordSource`, `SourceComposer`, `ChangePreview`, `ReplyPreparation`, `FilingHandoff`, consent controls, shared types and responsive styles. `AgentWorkspace` connects these canvases to the real run. `ConnectedExperience` provides the public interactive walkthrough.

Backend: `app/operations/connected_records.py`, `record_reader.py`, `page_preview.py`, `reply_preparation.py`, and `workbench_router.py` implement the connected experience. Existing facts, evidence, policy, identity, and document services supply the underlying data and integrity rules. No new database tables are required: source additions, reviews, and replies use the append-only case event stream.

New API paths (under `/v1/cases/{case_id}`):

- `GET /connected-records`
- `POST /connected-records/sources`
- `POST /connected-records/review`
- `GET|POST /reply-preparations`
- `PUT /reply-preparations/{reply_id}`
- `GET /filing-handoff`
- `GET /evidence/{evidence_id}/page-preview?page=1`

The existing export endpoint accepts `document_id`, `expected_case_version`, and `expected_revision`. What-if adoption accepts `expected_version`. Generated OpenAPI and TypeScript contracts include the new API surfaces.

## Setup and verification

Configure the following privately in `services/backend/.env`:

```dotenv
GROQ_API_KEY=<server-only-key>
GROQ_MODEL=openai/gpt-oss-120b
GROQ_VISION_MODEL=qwen/qwen3.8-27b
GROQ_TRANSCRIBE_MODEL=whisper-large-v3
```

An explicitly configured Gemini record reader remains an optional alternative; it was contract-tested with mocked HTTP, not live-tested with a Gemini credential. Model access is account-specific. The previously configured text model was unavailable for the supplied Groq account, so the supported current text model above was selected and verified live.

```sh
python scripts/tasks.py dev --no-reload
# In another terminal, with development services running:
python scripts/tasks.py backend run python ../../scripts/build_live_ai_fixtures.py
python scripts/tasks.py backend run python ../../scripts/verify_live_ai.py
python scripts/tasks.py check --scope foundation
python scripts/tasks.py check --scope core
python scripts/tasks.py contracts
```

`--no-reload` avoids a Windows file-watcher console interruption during extended provider QA. The fixture builder creates a clearly fictional bilingual receipt and, on Windows, a real playable local speech recording. The old blank image and invalid WebM fixtures were not used as proof of OCR or speech recognition.

### Live results

The [live-provider report](qa/connected-ai-live-2026-11-05.json) records successful requests through the actual Next.js BFF, not a direct-only provider test:

- English and Bangla situation summaries, contextual copilot responses, and model reply preparation.
- Real image OCR, including Bangla text, approximate source boxes, and genuine audio transcription with three segments.
- Six actual operation stages, persisted source-linked human review, and the 500 taka difference between a 5,000 taka receipt and a 5,500 taka account.
- Nonmutating what-if comparison, English and Bangla PDF exports, and preparation-only official handoff.

Regression coverage additionally checks owner isolation, current-version guards, source removal, reading reuse, review persistence, integer poisha, missing date context, edited draft attribution, saved replies, and unavailable-provider behavior. These tests isolate provider credentials so routine checks do not consume live API quota.

Live speech verification used an English recording. Bangla text generation and Bangla image text were verified. Bangla microphone recognition, Gemini production inference, government portal submission, deployment credentials, physical mid-range device performance, and external provider uptime are not claimed as tested.

## Suggested judge walkthrough

1. Start Judge Demo in English. The workstream shows actual tasks and the real 500 taka gap.
2. Open Evidence story, select the payment, and inspect the original PDF highlight. Show the attributed sample conversation and review a moment.
3. Add the second sample payment and rerun. The linked total reconciles.
4. Preview a changed fact; inspect the conditions that changed before adopting anything.
5. Paste a seller response. Show the message beside the case information and editable model reply.
6. Open Draft, inspect source attribution, then Filing handoff. Review the prepared fields and download a genuine PDF. Explain that the user completes the official filing.
7. Switch to Bangla or dark mode to show the same complete interaction, not a separate simplified product.

## Sources for provider and destination decisions

- [Groq current models](https://console.groq.com/docs/models), [vision](https://console.groq.com/docs/vision), [reasoning options](https://console.groq.com/docs/reasoning), [speech transcription](https://console.groq.com/docs/speech-to-text).
- [PDFium Python API](https://pypdfium2.readthedocs.io/en/stable/python_api.html): bounded real page rendering with a process-level lock because PDFium is not thread safe.
- [DNCRP complaint portal](https://dncrp.com/): the destination is opened for the user; Ebarki does not operate an account or submit a complaint there.

Provider model availability and official forms can change. Keep configuration and destination guidance reviewable; do not replace a failed integration with simulated success.
