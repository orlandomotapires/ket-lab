import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch, pressButton, replaceCode, solutionOf } from "./helpers";

test("hosted mode: progress in the browser, with export and import", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await expect(page.locator(".hub-extras")).toBeVisible();

  await openLessonBySearch(page, "computational basis", "1.1");
  await replaceCode(page, solutionOf("1.1"));
  await pressButton(page, "Check");
  await expect(page.locator(".mission")).toHaveClass(/is-done/);

  // A note written in the lesson stays in the browser too.
  await page.getByRole("button", { name: "Notes", exact: true }).click();
  await page.getByLabel(/^Note for lesson 1\.1/).fill("hosted note");
  await expect(page.locator(".note-status")).toHaveText("Saved");
  expect(await page.evaluate(() => localStorage.getItem("ket-lab.notes.v1"))).toContain("hosted note");

  // Progress survives a page reload: it is in localStorage, not in the engine. The reload keeps the lesson.
  await page.reload();
  await expect(page.locator(".crumb-id")).toHaveText("1.1");
  await expect(page.locator(".mission")).toHaveClass(/is-done/);
  await page.getByRole("button", { name: "Tracks" }).click();
  await expect(page.locator(".section-row.is-done").first()).toBeVisible();
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("ket-lab.progress.v1") ?? "{}"));
  expect(saved["1.1"].completed).toBe(true);

  // Exports, deletes and imports back.
  await page.getByRole("button", { name: /^Backup/ }).click();
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export progress" }).click();
  const file = await (await download).path();
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await expect(page.locator(".section-row.is-done")).toHaveCount(0);
  await page.getByRole("button", { name: /^Backup/ }).click();
  await page.locator(".backup-dialog input[type=file]").setInputFiles(file!);
  await expect(page.locator(".backup-dialog [role=status]")).toContainText("Imported");
  await expect(page.locator(".section-row.is-done").first()).toBeVisible();
  expect(await page.evaluate(() => localStorage.getItem("ket-lab.notes.v1"))).toContain("hosted note");
  expect(errors).toEqual([]);
});

test("hosted mode: note images stay in this browser and survive a reload", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: /^Notes/ }).click();
  const general = page.locator(".note-card").first();
  const png = Buffer.from(
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGP8z8DAwMDAxMDAwMDAAAANHQEDasKb6QAAAABJRU5ErkJggg==",
    "base64",
  );
  await general.locator("input[type=file]").setInputFiles({ name: "dot.png", mimeType: "image/png", buffer: png });
  await expect(general.locator(".note-image img")).toHaveCount(1);
  await page.reload();
  await page.getByRole("button", { name: /^Notes/ }).click();
  await expect(page.locator(".note-card").first().locator(".note-image img")).toHaveAttribute("src", /^blob:/);
  await page.getByRole("button", { name: "Remove image 1" }).click();
  await expect(page.locator(".note-image")).toHaveCount(0);
  expect(errors).toEqual([]);
});
