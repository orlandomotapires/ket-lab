import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonFromHub } from "./helpers";

const catalog = JSON.parse(
  readFileSync(resolve(dirname(fileURLToPath(import.meta.url)), "..", "..", "content", "catalog.json"), "utf-8"),
);
const ids: string[] = catalog.tracks.flatMap((track: { sections: { id: string }[] }) => track.sections.map((s) => s.id));

test("all lessons open, run the starting code and produce no errors", async ({ page }) => {
  test.setTimeout(10 * 60_000);
  const errors = collectErrors(page);
  await openHub(page);
  for (const id of ids) {
    await openLessonFromHub(page, id);
    await expect(page.locator(".crumb-id")).toHaveText(id);
    await expect(page.locator(".crumbs strong")).not.toBeEmpty();
    await expect(page.locator(".recap li").first()).toBeAttached();
    // The starting code runs without error (training lessons only run from the button, so there is no error to show).
    await expect(page.locator(".oracle"), `lesson ${id}: the starting code showed an error`).not.toHaveClass(/is-error/, { timeout: 20_000 });
    await expect(page.locator(".visualizer")).toBeVisible();
    await page.getByRole("button", { name: "Tracks" }).click();
    await expect(page.locator(".section-row").first()).toBeVisible();
  }
  expect(errors).toEqual([]);
});
