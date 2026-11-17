import { useState } from "react";
import { t } from "../strings";
import { selectCurrentStep, useStore } from "../state/store";

/** Composer gates: the ones used in Track 1. */
const GATES: { name: string; label: string; controlled?: boolean; measure?: boolean }[] = [
  { name: "h", label: "H" },
  { name: "x", label: "X" },
  { name: "y", label: "Y" },
  { name: "z", label: "Z" },
  { name: "s", label: "S" },
  { name: "sdg", label: "S†" },
  { name: "t", label: "T" },
  { name: "tdg", label: "T†" },
  { name: "cx", label: "CNOT", controlled: true },
  { name: "measure", label: "Measure", measure: true },
];

/** A line that is just a composer gate (the composer may remove it). */
const GATE_LINE = /^\s*qc\.(h|x|y|z|s|sdg|t|tdg|cx|measure)\(\s*\d+\s*(,\s*\d+\s*)?\)\s*(#.*)?$/;

/** The composer only works with a QuantumCircuit named qc (the convention of the Qiskit lessons). */
export function composerSupported(code: string, framework: string | undefined): boolean {
  return (framework ?? "qiskit") === "qiskit" && /^\s*qc\s*=\s*QuantumCircuit\(/m.test(code);
}

function appendLine(code: string, line: string): string {
  return `${code.replace(/\s*$/, "")}\n${line}\n`;
}

export function Composer() {
  const code = useStore((s) => s.code);
  const result = useStore((s) => s.result);
  const current = useStore(selectCurrentStep);
  const setCode = useStore((s) => s.setCode);
  const [gate, setGate] = useState<(typeof GATES)[number] | null>(null);
  const [control, setControl] = useState<number | null>(null);

  const qubits = result?.num_qubits ?? 0;
  const clbits = result?.num_clbits ?? 0;
  const step = current > 0 ? result?.steps[current - 1] : undefined;
  const lines = code.split("\n");
  const removable = step !== undefined && GATE_LINE.test(lines[step.line - 1] ?? "");

  const reset = () => {
    setGate(null);
    setControl(null);
  };

  const pickQubit = (q: number) => {
    if (!gate) return;
    if (gate.controlled && control === null) {
      setControl(q);
      return;
    }
    const line = gate.controlled ? `qc.cx(${control}, ${q})` : gate.measure ? `qc.measure(${q}, ${q})` : `qc.${gate.name}(${q})`;
    setCode(appendLine(code, line));
    reset();
  };

  const remove = () => {
    if (!step || !removable) return;
    setCode(lines.filter((_, index) => index !== step.line - 1).join("\n"));
  };

  const prompt = !gate
    ? t("composer.pickGate")
    : gate.controlled
      ? control === null ? t("composer.pickControl") : t("composer.pickTarget", { control })
      : t("composer.pickQubit", { gate: gate.label });

  return (
    <div className="composer" aria-label={t("composer.aria")}>
      <div className="composer-palette" role="toolbar" aria-label={t("composer.gates")}>
        {GATES.map((option) => {
          const disabled = qubits === 0 || (option.controlled && qubits < 2) || (option.measure && clbits === 0);
          return (
            <button
              key={option.name}
              className="composer-gate"
              aria-pressed={gate?.name === option.name}
              disabled={disabled}
              title={option.measure && clbits === 0 ? t("composer.noClbits") : t(`gate.${option.name}` as never)}
              onClick={() => {
                setGate(gate?.name === option.name ? null : option);
                setControl(null);
              }}
            >
              {option.label}
            </button>
          );
        })}
        <span className="grow" />
        <button className="btn btn-ghost btn-sm" onClick={remove} disabled={!removable} title={t("composer.removeHint")}>
          {t("composer.remove")}
        </button>
      </div>
      <div className="composer-prompt" aria-live="polite">
        <span className="muted small">{prompt}</span>
        {gate &&
          Array.from({ length: gate.measure ? Math.min(qubits, clbits) : qubits }, (_, q) => (
            <button key={q} className="btn btn-sm composer-qubit" disabled={q === control} onClick={() => pickQubit(q)}>
              q{q}
            </button>
          ))}
        {gate && (
          <button className="link small" onClick={reset}>{t("composer.cancel")}</button>
        )}
      </div>
    </div>
  );
}
