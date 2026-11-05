## Inspiration

**You paid. The order never arrived. Your proof is scattered across receipts, screenshots and messages.**

Saving those records is only the beginning. A consumer still needs to explain what happened, reconcile conflicting details and prepare a sensible next step.

I built **Ebarki (এ বার কি?)** around that moment of uncertainty. It is a Bangladesh-first consumer resolution copilot that helps people turn the records they already have into preparation they can inspect, correct and use - in English or Bangla.

## What it does

Ebarki brings the consumer's account, original evidence and possible next steps into one connected workspace.

The demonstration starts with a small but important discrepancy: the consumer reports paying **BDT 5,500**, while the first receipt shows **BDT 5,000**. Ebarki exposes the **BDT 500 difference**. The consumer can inspect the source, review the second payment and see the linked receipts explain the total - without silently rewriting the original account.

That workflow continues beyond the receipt:

- **Read the records:** inspect native PDFs, consented image/scanned-page readings and audio transcripts beside the original.
- **Review what matters:** confirm a finding, correct a date or leave information uncertain.
- **Explore the next step:** inspect procedural conditions and compare a what-if change before applying it.
- **Prepare a response:** review an AI-assisted seller reply or an editable document, then download preparation materials.
- **Continue in your language:** switch between English and Bangla within the same case.

A community preview adds shared experiences and discussions. A separate administrative console exposes case/access controls, notices, source review, knowledge-release controls and audit records. Community/merchant records are seeded demonstrations; new public posts remain disabled.

## How I built it

The interface uses **Next.js, React, TypeScript and next-intl**. A same-origin proxy connects it to a **FastAPI/Pydantic** backend with **SQLAlchemy**, case persistence and a private evidence vault.

Configured **Groq** models assist with situation summaries, image reading, speech transcription, contextual explanations and reply wording after applicable consent. Native PDF parsing, linked-payment comparisons, lexical reference retrieval and **true / false / unknown** conditions remain explicit processing stages.

The workspace records what actually ran, the method used and which outputs need review. Case/document version checks help prevent a stale result from silently overwriting newer information. I used AI-assisted development, while relying on actual tests, application behavior and provider receipts to check implementation claims.

## Challenges I worked through

The difficult part was keeping a useful connection between a confident-looking answer and the record behind it.

Reading an amount does not establish that the receipt belongs in the payment total. A model-generated sentence can misstate a speaker's intent. A changed fact can make an earlier draft stale. Ebarki therefore separates proposed readings, consumer review and procedural conditions instead of treating every generated result as settled truth.

Bangla text, scanned documents and mixed-language records added practical challenges. The implementation keeps originals available, bounds scanned-page processing and exposes unavailable/partial results when a provider or quota prevents completion.

## Accomplishments I am proud of

- A complete demonstration connects a real application interaction to a visible change: **the missing BDT 500 is explained by a reviewed second receipt**.
- Multimodal reading leads back to the original source instead of ending at a detached summary.
- English and Bangla share the same case workflow.
- Local verification passed **211 automated tests: 184 backend and 27 web tests**, with seven backend warnings retained.
- Administrative changes and actual processing calls have inspectable receipts.

These are implementation results on synthetic evaluation cases, not claims about real recovered funds or legal success.

## What I learned

The most important design lesson was to preserve the distinction between **what the consumer said, what a reader proposed and what the consumer confirmed**. That distinction makes uncertainty useful: it tells the person what to check next.

Ebarki became stronger when review, source inspection and recovery from incomplete processing became part of the main workflow.

## What's next

The next phase is a consented pilot with qualified procedural review, broader Bangla/device testing, stronger deployment safeguards and durable community moderation. Privileged evaluation access must be restricted before general consumer use.

Ebarki prepares and explains. It does not send notices, submit government complaints, authenticate evidence or guarantee a refund. The consumer keeps the final say.

**The next step, made clear.**
