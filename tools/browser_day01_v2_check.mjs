import assert from 'node:assert/strict';
import {spawn,spawnSync} from 'node:child_process';
import {mkdtempSync,mkdirSync,readdirSync,existsSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir,homedir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import puppeteer from 'puppeteer-core';
import {python} from './python.mjs';

const root=fileURLToPath(new URL('..',import.meta.url));
const profile=mkdtempSync(path.join(tmpdir(),'mastery-stereolab-browser-'));
const output=path.join(root,'test-results','day01-v2');mkdirSync(output,{recursive:true});
const [py,args]=python();
const pythonExe=spawnSync(py,[...args,'-c','import sys;print(sys.executable)'],{encoding:'utf8',windowsHide:true}).stdout.trim();
let executablePath=process.env.PUPPETEER_EXECUTABLE_PATH;
if(!executablePath){const cache=path.join(homedir(),'.cache','puppeteer','chrome');if(existsSync(cache))for(const version of readdirSync(cache).sort().reverse()){const file=path.join(cache,version,'chrome-win64','chrome.exe');if(existsSync(file)){executablePath=file;break;}}}
if(!executablePath)throw Error('Set PUPPETEER_EXECUTABLE_PATH to Chrome/Chromium');
const env={...process.env,PYTHONUTF8:'1',MASTERY_DATA:profile};
const backend=spawn(pythonExe,['-m','backend.server','--port','8768'],{cwd:root,env,windowsHide:true,stdio:['ignore','pipe','pipe']});
let logs='';backend.stdout.on('data',s=>logs+=s);backend.stderr.on('data',s=>logs+=s);
const base='http://127.0.0.1:8768';let browser,page;
const errors=[];
async function visit(hash){await page.goto(base+'/#/'+hash,{waitUntil:'networkidle0'});await page.waitForSelector('h1');}
async function click(text){await page.waitForFunction(t=>[...document.querySelectorAll('button,summary')].some(b=>b.textContent.includes(t)),{},text);await page.evaluate(t=>[...document.querySelectorAll('button,summary')].find(b=>b.textContent.includes(t)).click(),text);}
 async function fill(selector,value){await page.waitForSelector(selector);await page.click(selector);await page.keyboard.down('Control');await page.keyboard.press('KeyA');await page.keyboard.up('Control');await page.keyboard.type(value);}
async function noOverflow(){assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Horizontal page overflow');}
try{
 for(let i=0;i<100;i++){try{if((await fetch(base+'/api/session')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));if(i===99)throw Error(logs);}
 browser=await puppeteer.launch({executablePath,headless:true,args:['--disable-gpu'],defaultViewport:{width:1440,height:1080}});
 page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));
 await page.evaluateOnNewDocument(()=>{
  if(!sessionStorage.getItem('clean-profile-seeded')){
   localStorage.setItem('mastery-workspace','previous-workspace');
   localStorage.setItem('mastery-draft-d01-v2-a01','previous learner answer');
   sessionStorage.setItem('clean-profile-seeded','yes');
  }
 });
 const course=await (await fetch(base+'/api/course')).json();assert.equal(course.tasks.filter(t=>t.day===1).length,48);
 for(const task of course.tasks.filter(t=>t.version===2))assert.ok(!['answer','tests','checks','traceAnswer','diagnosisAnswer','variants'].some(k=>k in task));
 await visit('day/1');assert.equal(await page.$eval('h1',e=>e.textContent),'StereoLab');
 assert.equal(await page.evaluate(()=>localStorage.getItem('mastery-draft-d01-v2-a01')),null);
 assert.equal(await page.$('.v2-download'),null);
 assert.equal(await page.$$eval('.v2-roadmap button',e=>e.length),7);await page.waitForSelector('.v2-score-panel');
 await noOverflow();await page.screenshot({path:path.join(output,'roadmap-dark.png'),fullPage:true});
 await page.click('[aria-label="Сменить тему"]');await page.screenshot({path:path.join(output,'roadmap-light.png'),fullPage:true});await page.click('[aria-label="Сменить тему"]');
 for(const [stage,count] of Object.entries({quiz:16,syntax:14,prediction:6,debugging:6,A:3,B:2,C:1})){
  await visit('day/1/'+stage);assert.equal(await page.$$eval('.v2-task-row',e=>e.length),count);
 }
 await visit('task/d01-v2-q01');assert.equal(await page.$('.answer-review'),null);
 await page.click('.option');await click('Проверить ответ');await page.waitForSelector('.answer-review');
 await visit('task/d01-v2-p01');assert.equal(await page.$('.v2-feedback'),null);
 await fill('[aria-label="Ожидаемый вывод"]','my saved prediction');await fill('[aria-label="Объяснение результата"]','My own explanation survives navigation and reload.');
 await new Promise(r=>setTimeout(r,1600));await page.reload({waitUntil:'networkidle0'});
 assert.equal(await page.$eval('[aria-label="Ожидаемый вывод"]',e=>e.value),'my saved prediction');
 const originalCode=await page.$eval('.v2-reasoning-card pre',e=>e.textContent);
 await click('Новый вариант');await page.waitForFunction(previous=>document.querySelector('.v2-reasoning-card pre')?.textContent!==previous,{},originalCode);
 await new Promise(r=>setTimeout(r,1600));await page.reload({waitUntil:'networkidle0'});
 assert.notEqual(await page.$eval('.v2-reasoning-card pre',e=>e.textContent),originalCode);
 await visit('task/d01-v2-d02');await page.waitForSelector('.manual-cases');
 assert.ok((await page.$eval('.manual-condition',e=>e.textContent)).includes('Meter operator+='));
 assert.equal(await page.$('.run-toolbar'),null);await click('Показать main для проверки');await page.waitForSelector('.manual-main');
 assert.ok((await page.$eval('.manual-expected',e=>e.textContent)).includes('ALL CHECKS PASSED'));
 await page.screenshot({path:path.join(output,'manual-debugging.png'),fullPage:true});
 await visit('task/d01-v2-b02');await click('Показать main для проверки');await page.waitForSelector('.manual-dependencies');
 assert.ok((await page.$eval('.manual-dependencies',e=>e.textContent)).includes('AudioBlock'));
 await visit('task/d01-v2-c01');await click('Показать main для проверки');await page.waitForSelector('.manual-scenario-label select');
 assert.equal((await fetch(base+'/api/archive/day-1')).status,404);
 assert.equal((await fetch(base+'/api/task/d1-s01')).status,404);
 await visit('day/1');await page.setViewport({width:390,height:844});await noOverflow();await page.screenshot({path:path.join(output,'roadmap-mobile.png'),fullPage:true});
 await visit('task/d01-v2-p03');await noOverflow();await page.screenshot({path:path.join(output,'prediction-mobile.png'),fullPage:true});
 await visit('task/d01-v2-a01');await click('Ваш черновик решения');await page.waitForSelector('.cm-content');await noOverflow();await page.screenshot({path:path.join(output,'editor-mobile.png'),fullPage:true});
 await visit('day/2');assert.equal(await page.$('.v2-roadmap'),null);assert.ok(await page.$('.tabs'));
 const summary=await (await fetch(base+'/api/day01/summary')).json();assert.equal(summary.maximum,130);assert.ok(summary.critical.length);assert.notEqual(summary.state,'Полный автоматический зачёт');
 await page.evaluate(()=>localStorage.setItem('mastery-draft-d01-v2-a01','stale answer after reset'));
 writeFileSync(path.join(profile,'progress','workspace-id'),'reset-browser-profile');
 await page.reload({waitUntil:'networkidle0'});
 assert.equal(await page.evaluate(()=>localStorage.getItem('mastery-draft-d01-v2-a01')),null);
 assert.equal(await page.evaluate(()=>localStorage.getItem('mastery-workspace')),'reset-browser-profile');
 assert.deepEqual(errors,[]);
 console.log('StereoLab browser QA PASS: 48 tasks, seven stages, answer secrecy, prediction persistence/variants, manual debugging checks, component files, console scenarios, themes, mobile, unchanged Day 2.');
}catch(error){
 if(page){console.error('Browser errors:',errors);console.error((await page.$eval('body',e=>e.innerText)).slice(-5000));await page.screenshot({path:path.join(output,'failure.png'),fullPage:true});}
 throw error;
}finally{
 if(browser)await browser.close();
 if(backend.exitCode===null)await new Promise(r=>{backend.once('exit',r);backend.kill();});
 const absolute=path.resolve(profile);if(absolute.startsWith(path.resolve(tmpdir())+path.sep)&&path.basename(absolute).startsWith('mastery-stereolab-browser-'))rmSync(absolute,{recursive:true,force:true});
}
