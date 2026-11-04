# Ebarki - Agent Handoff

Updated: 5 November 2026. This is an implementation checkpoint, not a final submission-readiness certification.

## Current implementation

The bilingual agent workspace, visible consumer/admin/judge entry points, persisted run receipts, source inspection, and connected landing walkthrough are implemented. New connected features include evidence chronology, genuine image/audio readers, review persistence, what-if comparison, editable seller replies, and guided filing handoff.

Implementation and verified boundaries: docs/EBARKI_CONNECTED_EXPERIENCE.md.
Design specification: docs/EBARKI_AGENTIC_EXPERIENCE_V2.md.
Live-provider evidence: docs/qa/connected-ai-live-2026-11-05.json.

## Verification completed

- Foundation: i18n parity, backend Ruff, Next.js production build/typecheck passed.
- Core: 155 tests passed, 7 warnings.
- Contracts regenerated.
- Graphify incremental update completed: 3,734 nodes and 9,525 edges at the checkpoint.
- 18 live checks passed through the actual Next.js BFF using fictional records. These include English/Bangla summaries, copilot and reply wording, real image OCR and audio transcription, source-linked review, the 500 taka discrepancy, what-if, bilingual PDF export, and filing handoff.
- Fixtures include a genuine bilingual receipt PDF/PNG and playable synthetic speech WAV. Legacy blank/corrupt fixtures were not used as live inference proof.

## Remaining validation

Fresh browser visual QA for the connected screens could not be completed: Windows Computer Use could not determine the active Chrome URL confidently and stopped. Do not claim this check passed. Earlier browser observations do not replace a fresh full-system audit.

The user requested an independent final-system audit prompt, which has been supplied. That audit has not yet been executed. Physical mid-range device performance, Bangla microphone input, optional Gemini production inference, and government portal submission are not verified. Ebarki does not submit complaints automatically.

Keep P21.1 in progress until the remaining visual and acceptance review is completed. Do not mark the whole release ready based on the build alone.

## Local configuration

Provider keys live only in ignored server environment configuration. Never print or commit them. The tested Groq models are openai/gpt-oss-120b, qwen/qwen3.8-27b, and whisper-large-v3. Case-specific external-processing consent is required for user records.

Use python scripts/tasks.py dev --no-reload for stable Windows provider QA. No credentials belong in this handoff. Administrator bootstrap requires explicit server configuration; no default password is documented or provided by the UI.

## Git checkpoint

The user explicitly requested pushing all work completed so far to origin/main. Include the current related account-screen edits without overwriting them. Exclude local environment files, logs, duplicate local reports, build output, and generated graph backup snapshots. Keep the canonical graph outputs and the documented QA report.

Follow AGENTS.md, the graph-first protocol, and the task runner. Preserve the hash-protected source specifications. Next step after this checkpoint is the independent audit, including real browser checks, truthful issue tracking, and retesting any fixes.
