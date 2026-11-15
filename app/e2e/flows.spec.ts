import { expect, test } from "@playwright/test";
import { collectErrors, openHub, openLessonBySearch, pressButton, replaceCode, solutionOf } from "./helpers";

test("o hub carrega e a busca abre a lição certa", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await expect(page.locator(".hub-side h1")).toHaveText("Learning tracks");
  await openLessonBySearch(page, "entanglement", "1.5");
  await expect(page.locator(".lesson-title")).toContainText("Entanglement");
  expect(errors).toEqual([]);
});

test("lição da Trilha 1: resolver e validar", async ({ page }) => {
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

test("lição com oráculos secretos: código inicial falha, solução passa", async ({ page }) => {
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

test("laboratório livre: treino com curva ao vivo e Parar", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  await page.locator(".example-picker select").selectOption("training");
  await pressButton(page, "Run");
  await expect(page.locator(".oracle-message")).toContainText("Training finished after 80 steps", { timeout: 45_000 });
  await expect(page.locator(".visualizer [role=tab][aria-selected=true]")).toHaveText("Convergence");

  await replaceCode(page, "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\ni = 0\nwhile True:\n    i += 1\n    if i % 200000 == 0:\n        report(i)\n");
  await pressButton(page, "Run");
  await expect(page.locator(".pill-live")).toBeVisible({ timeout: 20_000 });
  await pressButton(page, "Stop");
  await expect(page.locator(".oracle-message")).toContainText("Execution stopped.");
  expect(errors).toEqual([]);
});

test("exportação em OpenQASM 3 e 2", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  await page.getByRole("button", { name: "Free lab" }).click();
  await page.locator(".example-picker select").selectOption("bell");
  await page.locator(".circuit-panel").getByRole("button", { name: "Export" }).click();
  await expect(page.locator(".export-code")).toContainText("OPENQASM 3.0;");
  await expect(page.locator(".export-code")).toContainText("cx q[0], q[1];");
  await page.locator(".export-dialog").getByRole("tab", { name: "OpenQASM 2" }).click();
  await expect(page.locator(".export-code")).toContainText("OPENQASM 2.0;");
  await page.keyboard.press("Escape");
  await expect(page.locator(".export-dialog")).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("os dois temas renderizam sem erros", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  const before = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await page.locator(".topbar .btn-icon").click();
  const after = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  expect(after).not.toEqual(before);
  await openLessonBySearch(page, "teleportation", "1.6");
  await expect(page.locator(".references li")).not.toHaveCount(0);
  expect(errors).toEqual([]);
});

for (const viewport of [{ width: 768, height: 1024 }, { width: 390, height: 844 }]) {
  test(`tela estreita (${viewport.width}px): abas, lição resolvida, sem rolagem horizontal`, async ({ page }) => {
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

test("guia da primeira lição: aparece uma vez e reabre pelo botão", async ({ page }) => {
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
  // Não volta sozinho ao abrir outra lição.
  await page.getByRole("button", { name: "Tracks" }).click();
  await openLessonBySearch(page, "entanglement", "1.5");
  await page.waitForTimeout(1200);
  await expect(card).toHaveCount(0);
  await page.getByRole("button", { name: "Show the guide" }).click();
  await expect(card).toContainText("Your code runs as you type");
  await page.keyboard.press("Escape");
  await expect(card).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("hardware real (IBM simulado): envia, acompanha e compara com a simulação", async ({ page }) => {
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
  // A chave não fica guardada sem pedir.
  expect(await page.evaluate(() => localStorage.getItem("qlp.ibm.key"))).toBeNull();
  expect(errors).toEqual([]);
});

test("link de compartilhamento: abre em revisão e só roda depois de aceito", async ({ page, context }) => {
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
  await other.addInitScript(() => localStorage.setItem("qlp.tour.v1", "1"));
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

test("compositor: lições 1.1, 1.2 e 1.5 resolvidas só com cliques", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  const compose = async (gate: string, ...qubits: string[]) => {
    await page.locator(".composer-gate", { hasText: new RegExp(`^${gate}$`) }).click();
    for (const q of qubits) await page.locator(".composer-qubit", { hasText: q }).click();
  };
  const solveWith = async (query: string, id: string, steps: [string, ...string[]][]) => {
    await openLessonBySearch(page, query, id);
    await pressButton(page, "Reset code"); // outros testes podem ter salvo uma solução nesta lição
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

  // Remover: seleciona a porta no circuito e apaga a linha correspondente.
  await openLessonBySearch(page, "computational basis", "1.1");
  await pressButton(page, "Reset code"); // a lição volta com a solução salva acima
  await expect(page.locator(".circuit .gate")).toHaveCount(0);
  await page.getByRole("button", { name: "Compose" }).click();
  await compose("H", "q0");
  await expect(page.locator(".circuit .gate")).toHaveCount(1);
  await page.locator(".circuit .gate .gate-box").first().click();
  await page.getByRole("button", { name: "Remove selected gate" }).click();
  await expect(page.locator(".circuit .gate")).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("relatório da turma: arquivos exportados viram uma tabela lição × aluno", async ({ page }) => {
  const errors = collectErrors(page);
  await openHub(page);
  // A exportação também existe com o progresso no motor local.
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export progress" }).click();
  expect((await download).suggestedFilename()).toBe("quantum-learning-progress.json");

  await page.getByRole("button", { name: "Class report (for teachers)" }).click();
  const file = (name: string, progress: object) => ({
    name,
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify({ format: "qlp-progress", version: 1, progress })),
  });
  await page.locator(".class-report input[type=file]").setInputFiles([
    file("ana.json", { "1.1": { code: "x", completed: true, hints_used: 2 }, "1.2": { code: "y", completed: false, hints_used: 0 } }),
    file("bruno.json", { "1.1": { code: "x", completed: true, hints_used: 0 } }),
    { name: "notes.json", mimeType: "application/json", buffer: Buffer.from("{}") },
  ]);
  await expect(page.locator(".class-table tbody tr")).toHaveCount(2);
  await expect(page.locator(".class-table tbody tr").first()).toContainText("ana");
  await expect(page.locator(".notice-error")).toContainText("notes.json");
  const col = await page.locator(".class-table thead th").allTextContents();
  const index = col.indexOf("1.1");
  await expect(page.locator(".class-table tfoot td").nth(index - 1)).toHaveText("100%");
  await page.getByRole("button", { name: "Back to tracks" }).click();
  await expect(page.locator(".section-row").first()).toBeVisible();
  expect(errors).toEqual([]);
});
