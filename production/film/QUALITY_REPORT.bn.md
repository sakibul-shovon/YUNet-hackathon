# চূড়ান্ত media QA — review cut

মূল film ৪:০০ মিনিট, ১৯২০×১০৮০, ৩০ fps, ৭২০০ frames। Captioned ও clean master দুটোই H.264/AAC, ৪৮ kHz audio। Supplementary reel ২:২৪ মিনিট, ৪৩২০ frames; এটি music-only supporting walkthrough, প্রধান narrated film-এর বিকল্প নয়।

## সম্পাদিত যাচাই

- তিনটি encoded MP4 সম্পূর্ণ decode: exit 0, কোনো decode error নেই। মূল film-এ blackdetect interval নেই।
- প্রথম concat-এ ভিন্ন timestamp scale-এর কারণে frame loss ধরা পড়ে। `media-verification-first-attempt.json` ব্যর্থতার প্রমাণ রাখা হয়েছে; lossless 90 kHz normalization-এর পর দুই main export-এ ঠিক ৭২০০ frames পাওয়া গেছে।
- মূল film-এর ১৯টি এবং supplementary reel-এর ১১টি encoded sample frame/contact sheet দৃশ্যত দেখা হয়েছে। বাংলা shaping, title, caption safe area ও architectural lanes নমুনায় দেখা হয়েছে। পুরো motion playback এবং human listening sign-off করা হয়নি।
- Caption text-এ সম্পূর্ণ ৪১৭টি spoken word; 69টি phrase cue; overlap বা zero-duration নেই। সর্বোচ্চ reading rate 23.79 characters/second। CTC acoustic alignment; ৩০ fps quantization-এর precision সর্বোচ্চ ১৬.৬৭ ms। এটি perceptual accuracy-এর নিশ্চয়তা নয়।
- Final AAC decode বনাম mastered PCM: ১০, ৬০, ১২০, ১৮০ ও ২৩০ সেকেন্ডে correlation পরীক্ষা; সর্বোচ্চ measured lag 0.0 ms। এই নমুনায় encode drift পাওয়া যায়নি।
- আলাদা Whisper transcription-এ sequence similarity 97.36%; brand pronunciation/spelling, সংখ্যার লিখন ও কয়েকটি শব্দে পার্থক্য আছে। Matched onset-এর mean difference প্রায় 209 ms; ASR timestamp ground truth নয়। `independent-audio-check.json`-এ সব পার্থক্য অক্ষুণ্ণ। Frame-accurate human-verified captions দাবি করা হচ্ছে না।
- Measured captioned mix: -16.02 LUFS, -0.99 dBTP, LRA 7.00 LU। Female synthetic narration; original procedural music। Voice performance-এর subjective professional sign-off বাকি।
- এই production session-এ core suite: ১৮৪ backend + ২৭ web = ২১১ tests pass; ৭ backend warnings। এটি film-এর প্রতিটি control বা production release-এর certification নয়।

## বাস্তব demo ও সীমা

আলাদা localhost database/vault-এ fictional records, real app এবং configured real provider calls ব্যবহার করা হয়েছে। Summary, image reading, audio transcription, reply generation, payment reconciliation, PDF download, comment, reminder ও admin notice-এর receipts রাখা আছে। Reply output-এ buyer/seller wording অসংগত হওয়ায় UI-তে ব্যবহারকারীর সংশোধন করে Save my wording করা হয়েছে; সংশোধিত অংশকে untouched AI output বলা হয়নি।

Community-তে নতুন public post unavailable; seeded fictional discussion দেখানো হয়েছে। Merchant lookup-এ empty state; invented risk verdict নেই। কোনো official submission, refund, provider resolution বা legal win দাবি নেই। Privacy/security diagram design ব্যাখ্যা করে; deployed isolation, scale বা qualified legal approval certify করে না।

78টি family-তে প্রতিনিধিত্বমূলক দৃশ্য আছে; 47টি family-র পৃথক দৃশ্য নেই। Combined main+appendix-ও every-feature acceptance পূরণ করে না। বিশেষত registration/logout, dictation, redaction/deletion, cancellation/recovery, সব export, role mutation, moderation mutation ও source-release lifecycle সম্পূর্ণ দেখানো হয়নি। Workspace search capture selector timeout হয়েছিল; সেই ব্যর্থতা manifest-এ রাখা আছে এবং সফল প্রদর্শন বলে গণনা করা হয়নি।

চার মিনিটের readable story ও exhaustive control walkthrough-এর মধ্যে প্রস্তাবিত সমঝোতা: এই main film, পৃথক supporting reel এবং auditable coverage matrix। প্রকাশের আগে সম্পূর্ণ ভিডিও শুনে/দেখে voice pronunciation, subjective pacing ও caption onset review বাকি। বর্তমান artifact একটি technically checked review cut; world-class quality বা complete coverage sign-off নয়।
