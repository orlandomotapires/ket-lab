import type { LessonProgress } from "../engine/types";

/** Progresso no navegador, usado quando o motor é hospedado (um motor para muitos alunos). */
const KEY = "qlp.progress.v1";

export function loadLocalProgress(): Record<string, LessonProgress> {
  try {
    const parsed = JSON.parse(localStorage.getItem(KEY) ?? "{}");
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

/** Mescla e grava; uma lição concluída continua concluída. */
export function saveLocalProgress(lessonId: string, patch: Partial<LessonProgress>): Record<string, LessonProgress> {
  const all = loadLocalProgress();
  const previous = all[lessonId] ?? { code: null, completed: false, hints_used: 0 };
  all[lessonId] = { ...previous, ...patch, completed: previous.completed || Boolean(patch.completed) };
  try {
    localStorage.setItem(KEY, JSON.stringify(all));
  } catch {
    // Armazenamento cheio ou bloqueado: o progresso vale só para esta sessão.
  }
  return all;
}

/** Arquivo de cópia do progresso, para guardar ou levar a outro navegador. */
export function exportLocalProgress(progress: Record<string, LessonProgress> = loadLocalProgress()): string {
  const slim = Object.fromEntries(
    Object.entries(progress).map(([id, entry]) => [id, { code: entry.code, completed: entry.completed, hints_used: entry.hints_used }]),
  );
  return JSON.stringify({ format: "qlp-progress", version: 1, progress: slim }, null, 2);
}


/** Importa um arquivo exportado; devolve o número de lições lidas ou lança erro. */
export function importLocalProgress(text: string): number {
  const data = JSON.parse(text);
  if (data?.format !== "qlp-progress" || typeof data.progress !== "object") throw new Error("invalid file");
  const current = loadLocalProgress();
  for (const [id, entry] of Object.entries(data.progress as Record<string, LessonProgress>)) {
    const previous = current[id];
    current[id] = {
      code: entry.code ?? previous?.code ?? null,
      completed: Boolean(entry.completed || previous?.completed),
      hints_used: Math.max(entry.hints_used ?? 0, previous?.hints_used ?? 0),
    };
  }
  localStorage.setItem(KEY, JSON.stringify(current));
  return Object.keys(data.progress).length;
}
