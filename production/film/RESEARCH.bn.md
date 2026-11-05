# গবেষণা ও production stack

৫ নভেম্বর ২০২৬-এ খোলা primary pages ও documentation-এর ভিত্তিতে। নিচের creative takeaways নির্মাণের জন্য বিশ্লেষণ; প্রতিটি সম্পূর্ণ চলচ্চিত্র frame-by-frame দেখা হয়েছে—এমন দাবি নয়। পুরোনো স্থিতিশীল reference-ও রাখা হয়েছে; তালিকাটি সমগ্র ২০২৬ বাজারের exhaustive survey নয়।

| Reference | যাচাইযোগ্য উৎস | Ebarki-তে প্রয়োগের সিদ্ধান্ত |
|---|---|---|
| Apple product presentation | [Apple Events](https://www.apple.com/apple-events/) | একটি frame-এ একটি প্রধান বক্তব্য; product silhouette থেকে real interface; বড় typography ও বিরতি |
| Meta Orion | [Meta introduction](https://about.fb.com/news/2024/09/introducing-orion-our-first-true-augmented-reality-glasses/) | বাস্তব ব্যবহারের মাধ্যমে প্রযুক্তি ব্যাখ্যা; prototype-কে prototype বলা |
| Google / Ordinary Folk | [studio portfolio](https://www.ordinaryfolk.co/work) | একই visual motif দিয়ে abstract idea ও product-এর মধ্যে যাতায়াত; নথির corner/line হবে connector |
| Stripe | [Sessions 2025](https://stripe.com/sessions/2025) | কাজের ফল আগে, infrastructure পরে; UI ও engineering একই গল্পে |
| Notion | [AI product](https://www.notion.com/product/ai), [launch keynote](https://info.notion.so/make-with-notion-on-demand) | input → transformation → editable output; admin control-ও product story-র অংশ |
| Linear | নির্দিষ্ট agent-launch URL এই গবেষণায় খোলা যায়নি | প্রত্যক্ষ film analysis হিসেবে ব্যবহার করা হয়নি; দাবিকৃত benchmark নয় |

প্রথম পাঁচ সেকেন্ডের hook: “PAID / NOT DELIVERED” এবং দুই আলাদা record। ব্যবহারকারীর দুর্দশার অভিনয় বা দীর্ঘ হতাশ মুখের stock shot নয়। Brand reveal-এ বিচ্ছিন্ন রেখা এক page-corner mark-এ এসে জুড়বে। Landing-এর আসল motion দেখিয়ে এরপর একই নথি workspace-এ যাবে। AI দৃশ্যে কী input গেল, কোন তথ্য পড়া হলো এবং কে review করল—তিন স্তর আলাদা থাকবে।

### Tool comparison

| Tool | প্রকৃত ভূমিকা | মান/নিয়ন্ত্রণ/খরচ/সীমা | সিদ্ধান্ত |
|---|---|---|---|
| [Remotion](https://www.remotion.dev/docs/) | React দিয়ে frame-based composition, render | deterministic, editable; licensing entity-নির্ভর, সর্বজনীন free নয় | প্রধান compositor; installed version lock |
| [Playwright video](https://playwright.dev/docs/videos) | আসল browser recording | viewport/video dimensions explicit করতে হয়; context close-এ file final হয় | UI capture ও interaction receipt |
| [After Effects](https://helpx.adobe.com/after-effects/desktop/get-started/after-effects-faq/faq.html) | motion graphics/compositing | অত্যন্ত শক্তিশালী, subscription ও manual production setup | উপলব্ধ license/operator যাচাই হয়নি; critical path নয় |
| [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) | edit/color/Fairlight/Fusion | final human polish-এর ভালো পথ; এই machine-এ installation যাচাই হয়নি | future finishing option |
| Blender | 3D camera/object render | original 3D asset ও lighting-এর বাড়তি কাজ; local executable পাওয়া যায়নি | প্রয়োজনহীন 3D বাদ |
| GSAP / Three.js / Rive | interface/vector/3D animation | browser-native motion-এ ভালো; একা পূর্ণ audio/subtitle pipeline নয় | app-এর নিজস্ব motion অক্ষুণ্ণ; film-এ deterministic React vector |
| [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) / [ONNX wrapper](https://github.com/thewh1teagle/kokoro-onnx) | local female TTS | open weights; CPU; pronunciation ও performance sample শুনে যাচাই প্রয়োজন | af_heart / af_sarah comparison; no cloned identity |
| [ElevenLabs](https://elevenlabs.io/docs/eleven-api/guides/cookbooks/forced-alignment) | hosted TTS/alignment option | existing audio+text alignment API; connected credential/plan এই task-এ পাওয়া যায়নি | available হলে premium voice alternative, blocked dependency নয় |
| [WhisperX](https://github.com/m-bain/whisperX) | ASR ও acoustic forced alignment | timestamps estimate; digit/OOV ও pause manually inspect করতে হয় | alignment methodology reference |
| FFmpeg | encode, loudness, mux, subtitle, decode checks | installed; creative quality নিজে নিশ্চিত করে না | final media verification |
| Generative video | human vignette / atmospheric imagery | identity/text/continuity অনিশ্চিত; actual UI demonstration-এর জন্য অনুপযুক্ত | মূল ছবির critical path নয় |

### Motion ও sound specification

- Warm ivory, ink, brick, restrained teal; ওয়েবসাইটের রঙের সঙ্গে মিল।
- ৩০ fps; short transitions ১২–২০ frames; body copy পড়ার সময় আগে মাপতে হবে।
- Narration-এর নিচে music duck; section change-এ সংযত click/paper/air sound। Original procedural bed-এর project থাকবে। Third-party song নেওয়া হয়নি।
- Target mix: প্রায় −১৬ LUFS, true peak সর্বোচ্চ −১ dBTP; measured result রিপোর্টে থাকবে, target-কে achieved বলা নয়।
- English phrase captions; ২ লাইনের মধ্যে, safe area, audio onset/offset অনুযায়ী; waveform ও final render-এ sample review।
- ৪K output-এর নাম দিয়ে 1080p capture upscale করে অতিরিক্ত detail-এর দাবি করা যাবে না।
