import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { openHub, openLessonBySearch, openNotesDrawer } from "./helpers";

/** Serious WCAG 2.1 A/AA violations on the current page. */
async function violations(page: Page) {
  const result = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  return result.violations
    .filter((v) => v.impact === "serious" || v.impact === "critical")
    .map((v) => `${v.id}: ${v.nodes.slice(0, 3).map((n) => n.target.join(" ")).join(" | ")}`);
}

for (const theme of ["light", "dark"] as const) {
  test(`accessibility (axe, ${theme} theme): hub and lesson`, async ({ page }) => {
    await page.emulateMedia({ colorScheme: theme });
    await openHub(page);
    expect(await violations(page)).toEqual([]);
    await openLessonBySearch(page, "entanglement", "1.5");
    await page.waitForTimeout(800);
    expect(await violations(page)).toEqual([]);
  });
}

for (const theme of ["light", "dark"] as const) {
  test(`accessibility (axe, ${theme} theme): references, notes, review and notes drawer`, async ({ page }) => {
    await page.emulateMedia({ colorScheme: theme });
    await openHub(page);

    await page.getByRole("button", { name: /^References/ }).click();
    await expect(page.locator(".bibliography h1")).toBeVisible();
    expect(await violations(page), "references").toEqual([]);
    await page.getByRole("button", { name: "Back to tracks" }).click();

    await page.getByRole("button", { name: /^Glossary/ }).click();
    await expect(page.locator(".glossary-page")).toBeVisible();
    expect(await violations(page), "glossary").toEqual([]);
    await page.getByRole("button", { name: "Back to tracks" }).click();

    await page.getByRole("button", { name: /^Notes/ }).click();
    await expect(page.locator(".notes-page")).toBeVisible();
    expect(await violations(page), "notes page (empty or not)").toEqual([]);
    await page.getByLabel("General", { exact: true }).fill("a note, so the page has a card");
    await expect(page.locator(".note-status")).toHaveText("Saved");
    expect(await violations(page), "notes page with text").toEqual([]);
    await page.getByLabel("General", { exact: true }).fill("");
    await expect(page.locator(".note-status")).toHaveText("Saved");
    await page.getByRole("button", { name: "Back to tracks" }).click();

    await page.locator("#track-1 .review-row").click();
    await expect(page.locator(".review-question")).toBeVisible();
    expect(await violations(page), "review question").toEqual([]);
    await page.locator(".option").first().click();
    expect(await violations(page), "review answered").toEqual([]);
    await page.getByRole("button", { name: "Back to tracks" }).click();

    await openLessonBySearch(page, "interference", "1.4");
    await openNotesDrawer(page);
    await page.waitForTimeout(800);
    expect(await violations(page), "notes drawer in the lab").toEqual([]);
  });
}

test("circuit navigable by keyboard, with the step announced", async ({ page }) => {
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  await page.locator(".example-picker select").selectOption("bell");
  await expect(page.locator(".circuit .gate")).toHaveCount(2);
  await page.locator(".circuit-scroll").focus();
  await page.keyboard.press("Home");
  await expect(page.locator("#circuit-current")).toHaveText("Initial state");
  await page.keyboard.press("ArrowRight");
  await expect(page.locator("#circuit-current")).toContainText("Step 1 of");
  await expect(page.locator(".timeline-count")).toContainText("Step 1 of");
  await expect(page.locator("#state-description")).toContainText("Qubit 0: Bloch vector");
});
