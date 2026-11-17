import { loadLocalProgress, mergeProgress, saveLocalProgress, type ProgressPatch } from "../lib/localProgress";
import { engine } from "./engine";
import { SANDBOX_ID } from "./selectors";
import type { Get, ProgressSlice, Set } from "./types";

const SAVE_DEBOUNCE_MS = 1500;

export interface ProgressTools {
  /** Updates progress in memory (local engine) or in the browser (hosted engine). */
  patch(key: string, patch: ProgressPatch): void;
  /** Saves the code and hints of the open lesson, after a pause in typing. */
  scheduleSave(): void;
}

export function createProgressTools(set: Set, get: Get): ProgressTools {
  let saveTimer: number | undefined;
  return {
    patch(key, patch) {
      set({
        progress: get().progressStorage === "client"
          ? saveLocalProgress(key, patch)
          : { ...get().progress, [key]: mergeProgress(get().progress[key], patch) },
      });
    },

    scheduleSave() {
      if (!get().codeTrusted) return; // code from a link is only saved after it is accepted
      const lessonId = get().lesson?.id ?? SANDBOX_ID;
      window.clearTimeout(saveTimer);
      saveTimer = window.setTimeout(() => {
        if (get().progressStorage === "client") {
          set({ progress: saveLocalProgress(lessonId, { code: get().code, hints_used: get().hintsShown }) });
          return;
        }
        void engine()
          .call("progress.save", { lesson_id: lessonId, code: get().code, hints_used: get().hintsShown })
          .catch(() => undefined);
      }, SAVE_DEBOUNCE_MS);
    },
  };
}

export function progressSlice(set: Set, get: Get): ProgressSlice {
  return {
    progress: {},
    progressStorage: "engine",
    reloadProgress() {
      if (get().progressStorage === "client") set({ progress: loadLocalProgress() });
    },
  };
}
