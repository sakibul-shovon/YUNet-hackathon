# Ebarki — The Missing Piece

৪ মিনিটের narrated product-film review cut ও ২:২৪ মিনিটের supplementary walkthrough। নির্বাচিত film tagline: **Your evidence. Your next move.**

- [Captioned film](out/ebarki-captioned.mp4)
- [Clean master](out/ebarki-master.mp4)
- [Supporting reel](out/ebarki-coverage-reel.mp4)
- [SRT](captions/ebarki.en.srt) · [VTT](captions/ebarki.en.vtt) · [Word timestamps](captions/words.json)
- [প্রকৃত QA ও সীমা](QUALITY_REPORT.bn.md)
- [Feature coverage](FEATURE_INVENTORY.bn.md) · [Machine-readable mapping](feature-coverage.json)
- [Storyboard](STORYBOARD.bn.md) · [English script](VOICEOVER.en.txt)
- [প্রাথমিক audit ও তিনটি concept](INITIAL_ANALYSIS.bn.md) · [Research](RESEARCH.bn.md)
- [Case bible](CASE_BIBLE.bn.md) · [Assets ও reproduction](ASSET_PLAN.bn.md)

`scenes.json`/`appendix.json` editable timing; `index.tsx` opening, wordmark ও engineering animation; `build_frames.mjs` UI backgrounds; `finish.py` authoritative hybrid compositor। npm/Python lock files সংরক্ষিত। Generated source archive-এ clips, actual end screenshots, fonts/licenses, voice/music stems ও caption data আছে। Database, cookies, credentials, model weights ও node_modules অন্তর্ভুক্ত নয়।

Original footage-এ অপেক্ষা ও playback retimed হয়েছে; ধারাবাহিক live session-এর দাবি নয়। UI ফল বদলানো বা API response mock করা হয়নি। Generated source archive থেকে fresh render করতে FFmpeg/FFprobe, Edge এবং npm dependencies প্রয়োজন; existing footage দিয়েই render হয়, নতুন provider calls দরকার হয় না।
