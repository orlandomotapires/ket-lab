import type { Step } from "../engine/types";
import { describeStep } from "../lib/quantum";
import { t } from "../strings";
import { selectCurrentStep, useStore } from "../state/store";

const LEFT = 46;
const COL = 48;
const ROW = 40;
const TOP = 26;
const BOX = 28;
/** Drawing is done at the scale above and enlarged: legible gates without redoing the geometry. */
const SCALE = 1.3;

/** Width of a gate box, from the label length (12 px mono font). */
function boxWidth(label: string): number {
  return Math.max(BOX, label.length * 7.2 + 12);
}

/** Column width: fits the widest box, with some slack (parameterized gates get wide). */
function columnWidth(step: Step): number {
  const label = step.kind === "conditional" ? step.label.replace(/ if .*/, "") : step.label;
  return Math.max(COL, boxWidth(label) + 14);
}

function rowY(row: number): number {
  return TOP + row * ROW;
}

function GateColumn({ step, x, classicalY }: { step: Step; x: number; classicalY: number | null }) {
  const rows = step.qubits;
  const ys = rows.map(rowY);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const box = (y: number, label: string, key: string, dashed = false) => {
    const width = boxWidth(label);
    return (
      <g key={key}>
        <rect className={`gate-box${dashed ? " is-dashed" : ""}`} x={x - width / 2} y={y - BOX / 2} width={width} height={BOX} rx={5} />
        <text className="gate-label" x={x} y={y + 4}>{label}</text>
      </g>
    );
  };

  if (step.kind === "noop") {
    return <line className="gate-barrier" x1={x} x2={x} y1={minY - ROW / 2 + 6} y2={maxY + ROW / 2 - 6} />;
  }
  if (step.kind === "measure") {
    return (
      <g>
        {classicalY !== null && <line className="gate-link is-classical" x1={x} x2={x} y1={ys[0]} y2={classicalY} />}
        {box(ys[0], step.outcome === null ? "M" : `M=${step.outcome}`, "m")}
      </g>
    );
  }
  if (step.name === "swap") {
    return (
      <g>
        <line className="gate-link" x1={x} x2={x} y1={minY} y2={maxY} />
        {ys.map((y) => (
          <path key={y} className="gate-cross" d={`M${x - 5} ${y - 5}l10 10M${x + 5} ${y - 5}l-10 10`} />
        ))}
      </g>
    );
  }
  if (step.kind === "gate" && step.num_ctrl > 0 && step.num_ctrl < rows.length) {
    const targets = ys.slice(step.num_ctrl);
    const isNot = step.label === "X" && targets.length === 1;
    return (
      <g>
        <line className="gate-link" x1={x} x2={x} y1={minY} y2={maxY} />
        {ys.slice(0, step.num_ctrl).map((y) => (
          <circle key={y} className="gate-control" cx={x} cy={y} r={4} />
        ))}
        {isNot ? (
          <g>
            <circle className="gate-target" cx={x} cy={targets[0]} r={10} />
            <path className="gate-cross" d={`M${x - 10} ${targets[0]}h20M${x} ${targets[0] - 10}v20`} />
          </g>
        ) : (
          targets.map((y) => box(y, step.label, `t${y}`))
        )}
      </g>
    );
  }
  // Plain (or conditional) gate: one box per qubit, linked when there is more than one.
  const dashed = step.kind === "conditional" && step.applied === false;
  const label = step.kind === "conditional" ? step.label.replace(/ if .*/, "") : step.label;
  return (
    <g>
      {rows.length > 1 && <line className="gate-link" x1={x} x2={x} y1={minY} y2={maxY} />}
      {step.kind === "conditional" && classicalY !== null && (
        <line className="gate-link is-classical" x1={x} x2={x} y1={maxY} y2={classicalY} />
      )}
      {ys.map((y) => box(y, label, `b${y}`, dashed))}
    </g>
  );
}

export function CircuitDiagram() {
  const result = useStore((s) => s.result);
  const current = useStore(selectCurrentStep);
  const setStep = useStore((s) => s.setStep);

  if (!result) return <div className="circuit-empty muted">{t("circuit.empty")}</div>;

  const { num_qubits: n, num_clbits, steps } = result;
  const classicalY = num_clbits > 0 ? rowY(n) : null;
  // Position of each column: sum of the previous widths.
  const widths = steps.map(columnWidth);
  const starts: number[] = [];
  widths.reduce((offset, w, i) => ((starts[i] = offset), offset + w), LEFT);
  const width = LEFT + (widths.reduce((a, b) => a + b, 0) || COL) + 20;
  const height = rowY(n - 1 + (num_clbits > 0 ? 1 : 0)) + TOP;

  // Keyboard: arrows, Home and End walk through the steps; the current step is announced.
  const onKeyDown = (event: React.KeyboardEvent) => {
    const target = { ArrowRight: current + 1, ArrowLeft: current - 1, Home: 0, End: steps.length }[event.key];
    if (target === undefined) return;
    event.preventDefault();
    setStep(Math.max(0, Math.min(steps.length, target)));
  };
  const announcement = current === 0
    ? t("viz.initial")
    : t("circuit.current", { n: current, total: steps.length, label: describeStep(steps[current - 1]) });

  return (
    <div
      className={`circuit-scroll${steps.length === 0 ? " is-empty" : ""}`}
      tabIndex={0}
      onKeyDown={onKeyDown}
      aria-label={t("circuit.keyboard")}
      aria-describedby="circuit-current"
    >
      <p id="circuit-current" className="sr-only" aria-live="polite">{announcement}</p>
      <svg
        className="circuit"
        width={width * SCALE}
        height={height * SCALE}
        viewBox={`0 0 ${width} ${height}`}
        role="img" aria-label={t("circuit.aria", { qubits: n, steps: steps.length })}>
        {Array.from({ length: n }, (_, q) => (
          <g key={q}>
            <text className="wire-label" x={10} y={rowY(q) + 4}>q{q}</text>
            <line className="wire" x1={LEFT - 12} x2={width - 8} y1={rowY(q)} y2={rowY(q)} />
          </g>
        ))}
        {classicalY !== null && (
          <g>
            <text className="wire-label" x={10} y={classicalY + 4}>c</text>
            <line className="wire is-classical" x1={LEFT - 12} x2={width - 8} y1={classicalY - 1.5} y2={classicalY - 1.5} />
            <line className="wire is-classical" x1={LEFT - 12} x2={width - 8} y1={classicalY + 1.5} y2={classicalY + 1.5} />
          </g>
        )}
        {steps.map((step, index) => {
          const columnW = widths[index];
          const x = starts[index] + columnW / 2;
          const state = index + 1 === current ? " is-current" : index + 1 > current ? " is-pending" : "";
          return (
            <g key={index} className={`gate${state}`} onClick={() => setStep(index + 1)}>
              <title>{t("circuit.stepTitle", { n: index + 1, line: step.line, label: step.label })}</title>
              <rect className="gate-hit" x={x - columnW / 2 + 2} y={2} width={columnW - 4} height={height - 4} rx={6} />
              <GateColumn step={step} x={x} classicalY={classicalY} />
            </g>
          );
        })}
      </svg>
      {steps.length === 0 && <p className="circuit-hint muted">{t("circuit.noGates")}</p>}
    </div>
  );
}
