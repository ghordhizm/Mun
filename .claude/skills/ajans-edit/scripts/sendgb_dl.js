const {chromium}=require('playwright');
(async()=>{const [url,outdir]=process.argv.slice(2);
const b=await chromium.launch();const ctx=await b.newContext({acceptDownloads:true});const p=await ctx.newPage();
await p.goto(url,{waitUntil:'networkidle',timeout:60000}).catch(()=>{});
await p.waitForTimeout(3000);
const [dl]=await Promise.all([p.waitForEvent('download',{timeout:120000}), p.getByText('Download All',{exact:true}).first().click()]);
console.log('URL',dl.url().slice(0,120)); const name=dl.suggestedFilename(); await dl.saveAs(outdir+'/'+name); console.log('SAVED',name);
await b.close();})().catch(e=>{console.log('ERR',e.message);process.exit(1)});
