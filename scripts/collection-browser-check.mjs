import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const base=process.env.PREVIEW_URL||'http://127.0.0.1:3001',dir=process.env.QA_DIR||'.output/collection-polish';await mkdir(dir,{recursive:true});
const browser=await chromium.launch({args:['--no-sandbox']});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/');await page.locator('#cards .card').last().waitFor();
 const courses=await(await page.request.get(base+'/courses.json')).json();
 assert.equal(courses.length,20);assert.equal(await page.locator('.public-browser .manual-thumbnail,.public-browser [role=tablist],#browse-thumbnails').count(),0);
 assert.equal(await page.locator('#browse-stage').getAttribute('aria-labelledby'),'browse-title');assert.equal(await page.locator('#browse-keyboard-help').count(),1);
 for(let i=0;i<courses.length;i++){
  if(i)await page.locator('#browse-next').click();
  assert.equal(await page.locator('#browse-title').textContent(),courses[i].title);
  await page.locator('#browse-cover').evaluate(e=>e.decode());
  assert.equal(await page.locator('#browse-handbook').getAttribute('href'),courses[i].downloads.handbook);
 }
 await page.locator('#browse-next').click();assert.match(await page.locator('#browse-counter').textContent(),/1 OF 20/);
 await page.locator('#browse-prev').click();assert.match(await page.locator('#browse-counter').textContent(),/20 OF 20/);
 await page.locator('#browse-stage').press('Home');assert.match(await page.locator('#browse-counter').textContent(),/1 OF 20/);
 await page.locator('#browse-stage').press('ArrowRight');assert.match(await page.locator('#browse-counter').textContent(),/2 OF 20/);
 await page.locator('#browse-next').press('End');assert.match(await page.locator('#browse-counter').textContent(),/20 OF 20/);
 await page.locator('#browse-next').press('ArrowLeft');assert.match(await page.locator('#browse-counter').textContent(),/19 OF 20/);
 await page.locator('#browse-prev').press('ArrowRight');assert.match(await page.locator('#browse-counter').textContent(),/20 OF 20/);
 await page.locator('#browse-stage').press('Home');
 const download=page.waitForEvent('download');await page.locator('#browse-download').click();assert.match((await download).suggestedFilename(),/\.html$/);
 await page.locator('.public-browser').screenshot({path:dir+'/collection-desktop.png'});
 async function checkArrowPlacement(){
  const image=await page.locator('#browse-cover').boundingBox(),left=await page.locator('#browse-prev').boundingBox(),right=await page.locator('#browse-next').boundingBox();
  assert.ok(left.x+left.width<=image.x,'Previous arrow must be left of the cover without overlap');
  assert.ok(right.x>=image.x+image.width,'Next arrow must be right of the cover without overlap');
  for(const button of [left,right]){assert.ok(button.width>=44&&button.height>=44);assert.ok(Math.abs(button.y+button.height/2-(image.y+image.height/2))<2,'Arrow vertically centered on cover')}
  assert.equal(await page.locator('.public-browser .division-title button').count(),0);
 }
 await checkArrowPlacement();
 for(const width of [320,360,390,768,1024]){
  await page.setViewportSize({width,height:900});
  for(const route of ['/','/dashboard.html','/library.html','/activities.html','/tools.html','/builds/earn-by-doing.html']){
   await page.goto(base+route);await page.locator('main:visible').first().waitFor();
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2),false,route+' at '+width);
  }
  await page.goto(base+'/');await page.locator('#cards .card').last().waitFor();
  await page.locator('#browse-cover').evaluate(e=>e.decode());
  await checkArrowPlacement();
  await page.locator('.public-browser').screenshot({path:dir+'/collection-'+width+'.png'});
 }
 await page.setViewportSize({width:390,height:900});await page.goto(base+'/');await page.locator('#cards .card').last().waitFor();await page.locator('#browse-swipe').scrollIntoViewIfNeeded();
 const rect=await page.locator('#browse-cover').boundingBox();const x=rect.x+rect.width*.8,y=rect.y+rect.height/2;
 await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x-120,y,{steps:8});await page.mouse.up();assert.match(await page.locator('#browse-counter').textContent(),/2 OF 20/);
 await page.locator('#browse-primary').click();await page.locator('#steps button').last().waitFor();assert.equal(await page.locator('#steps button').count(),6);
 assert.deepEqual(errors,[]);await writeFile(dir+'/result.json',JSON.stringify({thumbnailStripRemoved:true,coursesNavigated:20,keyboard:true,swipe:true,offlineDownload:true,courseOpen:true,responsiveWidths:[320,360,390,768,1024],coverSideArrows:true,responsivePages:6,pageErrors:errors},null,2));
 console.log('PASS: no public thumbnails; all 20 paths; arrows, wraparound, keyboard, swipe, offline download and course opening; centered side arrows with no artwork overlap; six pages at five widths.');
}finally{await browser.close()}
