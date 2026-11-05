import {chromium} from 'playwright';import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));const scenes=JSON.parse(await fs.readFile(root+'/scenes.json','utf8'));
scenes.push(...JSON.parse(await fs.readFile(root+'/appendix.json','utf8')));
await fs.mkdir(root+'/tmp/backgrounds',{recursive:true});
const display=(await fs.readFile(root+'/public/fonts/display-latin.woff2')).toString('base64');
const text=(await fs.readFile(root+'/public/fonts/text-latin.woff2')).toString('base64');
const b=await chromium.launch({channel:'msedge',headless:true});const p=await b.newPage({viewport:{width:1920,height:1080}});
for(const s of scenes.filter(s=>s.kind==='ui')){
 await p.setContent(`<style>@font-face{font-family:Display;src:url(data:font/woff2;base64,${display})}@font-face{font-family:Text;src:url(data:font/woff2;base64,${text})}body{margin:0;background:#f7f5ef;color:#1c2b2c;font-family:Text}.grid{position:absolute;inset:0;background-image:linear-gradient(#bcc2b526 1px,transparent 1px);background-size:100% 160px}.title{position:absolute;left:140px;top:48px;font:500 36px Display;letter-spacing:-.7px}.index{position:absolute;right:140px;top:60px;font-size:13px;letter-spacing:3px;color:#61716f}.label{position:absolute;left:240px;top:106px;font-size:12px;letter-spacing:2px;color:#61716f}.frame{position:absolute;left:231px;top:132px;width:1458px;height:821px;background:white;border:1px solid #cdd1c9;box-sizing:border-box;box-shadow:0 24px 60px #23383219}</style><div class="grid"></div><div class="title">${s.title}</div><div class="index">EBARKI / ${s.id}</div><div class="label">ACTUAL LOCAL APPLICATION · FICTIONAL RECORDS · EDITED DEMONSTRATION</div><div class="frame"></div>`);
 await p.evaluate(()=>document.fonts.ready);await p.screenshot({path:root+'/tmp/backgrounds/'+s.id+'.png'});
}
await b.close();console.log('UI composition backgrounds prepared.');
