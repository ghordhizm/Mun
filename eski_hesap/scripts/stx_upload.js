const {chromium}=require('playwright');
(async()=>{const [title,shot,...files]=process.argv.slice(2);
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1300,height:1300}});
const fails=[],hosts=new Set();p.on('requestfailed',r=>{const u=r.url(); if(!/promotional|iconify|fonts\.storage|analytics|web-components/.test(u)) fails.push(u.slice(0,140)+' '+r.failure().errorText)});
p.on('request',r=>{try{hosts.add(new URL(r.url()).host)}catch(e){}});
await p.goto('https://www.swisstransfer.com/en',{waitUntil:'networkidle',timeout:60000});
await p.getByRole('button',{name:'I agree'}).click(); await p.waitForTimeout(1500);
await p.locator('input[type=file]').first().setInputFiles(files); await p.waitForTimeout(3000);
await p.getByRole('button',{name:'Link',exact:true}).click(); await p.waitForTimeout(800);
const cb=p.getByRole('combobox',{name:'Transfer availability'}); await cb.click(); await p.waitForTimeout(600);
const opts=await p.$$eval('[role=option]',e=>e.map(x=>x.innerText.trim())); console.log('OPTS',JSON.stringify(opts));
const o30=p.getByRole('option',{name:new RegExp(process.env.DAYS||'30')}); if(await o30.count()) await o30.first().click(); else await p.keyboard.press('Escape');
if(title) await p.getByPlaceholder('Title (optional)').fill(title).catch(()=>{});
await p.getByRole('button',{name:'Transfer',exact:true}).click();
const t0=Date.now(); let link=null, last='';
while(Date.now()-t0<3*3600*1000){ await p.waitForTimeout(15000); if(Math.round((Date.now()-t0)/1000)%300<16) await p.screenshot({path:shot});
  const body=(await p.innerText('body')).replace(/\s+/g,' ');
  const m=body.match(/https:\/\/www\.swisstransfer\.com\/d\/[A-Za-z0-9-]+/) || (await p.$$eval('input',e=>e.map(x=>x.value))).join(' ').match(/https:\/\/www\.swisstransfer\.com\/d\/[A-Za-z0-9-]+/);
  if(m){link=m[0];break;}
  const pr=body.replace(/100% renewable/g,"").match(/\d+(\.\d+)?\s?%[^.]{0,60}/); const s=pr?pr[0]:body.slice(0,200); if(s!==last){console.log('STATE',Math.round((Date.now()-t0)/1000)+'s',s);last=s;}
  if(/error|failed|hata/i.test(body.slice(0,600))) {console.log('ERRBODY',body.slice(0,600));}
  if(fails.length>20) break;
}
console.log('LINK',link); console.log('HOSTS',[...hosts].join(' ')); console.log('FAILS',fails.slice(0,10).join('\n'));
await p.screenshot({path:shot});await b.close();})();
