import type { Lesson, ShotsResult } from "../engine/types";
import { writeLastLesson } from "../lib/resume";
import { clampStep } from "../lib/steps";
import { t } from "../strings";
import { engine } from "./engine";
import type { Execution } from "./execution";
import type { ProgressTools } from "./progress";
import { SANDBOX_ID, sandboxCode, selectCurrentStep, selectManual, usesReport } from "./selectors";
import type { Get, LabSlice, Set } from "./types";

function defaultControls(lesson: Lesson | null): Record<string, string | number | null> {
  return Object.fromEntries((lesson?.controls ?? []).map((control) => [control.id, control.default]));
}

export function labSlice(set: Set, get: Get, execution: Execution, saver: ProgressTools): LabSlice {
  function enterLab(lesson: Lesson | null, code: string, hintsShown: number, trusted = true): void {
    get().flushNotes();
    if (lesson) writeLastLesson(lesson.id);
    set({
      codeTrusted: trusted,
      view: "lab",
      lesson,
      code,
      result: null,
      resultIsCurrent: false,
      error: null,
      errorStdout: "",
      cursorLine: code.split("\n").length,
      followCursor: true,
      manualStep: 0,
      seed: 0,
      validation: null,
      shots: null,
      hintsShown,
      challengeMode: false,
      challengeHintsShown: 0,
      solution: null,
      controls: defaultControls(lesson),
      running: false,
      training: null,
    });
    execution.scheduleRun(0);
  }

  return {
    lesson: null,
    code: "",
    result: null,
    resultIsCurrent: false,
    error: null,
    errorStdout: "",
    cursorLine: 1,
    followCursor: true,
    manualStep: 0,
    seed: 0,
    shots: null,
    controls: {},
    running: false,
    training: null,
    codeTrusted: true,

    async openLesson(id) {
      const response = await engine().call<{ lesson: Lesson }>("lesson", { lesson_id: id });
      if (!response.ok) {
        set({ loadError: response.error?.message ?? t("hub.openLessonFailed") });
        return;
      }
      const saved = get().progress[id];
      enterLab(response.lesson, saved?.code ?? response.lesson.starter_code, saved?.hints_used ?? 0);
    },

    openSandbox() {
      enterLab(null, get().progress[SANDBOX_ID]?.code ?? sandboxCode(), 0);
    },

    openShared(code) {
      enterLab(null, code, 0, false);
    },

    trustShared() {
      set({ codeTrusted: true });
      execution.scheduleRun(0);
    },

    setCode(code) {
      if (code === get().code) return;
      set({ code, resultIsCurrent: false, validation: null, shots: null });
      // Free lab: with no report(...) in the code, the previous training curve goes away.
      if (!get().lesson && get().training && !get().training!.active && !usesReport(code)) set({ training: null });
      // Training runs only from the button; everything else runs at each pause in typing.
      if (!selectManual(get())) execution.scheduleRun();
      saver.scheduleSave();
    },

    resetCode() {
      const { lesson } = get();
      get().setCode(lesson ? lesson.starter_code : sandboxCode());
    },

    setCursorLine(line) {
      if (line !== get().cursorLine || !get().followCursor) set({ cursorLine: line, followCursor: true });
    },

    setStep(step) {
      const count = get().result?.steps.length ?? 0;
      set({ manualStep: clampStep(step, count), followCursor: false });
    },

    setFollowCursor(follow) {
      set({ followCursor: follow, manualStep: selectCurrentStep(get()) });
    },

    setControl(id, value) {
      set({ controls: { ...get().controls, [id]: value }, shots: null, validation: null });
      execution.scheduleRun(0);
    },

    reseed() {
      set({ seed: get().seed + 1, shots: null });
      execution.scheduleRun(0);
    },

    runNow() {
      if (!get().codeTrusted) return;
      if (selectManual(get())) {
        // A live run (from before the code became a training run) may be in progress: the training run replaces it.
        if (!get().training?.active) void execution.train();
      } else execution.scheduleRun(0);
    },

    stopRun() {
      execution.stopTraining();
    },

    async runShots() {
      const { code, lesson, seed } = get();
      if (!get().codeTrusted) return;
      try {
        const response = await engine().call<ShotsResult>("shots", {
          code,
          shots: 1024,
          seed: seed + Math.floor(Math.random() * 1e6),
          lesson_id: lesson?.id ?? null,
          controls: get().controls,
          challenge: get().challengeMode,
        });
        if (response.ok) set({ shots: response });
        else if (response.error) set({ error: response.error });
      } catch {
        // Connection notice already visible.
      }
    },
  };
}
