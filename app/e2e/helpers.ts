import { readdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { expect, type Page } from "@playwright/test";

const CONTENT = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..", "content");

/** Solução de referência de uma lição, pelo id do manifest. */
export function solutionOf(lessonId: string): string {
  for (const track of readdirSync(CONTENT).filter((name) => name.startsWith("track_"))) {
    for (const section of readdirSync(join(CONTENT, track))) {
      const folder = join(CONTENT, track, section);
      const manifest = JSON.parse(readFileSync(join(folder, "manifest.json"), "utf-8"));
      if (manifest.id === lessonId) return readFileSync(join(folder, "solution.py"), "utf-8");
    }
  }
  throw new Error(`lição ${lessonId} não encontrada`);
}

/** Erros de página e de console, para conferir no fim de cada teste. */
export function collectErrors(page: Page): string[] {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  return errors;
}

export async function openHub(page: Page, { tour = false } = {}): Promise<void> {
  // O guia da primeira lição cobriria botões nos outros testes; ele tem um teste próprio.
  if (!tour) await page.addInitScript(() => localStorage.setItem("qlp.tour.v1", "1"));
  await page.goto("/");
  await expect(page.locator(".section-row").first()).toBeVisible();
}

/** Abre uma lição pela busca da barra superior. */
export async function openLessonBySearch(page: Page, query: string, lessonId: string): Promise<void> {
  await page.locator(".search input").fill(query);
  const result = page.locator(".search-result", { has: page.locator(".search-result-id", { hasText: lessonId }) });
  await result.first().click();
  await expect(page.locator(".crumb-id")).toHaveText(lessonId);
  await expect(page.locator(".editor .view-lines")).toBeAttached();
}

/** Troca todo o código do editor. Cola pela área de transferência: digitar faria o
 *  Monaco reindentar cada linha e quebraria a indentação do Python. */
export async function replaceCode(page: Page, code: string): Promise<void> {
  await page.context().grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.evaluate((text) => navigator.clipboard.writeText(text), code);
  await page.locator(".editor .view-lines").click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.press("ControlOrMeta+V");
  // O Monaco desenha espaços como espaços não separáveis: confere um trecho sem espaços da última linha.
  const lastLine = code.trim().split("\n").pop() ?? "";
  const marker = lastLine.split(/\s+/).sort((x, y) => y.length - x.length)[0] ?? "";
  await expect(page.locator(".editor .view-lines")).toContainText(marker);
}

export async function pressButton(page: Page, name: string): Promise<void> {
  await page.locator(".oracle-actions").getByRole("button", { name, exact: true }).click();
}
