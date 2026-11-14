import type { Step } from "../engine/types";

/**
 * Quantos passos já foram executados quando o cursor está na linha dada.
 *
 * A unidade de passo é a instrução. O cursor seleciona a ÚLTIMA instrução, na
 * ordem de execução, cuja linha de origem é menor ou igual à do cursor. Em
 * código sem laços isso equivale a "o estado depois da linha do cursor".
 * Devolve um índice de snapshot: 0 = estado inicial, k = após o k-ésimo passo.
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

/** Linha de origem do passo atual (para destacar no editor). */
export function lineForStep(steps: readonly Step[], step: number): number | null {
  return step > 0 && step <= steps.length ? steps[step - 1].line : null;
}
