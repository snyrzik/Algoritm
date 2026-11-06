import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import {
  mkdtempSync,
  mkdirSync,
  readdirSync,
  existsSync,
  readFileSync,
  writeFileSync,
  rmSync,
} from "node:fs";
import { tmpdir, homedir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { python } from "./python.mjs";
const { default: puppeteer } = await import(
  process.env.MASTERY_PUPPETEER_MODULE || "puppeteer-core"
);
const root = fileURLToPath(new URL("..", import.meta.url));
const data = mkdtempSync(path.join(tmpdir(), "cpp-mastery-browser-"));
const [py, args] = python();
const pythonExe = spawnSync(
  py,
  [...args, "-c", "import sys;print(sys.executable)"],
  { encoding: "utf8", windowsHide: true },
).stdout.trim();
let executablePath = process.env.PUPPETEER_EXECUTABLE_PATH;
if (!executablePath) {
  const cache = path.join(homedir(), ".cache", "puppeteer", "chrome");
  if (existsSync(cache))
    for (const version of readdirSync(cache).sort().reverse()) {
      const candidate = path.join(cache, version, "chrome-win64", "chrome.exe");
      if (existsSync(candidate)) {
        executablePath = candidate;
        break;
      }
    }
}
if (!executablePath)
  throw new Error(
    "Set PUPPETEER_EXECUTABLE_PATH to an installed Chrome/Chromium.",
  );
const env = { ...process.env, PYTHONUTF8: "1", MASTERY_DATA: data };
let backend;
async function launch() {
  backend = spawn(pythonExe, ["-m", "backend.server", "--port", "8780"], {
    cwd: root,
    env,
    windowsHide: true,
    stdio: ["ignore", "pipe", "pipe"],
  });
  let logs = "";
  backend.stdout.on("data", (v) => (logs += v));
  backend.stderr.on("data", (v) => (logs += v));
  for (let i = 0; i < 100; i++) {
    try {
      const response = await fetch("http://127.0.0.1:8780/api/session");
      if (response.ok) return;
    } catch {}
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error("Server failed to start: " + logs);
}
async function stop() {
  if (!backend || backend.exitCode !== null) return;
  await new Promise((r) => {
    backend.once("exit", r);
    backend.kill();
  });
}
await launch();
const browser = await puppeteer.launch({
  executablePath,
  headless: true,
  args: ["--disable-gpu"],
  defaultViewport: { width: 1440, height: 1080 },
});
const page = await browser.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
const output = path.join(root, "test-results");
mkdirSync(output, { recursive: true });
async function click(text) {
  await page.waitForFunction(
    (t) =>
      [...document.querySelectorAll("button,summary")].some((b) =>
        b.innerText.includes(t),
      ),
    {},
    text,
  );
  await page.evaluate((t) => {
    const button = [...document.querySelectorAll("button,summary")].find((b) =>
      b.innerText.includes(t),
    );
    button.click();
  }, text);
}
async function visit(hash) {
  await page.goto("http://127.0.0.1:8780/#/" + hash, {
    waitUntil: "networkidle0",
  });
  await page.waitForSelector("h1");
}
const requests=[];page.on('request',r=>requests.push(r.url()));
try {
  await browser.defaultBrowserContext().overridePermissions('http://127.0.0.1:8780',['clipboard-read','clipboard-write','clipboard-sanitized-write']);
  const downloadPath=path.join(output,'lecture-pack-downloads');mkdirSync(downloadPath,{recursive:true});const cdp=await page.createCDPSession();await cdp.send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath,eventsEnabled:true});
  const lectureOne=await (await fetch('http://127.0.0.1:8780/api/theory/day-1/lecture-1')).json();
  const checkedFiles=[];
  for(const number of [2,3]){
    await visit('module/'+number);await page.waitForSelector('.pack-lecture');
    assert.ok((await page.$eval('.pack-lecture h1',e=>e.textContent)).includes(number===2?'переходный модуль':'RTTI'));
    const lecture=await (await fetch('http://127.0.0.1:8780/api/lectures/'+number)).json();
    for(const section of lecture.sections){
      await visit(`theory/${number}/${section.id}`);await page.waitForSelector('.pack-article');
      const actual=await page.$$eval('.pack-article .theory-code-block code',nodes=>nodes.map(node=>node.textContent.replace(/\r\n/g,'\n').trimEnd()));
      const expected=[...section.markdown.matchAll(/```[^\r\n]*\r?\n([\s\S]*?)\r?\n```/g)].map(match=>match[1].replace(/\r\n/g,'\n').trimEnd());
      assert.deepEqual(actual,expected,`Every code/diagram block must be complete: lecture ${number}, ${section.id}`);
      if(section.chapter){assert.ok(await page.$('.theory-check-card'));await click('Открыть закрепление');await page.waitForSelector('.pack-exercise');assert.ok((await page.$eval('.manual-condition',e=>e.textContent)).includes(lecture.checks[section.chapter-1].title.split(' · ')[1].replace('RTTI · ',''))||section.chapter===4);}
    }
    await visit(`theory/${number}/practice`);await page.waitForSelector('.lecture01-project');assert.equal((await page.$$('.lecture01-project')).length,number===2?2:3);
    assert.ok(!(await page.$eval('main',e=>e.textContent)).includes('Прежний практикум'));
    await visit(`theory/${number}/local-checks`);await page.waitForSelector('[aria-label="Проверочный main"]');
    const mains=[...lecture.projects,...lecture.checks].flatMap(task=>task.localMains);
    for(const main of mains){
      await page.select('[aria-label="Проверочный main"]',main.filename);await page.waitForFunction(filename=>document.querySelector('.pack-main-viewer h3')?.textContent===filename,{},main.filename);await page.waitForSelector('.pack-main-viewer .language-cpp');
      const response=await fetch(`http://127.0.0.1:8780/api/lecture-main/${number}/${main.filename}`),source=await response.text();
      await page.bringToFront();await page.click('.pack-main-viewer .lecture01-main-heading button');await page.waitForFunction(()=>document.querySelector('.pack-main-viewer .lecture01-main-heading button')?.textContent.includes('Скопировано'));
      assert.equal((await page.evaluate(()=>navigator.clipboard.readText())).replace(/\r\n/g,'\n'),source.replace(/\r\n/g,'\n'));
      const filename=path.join(downloadPath,main.filename);rmSync(filename,{force:true});await page.click('.pack-main-viewer a[download]');
      for(let i=0;i<50&&!existsSync(filename);i++)await new Promise(resolve=>setTimeout(resolve,100));assert.ok(existsSync(filename));assert.equal(readFileSync(filename,'utf8'),source);
      checkedFiles.push(main.filename);
    }
  }
  assert.equal(checkedFiles.length,7);
  await visit('theory/2/chapter-1');await page.waitForSelector('.lecture01-read-toggle');await click('Отметить главу прочитанной');await page.waitForFunction(()=>document.querySelector('.lecture01-read-toggle')?.textContent.includes('Прочитано ·'));
  assert.deepEqual((await (await fetch('http://127.0.0.1:8780/api/theory/day-1/lecture-1')).json()).reading,lectureOne.reading);
  await visit('task/l02-local-c03');await page.waitForSelector('.pack-confirm');assert.equal(await page.$('.pack-main-viewer'),null);
  assert.equal(await page.$eval('.pack-confirm .primary',button=>button.disabled),true);
  await page.$$eval('.pack-requirements input',inputs=>inputs.forEach(input=>input.click()));await page.type('[aria-label="Моё объяснение"]','My independent explanation of invalid pointer and index cases.');await click('Выполнил закрепление');await page.waitForSelector('.manual-saved .SELF_CHECKED');
  await visit('task/l03-local-p03');await page.waitForSelector('.pack-confirm');
  await page.$$eval('.pack-requirements input',inputs=>inputs.forEach(input=>input.click()));await click('Проверил локально');await page.waitForFunction(()=>document.querySelector('.exercise-title')?.textContent.includes('В работе'));
  await page.$$eval('[aria-label="Этапы проекта"] button',buttons=>buttons[1].click());await page.waitForFunction(()=>document.querySelector('.pack-main-viewer h3')?.textContent==='MAIN_POSTFIX.cpp');
  await page.$$eval('.pack-requirements input',inputs=>inputs.forEach(input=>input.click()));await click('Проверил локально');await page.waitForFunction(()=>document.querySelector('.exercise-title')?.textContent.includes('Отмечено мной'));
  await page.type('[aria-label="Ошибки и неуспешные сценарии"]','Repeat negative operands');await page.type('[aria-label="Использованные подсказки"]','Lecture notes');await click('Нужно повторить');await page.waitForFunction(()=>document.querySelector('.exercise-title')?.textContent.includes('Нужно повторить'));
  await page.reload({waitUntil:'networkidle0'});await page.waitForSelector('.pack-confirm');await page.$$eval('[aria-label="Этапы проекта"] button',buttons=>buttons[1].click());
  assert.equal(await page.$eval('[aria-label="Ошибки и неуспешные сценарии"]',input=>input.value),'Repeat negative operands');
  await visit('theory/3/progress');await page.waitForSelector('.pack-progress-list');assert.ok((await page.$eval('.pack-progress-list',e=>e.textContent)).includes('Repeat negative operands'));
  await visit('theory/2/chapter-4');await page.waitForSelector('.pack-article');await page.screenshot({path:path.join(output,'lecture02-desktop.png'),fullPage:false});
  await page.setViewport({width:390,height:844});
  for(const route of ['theory/2/overview','theory/2/chapter-4','theory/2/practice','theory/2/local-checks','theory/3/chapter-3','theory/3/practice','theory/3/progress','task/l03-local-p03']){
    await visit(route);await page.waitForSelector(route.startsWith('task')?'.pack-confirm':'.pack-lecture');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),route+' overflow');
  }
  await page.screenshot({path:path.join(output,'lecture03-mobile.png'),fullPage:true});await page.click('[aria-label="Сменить тему"]');await page.screenshot({path:path.join(output,'lecture03-mobile-light.png'),fullPage:false});
  assert.deepEqual(errors,[]);assert.ok(!requests.some(url=>url.includes('/api/run/')||url.includes('/api/doctor')));
  console.log('Lectures 2/3 browser PASS: complete chapters/examples, 8 checks, 5 projects, 7 exact clipboard/download files, separate reading, explicit reflection, independent postfix stage, error/hint history, both themes, mobile; lecture 1 preserved, no compiler.');
} catch(error){console.error('Lecture pack diagnostics:',errors,await page.evaluate(()=>document.body.innerText));throw error;} finally {
  await browser.close();await stop();const absolute=path.resolve(data);if(absolute.startsWith(path.resolve(tmpdir())+path.sep)&&path.basename(absolute).startsWith('cpp-mastery-browser-'))rmSync(absolute,{recursive:true,force:true});
}
