import assert from 'node:assert/strict';
import {spawn,spawnSync} from 'node:child_process';
import {mkdtempSync,mkdirSync,readdirSync,readFileSync,writeFileSync,existsSync,rmSync} from 'node:fs';
import {tmpdir,homedir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import puppeteer from 'puppeteer-core';
import {python} from './python.mjs';
const root=fileURLToPath(new URL('..',import.meta.url)),data=mkdtempSync(path.join(tmpdir(),'mastery-python-browser-')),output=path.join(root,'test-results'),downloads=path.join(output,'python-downloads'),base='http://127.0.0.1:8788';mkdirSync(downloads,{recursive:true});
const [py,prefix]=python(),pythonExe=spawnSync(py,[...prefix,'-c','import sys;print(sys.executable)'],{encoding:'utf8',windowsHide:true}).stdout.trim();
let executablePath=process.env.PUPPETEER_EXECUTABLE_PATH;
if(!executablePath){const cache=path.join(homedir(),'.cache/puppeteer/chrome');if(existsSync(cache))for(const version of readdirSync(cache).sort().reverse()){const file=path.join(cache,version,'chrome-win64/chrome.exe');if(existsSync(file)){executablePath=file;break;}}}
if(!executablePath)throw Error('Set PUPPETEER_EXECUTABLE_PATH to installed Chrome.');
let backend,browser,page,logs='';const errors=[],requests=[];
async function launch(){backend=spawn(pythonExe,['-m','backend.server','--port','8788'],{cwd:root,env:{...process.env,PYTHONUTF8:'1',MASTERY_DATA:data},windowsHide:true,stdio:['ignore','pipe','pipe']});backend.stdout.on('data',v=>logs+=v);backend.stderr.on('data',v=>logs+=v);for(let i=0;i<100;i++){try{if((await fetch(base+'/api/session')).ok)return;}catch{}await new Promise(r=>setTimeout(r,100));}throw Error(logs);}
async function stop(){if(backend&&backend.exitCode===null)await new Promise(resolve=>{backend.once('exit',resolve);backend.kill();});}
async function visit(route){await page.goto(base+'/#/'+route,{waitUntil:'networkidle0'});await page.waitForSelector('h1');}
async function click(text){await page.waitForFunction(t=>[...document.querySelectorAll('button,summary')].some(b=>b.textContent.includes(t)),{},text);await page.evaluate(t=>[...document.querySelectorAll('button,summary')].find(b=>b.textContent.includes(t)).click(),text);}
async function edit(text){await page.click('.cm-content');await page.keyboard.down('Control');await page.keyboard.press('KeyA');await page.keyboard.up('Control');await page.keyboard.type(text);}
const json=async route=>(await fetch(base+'/api/'+route)).json();
try{
 await launch();browser=await puppeteer.launch({executablePath,headless:true,defaultViewport:{width:1440,height:1000},args:['--disable-gpu']});page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));const cdp=await page.createCDPSession();await cdp.send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:downloads});
 await visit('home');const cppBefore=await json('progress'),cppLearning=await json('learning');assert.equal((await json('course')).tasks.length,28);
 await page.select('[aria-label="Выбрать предмет"]','python');await page.waitForSelector('.python-weeks');assert.equal((await page.$$('.python-weeks .platform-module-card')).length,8);
 const course=await json('python/course');assert.equal(course.tasks.length,40);
 for(const week of course.weeks){await visit('python/week/'+week.week);await page.waitForSelector('.platform-task-row');assert.equal((await page.$$('.platform-task-row')).length,5);}
 for(const task of course.tasks){await visit('python/task/'+task.id);await page.waitForSelector('.python-exercise .cm-content');assert.equal(await page.$eval('h1',e=>e.textContent),task.title);const text=await page.$eval('.python-task-content',e=>e.textContent);assert.ok(text.includes(task.description),task.id);assert.ok(text.includes(task.rules),task.id);assert.equal(await page.$('.python-solution'),null);assert.ok(!(await page.$eval('main',e=>e.textContent)).includes('PRIVATE_REFERENCE'));}
 await visit('python/task/py-01');await page.waitForSelector('.cm-content');assert.equal((await fetch(base+'/api/python/solution/py-01')).status,403);assert.equal(await page.$eval('.python-reference button',b=>b.disabled),true);
 await click('Подсказка');await page.waitForSelector('.python-hint');assert.equal((await fetch(base+'/api/python/solution/py-01')).status,403);
 await click('Сохранить попытку');await page.waitForSelector('.python-saved');assert.equal(await page.$eval('.python-reference button',b=>b.disabled),true);
 const own='def process_commands(commands: list[str]) -> dict[str, int]:\n    return {"my_attempt": len(commands)}\n';await edit(own);await click('Сохранить файлы');await page.waitForFunction(()=>document.querySelector('.platform-savebar')?.textContent.includes('Сохранено на компьютере'));assert.equal((await fetch(base+'/api/python/solution/py-01')).status,403);
 await click('Сохранить попытку');await page.waitForFunction(()=>document.querySelector('.python-reference button')?.disabled===false);await click('Показать эталон');await page.waitForSelector('.python-solution .language-python');assert.ok(await page.$('.python-solution .tok-keyword'));assert.equal((await json('python/progress')).states['py-01'].status,'in_progress');
 await page.click('.python-reflection .python-checkbox:nth-of-type(3) input').catch(async()=>{await page.$$eval('.python-reflection input[type="checkbox"]',inputs=>inputs[1].click());});
 if(await page.$eval('.python-reflection .primary',b=>b.disabled))await page.$$eval('.python-reflection input[type="checkbox"]',inputs=>inputs[1].click());
 await click('Отметить выполненным');await page.waitForFunction(()=>document.querySelector('.exercise-title')?.textContent.includes('Отмечено мной'));assert.equal((await json('python/progress')).states['py-01'].status,'completed');
 await click('В закладки');await page.waitForFunction(()=>document.querySelector('.python-task-content button[aria-pressed]')?.getAttribute('aria-pressed')==='true');
 const ownZip=path.join(downloads,'py-01-my-work.zip');rmSync(ownZip,{force:true});await click('Скачать мои файлы');for(let i=0;i<50&&!existsSync(ownZip);i++)await new Promise(r=>setTimeout(r,100));assert.ok(existsSync(ownZip));
 await page.screenshot({path:path.join(output,'python-task-desktop.png')});
 await visit('python/task/py-14');await page.waitForSelector('.cm-content');assert.equal((await page.$$('.file-tabs button')).length,2);await click('utils.py');await edit('def helper():\n    return 42\n');await click('Сохранить файлы');await page.waitForFunction(()=>document.querySelector('.platform-savebar')?.textContent.includes('Сохранено на компьютере'));await page.reload({waitUntil:'networkidle0'});await page.waitForSelector('.cm-content');await click('utils.py');await page.waitForFunction(()=>document.querySelector('.cm-content')?.textContent.includes('return 42'));
 await edit('# my draft before conflict\ndef helper():\n    return 7\n');const conflict=page.waitForResponse(r=>r.url().includes('/api/python/files/py-14')&&r.status()===409);writeFileSync(path.join(data,'student/python/py-14/utils.py'),'# external IDE edit\n');await conflict;await page.waitForSelector('.error-banner');await click('Загрузить с диска');await page.waitForFunction(()=>document.querySelector('.cm-content')?.textContent.includes('external IDE edit'));assert.equal(readFileSync(path.join(data,'student/python/py-14/utils.py'),'utf8'),'# external IDE edit\n');
 await visit('python/task/py-31');await page.waitForSelector('.python-optional');await click('Пропустить пока');await page.waitForFunction(()=>document.querySelector('.python-optional')?.textContent.includes('Вернуть в план'));await click('Тема уже пройдена');await page.waitForFunction(()=>document.querySelector('.python-optional')?.textContent.includes('Пока не изучал'));await click('Повторить позже');await page.waitForFunction(()=>document.querySelector('.exercise-title')?.textContent.includes('Нужно повторить'));
 await visit('python/saved');await page.waitForSelector('.platform-task-row');assert.ok((await page.$eval('.platform-task-row',e=>e.textContent)).includes('Учёт покупок'));
 await visit('python/review');await page.waitForSelector('.platform-task-row');assert.ok((await page.$eval('.platform-task-row',e=>e.textContent)).includes('NumPy'));
 await visit('python/progress');await page.waitForSelector('.platform-progress-summary');assert.ok((await page.$eval('.platform-progress-summary',e=>e.textContent)).includes('1 из'));
 assert.deepEqual(await json('progress'),cppBefore);assert.deepEqual(await json('learning'),cppLearning);
 await page.select('[aria-label="Выбрать предмет"]','cpp');await page.waitForSelector('.platform-resume');assert.ok((await page.$eval('h1',e=>e.textContent)).includes('Учитесь'));
 await page.select('[aria-label="Выбрать предмет"]','python');await page.waitForSelector('.python-weeks');await page.screenshot({path:path.join(output,'python-home-desktop.png')});
 await page.setViewport({width:390,height:844});
 for(const route of ['python','python/week/8','python/task/py-36','python/task/py-14','python/task/py-01','python/progress','python/saved','python/review','python/help']){await visit(route);await page.waitForSelector(route.includes('/task/')?'.python-exercise .cm-content':'h1');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),route+' overflow');}
 await visit('python/task/py-36');await page.waitForSelector('.python-exercise');await page.screenshot({path:path.join(output,'python-mobile.png')});await page.click('[aria-label="Сменить тему"]');await page.screenshot({path:path.join(output,'python-mobile-light.png')});
 await page.click('[aria-label="Открыть навигацию Python"]');await page.waitForSelector('.sidebar.open');await page.keyboard.press('Escape');assert.equal(await page.$('.sidebar.open'),null);
 await stop();await launch();await visit('python/task/py-01');await page.waitForSelector('.cm-content');assert.equal(await page.$eval('.python-reference button',b=>b.disabled),false);assert.ok((await page.$eval('.cm-content',e=>e.textContent)).includes('my_attempt'));
 assert.ok(!requests.some(url=>/\/api\/(?:python\/)?(?:run|check|doctor)(?:\/|$)/.test(url)));assert.deepEqual(errors,[]);
 console.log('Python browser PASS: 8 weeks, 40 complete tasks; separate subjects and C++ state; locked references; saved attempts and manual completion; two-file editor, ZIP and conflict recovery; optional topics, bookmarks, repeat; restart, themes, mobile; no execution.');
}catch(error){console.error('Python diagnostics:',errors,page?await page.evaluate(()=>document.body.innerText).catch(()=>''):logs);throw error;}
finally{await browser?.close();await stop();const resolved=path.resolve(data);if(resolved.startsWith(path.resolve(tmpdir())+path.sep)&&path.basename(resolved).startsWith('mastery-python-browser-'))rmSync(resolved,{recursive:true,force:true});}
