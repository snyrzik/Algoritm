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
      [...document.querySelectorAll("button")].some((b) =>
        b.innerText.includes(t),
      ),
    {},
    text,
  );
  await page.evaluate((t) => {
    const button = [...document.querySelectorAll("button")].find((b) =>
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
try {
  await visit("day/1");
  assert.equal(
    await page.$eval("h1", (n) => n.textContent),
    "Перегрузка операторов",
  );
  await page.screenshot({
    path: path.join(output, "day-1-dark.png"),
    fullPage: true,
  });
  for (let day = 2; day <= 5; day++) {
    await click("День " + day);
    await page.waitForFunction((n) => location.hash === "#/day/" + n, {}, day);
    assert.equal(
      await page.$$eval(".day-cards .selected", (nodes) => nodes.length),
      1,
    );
  }
  await visit("day/1");
  await page.click('[aria-label="Сменить тему"]');
  assert.equal(await page.$eval("html", (n) => n.dataset.theme), "light");
  await page.screenshot({
    path: path.join(output, "day-1-light.png"),
    fullPage: true,
  });
  await page.click('[aria-label="Сменить тему"]');
  await visit("task/d1-q01");
  assert.equal(await page.$(".answer-review"), null);
  await page.click(".option");
  await click("Проверить ответ");
  await page.waitForSelector(".answer-review");
  assert.ok(
    (await page.$eval(".answer-review", (n) => n.textContent.length)) > 30,
  );
  await visit("task/d3-s02");
  await page.waitForSelector(".cm-content");
  const failedResponse = page.waitForResponse(
    (r) =>
      r.url().includes("/api/run/d3-s02") && r.request().method() === "POST",
    { timeout: 90000 },
  );
  await click("Скомпилировать");
  assert.equal((await (await failedResponse).json()).status, "COMPILE_ERROR");
  await page.click(".cm-content");
  await page.keyboard.down("Control");
  await page.keyboard.press("KeyA");
  await page.keyboard.up("Control");
  await page.keyboard.type(
    "template<class T> T identity(T value) { return value; }\n// focus persists",
  );
  await new Promise((r) => setTimeout(r, 1300));
  await page.keyboard.type(" while typing");
  assert.ok(
    (await page.$eval(".cm-content", (e) => e.textContent)).includes(
      "focus persists while typing",
    ),
  );
  await page.waitForFunction(() =>
    document
      .querySelector(".editor-status")
      .textContent.includes("Сохранено на диск"),
  );
  const goodResponse = page.waitForResponse(
    (r) =>
      r.url().includes("/api/run/d3-s02") && r.request().method() === "POST",
    { timeout: 90000 },
  );
  await click("Запустить тесты");
  const good = await (await goodResponse).json();
  assert.equal(good.status, "PASS", JSON.stringify(good));
  assert.ok(good.tests.length > 0);
  await click("notes.md");
  await page.click(".cm-content");
  await page.keyboard.type(
    "Infrastructure QA uses isolated temporary student data.",
  );
  await new Promise((r) => setTimeout(r, 1300));
  await click("solution.hpp");
  assert.ok(
    (await page.$eval(".cm-content", (e) => e.textContent)).includes(
      "template<class T>",
    ),
  );
  await page.screenshot({
    path: path.join(output, "workspace-dark.png"),
    fullPage: true,
  });
  await page.reload({ waitUntil: "networkidle0" });
  await page.waitForSelector(".cm-content");
  assert.ok(
    (await page.$eval(".cm-content", (e) => e.textContent)).includes(
      "focus persists while typing",
    ),
  );
  await visit("review");
  assert.ok(
    (await page.$eval("main", (e) => e.textContent)).includes(
      "Свободная функция",
    ),
  );
  await visit("report");
  assert.ok(
    (await page.$eval("main", (e) => e.textContent)).includes(
      "Готовность к лабораторной ещё не подтверждена",
    ),
  );
  await visit("day/1");
  await page.setViewport({ width: 390, height: 844 });
  await page.waitForFunction(
    () => document.querySelector(".sidebar").getBoundingClientRect().right <= 0,
  );
  await page.screenshot({
    path: path.join(output, "mobile.png"),
    fullPage: true,
  });
  assert.ok(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  );
  await page.click('[aria-label="Открыть навигацию"]');
  await page.waitForSelector(".sidebar.open");
  await click("Память и строки");
  await page.waitForFunction(() => location.hash === "#/day/2");
  await visit("task/d3-s02");
  await page.waitForSelector(".workspace-switch");
  assert.equal(await page.$eval(".coding-pane", e => getComputedStyle(e).display), "none");
  await click("Код и проверка");
  await page.waitForFunction(() => getComputedStyle(document.querySelector(".coding-pane")).display !== "none");
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.screenshot({path:path.join(output,"mobile-editor.png"),fullPage:true});
  await click("Условие и история");
  await page.waitForFunction(() => getComputedStyle(document.querySelector(".problem-pane")).display !== "none");
  await page.setViewport({ width: 1366, height: 768 });
  await visit("task/d3-s02");
  await page.waitForSelector(".cm-content");
  assert.ok(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  );
  await stop();
  await launch();
  await visit("task/d3-s02");
  await page.waitForSelector(".cm-content");
  assert.ok(
    (await page.$eval(".cm-content", (e) => e.textContent)).includes(
      "focus persists while typing",
    ),
  );
  const persisted = await (
    await fetch("http://127.0.0.1:8766/api/progress")
  ).json();
  assert.ok(
    persisted.attempts.some((a) => a.task === "d3-s02" && a.status === "PASS"),
  );
  assert.deepEqual(errors, []);
  console.log(
    "Browser QA PASS: 5-day navigation, themes, quiz, diagnostics, real C++ PASS, focus, autosave, multi-file editor, reload, history, server restart, mobile and laptop layout.",
  );
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
