import { describe, expect, it } from "vitest";

import type { Step } from "../engine/types";
import {
  basisLabel,
  blochFidelity,
  concurrence,
  describeStep,
  entanglementWithRest,
  formatAmplitude,
  formatPercent,
  formatPhase,
  modularSequence,
  qspherePositions,
  registerState,
  rotationAxis,
} from "./quantum";
import { cleanCurves, formatTick, logTicks, makeAxis, niceTicks } from "./curve";
import { clampStep, lineForStep, stepForLine } from "./steps";

const step = (index: number, line: number, name = "h"): Step => ({
  index, line, name, kind: "gate", label: name.toUpperCase(), qubits: [0], clbits: [],
  num_ctrl: 0, outcome: null, applied: null,
});

describe("stepForLine", () => {
  const straight = [step(0, 3), step(1, 5)];
  it("shows the initial state before the first gate", () => {
    expect(stepForLine(straight, 2)).toBe(0);
  });
  it("includes the instruction on the cursor line", () => {
    expect(stepForLine(straight, 3)).toBe(1);
    expect(stepForLine(straight, 4)).toBe(1);
    expect(stepForLine(straight, 5)).toBe(2);
    expect(stepForLine(straight, 99)).toBe(2);
  });
  it("in loops, picks the last occurrence of the line in execution order", () => {
    const loop = [step(0, 4), step(1, 5), step(2, 4), step(3, 5)];
    expect(stepForLine(loop, 4)).toBe(3);
    expect(stepForLine(loop, 5)).toBe(4);
  });
  it("attributes function calls to the call line", () => {
    const withCall = [step(0, 6), step(1, 7), step(2, 7)];
    expect(stepForLine(withCall, 6)).toBe(1);
    expect(stepForLine(withCall, 3)).toBe(0);
  });
});

describe("step helpers", () => {
  it("clamps the step to the valid range", () => {
    expect(clampStep(-1, 3)).toBe(0);
    expect(clampStep(9, 3)).toBe(3);
  });
  it("finds the step line", () => {
    expect(lineForStep([step(0, 3)], 1)).toBe(3);
    expect(lineForStep([step(0, 3)], 0)).toBeNull();
  });
});

describe("formatting", () => {
  it("labels the basis with qubit 0 on the right", () => {
    expect(basisLabel(1, 2)).toBe("|01⟩");
    expect(basisLabel(4, 3)).toBe("|100⟩");
  });
  it("writes phases as fractions of π", () => {
    expect(formatPhase(0)).toBe("0");
    expect(formatPhase(Math.PI)).toBe("π");
    expect(formatPhase(-Math.PI / 2)).toBe("−π/2");
    expect(formatPhase((3 * Math.PI) / 4)).toBe("3π/4");
  });
  it("escreve amplitudes e porcentagens", () => {
    expect(formatAmplitude([0.707107, 0])).toBe("0.707");
    expect(formatAmplitude([0, -0.707107])).toBe("−0.707i");
    expect(formatPercent(1)).toBe("100%");
    expect(formatPercent(0.5)).toMatch(/^50[.,]0%$/);
    expect(formatPercent(0)).toBe("0%");
  });
  it("knows the rotation axis of the basic gates", () => {
    expect(rotationAxis(step(0, 1, "x"))).toEqual([1, 0, 0]);
    expect(rotationAxis(step(0, 1, "cx"))).toBeNull();
  });
});

describe("emaranhamento", () => {
  const h = Math.SQRT1_2;
  it("concurrence 1 for Bell states and 0 for product states", () => {
    expect(concurrence([[h, 0], [0, 0], [0, 0], [h, 0]])).toBeCloseTo(1);
    expect(concurrence([[0, 0], [h, 0], [0, -h], [0, 0]])).toBeCloseTo(1);
    expect(concurrence([[h, 0], [h, 0], [0, 0], [0, 0]])).toBeCloseTo(0); // |0⟩ ⊗ |+⟩
    expect(concurrence([[1, 0], [0, 0], [0, 0], [0, 0]])).toBeCloseTo(0);
  });
  it("converts purity into entanglement with the rest", () => {
    expect(entanglementWithRest(1)).toBe(0);
    expect(entanglementWithRest(0.5)).toBe(1);
  });
  it("computes the fidelity between Bloch vectors", () => {
    expect(blochFidelity([0, 0, 1], [0, 0, 1])).toBe(1);
    expect(blochFidelity([0, 0, 1], [0, 0, -1])).toBe(0);
    expect(blochFidelity([1, 0, 0], [0, 0, 0])).toBe(0.5);
  });
});

describe("Q-Sphere", () => {
  it("puts |00⟩ at the north pole, |11⟩ at the south and the others on the equator", () => {
    const [p00, p01, p10, p11] = qspherePositions(2);
    expect(p00[1]).toBeCloseTo(1);
    expect(p11[1]).toBeCloseTo(-1);
    expect(p01[1]).toBeCloseTo(0);
    expect(p10[1]).toBeCloseTo(0);
    expect(Math.hypot(p01[0] - p10[0], p01[2] - p10[2])).toBeCloseTo(2); // lados opostos
  });
  it("keeps all points on the surface", () => {
    for (const p of qspherePositions(3)) expect(Math.hypot(...p)).toBeCloseTo(1);
  });
});

describe("describeStep", () => {
  it("describes controlled gates, measurements and simple gates", () => {
    expect(describeStep({ ...step(0, 1, "cx"), qubits: [0, 1], num_ctrl: 1 })).toBe("CX q0 → q1");
    expect(describeStep({ ...step(0, 1, "measure"), kind: "measure", clbits: [0] })).toBe("Measure q0 → c0");
    expect(describeStep(step(0, 1, "h"))).toBe("H q0");
  });
});

describe("registerState", () => {
  const h = Math.SQRT1_2;
  it("extracts the register when the rest is in a product state (ancilla in |−⟩)", () => {
    // |q1 q0⟩ = |−⟩ ⊗ |+⟩: register = qubit 0 in |+⟩
    const amplitudes: [number, number][] = [[0.5, 0], [0.5, 0], [-0.5, 0], [-0.5, 0]];
    const state = registerState(amplitudes, 2, [0]);
    expect(state.amplitudes?.map(([re]) => re)).toEqual([expect.closeTo(h), expect.closeTo(h)]);
  });
  it("preserva sinais relativos e escolhe a maior amplitude como positiva", () => {
    const amplitudes: [number, number][] = [[-0.6, 0], [0.8, 0]];
    const state = registerState(amplitudes, 1, [0]);
    expect(state.amplitudes?.map(([re]) => re)).toEqual([expect.closeTo(-0.6), expect.closeTo(0.8)]);
  });
  it("tolera amplitudes arredondadas a 6 casas", () => {
    const r = 0.353553; // 1/√8 arredondado
    const amplitudes = Array.from({ length: 8 }, (_, k): [number, number] => [r * Math.cos((5 * k * Math.PI) / 4), r * Math.sin((5 * k * Math.PI) / 4)]);
    const state = registerState(amplitudes, 3, [0, 1, 2]);
    expect(state.amplitudes).not.toBeNull();
    expect(state.amplitudes![0][1]).toBeCloseTo(0); // |000⟩ is the phase reference
    expect(state.amplitudes![0][0]).toBeGreaterThan(0);
  });
  it("returns only probabilities when the register is entangled", () => {
    const bell: [number, number][] = [[h, 0], [0, 0], [0, 0], [h, 0]];
    const state = registerState(bell, 2, [0]);
    expect(state.amplitudes).toBeNull();
    expect(state.probabilities).toEqual([expect.closeTo(0.5), expect.closeTo(0.5)]);
  });
});

describe("modularSequence", () => {
  it("finds the period of 7^x mod 15", () => {
    const { values, period } = modularSequence(7, 15, 8);
    expect(values).toEqual([1, 7, 4, 13, 1, 7, 4, 13]);
    expect(period).toBe(4);
  });
});

describe("curve helpers", () => {
  it("picks round linear ticks and extends the axis to them", () => {
    expect(niceTicks(0, 1, 5)).toEqual([0, 0.2, 0.4, 0.6, 0.8, 1]);
    const axis = makeAxis(-0.97, 0.02, false, 100, 0);
    expect(axis.low).toBeLessThanOrEqual(-0.97);
    expect(axis.high).toBeGreaterThanOrEqual(0.02);
    expect(axis.scale(axis.low)).toBeCloseTo(100);
    expect(axis.scale(axis.high)).toBeCloseTo(0);
  });
  it("uses powers of ten on log axes", () => {
    const axis = makeAxis(0.018, 0.19, true, 0, 100);
    expect([axis.low, axis.high]).toEqual([0.01, 1]);
    expect(axis.ticks).toEqual([0.01, 0.03, 0.1, 0.3, 1]);
    expect(axis.scale(0.1)).toBeCloseTo(50);
    expect(logTicks(1, 1000)).toEqual([1, 10, 100, 1000]);
  });
  it("copes with a constant series", () => {
    const axis = makeAxis(3, 3, false, 0, 10);
    expect(axis.high).toBeGreaterThan(axis.low);
  });
  it("formats tick labels compactly", () => {
    expect(formatTick(-1)).toBe("−1");
    expect(formatTick(0.25)).toBe("0.25");
    expect(formatTick(500)).toBe("500");
    expect(formatTick(0.0001)).toBe("1e−4");
  });
  it("drops points that cannot be drawn and charts left empty", () => {
    const charts = cleanCurves({
      x_label: "n", y_label: "v", log_y: true,
      series: [{ label: "a", x: [1, 2, 3, 4], y: [1, 0, null, -2] }, { label: "b", x: [1], y: [null] }],
    });
    expect(charts).toHaveLength(1);
    expect(charts[0].series).toHaveLength(1);
    expect(charts[0].series[0].y).toEqual([1]);
    expect(cleanCurves(null)).toEqual([]);
    expect(cleanCurves([{ series: "nope" }])).toEqual([]);
  });
});
