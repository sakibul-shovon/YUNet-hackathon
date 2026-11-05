import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const root=path.dirname(fileURLToPath(import.meta.url));
const browser=await chromium.launch({channel:'msedge',headless:true});
const page=await browser.newPage({viewport:{width:1920,height:1080}});
async function sheet(folder,dest){
 const files=(await fs.readdir(folder)).filter(x=>x.endsWith('.png')).sort();
 const items=await Promise.all(files.map(async name=>`<div><img src="data:image/png;base64,${(await fs.readFile(path.join(folder,name))).toString('base64')}"><p>${name.replace('.png','')} seconds</p></div>`));
 await page.setContent(`<style>body{margin:0;background:#e2e5df;font:20px Arial;display:grid;grid-template-columns:repeat(3,640px)}div{height:390px}img{width:640px;height:360px}p{margin:3px 12px}</style>${items.join('')}`);
 await page.screenshot({path:dest,fullPage:true,type:'jpeg',quality:92});
}
await sheet(root+'/out/review-frames',root+'/out/contact-sheet-main.jpg');
await fs.mkdir(root+'/out/appendix-review',{recursive:true});
for(const s of JSON.parse(await fs.readFile(root+'/appendix.json','utf8'))){
 const sec=s.end-1;
 execFileSync('ffmpeg',['-y','-v','error','-ss',String(sec),'-i',root+'/out/ebarki-coverage-reel.mp4','-frames:v','1',root+'/out/appendix-review/'+String(sec).padStart(3,'0')+'.png']);
}
await sheet(root+'/out/appendix-review',root+'/out/contact-sheet-appendix.jpg');
await browser.close();
