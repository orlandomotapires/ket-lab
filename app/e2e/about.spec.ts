import { readFileSync } from "node:fs";
import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch } from "./helpers";

test("about dialog: opens from the top bar, describes the tracks and links to the references", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: "About Ket Lab" }).click();
  const dialog = page.getByRole("dialog", { name: "About Ket Lab" });
  await expect(dialog).toBeVisible();
  // One entry per track, with its real title and size.
  await expect(dialog.locator(".about-tracks li")).toHaveCount(7);
  await expect(dialog.locator(".about-tracks li").nth(6)).toContainText("Quantum Annealing");
  await expect(dialog.locator(".about-tracks li").nth(1)).toContainText("Basics of Quantum Information");
  await expect(dialog.locator(".about-tracks li").nth(1)).toContainText("11 lessons");
  await expect(dialog).toContainText("53 lessons");
  await expect(dialog).toContainText("Everything runs on your own computer");
  // The version comes from package.json and links to that release's notes.
  const version = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf-8")).version;
  const versionLink = dialog.getByRole("link", { name: `Ket Lab ${version}` });
  await expect(versionLink).toHaveAttribute("href", `https://github.com/orlandomotapires/ket-lab/releases/tag/v${version}`);

  const result = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  expect(result.violations.filter((v) => v.impact === "serious" || v.impact === "critical").map((v) => v.id)).toEqual([]);

  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();

  await page.getByRole("button", { name: "About Ket Lab" }).click();
  await dialog.getByRole("button", { name: "See all references" }).click();
  await expect(dialog).toBeHidden();
  await expect(page.locator(".bibliography h1")).toBeVisible();
  expect(errors).toEqual([]);
});

test("about dialog is also reachable inside a lesson and leaves the lesson as it was", async ({ page }) => {
  await openHub(page);
  await openLessonBySearch(page, "Bernstein", "2.4");
  await page.getByRole("button", { name: "About Ket Lab" }).click();
  await expect(page.getByRole("dialog", { name: "About Ket Lab" })).toBeVisible();
  await page.getByRole("dialog").getByRole("button", { name: "Close" }).click();
  await expect(page.locator(".crumb-id")).toHaveText("2.4");
});
