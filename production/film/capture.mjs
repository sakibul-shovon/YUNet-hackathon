import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const root=path.dirname(fileURLToPath(import.meta.url));
const base='http://localhost:3002';
const caseURL=new URL(await fs.readFile(root+'/tmp/case-url.txt','utf8'));
const casePath=caseURL.pathname;
const browser=await chromium.launch({channel:'msedge',headless:true});
const clips=JSON.parse(await fs.readFile(root+'/qa/capture-manifest.json','utf8').catch(()=>'[]'));const receipts=JSON.parse(await fs.readFile(root+'/qa/capture-receipts.json','utf8').catch(()=>'[]'));
await fs.mkdir(root+'/capture/raw',{recursive:true});await fs.mkdir(root+'/public/clips',{recursive:true});
const pause=(p,ms=900)=>p.waitForTimeout(ms);
async function move(p,loc){await loc.scrollIntoViewIfNeeded();const r=await loc.boundingBox();await p.mouse.move(r.x+r.width/2,r.y+r.height/2,{steps:24});await pause(p,350);}
async function click(p,loc){await move(p,loc).catch(()=>{});await loc.click();await pause(p);}
async function scroll(p,y){await p.evaluate(y=>window.scrollBy({top:y,behavior:'smooth'}),y);await pause(p,1200);}
async function record(name,route,prepare,action,minimum=13,admin=false){
 console.log('CAPTURE',name);
 const c=await browser.newContext({viewport:{width:1600,height:900},colorScheme:'light',storageState:root+'/tmp/'+(admin?'admin':'consumer')+'-session.json',recordVideo:{dir:root+'/capture/raw',size:{width:1600,height:900}},acceptDownloads:true});
 await c.addInitScript(()=>{localStorage.setItem('ebarki_theme','light');localStorage.setItem('theme','light');});
 const p=await c.newPage();p.setDefaultTimeout(25000);let started=null;let failure=null;
 const errors=[];p.on('pageerror',e=>errors.push(String(e)));
 p.on('response',async r=>{if(r.url().includes('/api/v1/')&&!r.url().includes('/auth/')){
   if(r.request().method()!=='GET'||/runs|reconciliation|reply-preparations/.test(r.url())){
    let data;try{data=await r.json()}catch{};receipts.push({clip:name,url:r.url(),method:r.request().method(),status:r.status(),data});
   }
 }});
 try{
  await p.goto(base+route,{waitUntil:'domcontentloaded',timeout:90000});await p.waitForTimeout(2400);
  await p.addStyleTag({content:'nextjs-portal{display:none!important}'});
  if(prepare)await prepare(p);
  await p.evaluate(()=>{
   const cursor=document.createElement('div');cursor.id='film-cursor';cursor.style.cssText='position:fixed;left:-50px;top:-50px;z-index:2147483647;pointer-events:none;width:24px;height:30px;filter:drop-shadow(0 2px 2px #0005)';
   cursor.innerHTML='<svg viewBox="0 0 24 30"><path d="M2 2 L2 23 L8 18 L13 28 L18 25 L13 16 L22 16 Z" fill="#192f32" stroke="white" stroke-width="2"/></svg>';
   document.body.appendChild(cursor);document.addEventListener('mousemove',e=>{cursor.style.left=e.clientX+'px';cursor.style.top=e.clientY+'px'});
  });
  await pause(p,700);started=Date.now();
  await p.screenshot({path:root+'/capture/'+name+'-start.png'});
  await action(p);
  await pause(p,Math.max(800,minimum*1000-(Date.now()-started)));
  await p.screenshot({path:root+'/capture/'+name+'-end.png'});
  await fs.writeFile(root+'/capture/'+name+'.txt',await p.locator('body').innerText());
 }catch(e){failure=String(e);console.log('CAPTURE_FAILED',name,failure.slice(0,400));await p.screenshot({path:root+'/capture/'+name+'-failure.png'}).catch(()=>{});}
 const duration=started?(Date.now()-started)/1000:0;const video=p.video();await c.close();const raw=await video.path();
 const total=Number(execFileSync('ffprobe',['-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',raw],{encoding:'utf8'}).trim());
 const offset=Math.max(0,total-duration-.08);
 if(!failure)execFileSync('ffmpeg',['-y','-ss',String(offset),'-i',raw,'-t',String(duration),'-an','-r','30','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p',root+'/public/clips/'+name+'.mp4'],{stdio:'ignore'});
 const previous=clips.findIndex(x=>x.name===name);if(previous>=0)clips.splice(previous,1);
 clips.push({name,route,duration,raw:path.basename(raw),trim_start:offset,status:failure?'FAILED':'CAPTURED',failure,errors});
 await fs.writeFile(root+'/qa/capture-manifest.json',JSON.stringify(clips,null,2));
 await fs.writeFile(root+'/qa/capture-receipts.json',JSON.stringify(receipts,null,2));
}
const only=new Set(process.argv.slice(2));
const job=async(name,...args)=>{if(!only.size||only.has(name))await record(name,...args)};
const canvas=async p=>{await p.locator('.ag-canvas').scrollIntoViewIfNeeded().catch(()=>{});await scroll(p,170)};
try{
await job('landing','/en',null,async p=>{await pause(p,1800);await scroll(p,570);await pause(p,1300);await scroll(p,650);});
await job('intake','/en/cases/new',async p=>{await p.waitForLoadState('networkidle');await pause(p,3500)},async p=>{
 const story=p.getByPlaceholder('I ordered a phone, paid in advance, and…');
 const narrative='I paid BDT 5,500 to Sample Electronics for a phone on 24 October 2026. Delivery was promised by 26 October. It has not arrived. Fictional demonstration only.';
 await story.fill(narrative);await pause(p,1400);if(await story.inputValue()!==narrative)await story.fill(narrative);
 await p.getByRole('button',{name:'Continue',exact:true}).click();await pause(p,1700);
 await p.getByRole('button',{name:'Review',exact:true}).waitFor();await click(p,p.getByRole('button',{name:'Review',exact:true}));await pause(p,2000);
});
await job('briefing',casePath+'?view=briefing',canvas,async p=>{await pause(p,1800);await click(p,p.getByText('Execution detail',{exact:true}).first());await scroll(p,380);});
await job('source',casePath+'?view=timeline',async p=>{await p.getByText('MOMENTS & SOURCES',{exact:true}).scrollIntoViewIfNeeded()},async p=>{
 await pause(p,1700);await click(p,p.getByRole('button',{name:/A promise to review/}).first());await pause(p,1500);await click(p,p.getByRole('button',{name:'This looks right',exact:true}));await scroll(p,190);
});
await job('reconcile',casePath+'?view=briefing',canvas,async p=>{
 await pause(p,1700);await click(p,p.getByRole('button',{name:'Add the sample second payment',exact:true}));await p.getByText('BDT 5,500',{exact:false}).first().waitFor().catch(()=>{});await pause(p,7000);await click(p,p.getByRole('button',{name:'Briefing',exact:true}));await scroll(p,330);
},18);
await job('whatif',casePath+'?view=whatif',canvas,async p=>{await click(p,p.getByRole('button',{name:'Preview the effect',exact:true}));await pause(p,1200);await scroll(p,450)});
await job('reply',casePath+'?view=reply',canvas,async p=>{
 await p.getByPlaceholder('Paste the actual response here…').fill('FICTIONAL SELLER MESSAGE, 5 November 2026. Please send both payment references so we can review your phone order and provide an update.');
 await click(p,p.getByRole('button',{name:'Save message & prepare reply',exact:true}));
 await p.locator('.ex-reply-paper').waitFor({timeout:60000});await p.getByRole('textbox',{name:'Edit your reply',exact:true}).scrollIntoViewIfNeeded();await pause(p,1300);
 await p.getByRole('textbox',{name:'Edit your reply',exact:true}).fill('Thank you for responding. My payment references are SAMPLE-001 for BDT 5,000 and SAMPLE-002 for BDT 500, both dated 24 October 2026. Please review these records and provide an update on the phone promised by 26 October. If delivery cannot be completed, please explain the next steps for reviewing my refund request.');
 await click(p,p.getByRole('button',{name:'Save my wording',exact:true}));await pause(p,2200);
},19);
await job('draft',casePath+'?view=draft',canvas,async p=>{
 await pause(p,1400);await scroll(p,320);await click(p,p.getByRole('button',{name:'Review & export',exact:true}));await pause(p,1300);
 const modal=p.getByRole('dialog');await modal.getByRole('checkbox').last().check();
 const download=p.waitForEvent('download');await click(p,p.getByRole('button',{name:'Download preparation materials',exact:true}));
 const d=await download;await d.saveAs(root+'/capture/prepared-case.pdf');await pause(p,1400);
},16);
await job('bangla',casePath+'?view=briefing',canvas,async p=>{
 await click(p,p.getByRole('link',{name:'বাংলা',exact:true}));await pause(p,2000);await scroll(p,420);
});
await job('community','/en/community',null,async p=>{
 await click(p,p.getByRole('button',{name:'Online shopping',exact:true}));await pause(p,900);await click(p,p.getByRole('button',{name:/Discussion/}));await pause(p,1800);
 await p.getByRole('dialog').getByRole('textbox').first().fill('Demo participant');
 await p.getByRole('dialog').getByRole('textbox').last().fill('Fictional demo: keeping both receipts together made the payment total easier to explain.');
 await click(p,p.getByRole('button',{name:'Publish comment',exact:true}));await pause(p,1300);
},17);
await job('media',casePath+'?view=timeline',async p=>{await p.getByRole('button',{name:/fictional-seller-messages.png/}).first().scrollIntoViewIfNeeded()},async p=>{
 await click(p,p.getByRole('button',{name:/fictional-seller-messages.png/}).first());await p.locator('.ex-source').evaluate(el=>el.scrollIntoView({behavior:'smooth',block:'start'}));await scroll(p,-100);await pause(p,2000);
 await click(p,p.getByRole('button',{name:/fictional-account.wav/}).first());await p.locator('.ex-source').evaluate(el=>el.scrollIntoView({behavior:'smooth',block:'start'}));await scroll(p,-100);await click(p,p.locator('.ex-audio-segments button').first());await pause(p,2400);
},17);
await job('handoff',casePath+'?view=handoff',canvas,async p=>{await scroll(p,430);await p.getByRole('checkbox').first().check();await pause(p,1600);await scroll(p,370)},9);
await job('workspace','/en/cases',null,async p=>{await p.getByRole('textbox',{name:'Search your cases'}).fill('phone');await pause(p,1800);await p.getByRole('textbox',{name:'Search your cases'}).fill('');await scroll(p,250)},12);
await job('settings','/en/settings',null,async p=>{await pause(p,1500);await scroll(p,480);await p.getByRole('combobox').last().selectOption({label:'An undelivered phone. One payment discrepancy.'});await pause(p,2500)},12);
await job('scenarios','/en/scenarios',null,async p=>{await p.getByText('Read the sample story',{exact:true}).first().click();await pause(p,2200);await scroll(p,520);await pause(p,1800);await scroll(p,450)},14);
await job('facts',casePath+'?view=review',canvas,async p=>{await scroll(p,370);await pause(p,1800);await click(p,p.getByRole('button',{name:'Add information',exact:true}));await pause(p,2600)},13);
await job('paths',casePath+'?view=paths',canvas,async p=>{await scroll(p,420);await pause(p,1800);await p.getByText('Why this path?',{exact:true}).first().click();await pause(p,1900);await scroll(p,360)},14);
await job('activity',casePath+'?view=activity',canvas,async p=>{await click(p,p.getByRole('button',{name:'Add reminder',exact:true}));await p.getByRole('dialog').getByRole('textbox').first().fill('Review seller response — fictional demo');await p.locator('input[type=datetime-local]').fill('2026-11-10T10:00');await click(p,p.getByRole('button',{name:'Save follow-up',exact:true}));await pause(p,1800);await click(p,p.getByRole('button',{name:'Record an update',exact:true}));await pause(p,2200)},16);
await job('originals',casePath+'?view=evidence',canvas,async p=>{await p.getByText('fictional-seller-messages.png',{exact:true}).first().click();await scroll(p,350);await pause(p,2200);await click(p,p.getByRole('button',{name:'Link to a fact',exact:true}));await pause(p,2400)},14);
await job('merchant','/en/merchants',null,async p=>{await p.getByRole('textbox').fill('Sample Electronics');await click(p,p.getByRole('button',{name:'Look up',exact:true}));await pause(p,2500)},10);
await job('reference','/en/sources',null,async p=>{await pause(p,1800);await scroll(p,500);await pause(p,1800);await scroll(p,400)},12);
await job('help','/en/help',null,async p=>{await pause(p,1800);await scroll(p,500);await pause(p,1800)},10);
await job('admin-actions','/en/admin',null,async p=>{
 await click(p,p.getByRole('button',{name:'Notices',exact:true}));await click(p,p.getByRole('button',{name:'Create notice',exact:true}));
 const modal=p.getByRole('dialog');const inputs=modal.locator('input[type=text]');await inputs.nth(0).fill('কাল্পনিক প্রদর্শনী');await inputs.nth(1).fill('Fictional demonstration');await modal.locator('textarea').fill('Sample notice for the isolated film workspace. No real consumer warning.');await modal.getByRole('checkbox').last().check();await click(p,p.getByRole('button',{name:'Confirm change',exact:true}));await pause(p,1200);await p.keyboard.press('Escape');
 const close=p.getByRole('button',{name:/Close/});if(await close.count())await close.last().click();
 await click(p,p.getByRole('button',{name:'Audit trail',exact:true}));await pause(p,2500);
},20,true);
// Separate genuine administrator session; no existing personal database is accessed.
if(!only.size||only.has('admin')){
 const c=await browser.newContext();const p=await c.newPage();await p.goto(base+'/en/admin/login',{waitUntil:'networkidle'});
 await p.getByRole('button',{name:/Judge Admin/}).click();await p.waitForURL(/\/en\/admin$/,{timeout:60000});await pause(p,1200);
 await c.storageState({path:root+'/tmp/admin-session.json'});await c.close();
 await job('admin','/en/admin',null,async p=>{
  for(const pane of ['Cases','People & access','Merchants','Moderation','Notices','Audit trail','Source review','Knowledge release']){
   await click(p,p.getByRole('button',{name:pane,exact:true}));await pause(p,700);
  }
 },18,true);
}
}finally{await browser.close()}
