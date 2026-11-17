import type { ExportResult, ShotsResult } from "../engine/types";
import { engine } from "./engine";
import type { Get, HardwareJob, HardwareSlice, Set } from "./types";

export function hardwareSlice(_set: Set, get: Get): HardwareSlice {
  /** What identifies the circuit on display to the engine. */
  function circuit(): Record<string, unknown> {
    const { code, lesson, controls, challengeMode } = get();
    return { code, lesson_id: lesson?.id ?? null, controls, challenge: challengeMode };
  }

  return {
    hardwareAvailable: false,

    submitHardware({ token, instance, shots }) {
      return engine().call<HardwareJob>("hardware.submit", { ...circuit(), token, instance, shots });
    },

    hardwareStatus({ jobId, token, instance }) {
      return engine().call<HardwareJob>("hardware.status", { job_id: jobId, token, instance });
    },

    simulateCounts(shots) {
      return engine().call<ShotsResult>("shots", { ...circuit(), shots, seed: 0 });
    },

    exportCircuit(format) {
      return engine().call<ExportResult>("export", { ...circuit(), format });
    },
  };
}
