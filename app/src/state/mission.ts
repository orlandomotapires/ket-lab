import type { ValidationResult } from "../engine/types";
import { engine } from "./engine";
import { printedBefore, type Execution } from "./execution";
import type { ProgressTools } from "./progress";
import { progressKey } from "./selectors";
import type { Get, MissionSlice, Set } from "./types";

export function missionSlice(set: Set, get: Get, execution: Execution, saver: ProgressTools): MissionSlice {
  // Id of the Check in progress, so it can be stopped (training lessons may check for minutes).
  let validateRequest: number | null = null;
  return {
    validation: null,
    validating: false,
    hintsShown: 0,
    challengeMode: false,
    challengeHintsShown: 0,
    solution: null,

    async validate() {
      const { lesson, code } = get();
      if (!lesson) return;
      set({ validating: true });
      try {
        const challenge = get().challengeMode;
        const request = await engine().start<ValidationResult>("validate", { code, lesson_id: lesson.id, challenge });
        validateRequest = request.id;
        const response = await request.done;
        if (!response.ok && response.error?.kind === "cancelled") return;
        if (response.ok) {
          set({ validation: response });
          // The challenge has its own progress, under the key "<id>:challenge". The local engine stores the same in SQLite.
          const key = progressKey(lesson.id, challenge);
          if (response.passed) {
            saver.patch(key, { code, completed: true, hints_used: challenge ? get().challengeHintsShown : get().hintsShown });
          } else {
            saver.patch(key, { failedAttempt: true }); // unsuccessful attempts unlock the solution
          }
        } else if (response.error) {
          set({ error: response.error, errorStdout: printedBefore(response) });
        }
      } catch {
        // Connection notice already visible.
      } finally {
        validateRequest = null;
        set({ validating: false });
      }
    },

    stopValidation() {
      if (validateRequest !== null) void engine().call("cancel", { target: validateRequest }).catch(() => undefined);
    },

    showNextHint() {
      const { lesson, hintsShown, challengeMode, challengeHintsShown } = get();
      if (challengeMode) {
        if (lesson?.challenge && challengeHintsShown < lesson.challenge.hints.length) {
          set({ challengeHintsShown: challengeHintsShown + 1 });
        }
        return;
      }
      if (lesson && hintsShown < lesson.hints.length) {
        set({ hintsShown: hintsShown + 1 });
        saver.scheduleSave();
      }
    },

    startChallenge() {
      set({ challengeMode: true, challengeHintsShown: 0, validation: null, solution: null });
      execution.scheduleRun(0);
    },

    leaveChallenge() {
      set({ challengeMode: false, validation: null, solution: null });
      execution.scheduleRun(0);
    },

    async showSolution() {
      const { lesson, challengeMode } = get();
      if (!lesson) return;
      try {
        const response = await engine().call<{ code: string }>("solution", { lesson_id: lesson.id, challenge: challengeMode });
        if (!response.ok) {
          if (response.error) set({ error: response.error });
          return;
        }
        if (get().lesson?.id !== lesson.id || get().challengeMode !== challengeMode) return; // left the lesson
        set({ solution: response.code });
        saver.patch(progressKey(lesson.id, challengeMode), { solution_seen: true });
      } catch {
        // Connection notice already visible.
      }
    },

    hideSolution() {
      set({ solution: null });
    },
  };
}
