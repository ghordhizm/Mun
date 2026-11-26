const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1300,height:1000}});
await p.goto('https://www.swisstransfer.com/en',{waitUntil:'networkidle',timeout:60000});
await p.waitForTimeout(2000);
// dismiss cookie banners if any
for (const t of ['Accept','Kabul','Tümünü kabul et','Accept all','OK']) { const l=p.getByRole('button',{name:t}); if(await l.count()) {await l.first().click().catch(()=>{});} }
console.log('INPUTS',JSON.stringify(await p.$$eval('input',e=>e.map(x=>({t:x.type,n:x.name,id:x.id,ph:x.placeholder,m:x.multiple})))));
console.log('BTNS',JSON.stringify(await p.$$eval('button,[role=tab],[role=radio]',e=>e.map(x=>x.innerText.trim()).filter(Boolean).slice(0,40))));
await p.screenshot({path:process.argv[2]});await b.close();})();
