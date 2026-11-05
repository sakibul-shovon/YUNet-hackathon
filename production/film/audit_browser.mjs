import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const base='http://localhost:3002';
await fs.mkdir(path.join(root,'capture'),{recursive:true});
await fs.mkdir(path.join(root,'qa'),{recursive:true});
const browser=await chromium.launch({channel:'msedge',headless:true});
const context=await browser.newContext({viewport:{width:1600,height:900},colorScheme:'light'});
await context.addInitScript(()=>{localStorage.setItem('theme','light');localStorage.setItem('ebarki_theme','light')});
const page=await context.newPage();
const errors=[];const responses=[];
page.on('pageerror',e=>errors.push(String(e)));
page.on('response',r=>{if(r.url().includes('/api/')&&r.status()>=400)responses.push({url:r.url(),status:r.status()})});
const results=[];
async function snap(name){await page.waitForTimeout(1800);await page.screenshot({path:path.join(root,'capture',name+'.png')});const text=await page.locator('body').innerText();results.push({name,url:page.url(),text});console.log(name+'\n'+text.slice(0,6500));}
try{
await page.goto(base+'/en',{waitUntil:'networkidle',timeout:90000});
await snap('landing');
await page.getByRole('button',{name:/Judge demo/i}).first().click();
await page.waitForURL(/\/cases\//,{timeout:90000});
await page.waitForTimeout(15000);
await snap('judge-workspace');
await context.storageState({path:path.join(root,'tmp','consumer-session.json')});
await fs.writeFile(path.join(root,'tmp','case-url.txt'),page.url());
for(const view of ['timeline','whatif','reply','draft','paths','review','evidence','activity','handoff']){
 const u=new URL(page.url());u.search='?view='+view;
 await page.goto(u.href,{waitUntil:'networkidle'});await snap('case-'+view);
}
for(const route of ['/bn/cases/'+new URL(page.url()).pathname.split('/').at(-1),'/en/community','/en/merchants','/en/scenarios','/en/settings']){
 await page.goto(base+route,{waitUntil:'networkidle'});await snap(route.replaceAll('/','-'));
}
}finally{
await fs.writeFile(path.join(root,'qa','browser-discovery.json'),JSON.stringify({results,errors,responses},null,2));
await browser.close();
}
