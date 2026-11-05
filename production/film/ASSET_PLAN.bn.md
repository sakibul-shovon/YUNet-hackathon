# Production assets ও পুনরুৎপাদন

## প্রস্তুত/সংরক্ষিত

- `scenes.json`: ১৯ দৃশ্যের timing, English voiceover, বাংলা composition description, features ও sound cue।
- `index.tsx`: deterministic vector opening/brand/architecture এবং real footage composition।
- `capture.mjs`, `audit_browser.mjs`, `prepare_media.mjs`: genuine browser interaction, screenshots, raw recordings, receipt capture। কোনো route interception/mock response নেই।
- `serve_demo.py`: আলাদা SQLite ও local vault, মূল FastAPI app। শুধু fictional seed records; provider calls আসল configuration ব্যবহার করে।
- `assets/fictional-seller-messages.png`: একই কেসের English/Bangla synthetic message sheet, স্পষ্ট fictional label।
- app-generated `SAMPLE-001`/`SAMPLE-002`: প্রকৃত sample PDFs; runtime evidence vault-এ original, hash, source links।
- `audio/fictional-account.wav`: একই কেসের actual playable synthetic recording; real transcription input।
- `audio/01.wav` … `19.wav`: consistent female voice; `af_heart-sample.wav` ও `af_sarah-sample.wav` comparison assets।
- `audio/voice.wav`, `music-original.wav`, `mix-premaster.wav`, `mix.wav`: editable stems ও mastered mix।
- `captions/words.json`, `cues.json`, `.srt`, `.vtt`: final audio-ভিত্তিক timestamp data।
- `public/fonts`: প্রকল্পের self-hosted fonts ও license copies।
- `qa/`: source index, route inventory, live run/provider receipts, capture manifest, alignment এবং media checks।

## Production constraints

UI ১৬০০×৯০০ light-mode recording; composition ১৯২০×১০৮০/৩০ fps। Camera scale সংযত; typography পড়ার জন্য প্রয়োজনীয় result-এ scroll। `nextjs-portal` কেবল development indicator হিসেবে capture-এ আড়াল; product error বা unavailable-state আড়াল নয়। Cursor overlay শুধু pointer visualization।

Local session cookies/database/credentials `tmp/`-এ এবং ignored। QA-তে isolated fictional case data ছাড়া অন্য user records নেই। Provider secret configuration পড়ে print/export করা হয় না। Public publishing disabled অবস্থাকে bypass করে নতুন post creation success দেখানো হয়নি; seed label দৃশ্যমান।

## Commands

Repository root থেকে:

```powershell
python scripts/tasks.py backend run python ../../production/film/serve_demo.py
$env:BACKEND_API_URL='http://127.0.0.1:8002'
$env:EBARKI_NEXT_DIST_DIR='.next-film'
python scripts/tasks.py web exec next dev -p 3002
python scripts/tasks.py web exec node ../../production/film/audit_browser.mjs
python scripts/tasks.py backend run python ../../production/film/setup_audio.py
python scripts/tasks.py backend run python ../../production/film/voice.py synth
python scripts/tasks.py backend run python ../../production/film/voice.py align
python scripts/tasks.py backend run python ../../production/film/voice.py music
python scripts/tasks.py backend run python ../../production/film/verify_audio.py
python scripts/tasks.py web exec node ../../production/film/prepare_media.mjs
python scripts/tasks.py web exec node ../../production/film/capture.mjs
python scripts/tasks.py web exec node ../../production/film/build_frames.mjs
python scripts/tasks.py backend run python ../../production/film/finish.py render
python scripts/tasks.py backend run python ../../production/film/finish.py appendix
python scripts/tasks.py backend run python ../../production/film/qa_media.py
python scripts/tasks.py backend run python ../../production/film/qa_encoded_audio.py
python scripts/tasks.py backend run python ../../production/film/make_review.py
python scripts/tasks.py backend run python ../../production/film/finalize.py package
```

Fresh পুনরুৎপাদনে প্রথমে `package-lock.json` অনুযায়ী isolated `production/film` npm dependencies install করতে হবে। Native browser/executable availability environment-নির্ভর। Raw footage ও generated outputs স্থানীয়ভাবে রাখা হয়; বড় binaries Git source checkpoint থেকে বাদ। Re-capture একই sandbox state-এ destructive commands পুনরাবৃত্তি নয়; নতুন database/session দিয়ে reproducible baseline শুরু করা উত্তম।

## QA gate

Playable render, actual duration/resolution/frame count; full decode; sampled frames; subtitle overlap/text coverage; independent ASR differences; measured loudness/peak; visible Bangla shaping; provider methods এবং final scene-to-feature coverage আলাদা check। কোনো control শুধু source-এ থাকলে `Verified in final render` নয়।

## Final render-এর প্রকৃত পথ

Full Remotion UI composition-এ source-end decoder error পাওয়া গিয়েছিল। ফলে authoritative output হলো hybrid pipeline: Remotion শুধু vector opening/engineering render করে, FFmpeg actual UI footage compose করে। Direct full-composition command-কে verified reproduction বলা হচ্ছে না। Stream time base 90 kHz-এ lossless normalize করে concat করা হয়। Captioned output-এ explicit 30 fps CFR আছে। Main UI shot-এ actual end screenshot-এর 2.5-second hold আছে; footage speed retimed।

Existing footage-সহ source archive থেকে render-এ নতুন login/provider দরকার নেই। Fresh capture-এর জন্য আলাদা server চালিয়ে audit_browser.mjs-এর demo setup সম্পন্ন করতে হবে; tmp session/database export করা হয়নি। এই setup app-এর configured provider credentials ব্যবহার করে, source archive থেকে credential পাওয়া যাবে না।
