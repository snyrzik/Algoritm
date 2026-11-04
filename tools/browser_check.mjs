import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import {
  mkdtempSync,
  mkdirSync,
  readdirSync,
  existsSync,
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
  await visit('day/1');assert.equal(await page.$eval('h1',e=>e.textContent),'StereoLab');
  for(let day=2;day<=5;day++){await click('День '+day);await page.waitForFunction(n=>location.hash==='#/day/'+n,{},day);}
  await page.click('[aria-label="Сменить тему"]');assert.equal(await page.$eval('html',e=>e.dataset.theme),'light');await page.click('[aria-label="Сменить тему"]');
  await visit('task/d01-v2-q01');await page.click('.option');await click('Проверить ответ');await page.waitForSelector('.answer-review');
  await visit('task/d01-v2-a01');await page.waitForSelector('.manual-cases');
  assert.equal(await page.$('.manual-main'),null);assert.equal(await page.$('.run-toolbar'),null);
  assert.equal(await page.$('.manual-saved'),null);
  await click('Показать main для проверки');await page.waitForSelector('.manual-main');
  assert.ok((await page.$eval('.manual-main',e=>e.textContent)).includes('int main()'));
  assert.ok((await page.$eval('.manual-expected',e=>e.textContent)).includes('ALL CHECKS PASSED (13)'));
  assert.equal((await (await fetch('http://127.0.0.1:8766/api/progress')).json()).attempts.some(a=>a.task==='d01-v2-a01'),false);
  const mark=page.waitForResponse(r=>r.url().includes('/api/self-check/d01-v2-a01')&&r.request().method()==='POST');
  await click('Да, всё совпало');assert.equal((await (await mark).json()).status,'SELF_CHECKED');
  await page.waitForSelector('.manual-saved.done');
  await page.screenshot({path:path.join(output,'manual-desktop.png'),fullPage:true});
  await page.reload({waitUntil:'networkidle0'});await page.waitForSelector('.manual-saved.done');
  assert.ok((await page.$eval('.exercise-title',e=>e.textContent)).includes('Проверено мной'));
  await click('Есть расхождения');await page.waitForSelector('.manual-saved.pending');
  await page.waitForFunction(()=>document.querySelector('.exercise-title')?.textContent.includes('Нужна доработка'));
  await visit('task/d3-s02');await click('Ваш черновик решения');await page.waitForSelector('.cm-content');
  await page.click('.cm-content');await page.keyboard.down('Control');await page.keyboard.press('KeyA');await page.keyboard.up('Control');
  await page.keyboard.type('template<class T> T identity(T value) { return value; }\n// saved manual draft');
  await new Promise(r=>setTimeout(r,1400));await page.reload({waitUntil:'networkidle0'});await click('Ваш черновик решения');await page.waitForSelector('.cm-content');
  assert.ok((await page.$eval('.cm-content',e=>e.textContent)).includes('saved manual draft'));
  for(const task of ['d2-c03','d4-c01','d5-c01','d1-l1-c01']){await visit('task/'+task);await page.waitForSelector('.manual-cases');await click('Показать main для проверки');await page.waitForSelector('.manual-expected');}
  await visit('task/d01-v2-c01');await click('Показать main для проверки');await page.waitForSelector('.manual-scenario-label select');
  await page.select('.manual-scenario-label select','7');await page.waitForFunction(()=>document.querySelector('.manual-expected')?.textContent.includes('OUT_OF_RANGE'));
  await visit('settings');assert.ok((await page.$eval('main',e=>e.textContent)).includes('Как сдавать задания'));
  assert.equal(await page.$('.compiler-output'),null);
  await visit('task/d01-v2-a02');await page.setViewport({width:390,height:844});await page.waitForSelector('.manual-reveal');await click('Показать main для проверки');
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:path.join(output,'manual-mobile.png'),fullPage:true});
  await page.click('[aria-label="Сменить тему"]');await page.screenshot({path:path.join(output,'manual-mobile-light.png'),fullPage:true});
  assert.ok(!requests.some(url=>url.includes('/api/doctor')||url.includes('/api/run/')));
  await stop();await launch();await visit('task/d01-v2-a01');await page.waitForSelector('.manual-saved.pending');
  assert.deepEqual(errors,[]);
  console.log('Browser QA PASS: five days, ready main and expected output, no compiler requests, explicit reversible self-check, draft/history persistence, server restart, dark/light and mobile.');
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
