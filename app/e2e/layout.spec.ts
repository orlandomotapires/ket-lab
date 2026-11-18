import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test, type Page } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch, openLessonFromHub, pressButton, replaceCode, resetCode, solutionOf } from "./helpers";

const catalog = JSON.parse(
  readFileSync(resolve(dirname(fileURLToPath(import.meta.url)), "..", "..", "content", "catalog.json"), "utf-8"),
);
const ids: string[] = catalog.tracks.flatMap((track: { sections: { id: string }[] }) => track.sections.map((s) => s.id));

/** The mission's first line and the hint button (when the lesson has hints) are inside the
 *  theory panel's visible area, without scrolling anything. */
async function expectMissionVisible(page: Page, label: string): Promise<void> {
  const viewport = page.viewportSize()!;
  const scroll = (await page.locator(".theory-scroll").boundingBox())!;
  const text = (await page.locator(".mission .mission-text").boundingBox())!;
  const within = (box: { x: number; y: number; width: number; height: number }) =>
    box.y >= scroll.y - 1 && box.y + Math.min(box.height, 22) <= Math.min(scroll.y + scroll.height, viewport.height) + 1;
  expect(within(text), `${label}: first line of the mission is cut off`).toBe(true);
  const hint = page.locator(".mission").getByRole("button", { name: /Show hint/ });
  if ((await hint.count()) > 0) {
    const box = (await hint.boundingBox())!;
    expect(
      box.y >= scroll.y - 1 && box.y + box.height <= Math.min(scroll.y + scroll.height, viewport.height) + 1,
      `${label}: the hint button is cut off`,
    ).toBe(true);
  }
}

test("1366x768: every lesson shows its mission and the hint button without scrolling", async ({ page }) => {
  test.setTimeout(10 * 60_000);
  const errors = collectErrors(page);
  await page.setViewportSize({ width: 1366, height: 768 });
  await openHub(page);
  for (const id of ids) {
    await openLessonFromHub(page, id);
    await expect(page.locator(".crumb-id")).toHaveText(id);
    await expect(page.locator(".mission .mission-text")).toBeVisible();
    await expectMissionVisible(page, `lesson ${id}`);
    await page.getByRole("button", { name: "Tracks" }).click();
    await expect(page.locator(".section-row").first()).toBeVisible();
  }
  expect(errors).toEqual([]);
});

test("1366x768: with all hints open the mission and the page scroll stay put", async ({ page }) => {
  await page.setViewportSize({ width: 1366, height: 768 });
  await openHub(page);
  await openLessonBySearch(page, "entanglement", "1.5");
  const before = (await page.locator(".mission .mission-text").boundingBox())!;
  for (let i = 0; i < 3; i++) await page.getByRole("button", { name: /Show hint/ }).click();
  await expect(page.locator(".hints li")).toHaveCount(3);
  await expectMissionVisible(page, "lesson 1.5 with hints");
  const after = (await page.locator(".mission .mission-text").boundingBox())!;
  expect(after.y).toBe(before.y);
  // The mission card stays pinned while the theory scrolls.
  await page.locator(".theory-scroll").evaluate((el) => (el.scrollTop = el.scrollHeight));
  const pinned = (await page.locator(".mission-pin").boundingBox())!;
  const scroll = (await page.locator(".theory-scroll").boundingBox())!;
  expect(Math.abs(pinned.y - scroll.y)).toBeLessThanOrEqual(2);
});

test("390px: the mission is visible on the Theory tab and the bottom bar is one line", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openHub(page);
  await openLessonBySearch(page, "entanglement", "1.5");
  await expect(page.locator(".mission .mission-text")).toBeVisible();
  await expectMissionVisible(page, "lesson 1.5 at 390px");
  const bar = (await page.locator(".oracle").boundingBox())!;
  expect(bar.height).toBeLessThan(70);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
});

test("Reset code asks before it discards the learner's code", async ({ page }) => {
  await openHub(page);
  await openLessonBySearch(page, "computational basis", "1.1");
  await replaceCode(page, solutionOf("1.1"));
  await expect(page.locator(".circuit .gate")).toHaveCount(1);
  const bar = page.locator(".oracle-actions");
  // Not on the bar itself: it is behind "More".
  await expect(bar.getByRole("button", { name: "Reset code" })).toHaveCount(0);
  await bar.getByRole("button", { name: "More", exact: true }).click();
  await bar.getByRole("button", { name: "Reset code", exact: true }).click();
  await expect(page.getByText("This discards your code")).toBeVisible();
  await bar.getByRole("button", { name: "Keep my code" }).click();
  await expect(page.locator(".circuit .gate")).toHaveCount(1);
  await resetCode(page);
  await expect(page.locator(".circuit .gate")).toHaveCount(0);
});

test("Check is the one main action, then Next lesson", async ({ page }) => {
  await openHub(page);
  await openLessonBySearch(page, "computational basis", "1.1");
  await expect(page.locator(".oracle-actions .btn-primary")).toHaveCount(1);
  await expect(page.locator(".oracle-actions .btn-primary")).toHaveText("Check");
  await replaceCode(page, solutionOf("1.1"));
  await pressButton(page, "Check");
  await expect(page.locator(".oracle")).toHaveClass(/is-success/);
  await expect(page.locator(".oracle-actions .btn-primary")).toHaveText("Next lesson");
});

test("objectives: an \"i\" next to the lesson name shows them on hover; the lesson reads them back at the end", async ({ page }) => {
  await openHub(page);
  // Hub: the "i" in the next lesson's row, and the row describes the goals to screen readers.
  const row = page.locator(".section-row.is-next");
  await expect(row).toHaveAttribute("aria-describedby", /^goals-/);
  await row.locator(".lesson-info").hover();
  const pop = page.getByRole("tooltip");
  await expect(pop).toContainText("What you will learn");
  await expect(pop.locator("li").first()).toBeVisible();
  await page.mouse.move(0, 0);
  await expect(pop).toHaveCount(0);

  // Lesson: no title or goals above the mission; the "i" is in the top bar, by keyboard too.
  await openLessonBySearch(page, "entanglement", "1.5");
  await expect(page.locator(".theory h1")).toHaveCount(0);
  const info = page.getByRole("button", { name: "What you will learn" });
  await info.focus();
  await expect(pop).toContainText(/About \d+ min/);
  await page.keyboard.press("Escape");
  await expect(pop).toHaveCount(0);
  const recap = page.locator(".recap");
  await expect(recap.locator("li").first()).toBeAttached();
  const recapTop = (await recap.boundingBox())!.y;
  const lastHeading = (await page.locator(".prose > h2").last().boundingBox())!.y;
  expect(recapTop).toBeGreaterThan(lastHeading);
});

test("further reading: folded at the end, and the solved mission links to it", async ({ page }) => {
  await openHub(page);
  await openLessonBySearch(page, "computational basis", "1.1");
  const toggle = page.getByRole("button", { name: /^Further reading \(\d+\)/ });
  await expect(toggle).toHaveAttribute("aria-expanded", "false");
  await expect(page.locator(".references a")).toHaveCount(0);

  // Progress is shared between tests, so 1.1 may already be solved: solving it again is harmless.
  await replaceCode(page, solutionOf("1.1"));
  await pressButton(page, "Check");
  await expect(page.locator(".oracle")).toHaveClass(/is-success/);
  await page.getByRole("button", { name: /Go deeper/ }).click();
  await expect(toggle).toHaveAttribute("aria-expanded", "true");
  await expect(toggle).toBeFocused();
  await expect(page.locator(".references a").first()).toBeInViewport();
});

// Lesson 1.3: no other test completes it, so its challenge pill starts hidden.
test("challenge mode hides the recap of the objectives; the hub shows the Challenge pill only after the mission", async ({ page }) => {
  await openHub(page);
  const pill = page.locator(".section-row", { has: page.locator(".section-id", { hasText: /^1\.3$/ }) }).locator(".pill", { hasText: "Challenge" });
  await expect(pill).toHaveCount(0);
  await openLessonBySearch(page, "relative phase", "1.3");
  await replaceCode(page, solutionOf("1.3"));
  await pressButton(page, "Check");
  await expect(page.locator(".oracle")).toHaveClass(/is-success/);
  await page.getByRole("button", { name: "Try the challenge" }).click();
  await expect(page.locator(".mission.is-challenge")).toBeVisible();
  await expect(page.locator(".recap")).toHaveCount(0);
  await page.getByRole("button", { name: "Tracks" }).click();
  await expect(pill).toHaveCount(1);
});
