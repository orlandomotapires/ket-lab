import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { openHub, openLessonBySearch } from "./helpers";

/** Violações graves de WCAG 2.1 A/AA na página atual. */
async function violations(page: Page) {
  const result = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  return result.violations
    .filter((v) => v.impact === "serious" || v.impact === "critical")
    .map((v) => `${v.id}: ${v.nodes.slice(0, 3).map((n) => n.target.join(" ")).join(" | ")}`);
}

for (const theme of ["light", "dark"] as const) {
  test(`acessibilidade (axe, tema ${theme}): hub e lição`, async ({ page }) => {
    await page.emulateMedia({ colorScheme: theme });
    await openHub(page);
    expect(await violations(page)).toEqual([]);
    await openLessonBySearch(page, "entanglement", "1.5");
    await page.waitForTimeout(800);
    expect(await violations(page)).toEqual([]);
  });
}

test("circuito navegável pelo teclado, com o passo anunciado", async ({ page }) => {
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
