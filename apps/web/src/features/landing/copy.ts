export const english = {
  nav: { how: 'How it works', toolkit: 'The toolkit', trust: 'Built on trust', login: 'Log in', start: 'Start a case', menu: 'Open navigation', close: 'Close navigation', language: 'বাংলা', theme: 'Switch to dark theme', light: 'Switch to light theme' },
  hero: {
    eyebrow: 'YOUR AI CONSUMER RESOLUTION AGENT',
    line1: 'Your evidence.', line2: 'A clear', line3: 'next step.',
    description: 'Tell Ebarki what happened. Watch it organize your evidence, spot what does not add up, and prepare your next step. Every finding stays open for your review.',
    sample: 'Explore a sample', note: 'Start with what you have. No account needed to begin.',
    marker: 'FROM “WHAT NOW?” TO A WAY FORWARD', event: 'A solo build. An everyday problem worth solving.',
    handwritten: 'A clearer picture, one piece at a time.',
  },
  scene: {
    label: 'THE CASE DESK', sample: 'Interactive sample', title: 'A phone that never arrived.',
    storyLabel: '01 / YOUR SIDE OF THE STORY', story: '“I paid ৳5,500 for a phone. The delivery date passed, and the seller stopped replying.”',
    receipt: 'PAYMENT RECEIPT', receipt2: 'SECOND PAYMENT', merchant: 'Sample Electronics', transaction: 'REFERENCE', ref: 'SAMPLE—001', date: 'SAMPLE DATE', dateValue: '20 October', total: 'AMOUNT PAID',
    source: 'From your receipt', reported: 'You reported', documented: 'Receipts show', mismatch: 'There’s a ৳500 difference.', match: 'The two payments explain the total.',
    question: 'Was this paid in two parts?', add: 'Add the second receipt', added: 'Second receipt added', reset: 'Reset sample',
    review: 'Ready for your review', reviewNote: 'You stay in control of the facts.', warning: 'One detail needs your review',
    caption: 'Fictional details. A browser-local illustration, not a live AI run.',
  },
  strip: ['YOUR STORY, IN YOUR LANGUAGE', 'YOUR RECORDS, KEPT TOGETHER', 'YOUR NEXT STEP, EXPLAINED'],
  problem: {
    eyebrow: 'THE HARD PART IS KNOWING WHERE TO START', title: 'You have a problem.\nYou shouldn’t need a playbook.',
    description: 'The receipt is in your gallery. The promise is in a message. Getting them into a clear, useful case shouldn’t be another struggle.',
    parts: [
      { title: 'Bring the scattered pieces.', text: 'A voice note, a screenshot, a receipt—or just your side of the story.', label: '01 / START WITH WHAT YOU HAVE' },
      { title: 'See the important details.', text: 'Review what the records show. Spot gaps before they become assumptions.', label: '02 / MAKE SENSE OF IT' },
      { title: 'Take an informed next step.', text: 'Understand a possible route and prepare a request you can review.', label: '03 / MOVE FORWARD' },
    ],
  },
  demo: {
    eyebrow: 'OPEN THE CASE FILE', title: 'Less guesswork.\nMore “I know what to do.”', description: 'Follow one sample from a messy story to an organized next step. Click a stage to look closer.',
    tag: 'ILLUSTRATIVE WALKTHROUGH', steps: ['Tell the story', 'Review the facts', 'Explore a path', 'Prepare an action'],
    stage: 'STAGE', of: 'OF', inspector: 'CASE NOTES', next: 'Next stage', restart: 'Back to the story',
    titles: ['Start in your own words.', 'Every detail has a source.', 'Understand the route, not just the result.', 'A draft that stays yours.'],
    descriptions: [
      'You don’t need the perfect wording. Explain what happened and what you would like to happen next.',
      'The story and receipt disagree. Adding the second payment explains the difference without erasing either record.',
      'Separate the issue with the seller from the service used to pay. A payment method alone doesn’t establish a provider failure.',
      'Use the reviewed facts to prepare a factual request. Check the details before copying, downloading, or using an official channel.',
    ],
    narrative: 'YOUR ACCOUNT', issue: 'Phone not delivered', desired: 'Desired outcome', refund: 'Request a refund', inputs: 'Sample inputs', inputsValue: 'A story + payment records', language: 'Input language', languageValue: 'English, Bangla, or Banglish',
    conditionTitle: 'POSSIBLE CONSUMER COMPLAINT ROUTE', conditions: ['Purchase and seller identified', 'Payment records attached', 'Delivery and eligibility details need review'],
    conditionStates: ['In sample', 'In sample', 'Needs review'], notProvider: 'Why not a payment-provider complaint?', notProviderText: 'This sample describes non-delivery by the seller. It does not establish a fault by the payment provider.',
    sourceLink: 'Read the official complaint process', draftTitle: 'Request concerning an undelivered phone', draftGreeting: 'To Sample Electronics,',
    draftBody: 'I am writing about a phone order that has not arrived. I reported paying ৳5,500. Please review the attached payment records and respond to my request for a refund.',
    draftResolved: 'The two sample receipts record ৳5,000 and ৳500, totaling ৳5,500.', draftUnresolved: 'The current receipt records ৳5,000. The remaining ৳500 needs clarification.',
    draftFoot: 'SAMPLE DRAFT · PREPARED, NOT SUBMITTED', copy: 'Copy sample draft', copied: 'Draft copied', copyError: 'Copy unavailable. Select the draft text to copy it.',
    foot: 'This walkthrough explains the interface. It does not assess a real dispute or submit a complaint.',
  },
  toolkit: {
    eyebrow: 'A PURPOSEFUL TOOLKIT', title: 'A place for every piece.\nA reason for every step.',
    intro: 'From the first “what happened?” to the next response, your case stays connected.',
    items: [
      { title: 'Tell it your way.', text: 'Type it out, speak in Bangla, or bring a document. Review the important details together.', label: 'VOICE + TEXT + DOCUMENTS', link: 'Start your story' },
      { title: 'Follow the evidence.', text: 'Keep receipts, messages, and facts linked. See what supports a statement and what still needs checking.', label: 'EVIDENCE + FACT REVIEW', link: 'Explore the sample' },
      { title: 'Know why. See what changes.', text: 'Explore possible paths, useful questions, and what-if comparisons before choosing an action.', label: 'PATHS + QUESTIONS + WHAT-IF', link: 'See how it works' },
      { title: 'Keep moving forward.', text: 'Prepare a draft, record a response, set a follow-up, and see how new information affects the case.', label: 'DRAFTS + ACTIVITY + REMINDERS', link: 'Explore a case' },
    ],
    voiceText: '“টাকা দিয়েছি, পণ্য পাইনি…”', voiceReview: 'Amount awaiting your review', linked: 'Linked to payment receipt', fact: 'Payment amount', supported: 'A source, not an assumption.',
    paths: ['Consumer route', 'Provider route', 'One useful question'], pathState: ['Explore conditions', 'Issue not established', 'Clarify the delivery date'],
    activity: ['Request prepared', 'New response added', 'Next step reviewed'], activityTime: ['Version 01', 'New information', 'Version 02'],
    moreTitle: 'A little more awareness, beyond your case.', merchantTitle: 'Merchant Check', merchantText: 'Explore reported merchant patterns with the context behind the numbers.', merchantLink: 'Check a merchant', communityTitle: 'Community experiences', communityText: 'Learn from shared experiences. Choose what you make public.', communityLink: 'Visit the community',
  },
  living: {
    eyebrow: 'A CASE THAT KEEPS UP', title: 'The story changes.\nYour next step can, too.', description: 'A new receipt. A seller’s reply. A missing detail filled in. Keep the history and see exactly what changed.',
    before: 'BEFORE', after: 'AFTER ADDING A RECEIPT', beforeText: 'Payment total needs clarification.', afterText: 'Two payments explain the reported total.', note: 'Original records stay linked. Changes stay visible.',
  },
  trust: {
    eyebrow: 'CLARITY ALSO MEANS HONEST LIMITS', title: 'Built to earn your trust.\nOne detail at a time.',
    items: [
      { title: 'Sources you can inspect.', text: 'Open the reference behind a possible route. See when more information or review is needed.', link: 'Explore sources', href: 'sources' },
      { title: 'Your review matters.', text: 'AI can propose. You can correct. Important facts stay open to your review before the next action.', link: 'How Ebarki works', href: 'how-it-works' },
      { title: 'Prepared means prepared.', text: 'A draft is not an official submission. You decide what to use and complete external steps yourself.', link: 'Understand the scope', href: 'limitations' },
    ],
    techTitle: 'Useful AI. Explicit rules. Human judgment.', techText: 'The system brings together evidence processing, source retrieval, procedural conditions, and your review. Inspect the build and its limits.', techLink: 'Under the hood',
    techSteps: ['Evidence', 'Facts', 'Sources', 'Conditions', 'Your next step'], privacy: 'Private case information and public reference material belong in separate places.', privacyLink: 'Read about your data',
  },
  faq: {
    eyebrow: 'A FEW THINGS YOU MIGHT BE WONDERING', title: 'Good questions.\nClear answers.',
    items: [
      { q: 'What can I bring to Ebarki?', a: 'Start with a consumer purchase, payment, or service problem in Bangladesh. Shopping and financial-service disputes are the main focus. Other domains have different support limits, which should be checked before relying on a route.' },
      { q: 'What if I don’t have a receipt?', a: 'You can begin with your account of what happened. Ebarki helps organize the available information and identify useful missing records. Your account remains attributed to you; it is not automatically treated as independently verified.' },
      { q: 'Can I use Bangla or voice?', a: 'The product supports English and Bangla interfaces, with narrative input in English, Bangla, and Banglish. Voice availability depends on the configured transcription capability and your browser. Important amounts and dates need your review.' },
      { q: 'Will Ebarki submit a complaint for me?', a: 'No. Ebarki helps prepare materials and identify possible official channels. You review the material and complete any external submission yourself. Preparing or downloading a draft does not file a complaint.' },
      { q: 'What happens to my personal information?', a: 'Real cases are private to their owner. Review the privacy information and processing choices before uploading sensitive records. This landing-page sample uses fictional details and does not upload any files.' },
      { q: 'Is a result or refund guaranteed?', a: 'No. Possible routes depend on the facts, applicable procedures, and review. Ebarki does not guarantee a refund, official acceptance, or a resolution. Uncertainty should stay visible.' },
    ],
  },
  final: { eyebrow: 'YOU DON’T NEED TO HAVE IT ALL FIGURED OUT', title: 'Start with\nwhat you have.', text: 'A story. A screenshot. A question. Let’s put the next step within reach.', sample: 'Or, take a look around first', stamp: 'YOUR NEXT CHAPTER\nSTARTS HERE' },
  footer: { tagline: 'The next step, made clear.', product: 'THE PRODUCT', useful: 'GOOD TO KNOW', how: 'How it works', cases: 'Your cases', scenarios: 'Sample cases', tech: 'Technology', sources: 'Sources', privacy: 'Privacy', limits: 'Scope & limitations', help: 'Help', made: 'Made in Bangladesh by Sakibul Islam Shovon.', note: 'Independent consumer preparation support. No government affiliation.', top: 'Back to top' },
};

export { bangla } from './bangla';

export type LandingCopy = typeof english;
