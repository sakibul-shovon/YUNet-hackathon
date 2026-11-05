# Submission owner checklist

[README](../../README.md) · [Judge guide](judge_quickstart.md) · [Submission copy](devpost_submission.md)

Checked against the [official event](https://yunet-aignite26.devpost.com/) and [rules](https://yunet-aignite26.devpost.com/rules) on **5 November 2026**. General hackathon advice is supplementary; this event's requirements control the submission.

## Submission links

| Material | Draft URL | Current state |
| --- | --- | --- |
| Hosted application | <https://ebarki.165.99.219.253.sslip.io/> | Root redirects to `/en`, HTTP 200; full deployed journey not retested |
| YouTube demo | <https://www.youtube.com/watch?v=FE5Hs5RiUUw> | User-supplied public link; playback not independently verified |
| Presentation deck | [Five-slide PDF](Ebarki_AIgnite_2026_Pitch_Deck.pdf) | Exported 16:9 PDF; five pages rendered and visually inspected |
| Source repository | [GitHub](https://github.com/sakibul-shovon/YUNet-hackathon) | Existing project repository |

The machine-readable [link register](project-links.json) records the supplied URLs and verification scope. The former placeholders have been replaced. Test the app/video signed out and upload the PDF through the official submission platform.

## Event-specific essentials

- [ ] Confirm individual student eligibility and registration with the organizer.
- [ ] Supply a functional publicly accessible B2C application with meaningful AI use.
- [ ] Display the organizer-provided buildathon sticker near the top of the app; README branding alone does not fulfill the app requirement.
- [x] Prepare the required presentation, no more than five slides. PDF export is ready; submission/upload remains the owner's action.
- [ ] If including the recommended video, provide an English public YouTube demo.
- [ ] Complete the official submission flow; a repository link is supporting material, not a substitute for submitting.

The source brief and current page conflict on deadline time: the header displays **22:00 +06**, while the rules body displays **23:59 Bangladesh time**, both on 5 November. Obtain organizer clarification and use the platform's actual closing behavior; this document does not resolve that discrepancy. The overview also gives a final-round date while the rules body retains “to be announced.”

## Technical handoff before sharing

- [x] Replace the app/video placeholders and attach the exported deck locally.
- [ ] Verify complete app/video access anonymously and upload the deck.
- [ ] Verify the deployed consumer Judge Demo creates the intended isolated fictional case.
- [ ] Keep privileged judge-admin access in an isolated synthetic environment; gate/remove it for general consumer use.
- [ ] Confirm actual provider configuration, consent and quota behavior in that deployment.
- [ ] Verify migrations, storage persistence, origins, cookies and restart behavior on the actual host.
- [ ] Replace/review public merchant/community seed content so it cannot be mistaken for verified allegations.
- [ ] Check English/Bangla rendering, core keyboard use, phone layout and error recovery.
- [ ] Keep remaining limitations consistent with [current status](../qa/CURRENT_STATUS.md).

## Evidence and ownership

- [ ] Identify Sakibul Islam Shovon as the solo builder; confirm any institution/biography before adding it.
- [ ] Describe hackathon improvements using source history; do not invent a daily work log or customer testimonials.
- [ ] Disclose AI tools, third-party code/assets and synthetic demonstration data appropriately.
- [ ] Confirm the exact organizer sticker file. Current asset provenance is [documented](../assets/README.md), not independently certified.
- [ ] Decide the repository-wide software license separately; no license is selected by this documentation refresh.
- [ ] Review the complete film's voice pronunciation, pacing and caption timing before public upload.

This checklist is deliberately unfinished. It does not assert that the entry has been submitted or accepted.
