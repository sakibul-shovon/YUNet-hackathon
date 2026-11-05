# Judge walkthrough

**Ebarki — The next step, made clear.**

[Project](../../README.md) · [Features](../product/FEATURES.md) · [Evidence and limitations](../qa/CURRENT_STATUS.md)

## Before you begin

Open the [live application](https://ebarki.165.99.219.253.sslip.io/), or follow [setup](../engineering/LOCAL_DEVELOPMENT.md) for local evaluation at `http://localhost:3000/en`. English is the default; the same application also has a Bangla interface. Use only fictional information. The public root redirected to `/en` and returned HTTP 200 in the link check; a full hosted journey was not rerun in this session.

The landing illustration is browser-local demonstration content. **Judge Demo** opens an actual owned case workspace with fictional PDF records; these are different experiences.

## The three-minute consumer route

| Time | Action | What to look for |
| --- | --- | --- |
| 0:00–0:30 | Choose **Judge Demo** | A fresh consumer workspace; clearly synthetic records; the saved story and first payment differ |
| 0:30–1:10 | Open **Evidence story**, choose a payment/promise and inspect its source | Original record beside the finding; review/uncertainty controls; reading is distinct from confirmation |
| 1:10–1:40 | Add the second sample payment, then return to **Briefing** | Linked receipts explain **BDT 5,500**, resolving a **BDT 500** difference |
| 1:40–2:10 | Open **Try a change** and preview a changed fact | Conditions and possible paths change in a preview; the saved case is separate |
| 2:10–2:40 | Review **Draft**, open **Review & export**, check the information and download | Actual preparation materials; clear not-submitted state |
| 2:40–3:00 | Switch to **বাংলা** | The same case and records remain available with the Bangla UI |

Timing is a suggested route, not a latency benchmark. Provider processing can take longer or be unavailable.

## Inspect AI directly

With configured providers and applicable consent, add a fictional image or audio record. Inspect original text/audio beside the proposed reading and its execution detail. Native PDFs use a local parser; reference lookup and explicit rules are separate from model inference.

For reply preparation, use a fictional seller response, generate wording, then check the speaker, amounts and request before saving your own edit. Real generated wording has required correction during evaluation. There is no automatic send action.

## Community and merchant preview

Open Community, filter a category and inspect a discussion. Comments/reactions operate on process-local seeded records; new post creation is disabled. Merchant lookup uses seeded preview data. Neither surface proves real allegations, verified risk or recovered money. The documentation screenshots use a separate fully fictional public dataset.

## Separate administrative evaluation

On a synthetic-only instance, open `/en/admin/login` and choose **Judge Admin 1-Click**. This deliberately creates a real privileged evaluation session. It is distinct from consumer Judge Demo and is not currently environment-gated.

Inspect the nine panes. For a reversible write demonstration, create a clearly fictional notice, then inspect its action in Audit trail. Source review and release transitions should be inspected without manufacturing an approval. [Full operator guide](../ADMIN_PORTAL_GUIDE.md)

## What would count as a failed evaluation?

- No actual request/receipt behind an AI success claim.
- A source highlight or model output treated as verified truth without review.
- A consumer session obtaining privileged resources without the separate evaluation grant.
- A preview silently replacing the saved case.
- A download being presented as an official submission or a guaranteed refund.

Record the route, operation, sanitized error and synthetic input. A failed provider request should remain visible; do not replace it with invented output.

## Read deeper

[Architecture](../engineering/ARCHITECTURE.md) · [AI/data register](../engineering/providers.md) · [Current status](../qa/CURRENT_STATUS.md)

## Evidence against the event rubric

This is an evidence map, not a predicted score. The organizer's [published criteria](https://yunet-aignite26.devpost.com/rules) do not publish numerical weights.

| Criterion | Evaluate this concrete behavior | Inspect the support |
| --- | --- | --- |
| Problem and user value | A consumer explains a missing order and resolves a BDT 500 evidence discrepancy | Flagship story and linked receipts |
| Solution and innovation | Review a source, trace its contribution and compare a what-if change | [Feature guide](../product/FEATURES.md), connected-records services |
| AI and technical implementation | See an actual reading/wording request and distinguish parser/rule stages | [Provider receipts](../qa/connected-ai-live-2026-11-05.json) |
| UX and product readiness | Complete the review/download route; switch language; inspect failure states | [Current status](../qa/CURRENT_STATUS.md), scoped browser captures |
| Presentation and pitch | Follow one case from scattered evidence to reviewed preparation | [Story](devpost_submission.md), [demo source](demo_script.md) |

The AI evidence entry is the [connected-AI receipt set](../qa/connected-ai-live-2026-11-05.json). No synthetic scenario is claimed as real customer validation.

This guide supersedes the earlier floating-widget, 134-test scorecard, automatic legal dispatch, deadline countdown and zero-hallucination claims. They are not instructions for the current product.
