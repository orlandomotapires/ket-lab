import type { LessonProgress } from "../engine/types";
import { clampStep, stepForLine } from "../lib/steps";
import { t } from "../strings";
import type { State } from "./types";

export const SANDBOX_ID = "sandbox";
/** Unsuccessful Checks (with all hints open) before the solution is offered. */
export const SOLUTION_AFTER_ATTEMPTS = 3;

/** Starting code of the free lab. */
export function sandboxCode(): string {
  return `from qiskit import QuantumCircuit

${t("lab.sandboxCode")}
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
`;
}

/** The code calls report(...) outside a comment: it is a training run, executed with the button. */
export function usesReport(code: string): boolean {
  return /^[^#\n]*\breport\s*\(/m.test(code);
}

/** Code that only runs with the Run button: training lessons and training runs in the free lab. */
export function selectManual(state: Pick<State, "lesson" | "code">): boolean {
  return state.lesson ? state.lesson.live === false : usesReport(state.code);
}

/** Index of the snapshot on display: follows the cursor or the timeline. */
export function selectCurrentStep(state: Pick<State, "result" | "followCursor" | "cursorLine" | "manualStep">): number {
  if (!state.result) return 0;
  const count = state.result.steps.length;
  return state.followCursor ? stepForLine(state.result.steps, state.cursorLine) : clampStep(state.manualStep, count);
}

/** Next lesson available after the current one, if any. */
export function selectNextLessonId(state: Pick<State, "catalog" | "lesson">): string | null {
  if (!state.catalog || !state.lesson) return null;
  const sections = state.catalog.tracks.flatMap((track) => track.sections);
  const index = sections.findIndex((section) => section.id === state.lesson!.id);
  const next = sections.slice(index + 1).find((section) => section.available);
  return next?.id ?? null;
}

/** Progress key of the mission or challenge of the open lesson. */
export function progressKey(lessonId: string, challenge: boolean): string {
  return challenge ? `${lessonId}:challenge` : lessonId;
}

/**
 * The annotated solution can be requested: for the mission, all hints open and some unsuccessful
 * attempts; for the challenge, all of its hints open. Without confirmation when the mission or
 * challenge is already complete, or the solution was already seen (nothing left to protect).
 */
export function selectSolutionOffer(
  state: Pick<State, "lesson" | "challengeMode" | "hintsShown" | "challengeHintsShown" | "progress">,
): { offered: boolean; needsConfirmation: boolean } {
  const { lesson, challengeMode } = state;
  if (!lesson) return { offered: false, needsConfirmation: false };
  const entry: LessonProgress | undefined = state.progress[progressKey(lesson.id, challengeMode)];
  if (entry?.completed || entry?.solution_seen) return { offered: true, needsConfirmation: false };
  const hints = challengeMode ? lesson.challenge?.hints.length ?? 0 : lesson.hints.length;
  const shown = challengeMode ? state.challengeHintsShown : state.hintsShown;
  const tried = challengeMode || (entry?.attempts ?? 0) >= SOLUTION_AFTER_ATTEMPTS;
  return { offered: hints > 0 && shown >= hints && tried, needsConfirmation: true };
}
