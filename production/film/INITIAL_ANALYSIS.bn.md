# এবারের কাজ: Ebarki চলচ্চিত্র

গবেষণা ও স্থানীয় পর্যবেক্ষণের তারিখ: ৫ নভেম্বর ২০২৬। এটি নির্মাণ-পূর্ব সিদ্ধান্তপত্র; চূড়ান্ত ভিডিও বা সম্পূর্ণ feature coverage-এর সনদ নয়।

## বাস্তব পণ্য সম্পর্কে সিদ্ধান্ত

Ebarki ভোক্তার বক্তব্য, নথি, গুরুত্বপূর্ণ তথ্য ও সম্ভাব্য করণীয় গুছিয়ে দেয়। এর সবচেয়ে বিশ্বাসযোগ্য প্রতিশ্রুতি: **নিজের নথির ভিত্তিতে পরের পদক্ষেপটি প্রস্তুত করা, সিদ্ধান্তের নিয়ন্ত্রণ নিজের হাতে রাখা।** নথি সত্যায়ন, মামলা জেতার সম্ভাবনা, টাকা ফেরতের নিশ্চয়তা কিংবা সরকারি পোর্টালে স্বয়ংক্রিয় অভিযোগ জমা—এর কোনোটিই দাবি করা যাবে না।

কোড-গ্রাফ, বর্তমান route/API, frontend controls, backend implementation, পুরোনো পরীক্ষার রিপোর্ট এবং নতুন browser discovery একসঙ্গে ব্যবহার করা হয়েছে। `video prompt.txt` কেবল পদ্ধতির রেফারেন্স। তার আলাদা প্রকল্পের exploit-কাহিনি, নির্দিষ্ট নয় অঙ্কের কাঠামো এবং স্বয়ংক্রিয়ভাবে নির্ভুল subtitle ধরে নেওয়া গ্রহণ করা হয়নি।

নতুন পরীক্ষায় backend-এর ১৮৪টি এবং web-এর ২৭টি পরীক্ষা পাস করেছে। এগুলো সমগ্র ব্রাউজার অভিজ্ঞতার সমতুল্য নয়। প্রথম browser discovery-তে ১৬টি view খোলা হয়েছে, page exception বা HTTP error রেকর্ড হয়নি। ফর্মের সব mutation এখনো পরীক্ষা করা হয়নি।

### যে পার্থক্যগুলো চলচ্চিত্রে জরুরি

| বিষয় | বর্তমান বাস্তবতা | চলচ্চিত্রে সঠিক ভাষা |
|---|---|---|
| পরিস্থিতির সারাংশ, contextual chat, reply wording | Groq-নির্ভর, consent প্রয়োজন; ব্যর্থ হলে fallback | সফল provider receipt থাকলে AI output; অন্যথায় মূল বক্তব্য বা template |
| image/scanned PDF reading | consent-ভিত্তিক vision; আনুমানিক source box, সীমিত পৃষ্ঠা | “AI-read, review required” |
| audio transcription | আপলোড করা সত্যিকারের audio-তে Whisper; manual বিকল্প | transcript-এর সঙ্গে মূল recording দেখানো |
| native PDF | parser ও PDFium | AI হিসেবে চিহ্নিত করা নয় |
| টাকার অমিল, chronology, pattern facts | নিয়মভিত্তিক হিসাব/প্রস্তাব | “Records compared”; মানব review ছাড়া সত্যায়ন নয় |
| retrieval | চলমান workspace-এ lexical reference lookup | embeddings বা vector reasoning চালু আছে বলা নয় |
| procedural paths ও what-if | true/false/unknown condition engine | শর্তের ব্যাখ্যা; বিজয়ের পূর্বাভাস নয় |
| community | seed feed, filter, comments/reactions; নতুন post প্রকাশে 503/disabled; in-memory সীমা | সীমিত preview, public publishing unavailable |
| merchant records | seeded profiles; calibrated AI risk model নয় | synthetic data/empty state; বাস্তব প্রতিষ্ঠানের অভিযোগ প্রচার নয় |
| admin | overview, cases, access, merchant overrides, moderation, notices, audit, source review, release controls | প্রকৃত admin console; consumer case-এর official adjudication নয় |
| নিরাপত্তা | owner checks, consent, role checks, version guards, local persistence | “Access checked by the server”; সর্বজনীন নিরাপত্তা সনদ নয় |

README, পরের হ্যান্ডঅফ ও বর্তমান কোডের মধ্যে community/merchant বিষয়ে অমিল আছে। বর্তমান source ও নতুন runtime-কে অগ্রাধিকার দেওয়া হয়েছে। Judge-admin evaluation route বর্তমানে আছে; consumer judge route আলাদা। Public deployment বা hardened admin-access certification এই চলচ্চিত্রের দাবি নয়।

## তিনটি সৃজনশীল দিক

| অবস্থান | ধারণা | শক্তি | সীমা |
|---|---|---|---|
| ১ | **The Missing Piece — ছড়িয়ে থাকা নথি, পরিষ্কার পরের পদক্ষেপ** | একই কেসে ৳৫০০-এর অমিল, উৎস দেখা, দ্বিতীয় রসিদ, reply, draft; প্রত্যক্ষ পরিবর্তন বোঝা যায় | “টাকা উদ্ধার” দিয়ে শেষ করা যাবে না |
| ২ | **One Question Changes the Next Step** | unknown condition ও what-if-কে স্মরণীয় করে | মানবিক সমস্যা ও multimodal AI তুলনামূলক কম গুরুত্ব পায় |
| ৩ | **From One Voice to Accountable Action** | বাংলা, community, admin স্বাভাবিকভাবে যুক্ত হয় | বর্তমান public-post সীমার কারণে পূর্ণ সামাজিক সমাধানের গল্প বিভ্রান্তিকর হবে |

প্রথম দিকটি নির্বাচিত। ফলাফল হলো পর্যালোচিত, ব্যবহারযোগ্য প্রস্তুতি। শেষ দৃশ্যে refund-confirmed বা complaint-submitted stamp থাকবে না।

## Tagline

১. **Your evidence. Your next move.** — চলচ্চিত্রের নির্বাচিত line; সংক্ষিপ্ত, সক্রিয়, সীমার মধ্যে।

২. **From scattered records to a clearer next step.** — অর্থ স্পষ্ট, brand reveal-এ একটু দীর্ঘ।

৩. **Clarity you can trace.** — প্রযুক্তির জন্য শক্তিশালী; সাধারণ ভোক্তার জন্য অপেক্ষাকৃত বিমূর্ত।

বর্তমান পণ্যের “The next step, made clear.” tagline ওয়েবসাইটে অপরিবর্তিত থাকবে। নির্বাচিত line চলচ্চিত্রের copy; নতুন logo বা পণ্যের নামকরণ নয়।

## সময় ও coverage সিদ্ধান্ত

লক্ষ্য ৩:৫০–৪:০০, ১৬:৯, ১৯২০×১০৮০, ৩০ fps। প্রথম ৫ সেকেন্ডে paid/not delivered এবং বিচ্ছিন্ন records। প্রায় ২০ সেকেন্ডের মধ্যে brand, তারপর real landing। মূল সময় AI ও নথির রূপান্তরে। community ও admin-এর নির্দিষ্ট অংশ থাকবে। শেষ প্রায় ৪৫ সেকেন্ডে স্তরে স্তরে প্রকৃত architecture।

প্রতিটি ক্ষুদ্র control-এর পাঠযোগ্য পূর্ণ interaction চার মিনিটে ঢোকানো সম্ভব নয়। প্রস্তাব: চার মিনিটের প্রধান চলচ্চিত্র এবং প্রয়োজনে পৃথক দীর্ঘ coverage reel। Coverage matrix-এ প্রধান চলচ্চিত্রে অনুপস্থিত control স্পষ্ট থাকবে। শুধু screenshot-এ বোতাম দেখা মানে তার কাজ সম্পাদনের প্রমাণ নয়।

## নির্বাচিত নির্মাণপদ্ধতি

Playwright-এ আলাদা স্থানীয় database ও কাল্পনিক records দিয়ে প্রকৃত UI interaction; Remotion-এ সম্পাদনাযোগ্য motion; FFmpeg-এ encode/mix/QA। UI সর্বত্র light mode। Local Kokoro female voice-এর নমুনা, এরপর final audio-ভিত্তিক acoustic alignment। চার শব্দের মধ্যে সময় সমান ভাগ করে subtitle বানানো গ্রহণযোগ্য নয়।

Browser footage-এ শুধু cursor এবং development-indicator suppression অনুমোদিত presentation overlay। API mocking, result injection, source text বদলানো বা ব্যর্থ request-কে success বানানো নিষিদ্ধ। দীর্ঘ অপেক্ষা কাটলে “Processing time condensed” লেখা থাকবে।

এই পরিবেশে ৪K render-এর চেয়ে sharp 1080p UI framing, সঠিক তথ্য, বাস্তব interaction ও ভালো audio-কে অগ্রাধিকার দেওয়া হয়েছে। মূল এডিট inspect না করে “world-class” বা “perfectly synchronized” quality verdict দেওয়া হবে না।
