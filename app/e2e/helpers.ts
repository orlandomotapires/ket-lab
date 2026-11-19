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

/** Replaces all the editor code with a real paste: typing makes Monaco reindent each line,
 *  and Playwright's insertText puts multi-line text into Monaco twice in Firefox (and kept the
 *  old code in desktop WebKit). The clipboard is written during the click on the editor, a
 *  user gesture: Firefox and WebKit allow it then, without the permission only Chromium grants.
 *  Ends only when the editor holds exactly `code`. */
export async function replaceCode(page: Page, code: string): Promise<void> {
  if (page.context().browser()?.browserType().name() === "chromium") {
    await page.context().grantPermissions(["clipboard-read", "clipboard-write"]);
  }
  await page.evaluate((text) => {
    const target = window as unknown as { __clipboardWrite?: Promise<string> };
    document.addEventListener("click", () => {
      target.__clipboardWrite = navigator.clipboard.writeText(text).then(() => "ok", (error) => String(error));
    }, { once: true, capture: true });
  }, code);
  await page.locator(".editor .view-lines").click();
  const written = await page.evaluate(() => (window as unknown as { __clipboardWrite?: Promise<string> }).__clipboardWrite);
  expect(written, "writing the code to the clipboard").toBe("ok");
  // Select all is Monaco's own keybinding, picked from the page's user agent: desktop WebKit
  // claims to be a Mac even on Linux, so Monaco wants Cmd+A there (Ctrl+A only moves to the
  // line start, and the paste lands before the old code). The paste is the browser's own,
  // picked from the host system.
  const mac = await page.evaluate(() => navigator.userAgent.includes("Macintosh"));
  await page.keyboard.press(mac ? "Meta+A" : "Control+A");
  await page.keyboard.press("ControlOrMeta+V");
  // After the paste Monaco shows the end of the code, and draws only the lines in view. The
  // check: the last line number is the code's line count, and the lines in view (in screen
  // order: Monaco positions them, and the parts of wrapped lines, by `top`) end the code.
  // Text is compared without whitespace: Monaco shows spaces as non-breaking spaces.
  const flat = (text: string) => text.replace(/\s+/g, "");
  const shown = () => page.locator(".editor").evaluate((editor) => {
    const inView = [...editor.querySelectorAll<HTMLElement>(".view-lines > .view-line")]
      .map((line) => ({ top: parseFloat(line.style.top), text: line.textContent ?? "" }))
      .sort((a, b) => a.top - b.top)
      .map((line) => line.text)
      .join("");
    const numbers = [...editor.querySelectorAll(".line-numbers")].map((cell) => Number(cell.textContent) || 0);
    return { inView, lastLine: Math.max(0, ...numbers) };
  });
  const lineCount = code.split("\n").length;
  await expect.poll(async () => {
    const { inView, lastLine } = await shown();
    return lastLine === lineCount && flat(inView) !== "" && flat(code).endsWith(flat(inView));
  }, { message: "the editor holds the new code" }).toBe(true);
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
