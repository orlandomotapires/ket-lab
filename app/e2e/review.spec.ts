import { expect, test } from "@playwright/test";
import { collectErrors, openHub } from "./helpers";

test("track review: answer with the keyboard, see the score, revisit a lesson, best score in the hub", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  const row = page.locator("#track-1 .review-row");
  await expect(row).toContainText("Track review");
  await row.click();

  const progress = page.locator(".review-progress");
  await expect(progress).toContainText("Question 1 of");
  const total = Number((await progress.innerText()).match(/of (\d+)/)![1]);
  expect(total).toBeGreaterThanOrEqual(8);
  await expect(page.locator(".review-question")).toBeFocused();

  // Press 1: the first option is chosen, the explanation shows and focus moves to "Next question".
  await page.keyboard.press("1");
  await expect(page.locator(".option.is-correct")).toHaveCount(1);
  await expect(page.locator(".review-card [role=status]")).toContainText(/Correct\.|Not quite\./);
  await expect(page.getByRole("button", { name: "Next question" })).toBeFocused();
  // A second answer to the same question is ignored.
  await page.locator(".option").nth(1).click({ force: true });
  await expect(page.locator(".option.is-correct")).toHaveCount(1);

  for (let n = 1; n < total; n++) {
    await page.getByRole("button", { name: "Next question" }).click();
    await expect(progress).toContainText(`Question ${n + 1} of ${total}`);
    await page.locator(".option").first().click();
  }
  await page.getByRole("button", { name: "See the result" }).click();
  const score = page.getByRole("heading", { level: 1 });
  await expect(score).toHaveText(/^\d+ of \d+ correct$/);
  const [, got] = (await score.innerText()).match(/^(\d+) of/)!;

  // Wrong answers become buttons that open the lesson to revisit.
  const lessons = page.locator(".review-lessons button");
  if ((await lessons.count()) > 0) {
    const id = (await lessons.first().locator(".section-id").innerText()).trim();
    await lessons.first().click();
    await expect(page.locator(".crumb-id")).toHaveText(id);
    await page.getByRole("button", { name: "Tracks" }).click();
  } else {
    await expect(page.getByText("Every answer was right")).toBeVisible();
    await page.getByRole("button", { name: "Back to tracks" }).click();
  }
  await expect(page.locator("#track-1 .review-row")).toContainText(`Best: ${got} of ${total}`);

  // Opening it again starts over; the best score stays.
  await page.locator("#track-1 .review-row").click();
  await page.locator(".option").first().click();
  await page.getByRole("button", { name: "Back to tracks" }).click();
  await expect(page.locator("#track-1 .review-row")).toContainText(`Best: ${got} of ${total}`);
  expect(errors).toEqual([]);
});

test("every track from 1 to 5 has a review row; Track 0 has none", async ({ page }) => {
  await openHub(page);
  for (const id of [1, 2, 3, 4, 5]) {
    // Collapsed tracks hide their rows: open each one first.
    const toggle = page.locator(`#track-${id} .track-toggle`);
    if ((await toggle.getAttribute("aria-expanded")) === "false") await toggle.click();
    await expect(page.locator(`#track-${id} .review-row`)).toHaveCount(1);
  }
  await expect(page.locator("#track-0 .review-row")).toHaveCount(0);
});
