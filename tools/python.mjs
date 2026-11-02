import { spawn, spawnSync } from "node:child_process";
export function python() {
  for (const [bin, prefix] of process.platform === "win32"
    ? [
        ["py", ["-3"]],
        ["python", []],
      ]
    : [
        ["python3", []],
        ["python", []],
      ]) {
    if (
      spawnSync(bin, [...prefix, "--version"], { windowsHide: true }).status ===
      0
    )
      return [bin, prefix];
  }
  throw new Error("Установите Python 3.10+ и добавьте его в PATH.");
}
if (process.argv[1]?.endsWith("python.mjs")) {
  const [bin, prefix] = python();
  const child = spawn(bin, [...prefix, ...process.argv.slice(2)], {
    stdio: "inherit",
    windowsHide: true,
    env: { ...process.env, PYTHONUTF8: "1" },
  });
  child.on("exit", (code) => process.exit(code ?? 1));
}
