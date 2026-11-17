import type { Step } from "../engine/types";

/**
 * How many steps have already been executed when the cursor is on the given line.
 *
 * The step unit is the instruction. The cursor selects the LAST instruction, in
 * execution order, whose source line is less than or equal to the cursor's. In
 * code without loops this equals "the state after the cursor line".
 * Returns a snapshot index: 0 = initial state, k = after the k-th step.
 */
export function stepForLine(steps: readonly Step[], line: number): number {
  let last = 0;
  for (let i = 0; i < steps.length; i++) {
    if (steps[i].line <= line) last = i + 1;
  }
  return last;
}

export function clampStep(step: number, stepCount: number): number {
  return Math.max(0, Math.min(step, stepCount));
}

/** Source line of the current step (to highlight in the editor). */
export function lineForStep(steps: readonly Step[], step: number): number | null {
  return step > 0 && step <= steps.length ? steps[step - 1].line : null;
}
