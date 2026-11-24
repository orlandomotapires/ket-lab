import { expect, test, type Page } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch, pressButton, replaceCode, solutionOf } from "./helpers";

// Browser mode: no server, the engine runs in the page (Pyodide in a Web Worker).
// The first start downloads and imports Qiskit and PennyLane: allow it time.
test.setTimeout(240_000);

// On a failure, the CI log shows what the page showed and what the browser said: the
// browser-only failures (Firefox, WebKit on CI) cannot be reproduced on every machine.
const consoleLog = new WeakMap<Page, string[]>();
test.beforeEach(({ page }) => {
  const lines: string[] = [];
  consoleLog.set(page, lines);
  const stamp = () => new Date().toISOString().slice(11, 23);
  page.on("console", (message) => lines.push(`${stamp()} [${message.type()}] ${message.text()}`));
  page.on("pageerror", (error) => lines.push(`${stamp()} [pageerror] ${error.message}`));
  page.on("crash", () => lines.push(`${stamp()} [crash] the page crashed`));
});

test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status === testInfo.expectedStatus) return;
  const text = async (selector: string) => {
    const element = page.locator(selector).first();
    try {
      if ((await element.count()) === 0) return "(none)";
      const [classes, content] = await Promise.all([element.getAttribute("class", { timeout: 2000 }), element.innerText({ timeout: 2000 })]);
      return `class="${classes}"\n${content}`;
    } catch (error) {
      return `(could not read: ${error instanceof Error ? error.message.split("\n")[0] : error})`;
    }
  };
  const report = [
    `== ${testInfo.project.name} › ${testInfo.title} (retry ${testInfo.retry})`,
    `-- .oracle: ${await text(".oracle")}`,
    `-- .engine-loading: ${await text(".engine-loading")}`,
    `-- .banner: ${await text(".banner")}`,
    `-- console:`,
    ...(consoleLog.get(page) ?? []),
  ].join("\n");
  console.log(report);
  await testInfo.attach("diagnostics.txt", { body: report, contentType: "text/plain" });
});

/** On a phone the lab shows one panel at a time: opens it from the tabs (no-op on wide screens). */
async function showPanel(page: Page, name: "Code" | "State"): Promise<void> {
  const tabs = page.locator(".lab-tabs");
  if (await tabs.isVisible()) await tabs.getByRole("tab", { name }).click();
}

test("browser mode: a lesson runs and is checked in the browser, progress stays in the browser", async ({ page }) => {
  const errors = collectErrors(page);
  await page.addInitScript(() => localStorage.setItem("ket-lab.tour.v1", "1"));
  await page.goto("/");
  // While Python starts, the banner says which step it is on; it goes away when ready.
  const loading = page.locator(".engine-loading");
  await expect(loading).toContainText(/Step [1-5] of 5/);
  await expect(loading).toHaveCount(0);
  await expect(page.locator(".section-row").first()).toBeVisible();
  await openLessonBySearch(page, "computational basis", "1.1");
  await showPanel(page, "Code");
  await replaceCode(page, solutionOf("1.1"));
  // The engine in the page ran the code: the state after the X gate is shown.
  await showPanel(page, "State");
  await expect(page.locator(".visualizer")).toContainText("After step");
  await pressButton(page, "Check");
  await expect(page.locator(".mission")).toHaveClass(/is-done/);
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("ket-lab.progress.v1") ?? "{}"));
  expect(saved["1.1"].completed).toBe(true);
  expect(errors).toEqual([]);
});

test("browser mode: an infinite loop times out, and the engine keeps working", async ({ page }) => {
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  await replaceCode(page, "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nwhile True:\n    pass\n");
  await expect(page.locator(".oracle")).toContainText("took longer than", { timeout: 60_000 });
  // The timeout terminated the worker; a new one starts and serves the next edit.
  await replaceCode(page, "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n");
  await expect(page.locator(".oracle")).not.toHaveClass(/is-error/, { timeout: 120_000 });
  await expect(page.locator(".oracle")).not.toContainText("took longer than");
});

test("browser mode: too much memory gets a clear message, and the memory is given back", async ({ page }) => {
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  // Over 2 GB: NumPy refuses under WebAssembly; the message is the engine's memory one.
  await replaceCode(page, "import numpy as np\nfrom qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\na = np.zeros((40000, 40000))\n");
  await expect(page.locator(".oracle")).toContainText("too much memory", { timeout: 60_000 });
  // 1.6 GB: it works, and the page replaces the worker afterwards to give the memory back.
  await replaceCode(page, "import numpy as np\nfrom qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\na = np.ones((14000, 14000))\n");
  await expect(page.locator(".engine-loading")).toContainText("free memory", { timeout: 60_000 });
  await expect(page.locator(".engine-loading")).toHaveCount(0);
  await replaceCode(page, "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n");
  await expect(page.locator(".oracle")).not.toHaveClass(/is-error/);
});
