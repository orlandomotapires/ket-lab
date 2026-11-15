import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test } from "@playwright/test";
import { collectErrors, openHub } from "./helpers";

const catalog = JSON.parse(
  readFileSync(resolve(dirname(fileURLToPath(import.meta.url)), "..", "..", "content", "catalog.json"), "utf-8"),
);
const ids: string[] = catalog.tracks.flatMap((track: { sections: { id: string }[] }) => track.sections.map((s) => s.id));

test("todas as lições abrem, rodam o código inicial e não geram erros", async ({ page }) => {
  test.setTimeout(10 * 60_000);
  const errors = collectErrors(page);
  await openHub(page);
  for (const id of ids) {
    await page.locator(".section-row", { has: page.locator(".section-id", { hasText: new RegExp(`^${id.replace(".", "\\.")}$`) }) }).click();
    await expect(page.locator(".crumb-id")).toHaveText(id);
    await expect(page.locator(".lesson-title")).not.toBeEmpty();
    await expect(page.locator(".objectives li").first()).toBeVisible();
    // O código inicial executa sem erro (lições de treino só rodam pelo botão, então não há erro a mostrar).
    await expect(page.locator(".oracle"), `lição ${id}: o código inicial mostrou erro`).not.toHaveClass(/is-error/, { timeout: 20_000 });
    await expect(page.locator(".visualizer")).toBeVisible();
    await page.getByRole("button", { name: "Tracks" }).click();
    await expect(page.locator(".section-row").first()).toBeVisible();
  }
  expect(errors).toEqual([]);
});
