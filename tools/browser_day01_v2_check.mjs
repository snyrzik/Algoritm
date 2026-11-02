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
// Historical solution is a sentinel, never a reference implementation.
const old=path.join(profile,'student','day-01','d1-s01');mkdirSync(old,{recursive:true});
writeFileSync(path.join(old,'solution.hpp'),'// learner archive sentinel');
const env={...process.env,PYTHONUTF8:'1',MASTERY_DATA:profile};
const migration=spawnSync(pythonExe,['-c','from tools.build_day01_v2 import archive_legacy; archive_legacy()'],{cwd:root,env,windowsHide:true,encoding:'utf8'});
assert.equal(migration.status,0,migration.stderr);
const backend=spawn(pythonExe,['-m','backend.server','--port','8768'],{cwd:root,env,windowsHide:true,stdio:['ignore','pipe','pipe']});
let logs='';backend.stdout.on('data',s=>logs+=s);backend.stderr.on('data',s=>logs+=s);
const base='http://127.0.0.1:8768';let browser,page;
const errors=[];
async function visit(hash){await page.goto(base+'/#/'+hash,{waitUntil:'networkidle0'});await page.waitForSelector('h1');}
async function click(text){await page.waitForFunction(t=>[...document.querySelectorAll('button')].some(b=>b.textContent.includes(t)),{},text);await page.evaluate(t=>[...document.querySelectorAll('button')].find(b=>b.textContent.includes(t)).click(),text);}
 async function fill(selector,value){await page.waitForSelector(selector);await page.click(selector);await page.keyboard.down('Control');await page.keyboard.press('KeyA');await page.keyboard.up('Control');await page.keyboard.type(value);}
async function noOverflow(){assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Horizontal page overflow');}
try{
 for(let i=0;i<100;i++){try{if((await fetch(base+'/api/session')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));if(i===99)throw Error(logs);}
 browser=await puppeteer.launch({executablePath,headless:true,args:['--disable-gpu'],defaultViewport:{width:1440,height:1080}});
 page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));
 const course=await (await fetch(base+'/api/course')).json();assert.equal(course.tasks.filter(t=>t.day===1).length,48);
 for(const task of course.tasks.filter(t=>t.version===2))assert.ok(!['answer','tests','checks','traceAnswer','diagnosisAnswer','variants'].some(k=>k in task));
 await visit('day/1');assert.equal(await page.$eval('h1',e=>e.textContent),'StereoLab');
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
 await visit('task/d01-v2-d02');await page.waitForSelector('.cm-content');
 assert.equal(await page.$eval('.cm-content',e=>e.contentEditable),'false');
 assert.equal(await page.$$eval('.run-toolbar button',nodes=>nodes.length===2&&nodes.every(n=>n.disabled)),true);
 await fill('[aria-label="В чём дефект?"]','The operation changes a different object during the chained expression.');
 await page.click('.v2-diagnosis-rules input');await click('Зафиксировать разбор');
 await page.waitForFunction(()=>document.querySelector('.cm-content')?.contentEditable==='true');
 await page.screenshot({path:path.join(output,'diagnosis-editor.png'),fullPage:true});
 await visit('task/d01-v2-b02');const response=page.waitForResponse(r=>r.url().includes('/api/run/d01-v2-b02')&&r.request().method()==='POST');
 await click('Скомпилировать');assert.equal((await (await response).json()).status,'DEPENDENCY_ERROR');
 await visit('task/d01-v2-c01');await page.waitForSelector('.cm-content');assert.ok((await page.$eval('.file-tabs',e=>e.textContent)).includes('main.cpp'));
 await visit('archive/1');await page.waitForSelector('.v2-task-row');assert.equal(await page.$$eval('.v2-task-row',e=>e.length),52);
 const zip=await fetch(base+'/api/archive/day-1/solutions.zip');assert.equal(zip.status,200);assert.ok((await zip.arrayBuffer()).byteLength>100);
 await visit('task/d1-s01');await page.waitForSelector('.cm-content');assert.ok((await page.$eval('.cm-content',e=>e.textContent)).includes('learner archive sentinel'));assert.ok(await page.$('.v2-archive-banner'));
 await visit('day/1');await page.setViewport({width:390,height:844});await noOverflow();await page.screenshot({path:path.join(output,'roadmap-mobile.png'),fullPage:true});
 await visit('task/d01-v2-p03');await noOverflow();await page.screenshot({path:path.join(output,'prediction-mobile.png'),fullPage:true});
 await visit('task/d01-v2-a01');await click('Код и проверка');await page.waitForSelector('.cm-content');await noOverflow();await page.screenshot({path:path.join(output,'editor-mobile.png'),fullPage:true});
 await visit('day/2');assert.equal(await page.$('.v2-roadmap'),null);assert.ok(await page.$('.tabs'));
 const summary=await (await fetch(base+'/api/day01/summary')).json();assert.equal(summary.maximum,130);assert.ok(summary.critical.length);assert.notEqual(summary.state,'Полный автоматический зачёт');
 assert.deepEqual(errors,[]);
 console.log('StereoLab browser QA PASS: 48 tasks, seven stages, answer secrecy, prediction persistence/variants, diagnosis gate, real dependency errors, console files, archive, themes, mobile, unchanged Day 2.');
}catch(error){
 if(page){console.error('Browser errors:',errors);console.error((await page.$eval('body',e=>e.innerText)).slice(-5000));await page.screenshot({path:path.join(output,'failure.png'),fullPage:true});}
 throw error;
}finally{
 if(browser)await browser.close();
 if(backend.exitCode===null)await new Promise(r=>{backend.once('exit',r);backend.kill();});
 const absolute=path.resolve(profile);if(absolute.startsWith(path.resolve(tmpdir())+path.sep)&&path.basename(absolute).startsWith('mastery-stereolab-browser-'))rmSync(absolute,{recursive:true,force:true});
}
