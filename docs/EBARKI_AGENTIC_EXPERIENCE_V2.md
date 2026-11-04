# Ebarki — Agentic Experience V2

Design date: 4 November 2026. Implementation updated: 5 November 2026. The shared workspace and connected feature set are implemented; [implementation details and verified boundaries](EBARKI_CONNECTED_EXPERIENCE.md) take precedence over aspirational capability descriptions in this design specification.

This revision supersedes the quiet case-desk metaphor and feature-first navigation in the previous design direction. The existing product rules, ownership boundaries, evidence relationships, and preparation-only scope remain requirements.

## The decision

Build **a consumer resolution workspace where intelligence is visible through the work it performs**. A person gives Ebarki an outcome. Ebarki proposes a bounded plan, works with their records, asks useful questions, and builds inspectable results. The person can correct, interrupt, redirect, and approve the work.

The experience must communicate five things without a tutorial:

1. It understood my situation.
2. It is doing a useful task for me.
3. I can see what supports its findings.
4. It asks me when information is uncertain.
5. The result is something I can use and control.

English and Bangla use the same interaction model and receive equal design attention. Local familiarity comes from predictable actions, legible content, mobile controls, receipts, references, and clear next steps. Language selection is explicit and remembered. Judge Demo opens an English sample without changing the consumer's saved language preference.

## Why the present composition misses the product

- The navigation mirrors data categories: evidence, facts, paths, actions, activity. The consumer has to operate the workflow manually.
- Agent activity is a subsidiary panel. The dominant visual does not show delegated work.
- A status label says that something ran, but the input, operation, and useful result are visually disconnected.
- Generous whitespace and very small labels make ordinary tasks feel remote and make the interface difficult to read.
- The assistant lives in a drawer, separate from the object the consumer is working on.
- Multiple features receive similar containers even when the underlying interaction should be completely different.

The redesign changes the unit of interaction from a page of records to a task with connected inputs, interventions, and artifacts.

## Art direction: The Evidence Thread

Public expression: **Intelligence you can follow.**

Product promise: **Your story, understood. Your next step, prepared.**

The signature visual is a fine thread connecting a source to a finding, a finding to a condition, and a condition to a prepared action. Its geometry derives from the product's evidence relationships. Threads appear selectively during focus or change; the default workspace stays readable.

Use warm neutral surfaces, charcoal text, clay primary actions, and a dedicated teal signal for agent work. Amber marks an intervention. Red marks a failure or material conflict. Never depend on color alone.

| Purpose | Light | Dark |
| --- | --- | --- |
| Canvas | #F6F5F1 | #141B1E |
| Working surface | #FFFFFF | #20292D |
| Main text | #202B2E | #F3F4ED |
| Secondary text | #58666A | #B2C1C5 |
| Divider | #D4DCD8 | #405056 |
| Primary action | #AE3E2B | #F39A83 |
| Text on primary | #FFFFFF | #241A17 |
| Agent signal | #12665E | #8ADACB |
| Agent surface | #E7F3ED | #203D36 |
| Intervention | #7C4B0A | #F5CF8B |

Typography: Bricolage Grotesque for concise display text, Source Sans 3 for English text, Noto Sans Bengali for Bangla, IBM Plex Mono only for short diagnostic identifiers. English body 16–18px, Bangla body 17–18px, controls 15–16px, secondary task text 14px. Essential information must never rely on 8–12px labels. Use script-specific line heights and natural wrapping rather than fixed text boxes.

Premium craft comes from a consistent optical grid, restrained layers, realistic document surfaces, precise state transitions, strong focus behavior, original product visuals, and reliable interactions. Avoid oversized decorative AI orbs, glass everywhere, endless particle fields, invented confidence scores, and agent headcounts that do not correspond to execution.

## The workspace architecture

### Home: give Ebarki a job

Lead with an outcome composer, not statistics. It accepts a written account, browser-supported dictation, screenshots, and documents. Suggested tasks use real needs: understand an unexplained debit, compare receipts, prepare a refund request, organize an undelivered order.

After submission, show Ebarki's understanding and a short editable plan. Use structured controls for choices and missing facts. Keep a guest start available and explain session continuity at the relevant moment.

Returning users see the next unfinished action and what changed since their last visit. Counts remain secondary. Pending questions and new evidence matter more than total case volume.

### Active case: Workstream + Working Canvas

The main workspace has two linked surfaces. The workstream occupies approximately 38% and the working canvas 62%, within a compact application shell. The actual proportions must be tested at 1024px and 1440px.

The **workstream** contains the goal, current plan, active task, concise explanation, interventions, and controls. It uses task blocks and interactive results rather than a sequence of chat bubbles.

The **working canvas** changes with the task: document inspection, evidence comparison, issue branches, route conditions, what-if comparison, document editing, or change replay. The user can pin an object while Ebarki continues. User selection must not be overridden by automatic navigation.

Cases, records, and history remain directly accessible for experienced users. They are supporting views, not prerequisites for following the guided journey. URLs remain meaningful; opening a direct evidence link must work without replaying an agent animation.

At mobile widths, show the current intervention and relevant canvas in one column. The workstream folds into a compact, labeled activity strip with an expandable history. Essential answers and controls remain available without hover or side-by-side reading.

## Six signature interactions to build exceptionally well

### 1. Watch the case take shape

Input: a story and a receipt. Action: understand and compare. Visible result: proposed names, amounts, and dates appear next to their sources. The document remains an object the user can open and inspect.

The interface should demonstrate how the result was assembled. A newly extracted amount moves from its real source location into the structured comparison. Use real bounding boxes only when available. Text-only extraction uses a text span; missing OCR uses an explicit manual-review state.

### 2. Resolve one meaningful contradiction

The first memorable moment is a disagreement the system notices: a statement of ৳5,500 and a receipt for ৳5,000. Show the two originals, the exact difference, and a useful question. Accepting a second receipt resolves the difference while retaining both sources. Reporting one payment keeps the discrepancy visible instead of correcting the consumer silently.

Each answer changes the canvas and the next step. This is the primary demonstration of useful intelligence.

### 3. Inspect the evidence behind any statement

Working name: **Evidence Lens**. Clicking a supported fact or draft reference focuses the relevant source beside it. The amount, date, or quote is highlighted. The connecting thread identifies the relationship; a simple origin label distinguishes a user statement, extracted proposal, and user-confirmed value.

The same action must work in the review screen, route explanation, draft, and saved history. Closing the inspection restores position and focus. User edits remove inherited support until separately reviewed.

### 4. Try a change before applying it

Working name: **Try a change**. A user changes a material assumption and sees the affected route, missing question, and proposed next action update together. Use side-by-side before/after at desktop and a clear stacked comparison on mobile.

Hypothetical input is visibly separate from saved case information. Applying the change is an explicit action. The view highlights what changed and explains the recorded condition behind it. Do not invent a probability of success or a legal outcome.

### 5. Produce a document that remains inspectable

A draft is a working artifact. Confirmed information connects to its relevant passages. The user can edit a selected section, inspect its support, compare revisions, and download a reviewed copy.

Use true token streaming when the provider delivers it. For fast template generation, show the completed document with a short structural reveal; do not simulate an LLM stream. The final review surface distinguishes preparation from external submission.

### 6. Continue when the story changes

Add a seller reply or receipt. Ebarki summarizes the new information, preserves the original case, identifies changed facts, and reassesses the next step. A concise change replay shows the affected portion, not the entire workflow again.

Example: a seller promises a refund. The workspace records a promise and suggests a personal follow-up. It does not mark the money as received. On return, the next useful question is whether the refund arrived.

This is the second major demo moment: Ebarki supports an ongoing case rather than ending at the first generated answer.

## Feature-specific treatment

| Capability | Primary UI | Meaningful visible behavior |
| --- | --- | --- |
| Narrative understanding | Editable situation summary | Facts emerge with source labels and uncertainty |
| Voice | Recording/dictation state + transcript | Spoken input becomes editable case information |
| Images/PDFs | Private document viewer | Extraction is linked to actual text spans or boxes |
| Reconciliation | Comparison surface | Amounts and dates agree or become interventions |
| Multiple issues | Simple issue branches | Facts attach to the appropriate issue; split and merge stay inspectable |
| Source retrieval | Reference tray + exact source viewer | Relevant provisions and qualifications can be opened |
| Procedural rules | Condition chain | Supported, unsupported, and unknown remain distinguishable |
| Useful questions | Focused intervention | Answer, correct, or leave uncertain, then continue |
| What-if | Before/after workspace | Preview consequences without mutating the case |
| Drafts | Document canvas | Source support, edits, revisions, exports |
| Portal fields | Preparation checklist and field mapping | Copy prepared values and perform official steps separately |
| Activity | Case changes with origin labels | User reports differ from official receipts |
| Reminders | Personal follow-up scheduling | Reminder time is distinct from any statutory caution |
| Merchant information | Search-led research result | Reported records and aggregation method remain inspectable |
| Community | Familiar public experience feed | Sharing is explicit; private case records are not attached |
| Source governance | Review queue + source diff | Discovery, human review, impact, and release changes are visible |

Do not force an AI treatment onto ordinary account settings or public comments. Global identity and task continuity provide consistency; each interaction should have a clear reason.

## Site-wide expression

### Landing

The first viewport contains a precise value proposition, an immediate sample action, and a functional miniature of the workstream and canvas. The signature moment is evidence disagreement and consumer clarification. The visitor controls it.

Continue the narrative through the same objects: scattered inputs → structured understanding → evidence comparison → useful question → supported next step → reviewed artifact → a new reply changes the case. The transition into the actual application reuses the same visual objects and interaction conventions.

Show the official event sticker prominently near the top, including mobile. Keep the judge entry visible. Avoid slow intro sequences that block the first interaction.

### Authentication and judge entry

Consumer login, guest start, Judge Demo, and Admin Login are explicit and legible. Judge Demo creates a separate sample session and opens an English guided case. A judge can take control, change an input, inspect actual execution, and reset their own sample.

Administrative access uses an actual role-checked login. No public frontend contains a privileged account password. If an admin demonstration is desired, use an isolated, restricted demonstration environment.

### Case home

Lead with a current-case briefing: what Ebarki understands, what needs an answer, what changed, and the next useful action. Cases look like ongoing work with meaningful state. Avoid filling the home screen with generic counters.

### Evidence, review, paths, documents

Each direct route opens the same objects used by the agent workspace. A persistent case goal and compact agent state maintain continuity. Manual work remains first-class; an agent must not repeatedly take focus away from the user.

### Merchant research and community

Merchant search uses a clearly scoped research result: available records, dates, recurring allegations, and source limitations. Do not present a guilt score as intelligence. Community retains familiar post and reply behavior, explicit public-sharing review, and privacy separation.

### Sources and administration

Source review deserves a distinctive comparison workflow: original text, candidate change, affected conditions, named review, and release state. Show proposal and publication separately. Administrative dashboards prioritize review queues and required decisions, with actual audit history.

### Settings and help

Retain the same typography and control craft. Provide remembered appearance/language settings and clear data controls. Help should reopen the relevant task or explain the currently selected object. It should not require understanding internal model terminology.

## Agent presence and motion system

Use a small geometric brand-derived mark with consistent states: listening, working, needs input, paused, complete, and failed. Every state has a text label. The mark is subordinate to the useful task and artifact.

| Event | Motion | Duration guidance |
| --- | --- | --- |
| File added | Object joins the input tray | 180–250ms |
| Task starts | Active task gains focus; mark changes state | 150–220ms |
| Fact appears | Source-linked finding enters its position | 220–350ms |
| Evidence focused | Selected source and finding align | 250–400ms |
| User answer accepted | Intervention becomes a recorded answer; next task activates | 180–300ms |
| Result changes | Relevant values and sections transition together | 250–400ms |
| Draft arrives | Structured document is revealed without delaying access | 250–450ms |
| Source inspection closes | Return to the exact previous context | 150–220ms |

Use Motion layout transitions for task and artifact changes. Use GSAP for the landing's controlled narrative sequence. Preserve scroll position, focus, text selection, and keyboard access. Reduced-motion uses instantaneous state changes and static source highlighting. Do not block work to finish an animation.

Avoid fake percentages and invented time remaining. A short operation can finish immediately; the work history still explains what ran. Long tasks expose actual progress, interruption, and retry. Ambient motion remains restrained, and decoration stops when it interferes with reading.

## Technical implications

The new UI needs a stable task/event model. Existing bounded runs can be a starting point, but a list of receipt stages alone does not implement the complete experience.

Proposed events include `run.started`, `plan.updated`, `tool.started`, `tool.completed`, `fact.proposed`, `conflict.detected`, `input.required`, `artifact.updated`, `run.paused`, `run.completed`, and `run.failed`. Include run ID, event ID, sequence, case version, timestamp, task ID, input/output artifact references, and concise public explanation.

Keep long-form private reasoning out of the event stream. Publish task plans, tool summaries, evidence links, uncertainty, and results. Events must reflect actual execution. A deterministic rule check remains labeled as a rule check; a model call is claimed only when a model actually ran. Show specialist agent handoffs only if the backend genuinely implements them.

Render structured, validated UI schemas. The model may propose a question, comparison, or artifact update, but it must not inject arbitrary executable UI. Keep owner checks and consent enforcement on every private object and stream.

On reconnect, resume by sequence without duplicating tasks. New evidence invalidates affected results while retaining historical versions. Background work must be bounded and recoverable; acknowledge interruption at actual checkpoints. Provider unavailability exposes an honest fallback and preserves user input.

## Important edge cases

- No evidence: preserve the person's account and explain which records could help; do not make upload mandatory without a real need.
- Unclear image: permit manual correction and keep extraction uncertain.
- Dictation unavailable: retain typing and upload paths.
- Provider failure: say which task failed and offer a meaningful recovery; never manufacture a transcript or successful extraction.
- Navigation during a run: retain run state and restore the appropriate artifact on return.
- User manually inspects a record: pin their context while the agent works.
- Conflicting edits: explain the newer version and allow safe reload or comparison.
- Interrupted work: completed stages and created artifacts remain distinguishable from unfinished work.
- Source changes: show the affected condition and separate the update proposal from human approval.
- External action: preparation, user-reported submission, official receipt, provider promise, and actual resolution are distinct.

## Judge experience

Suggested demonstration target, subject to real runtime:

1. Immediately understand the consumer problem and see a sample entry.
2. Start an isolated English sample.
3. See source-linked information and a meaningful discrepancy.
4. Answer the question and watch the relevant result change.
5. Inspect the source behind a prepared statement.
6. Try one hypothetical change without altering the original case.
7. Add a reply and see the next step update.
8. Download the reviewed preparation material.

Keep a transparent replay fallback for presentation connectivity problems. It must be visibly a recorded demonstration. The main path remains a real, functional application.

## Build priorities

1. Correct readability, consumer/admin/judge entry, and session isolation.
2. Build the task/event contract and one complete story-to-artifact vertical slice.
3. Perfect contradiction resolution and source inspection as signature interactions.
4. Add change preview and living-case reassessment.
5. Apply the same objects and interaction rules to every supporting route.
6. Connect the landing's interactive moment to the real sample workflow.
7. Complete visual, bilingual, mobile, keyboard, reduced-motion, failure, and reconnect QA.

Do not divide effort equally across decorative effects. The highest-value work is the relation between a user's goal, the agent's current task, the evidence, and the artifact.

## Acceptance criteria

- In either language, a new user can identify the product's purpose, the next action, and the agent's current work without opening help.
- Within the case, users can tell what the system found, what they confirmed, and what is unresolved.
- A supported statement opens its real evidence or source, and closing it restores context.
- Changing a material input produces a visible, explainable change in the affected result.
- Every task result and animation corresponds to a real event or clearly labeled demonstration state.
- Starting, interrupting, reloading, and resuming do not duplicate private operations.
- The complete core journey works at 360px without horizontal overflow; desktop views remain readable at 1024px and 1440px.
- English and Bangla are tested independently, including long labels, dates, amounts, and exported documents.
- Controls have visible focus, adequate contrast, and practical touch targets; zoom and reduced motion preserve all functionality.
- Five representative users can explain what Ebarki helped them do after completing the core journey. Observation, rather than visual preference alone, determines the next iteration.

## References and specific lessons

- [Claude artifacts](https://support.anthropic.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them): put a substantial working result beside the interaction, retaining editable versions.
- [Cursor review](https://docs.cursor.com/en/agent/review): make generated changes inspectable and controllable.
- [Cursor checkpoints](https://docs.cursor.com/en/agent/chat/checkpoints): preserve meaningful previous states.
- [Anthropic's agent-autonomy research](https://www.anthropic.com/research/measuring-agent-autonomy): provide trustworthy visibility and simple intervention.
- [bKash](https://www.bkash.com/app) and [myGov](https://www.mygov.bd/faq-list): draw on recognizable task entry and service progress conventions; do not copy their visual skins.
- [a2i accessibility work](https://a2i.gov.bd/pages/static-pages/6922dea5933eb65569e1c4c2): validate local usability and accessibility with representative users.

The interactive concept at `docs/design/previews/ebarki-agent-workspace-concept.html` demonstrates a workstream and canvas, alternative answers, statement support, and a new reply. It uses fictional data, local interaction, and a clearly labeled simulated review. It does not call a model or modify case records.
