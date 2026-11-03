# Ebarki — Complete Design and Implementation Plan

**Direction:** The next step, made clear.  
**Research cutoff:** 3 November 2026.  
**Plan saved:** 4 November 2026.  
**Approval:** The design direction is approved. The landing page was reviewed positively. The full application redesign is now authorized, with explicit emphasis on natural Bangla copy.

Ebarki should feel like a beautifully organized case desk: receipts, messages, facts, sources, and actions connected by a visible thread. Its signature moment is watching scattered evidence become a clear next step, with the consumer involved in the decisions.

## 1. Project understanding and hackathon strategy

### Product and audience

Ebarki is a Bangladesh-first consumer resolution copilot for people facing problems with purchases, payments, and service providers. Its core value is reducing the uncertainty between “something went wrong” and “I understand what to do next.”

The main journey is:

**Explain the problem → organize evidence → review facts → understand possible routes → prepare an action → track what changes.**

The strongest features are:

- Multimodal intake: English, Bangla, and Banglish narratives; voice; screenshots; receipts; documents.
- Evidence-linked facts: distinguish what the consumer said, what a document indicates, and what remains uncertain.
- Conflict resolution: expose inconsistent amounts, dates, or transaction details.
- Procedural assessment: evaluate conditions through deterministic three-valued logic: supported, unsupported, or unknown.
- Next-best questions: ask for information that materially changes the next step.
- Action preparation: editable requests, complaint materials, evidence indexes, and official-channel field guidance.
- Living cases: reassess after new evidence or responses, with visible decision changes.
- Merchant intelligence and community: discover reported patterns and share experiences.
- Source governance: inspect references, source health, updates, and administrative review.

Shopping and financial-service disputes lead the public story. Telecom follows the same framework. Insurance has explicitly limited depth; government grievances remain a secondary track. Unknown or unsupported issues retain useful evidence-organization behavior without fabricated guidance.

### Repository understanding

The review covered the task ledger, handoff, specifications, knowledge graph, route inventory, frontend components, API routers, and critical service implementations.

| Layer | Current implementation |
| --- | --- |
| Frontend | Next.js App Router, React, TypeScript, Tailwind |
| Resolved frontend versions at review | Next.js 15.5, React 19, Tailwind 3.4 |
| Localization | English and Bangla through next-intl |
| Backend | FastAPI, Pydantic, async SQLAlchemy |
| Local persistence | SQLite and local evidence storage |
| Browser/API boundary | Same-origin Next.js API proxy |
| Contracts | OpenAPI and generated TypeScript |
| Product surfaces | 21 page entry points, including cases, evidence, paths, actions, activity, community, merchants, sources, and admin |
| Existing styling | Inter/Noto Sans Bengali, green semantic tokens, rounded panels, and scattered hard-coded styles |

The complete redesign replaces the presentation. Domain services, procedural rules, ownership boundaries, evidence relationships, and working API behavior remain the foundation.

The bounded pipeline is authorization/consent → parsing or transcription → structured proposals → reconciliation → human review → source retrieval → deterministic assessment → useful question/action → grounded artifact → validated publication → follow-up and reassessment. Model calls are bounded adapters, not the application's authority.

### Implementation distinctions

Source behavior must take precedence over optimistic documentation:

- Several agent displays contain scripted states.
- Processing receipts include hard-coded durations and provider labels.
- The nominal dense embedding adapter uses deterministic hashing.
- Voice processing contains browser-transcript and synthetic fallback behavior.
- The export endpoint supports Markdown and HTML; a real PDF service is an additional deliverable.
- The API proxy buffers responses, preventing genuine streaming passthrough.
- Collective participation includes local-only success behavior that must not be represented as a saved action.

Relevant source includes `services/backend/app/operations/pipeline_service.py`, `services/backend/app/retrieval/e5_adapter.py`, `services/backend/app/multimodal/audio/stt_adapter.py`, `services/backend/app/actions/router.py`, and `apps/web/src/app/api/v1/[...path]/route.ts`.

“Live,” “verified,” “streaming,” confidence values, and provider badges must reflect actual execution. The doctor check reported Gemini and Google STT configuration unavailable in its environment; it did not establish whether the separate Groq path worked. Live-provider capabilities need a demonstrated run before being advertised.

### Hackathon requirements

The complete supplied `docs/hacakthon details.txt` was read and cross-checked against the [official rules](https://yunet-aignite26.devpost.com/rules). Deadlines are deliberately excluded from this plan.

- Functional, publicly accessible B2C web application addressing a concrete everyday problem.
- Meaningful AI contribution and easy-to-use, accessible product behavior.
- Solo participation and one project. Existing work is eligible with meaningful improvements.
- Official organizer-provided sticker clearly visible near the top, including mobile.
- Mandatory live application and presentation deck of no more than five slides.
- Optional product video; English narration is required if submitted.
- Optional repository; organizers may request source verification.
- Submission through Devpost.
- No specific model, cloud, or sponsor SDK is mandated in the reviewed requirements. Ostad and YUNet are the named event organizations.

| Judging criterion | Ebarki design response |
| --- | --- |
| Problem and user value | One recognizable consumer problem immediately visible |
| Solution and innovation | Evidence conflicts, useful questions, explainable routing, decision changes |
| AI and technical implementation | Inspectable real execution and grounded outputs |
| UX and readiness | Complete mobile journey, clear recovery, bilingual parity |
| Presentation and pitch | Memorable interaction followed by a downloadable result |

No numerical judging weights were published in the reviewed material.

In the first ten seconds, establish the name and purpose, show an understandable receipt discrepancy, and make “Try a sample case” available. The demo arc is problem → conflicting evidence → consumer clarification → explained path → reviewed document → new evidence changes the recommendation.

## 2. Research findings and selected references

The research cutoff is 3 November 2026. Dated 2026 material informs the trend assessment. Undated product pages are references, not proof a pattern originated in 2026. Public previews are not equivalent to testing complete authenticated products.

| Reference | Takeaway to apply, without copying |
| --- | --- |
| [Paper Tiger's 2026 redesign](https://www.papertiger.com/blog-posts/paper-tiger-wins-awwwards-site-of-the-day-for-website-redesign) | Strong typographic identity and memorable composition; give Ebarki one recognizable visual idea |
| [CSSDA November selection](https://www.cssdesignawards.com/sites/polparma-biologics/50326/) | Assess visual design, usability, and innovation independently |
| [FWA](https://thefwa.com/) | Treat interaction as storytelling; concentrate effort on one purposeful demonstration; individual case access was limited |
| [Godly redirect / Recent](https://recent.design/) | Graphic identity, motion, and crafted details applied selectively to product communication |
| [Lapa Ninja](https://www.lapa.ninja/) and [Land-book](https://land-book.com/) | Section rhythm, typography, product-image placement; avoid inheriting a template's structure |
| [Dribbble Vellum concept](https://dribbble.com/shots/27118009-Vellum-AI-Dashboard-Concept) | Visual-density exploration; glass treatments show why attractive concepts still need task-specific judgment |
| [Mobbin](https://mobbin.com/discover/apps/web) | Shipped-product patterns for navigation and recovery; complete authenticated flows were not exposed by public access |
| [Linear for Agents](https://linear.app/agents) | Visible delegated work, human ownership, inspectable review |
| [Cursor](https://cursor.com/) | Realistic product interactions explain work in progress and work ready for review |
| [Raycast](https://www.raycast.com/) | Fast command discovery, keyboard access, concise action language |
| [Claude](https://claude.com/product/overview) and [Stripe](https://stripe.com/) | Explain complex capabilities through concrete tasks and progressively richer examples |

Service-design references:

- [GOV.UK form structure](https://www.gov.uk/service-manual/design/form-structure): focused questions, branching, and asking only for information the service needs. Present one material question at a time.
- [NN/G: Types of AI Explanations, July 2026](https://www.nngroup.com/articles/ai-explanations/): match explanation depth to audience and purpose. Consumers need useful reasons; judges may inspect execution detail.
- [Official consumer complaint portal](https://ccms.dncrp.com/): registration, login, complaint information, and evidence are separate official steps. Ebarki must distinguish preparation from submission.

### Trends to adopt

- Product demonstrations instead of decorative hero artwork.
- AI inside a task workspace, with review queues and artifacts.
- Decision histories and understandable changes.
- Strong typography and restrained brand color.
- Progressive explanations, not permanently expanded technical panels.
- Motion communicating relationships and state changes.

### Trends to avoid

Generic gradient heroes, floating glass panels, infinite marquees, decorative agent swarms, synthetic terminal logs, giant context-free prompt boxes, indistinguishable feature-card grids, and unsupported metrics.

## 3. Art direction: The clear case

### Concept and mood

The metaphor is a case file being assembled. A receipt becomes a fact. A fact connects to a condition. A condition leads to a possible action. A thin annotation thread connects those relationships across landing page and workspace.

Mood: precise, composed, humane, quietly confident. Marketing has editorial asymmetry; task screens remain predictable.

### Palette

| Token | Light | Dark |
| --- | --- | --- |
| Canvas | #F7F6F2 | #151A1D |
| Surface | #FFFFFF | #1E2529 |
| Elevated surface | #EFEEE8 | #283136 |
| Primary text | #20262B | #F4F2EB |
| Secondary text | #56616A | #B4BEC2 |
| Subtle divider | #D8D8D0 | #38454B |
| Control boundary | #7E878D | #7E9098 |
| Brand/action | #B13F2C | #F49278 |
| Brand hover | #8D2F21 | #FFB29A |
| Text on brand | #FFFFFF | #261C17 |
| Reviewed/source signal | #17675E | #8AD1BF |
| Reviewed background | #E5F2ED | #203831 |
| Attention | #85510C | #F3C77F |
| Error | #AC2838 | #FFADB7 |
| Keyboard focus | #2457D6 | #A5C0FF |

Vermilion identifies the primary action and active evidence thread. Teal indicates specific source/review states. Labels and shapes accompany color. Calculated primary-button contrast is 5.81:1 in light and 7.32:1 in dark. Test every final component rather than assuming token selection guarantees conformance.

Dark mode has its own surface hierarchy, softer highlights, and controlled evidence-preview lighting. Printable documents retain readable paper presentation in both themes.

### Typography

- Bricolage Grotesque, 600–700: display and major headings.
- Source Sans 3, 400–600: interface and body.
- IBM Plex Mono, 400–500: execution receipts, labels, and identifiers.
- Noto Sans Bengali: Bangla with optical balancing, appropriate line height, and correct shaping.
- Self-host licensed WOFF2 files with locale-aware loading. Never split Bangla conjuncts into animated letters.

### Logo, icons, and imagery

- Custom Ebarki wordmark and compact folded-file/forward-step symbol.
- Bespoke domain symbols on a 24px grid with consistent strokes and folded-corner details.
- Product visuals composed from actual interface components and explicitly synthetic sample evidence.
- Small vector illustrations for empty states: evidence sleeve, unfinished timeline, document awaiting review.
- Very light grain only on marketing backgrounds.
- No decorative courtroom imagery, gavels, robot heads, or generated human portraits.

## 4. Anti-AI-generated checklist

| Common tell | Ebarki counter-rule |
| --- | --- |
| Purple/blue gradient identity | Flat ink-and-vermilion palette |
| Centered hero plus three cards | Asymmetric headline and interactive case composition |
| Identical rounded containers | Sheets, ledgers, timelines, inspectors, comparison views |
| Emoji or stock-icon identity | Custom domain symbols; familiar utility icons remain secondary |
| Generic transformation copy | Name the input, action, and resulting artifact |
| Default component-library styling | Custom proportions, typography, states, borders, density |
| Glowing agents and terminal theatre | Observable stages, actual tools, timestamps, results |
| Fake testimonials/counters | Real artifacts, measured evaluations, explicit limitations |
| Arbitrary asymmetry | Expressive marketing; stable task workspace |
| Motion everywhere | Animate relationships, progress, meaningful changes |

Copy examples: “Two records show different amounts.” “Was this payment made in two parts?” “See why this path needs another detail.” “Review your complaint draft.” “Prepared. You haven't submitted it yet.”

Cursor behavior is limited to useful zoom, inspect, drag, and resize states. Preserve familiar pointers for normal navigation. Maintain strict alignment and spacing even in asymmetric sections.

## 5. Information architecture and screens

All consumer screens support `/en` and `/bn`; English is the fresh-visit default.

| Area | Screens |
| --- | --- |
| Public | Landing, How it works, Scenario Lab, Technology, Sources, Privacy, Limitations, Help |
| Authentication | Login, Register, guest-to-account upgrade |
| Home | Case dashboard at /cases |
| Intake | /cases/new: story, optional voice/evidence, desired outcome, processing consent |
| Case | Overview, Evidence, Fact Review, Paths, Actions, Activity |
| Merchant intelligence | Merchant Check search/results and merchant inspector |
| Community | Feed, category filters, composer, comments, similar-experience interaction |
| Settings | Appearance/language, account, data/consent/deletion |
| Administration | Overview, cases, merchants, moderation, users, alerts, audit |
| Knowledge administration | Sources, candidate review/diff, releases, operations |
| Shared inspectors | Source excerpt, evidence region, execution run, document history, what-if comparison |

Preserve existing URLs. Make inspector states deep-linkable where authorization allows. Do not add inert password-reset or settings controls without their backend behavior.

Desktop: compact global rail, contextual case navigation, main workspace, optional evidence/assistant inspector. Mobile: single-column flow with a persistent next action; inside a case use Overview, Evidence, Actions, More. Paths and Activity remain accessible.

Primary journey: **start without an account → explain → optionally add evidence → review material facts → answer a useful question → inspect a path → review/export → record a response**. Account creation becomes useful for reliable cross-device access.

## 6. Detailed landing-page plan

### A. Masthead and event identity

- Purpose: establish credibility and navigation immediately.
- Layout: Ebarki wordmark, How it works, Sources, sample entry, language/theme, Start a case.
- Official sticker: dedicated near-top band, correct proportions/colors, visible on mobile. Repository has two asset copies; verify provenance before release.
- Motion: 180–240ms entrance; navigation is immediately usable.

### B. Hero: evidence becomes a next step

- Headline direction: “Turn your evidence into a clear next step.” Short typographic line breaks may adapt the wording without changing the promise.
- Supporting copy: “Ebarki helps you organize a consumer dispute, understand possible routes, and prepare a complaint you can review.”
- Layout: five-column text area beside seven-column product composition; mobile copy/actions first.
- CTAs: Start a case and Try a sample case.
- Visual: narrative excerpt, payment receipt, extracted amount, and annotation thread. A discrepancy opens one understandable question.
- Interaction: add a second sample receipt or correct the amount; the explanation changes.
- Motion: heading-line reveal and 350–500ms evidence assembly, 8–12px movement; initial entrance around 900ms maximum. Synthetic sample clearly labeled.

### C. Problem: scattered records

- Purpose: make the consumer's difficulty recognizable.
- Copy direction: “The receipt is in your gallery. The promise is in a message. The next step is still unclear.”
- Layout: editorial text and three differently proportioned evidence fragments.
- Visual: receipt, chat, delivery update with distinct source labels.
- Motion: fragments align into an index on entry; restrained desktop parallax; straightforward mobile reveal.

### D. Interactive workbench

- Purpose: demonstrate the actual contribution.
- Layout: evidence/input pane, execution sequence, resulting fact sheet.
- Stages: read input → propose facts → flag conflict → request review → compare routes → prepare material.
- Controls: run sample, inspect step, review fact, replay recorded run, start fresh.
- Motion: real completed steps update from responses; validated output appears in blocks. No timed simulation presented as live execution.
- Lightweight illustrative preview first. A real run, when enabled, creates an isolated synthetic case. Landing-only local demonstration must explicitly identify itself as illustrative and must not claim live AI execution.

### E. Paths and next question

- Purpose: explain the decision process.
- Copy direction: “See what supports a path—and what still needs checking.”
- Layout: one prominent next step, expandable explanation, quieter alternatives.
- Visual: condition ledger with supported / needs information / does not apply.
- Interaction: answer a question or explore a labeled what-if branch.
- Motion: changed conditions crossfade; only affected actions receive brief emphasis.

### F. Action Studio

- Purpose: turn understanding into a tangible result.
- Copy: “A complaint draft you can inspect, edit, and use.”
- Layout: document preview and evidence/reference margin.
- Interaction: inspect sentence support, switch language, edit, inspect official-channel checklist, preview export.
- Motion: source-to-document shared elements; sentences appear after validation.

### G. Living case

- Purpose: demonstrate usefulness after the first draft.
- Copy: “New evidence can change the next step.”
- Layout: before/after assessment separated by new response/receipt.
- Visual: specific changes with plain-language explanations.
- Interaction: add a sample event and inspect the diff.
- Motion: 250–350ms comparison; preserve previous versions.

### H. Capability atlas

- Purpose: make the full feature set scannable.
- Editorial index with purposeful miniatures: transcript/number review, receipt region, clarification question, condition ledger, document/checklist, version comparison, merchant report, privacy-previewed community experience.
- Source monitoring and administrative review appear in technology/trust.
- Interaction: selected capability changes adjacent miniature; mobile uses stacked summaries, not a horizontal carousel.

### I. Trust and technology

- Purpose: substantiate product claims.
- Layout: source register, data-handling explanation, expandable execution diagram.
- Distinguish private case data and public references, human review and external submission.
- Technical proof shows exercised capabilities, actual methods, and recorded versions, linked to scenario checkpoints.
- Motion: selected stage only; no perpetual traveling particles.

### J. FAQ

Answer scope, absent receipts, Bangla/voice, file handling, submission boundaries, uncertainty, and deletion. Use an accessible keyboard-operable accordion and detailed policy links.

### K. Final CTA and footer

- Copy: “Start with what you have.”
- Primary start-case action and secondary sample entry.
- Visual: an assembled file with an unfinished next-step marker.
- Footer: product, sources, privacy, limitations, help, genuine builder attribution, appropriate build/repository information.
- Motion: restrained final reveal; no endless marquee.

## 7. Feature-by-feature UI and AI-native behavior

| Feature | Recommended interface |
| --- | --- |
| Text intake | Focused story editor, example prompts, real saved state |
| Voice | Recording/playback, editable transcript, critical-number review |
| Upload | Per-file acceptance, processing, failure, retry |
| Evidence inspection | Document canvas linked to extracted-fact ledger |
| Provenance | You said / Receipt indicates / Reviewed by you |
| Conflicts | Side-by-side values; correct/add evidence/keep uncertain |
| Fact review | Prioritized material amounts, dates, parties, references |
| Multi-issue | Issue outline connecting evidence and possible actions |
| Next-best questions | One question, why it matters, I don't know |
| Routes | Ranked next steps, condition explanations, source access |
| What-if | Separate comparison; explicit application of changes |
| Action planning | Readable dependencies, prerequisites, review state |
| Drafting | Sentence-level support and revision history |
| Filing companion | Copyable fields, missing details, checked official links |
| Export/redaction | Attachment selection, privacy preview, artifact versions |
| Living case | Timeline, before/after diff, superseded labels |
| Reminders | User-set follow-ups distinct from conditional legal cautions |
| Fraud | Protective guidance before ordinary intake |
| Merchants | Search-first report, counts, dates, methodology, limits |
| Community | Experience feed with privacy preview before publishing |
| Collective preparation | Draft/interest state; Joined requires saved participation |
| Monetary information | Actual amounts and documented conditional information; no speculative payout meters |
| Sources | Searchable register, health history, originals, review state |
| Admin | Dense tables and inspectors, separated from consumer navigation |

The workspace coordinates Plan (intended work), Work (evidence/questions/tools/artifacts), and Result (reviewed information/next action). The assistant emits structured components rather than a wall of alternating chat bubbles.

Visible “reasoning” means observable conditions, decisions, and evidence, not private model chain-of-thought. Parallel lanes only represent genuinely concurrent execution. Label models, parsers, rules, and human reviews accurately.

Presence language: active bracket = processing; open marker = needs review; solid marker = completed; amber interruption = missing/degraded capability. Provide Stop during supported runs. Confidence belongs to specific defensible extractions, never a chance-of-winning gauge.

Command palette supports navigation and context-sensitive case actions. Suggestions come from current case state. History and replay identify original run dates, versions, and whether work is recorded or newly executed.

## 8. Design system and component inventory

| Foundation | Specification |
| --- | --- |
| Spacing | 4px base; 8, 12, 16, 24, 32, 48, 64, 96 |
| Grid | 4-column mobile, 8 tablet, 12 desktop |
| Marketing width | Approximately 1280px maximum |
| Workspace | Fluid up to approximately 1560px |
| Body | 16px baseline; larger Bangla where necessary |
| Display | Fluid 40–88px, controlled measures |
| Radius | 6px controls, 12px panels, 18px large workspaces |
| Elevation | Borders first; restrained floating-inspector shadows |
| Timing | 120ms feedback, 220ms transitions, 450ms narrative motion |

Component families:

- Controls: buttons, fields, selectors, tabs, menus, dialogs, tooltips.
- Navigation: public masthead, app rail, case navigation, mobile dock, breadcrumbs.
- Evidence: upload queue, document viewer, region highlights, source chips, conflict comparisons.
- Agent work: plan, execution timeline, review prompt, tool receipt, interruption state.
- Decisions: condition ledger, route summary, comparison, next-action block.
- Artifacts: document editor, citation margin, export preview, history.
- Operations: filter bars, tables, moderation inspector, source diff, audit timeline.

State contracts:

- Hover: restrained movement or boundary change.
- Focus: visible 2px ring with offset.
- Loading: correctly sized skeleton, actual stage when known.
- Empty: explanation and one useful action.
- Error: what failed, what was saved, recovery.
- Partial: retain successes and isolate failed stages.
- Success: precisely identify the completed action.
- Stale: preserve results and explain update/review requirements.

Target [WCAG 2.2 AA](https://www.w3.org/TR/WCAG22/): text and non-text contrast, keyboard operation, focus management, labels, reflow, understandable errors. Aim for 44px targets; support 200% zoom. No hover-only functions. Announce milestones, not every streamed character. Mobile has complete functionality, with inspectors adapted into sheets/full views and stacked evidence comparisons.

## 9. Technical implementation and migration

### Libraries

Keep the existing framework/backend. Add GSAP and @gsap/react for scoped marketing motion; ScrollTrigger for progression; SplitText for accessible line reveals; Flip for evidence assembly. Use Motion for React for drawers, review states, shared elements, and lists. Use Radix accessible primitives with Ebarki styles. The full redesign may use TanStack Query for owner-scoped run/case state, retries, invalidation, and read cancellation.

GSAP and Motion must own separate elements. Use native scrolling in the first release; Lenis adds limited value to this task-oriented interface and complicates nested viewers and keyboard scrolling.

References: [GSAP](https://gsap.com/docs/v3/Plugins/ScrollTrigger/), [Motion](https://motion.dev/docs/react).

### Motion specifications

- Magnetic CTA: fine pointers, maximum 3px visual movement, stable hit target.
- Shared elements: evidence to inspector, fact to source, revision comparison.
- Counters use real evidence/review counts, never invented outcomes.
- Stream actual stage events and validated blocks only.
- Reduced motion uses immediate states/short fades, no pinned storytelling.
- Prefer transform/opacity. Avoid perpetual workspace motion.

### Proposed full-redesign structure

```text
apps/web/src/
  app/[locale]/
    (marketing)/
    (auth)/
    (workspace)/
    (admin)/
  components/
    primitives/
    navigation/
    brand/
  features/
    landing/
    intake/
    cases/
    evidence/
    fact-review/
    paths/
    actions/
    activity/
    assistant/
    merchants/
    community/
    sources/
    settings/
    admin/
  design/
    tokens/
    typography/
    motion/
  lib/
    api/
    query/
    i18n/
```

Route groups preserve public URLs. The landing-only milestone can use an isolated feature module and scoped stylesheet without reorganizing unrelated routes.

### Contract dependencies for full AI-native behavior

- Durable run/stage records with actual timestamps/executors.
- Owner-authorized event streams, reconnect, replay.
- Streaming BFF passthrough.
- Cooperative cancellation; aborting a browser fetch alone is insufficient.
- Structured, authorized assistant case context.
- Validated output blocks and source references.
- Real PDF generation.
- Persisted collective participation before success states.

Keep additions isolated from procedural rules; regenerate contracts with the task runner. Private caches are owner-scoped, cleared on session changes, and not persistently exposed. No private evidence enters public knowledge indexes.

### Performance and accessibility

Server-render content; lazy-load animation/viewers/inspectors. Model-backed samples run only after interaction. Optimize synthetic assets and fonts, pause offscreen work, avoid WebGL. Target 60fps on a mid-range Android device.

Measure p75 LCP ≤2.5s, INP ≤200ms, CLS ≤0.1, split by device class. These are targets, not pre-implementation claims. [Core Web Vitals](https://web.dev/articles/vitals)

### Theme behavior

Light by default. Store light, dark, or system as an explicit preference. Follow system only when the user selects and saves System. Apply the stored value before first paint. Semantic CSS variables drive both independently designed themes. Disable transition at load and under reduced motion.

### Migration

1. Append redesign tasks/acceptance criteria to the ledger.
2. Build brand, tokens, primitives, layouts independently.
3. Extract working API behavior into typed hooks.
4. Completely replace each approved screen composition.
5. Preserve URLs, case data, evidence relationships, authorization.
6. Rebrand UI, metadata, logo, README, active docs, package labels, API descriptions, exports, generated assets to Ebarki as each scope is approved.
7. Migrate preference identifiers without losing choices.
8. Remove obsolete presentation after parity checks.

Use `python scripts/tasks.py check --scope foundation` and `--scope core`; add meaningful browser checks for main journey, isolation, themes, localization, and recovery. Keep dev/production artifacts separate to prevent concurrent build cache corruption. Do not modify immutable source documents merely to satisfy a cosmetic rename.

## 10. Priority roadmap

| Priority | Deliverable | Exit condition |
| --- | --- | --- |
| 1 | Capability truth map and visual specification | Advertised behavior classified, demo checkpoints defined |
| 2 | Identity, fonts, tokens, themes, hero | Distinct first impression across themes/devices |
| 3 | Complete landing and interactive sample | Visitor understands and exercises key interaction |
| 4 | Primary case journey | Intake through activity works end to end |
| 5 | Real execution visibility | Recorded steps, review gates, interruption, recovery, replay |
| 6 | Remaining consumer features | Merchants, community, domain variants, settings, sources |
| 7 | Administration | Operational/knowledge workflows retain parity |
| 8 | Release/demo polish | Accessibility, performance, bilingual exports, five-slide assets, English demo flow |

Each completed phase follows validation, ledger, descriptive commit, push, remote-receipt verification, and handoff protocol. The primary demonstration remains discrepancy → explained route → reviewed artifact → new evidence changes the next step.

### Current authorized landing milestone

- Save this full plan.
- Implement the landing only with Ebarki branding/metadata, custom art direction, responsive layout, bilingual copy, both themes, motion, functional navigation/FAQ/sample interactions.
- Mark the browser-local sample as illustrative, not live AI or an official determination.
- Keep the application redesign pending user review.
- Validate the build and inspect the page visually at desktop/mobile and both themes; record any verification limits.

## 11. Risks and open inputs

| Risk/input | Treatment |
| --- | --- |
| Documentation overstates capability | Gate public claims against exercised behavior |
| Provider configuration | Verify actual models/providers before recording |
| Legal/source approval | Expose reviewed capabilities at documented depth |
| Shared deterministic fixtures | Fresh owner-scoped cases for interactive judge runs |
| Scripted confidence/telemetry | Recorded evidence or explicit illustration labels |
| PDF/Bangla rendering | Real export path and visual inspection |
| Merchant accusations/community privacy | Provenance, moderation, publication preview |
| Collective/payout claims | Preparation utility; gate unsupported outcomes |
| Official sticker | Verify source/provenance of repository asset |
| Existing working-tree changes | Preserve pre-existing deletions and new demo assets |
| Feature breadth | Keep main journey dominant; maintain discoverability |

Remaining release inputs: verified live provider configuration, reviewed domain/source scope, hosting target, and sticker provenance. These do not block the landing's bounded illustrative experience. The full application redesign requires a separate review after this landing milestone.
