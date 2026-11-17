import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";
import { clearNotes, collectErrors, openHub, openLessonBySearch, openNotesDrawer } from "./helpers";

// Lessons used here are not solved by other tests: notes do not depend on progress anyway.

test("notes drawer: opens focused, saves by itself, closes with Escape and survives a reload", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await clearNotes(page);
  await openLessonBySearch(page, "interference", "1.4");
  const button = page.locator(".topbar").getByRole("button", { name: "Notes" });
  await expect(button.locator(".note-dot")).toHaveCount(0);
  await openNotesDrawer(page);
  const field = page.locator(".notes-drawer .note-field");
  await expect(field).toBeFocused();
  await expect(field).toHaveAttribute("placeholder", /Things to remember/);
  await expect(page.locator(".notes-drawer").getByRole("button", { name: /^Save/ })).toHaveCount(0);
  await field.fill("Phase decides whether paths add or cancel.");
  await expect(page.locator(".notes-drawer .note-status")).toHaveText("Saved");
  await expect(button.locator(".note-dot")).toHaveCount(1);

  // The editor keeps its space: the drawer sits beside it, and the bottom bar stays visible.
  const bar = (await page.locator(".oracle").boundingBox())!;
  const drawer = (await page.locator(".notes-drawer").boundingBox())!;
  expect(drawer.y + drawer.height).toBeLessThanOrEqual(bar.y + 1);
  expect((await page.locator(".editor-panel").boundingBox())!.width).toBeGreaterThan(300);

  await page.keyboard.press("Escape");
  await expect(page.locator(".notes-drawer")).toHaveCount(0);
  await expect(button).toBeFocused();

  // Alt+N toggles it; the text is still there after reloading the page.
  await page.reload();
  await openLessonBySearch(page, "interference", "1.4");
  await page.keyboard.press("Alt+n");
  await expect(page.locator(".notes-drawer .note-field")).toHaveValue("Phase decides whether paths add or cancel.");
  await page.keyboard.press("Alt+n");
  await expect(page.locator(".notes-drawer")).toHaveCount(0);

  // The hub marks the row.
  await page.getByRole("button", { name: "Tracks" }).click();
  const row = page.locator(".section-row", { has: page.locator(".section-id", { hasText: /^1\.4$/ }) });
  await expect(row.locator(".note-dot")).toHaveCount(1);
  await clearNotes(page);
  await expect(row.locator(".note-dot")).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("notes page: general note, lesson notes by track, edit in place, open the lesson, empty state", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await clearNotes(page);
  await page.getByRole("button", { name: /^Notes/ }).click();
  await expect(page.locator(".notes-empty")).toContainText("No lesson notes yet");
  await page.getByLabel("General", { exact: true }).fill("Ask about the Born rule.");
  await expect(page.locator(".note-status")).toHaveText("Saved");

  await page.getByRole("button", { name: "Back to tracks" }).click();
  await openLessonBySearch(page, "interference", "1.4");
  await openNotesDrawer(page);
  await page.locator(".notes-drawer .note-field").fill("Interference needs a relative phase.");
  await expect(page.locator(".notes-drawer .note-status")).toHaveText("Saved");
  await page.getByRole("button", { name: "Tracks" }).click();

  await page.getByRole("button", { name: /^Notes/ }).click();
  await expect(page.locator(".notes-empty")).toHaveCount(0);
  await expect(page.locator(".notes-track")).toContainText("Track 1");
  const card = page.locator(".note-card", { has: page.locator(".section-id", { hasText: /^1\.4$/ }) });
  await expect(card.locator(".note-field")).toHaveValue("Interference needs a relative phase.");
  await card.locator(".note-field").fill("Interference needs a relative phase. Edited here.");
  await expect(page.locator(".note-status")).toHaveText("Saved");
  await card.getByRole("button", { name: "Open lesson" }).click();
  await expect(page.locator(".crumb-id")).toHaveText("1.4");
  await openNotesDrawer(page);
  await expect(page.locator(".notes-drawer .note-field")).toHaveValue("Interference needs a relative phase. Edited here.");
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Tracks" }).click();
  await clearNotes(page);
  expect(errors).toEqual([]);
});

test("search finds notes in their own group and opens the lesson or the notes page", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await clearNotes(page);
  await openLessonBySearch(page, "interference", "1.4");
  await openNotesDrawer(page);
  await page.locator(".notes-drawer .note-field").fill("zebrafish reminder for the exam");
  await expect(page.locator(".notes-drawer .note-status")).toHaveText("Saved");
  await page.getByRole("button", { name: "Tracks" }).click();
  await page.getByRole("button", { name: /^Notes/ }).click();
  await page.getByLabel("General", { exact: true }).fill("quokka question for later");
  await expect(page.locator(".note-status")).toHaveText("Saved");
  await page.getByRole("button", { name: "Back to tracks" }).click();

  await page.locator(".search input").fill("zebrafish");
  await expect(page.locator(".search-group")).toHaveText("In your notes");
  await page.locator(".search-result", { hasText: "zebrafish" }).click();
  await expect(page.locator(".crumb-id")).toHaveText("1.4");
  await expect(page.locator(".notes-drawer .note-field")).toHaveValue(/zebrafish/);
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Tracks" }).click();

  await page.locator(".search input").fill("quokka");
  await page.locator(".search-result", { hasText: "quokka" }).click();
  await expect(page.locator(".notes-page")).toBeVisible();
  await page.getByRole("button", { name: "Back to tracks" }).click();
  await clearNotes(page);
  expect(errors).toEqual([]);
});

test("backup: the export carries the notes and the import restores them in local mode", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await clearNotes(page);
  await page.getByRole("button", { name: /^Notes/ }).click();
  await page.getByLabel("General", { exact: true }).fill("backup me");
  await expect(page.locator(".note-status")).toHaveText("Saved");
  await page.getByRole("button", { name: "Back to tracks" }).click();

  await page.getByRole("button", { name: /^Backup/ }).click();
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export progress" }).click();
  const file = (await (await download).path())!;
  const data = JSON.parse(readFileSync(file, "utf-8"));
  expect(data.format).toBe("qlp-progress");
  expect(data.notes.general.body).toBe("backup me");
  await expect(page.locator(".backup-dialog [role=status]")).toHaveText("File downloaded.");
  await page.locator(".backup-dialog").getByRole("button", { name: "Close" }).click();

  await clearNotes(page);
  await expect(page.getByRole("button", { name: /^Notes/ })).not.toContainText("saved");
  // Export and import live in the same dialog, with the local engine too.
  await page.getByRole("button", { name: /^Backup/ }).click();
  await expect(page.locator(".backup-dialog").getByRole("button", { name: "Import progress" })).toBeVisible();
  await page.locator(".backup-dialog input[type=file]").setInputFiles(file);
  await expect(page.locator(".backup-dialog [role=status]")).toContainText(/Imported\. Lessons: \d+\. Notes: 1\./);
  await page.keyboard.press("Escape");
  await expect(page.locator(".backup-dialog")).toHaveCount(0);
  await page.getByRole("button", { name: /^Notes/ }).click();
  await expect(page.getByLabel("General", { exact: true })).toHaveValue("backup me");
  await page.getByRole("button", { name: "Back to tracks" }).click();

  // A file that is not a backup is refused with a message.
  await page.getByRole("button", { name: /^Backup/ }).click();
  await page.locator(".backup-dialog input[type=file]").setInputFiles({ name: "x.json", mimeType: "application/json", buffer: Buffer.from("{\"a\":1}") });
  await expect(page.locator(".backup-dialog [role=status]")).toContainText("not a backup");
  await page.keyboard.press("Escape");
  await clearNotes(page);
  expect(errors).toEqual([]);
});
