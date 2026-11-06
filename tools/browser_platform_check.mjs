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
  backend = spawn(pythonExe, ["-m", "backend.server", "--port", "8770"], {
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
      const response = await fetch("http://127.0.0.1:8770/api/session");
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
  await page.goto("http://127.0.0.1:8770/#/" + hash, {
    waitUntil: "networkidle0",
  });
  await page.waitForSelector("h1");
}
const requests=[];page.on('request',r=>requests.push(r.url()));
try {
  const cdp=await page.createCDPSession();await cdp.send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:output,eventsEnabled:true});
  await visit('');await page.waitForSelector('.platform-resume');
  assert.equal(await page.$eval('h1',e=>e.textContent),'Учитесь в своём темпе');
  assert.ok(!(await page.$eval('.sidebar',e=>e.textContent)).includes('Интенсив'));
  await click('Начать обучение');await page.waitForFunction(()=>location.hash==='#/theory/1/chapter-1');await page.waitForSelector('.theory-article');
  await visit('search');await page.waitForSelector('.platform-task-row');
  assert.equal((await page.$$('.platform-task-row')).length,20);await click('\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c \u0435\u0449\u0451');assert.equal((await page.$$('.platform-task-row')).length,28);
  assert.equal(await page.$('.platform-load-more'),null);
  await page.select('[aria-label="Тип задания"]','lecture-practice');assert.equal((await page.$$('.platform-task-row')).length,11);
  await page.select('[aria-label="Состояние задания"]','done');await page.waitForSelector('.platform-empty');
  await click('Сбросить фильтры');await page.waitForSelector('.platform-task-row');
  await page.click('.platform-task-row .bookmark-button');await page.waitForFunction(()=>document.querySelector('.platform-task-row .bookmark-button')?.getAttribute('aria-pressed')==='true');
  await visit('saved');await page.waitForSelector('.platform-task-row');assert.equal((await page.$$('.platform-task-row')).length,1);
  await page.reload({waitUntil:'networkidle0'});await page.waitForSelector('.platform-task-row');assert.equal((await page.$$('.platform-task-row')).length,1);
  await visit('search');await page.waitForSelector('.platform-task-row');
  while(await page.$('.platform-load-more button'))await page.click('.platform-load-more button');
  assert.equal((await page.$$('.platform-task-row')).length,28);
  await page.type('[aria-label="Поиск в заданиях"]','Duration');await page.waitForFunction(()=>document.querySelectorAll('.platform-task-row').length<20);
  assert.ok((await page.$$eval('.platform-task-row',rows=>rows.map(e=>e.textContent).join(' '))).includes('Duration'));
  await page.screenshot({path:path.join(output,'platform-search-desktop.png'),fullPage:false});
  await visit('theory/1/chapter-3');await page.waitForSelector('.theory-article');await new Promise(r=>setTimeout(r,400));
  await click('Отметить главу прочитанной');await page.waitForFunction(()=>document.querySelector('.lecture01-read-toggle')?.textContent.includes('Прочитано ·'));
  await page.evaluate(()=>document.querySelector('.brand').click());await page.waitForSelector('.platform-resume');
  assert.ok((await page.$eval('.platform-resume',e=>e.textContent)).includes('Класс, ссылки'));
  // The current chapter is read; resume correctly proposes the first unread chapter.
  await click('Продолжить обучение');await page.waitForFunction(()=>location.hash==='#/theory/1/chapter-1');
  await visit('theory/1/chapter-2');await page.waitForSelector('.theory-article');await new Promise(r=>setTimeout(r,400));await page.evaluate(()=>document.querySelector('.brand').click());await page.waitForSelector('.platform-resume');
  assert.ok((await page.$eval('.platform-resume',e=>e.textContent)).includes('Перегрузка операторов'));
  await visit('task/l01-v3-c01');await page.waitForSelector('.manual-cases');await click('Да, всё совпало');await page.waitForSelector('.manual-saved.done');
  await visit('report');await page.waitForSelector('.platform-progress-summary');assert.ok((await page.$eval('.platform-progress-summary',e=>e.textContent)).includes('1 из 28'));
  assert.ok((await page.$eval('.platform-module-card',e=>e.textContent)).includes('1 / 8'));
  await visit('task/l01-v3-p01');await page.waitForSelector('.manual-cases');await click('Есть расхождения');await page.waitForSelector('.manual-saved.pending');
  await visit('review');await page.waitForSelector('.platform-task-row');assert.ok((await page.$eval('.platform-task-row',e=>e.textContent)).includes('Matrix2x2'));
  await page.click('.platform-task-open');await page.waitForSelector('.manual-cases');await click('Да, всё совпало');await page.waitForSelector('.manual-saved.done');
  await visit('review');await page.waitForSelector('.platform-empty');assert.ok((await page.$eval('.platform-empty',e=>e.textContent)).includes('Заданий на доработку нет'));
  await click('Повторить выполненное');assert.equal((await page.$$('.platform-task-row')).length,2);
  await visit('task/l01-v3-p01');await page.waitForSelector('.manual-cases');await click('Ваш черновик решения');await page.waitForSelector('.cm-content');
  await page.click('.cm-content');await page.keyboard.down('Control');await page.keyboard.press('KeyA');await page.keyboard.up('Control');
  await page.keyboard.type('// draft preserved during conflict');
  const conflict=page.waitForResponse(r=>r.url().includes('/api/files/l01-v3-p01')&&r.status()===409);
  writeFileSync(path.join(data,'student/day-01/l01-v3-p01/Matrix2x2.hpp'),'// external IDE edit\n');await conflict;
  await page.waitForSelector('.error-banner');await page.click('.error-banner button');
  await page.waitForFunction(()=>document.querySelector('.cm-content')?.textContent.includes('external IDE edit'));
  assert.equal(readFileSync(path.join(data,'student/day-01/l01-v3-p01/Matrix2x2.hpp'),'utf8'),'// external IDE edit\n');
  assert.ok((await page.$eval('.manual-exercise',e=>e.textContent)).includes('Решение изменилось'));
  await visit('settings');await page.waitForSelector('[aria-label="Размер текста лекции"]');
  await page.$eval('[aria-label="Размер текста лекции"]',input=>{const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;setter.call(input,'19');input.dispatchEvent(new Event('input',{bubbles:true}));});
  await click('Светлая');await visit('theory/1/chapter-1');await page.waitForSelector('.theory-article');
  assert.equal(await page.$eval('.theory-article p',e=>getComputedStyle(e).fontSize),'19px');
  await page.reload({waitUntil:'networkidle0'});assert.equal(await page.$eval('html',e=>e.dataset.theme),'light');
  await visit('home');await page.waitForSelector('.platform-resume');await page.screenshot({path:path.join(output,'platform-home-light.png'),fullPage:false});
  await page.click('[aria-label="Сменить тему"]');await page.screenshot({path:path.join(output,'platform-home-dark.png'),fullPage:false});
  await page.setViewport({width:390,height:844});
  for(const route of ['home','program','module/3','search','saved','review','report','settings','help','theory/1/chapter-4','task/l01-v3-p02']){
    await visit(route);if(route.startsWith('task'))await page.waitForSelector('.manual-cases');else if(route.includes('chapter'))await page.waitForSelector('.theory-article');else await page.waitForSelector('h1');
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),route+' overflows mobile');
  }
  await visit('home');await page.waitForSelector('.platform-resume');await page.screenshot({path:path.join(output,'platform-home-mobile.png'),fullPage:true});
  await page.click('[aria-label="Открыть навигацию"]');await page.waitForSelector('.sidebar.open');await page.keyboard.press('Escape');assert.equal(await page.$('.sidebar.open'),null);
  await visit('unknown-page');await page.waitForSelector('.platform-empty');assert.ok((await page.$eval('.platform-empty',e=>e.textContent)).includes('Такой страницы нет'));
  await stop();await launch();await visit('saved');await page.waitForSelector('.platform-task-row');assert.equal((await page.$$('.platform-task-row')).length,1);
  assert.ok(!requests.some(url=>url.includes('/api/doctor')||url.includes('/api/run/')));assert.deepEqual(errors,[]);
  console.log('Platform QA PASS: self-paced home, resume, all active searchable tasks, pagination/filters, bookmarks, separate full progress, review, external-edit conflict recovery, preferences, all mobile pages, navigation, 404, restart; no compiler.');
} catch(error) {
  console.error('Platform diagnostics:',errors,await page.evaluate(()=>document.body.innerText).catch(()=>''));throw error;
} finally {
  await browser.close();await stop();const absolute=path.resolve(data);
  if(absolute.startsWith(path.resolve(tmpdir())+path.sep)&&path.basename(absolute).startsWith('cpp-mastery-browser-'))rmSync(absolute,{recursive:true,force:true});
}
