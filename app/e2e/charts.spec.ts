import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch, replaceCode, solutionOf } from "./helpers";

for (const scheme of ["light", "dark"] as const) {
  test(`lesson without a circuit (${scheme}): chart tab and variables tab, no serious axe violations`, async ({ page }) => {
    const errors = collectErrors(page);
    await page.emulateMedia({ colorScheme: scheme });
    await openHub(page);
    await openLessonBySearch(page, "adiabatic", "6.2");
    const tabs = page.locator(".visualizer .segmented");
    await expect(tabs.getByRole("button", { name: "Chart" })).toHaveAttribute("aria-pressed", "true");
    // The data dir is shared: the second run already finds the solution in the editor.
    if (scheme === "light") await expect(page.locator(".visualizer")).toContainText("The chart appears once your code computes");

    await replaceCode(page, solutionOf("6.2"));
    // Two charts: the gap against s with its minimum marked, and the success probability against T.
    await expect(page.locator(".curve-chart")).toHaveCount(2, { timeout: 30_000 });
    await expect(page.locator(".curve-chart").first()).toContainText("smallest gap, 0.136");
    await expect(page.locator(".curve-chart svg.curve-svg")).toHaveCount(2);
    await expect(page.locator(".curve-chart").nth(1)).toContainText("log scale");

    await page.waitForTimeout(500);
    const result = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
    const serious = result.violations.filter((v) => v.impact === "serious" || v.impact === "critical");
    expect(serious.map((v) => `${v.id}: ${v.nodes.slice(0, 3).map((n) => n.target.join(" ")).join(" | ")}`)).toEqual([]);

    await tabs.getByRole("button", { name: "Variables" }).click();
    await expect(page.locator(".variables-table")).toBeVisible();
    await expect(page.locator(".curve-chart")).toHaveCount(0);
    await tabs.getByRole("button", { name: "Chart" }).click();
    await expect(page.locator(".curve-chart")).toHaveCount(2);
    expect(errors).toEqual([]);
  });
}

// Skipped: the theory panel (theory text, hints, solution offer, recap, further reading) is hidden
// in the mission-on-top layout. Turn back on when it returns.
test.skip("the reading position is remembered per lesson", async ({ page }) => {
  await page.setViewportSize({ width: 1366, height: 768 });
  await openHub(page);
  await openLessonBySearch(page, "entanglement", "1.5");
  const scroll = page.locator(".theory-scroll");
  await scroll.evaluate((el) => (el.scrollTop = 600));
  await expect.poll(() => scroll.evaluate((el) => el.scrollTop)).toBeGreaterThan(100);

  // Reading position: leave the lesson and come back.
  const position = await scroll.evaluate((el) => el.scrollTop);
  await page.waitForTimeout(400);
  await page.getByRole("button", { name: "Tracks" }).click();
  await openLessonBySearch(page, "entanglement", "1.5");
  await expect.poll(() => scroll.evaluate((el) => el.scrollTop)).toBeGreaterThan(position - 5);
});

test("references: two lesson chips per row with a +N button", async ({ page }) => {
  await openHub(page);
  await page.getByRole("button", { name: /^References/ }).click();
  await expect(page.locator(".bibliography h1")).toBeVisible();
  await expect(page.getByLabel("Lessons from")).toBeVisible();
  const row = page.locator(".bib-lessons", { has: page.locator(".bib-more") }).first();
  await expect(row.locator(".bib-lesson:not(.bib-more)")).toHaveCount(2);
  await row.locator(".bib-more").click();
  expect(await row.locator(".bib-lesson:not(.bib-more)").count()).toBeGreaterThan(2);
});
