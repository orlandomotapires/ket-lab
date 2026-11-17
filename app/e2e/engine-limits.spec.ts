import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch, replaceCode, solutionOf } from "./helpers";

test("a large circuit keeps the full state only for some steps, and says so", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  // 10 qubits and 1,600 gates: over the engine's budget for full snapshots.
  await replaceCode(page, "from qiskit import QuantumCircuit\nqc = QuantumCircuit(10)\nfor layer in range(160):\n    for q in range(10):\n        qc.h(q)\n");
  await expect(page.locator(".timeline")).toContainText("1600", { timeout: 30_000 });
  const back = page.getByRole("button", { name: "Previous step" });
  // Steps with the full state are about ten apart: going back a few lands on a reduced one.
  for (let i = 0; i < 3; i++) await back.click();
  await expect(page.locator(".visualizer")).toContainText("Bloch spheres are shown for every step");
  expect(errors).toEqual([]);
});

test("a long Check can be stopped, and nothing is recorded", async ({ page }) => {
  await openHub(page);
  await openLessonBySearch(page, "hardware-efficient", "3.8");
  await replaceCode(page, solutionOf("3.8"));
  await page.locator(".oracle-actions").getByRole("button", { name: "Check", exact: true }).click();
  const stop = page.locator(".oracle-actions").getByRole("button", { name: "Stop", exact: true });
  await expect(stop).toBeVisible();
  await stop.click();
  await expect(stop).toHaveCount(0, { timeout: 15_000 });
  await expect(page.locator(".oracle")).not.toHaveClass(/is-success/);
  await expect(page.locator(".oracle-actions").getByRole("button", { name: "Check", exact: true })).toBeEnabled();
});
