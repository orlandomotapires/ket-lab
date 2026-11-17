import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch } from "./helpers";

test("glossary page: every term, a filter and the lesson that introduces each", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: /^Glossary/ }).click();
  await expect(page.locator(".glossary-page h1")).toHaveText("Glossary");
  const entries = page.locator(".glossary-entry");
  expect(await entries.count()).toBeGreaterThan(100);
  // Alphabetical, under letter headings.
  const terms = await page.locator(".glossary-entry dt").allTextContents();
  const folded = terms.map((term) => term.toLowerCase().replace(/^[^a-z0-9]+/, ""));
  expect(folded).toEqual([...folded].sort((a, b) => a.localeCompare(b)));
  await expect(page.locator(".glossary-letter").first()).toBeVisible();

  await page.getByLabel("Filter terms").fill("teleportation");
  await expect(page.locator(".glossary-entry dt").first()).toHaveText("quantum teleportation");
  expect(await entries.count()).toBeLessThan(20);
  await page.getByLabel("Filter terms").fill("zzzz no such term");
  await expect(page.locator(".notes-empty")).toContainText("No term matches");

  // Each entry links to its lesson.
  await page.getByLabel("Filter terms").fill("no-cloning");
  const entry = page.locator(".glossary-entry", { has: page.locator("dt", { hasText: /^no-cloning theorem$/ }) });
  await entry.getByRole("button", { name: /^Lesson / }).click();
  await expect(page.locator(".crumb-id")).toBeVisible();
  expect(errors).toEqual([]);
});

test("a term in the theory opens its glossary entry, and Back returns to the lesson as it was", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "interference", "1.4");
  await page.locator(".editor .view-lines").click();
  await page.keyboard.press("ControlOrMeta+End");
  await page.keyboard.type("# kept while I look something up");
  const term = page.locator(".glossary-term").first();
  const name = (await term.getAttribute("aria-describedby")) ?? "";
  expect(name).toMatch(/^term-/);
  // Hover still shows the definition in place.
  await term.hover();
  await expect(term.locator(".glossary-tip")).toBeVisible();
  await term.click();
  await expect(page.locator(".glossary-page")).toBeVisible();
  await expect(page.locator(".glossary-entry.is-focus")).toBeInViewport();
  await page.getByRole("button", { name: "Back to the lesson" }).click();
  await expect(page.locator(".crumb-id")).toHaveText("1.4");
  await expect(page.locator(".editor .view-lines")).toContainText("kept");
  expect(errors).toEqual([]);
});

test("search finds glossary terms and opens the entry", async ({ page }) => {
  await openHub(page);
  await page.locator(".search input").fill("pseudo-threshold");
  const hit = page.locator(".search-result", { has: page.locator(".search-result-title", { hasText: /^pseudo-threshold$/ }) });
  await expect(page.locator(".search-group", { hasText: "In the glossary" })).toBeVisible();
  await hit.click();
  await expect(page.locator(".glossary-entry.is-focus dt")).toHaveText("pseudo-threshold");
  await page.getByRole("button", { name: "Back to tracks" }).click();
  await expect(page.locator(".section-row").first()).toBeVisible();
});
