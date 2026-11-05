import {chromium} from 'playwright';import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));const b=await chromium.launch({channel:'msedge',headless:true});
const c=await b.newContext({storageState:root+'/tmp/consumer-session.json'});const u=new URL(await fs.readFile(root+'/tmp/case-url.txt','utf8'));const id=u.pathname.split('/').at(-1);
const r=await c.request.get(`http://localhost:3002/api/v1/cases/${id}/runs`);const d=await r.json();
await fs.writeFile(root+'/qa/run-receipts.json',JSON.stringify(d,null,2));console.log(JSON.stringify(d).slice(0,12000));await b.close();
