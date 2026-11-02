import { spawn, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { python } from "./python.mjs";
process.chdir(fileURLToPath(new URL("..", import.meta.url)));
const [bin, prefix] = python();
const env = { ...process.env, PYTHONUTF8: "1" };
const setup = spawnSync(bin, [...prefix, "tools/build_course.py"], {
  stdio: "inherit",
  env,
  windowsHide: true,
});
if (setup.status !== 0) process.exit(setup.status ?? 1);
const dev = process.argv.includes("--dev");
if (!dev && !existsSync("app/dist/index.html")) {
  const build = spawnSync(
    process.execPath,
    ["node_modules/vite/bin/vite.js", "build"],
    { stdio: "inherit", windowsHide: true },
  );
  if (build.status !== 0) process.exit(build.status ?? 1);
}
const children = [
  spawn(bin, [...prefix, "-m", "backend.server"], {
    stdio: "inherit",
    env,
    windowsHide: true,
  }),
];
if (dev)
  children.push(
    spawn(process.execPath, ["node_modules/vite/bin/vite.js"], {
      stdio: "inherit",
      windowsHide: true,
    }),
  );
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const c of children) c.kill();
  process.exit(code);
}
process.on("SIGINT", () => stop());
process.on("SIGTERM", () => stop());
for (const c of children) c.on("exit", (code) => stop(code ?? 1));
