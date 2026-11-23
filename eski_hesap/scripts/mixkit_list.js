const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
for (const u of process.argv.slice(2)){
 await p.goto(u,{waitUntil:'networkidle',timeout:60000}).catch(()=>{}); await p.waitForTimeout(2500);
 for(let i=0;i<4;i++){await p.mouse.wheel(0,4000);await p.waitForTimeout(800);}
 const items=await p.$$eval('[data-audio-player-preview-url-value]',els=>els.map(e=>{const c=e.closest('.item-grid-card')||e.parentElement; const t=(c&&c.querySelector('.item-grid-card__title'))?c.querySelector('.item-grid-card__title').innerText.trim():''; const d=(c&&c.innerText.match(/\d+:\d\d/))||[''];return t+' | '+d[0]+' | '+e.getAttribute('data-audio-player-preview-url-value');}));
 console.log('##',u,items.length); console.log([...new Set(items)].join('\n'));}
await b.close();})();
