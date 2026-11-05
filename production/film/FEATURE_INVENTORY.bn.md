# Feature inventory ও final coverage

১২৫টি capability/control family, ৯০১টি localized-copy entry, ১৪৮টি canonical API operation এবং ২৩টি page route-এর inventory। Copy-entry index প্রতিটি control/action-এর সম্পূর্ণ semantic audit নয়।

`Verified in final render` মানে নিচে উল্লেখ করা প্রতিনিধিত্বমূলক দৃশ্যের নমুনা final encoded frame-এ দেখা গেছে। এক family-র সব CRUD, error, accessibility বা security branch যাচাই হয়েছে—এমন অর্থ নয়। অনুপস্থিত family ও অপ্রদর্শিত variants আলাদা লেখা আছে।

Family-স্তরে দৃশ্য আছে: 78; পৃথক দৃশ্য নেই: 47। এটি complete feature coverage নয়।

| ID | Feature | Appearance | Status / সীমা |
|---|---|---|---|
| F001 | ল্যান্ডিং hero ও CTA | main 04 · 28–40s: landing ও sample illustration দেখা; সব CTA/animation state নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F002 | fictional payment illustration/reset | main 04 · 28–40s: landing ও sample illustration দেখা; সব CTA/animation state নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F003 | evidence/change/reply landing illustrations | main 04 · 28–40s: landing ও sample illustration দেখা; সব CTA/animation state নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F004 | FAQ expand/collapse | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F005 | guest start | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F006 | registration | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F007 | consumer login/password visibility | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F008 | logout | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F009 | consumer judge workspace | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F010 | admin login | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F011 | judge admin evaluation entry | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F012 | workspace case list/counts | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F013 | case search/status filter | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F014 | command palette/global actions | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F015 | sidebar/navigation | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F016 | Bangla/English locale switch | main 13 · 148–158s: একই case-এর Bangla UI; সব language/input combination নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F017 | light/dark/system preference | appendix A01 · 0–12s: settings/data-control UI দেখা; theme cycle, withdrawal ও deletion execute করা হয়নি | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F018 | help/how-it-works/privacy/limitations/technology/source pages | appendix A08 · 93–105s: primary-reference library দেখা; official portal submission নয়; appendix A11 · 134–144s: help ও limitation copy দেখা | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F019 | three-step narrative/context/review intake | main 05 · 40–53s: English narrative থেকে review; consent controls দৃশ্যমান, এই shot-এ নতুন case submit নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F020 | Bangla/English/Banglish narrative | main 05 · 40–53s: English narrative থেকে review; consent controls দৃশ্যমান, এই shot-এ নতুন case submit নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F021 | optional incident date/merchant/request | main 05 · 40–53s: English narrative থেকে review; consent controls দৃশ্যমান, এই shot-এ নতুন case submit নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F022 | multiple evidence selection/remove | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F023 | case storage consent | main 05 · 40–53s: English narrative থেকে review; consent controls দৃশ্যমান, এই shot-এ নতুন case submit নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F024 | optional external AI consent | main 05 · 40–53s: English narrative থেকে review; consent controls দৃশ্যমান, এই shot-এ নতুন case submit নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F025 | browser speech dictation | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F026 | case title/story/context edit | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F027 | guest-to-account continuity | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F028 | consent withdrawal | appendix A01 · 0–12s: settings/data-control UI দেখা; theme cycle, withdrawal ও deletion execute করা হয়নি | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F029 | case deletion request/status | appendix A01 · 0–12s: settings/data-control UI দেখা; theme cycle, withdrawal ও deletion execute করা হয়নি | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F030 | PDF/image/audio upload and validation | main 09 · 95–108s: বাস্তব image/audio upload ও reader receipt; source image/audio transcript ও playback; validation edge cases নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F031 | 20MB limit/duplicate handling | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F032 | private original download/preview | main 09 · 95–108s: বাস্তব image/audio upload ও reader receipt; source image/audio transcript ও playback; validation edge cases নয়; appendix A06 · 69–83s: original selection ও link-to-fact form; নতুন link save নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F033 | native PDF text/page coordinates | main 07 · 67–82s: source moment নির্বাচন ও This looks right; সব correction/exclusion variant নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F034 | scanned/hybrid PDF vision reading | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F035 | image OCR/approximate boxes | main 09 · 95–108s: বাস্তব image/audio upload ও reader receipt; source image/audio transcript ও playback; validation edge cases নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F036 | audio transcription/timestamped segments | main 09 · 95–108s: বাস্তব image/audio upload ও reader receipt; source image/audio transcript ও playback; validation edge cases নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F037 | audio playback/waveform | main 09 · 95–108s: বাস্তব image/audio upload ও reader receipt; source image/audio transcript ও playback; validation edge cases নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F038 | manual transcript alternative | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F039 | paste attributed message source | main 11 · 121–135s: fictional seller message, real model response, ব্যবহারকারীর সংশোধিত wording সংরক্ষণ | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F040 | source-linked chronology | main 07 · 67–82s: source moment নির্বাচন ও This looks right; সব correction/exclusion variant নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F041 | moment filters/review state | main 07 · 67–82s: source moment নির্বাচন ও This looks right; সব correction/exclusion variant নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F042 | confirm/correct date/exclude/reopen moment | main 07 · 67–82s: source moment নির্বাচন ও This looks right; সব correction/exclusion variant নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F043 | fact-source links/page/quote/region | main 07 · 67–82s: source moment নির্বাচন ও This looks right; সব correction/exclusion variant নয়; appendix A06 · 69–83s: original selection ও link-to-fact form; নতুন link save নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F044 | image region selection/redacted copy | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F045 | evidence delete/derived reading cleanup | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F046 | payment linked-receipt reconciliation | main 08 · 82–95s: দ্বিতীয় sample receipt যোগ, linked total ৳৫,৫০০ | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F047 | second sample receipt addition | main 08 · 82–95s: দ্বিতীয় sample receipt যোগ, linked total ৳৫,৫০০ | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F048 | fact accept/correct/uncertain/reject | appendix A03 · 26–39s: fact review ও Add information form; নতুন fact save নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F049 | manual typed fact addition | appendix A03 · 26–39s: fact review ও Add information form; নতুন fact save নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F050 | Bangla digit/date/poisha normalization | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F051 | consent-scoped situation summary | main 06 · 53–67s: বাস্তব summary ও work plan/receipt; পুরো run history নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F052 | original-account fallback | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F053 | contextual copilot/general guidance | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F054 | reply preparation from seller message | main 11 · 121–135s: fictional seller message, real model response, ব্যবহারকারীর সংশোধিত wording সংরক্ষণ | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F055 | reply edit/save/reopen | main 11 · 121–135s: fictional seller message, real model response, ব্যবহারকারীর সংশোধিত wording সংরক্ষণ | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F056 | run plan/real stage receipts/duration | main 06 · 53–67s: বাস্তব summary ও work plan/receipt; পুরো run history নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F057 | SSE updates/polling recovery | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F058 | cancel at checkpoints | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F059 | run history/replay | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F060 | reuse readings by evidence ID/hash | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F061 | auto-follow canvas/manual pin | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F062 | conditional procedural routes/trace | main 10 · 108–121s: goods-received preview ও condition comparison; saved case-এ adoption নয়; appendix A04 · 39–53s: path list ও Why this path; সব domain/citation/action branch নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F063 | reference lookup/exact citation navigation | appendix A04 · 39–53s: path list ও Why this path; সব domain/citation/action branch নয়; appendix A08 · 93–105s: primary-reference library দেখা; official portal submission নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F064 | next-best question answer/skip | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F065 | unknown fact propagation | main 10 · 108–121s: goods-received preview ও condition comparison; saved case-এ adoption নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F066 | what-if presets/custom values/compare | main 10 · 108–121s: goods-received preview ও condition comparison; saved case-এ adoption নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F067 | version-guarded what-if adoption | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F068 | issue add/confirm/reject | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F069 | issue split/merge | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F070 | multi-domain packs | appendix A04 · 39–53s: path list ও Why this path; সব domain/citation/action branch নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F071 | action prerequisites/next preparation | appendix A04 · 39–53s: path list ও Why this path; সব domain/citation/action branch নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F072 | document purpose/language selection | main 12 · 135–148s: draft, review dialog ও genuine PDF export; সব format/version guard নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F073 | editable sentence attribution | main 12 · 135–148s: draft, review dialog ও genuine PDF export; সব format/version guard নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F074 | saved document versions | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F075 | PDF/HTML/Markdown/evidence ZIP export | main 12 · 135–148s: draft, review dialog ও genuine PDF export; সব format/version guard নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F076 | evidence index/original inclusion choice | main 12 · 135–148s: draft, review dialog ও genuine PDF export; সব format/version guard নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F077 | reviewed export/current-version guard | main 12 · 135–148s: draft, review dialog ও genuine PDF export; সব format/version guard নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F078 | filing handoff/review/copy fields | appendix A09 · 105–114s: ৳৫,৫০০ handoff ও review checkbox; official form submit নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F079 | official destination links/needs-recheck flags | appendix A08 · 93–105s: primary-reference library দেখা; official portal submission নয়; appendix A09 · 105–114s: ৳৫,৫০০ handoff ও review checkbox; official form submit নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F080 | activity timeline | appendix A05 · 53–69s: বাস্তব reminder save; update form খোলা, update submit/cancel নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F081 | user-reported seller/provider/external update | appendix A05 · 53–69s: বাস্তব reminder save; update form খোলা, update submit/cancel নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F082 | reported resolution flag | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F083 | Bangladesh-time personal reminders/add/cancel | appendix A05 · 53–69s: বাস্তব reminder save; update form খোলা, update submit/cancel নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F084 | community feed/category filter | main 14 · 158–172s: fictional seeded feed, category ও discussion/comment; নতুন post unavailable | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F085 | open discussion/read comments | main 14 · 158–172s: fictional seeded feed, category ও discussion/comment; নতুন post unavailable | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F086 | add public comment | main 14 · 158–172s: fictional seeded feed, category ও discussion/comment; নতুন post unavailable | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F087 | similar-experience reaction | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F088 | new public post composer (disabled/503) | main 14 · 158–172s: fictional seeded feed, category ও discussion/comment; নতুন post unavailable | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F089 | private-case CTA/privacy guidance | main 14 · 158–172s: fictional seeded feed, category ও discussion/comment; নতুন post unavailable | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F090 | merchant name lookup | appendix A07 · 83–93s: fictional merchant lookup-এর প্রকৃত empty state; safety verdict নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F091 | merchant report counts/details | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F092 | merchant radar seed/empty state | appendix A07 · 83–93s: fictional merchant lookup-এর প্রকৃত empty state; safety verdict নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F093 | role-filtered panes | main 15 · 172–187s: নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F094 | overview metrics | main 15 · 172–187s: নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F095 | record inspect/filter/refresh | main 15 · 172–187s: নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F096 | case list/status override/reason | main 15 · 172–187s: নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F097 | people roles/restrict/restore | main 15 · 172–187s: নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F098 | merchant review override | main 15 · 172–187s: নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F099 | post pin/unpin/hide/unhide/dismiss reports | main 15 · 172–187s: নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F100 | notice create/edit/disable | appendix A10 · 114–134s: fictional notice create 200 এবং audit receipt; edit/disable নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F101 | audit action receipts | appendix A10 · 114–134s: fictional notice create 200 এবং audit receipt; edit/disable নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F102 | source candidate list/diff | main 15 · 172–187s: নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F103 | official source watcher check | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F104 | manual source import | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F105 | source review scope/decision/rationale | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F106 | release build | main 15 · 172–187s: নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F107 | release promote/disable | main 15 · 172–187s: নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F108 | release rollback | main 15 · 172–187s: নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F109 | flag impacted cases | main 15 · 172–187s: নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F110 | Next.js/React/next-intl frontend | main 16 · 187–201s: source-grounded engineering illustration; runtime security/persistence certification নয় | Verified in final render; সব implementation/operational guarantee পরীক্ষা নয়। |
| F111 | same-origin API BFF | main 16 · 187–201s: source-grounded engineering illustration; runtime security/persistence certification নয় | Verified in final render; সব implementation/operational guarantee পরীক্ষা নয়। |
| F112 | FastAPI/Pydantic API | main 16 · 187–201s: source-grounded engineering illustration; runtime security/persistence certification নয় | Verified in final render; সব implementation/operational guarantee পরীক্ষা নয়। |
| F113 | SQLAlchemy owner-scoped local persistence | main 16 · 187–201s: source-grounded engineering illustration; runtime security/persistence certification নয় | Verified in final render; সব implementation/operational guarantee পরীক্ষা নয়। |
| F114 | private local evidence vault | main 16 · 187–201s: source-grounded engineering illustration; runtime security/persistence certification নয় | Verified in final render; সব implementation/operational guarantee পরীক্ষা নয়। |
| F115 | session cookies/JWT/revocation/CSRF/origin checks | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F116 | role enforcement | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F117 | optimistic case/document versions | main 18 · 215–232s: source-grounded engineering illustration; runtime security/persistence certification নয় | Verified in final render; সব implementation/operational guarantee পরীক্ষা নয়। |
| F118 | public reference/private case separation | main 18 · 215–232s: source-grounded engineering illustration; runtime security/persistence certification নয় | Verified in final render; সব implementation/operational guarantee পরীক্ষা নয়। |
| F119 | source governance/versioned release | main 18 · 215–232s: source-grounded engineering illustration; runtime security/persistence certification নয় | Verified in final render; সব implementation/operational guarantee পরীক্ষা নয়। |
| F120 | jobs/outbox/watcher interfaces | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F121 | eight isolated scenarios/launch/reset | appendix A02 · 12–26s: scenario library ও sample story দেখা; আটটি launch/reset journey নয় | Verified in final render; একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে। |
| F122 | legacy multimodal compatibility endpoints | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F123 | optional Gemini reader/dense adapter | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F124 | health/readiness checks | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
| F125 | reduced motion/focus/responsive controls | — | Not planned; চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়। |
