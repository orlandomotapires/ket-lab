import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch, pressButton, replaceCode, solutionOf } from "./helpers";

// Browser mode: no server, the engine runs in the page (Pyodide in a Web Worker).
// The first start downloads and imports Qiskit and PennyLane: allow it time.
test.setTimeout(240_000);

test("browser mode: a lesson runs and is checked in the browser, progress stays in the browser", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "computational basis", "1.1");
  await replaceCode(page, solutionOf("1.1"));
  await expect(page.locator(".timeline")).toBeVisible();
  await pressButton(page, "Check");
  await expect(page.locator(".mission")).toHaveClass(/is-done/);
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("qlp.progress.v1") ?? "{}"));
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
