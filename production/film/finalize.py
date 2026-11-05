"""Record evidence-scoped coverage and package the local production assets."""
import hashlib
import json
import re
import shutil
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
scenes=read('scenes.json');appendix=read('appendix.json')
manifest={r['name']:r for r in read('qa/capture-manifest.json')}

# Each mapping describes only the part actually demonstrated, never every
# operation mentioned in a grouped capability's name.
mapping={
 'landing':([1,2,3],'landing ও sample illustration দেখা; সব CTA/animation state নয়'),
 'intake':([19,20,21,23,24],'English narrative থেকে review; consent controls দৃশ্যমান, এই shot-এ নতুন case submit নয়'),
 'briefing':([51,56],'বাস্তব summary ও work plan/receipt; পুরো run history নয়'),
 'source':([33,40,41,42,43],'source moment নির্বাচন ও This looks right; সব correction/exclusion variant নয়'),
 'reconcile':([46,47],'দ্বিতীয় sample receipt যোগ, linked total ৳৫,৫০০'),
 'media':([30,32,35,36,37],'বাস্তব image/audio upload ও reader receipt; source image/audio transcript ও playback; validation edge cases নয়'),
 'whatif':([62,65,66],'goods-received preview ও condition comparison; saved case-এ adoption নয়'),
 'reply':([39,54,55],'fictional seller message, real model response, ব্যবহারকারীর সংশোধিত wording সংরক্ষণ'),
 'draft':([72,73,75,76,77],'draft, review dialog ও genuine PDF export; সব format/version guard নয়'),
 'bangla':([16],'একই case-এর Bangla UI; সব language/input combination নয়'),
 'community':([84,85,86,88,89],'fictional seeded feed, category ও discussion/comment; নতুন post unavailable'),
 'admin':([93,94,95,96,97,98,99,102,106,107,108,109],'নয়টি admin pane navigation; mutation/release lifecycle-এর পূর্ণ পরীক্ষা নয়'),
 'settings':([17,28,29],'settings/data-control UI দেখা; theme cycle, withdrawal ও deletion execute করা হয়নি'),
 'scenarios':([121],'scenario library ও sample story দেখা; আটটি launch/reset journey নয়'),
 'facts':([48,49],'fact review ও Add information form; নতুন fact save নয়'),
 'paths':([62,63,70,71],'path list ও Why this path; সব domain/citation/action branch নয়'),
 'activity':([80,81,83],'বাস্তব reminder save; update form খোলা, update submit/cancel নয়'),
 'originals':([32,43],'original selection ও link-to-fact form; নতুন link save নয়'),
 'merchant':([90,92],'fictional merchant lookup-এর প্রকৃত empty state; safety verdict নয়'),
 'reference':([18,63,79],'primary-reference library দেখা; official portal submission নয়'),
 'handoff':([78,79],'৳৫,৫০০ handoff ও review checkbox; official form submit নয়'),
 'admin-actions':([100,101],'fictional notice create 200 এবং audit receipt; edit/disable নয়'),
 'help':([18],'help ও limitation copy দেখা'),
}
rows=read('feature-coverage.json')
for row in rows:
    row['appearances']=[]
    row['coverage_status']='Not planned'
    row['verification_evidence']=None
    row['omission_reason']='চার মিনিটের মূল film ও supplementary reel-এ পৃথক প্রদর্শন নেই; source presence সফল runtime প্রমাণ নয়।'
for clip,(ids,scope) in mapping.items():
    for sequence,items in [('main',scenes),('appendix',appendix)]:
        for scene in items:
            if scene.get('clip')!=clip:continue
            for fid in ids:
                row=rows[fid-1]
                row['appearances'].append({'sequence':sequence,'scene':scene['id'],'start':scene['start'],'end':scene['end'],'scope_bn':scope,'capture_status':manifest[clip]['status'],'evidence':['qa/capture-manifest.json','qa/capture-receipts.json',f'capture/{clip}-end.png']})
                row['coverage_status']='Verified in final render'
                row['verification_evidence']='Final encoded contact-sheet sample inspected; representative scope only. Not full control-family acceptance.'
                row['omission_reason']='একই family-র অপ্রদর্শিত variants উপরোক্ত scope-এ উল্লেখ আছে।'
for fid,scene_ids in [(110,['16']),(111,['16']),(112,['16']),(113,['16']),(114,['16']),(117,['18']),(118,['18']),(119,['18'])]:
    row=rows[fid-1]
    for sid in scene_ids:
        scene=next(s for s in scenes if s['id']==sid)
        row['appearances'].append({'sequence':'main','scene':sid,'start':scene['start'],'end':scene['end'],'scope_bn':'source-grounded engineering illustration; runtime security/persistence certification নয়','evidence':['index.tsx',f'out/review-frames/{194 if sid=="16" else 223:03}.png']})
    row['coverage_status']='Verified in final render'
    row['verification_evidence']='Final encoded architecture sample inspected; diagram only.'
    row['omission_reason']='সব implementation/operational guarantee পরীক্ষা নয়।'
(ROOT/'feature-coverage.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
counts=Counter(r['coverage_status'] for r in rows)
lines=['# Feature inventory ও final coverage','','১২৫টি capability/control family, ৯০১টি localized-copy entry, ১৪৮টি canonical API operation এবং ২৩টি page route-এর inventory। Copy-entry index প্রতিটি control/action-এর সম্পূর্ণ semantic audit নয়।','','`Verified in final render` মানে নিচে উল্লেখ করা প্রতিনিধিত্বমূলক দৃশ্যের নমুনা final encoded frame-এ দেখা গেছে। এক family-র সব CRUD, error, accessibility বা security branch যাচাই হয়েছে—এমন অর্থ নয়। অনুপস্থিত family ও অপ্রদর্শিত variants আলাদা লেখা আছে।','',f'Family-স্তরে দৃশ্য আছে: {counts["Verified in final render"]}; পৃথক দৃশ্য নেই: {counts["Not planned"]}। এটি complete feature coverage নয়।','','| ID | Feature | Appearance | Status / সীমা |','|---|---|---|---|']
for row in rows:
    appearances='; '.join(f"{a['sequence']} {a['scene']} · {a['start']}–{a['end']}s: {a['scope_bn']}" for a in row['appearances']) or '—'
    lines.append('| '+' | '.join([row['id'],row['feature'].replace('|','/'),appearances.replace('|','/'),row['coverage_status']+'; '+row['omission_reason']])+' |')
(ROOT/'FEATURE_INVENTORY.bn.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

metrics=read('qa/media-verification.json');audio=read('qa/encoded-audio-timing.json');alignment=read('qa/caption-alignment.json');asr=read('qa/independent-audio-check.json')
for name in ['ebarki-master.mp4','ebarki-captioned.mp4']:
    m=metrics[name]
    assert m['frame_rate']=='30/1' and m['frame_count']=='7200' and m['duration_seconds']==240 and not m['decode_errors']
assert metrics['captions']['overlaps']==0
qa=f'''# চূড়ান্ত media QA — review cut

মূল film ৪:০০ মিনিট, ১৯২০×১০৮০, ৩০ fps, ৭২০০ frames। Captioned ও clean master দুটোই H.264/AAC, ৪৮ kHz audio। Supplementary reel ২:২৪ মিনিট, ৪৩২০ frames; এটি music-only supporting walkthrough, প্রধান narrated film-এর বিকল্প নয়।

## সম্পাদিত যাচাই

- তিনটি encoded MP4 সম্পূর্ণ decode: exit 0, কোনো decode error নেই। মূল film-এ blackdetect interval নেই।
- প্রথম concat-এ ভিন্ন timestamp scale-এর কারণে frame loss ধরা পড়ে। `media-verification-first-attempt.json` ব্যর্থতার প্রমাণ রাখা হয়েছে; lossless 90 kHz normalization-এর পর দুই main export-এ ঠিক ৭২০০ frames পাওয়া গেছে।
- মূল film-এর ১৯টি এবং supplementary reel-এর ১১টি encoded sample frame/contact sheet দৃশ্যত দেখা হয়েছে। বাংলা shaping, title, caption safe area ও architectural lanes নমুনায় দেখা হয়েছে। পুরো motion playback এবং human listening sign-off করা হয়নি।
- Caption text-এ সম্পূর্ণ ৪১৭টি spoken word; {alignment['cues']}টি phrase cue; overlap বা zero-duration নেই। সর্বোচ্চ reading rate {metrics['captions']['max_characters_per_second']:.2f} characters/second। CTC acoustic alignment; ৩০ fps quantization-এর precision সর্বোচ্চ ১৬.৬৭ ms। এটি perceptual accuracy-এর নিশ্চয়তা নয়।
- Final AAC decode বনাম mastered PCM: ১০, ৬০, ১২০, ১৮০ ও ২৩০ সেকেন্ডে correlation পরীক্ষা; সর্বোচ্চ measured lag {audio['max_absolute_lag_ms']} ms। এই নমুনায় encode drift পাওয়া যায়নি।
- আলাদা Whisper transcription-এ sequence similarity {asr['sequence_similarity']:.2%}; brand pronunciation/spelling, সংখ্যার লিখন ও কয়েকটি শব্দে পার্থক্য আছে। Matched onset-এর mean difference প্রায় {asr['matched_word_onset_mean_difference_ms']:.0f} ms; ASR timestamp ground truth নয়। `independent-audio-check.json`-এ সব পার্থক্য অক্ষুণ্ণ। Frame-accurate human-verified captions দাবি করা হচ্ছে না।
- Measured captioned mix: {metrics['ebarki-captioned.mp4']['loudness']['input_i']} LUFS, {metrics['ebarki-captioned.mp4']['loudness']['input_tp']} dBTP, LRA {metrics['ebarki-captioned.mp4']['loudness']['input_lra']} LU। Female synthetic narration; original procedural music। Voice performance-এর subjective professional sign-off বাকি।
- এই production session-এ core suite: ১৮৪ backend + ২৭ web = ২১১ tests pass; ৭ backend warnings। এটি film-এর প্রতিটি control বা production release-এর certification নয়।

## বাস্তব demo ও সীমা

আলাদা localhost database/vault-এ fictional records, real app এবং configured real provider calls ব্যবহার করা হয়েছে। Summary, image reading, audio transcription, reply generation, payment reconciliation, PDF download, comment, reminder ও admin notice-এর receipts রাখা আছে। Reply output-এ buyer/seller wording অসংগত হওয়ায় UI-তে ব্যবহারকারীর সংশোধন করে Save my wording করা হয়েছে; সংশোধিত অংশকে untouched AI output বলা হয়নি।

Community-তে নতুন public post unavailable; seeded fictional discussion দেখানো হয়েছে। Merchant lookup-এ empty state; invented risk verdict নেই। কোনো official submission, refund, provider resolution বা legal win দাবি নেই। Privacy/security diagram design ব্যাখ্যা করে; deployed isolation, scale বা qualified legal approval certify করে না।

{counts['Verified in final render']}টি family-তে প্রতিনিধিত্বমূলক দৃশ্য আছে; {counts['Not planned']}টি family-র পৃথক দৃশ্য নেই। Combined main+appendix-ও every-feature acceptance পূরণ করে না। বিশেষত registration/logout, dictation, redaction/deletion, cancellation/recovery, সব export, role mutation, moderation mutation ও source-release lifecycle সম্পূর্ণ দেখানো হয়নি। Workspace search capture selector timeout হয়েছিল; সেই ব্যর্থতা manifest-এ রাখা আছে এবং সফল প্রদর্শন বলে গণনা করা হয়নি।

চার মিনিটের readable story ও exhaustive control walkthrough-এর মধ্যে প্রস্তাবিত সমঝোতা: এই main film, পৃথক supporting reel এবং auditable coverage matrix। প্রকাশের আগে সম্পূর্ণ ভিডিও শুনে/দেখে voice pronunciation, subjective pacing ও caption onset review বাকি। বর্তমান artifact একটি technically checked review cut; world-class quality বা complete coverage sign-off নয়।
'''
(ROOT/'QUALITY_REPORT.bn.md').write_text(qa,encoding='utf-8')

readme='''# Ebarki — The Missing Piece

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
'''
(ROOT/'README.bn.md').write_text(readme,encoding='utf-8')

for item in manifest.values():
    p=ROOT/'capture'/f"{item['name']}-end.png"
    if item['status']=='CAPTURED' and p.exists():
        (ROOT/'public/stills').mkdir(exist_ok=True)
        shutil.copy2(p,ROOT/'public/stills'/p.name)
for name in ['ebarki.en.srt','ebarki.en.vtt','words.json']:
    shutil.copy2(ROOT/'captions'/name,OUT/name)
if len(sys.argv)>1 and sys.argv[1]=='package':
    archive=OUT/'ebarki-editable-source.zip'
    candidates=[p for p in ROOT.iterdir() if p.is_file() and p.suffix in {'.py','.mjs','.tsx','.json','.md','.txt'}]
    for folder in ['assets','captions','public/fonts','public/clips','public/stills','audio','qa']:
        candidates.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix!='.log')
    candidates.extend(p for p in (ROOT/'capture').glob('*-end.png'))
    candidates.extend(p for p in (ROOT/'capture').glob('*.pdf'))
    sensitive=[]
    for p in candidates:
        if p.suffix in {'.json','.txt','.md','.py','.mjs','.tsx'}:
            t=p.read_text(encoding='utf-8',errors='replace')
            if re.search(r'(?:gsk_[A-Za-z0-9]{20,}|sk-proj-[A-Za-z0-9_-]{20,}|eyJ[A-Za-z0-9_-]{30,}\.eyJ)',t):sensitive.append(p.name)
    if sensitive:raise RuntimeError('Potential secret in package: '+', '.join(sensitive))
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for p in sorted(set(candidates)):z.write(p,'ebarki-film/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(OUT/'ebarki-captions.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in (ROOT/'captions').iterdir():
            if p.is_file():z.write(p,p.name)
    checksums={p.name:hashlib.file_digest(p.open('rb'),'sha256').hexdigest() for p in OUT.iterdir() if p.is_file() and p.suffix in {'.mp4','.zip','.srt','.vtt','.json'}}
    (OUT/'SHA256SUMS.json').write_text(json.dumps(checksums,indent=2),encoding='utf-8')
print(json.dumps({'coverage':dict(counts),'package_requested':len(sys.argv)>1},ensure_ascii=False))
