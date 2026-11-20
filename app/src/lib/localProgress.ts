import type { LessonProgress } from "../engine/types";

/** Progress in the browser, used when the engine is hosted (one engine for many learners). */
const KEY = "ket-lab.progress.v1";
/** Lesson renumberings already applied to this browser (the local engine does the same in SQLite). */
const SCHEMA_KEY = "ket-lab.progress.schema";
const SCHEMA = 2;
/** P3.2: the Track 3 project moved from 3.5 to 3.9. */
const RENAMED_IN_2: [from: string, to: string][] = [["3.5", "3.9"]];

export type ProgressPatch = Partial<LessonProgress> & {
  /** An unsuccessful Check: adds one attempt. */
  failedAttempt?: boolean;
};

const EMPTY: LessonProgress = { code: null, completed: false, hints_used: 0 };

/** Merges a change into a lesson's progress; completed stays completed. */
export function mergeProgress(previous: LessonProgress | undefined, patch: ProgressPatch): LessonProgress {
  const base = previous ?? EMPTY;
  const { failedAttempt, ...fields } = patch;
  const solutionSeen = Boolean(base.solution_seen || fields.solution_seen);
  return {
    ...base,
    ...fields,
    completed: base.completed || Boolean(fields.completed),
    hints_used: Math.max(base.hints_used ?? 0, fields.hints_used ?? 0),
    attempts: (base.attempts ?? 0) + (failedAttempt ? 1 : 0),
    solution_seen: solutionSeen,
    // "With solution" only counts if the solution was seen before completing.
    with_solution: Boolean(base.with_solution || fields.with_solution || (!base.completed && fields.completed && base.solution_seen)),
  };
}

function rename(all: Record<string, LessonProgress>, pairs: [string, string][]): void {
  for (const [from, to] of pairs) {
    for (const suffix of ["", ":challenge"]) {
      if (all[from + suffix] && !all[to + suffix]) all[to + suffix] = all[from + suffix];
      delete all[from + suffix];
    }
  }
}

export function loadLocalProgress(): Record<string, LessonProgress> {
  try {
    const parsed = JSON.parse(localStorage.getItem(KEY) ?? "{}");
    const all: Record<string, LessonProgress> = parsed && typeof parsed === "object" ? parsed : {};
    if (Number(localStorage.getItem(SCHEMA_KEY) ?? 1) < SCHEMA) {
      rename(all, RENAMED_IN_2);
      localStorage.setItem(KEY, JSON.stringify(all));
      localStorage.setItem(SCHEMA_KEY, String(SCHEMA));
    }
    return all;
  } catch {
    return {};
  }
}

/** Merges and saves; a completed lesson stays completed. */
export function saveLocalProgress(lessonId: string, patch: ProgressPatch): Record<string, LessonProgress> {
  const all = loadLocalProgress();
  all[lessonId] = mergeProgress(all[lessonId], patch);
  try {
    localStorage.setItem(KEY, JSON.stringify(all));
  } catch {
    // Storage full or blocked: progress only lasts for this session.
  }
  return all;
}

/** Progress backup file, to keep or take to another browser. */
export function exportLocalProgress(progress: Record<string, LessonProgress> = loadLocalProgress()): string {
  const slim = Object.fromEntries(
    Object.entries(progress).map(([id, entry]) => [
      id,
      {
        code: entry.code,
        completed: entry.completed,
        hints_used: entry.hints_used,
        attempts: entry.attempts ?? 0,
        solution_seen: Boolean(entry.solution_seen),
        with_solution: Boolean(entry.with_solution),
      },
    ]),
  );
  return JSON.stringify({ format: "ket-lab-progress", version: SCHEMA, progress: slim }, null, 2);
}

/** Imports an exported file; returns the number of lessons read or throws. */
export function importLocalProgress(text: string): number {
  const data = JSON.parse(text);
  if (data?.format !== "ket-lab-progress" || typeof data.progress !== "object") throw new Error("invalid file");
  const incoming = { ...(data.progress as Record<string, LessonProgress>) };
  if (Number(data.version ?? 1) < 2) rename(incoming, RENAMED_IN_2);
  const current = loadLocalProgress();
  for (const [id, entry] of Object.entries(incoming)) {
    const previous = current[id];
    current[id] = {
      code: entry.code ?? previous?.code ?? null,
      completed: Boolean(entry.completed || previous?.completed),
      hints_used: Math.max(entry.hints_used ?? 0, previous?.hints_used ?? 0),
      attempts: Math.max(entry.attempts ?? 0, previous?.attempts ?? 0),
      solution_seen: Boolean(entry.solution_seen || previous?.solution_seen),
      with_solution: previous?.completed ? Boolean(previous.with_solution) : Boolean(entry.with_solution),
    };
  }
  localStorage.setItem(KEY, JSON.stringify(current));
  return Object.keys(incoming).length;
}
