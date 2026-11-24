import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch, replaceCode } from "./helpers";

// Lesson 1.8 is not solved by other tests.

test("the hub offers to continue the lesson opened last", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "Bernstein", "2.4");
  await page.getByRole("button", { name: "Tracks" }).click();
  const main = page.locator(".hub-next");
  await expect(main).toHaveAccessibleName(/^Continue 2\.4 /);
  await expect(main.locator(".hub-next-label")).toHaveText("Continue");
  await expect(page.locator(".section-row.is-next .section-id")).toHaveText("2.4");
  await main.click();
  await expect(page.locator(".crumb-id")).toHaveText("2.4");
  expect(errors).toEqual([]);
});

test("Ctrl+Shift+Enter checks, Alt+1/2 move between the panels", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "Bernstein", "2.4");
  await page.locator(".editor .view-lines").click();
  await page.keyboard.press("ControlOrMeta+Shift+Enter");
  await expect(page.locator(".oracle")).toHaveClass(/is-(warn|error|success)/);

  await page.keyboard.press("Alt+2");
  await expect(page.locator(".visualizer").locator(":focus")).toHaveCount(1);
  await page.keyboard.press("Alt+1");
  await expect(page.locator(".editor textarea")).toBeFocused();
  expect(errors).toEqual([]);
});

test("narrow screen: the mission stays on top, Alt+1/2 switch the tab, and the tabs answer to the arrow keys", async ({ page }) => {
  const errors = collectErrors(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await openHub(page);
  await openLessonBySearch(page, "Bernstein", "2.4");
  await expect(page.locator(".mission")).toBeVisible();
  await expect(page.locator(".editor-panel")).toBeVisible();
  await page.keyboard.press("Alt+2");
  await expect(page.locator(".visualizer")).toBeVisible();
  await expect(page.locator(".editor-panel")).toBeHidden();
  await expect(page.locator(".mission")).toBeVisible();
  await page.keyboard.press("Alt+1");
  await expect(page.locator(".editor-panel")).toBeVisible();

  const tabs = page.locator(".lab-tabs");
  const code = tabs.getByRole("tab", { name: "Code" });
  await expect(code).toHaveAttribute("aria-selected", "true");
  await expect(code).toHaveAttribute("aria-controls", "pane-code");
  await expect(tabs.getByRole("tab", { name: "State" })).toHaveAttribute("tabindex", "-1");
  await code.focus();
  await page.keyboard.press("ArrowRight");
  await expect(tabs.getByRole("tab", { name: "State" })).toBeFocused();
  await expect(tabs.getByRole("tab", { name: "State" })).toHaveAttribute("aria-selected", "true");
  await expect(page.getByRole("tabpanel", { name: "State" })).toBeVisible();
  await page.keyboard.press("ArrowRight");
  await expect(code).toBeFocused();
  expect(errors).toEqual([]);
});

test("the notes drawer is a sheet on narrow screens and does not hide the bottom bar", async ({ page }) => {
  await page.setViewportSize({ width: 768, height: 900 });
  await openHub(page);
  await openLessonBySearch(page, "Bernstein", "2.4");
  await page.keyboard.press("Alt+n");
  const drawer = (await page.locator(".notes-drawer").boundingBox())!;
  const bar = (await page.locator(".oracle").boundingBox())!;
  expect(drawer.y + drawer.height).toBeLessThanOrEqual(bar.y + 1);
  expect(drawer.width).toBeGreaterThan(600);
  await expect(page.locator(".mission")).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
});

test("help menu: the guide and the list of keyboard shortcuts", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "Bernstein", "2.4");
  await page.getByRole("button", { name: "Help", exact: true }).click();
  await expect(page.getByRole("button", { name: "Show the guide" })).toBeVisible();
  await page.getByRole("button", { name: "Keyboard shortcuts" }).click();
  const dialog = page.locator(".shortcuts-dialog");
  await expect(dialog).toBeVisible();
  await expect(dialog).toContainText("Check the mission");
  await expect(dialog).toContainText("Open or close the notes");
  await expect(dialog.locator("kbd", { hasText: "Ctrl" }).first()).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(dialog).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("a failed run still shows what the code printed", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  await replaceCode(page, 'from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nprint("debug marker 42")\nraise ValueError("boom")\n');
  await expect(page.locator(".oracle")).toHaveClass(/is-error/);
  await expect(page.locator(".visualizer .stdout")).toContainText("debug marker 42");
  // Fixing the code clears the failed run's output.
  await replaceCode(page, 'from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nqc.h(0)\nprint("fine now")\n');
  await expect(page.locator(".visualizer .stdout")).toContainText("fine now");
  await expect(page.locator(".visualizer .stdout")).not.toContainText("debug marker 42");
  expect(errors).toEqual([]);
});
