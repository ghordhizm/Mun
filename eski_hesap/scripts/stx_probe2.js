const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1300,height:1100}});
await p.goto('https://www.swisstransfer.com/en',{waitUntil:'networkidle',timeout:60000});
await p.getByRole('button',{name:'I agree'}).click(); await p.waitForTimeout(2500);
console.log('INPUTS',JSON.stringify(await p.$$eval('input,textarea',e=>e.map(x=>({t:x.type,n:x.name,ph:x.placeholder,m:x.multiple,acc:x.accept})))));
console.log('BTNS',JSON.stringify(await p.$$eval('button,[role=tab],[role=radio],label',e=>e.map(x=>x.innerText.trim()).filter(Boolean).slice(0,40))));
await p.screenshot({path:process.argv[2]});await b.close();})();
