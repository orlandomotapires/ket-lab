import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch, pressButton, replaceCode, solutionOf } from "./helpers";

test("modo hospedado: progresso no navegador, com exportação e importação", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await expect(page.locator(".hub-extras")).toBeVisible();

  await openLessonBySearch(page, "computational basis", "1.1");
  await replaceCode(page, solutionOf("1.1"));
  await pressButton(page, "Check");
  await expect(page.locator(".mission")).toHaveClass(/is-done/);

  // O progresso sobrevive a recarregar a página: está no localStorage, não no motor.
  await page.reload();
  await expect(page.locator(".section-row.is-done").first()).toBeVisible();
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("qlp.progress.v1") ?? "{}"));
  expect(saved["1.1"].completed).toBe(true);

  // Exporta, apaga e importa de volta.
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export progress" }).click();
  const file = await (await download).path();
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await expect(page.locator(".section-row.is-done")).toHaveCount(0);
  await page.locator(".hub-extras input[type=file]").setInputFiles(file!);
  await expect(page.locator(".hub-extras [role=status]")).toContainText("Progress imported");
  await expect(page.locator(".section-row.is-done").first()).toBeVisible();
  expect(errors).toEqual([]);
});
