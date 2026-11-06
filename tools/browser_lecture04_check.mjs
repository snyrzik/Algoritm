import assert from 'node:assert/strict';
import {spawn,spawnSync} from 'node:child_process';
import {mkdtempSync,mkdirSync,readFileSync,readdirSync,existsSync,rmSync} from 'node:fs';
import {tmpdir,homedir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {python} from './python.mjs';
import puppeteer from 'puppeteer-core';

const root=fileURLToPath(new URL('..',import.meta.url));
const data=mkdtempSync(path.join(tmpdir(),'cpp-mastery-lecture04-'));
const output=path.join(root,'test-results');mkdirSync(output,{recursive:true});
const downloads=path.join(output,'lecture04-downloads');mkdirSync(downloads,{recursive:true});
const base='http://127.0.0.1:8784';
const [py,prefix]=python();
const pythonExe=spawnSync(py,[...prefix,'-c','import sys;print(sys.executable)'],{encoding:'utf8',windowsHide:true}).stdout.trim();
let executablePath=process.env.PUPPETEER_EXECUTABLE_PATH;
if(!executablePath){const cache=path.join(homedir(),'.cache/puppeteer/chrome');if(existsSync(cache))for(const version of readdirSync(cache).sort().reverse()){const file=path.join(cache,version,'chrome-win64/chrome.exe');if(existsSync(file)){executablePath=file;break;}}}
if(!executablePath)throw Error('Set PUPPETEER_EXECUTABLE_PATH to Chrome/Chromium.');
let server,browser,page,logs='';const errors=[],requests=[];
async function launch(){
  server=spawn(pythonExe,['-m','backend.server','--port','8784'],{cwd:root,env:{...process.env,PYTHONUTF8:'1',MASTERY_DATA:data},windowsHide:true,stdio:['ignore','pipe','pipe']});
  server.stdout.on('data',v=>logs+=v);server.stderr.on('data',v=>logs+=v);
  for(let i=0;i<100;i++){try{if((await fetch(base+'/api/session')).ok)return;}catch{}await new Promise(resolve=>setTimeout(resolve,100));}throw Error(logs);
}
async function stop(){if(server&&server.exitCode===null)await new Promise(resolve=>{server.once('exit',resolve);server.kill();});}
async function visit(route){await page.goto(base+'/#/'+route,{waitUntil:'networkidle0'});await page.waitForSelector('h1');}
async function click(text){await page.waitForFunction(t=>[...document.querySelectorAll('button,summary')].some(b=>b.textContent.includes(t)),{},text);await page.evaluate(t=>[...document.querySelectorAll('button,summary')].find(b=>b.textContent.includes(t)).click(),text);}
const json=async url=>(await fetch(base+'/api/'+url)).json();
try{
  await launch();browser=await puppeteer.launch({executablePath,headless:true,defaultViewport:{width:1440,height:1000},args:['--disable-gpu']});page=await browser.newPage();
  page.on('pageerror',error=>errors.push(error.message));page.on('request',request=>requests.push(request.url()));
  await browser.defaultBrowserContext().overridePermissions(base,['clipboard-read','clipboard-write','clipboard-sanitized-write']);
  const cdp=await page.createCDPSession();await cdp.send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:downloads});
  const priorReading=(await json('progress')).reading;
  const lecture=await json('lectures/4');assert.equal(lecture.projects.length,3);assert.equal(lecture.checks.length,4);
  await visit('program');assert.equal((await page.$$('.platform-module-card')).length,4);
  await visit('module/4');await page.waitForSelector('.pack-lecture');assert.ok((await page.$eval('h1',e=>e.textContent)).includes('Списки'));
  for(const section of lecture.sections){
    await visit('theory/4/'+section.id);await page.waitForSelector('.pack-article');
    const expected=[...section.markdown.matchAll(/```[^\r\n]*\r?\n([\s\S]*?)\r?\n```/g)].map(m=>m[1].replace(/\r\n/g,'\n').trimEnd());
    const actual=await page.$$eval('.pack-article .theory-code-block code',nodes=>nodes.map(n=>n.textContent.replace(/\r\n/g,'\n').trimEnd()));assert.deepEqual(actual,expected,section.id);
    if(section.chapter){await click('Открыть закрепление');await page.waitForSelector('.pack-confirm');assert.equal(await page.$('.pack-main-viewer'),null);assert.equal(await page.$eval('.pack-confirm .primary',b=>b.disabled),true);}
  }
  await visit('theory/4/chapter-2');await page.waitForSelector('.lecture01-read-toggle');await click('Отметить главу прочитанной');await page.waitForFunction(()=>document.querySelector('.lecture01-read-toggle')?.textContent.includes('Прочитано ·'));
  assert.deepEqual((await json('progress')).reading.filter(k=>!k.startsWith('lecture-4/')),priorReading);
  await page.reload({waitUntil:'networkidle0'});assert.ok((await page.$eval('.lecture01-read-toggle',e=>e.textContent)).includes('Прочитано ·'));
  await visit('theory/4/practice');await page.waitForSelector('.lecture01-project');assert.equal((await page.$$('.lecture01-project')).length,3);assert.ok((await page.$eval('main',e=>e.textContent)).includes('STL'));
  await visit('theory/4/local-checks');await page.waitForSelector('[aria-label="Проверочный main"]');
  for(const task of lecture.projects){
    const main=task.localMains[0];await page.select('[aria-label="Проверочный main"]',main.filename);await page.waitForFunction(name=>document.querySelector('.pack-main-viewer h3')?.textContent===name,{},main.filename);await page.waitForSelector('.pack-main-viewer .language-cpp');
    const original=readFileSync(path.join(root,'content/lecture-04',main.sourcePath));
    await page.bringToFront();await page.click('.pack-main-viewer .lecture01-main-heading button');await page.waitForFunction(()=>document.querySelector('.pack-main-viewer .lecture01-main-heading button')?.textContent.includes('Скопировано'));
    assert.equal((await page.evaluate(()=>navigator.clipboard.readText())).replace(/\r\n/g,'\n'),original.toString().replace(/\r\n/g,'\n'));
    const file=path.join(downloads,main.filename);rmSync(file,{force:true});await page.click('.pack-main-viewer a[download]');for(let i=0;i<50&&!existsSync(file);i++)await new Promise(resolve=>setTimeout(resolve,100));assert.deepEqual(readFileSync(file),original);
    assert.ok((await page.$eval('.lecture01-output',e=>e.textContent)).includes(main.expectedOutput.trim()));
  }
  assert.equal((await json('progress')).attempts.length,0);
  await visit('task/l04-local-c04');await page.waitForSelector('.pack-confirm');await page.$$eval('.pack-requirements input',inputs=>inputs.forEach(input=>input.click()));
  assert.equal(await page.$eval('.pack-confirm .primary',b=>b.disabled),true);await page.type('[aria-label="Моё объяснение"]','I count iterations and distinguish a single append from the whole series.');await click('Выполнил закрепление');await page.waitForSelector('.manual-saved .SELF_CHECKED');
  await visit('task/l04-local-p01');await page.waitForSelector('.pack-project-notebook');assert.equal(await page.$eval('.pack-project-main',e=>e.open),false);await click('Проверочный main');assert.ok(await page.$('.pack-project-main .language-cpp'));
  await page.$$eval('.pack-implementation input',inputs=>inputs.slice(0,2).forEach(input=>input.click()));await page.type('[aria-label="Проблемы компиляции"]','Missing include diagnosed locally');await page.type('[aria-label="Замечания при ревью"]','Review head ownership');await click('Сохранить ход работы');await page.waitForSelector('.manual-saved .IN_PROGRESS');
  await page.reload({waitUntil:'networkidle0'});await page.waitForSelector('.pack-project-notebook');assert.equal((await page.$$('.pack-implementation input:checked')).length,2);assert.equal(await page.$eval('[aria-label="Проблемы компиляции"]',e=>e.value),'Missing include diagnosed locally');
  await page.$$eval('.pack-confirm input:not(:checked)',inputs=>inputs.forEach(input=>input.click()));assert.equal(await page.$eval('.pack-confirm .primary',b=>b.disabled),true);await page.type('[aria-label="Обоснование сложности"]','I explain input length, reachable nodes and the number of pointer updates.');
  await page.select('[aria-label="Проверка памяти"]','errors');assert.equal(await page.$eval('.pack-confirm .primary',b=>b.disabled),true);await page.select('[aria-label="Проверка памяти"]','sanitized');await click('Проверил локально');await page.waitForSelector('.manual-saved .SELF_CHECKED');
  await visit('theory/4/progress');await page.waitForSelector('.pack-progress-list');assert.ok((await page.$eval('.pack-progress-list',e=>e.textContent)).includes('Review head ownership'));assert.ok((await page.$eval('.pack-progress-list',e=>e.textContent)).includes('reachable nodes'));
  await visit('task/l04-local-p02');await page.waitForSelector('.pack-confirm');assert.equal(await page.$('.manual-saved'),null);
  await visit('theory/4/chapter-2');await page.waitForSelector('.pack-article');await page.screenshot({path:path.join(output,'lecture04-desktop.png')});
  await page.setViewport({width:390,height:844});
  for(const route of ['theory/4/overview','theory/4/chapter-1','theory/4/chapter-3','theory/4/practice','theory/4/local-checks','theory/4/progress','task/l04-local-p03','report']){
    await visit(route);await page.waitForSelector(route.startsWith('task')?'.pack-confirm':route==='report'?'.platform-progress-summary':'.pack-lecture');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),route+' overflow');
  }
  await visit('theory/4/chapter-3');await page.waitForSelector('.pack-article');await page.screenshot({path:path.join(output,'lecture04-mobile.png')});await page.click('[aria-label="Сменить тему"]');await page.screenshot({path:path.join(output,'lecture04-mobile-light.png')});
  await stop();await launch();await visit('task/l04-local-p01');await page.waitForSelector('.manual-saved .SELF_CHECKED');
  assert.deepEqual(errors,[]);assert.ok(!requests.some(url=>url.includes('/api/run/')||url.includes('/api/doctor')));
  console.log('Lecture 4 browser PASS: complete source and diagrams; four composed checkpoints; three projects; exact main copy/download; independent reading, stages, complexity and memory; saved notes and restart; mobile and both themes; no compiler.');
}catch(error){console.error('Lecture 4 diagnostics:',errors,page?await page.evaluate(()=>document.body.innerText).catch(()=>''):logs);throw error;}
finally{await browser?.close();await stop();const absolute=path.resolve(data);if(absolute.startsWith(path.resolve(tmpdir())+path.sep)&&path.basename(absolute).startsWith('cpp-mastery-lecture04-'))rmSync(absolute,{recursive:true,force:true});}
