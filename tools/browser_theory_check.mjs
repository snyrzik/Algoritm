import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import {
  existsSync,
  readdirSync,
  mkdtempSync,
  mkdirSync,
  rmSync,
  readFileSync,
} from "node:fs";
import { tmpdir, homedir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import puppeteer from "puppeteer-core";
import { python } from "./python.mjs";

const root = fileURLToPath(new URL("..", import.meta.url));
const profile = mkdtempSync(path.join(tmpdir(), "mastery-theory-browser-"));
const output = path.join(root, "test-results", "day01-theory");
mkdirSync(output, { recursive: true });
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
    "Set PUPPETEER_EXECUTABLE_PATH to installed Chrome/Chromium.",
  );
const backend = spawn(pythonExe, ["-m", "backend.server", "--port", "8767"], {
  cwd: root,
  env: { ...process.env, PYTHONUTF8: "1", MASTERY_DATA: profile },
  windowsHide: true,
  stdio: ["ignore", "pipe", "pipe"],
});
let serverLogs = "";
backend.stdout.on("data", (v) => (serverLogs += v));
backend.stderr.on("data", (v) => (serverLogs += v));
const base = "http://127.0.0.1:8767";
let browser;
async function click(text) {
  await page.waitForFunction(
    (t) =>
      [...document.querySelectorAll("button")].some((b) =>
        b.innerText.includes(t),
      ),
    {},
    text,
  );
  await page.evaluate(
    (t) =>
      [...document.querySelectorAll("button")]
        .find((b) => b.innerText.includes(t))
        .click(),
    text,
  );
}
async function visit(route) {
  await page.goto(base + "/#/" + route, { waitUntil: "networkidle0" });
}
let page;
try {
  for (let i = 0; i < 100; i++) {
    try {
      if ((await fetch(base + "/api/session")).ok) break;
    } catch {}
    if (i === 99) throw new Error(serverLogs);
    await new Promise((r) => setTimeout(r, 100));
  }
  const lecture = await (
    await fetch(base + "/api/theory/day-1/lecture-1")
  ).json();
  assert.equal(lecture.sections.length, 6);
  const source = readFileSync(
    path.join(root, "days/day-01-operators/theory/lecture-01/theory.md"),
  );
  assert.equal(
    createHash("sha256").update(source).digest("hex"),
    lecture.sourceSha256,
  );
  assert.equal(
    lecture.sections.map((s) => s.markdown).join(""),
    source.toString("utf8"),
  );
  browser = await puppeteer.launch({
    executablePath,
    headless: true,
    args: ["--disable-gpu"],
    defaultViewport: { width: 1440, height: 1080 },
  });
  page = await browser.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await visit("day/1");
  await page.waitForSelector(".day01-theory-entry");
  assert.ok(
    (await page.$eval(".day01-theory-entry", (e) => e.textContent)).includes(
      "0 / 4",
    ),
  );
  const course = await (await fetch(base + "/api/course")).json();
  assert.equal(course.tasks.filter((t) => t.day === 1).length, 52);
  await click("Читать лекцию");
  await page.waitForSelector(".theory-article");
  assert.ok(
    (await page.$eval(".theory-article", (e) => e.textContent)).includes(
      "Чему ты научишься за этот день",
    ),
  );
  await page.screenshot({
    path: path.join(output, "overview-dark.png"),
    fullPage: true,
  });
  for (const section of lecture.sections) {
    await visit("theory/1/" + section.id);
    await page.waitForSelector(".theory-article");
    const expected = renderToStaticMarkup(
      createElement(
        ReactMarkdown,
        { remarkPlugins: [remarkGfm] },
        section.markdown,
      ),
    );
    const mismatch = await page.evaluate((expectedHtml) => {
      const expected = document.createElement("div");
      expected.innerHTML = expectedHtml;
      const actual = document.querySelector(".theory-article .theory-markdown");
      const normalize = (s) => s.replace(/\s+/g, " ").trim();
      const selector = "h1,h2,h3,h4,p,li,th,td";
      const a = [...actual.querySelectorAll(selector)].map((e) =>
        normalize(e.textContent),
      );
      const b = [...expected.querySelectorAll(selector)].map((e) =>
        normalize(e.textContent),
      );
      if (JSON.stringify(a) !== JSON.stringify(b))
        return { type: "prose", actual: a, expected: b };
      const ac = [...actual.querySelectorAll("pre code")].map(
        (e) => e.textContent,
      );
      const bc = [...expected.querySelectorAll("pre code")].map(
        (e) => e.textContent,
      );
      return JSON.stringify(ac) === JSON.stringify(bc)
        ? null
        : { type: "examples", actual: ac, expected: bc };
    }, expected);
    assert.equal(
      mismatch,
      null,
      `Source altered in ${section.id}: ${JSON.stringify(mismatch)}`,
    );
    if (section.chapter) {
      assert.ok(await page.$(".theory-check-card"));
      assert.equal(await page.$$eval(".theory-check-card", (e) => e.length), 1);
      assert.ok(
        (await page.$$eval('.language-cpp [class^="tok-"]', (e) => e.length)) >
          0,
      );
      if (section.chapter === 1) {
        assert.ok(await page.$(".theory-memory"));
        await page.screenshot({
          path: path.join(output, "chapter-1-dark.png"),
          fullPage: false,
        });
      }
      await click("Открыть редактор");
      await page.waitForSelector(".cm-content");
      assert.ok(
        (await page.$eval(".exercise-title", (e) => e.textContent)).includes(
          section.checkId,
        ),
      );
      assert.ok(
        (await page.$eval(".cm-content", (e) => e.textContent)).includes(
          "Напишите класс с нуля",
        ),
      );
      assert.ok(
        !(await page.$eval(".cm-content", (e) => e.textContent)).includes(
          "class ",
        ),
      );
      if (section.chapter === 1) {
        await click("test_adapter.hpp");
        assert.ok(
          (await page.$eval(".cm-content", (e) => e.textContent)).includes(
            "score_read",
          ),
        );
        await click("solution.hpp");
      }
      await click(`Лекция № 1 · Глава ${section.chapter}`);
      await page.waitForSelector(".theory-article");
      assert.ok(
        (
          await page.$eval(".theory-article h1", (e) => e.textContent)
        ).startsWith(`Глава ${section.chapter}.`),
      );
    }
  }
  await visit("theory/1/chapter-1");
  await page.waitForSelector(".theory-section-toc");
  await page.click(".theory-section-toc summary");
  await click("1.2. Что находится в памяти");
  await page.waitForFunction(() => location.hash.includes("/theory-1-2-"));
  await page.reload({ waitUntil: "networkidle0" });
  await page.waitForSelector(".theory-article");
  await page.waitForFunction(
    () =>
      document
        .querySelector('.theory-article h2[id*="1-2"]')
        .getBoundingClientRect().top < 100,
  );
  await page.click('[aria-label="Сменить тему"]');
  await page.waitForFunction(
    () => document.documentElement.dataset.theme === "light",
  );
  await page.screenshot({
    path: path.join(output, "chapter-1-light.png"),
    fullPage: false,
  });
  await visit("theory/1/chapter-4");
  await page.waitForSelector(".theory-check-card");
  await page.setViewport({ width: 390, height: 844 });
  await page.waitForFunction(
    () => document.querySelector(".sidebar").getBoundingClientRect().right <= 0,
  );
  assert.ok(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  );
  await page.click(".theory-mobile-menu");
  await page.waitForSelector(".theory-navigation.is-open");
  await click("Класс как тип: конструкторы");
  await page.waitForFunction(() => location.hash === "#/theory/1/chapter-1");
  assert.ok(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  );
  await page.screenshot({
    path: path.join(output, "mobile-theory.png"),
    fullPage: true,
  });
  await click("Открыть редактор");
  await page.waitForSelector(".workspace-switch");
  await click("Код и проверка");
  await page.waitForSelector(".cm-content");
  const response = page.waitForResponse(
    (r) =>
      r.url().includes("/api/run/d1-l1-c01") && r.request().method() === "POST",
    { timeout: 90000 },
  );
  await click("Скомпилировать");
  const result = await (await response).json();
  assert.equal(result.status, "COMPILE_ERROR");
  await page.screenshot({
    path: path.join(output, "mobile-check.png"),
    fullPage: true,
  });
  await visit("day/2");
  await page.waitForSelector("h1");
  assert.equal(await page.$(".day01-theory-entry"), null);
  await visit("theory/1/summary");
  await page.waitForSelector(".theory-practice-card");
  await click("Открыть практику A/B/C");
  await page.waitForFunction(() => location.hash === "#/day/1/practice");
  await page.waitForFunction(() =>
    document.querySelector(".tabs .active")?.textContent.includes("Практика"),
  );
  assert.equal(await page.$$eval(".task-row", (rows) => rows.length), 8);
  const progress = await (await fetch(base + "/api/progress")).json();
  assert.ok(!progress.attempts.some((a) => a.status === "PASS"));
  assert.deepEqual(errors, []);
  console.log(
    "Theory browser QA PASS: complete verbatim prose and examples in all six sections; four chapter checks; C++ highlighting; memory diagrams; TOC deep links; reload; light/dark; mobile navigation/editor; real compile errors; original Day 1/other days preserved.",
  );
} finally {
  if (browser) await browser.close();
  if (backend.exitCode === null)
    await new Promise((r) => {
      backend.once("exit", r);
      backend.kill();
    });
  const absolute = path.resolve(profile);
  if (
    absolute.startsWith(path.resolve(tmpdir()) + path.sep) &&
    path.basename(absolute).startsWith("mastery-theory-browser-")
  )
    rmSync(absolute, { recursive: true, force: true });
}
