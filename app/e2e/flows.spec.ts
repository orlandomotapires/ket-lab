import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch, pressButton, replaceCode, solutionOf } from "./helpers";

test("the hub loads and search opens the right lesson", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await expect(page.locator(".hub-side h1")).toHaveText("Learning tracks");
  await openLessonBySearch(page, "entanglement", "1.5");
  await expect(page.locator(".crumbs strong")).toContainText("Entanglement");
  expect(errors).toEqual([]);
});

test("Track 1 lesson: solve and validate", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "computational basis", "1.1");
  await expect(page.locator(".mission")).not.toHaveClass(/is-done/);
  await replaceCode(page, solutionOf("1.1"));
  await expect(page.locator(".circuit .gate")).toHaveCount(1);
  await pressButton(page, "Check");
  await expect(page.locator(".oracle")).toHaveClass(/is-success/);
  await expect(page.locator(".mission")).toHaveClass(/is-done/);
  expect(errors).toEqual([]);
});

test("lesson with secret oracles: starting code fails, solution passes", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "Deutsch-Jozsa", "2.3");
  await pressButton(page, "Check");
  await expect(page.locator(".oracle")).toHaveClass(/is-(warn|error)/);
  await replaceCode(page, solutionOf("2.3"));
  await pressButton(page, "Check");
  await expect(page.locator(".oracle")).toHaveClass(/is-success/);
  expect(errors).toEqual([]);
});

test("free lab: training run with live curve and Stop", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  await page.locator(".example-picker select").selectOption("training");
  await pressButton(page, "Run");
  await expect(page.locator(".oracle-message")).toContainText("Training finished after 80 steps", { timeout: 45_000 });
  await expect(page.locator(".visualizer .segmented [aria-pressed=true]")).toHaveText("Convergence");

  await replaceCode(page, "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\ni = 0\nwhile True:\n    i += 1\n    if i % 200000 == 0:\n        report(i)\n");
  await pressButton(page, "Run");
  await expect(page.locator(".pill-live")).toBeVisible({ timeout: 20_000 });
  await pressButton(page, "Stop");
  await expect(page.locator(".oracle-message")).toContainText("Execution stopped.");
  expect(errors).toEqual([]);
});

test("export to OpenQASM 3 and 2", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  await page.locator(".example-picker select").selectOption("bell");
  await page.locator(".circuit-panel").getByRole("button", { name: "Export" }).click();
  await expect(page.locator(".export-code")).toContainText("OPENQASM 3.0;");
  await expect(page.locator(".export-code")).toContainText("cx q[0], q[1];");
  await page.locator(".export-dialog").getByRole("button", { name: "OpenQASM 2" }).click();
  await expect(page.locator(".export-code")).toContainText("OPENQASM 2.0;");
  await page.keyboard.press("Escape");
  await expect(page.locator(".export-dialog")).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("both themes render without errors", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  const before = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await page.getByRole("button", { name: /^Switch to (dark|light) theme$/ }).click();
  const after = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  expect(after).not.toEqual(before);
  await openLessonBySearch(page, "teleportation", "1.6");
  // Further reading is folded at the end of the lesson; opening it shows the list.
  await page.getByRole("button", { name: /^Further reading \(\d+\)/ }).click();
  await expect(page.locator(".references li")).not.toHaveCount(0);
  expect(errors).toEqual([]);
});

for (const viewport of [{ width: 768, height: 1024 }, { width: 390, height: 844 }]) {
  test(`narrow screen (${viewport.width}px): tabs, solved lesson, no horizontal scrolling`, async ({ page }) => {
    const errors = collectErrors(page);
    await page.setViewportSize(viewport);
    await openHub(page);
    await openLessonBySearch(page, "computational basis", "1.1");
    const tabs = page.locator(".lab-tabs");
    await expect(tabs).toBeVisible();
    await expect(page.locator(".mission")).toBeVisible();
    await tabs.getByRole("tab", { name: "Code" }).click();
    await expect(page.locator(".mission")).toBeHidden();
    await replaceCode(page, solutionOf("1.1"));
    await expect(page.locator(".circuit .gate")).toHaveCount(1);
    await tabs.getByRole("tab", { name: "State" }).click();
    await expect(page.locator(".visualizer")).toBeVisible();
    await pressButton(page, "Check");
    await expect(page.locator(".oracle")).toHaveClass(/is-success/);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(0);
    expect(errors).toEqual([]);
  });
}

test("first-lesson guide: appears once and reopens from the button", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page, { tour: true });
  await openLessonBySearch(page, "computational basis", "1.1");
  const card = page.locator(".tour-card");
  await expect(card).toContainText("Your code runs as you type");
  await expect(page.locator(".editor-panel")).toHaveClass(/tour-target/);
  for (const title of ["Step through the circuit", "The mission", "Check your answer"]) {
    await card.getByRole("button", { name: "Next" }).click();
    await expect(card).toContainText(title);
  }
  await card.getByRole("button", { name: "Start" }).click();
  await expect(card).toHaveCount(0);
  // Does not come back on its own when another lesson is opened.
  await page.getByRole("button", { name: "Tracks" }).click();
  await openLessonBySearch(page, "entanglement", "1.5");
  await page.waitForTimeout(1200);
  await expect(card).toHaveCount(0);
  await page.getByRole("button", { name: "Help", exact: true }).click();
  await page.getByRole("button", { name: "Show the guide" }).click();
  await expect(card).toContainText("Your code runs as you type");
  await page.keyboard.press("Escape");
  await expect(card).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("real hardware (simulated IBM): submits, tracks and compares with the simulation", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  await page.locator(".example-picker select").selectOption("bell");
  await page.locator(".circuit-panel").getByRole("button", { name: "Run on hardware" }).click();
  const dialog = page.locator(".hardware-dialog");
  await dialog.getByLabel("IBM Quantum API key").fill("wrong-key");
  await dialog.getByRole("button", { name: /Send/ }).click();
  await expect(dialog.locator(".notice-error")).toContainText("did not accept");
  await dialog.getByLabel("IBM Quantum API key").fill("test-key");
  await dialog.getByRole("button", { name: /Send/ }).click();
  await expect(dialog).toContainText("Job fake-job-1");
  await expect(dialog).toContainText("done");
  await expect(dialog.locator(".hw-compare tbody tr")).toHaveCount(4);
  await expect(dialog.locator(".hw-compare")).toContainText("48.6%");
  // The key is not stored without asking.
  expect(await page.evaluate(() => localStorage.getItem("ket-lab.ibm.key"))).toBeNull();
  expect(errors).toEqual([]);
});

test("share link: opens in review and only runs after being accepted", async ({ page, context }) => {
  const errors = collectErrors(page);
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  await page.locator(".example-picker select").selectOption("bell");
  await expect(page.locator(".circuit .gate")).toHaveCount(2);
  await page.getByRole("button", { name: "Share" }).click();
  await expect(page.getByRole("button", { name: "Link copied" })).toBeVisible();
  const link = await page.evaluate(() => navigator.clipboard.readText());
  expect(link).toContain("#lab=");

  const other = await context.newPage();
  await other.addInitScript(() => localStorage.setItem("ket-lab.tour.v1", "1"));
  await other.goto(link);
  await expect(other.locator(".shared-notice")).toBeVisible();
  await expect(other.locator(".editor .view-lines")).toContainText("qc.cx(0,");
  await other.waitForTimeout(1500);
  await expect(other.locator(".circuit .gate")).toHaveCount(0); // nada rodou
  expect(other.url()).not.toContain("#lab=");
  await other.getByRole("button", { name: "Run this code" }).click();
  await expect(other.locator(".shared-notice")).toHaveCount(0);
  await expect(other.locator(".circuit .gate")).toHaveCount(2);
  expect(errors).toEqual([]);
});

test("composer: lessons 1.1, 1.2 and 1.5 solved with clicks only", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  const compose = async (gate: string, ...qubits: string[]) => {
    await page.locator(".composer-gate", { hasText: new RegExp(`^${gate}$`) }).click();
    for (const q of qubits) await page.locator(".composer-qubit", { hasText: q }).click();
  };
  const solveWith = async (query: string, id: string, steps: [string, ...string[]][]) => {
    await openLessonBySearch(page, query, id);
    await pressButton(page, "Reset code"); // other tests may have saved a solution in this lesson
    await page.getByRole("button", { name: "Compose" }).click();
    for (const [gate, ...qubits] of steps) await compose(gate, ...qubits);
    await expect(page.locator(".circuit .gate")).toHaveCount(steps.length);
    await pressButton(page, "Check");
    await expect(page.locator(".oracle")).toHaveClass(/is-success/);
    await page.getByRole("button", { name: "Tracks" }).click();
  };
  await solveWith("computational basis", "1.1", [["X", "q0"]]);
  await solveWith("Hadamard", "1.2", [["H", "q0"], ["H", "q1"], ["H", "q2"], ["Measure", "q0"], ["Measure", "q1"], ["Measure", "q2"]]);
  await solveWith("entanglement", "1.5", [["H", "q0"], ["CNOT", "q0", "q1"]]);

  // Remove: selects the gate in the circuit and deletes the matching line.
  await openLessonBySearch(page, "computational basis", "1.1");
  await pressButton(page, "Reset code"); // the lesson comes back with the solution saved above
  await expect(page.locator(".circuit .gate")).toHaveCount(0);
  await page.getByRole("button", { name: "Compose" }).click();
  await compose("H", "q0");
  await expect(page.locator(".circuit .gate")).toHaveCount(1);
  await page.locator(".circuit .gate .gate-box").first().click();
  await page.getByRole("button", { name: "Remove selected gate" }).click();
  await expect(page.locator(".circuit .gate")).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("export progress as a backup", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: /^Backup/ }).click();
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export progress" }).click();
  expect((await download).suggestedFilename()).toBe("ket-lab-progress.json");
  expect(errors).toEqual([]);
});

test("references page: all sources, and each cited lesson opens", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: /^References/ }).click();
  await expect(page.locator(".bibliography h1")).toHaveText("References");
  for (const heading of ["Books", "Papers", "Courses", "Documentation and tutorials", "Lecture notes used to design the exercises", "Software"]) {
    await expect(page.locator(".bibliography h2", { hasText: heading })).toBeVisible();
  }
  await expect(page.locator(".bibliography")).toContainText("Quantum Computation and Quantum Information");
  await expect(page.locator(".bibliography")).toContainText("Wegewijs");
  // Books: reading guide by section, in book order.
  await expect(page.locator(".bib-book").first().locator(".bib-sections li").first()).toBeVisible();
  // Filter by track: only what Track 4 uses.
  await page.locator(".bib-filter select").selectOption("4");
  await expect(page.locator(".bibliography")).toContainText("The Shor code");
  await expect(page.locator(".bibliography")).not.toContainText("Deutsch’s algorithm");
  await page.locator(".bib-filter select").selectOption("");
  await page.locator(".bib-list li", { hasText: "Entanglement in action: CHSH game" }).getByRole("button", { name: /1\.10/ }).click();
  await expect(page.locator(".crumb-id")).toHaveText("1.10");
  expect(errors).toEqual([]);
});

test("annotated solution: only after the hints and three attempts, and the hub records it", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "Controlled", "1.7");
  const offer = page.getByRole("button", { name: "Show solution" });
  for (let attempt = 0; attempt < 3; attempt++) {
    await pressButton(page, "Check");
    await expect(page.locator(".oracle")).toHaveClass(/is-(warn|error)/);
    // Editing clears the result, so the next Check counts as a new attempt.
    await page.locator(".editor .view-lines").click();
    await page.keyboard.press("ControlOrMeta+End");
    await page.keyboard.type(" ");
    await expect(page.locator(".oracle")).not.toHaveClass(/is-(warn|error)/);
  }
  await expect(offer).toHaveCount(0); // the hints are still closed
  for (let hint = 0; hint < 3; hint++) await page.getByRole("button", { name: /Show hint/ }).click();
  await offer.click();
  await expect(page.locator(".solution-card")).toHaveCount(0); // asks for confirmation first
  await page.getByRole("button", { name: "Keep trying" }).click();
  await offer.click();
  await page.getByRole("button", { name: "Show it anyway", exact: true }).click();
  await expect(page.locator(".solution-code .is-comment").first()).toBeVisible();
  await page.getByRole("button", { name: "Copy into the editor" }).click();
  await pressButton(page, "Check");
  await expect(page.locator(".oracle")).toHaveClass(/is-success/);
  await page.locator(".crumb-home, .topbar").getByRole("button", { name: "Tracks" }).first().click();
  const row = page.locator(".section-row", { has: page.locator(".section-id", { hasText: /^1\.7$/ }) });
  await expect(row).toContainText("Completed with the solution");
  expect(errors).toEqual([]);
});

test("challenge solution: offered once all the challenge hints are open", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await openLessonBySearch(page, "Superdense", "1.9");
  await replaceCode(page, solutionOf("1.9"));
  await pressButton(page, "Check");
  await expect(page.locator(".oracle")).toHaveClass(/is-success/);
  await page.getByRole("button", { name: "Try the challenge" }).click();
  const offer = page.getByRole("button", { name: "Show solution" });
  await expect(offer).toHaveCount(0);
  for (let hint = 0; hint < 2; hint++) await page.getByRole("button", { name: /Show hint/ }).click();
  await expect(offer).toHaveCount(0); // one hint still closed
  await page.getByRole("button", { name: /Show hint/ }).click();
  await offer.click();
  await expect(page.locator(".solution-card")).toHaveCount(0); // asks for confirmation first
  await page.getByRole("button", { name: "Keep trying" }).click();
  await offer.click();
  await page.getByRole("button", { name: "Show it anyway", exact: true }).click();
  await expect(page.locator(".solution-card")).toBeVisible();
  await page.getByRole("button", { name: "Copy into the editor" }).click();
  await pressButton(page, "Check");
  await expect(page.locator(".oracle")).toHaveClass(/is-success/);
  await page.locator(".crumb-home, .topbar").getByRole("button", { name: "Tracks" }).first().click();
  const row = page.locator(".section-row", { has: page.locator(".section-id", { hasText: /^1\.9$/ }) });
  await expect(row).toContainText("Challenge completed with the solution");
  expect(errors).toEqual([]);
});
