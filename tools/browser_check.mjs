import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import {
  mkdtempSync,
  mkdirSync,
  readdirSync,
  existsSync,
  readFileSync,
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
  backend = spawn(pythonExe, ["-m", "backend.server", "--port", "8766"], {
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
      const response = await fetch("http://127.0.0.1:8766/api/session");
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
  await page.goto("http://127.0.0.1:8766/#/" + hash, {
    waitUntil: "networkidle0",
  });
  await page.waitForSelector("h1");
}
const requests=[];page.on('request',r=>requests.push(r.url()));
try {
  await visit('day/1');await page.waitForSelector('.lecture01-tabs');
  assert.equal(await page.$eval('h1',e=>e.textContent),'Перегрузка операций');
  assert.equal(await page.$('.stereolab-page'),null);
  for(let module=2;module<=3;module++){await click('\u041c\u043e\u0434\u0443\u043b\u044c '+module);await page.waitForFunction(n=>location.hash==='#/module/'+n,{},module);}
  await visit('theory/1/overview');await page.waitForSelector('.theory-article');
  assert.equal(await page.$$eval('.theory-navigation nav button',nodes=>nodes.length),7);
  for(let chapter=1;chapter<=5;chapter++){
    await visit('theory/1/chapter-'+chapter);await page.waitForSelector('.theory-check-card');
    assert.ok((await page.$eval('.theory-article',e=>e.textContent)).includes('Глава '+chapter));
    assert.ok(await page.$('.language-cpp .tok-keyword'));
    assert.ok((await page.$eval('.theory-check-card',e=>e.textContent)).includes(['ScoreCounter','Duration','FixedHistory','TextHolder','ClockTime'][chapter-1]));
  }
  await click('Отметить главу прочитанной');await page.waitForFunction(()=>document.querySelector('.lecture01-read-toggle')?.textContent.includes('Прочитано ·'));
  assert.equal((await (await fetch('http://127.0.0.1:8766/api/progress')).json()).attempts.length,0);
  await page.reload({waitUntil:'networkidle0'});await page.waitForFunction(()=>document.querySelector('.lecture01-read-toggle')?.textContent.includes('Прочитано ·'));
  await visit('theory/1/chapter-4');assert.ok(await page.$('.theory-memory'));
  await page.screenshot({path:path.join(output,'lecture01-theory-desktop.png'),fullPage:false});
  await visit('theory/1/practice');await page.waitForSelector('.lecture01-project');
  assert.equal((await page.$$('.lecture01-project')).length,3);
  const context=browser.defaultBrowserContext();await context.overridePermissions('http://127.0.0.1:8766',['clipboard-read','clipboard-write','clipboard-sanitized-write']);
  const cdp=await page.createCDPSession();
  await cdp.send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:output,eventsEnabled:true});
  await visit('theory/1/local-checks');await page.waitForSelector('.lecture01-local-main');
  for(const [index,name] of ['Matrix2x2','CMyString','DynamicVector'].entries()){
    await page.$$eval('.lecture01-project-picker button',(buttons,i)=>buttons[i].click(),index);
    await page.waitForFunction(n=>document.querySelector('.lecture01-local-main h3')?.textContent.includes(n),{},name);
    await page.bringToFront();
    await (await page.$('.lecture01-main-heading button')).click();
    await page.waitForFunction(()=>[...document.querySelectorAll('.lecture01-main-heading button')].some(b=>b.textContent.includes('Скопировано')));
    const clipboard=await page.evaluate(()=>navigator.clipboard.readText());
    const guide=await (await fetch('http://127.0.0.1:8766/api/self-check/l01-v3-p0'+(index+1))).json();
    assert.equal(clipboard.replace(/\r\n/g,'\n'),guide.main);
    assert.ok((await page.$eval('.lecture01-output',e=>e.textContent)).includes(name+': основные проверки пройдены.'));
  }
  rmSync(path.join(output,'main.cpp'),{force:true});
  await click('Скачать main.cpp');
  for(let i=0;i<50&&!existsSync(path.join(output,'main.cpp'));i++)await new Promise(r=>setTimeout(r,100));
  assert.ok(existsSync(path.join(output,'main.cpp')));
  assert.equal(readFileSync(path.join(output,'main.cpp'),'utf8'),(await (await fetch('http://127.0.0.1:8766/api/self-check/l01-v3-p03')).json()).main);
  console.log('Lecture/source navigation and three real clipboard/download checks passed.');
  await page.screenshot({path:path.join(output,'lecture01-local-desktop.png'),fullPage:false});
  await visit('task/l01-v3-p01');await page.waitForSelector('.manual-cases');
  assert.equal(await page.$('.manual-main'),null);assert.equal(await page.$('.run-toolbar'),null);
  await click('Показать main для проверки');await page.waitForSelector('.manual-main');
  assert.ok((await page.$eval('.manual-expected',e=>e.textContent)).includes('Matrix2x2: основные проверки пройдены.'));
  assert.ok(!(await page.$eval('.manual-expected',e=>e.textContent)).includes('ALL CHECKS PASSED'));
  assert.equal((await (await fetch('http://127.0.0.1:8766/api/progress')).json()).attempts.length,0);
  const mark=page.waitForResponse(r=>r.url().includes('/api/self-check/l01-v3-p01')&&r.request().method()==='POST');
  await click('Да, всё совпало');assert.equal((await (await mark).json()).status,'SELF_CHECKED');
  await page.waitForSelector('.manual-saved.done');await page.reload({waitUntil:'networkidle0'});await page.waitForSelector('.manual-saved.done');
  assert.ok((await page.$eval('.exercise-title',e=>e.textContent)).includes('Отмечено мной'));
  await click('Есть расхождения');await page.waitForSelector('.manual-saved.pending');
  await click('Ваш черновик решения');await page.waitForSelector('.cm-content');
  assert.ok((await page.$eval('.file-tabs .active',e=>e.textContent)).includes('Matrix2x2.hpp'));
  await page.click('.cm-content');await page.keyboard.down('Control');await page.keyboard.press('KeyA');await page.keyboard.up('Control');await page.keyboard.type('// saved local draft');
  await new Promise(r=>setTimeout(r,1400));await page.reload({waitUntil:'networkidle0'});await click('Ваш черновик решения');await page.waitForSelector('.cm-content');
  assert.ok((await page.$eval('.cm-content',e=>e.textContent)).includes('saved local draft'));
  for(let chapter=1;chapter<=5;chapter++){await visit('task/l01-v3-c0'+chapter);await page.waitForSelector('.manual-cases');await click('Показать main для проверки');await page.waitForSelector('.manual-expected');}
  await page.setViewport({width:390,height:844});
  for(const route of ['theory/1/chapter-4','theory/1/practice','theory/1/local-checks','task/l01-v3-p02']){
    await visit(route);await page.waitForSelector(route.startsWith('task')?'.manual-cases':'.lecture01-tabs');
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),route+' must not overflow');
  }
  await page.screenshot({path:path.join(output,'lecture01-mobile.png'),fullPage:true});
  await page.click('[aria-label="Сменить тему"]');await page.screenshot({path:path.join(output,'lecture01-mobile-light.png'),fullPage:false});
  assert.ok(!requests.some(url=>url.includes('/api/doctor')||url.includes('/api/run/')));
  await stop();await launch();await visit('task/l01-v3-p01');await page.waitForSelector('.manual-saved.pending');
  assert.deepEqual(errors,[]);
  console.log('Browser QA PASS: five exact chapters, five checks, three projects, copy/download main, local instructions, separate reading, reversible marks, drafts, restart, lecture navigation, dark/light and mobile.');
} catch(error) {
  console.error('Browser diagnostics:',errors,await page.evaluate(()=>document.body.innerText).catch(()=>''));throw error;
} finally {
  await browser.close();
  await stop();
  const absolute = path.resolve(data);
  if (
    absolute.startsWith(path.resolve(tmpdir()) + path.sep) &&
    path.basename(absolute).startsWith("cpp-mastery-browser-")
  )
    rmSync(absolute, { recursive: true, force: true });
}
