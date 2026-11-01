import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const base=process.env.PREVIEW_URL||'http://127.0.0.1:3001',dir=process.env.QA_DIR||'.output/library-dedup';await mkdir(dir,{recursive:true});
const browser=await chromium.launch({args:['--no-sandbox']});
try{
 const context=await browser.newContext({acceptDownloads:true,viewport:{width:1440,height:1100}}),page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const items=await(await context.request.get(base+'/resources.json')).json(),courses=await(await context.request.get(base+'/courses.json')).json();assert.equal(items.length,55);
 const expected=items.flatMap(r=>r.downloads||[{url:r.url}]).map(f=>f.url);assert.equal(expected.length,91);assert.equal(new Set(expected).size,91);
 await page.goto(base+'/library.html');await page.locator('#hub-search[data-search-bound=true]').waitFor();
 assert.equal(await page.locator('.resource-card').count(),55);assert.equal(await page.locator('.library-downloads a').count(),91);
 const titles=await page.locator('.resource-card h3').allTextContents();assert.equal(new Set(titles).size,55);
 assert.deepEqual((await page.locator('.library-downloads a').evaluateAll(es=>es.map(e=>e.getAttribute('href')))).sort(),expected.slice().sort());
 for(const c of courses){const card=page.locator('.resource-card').filter({has:page.getByRole('heading',{name:c.title,exact:true})});assert.equal(await card.count(),1);assert.equal(await card.locator('.library-downloads a').count(),2)}
 const hashes=new Set();let done=0;
 for(let start=0;start<expected.length;start+=6){
  const results=await Promise.all(expected.slice(start,start+6).map(async url=>{const r=await context.request.get(base+url);assert.equal(r.status(),200,url);const bytes=await r.body();assert.ok(bytes.length>20,url);return createHash('sha256').update(bytes).digest('hex')}));
  for(const hash of results){assert.ok(!hashes.has(hash),'Identical download payload');hashes.add(hash);done++}
 }
 for(const query of ['Earn by Doing','Fictional expenses']){await page.locator('#hub-search').fill(query);assert.equal(await page.locator('.resource-card').count(),1)}
 await page.locator('#hub-search').fill('Earn by Doing');const grouped=page.locator('.resource-card');
 for(const label of ['Handbook · MD','Practice pack · ZIP']){const download=page.waitForEvent('download');await grouped.getByRole('link',{name:label+' ↓',exact:true}).click();const d=await download;assert.equal(await d.failure(),null);assert.match(d.suggestedFilename(),label.startsWith('Handbook')?/\.md$/:/\.zip$/)}
 await page.screenshot({path:dir+'/grouped-course-downloads.png'});
 await page.locator('#hub-search').fill('unfindable-library-test-92845');assert.equal(await page.locator('.resource-card').count(),0);assert.match(await page.locator('#hub-results').textContent(),/0 of 55/);
 await page.locator('#hub-search').fill('');assert.equal(await page.locator('.resource-card').count(),55);
 const nojs=await browser.newContext({javaScriptEnabled:false}),readable=await nojs.newPage();await readable.goto(base+'/library.html');assert.equal(await readable.locator('.resource-card').count(),55);assert.equal(await readable.locator('.library-downloads a').count(),91);assert.match(await readable.locator('#hub-results').textContent(),/55 resources/);await nojs.close();
 for(const width of [360,390,768,1024]){await page.setViewportSize({width,height:900});await page.goto(base+'/library.html');await page.locator('#hub-search[data-search-bound=true]').waitFor();assert.equal(await page.locator('.resource-card').count(),55);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2),false);await page.locator('#hub-search').fill('Earn by Doing');await page.screenshot({path:dir+'/grouped-course-'+width+'.png'})}
 assert.deepEqual(errors,[]);const report={uniqueCards:55,groupedCourses:20,downloadsChecked:done,uniquePayloadHashes:hashes.size,downloadFormatsTested:['MD','ZIP'],searchAndReset:true,noJavaScript:true,responsiveWidths:[360,390,768,1024],pageErrors:errors};await writeFile(dir+'/result.json',JSON.stringify(report,null,2));console.log('PASS:',JSON.stringify(report));
}finally{await browser.close()}
