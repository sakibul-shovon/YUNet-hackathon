"""Source-grounded inventory; capture and render verification are separate gates."""
import json
import re
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
groups=[
('প্রবেশ ও নেভিগেশন','public/user','নিজের কাজ শুরু করা ও খুঁজে পাওয়া','নেই','04,05,13','apps/web/src/features/agent/Access.tsx',[
 'ল্যান্ডিং hero ও CTA','fictional payment illustration/reset','evidence/change/reply landing illustrations','FAQ expand/collapse','guest start','registration','consumer login/password visibility','logout','consumer judge workspace','admin login','judge admin evaluation entry','workspace case list/counts','case search/status filter','command palette/global actions','sidebar/navigation','Bangla/English locale switch','light/dark/system preference','help/how-it-works/privacy/limitations/technology/source pages']),
('কেস ও সম্মতি','user','বিক্ষিপ্ত বক্তব্যকে ব্যক্তিগত কেসে রাখা','সারাংশে configurable model; intake manual','05,06','apps/web/src/features/workspace/Cases.tsx',[
 'three-step narrative/context/review intake','Bangla/English/Banglish narrative','optional incident date/merchant/request','multiple evidence selection/remove','case storage consent','optional external AI consent','browser speech dictation','case title/story/context edit','guest-to-account continuity','consent withdrawal','case deletion request/status']),
('নথি ও গুরুত্বপূর্ণ তথ্য','user','কোন বক্তব্যের কী উৎস তা দেখা','vision/audio configurable; parser/links deterministic','07,08,09','apps/web/src/features/workspace/Evidence.tsx',[
 'PDF/image/audio upload and validation','20MB limit/duplicate handling','private original download/preview','native PDF text/page coordinates','scanned/hybrid PDF vision reading','image OCR/approximate boxes','audio transcription/timestamped segments','audio playback/waveform','manual transcript alternative','paste attributed message source','source-linked chronology','moment filters/review state','confirm/correct date/exclude/reopen moment','fact-source links/page/quote/region','image region selection/redacted copy','evidence delete/derived reading cleanup','payment linked-receipt reconciliation','second sample receipt addition','fact accept/correct/uncertain/reject','manual typed fact addition','Bangla digit/date/poisha normalization']),
('AI ও কাজের ধাপ','user','সিস্টেম কী করেছে তা বোঝা','Groq summary/chat/reply; stages mix of model and rules','06,09,11,17','apps/web/src/features/agent/AgentWorkspace.tsx',[
 'consent-scoped situation summary','original-account fallback','contextual copilot/general guidance','reply preparation from seller message','reply edit/save/reopen','run plan/real stage receipts/duration','SSE updates/polling recovery','cancel at checkpoints','run history/replay','reuse readings by evidence ID/hash','auto-follow canvas/manual pin']),
('পথ ও প্রস্তুতি','user','শর্ত বুঝে নিজের পরবর্তী কাজ প্রস্তুত করা','policy/templates deterministic; no win prediction','10,12,18','apps/web/src/features/workspace/Paths.tsx',[
 'conditional procedural routes/trace','reference lookup/exact citation navigation','next-best question answer/skip','unknown fact propagation','what-if presets/custom values/compare','version-guarded what-if adoption','issue add/confirm/reject','issue split/merge','multi-domain packs','action prerequisites/next preparation','document purpose/language selection','editable sentence attribution','saved document versions','PDF/HTML/Markdown/evidence ZIP export','evidence index/original inclusion choice','reviewed export/current-version guard','filing handoff/review/copy fields','official destination links/needs-recheck flags','activity timeline','user-reported seller/provider/external update','reported resolution flag','Bangladesh-time personal reminders/add/cancel']),
('কমিউনিটি ও merchant','community/user','অভিজ্ঞতা থেকে প্রেক্ষাপট পাওয়া','AI নয়; seed/in-memory records','14','apps/web/src/features/workspace/Community.tsx',[
 'community feed/category filter','open discussion/read comments','add public comment','similar-experience reaction','new public post composer (disabled/503)','private-case CTA/privacy guidance','merchant name lookup','merchant report counts/details','merchant radar seed/empty state']),
('অ্যাডমিন','admin/reviewer/publisher','পরিবর্তন ও পর্যালোচনার জবাবদিহি','administrative controls, no claimed admin AI','15,16,18','apps/web/src/features/workspace/Admin.tsx',[
 'role-filtered panes','overview metrics','record inspect/filter/refresh','case list/status override/reason','people roles/restrict/restore','merchant review override','post pin/unpin/hide/unhide/dismiss reports','notice create/edit/disable','audit action receipts','source candidate list/diff','official source watcher check','manual source import','source review scope/decision/rationale','release build','release promote/disable','release rollback','flag impacted cases']),
('কারিগরি ও পরীক্ষামূলক','technical/user','ব্যক্তিগত data ও কাজের consistency','মডেল/নিয়ম আলাদা','16,17,18','services/backend/app/main.py',[
 'Next.js/React/next-intl frontend','same-origin API BFF','FastAPI/Pydantic API','SQLAlchemy owner-scoped local persistence','private local evidence vault','session cookies/JWT/revocation/CSRF/origin checks','role enforcement','optimistic case/document versions','public reference/private case separation','source governance/versioned release','jobs/outbox/watcher interfaces','eight isolated scenarios/launch/reset','legacy multimodal compatibility endpoints','optional Gemini reader/dense adapter','health/readiness checks','reduced motion/focus/responsive controls'])
]
rows=[]
for group,role,problem,ai,scenes,source,names in groups:
 for name in names:
  state='আংশিক—কোডে আছে; সব browser action পুনঃপরীক্ষিত নয়'
  if any(x in name for x in ['disabled/503','optional Gemini','browser speech','jobs/outbox','legacy multimodal']):state='আংশিক/অনুপলব্ধ—সীমা দেখাতে হবে'
  if any(x in name for x in ['illustration','eight isolated','judge workspace','seed']):state='নমুনা—কাল্পনিক input; live production ফল নয়'
  rows.append(dict(id=f'F{len(rows)+1:03}',feature=name,group=group,user_problem=problem,user_role=role,ai_involvement=ai,implementation_status=state,source=source,demo_opportunity='আসল control ও প্রয়োজনীয় ফল inspect; শুধু উপস্থিতিকে success নয়',narrative_connection=scenes,priority='hero' if group in ['নথি ও গুরুত্বপূর্ণ তথ্য','AI ও কাজের ধাপ'] else 'supporting/montage',storyboard_scene=scenes,planned_visual='সংশ্লিষ্ট বাস্তব UI; technical হলে source-grounded animation',demonstration_method='browser capture / source diagram',estimated_screen_time='দৃশ্যের মধ্যে shared; নির্দিষ্ট allocation edit-এর পর',coverage_status='Planned',verification_evidence=None))
(ROOT/'feature-coverage.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
out=['# Feature inventory ও coverage matrix','',f'{len(rows)}টি capability/control family। এটি source inventory; সবগুলো runtime বা final-film verified নয়। প্রতিটি granular UI label নিচের control-index-এ রয়েছে।', '', '| ID | Feature | Role | AI | Implementation | Scene | Priority | Coverage |','|---|---|---|---|---|---|---|---|']
for r in rows:out.append('| '+' | '.join(str(r[k]).replace('|','/') for k in ['id','feature','user_role','ai_involvement','implementation_status','storyboard_scene','priority','coverage_status'])+' |')
out+=['','প্রতি feature-এর user problem, source, demo opportunity, narrative connection, planned visual, method, screen-time allocation ও verification-evidence field machine-readable JSON-এ আছে। Planned কোনো success verdict নয়। Captured → Edited → Verified in final render আলাদাভাবে প্রমাণ পেলে বদলাবে।']
(ROOT/'FEATURE_INVENTORY.bn.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
controls=[]
for folder in ['agent','workspace','landing']:
 for p in sorted((REPO/'apps/web/src/features'/folder).rglob('*.tsx')):
  t=p.read_text(encoding='utf-8')
  for m in re.finditer(r"words\(locale,\s*'([^'\n]+)'",t):
   controls.append({'source':p.relative_to(REPO).as_posix(),'line':t[:m.start()].count('\n')+1,'english_copy':m.group(1),'runtime_verified':False,'coverage':'Not planned'})
(ROOT/'qa'/'control-index.json').write_text(json.dumps(controls,ensure_ascii=False,indent=2),encoding='utf-8')
with urllib.request.urlopen('http://127.0.0.1:8002/openapi.json') as response:schema=json.load(response)
api=[]
for route, methods in schema['paths'].items():
 if route.startswith('/api/'):continue
 for method,item in methods.items():
  if method in ['get','post','put','patch','delete']:
   api.append({'method':method.upper(),'path':route,'summary':item.get('summary'),'tags':item.get('tags'),'runtime_verified':False})
(ROOT/'qa'/'api-inventory.json').write_text(json.dumps(api,ensure_ascii=False,indent=2),encoding='utf-8')
pages=[p.relative_to(REPO).as_posix() for p in (REPO/'apps/web/src/app').rglob('page.tsx')]
(ROOT/'qa'/'page-inventory.json').write_text(json.dumps(pages,indent=2),encoding='utf-8')
scenes=json.loads((ROOT/'scenes.json').read_text(encoding='utf-8'))
story=['# Time-coded storyboard ও shot list','','Voiceover ইংরেজি; নিচের সব timing provisional editorial target। final audio alignment ছাড়া subtitle timing নয়।','', '| Scene / time | Visual ও narrative objective | Voiceover | Camera / transition | Assets / sound |','|---|---|---|---|---|']
for s in scenes:
 tm=lambda n:f'{n//60:02}:{n%60:02}'
 story.append(f"| {s['id']} · {tm(s['start'])}–{tm(s['end'])} | {s['visual_bn']} | {s['voice']} | {'বাস্তব interaction, gentle push-in, matched document edge cut' if s['kind']=='ui' else 'progressive vector composition; eased movement'} | {s.get('clip',s['kind'])}; {s['sound']} |")
story+=['','সব দৃশ্যে subtitle lower safe area; UI-এর প্রয়োজনীয় control ঢাকলে screenshot frame উপরে। captions ২ লাইনের মধ্যে; title upper margin। Voice শুরুতে ০.৫–১ সেকেন্ড visual lead, শেষে natural pause; actual measured voice length অনুযায়ী সমন্বয়।','', '## পৃথক shot list','']
for s in scenes:
 story.append(f"- S{s['id']}A — {s['title']}: establishing frame; S{s['id']}B — source/result detail; S{s['id']}C — next scene-এর document/line match cut।")
(ROOT/'STORYBOARD.bn.md').write_text('\n'.join(story)+'\n',encoding='utf-8')
(ROOT/'VOICEOVER.en.txt').write_text('\n\n'.join(s['voice'] for s in scenes)+'\n',encoding='utf-8')
print(json.dumps({'feature_families':len(rows),'localized_copy_entries':len(controls),'canonical_api_operations':len(api),'pages':len(pages),'storyboard_scenes':len(scenes),'voice_words':sum(len(s['voice'].split()) for s in scenes)}))
