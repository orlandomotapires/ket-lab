import type { RunResult } from "../engine/types";
import { engine } from "./engine";
import { usesReport } from "./selectors";
import type { Get, Set } from "./types";

const RUN_DEBOUNCE_MS = 200;

/** Text the code printed before it failed: the engine sends it next to the error. */
export function printedBefore(response: object): string {
  const stdout = (response as { stdout?: unknown }).stdout;
  return typeof stdout === "string" ? stdout : "";
}

export interface Execution {
  /** Schedules a live run (at each pause in typing). */
  scheduleRun(delay?: number): void;
  /** Cancels the scheduled run (when leaving the lab). */
  cancelScheduled(): void;
  /** Run from the button, with report(...) metrics arriving while it runs. */
  train(): Promise<void>;
  /** Stops the training run in progress. */
  stopTraining(): void;
}

export function createExecution(set: Set, get: Get): Execution {
  let runTimer: number | undefined;
  let runToken = 0;
  let trainRequest: number | null = null;

  function payload(): Record<string, unknown> {
    const { code, lesson, seed, controls, challengeMode } = get();
    return { code, seed, lesson_id: lesson?.id ?? null, controls, challenge: challengeMode };
  }

  async function run(): Promise<void> {
    const token = ++runToken;
    try {
      set({ running: true });
      const response = await engine()
        .call<RunResult>("run", payload())
        .finally(() => {
          if (token === runToken) set({ running: false });
        });
      if (token !== runToken) return; // a newer edit arrived
      if (response.ok) {
        set({ result: response, resultIsCurrent: true, error: null, errorStdout: "" });
      } else if (!response.stale) {
        set({ error: response.error ?? null, errorStdout: printedBefore(response), resultIsCurrent: false });
      }
    } catch {
      // Connection dropped: keeps the last valid state on screen.
    }
  }

  return {
    scheduleRun(delay = RUN_DEBOUNCE_MS) {
      window.clearTimeout(runTimer);
      // A training run in the free lab can take minutes: it only runs from the button.
      if (!get().lesson && usesReport(get().code)) return;
      // Code from a link runs on the opener's machine: only after it has been reviewed.
      if (!get().codeTrusted) return;
      runTimer = window.setTimeout(() => void run(), delay);
    },

    cancelScheduled() {
      window.clearTimeout(runTimer);
    },

    async train() {
      const token = ++runToken;
      window.clearTimeout(runTimer);
      set({ running: true, training: { series: {}, active: true } });
      try {
        const request = await engine().start<RunResult>("run", { ...payload(), train: true }, (event) => {
          if (token !== runToken) return;
          const series = { ...(get().training?.series ?? {}) };
          for (const [name, values] of Object.entries(event.series as Record<string, number[]>)) {
            series[name] = [...(series[name] ?? []), ...values];
          }
          set({ training: { series, active: true } });
        });
        trainRequest = request.id;
        const response = await request.done;
        if (token !== runToken) return;
        if (response.ok) {
          set({
            result: response,
            resultIsCurrent: true,
            error: null,
            errorStdout: "",
            training: response.training ? { series: response.training.series, active: false } : null,
          });
        } else if (!response.stale) {
          const partial = get().training;
          set({
            error: response.error ?? null,
            errorStdout: printedBefore(response),
            resultIsCurrent: false,
            training: partial && Object.keys(partial.series).length ? { ...partial, active: false } : null,
          });
        }
      } catch {
        // Connection dropped: keeps the last valid state on screen.
      } finally {
        trainRequest = null;
        if (token === runToken) set({ running: false });
      }
    },

    stopTraining() {
      if (trainRequest !== null) void engine().call("cancel", { target: trainRequest }).catch(() => undefined);
    },
  };
}
