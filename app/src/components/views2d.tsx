/**
 * Visualizações 2D da Trilha 2: amplitudes com sinal (e linha da média), mostradores
 * de fase, histograma de um registrador e a função periódica a^x mod N do Shor.
 * São SVG simples; as cores vêm dos tokens de tema em CSS.
 */
import { t } from "../i18n";
import type { Complex } from "../engine/types";
import {
  formatPercent,
  formatPhase,
  modularSequence,
  phaseColor,
  phaseOf,
  probability,
  registerProbabilities,
  registerState,
} from "../lib/quantum";
import { useTheme } from "../theme/theme";

const W = 600;
const H = 250;
const EPSILON = 1e-9;

function bitLabel(value: number, width: number): string {
  return value.toString(2).padStart(width, "0");
}

/** Valor com sinal de uma amplitude: real quando ela é real; senão, o módulo. */
function signedValue([re, im]: Complex): number {
  return Math.abs(im) < 1e-6 ? re : Math.hypot(re, im);
}

// --------------------------------------------------------------------------- //
// Amplitudes com sinal
// --------------------------------------------------------------------------- //

export function AmplitudesView({ amplitudes, numQubits, register, scale, note }: {
  amplitudes: Complex[]; numQubits: number; register: number[]; scale: number; note?: string;
}) {
  const dark = useTheme() === "dark";
  const state = registerState(amplitudes, numQubits, register);
  const width = register.length;
  const count = 2 ** width;
  const signed = state.amplitudes !== null;
  const values = signed ? state.amplitudes!.map(signedValue) : state.probabilities.map(Math.sqrt);
  const mean = values.reduce((sum, v) => sum + v, 0) / count;

  const left = 34;
  const right = W - 10;
  const top = 16;
  const bottom = H - 34;
  const zero = signed ? (top + bottom) / 2 : bottom;
  const half = signed ? (bottom - top) / 2 : bottom - top;
  const slot = (right - left) / count;
  const bar = Math.max(3, Math.min(28, slot * 0.62));
  const y = (v: number) => zero - (v / scale) * half;
  const showLabels = count <= 16;

  return (
    <>
      <svg className="view2d" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" role="img" aria-label={t("viz.view.amplitudes")}>
        <line className="chart-axis" x1={left} x2={right} y1={zero} y2={zero} />
        {signed && (
          <>
            <text className="chart-tick" x={left - 6} y={y(scale) + 4} textAnchor="end">+{scale.toFixed(1)}</text>
            <text className="chart-tick" x={left - 6} y={y(-scale) + 4} textAnchor="end">−{scale.toFixed(1)}</text>
          </>
        )}
        {values.map((value, index) => {
          const x = left + slot * index + (slot - bar) / 2;
          const amplitude = signed ? state.amplitudes![index] : null;
          const color = amplitude && probability(amplitude) > EPSILON ? phaseColor(phaseOf(amplitude), dark) : undefined;
          const y1 = Math.min(y(value), zero);
          const height = Math.max(Math.abs(y(value) - zero), Math.abs(value) > EPSILON ? 1 : 0);
          return (
            <g key={index}>
              <title>{`|${bitLabel(index, width)}⟩  ${value.toFixed(3)}`}</title>
              <rect className={`chart-bar${signed ? "" : " is-neutral"}`} x={x} y={y1} width={bar} height={height} rx={2} style={color ? { fill: color } : undefined} />
              {showLabels && (
                <text className="chart-label" x={x + bar / 2} y={H - 14} textAnchor="middle">
                  {bitLabel(index, width)}
                </text>
              )}
            </g>
          );
        })}
        {signed && (
          <>
            <line className="chart-mean" x1={left} x2={right} y1={y(mean)} y2={y(mean)} />
            <text className="chart-mean-label" x={left + 4} y={y(mean) - 6} textAnchor="start">
              {t("viz.mean")} {mean.toFixed(3)}
            </text>
          </>
        )}
      </svg>
      <div className="stage-footer">{note ?? (signed ? t("viz.amplitudesNote") : t("viz.registerEntangled"))}</div>
    </>
  );
}

/** Escala fixa ao longo da execução: as barras não "pulam" ao navegar pelos passos. */
export function amplitudeScale(snapshots: { amplitudes: Complex[] | null }[], numQubits: number, register: number[]): number {
  let peak = 0;
  for (const snapshot of snapshots) {
    if (!snapshot.amplitudes) continue;
    const state = registerState(snapshot.amplitudes, numQubits, register);
    const values = state.amplitudes ? state.amplitudes.map(signedValue) : state.probabilities.map(Math.sqrt);
    for (const v of values) peak = Math.max(peak, Math.abs(v));
  }
  return Math.max(0.25, Math.ceil(peak * 4) / 4);
}

// --------------------------------------------------------------------------- //
// Mostradores de fase
// --------------------------------------------------------------------------- //

export function DialsView({ amplitudes, numQubits, register, note }: {
  amplitudes: Complex[]; numQubits: number; register: number[]; note?: string;
}) {
  const dark = useTheme() === "dark";
  const state = registerState(amplitudes, numQubits, register);
  const width = register.length;
  const count = 2 ** width;
  const cols = count <= 4 ? count : count <= 8 ? 4 : Math.ceil(Math.sqrt(count));
  const rows = Math.ceil(count / cols);
  const cellW = W / cols;
  const cellH = (H - 26) / rows;
  const radius = Math.min(cellW, cellH) * 0.3;

  return (
    <>
      <svg className="view2d" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" role="img" aria-label={t("viz.view.dials")}>
        {Array.from({ length: count }, (_, index) => {
          const cx = cellW * (index % cols) + cellW / 2;
          const cy = cellH * Math.floor(index / cols) + cellH / 2 - 6;
          const p = state.probabilities[index];
          const amplitude = state.amplitudes?.[index];
          const hasPhase = amplitude !== undefined && p > EPSILON;
          const phase = hasPhase ? phaseOf(amplitude) : 0;
          const color = hasPhase ? phaseColor(phase, dark) : undefined;
          return (
            <g key={index}>
              <circle className="dial-ring" cx={cx} cy={cy} r={radius} />
              {p > EPSILON && (
                <circle className="dial-disc" cx={cx} cy={cy} r={radius * Math.sqrt(p)} style={color ? { fill: color } : undefined} />
              )}
              {hasPhase && (
                <line
                  className="dial-hand"
                  x1={cx}
                  y1={cy}
                  x2={cx + radius * Math.cos(phase)}
                  y2={cy - radius * Math.sin(phase)}
                  style={{ stroke: color }}
                />
              )}
              <text className="chart-label" x={cx} y={cy + radius + 14} textAnchor="middle">
                |{bitLabel(index, width)}⟩{hasPhase ? `  ${formatPhase(phase)}` : ""}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="stage-footer">{note ?? (state.amplitudes ? t("viz.dialsNote") : t("viz.registerEntangled"))}</div>
    </>
  );
}

// --------------------------------------------------------------------------- //
// Histograma de um registrador
// --------------------------------------------------------------------------- //

/** Recebe as probabilidades da base inteira: funciona também para estados mistos. */
export function HistogramView({ probabilities, register, note }: {
  probabilities: number[]; register: number[]; note?: string;
}) {
  const state = { probabilities: registerProbabilities(probabilities, register) };
  const width = register.length;
  const count = 2 ** width;
  const left = 10;
  const right = W - 10;
  const top = 26;
  const bottom = H - 46;
  const slot = (right - left) / count;
  const bar = Math.max(3, Math.min(30, slot * 0.6));

  return (
    <>
      <svg className="view2d" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" role="img" aria-label={t("viz.view.histogram")}>
        <line className="chart-axis" x1={left} x2={right} y1={bottom} y2={bottom} />
        {state.probabilities.map((p, index) => {
          const x = left + slot * index + (slot - bar) / 2;
          const height = (bottom - top) * p;
          const peak = p > 0.01;
          return (
            <g key={index}>
              <title>{`|${bitLabel(index, width)}⟩ = ${index}/${count}  ${formatPercent(p)}`}</title>
              <rect className={`chart-bar${peak ? "" : " is-faint"}`} x={x} y={bottom - height} width={bar} height={Math.max(height, p > EPSILON ? 1 : 0)} rx={2} />
              {peak && (
                <text className="chart-value" x={x + bar / 2} y={bottom - height - 5} textAnchor="middle">
                  {formatPercent(p)}
                </text>
              )}
              <text className={`chart-label${peak ? " is-strong" : ""}`} x={x + bar / 2} y={bottom + 15} textAnchor="middle">
                {bitLabel(index, width)}
              </text>
              <text className="chart-label is-sub" x={x + bar / 2} y={bottom + 29} textAnchor="middle">
                {index}/{count}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="stage-footer">{note ?? t("viz.histogramNote", { size: count })}</div>
    </>
  );
}

// --------------------------------------------------------------------------- //
// a^x mod N
// --------------------------------------------------------------------------- //

export function ModularView({ a, N, points = 16 }: { a: number; N: number; points?: number }) {
  const { values, period } = modularSequence(a, N, points);
  const left = 34;
  const right = W - 14;
  const top = 26;
  const bottom = H - 40;
  const x = (i: number) => left + ((right - left) * i) / (points - 1);
  const y = (v: number) => bottom - ((bottom - top) * v) / (N - 1);
  const path = values.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ");

  return (
    <>
      <svg className="view2d" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" role="img" aria-label={t("viz.modularTitle", { a, N })}>
        <line className="chart-axis" x1={left} x2={right} y1={bottom} y2={bottom} />
        {[0, N - 1].map((v) => (
          <text key={v} className="chart-tick" x={left - 8} y={y(v) + 4} textAnchor="end">{v}</text>
        ))}
        {period &&
          values.map((v, i) =>
            v === 1 ? <line key={`p${i}`} className="chart-period" x1={x(i)} x2={x(i)} y1={top - 8} y2={bottom} /> : null,
          )}
        <path className="chart-line" d={path} />
        {values.map((v, i) => (
          <g key={i}>
            <circle className={`chart-dot${v === 1 ? " is-one" : ""}`} cx={x(i)} cy={y(v)} r={4} />
            <text className="chart-label is-sub" x={x(i)} y={y(v) - 9} textAnchor="middle">{v}</text>
            <text className="chart-label" x={x(i)} y={bottom + 16} textAnchor="middle">{i}</text>
          </g>
        ))}
      </svg>
      <div className="stage-footer">
        <span className="mono">{t("viz.modularTitle", { a, N })}</span>
        {" · "}
        <strong>{period ? t("viz.period", { r: period }) : t("viz.noPeriod", { limit: points - 1 })}</strong>
      </div>
    </>
  );
}
