import type { Complex, Step, Vec3 } from "../engine/types";
import { formatNumber, t } from "../i18n";

/** Rótulo do estado da base no padrão do Qiskit: |q_{n-1} ... q_0⟩ (qubit 0 à direita). */
export function basisLabel(index: number, numQubits: number): string {
  return `|${index.toString(2).padStart(numQubits, "0")}⟩`;
}

export function probability([re, im]: Complex): number {
  return re * re + im * im;
}

export function phaseOf([re, im]: Complex): number {
  return Math.atan2(im, re);
}

/**
 * Cor da fase em uma roda cíclica: 0 = azul, π = laranja.
 * A cor nunca é a única pista: quem usa a fase também mostra o ângulo.
 */
export function phaseColor(phase: number, dark: boolean): string {
  const degrees = (((phase * 180) / Math.PI) % 360 + 360) % 360;
  const hue = (212 + degrees) % 360;
  // Sintaxe com vírgulas: aceita tanto pelo CSS quanto pelo THREE.Color.
  return `hsl(${hue.toFixed(0)}, ${dark ? 52 : 58}%, ${dark ? 62 : 42}%)`;
}

export function formatPhase(phase: number): string {
  const ratio = phase / Math.PI;
  if (Math.abs(ratio) < 5e-4) return "0";
  for (const denominator of [1, 2, 3, 4, 6, 8]) {
    const numerator = ratio * denominator;
    if (Math.abs(numerator - Math.round(numerator)) < 5e-4) {
      const n = Math.round(numerator);
      const head = Math.abs(n) === 1 ? "π" : `${Math.abs(n)}π`;
      return `${n < 0 ? "−" : ""}${head}${denominator === 1 ? "" : `/${denominator}`}`;
    }
  }
  return `${ratio.toFixed(2).replace("-", "−")}π`;
}

export function formatAmplitude([re, im]: Complex): string {
  const f = (v: number) => Math.abs(v).toFixed(3);
  if (Math.abs(im) < 5e-4) return `${re < 0 ? "−" : ""}${f(re)}`;
  if (Math.abs(re) < 5e-4) return `${im < 0 ? "−" : ""}${f(im)}i`;
  return `${re < 0 ? "−" : ""}${f(re)} ${im < 0 ? "−" : "+"} ${f(im)}i`;
}

export function formatPercent(p: number): string {
  const value = p * 100;
  if (value > 0 && value < 0.1) return `<${formatNumber(0.1, 1)}%`;
  return `${formatNumber(value, value >= 99.95 || value < 0.05 ? 0 : 1)}%`;
}

export function vectorLength([x, y, z]: Vec3): number {
  return Math.hypot(x, y, z);
}

/** Descrição curta de um passo para legendas: "CX q0 → q1", "H q0", "Medição q0 → c0". */
export function describeStep(step: Step): string {
  const qubits = step.qubits.map((q) => `q${q}`);
  if (step.kind === "measure") return t("step.measure", { qubit: qubits[0], clbit: step.clbits[0] });
  if (step.kind === "noop") return t("step.barrier");
  if (step.kind === "conditional") return step.label;
  if (step.num_ctrl > 0 && step.qubits.length > step.num_ctrl) {
    const controls = qubits.slice(0, step.num_ctrl).join(", ");
    const targets = qubits.slice(step.num_ctrl).join(", ");
    return `${step.name.toUpperCase()} ${controls} → ${targets}`;
  }
  return `${step.label} ${qubits.join(", ")}`;
}

/** Eixo de rotação (em coordenadas de Bloch) de portas de 1 qubit conhecidas. */
export function rotationAxis(step: Step | undefined): Vec3 | null {
  if (!step || step.kind !== "gate" || step.qubits.length !== 1) return null;
  switch (step.name) {
    case "x":
    case "rx":
    case "sx":
      return [1, 0, 0];
    case "y":
    case "ry":
      return [0, 1, 0];
    case "z":
    case "rz":
    case "s":
    case "sdg":
    case "t":
    case "tdg":
    case "p":
      return [0, 0, 1];
    case "h":
      return [Math.SQRT1_2, 0, Math.SQRT1_2];
    default:
      return null;
  }
}

function multiply([a, b]: Complex, [c, d]: Complex): Complex {
  return [a * c - b * d, a * d + b * c];
}

/**
 * Concorrência de um estado puro de 2 qubits: 0 = separável, 1 = maximamente
 * emaranhado. C = 2|a00·a11 − a01·a10| (índices na ordem |q1 q0⟩).
 */
export function concurrence(amplitudes: readonly Complex[]): number {
  if (amplitudes.length !== 4) throw new Error("A concorrência é definida aqui só para 2 qubits.");
  const [re1, im1] = multiply(amplitudes[0], amplitudes[3]);
  const [re2, im2] = multiply(amplitudes[1], amplitudes[2]);
  return Math.min(1, 2 * Math.hypot(re1 - re2, im1 - im2));
}

/**
 * Emaranhamento de um qubit com o restante, pela pureza do estado reduzido:
 * 2(1 − Tr ρ²) vai de 0 (estado puro, sem emaranhamento) a 1 (máximo).
 */
export function entanglementWithRest(purity: number): number {
  return Math.max(0, Math.min(1, 2 * (1 - purity)));
}

/** Fidelidade entre dois estados de 1 qubit pelos vetores de Bloch (exata se um deles é puro). */
export function blochFidelity(a: Vec3, b: Vec3): number {
  return (1 + a[0] * b[0] + a[1] * b[1] + a[2] * b[2]) / 2;
}

/** Posição de cada estado da base na Q-Sphere: latitude pelo número de 1s, longitude espalhada. */
export function qspherePositions(numQubits: number): Vec3[] {
  const size = 2 ** numQubits;
  const groups = new Map<number, number[]>();
  for (let index = 0; index < size; index++) {
    const weight = popcount(index);
    groups.set(weight, [...(groups.get(weight) ?? []), index]);
  }
  const positions: Vec3[] = new Array(size);
  for (const [weight, members] of groups) {
    const theta = (Math.PI * weight) / numQubits;
    members.forEach((index, k) => {
      const phi = (2 * Math.PI * k) / members.length + (weight % 2 ? Math.PI / members.length : 0);
      // Coordenadas de cena: y para cima (|0…0⟩ no polo norte).
      positions[index] = [Math.sin(theta) * Math.cos(phi), Math.cos(theta), Math.sin(theta) * Math.sin(phi)];
    });
  }
  return positions;
}

function popcount(value: number): number {
  let count = 0;
  for (let v = value; v; v >>= 1) count += v & 1;
  return count;
}

export interface RegisterState {
  /** Amplitudes do registrador (2^k), ou null se ele estiver emaranhado com o resto. */
  amplitudes: Complex[] | null;
  probabilities: number[];
}

/**
 * Estado de um registrador (subconjunto de qubits).
 *
 * Se o registrador não está emaranhado com os demais qubits (ex.: auxiliar em
 * |−⟩ em Deutsch-Jozsa), o estado dele é puro e pode ser extraído projetando o
 * resto no ramo de maior peso. A fase global é escolhida para que a maior
 * amplitude seja real e positiva. Se estiver emaranhado, sobram as probabilidades.
 */
export function registerState(amplitudes: readonly Complex[], numQubits: number, register: readonly number[]): RegisterState {
  const size = 2 ** register.length;
  const rest = [...Array(numQubits).keys()].filter((q) => !register.includes(q));
  const branches = new Map<number, Complex[]>();
  const probabilities = new Array<number>(size).fill(0);

  amplitudes.forEach((amplitude, index) => {
    let value = 0;
    register.forEach((qubit, position) => (value |= ((index >> qubit) & 1) << position));
    let other = 0;
    rest.forEach((qubit, position) => (other |= ((index >> qubit) & 1) << position));
    const branch = branches.get(other) ?? Array.from({ length: size }, (): Complex => [0, 0]);
    branch[value] = amplitude;
    branches.set(other, branch);
    probabilities[value] += probability(amplitude);
  });

  const norm = (v: Complex[]) => v.reduce((sum, a) => sum + probability(a), 0);
  let best: Complex[] = [];
  let bestNorm = -1;
  for (const branch of branches.values()) {
    const n = norm(branch);
    if (n > bestNorm) [best, bestNorm] = [branch, n];
  }
  const scale = 1 / Math.sqrt(bestNorm);
  const unit = best.map(([re, im]): Complex => [re * scale, im * scale]);

  // Produto (não emaranhado) se a soma das projeções de todos os ramos no ramo escolhido for 1.
  let overlap = 0;
  for (const branch of branches.values()) {
    let re = 0;
    let im = 0;
    unit.forEach(([ur, ui], i) => {
      const [br, bi] = branch[i];
      re += ur * br + ui * bi;
      im += ur * bi - ui * br;
    });
    overlap += re * re + im * im;
  }
  // Tolerância relativa: as amplitudes chegam arredondadas a 6 casas.
  const total = probabilities.reduce((sum, p) => sum + p, 0);
  if (overlap < total * (1 - 1e-4)) return { amplitudes: null, probabilities };

  let peak = 0;
  unit.forEach((a, i) => {
    // Empates (comuns, com amplitudes arredondadas) ficam com o primeiro estado: |0…0⟩ vira a referência de fase.
    if (probability(a) > probability(unit[peak]) + 1e-5) peak = i;
  });
  const [pr, pi] = unit[peak];
  const magnitude = Math.hypot(pr, pi) || 1;
  const [cr, ci] = [pr / magnitude, -pi / magnitude]; // multiplica por e^{-i·fase do pico}
  const rotated = unit.map(([re, im]): Complex => [re * cr - im * ci, re * ci + im * cr]);
  return { amplitudes: rotated, probabilities };
}

/** Probabilidade de cada valor de um registrador, a partir das probabilidades da base inteira. */
export function registerProbabilities(probabilities: readonly number[], register: readonly number[]): number[] {
  const result = new Array<number>(2 ** register.length).fill(0);
  probabilities.forEach((p, index) => {
    let value = 0;
    register.forEach((qubit, position) => (value |= ((index >> qubit) & 1) << position));
    result[value] += p;
  });
  return result;
}

/** Valores de a^x mod N para x = 0 … count−1 e o período (ou null). */
export function modularSequence(a: number, N: number, count: number): { values: number[]; period: number | null } {
  const values: number[] = [];
  let value = 1 % N;
  for (let x = 0; x < count; x++) {
    values.push(value);
    value = (value * a) % N;
  }
  const period = values.findIndex((v, x) => x > 0 && v === 1);
  return { values, period: period > 0 ? period : null };
}
