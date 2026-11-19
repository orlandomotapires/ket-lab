import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { expect, type Page } from "@playwright/test";

const CONTENT = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..", "content");

/** Reference solution of a lesson, by manifest id. */
export function solutionOf(lessonId: string): string {
  for (const track of readdirSync(CONTENT).filter((name) => name.startsWith("track_"))) {
    for (const section of readdirSync(join(CONTENT, track))) {
      const folder = join(CONTENT, track, section);
      if (!existsSync(join(folder, "manifest.json"))) continue; // review.json and the like
      const manifest = JSON.parse(readFileSync(join(folder, "manifest.json"), "utf-8"));
      if (manifest.id === lessonId) return readFileSync(join(folder, "solution.py"), "utf-8");
    }
  }
  throw new Error(`lesson ${lessonId} not found`);
}

/** Page and console errors, to check at the end of each test. */
export function collectErrors(page: Page): string[] {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  return errors;
}

export async function openHub(page: Page, { tour = false } = {}): Promise<void> {
  // The first-lesson guide would cover buttons in the other tests; it has its own test.
  if (!tour) await page.addInitScript(() => localStorage.setItem("qlp.tour.v1", "1"));
  await page.goto("/");
  await expect(page.locator(".section-row").first()).toBeVisible();
}

/** Opens a lesson via the top bar search. */
export async function openLessonBySearch(page: Page, query: string, lessonId: string): Promise<void> {
  await page.locator(".search input").fill(query);
  const result = page.locator(".search-result", { has: page.locator(".search-result-id", { hasText: lessonId }) });
  await result.first().click();
  await expect(page.locator(".crumb-id")).toHaveText(lessonId);
  await expect(page.locator(".editor .view-lines")).toBeAttached();
}

/** Replaces all the editor code. Pastes via the clipboard: typing would make
 *  Monaco reindent each line and break Python's indentation. Firefox and WebKit do not let
 *  tests grant clipboard access: there the text goes in as one input event (no reindenting either). */
export async function replaceCode(page: Page, code: string): Promise<void> {
  const chromium = page.context().browser()?.browserType().name() === "chromium";
  if (chromium) {
    await page.context().grantPermissions(["clipboard-read", "clipboard-write"]);
    await page.evaluate((text) => navigator.clipboard.writeText(text), code);
  }
  await page.locator(".editor .view-lines").click();
  await page.keyboard.press("ControlOrMeta+A");
  if (chromium) await page.keyboard.press("ControlOrMeta+V");
  else await page.keyboard.insertText(code);
  // Monaco renders spaces as non-breaking spaces: checks a span without spaces from the last line.
  const lastLine = code.trim().split("\n").pop() ?? "";
  const marker = lastLine.split(/\s+/).sort((x, y) => y.length - x.length)[0] ?? "";
  await expect(page.locator(".editor .view-lines")).toContainText(marker);
}

/** "Reset code" lives in the More menu and asks for confirmation. */
export async function resetCode(page: Page): Promise<void> {
  const bar = page.locator(".oracle-actions");
  await bar.getByRole("button", { name: "More", exact: true }).click();
  await bar.getByRole("button", { name: "Reset code", exact: true }).click();
  await bar.getByRole("button", { name: "Reset code", exact: true }).click();
}

export async function pressButton(page: Page, name: string): Promise<void> {
  if (name === "Reset code") return resetCode(page);
  await page.locator(".oracle-actions").getByRole("button", { name, exact: true }).click();
}

/** Opens the notes drawer of the open lesson from the top bar. */
export async function openNotesDrawer(page: Page): Promise<void> {
  await page.locator(".topbar").getByRole("button", { name: "Notes" }).click();
  await expect(page.locator(".notes-drawer")).toBeVisible();
}

/** Empties every note, so a test starts without notes (the engine data is shared). */
export async function clearNotes(page: Page): Promise<void> {
  await page.getByRole("button", { name: /^Notes/ }).click();
  await expect(page.locator(".notes-page")).toBeVisible();
  const fields = page.locator(".notes-page .note-field");
  let changed = false;
  for (let i = (await fields.count()) - 1; i >= 0; i--) {
    if ((await fields.nth(i).inputValue()) === "") continue;
    await fields.nth(i).fill("");
    changed = true;
  }
  if (changed) await expect(page.locator(".note-status")).toHaveText("Saved");
  await page.getByRole("button", { name: "Back to tracks" }).click();
  await expect(page.locator(".section-row").first()).toBeVisible();
}

/** Opens a lesson from its row on the hub, first opening its track if it is collapsed. */
export async function openLessonFromHub(page: Page, lessonId: string): Promise<void> {
  const row = page.locator(".section-row", { has: page.locator(".section-id", { hasText: new RegExp(`^${lessonId.replace(".", "\\.")}$`) }) });
  if (!(await row.isVisible())) {
    const track = lessonId.split(".")[0];
    await page.locator(`#track-${track}`).getByRole("button", { name: /^Show/ }).click();
  }
  await row.click();
}
