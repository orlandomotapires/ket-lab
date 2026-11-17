import { create } from "zustand";
import { connectionSlice } from "./connection";
import { createExecution } from "./execution";
import { hardwareSlice } from "./hardware";
import { labSlice } from "./lab";
import { missionSlice } from "./mission";
import { createProgressTools, progressSlice } from "./progress";
import { flushNotesOnHide, notesSlice } from "./notes";
import { reviewSlice } from "./review";
import type { State } from "./types";

/**
 * Interface state, in slices by topic: engine connection, progress, lab
 * (lesson and execution), mission (validation, hints, challenge, solution), hardware and review.
 */
export const useStore = create<State>((set, get) => {
  const execution = createExecution(set, get);
  const saver = createProgressTools(set, get);
  flushNotesOnHide(get);
  return {
    ...connectionSlice(set, get, execution),
    ...progressSlice(set, get),
    ...labSlice(set, get, execution, saver),
    ...missionSlice(set, get, execution, saver),
    ...hardwareSlice(set, get),
    ...reviewSlice(set, get, execution, saver),
    ...notesSlice(set, get),
  };
});

export {
  SANDBOX_ID,
  SOLUTION_AFTER_ATTEMPTS,
  progressKey,
  sandboxCode,
  selectCurrentStep,
  selectManual,
  selectNextLessonId,
  selectSolutionOffer,
  usesReport,
} from "./selectors";
export { reviewKey, reviewScore } from "./review";
export type { HardwareJob, State, TrainingState, View } from "./types";
