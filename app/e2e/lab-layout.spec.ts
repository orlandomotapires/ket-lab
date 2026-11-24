import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch } from "./helpers";

test("a reload keeps the open lesson, and a right prediction stays green", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "Hadamard", "1.2");
  await expect(page).toHaveURL(/#lesson=1\.2$/);

  const predict = page.getByRole("button", { name: "Predict before you run" });
  await predict.click();
  await page.getByRole("radio", { name: /about 50 away from 5,000/ }).click();
  await expect(predict).toHaveClass(/is-correct/);

  await page.reload();
  await expect(page.locator(".crumb-id")).toHaveText("1.2");
  await expect(page.getByRole("button", { name: "Predict before you run" })).toHaveClass(/is-correct/);

  await page.getByRole("button", { name: "Tracks" }).click();
  await expect(page).not.toHaveURL(/#lesson=/);
  expect(errors).toEqual([]);
});

test("previous and next lesson from the top bar", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "Hadamard", "1.2");
  await page.getByRole("button", { name: /^Next lesson: 1\.3 / }).click();
  await expect(page.locator(".crumb-id")).toHaveText("1.3");
  await page.getByRole("button", { name: /^Previous lesson: 1\.2 / }).click();
  await expect(page.locator(".crumb-id")).toHaveText("1.2");
  expect(errors).toEqual([]);
});

test("code and circuit share one panel; the readouts follow the sphere chosen", async ({ page }) => {
  const errors = collectErrors(page);
  await page.addInitScript(() => {
    if (!sessionStorage.getItem("seeded")) {
      sessionStorage.setItem("seeded", "1");
      localStorage.setItem("ket-lab.lab.showCircuit", "0");
    }
  });
  await openHub(page);
  await openLessonBySearch(page, "Superdense", "1.9");
  const views = page.locator(".work-panel .segmented");
  await expect(page.locator(".circuit-panel")).toHaveCount(0);
  await views.getByRole("button", { name: "Circuit" }).click();
  await expect(page.locator(".editor-panel")).toBeVisible();
  await expect(page.locator(".circuit-panel")).toBeVisible();
  await views.getByRole("button", { name: "Code" }).click();
  await expect(page.locator(".editor-panel")).toHaveCount(0);
  // The last open view cannot be closed.
  await views.getByRole("button", { name: "Circuit" }).click();
  await expect(page.locator(".circuit-panel")).toBeVisible();
  await views.getByRole("button", { name: "Code" }).click();

  const viz = page.locator(".visualizer");
  await viz.getByRole("button", { name: "Q-Sphere" }).click();
  await expect(viz.locator("#readout-amplitudes")).toBeVisible();
  await expect(viz.locator("#readout-bloch")).toHaveCount(0);
  await viz.getByRole("button", { name: "Bloch spheres" }).click();
  await expect(viz.locator("#readout-bloch")).toBeVisible();
  await expect(viz.locator("#readout-amplitudes")).toHaveCount(0);

  // The handle between the columns moves them, by keyboard too.
  const handle = page.getByRole("separator", { name: "Resize the code and state columns" });
  const before = Number(await handle.getAttribute("aria-valuenow"));
  await handle.focus();
  await page.keyboard.press("ArrowRight");
  await expect(handle).toHaveAttribute("aria-valuenow", String(before + 2));
  expect(errors).toEqual([]);
});

test("before you start: the lesson's sources open under the mission", async ({ page }) => {
  await openHub(page);
  await openLessonBySearch(page, "Hadamard", "1.2");
  await page.getByRole("button", { name: "Before you start" }).click();
  const items = page.locator(".primer li");
  await expect(items).not.toHaveCount(0);
  await expect(items.first().locator("a")).toHaveAttribute("href", /^https:\/\//);
});
