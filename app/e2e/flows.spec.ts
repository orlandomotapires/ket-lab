import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch, pressButton, replaceCode, solutionOf } from "./helpers";

test("o hub carrega e a busca abre a lição certa", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await expect(page.locator(".hub-side h1")).toHaveText("Learning tracks");
  await openLessonBySearch(page, "entanglement", "1.5");
  await expect(page.locator(".lesson-title")).toContainText("Entanglement");
  expect(errors).toEqual([]);
});

test("lição da Trilha 1: resolver e validar", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "computational basis", "1.1");
  await expect(page.locator(".mission")).not.toHaveClass(/is-done/);
  await replaceCode(page, solutionOf("1.1"));
  await expect(page.locator(".circuit .gate")).toHaveCount(1);
  await pressButton(page, "Check");
  await expect(page.locator(".oracle")).toHaveClass(/is-success/);
  await expect(page.locator(".mission")).toHaveClass(/is-done/);
  expect(errors).toEqual([]);
});

test("lição com oráculos secretos: código inicial falha, solução passa", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "Deutsch-Jozsa", "2.3");
  await pressButton(page, "Check");
  await expect(page.locator(".oracle")).toHaveClass(/is-(warn|error)/);
  await replaceCode(page, solutionOf("2.3"));
  await pressButton(page, "Check");
  await expect(page.locator(".oracle")).toHaveClass(/is-success/);
  expect(errors).toEqual([]);
});

test("laboratório livre: treino com curva ao vivo e Parar", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  await page.locator(".example-picker select").selectOption("training");
  await pressButton(page, "Run");
  await expect(page.locator(".oracle-message")).toContainText("Training finished after 80 steps", { timeout: 45_000 });
  await expect(page.locator(".visualizer [role=tab][aria-selected=true]")).toHaveText("Convergence");

  await replaceCode(page, "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\ni = 0\nwhile True:\n    i += 1\n    if i % 200000 == 0:\n        report(i)\n");
  await pressButton(page, "Run");
  await expect(page.locator(".pill-live")).toBeVisible({ timeout: 20_000 });
  await pressButton(page, "Stop");
  await expect(page.locator(".oracle-message")).toContainText("Execution stopped.");
  expect(errors).toEqual([]);
});

test("exportação em OpenQASM 3 e 2", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  await page.locator(".example-picker select").selectOption("bell");
  await page.locator(".circuit-panel").getByRole("button", { name: "Export" }).click();
  await expect(page.locator(".export-code")).toContainText("OPENQASM 3.0;");
  await expect(page.locator(".export-code")).toContainText("cx q[0], q[1];");
  await page.locator(".export-dialog").getByRole("tab", { name: "OpenQASM 2" }).click();
  await expect(page.locator(".export-code")).toContainText("OPENQASM 2.0;");
  await page.keyboard.press("Escape");
  await expect(page.locator(".export-dialog")).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("os dois temas renderizam sem erros", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  const before = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await page.locator(".topbar .btn-icon").click();
  const after = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  expect(after).not.toEqual(before);
  await openLessonBySearch(page, "teleportation", "1.6");
  await expect(page.locator(".references li")).not.toHaveCount(0);
  expect(errors).toEqual([]);
});
