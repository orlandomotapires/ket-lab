import { describe, expect, it } from "vitest";
import { setLocale } from "../i18n";

setLocale("pt");
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
import { clampStep, lineForStep, stepForLine } from "./steps";

const step = (index: number, line: number, name = "h"): Step => ({
  index, line, name, kind: "gate", label: name.toUpperCase(), qubits: [0], clbits: [],
  num_ctrl: 0, outcome: null, applied: null,
});

describe("stepForLine", () => {
  const straight = [step(0, 3), step(1, 5)];
  it("mostra o estado inicial antes da primeira porta", () => {
    expect(stepForLine(straight, 2)).toBe(0);
  });
  it("inclui a instrução da linha do cursor", () => {
    expect(stepForLine(straight, 3)).toBe(1);
    expect(stepForLine(straight, 4)).toBe(1);
    expect(stepForLine(straight, 5)).toBe(2);
    expect(stepForLine(straight, 99)).toBe(2);
  });
  it("em laços, escolhe a última ocorrência da linha na ordem de execução", () => {
    const loop = [step(0, 4), step(1, 5), step(2, 4), step(3, 5)];
    expect(stepForLine(loop, 4)).toBe(3);
    expect(stepForLine(loop, 5)).toBe(4);
  });
  it("atribui chamadas de função à linha da chamada", () => {
    const withCall = [step(0, 6), step(1, 7), step(2, 7)];
    expect(stepForLine(withCall, 6)).toBe(1);
    expect(stepForLine(withCall, 3)).toBe(0);
  });
});

describe("auxiliares de passo", () => {
  it("limita o passo ao intervalo válido", () => {
    expect(clampStep(-1, 3)).toBe(0);
    expect(clampStep(9, 3)).toBe(3);
  });
  it("encontra a linha do passo", () => {
    expect(lineForStep([step(0, 3)], 1)).toBe(3);
    expect(lineForStep([step(0, 3)], 0)).toBeNull();
  });
});

describe("formatação", () => {
  it("rotula a base com o qubit 0 à direita", () => {
    expect(basisLabel(1, 2)).toBe("|01⟩");
    expect(basisLabel(4, 3)).toBe("|100⟩");
  });
  it("escreve fases como frações de π", () => {
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
  it("conhece o eixo de rotação das portas básicas", () => {
    expect(rotationAxis(step(0, 1, "x"))).toEqual([1, 0, 0]);
    expect(rotationAxis(step(0, 1, "cx"))).toBeNull();
  });
});

describe("emaranhamento", () => {
  const h = Math.SQRT1_2;
  it("concorrência 1 nos estados de Bell e 0 em estados produto", () => {
    expect(concurrence([[h, 0], [0, 0], [0, 0], [h, 0]])).toBeCloseTo(1);
    expect(concurrence([[0, 0], [h, 0], [0, -h], [0, 0]])).toBeCloseTo(1);
    expect(concurrence([[h, 0], [h, 0], [0, 0], [0, 0]])).toBeCloseTo(0); // |0⟩ ⊗ |+⟩
    expect(concurrence([[1, 0], [0, 0], [0, 0], [0, 0]])).toBeCloseTo(0);
  });
  it("converte pureza em emaranhamento com o restante", () => {
    expect(entanglementWithRest(1)).toBe(0);
    expect(entanglementWithRest(0.5)).toBe(1);
  });
  it("calcula a fidelidade entre vetores de Bloch", () => {
    expect(blochFidelity([0, 0, 1], [0, 0, 1])).toBe(1);
    expect(blochFidelity([0, 0, 1], [0, 0, -1])).toBe(0);
    expect(blochFidelity([1, 0, 0], [0, 0, 0])).toBe(0.5);
  });
});

describe("Q-Sphere", () => {
  it("põe |00⟩ no polo norte, |11⟩ no sul e os demais no equador", () => {
    const [p00, p01, p10, p11] = qspherePositions(2);
    expect(p00[1]).toBeCloseTo(1);
    expect(p11[1]).toBeCloseTo(-1);
    expect(p01[1]).toBeCloseTo(0);
    expect(p10[1]).toBeCloseTo(0);
    expect(Math.hypot(p01[0] - p10[0], p01[2] - p10[2])).toBeCloseTo(2); // lados opostos
  });
  it("mantém todos os pontos na superfície", () => {
    for (const p of qspherePositions(3)) expect(Math.hypot(...p)).toBeCloseTo(1);
  });
});

describe("describeStep", () => {
  it("descreve portas controladas, medições e portas simples", () => {
    expect(describeStep({ ...step(0, 1, "cx"), qubits: [0, 1], num_ctrl: 1 })).toBe("CX q0 → q1");
    expect(describeStep({ ...step(0, 1, "measure"), kind: "measure", clbits: [0] })).toBe("Medição q0 → c0");
    expect(describeStep(step(0, 1, "h"))).toBe("H q0");
  });
});

describe("registerState", () => {
  const h = Math.SQRT1_2;
  it("extrai o registrador quando o resto está em produto (auxiliar em |−⟩)", () => {
    // |q1 q0⟩ = |−⟩ ⊗ |+⟩: registrador = qubit 0 em |+⟩
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
    expect(state.amplitudes![0][1]).toBeCloseTo(0); // |000⟩ é a referência de fase
    expect(state.amplitudes![0][0]).toBeGreaterThan(0);
  });
  it("devolve só probabilidades quando o registrador está emaranhado", () => {
    const bell: [number, number][] = [[h, 0], [0, 0], [0, 0], [h, 0]];
    const state = registerState(bell, 2, [0]);
    expect(state.amplitudes).toBeNull();
    expect(state.probabilities).toEqual([expect.closeTo(0.5), expect.closeTo(0.5)]);
  });
});

describe("modularSequence", () => {
  it("encontra o período de 7^x mod 15", () => {
    const { values, period } = modularSequence(7, 15, 8);
    expect(values).toEqual([1, 7, 4, 13, 1, 7, 4, 13]);
    expect(period).toBe(4);
  });
});
