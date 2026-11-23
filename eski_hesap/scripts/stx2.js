const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [title,dir,email,...files]=process.argv.slice(2);
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1300,height:1300}});
p.on('requestfailed',r=>console.log('RF',r.url().slice(0,150),r.failure().errorText));p.on('response',r=>{if(r.status()>=400)console.log('RS',r.status(),r.url().slice(0,150))});
const shot=n=>p.screenshot({path:`${dir}/${n}.png`});
await p.goto('https://www.swisstransfer.com/en',{waitUntil:'networkidle',timeout:60000});
await p.getByRole('button',{name:'I agree'}).click().catch(()=>{}); await p.waitForTimeout(1500);
await p.locator('input[type=file]').first().setInputFiles(files); await p.waitForTimeout(3000);
await p.getByRole('button',{name:'Link',exact:true}).click(); await p.waitForTimeout(800);
await p.getByPlaceholder('Title (optional)').fill(title).catch(()=>{});
await p.getByPlaceholder(/email/i).first().fill(email).catch(e=>console.log('EMAILERR',e.message));
const tr=p.getByLabel('Transfer availability'); const tb=await tr.boundingBox(); await p.mouse.click(tb.x+tb.width/2,tb.y+tb.height/2); await p.waitForTimeout(1000);
const want=(process.env.DAYS||'30')+' days'; const ob=await p.getByRole('option',{name:want}).boundingBox(); await p.mouse.move(ob.x+20,ob.y+ob.height/2); await p.waitForTimeout(300); await p.mouse.down(); await p.waitForTimeout(100); await p.mouse.up(); await p.waitForTimeout(1200);
console.log('AVAIL', await tr.innerText());
await shot('form');
await p.getByRole('button',{name:'Transfer',exact:true}).click(); await p.waitForTimeout(6000); await shot('after');
console.log('BODY',(await p.innerText('body')).replace(/\s+/g,' ').slice(0,600));
const t0=Date.now(); let link=null,last='',coded=false;
while(Date.now()-t0<4*3600*1000){ await p.waitForTimeout(10000);
  const body=(await p.innerText('body')).replace(/\s+/g,' ');
  if(!coded && fs.existsSync(dir+'/code.txt')){const c=fs.readFileSync(dir+'/code.txt','utf8').trim();
     const ins=p.locator('input:visible'); const n=await ins.count(); console.log('INPUTS',n);
     if(n>=c.length){for(let i=0;i<c.length;i++) await ins.nth(i).fill(c[i]);} else {await ins.first().click(); await p.keyboard.type(c);}
     await p.waitForTimeout(1000); const btn=p.getByRole('button',{name:/confirm|validate|verify|continue|send/i}); if(await btn.count()) await btn.first().click().catch(()=>{});
     coded=true; await p.waitForTimeout(5000); await shot('coded'); console.log('CODED',(await p.innerText('body')).replace(/\s+/g,' ').slice(0,400)); continue;}
  const m=body.match(/https:\/\/www\.swisstransfer\.com\/d\/[A-Za-z0-9-]+/)||(await p.$$eval('input',e=>e.map(x=>x.value))).join(' ').match(/https:\/\/www\.swisstransfer\.com\/d\/[A-Za-z0-9-]+/);
  if(m){link=m[0];break;}
  const pr=body.replace(/100% renewable/g,'').match(/\d+(\.\d+)?\s?%[^.]{0,50}/); const s=pr?pr[0]:body.slice(0,160);
  if(s!==last){console.log('STATE',Math.round((Date.now()-t0)/1000)+'s',s);last=s;}
  if(Math.round((Date.now()-t0)/1000)%600<11) await shot('prog');
}
console.log('LINK',link); await shot('final'); await b.close();})();
