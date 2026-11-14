/**
 * Visualizações de treino (Trilha 3). Os dados vêm do analysis.py da lição,
 * calculados no motor depois de executar o código do aluno.
 */
import { formatNumber, t } from "../i18n";

const W = 600;
const H = 260;

/** Rampa sequencial perceptualmente uniforme (viridis), legível nos dois temas. */
const RAMP = ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"];

function rampColor(value: number): string {
  const v = Math.max(0, Math.min(1, value)) * (RAMP.length - 1);
  const i = Math.min(Math.floor(v), RAMP.length - 2);
  const f = v - i;
  const a = parseInt(RAMP[i].slice(1), 16);
  const b = parseInt(RAMP[i + 1].slice(1), 16);
  const mix = (shift: number) => Math.round(((a >> shift) & 255) * (1 - f) + ((b >> shift) & 255) * f);
  return `rgb(${mix(16)}, ${mix(8)}, ${mix(0)})`;
}

function niceNumber(value: number): string {
  const abs = Math.abs(value);
  return formatNumber(value, abs >= 100 ? 0 : abs >= 10 ? 1 : abs >= 1 ? 2 : 3).replace("-", "−");
}

// --------------------------------------------------------------------------- //
// Paisagem de custo
// --------------------------------------------------------------------------- //

export interface LandscapeData {
  x: number[];
  y: number[];
  z: number[][];
  x_label?: string;
  y_label?: string;
  path?: number[][];
  min?: number;
  max?: number;
}

export function LandscapeView({ data }: { data: LandscapeData }) {
  const { x, y, z } = data;
  const flat = z.flat().filter((v) => v !== null && Number.isFinite(v));
  const low = data.min ?? Math.min(...flat);
  const high = data.max ?? Math.max(...flat);
  const size = H - 40;
  const left = (W - size) / 2 - 30;
  const top = 8;
  const cellW = size / x.length;
  const cellH = size / y.length;
  const toX = (value: number) => left + ((value - x[0]) / (x[x.length - 1] - x[0])) * size;
  const toY = (value: number) => top + size - ((value - y[0]) / (y[y.length - 1] - y[0])) * size;
  const path = (data.path ?? []).filter((p) => p.length >= 2);
  const points = path.map(([px, py]) => `${toX(px)},${toY(py)}`).join(" ");
  const legendX = left + size + 24;

  return (
    <>
      <svg className="view2d" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" role="img" aria-label={t("viz.view.landscape")}>
        {z.map((row, j) =>
          row.map((value, i) => (
            <rect
              key={`${i}-${j}`}
              x={left + i * cellW}
              y={top + size - (j + 1) * cellH}
              width={cellW + 0.5}
              height={cellH + 0.5}
              fill={rampColor((value - low) / (high - low || 1))}
            />
          )),
        )}
        <rect className="chart-frame" x={left} y={top} width={size} height={size} />
        {points && <polyline className="chart-path" points={points} />}
        {path.length > 0 && (
          <>
            <circle className="chart-path-start" cx={toX(path[0][0])} cy={toY(path[0][1])} r={5} />
            <circle className="chart-path-end" cx={toX(path[path.length - 1][0])} cy={toY(path[path.length - 1][1])} r={5} />
          </>
        )}
        <text className="chart-label" x={left + size / 2} y={top + size + 22} textAnchor="middle">
          {data.x_label ?? "x"}: {niceNumber(x[0])} … {niceNumber(x[x.length - 1])}
        </text>
        <text className="chart-label" x={left - 10} y={top + size / 2} textAnchor="middle" transform={`rotate(-90 ${left - 10} ${top + size / 2})`}>
          {data.y_label ?? "y"}: {niceNumber(y[0])} … {niceNumber(y[y.length - 1])}
        </text>
        {RAMP.map((_, k) => (
          <rect key={k} x={legendX} y={top + (size / RAMP.length) * k} width={12} height={size / RAMP.length + 0.5} fill={rampColor(1 - k / (RAMP.length - 1))} />
        ))}
        <text className="chart-tick" x={legendX + 18} y={top + 10}>{niceNumber(high)}</text>
        <text className="chart-tick" x={legendX + 18} y={top + size}>{niceNumber(low)}</text>
      </svg>
      <div className="stage-footer">{t("viz.landscapeNote")}</div>
    </>
  );
}

// --------------------------------------------------------------------------- //
// Convergência
// --------------------------------------------------------------------------- //

export interface ConvergenceData {
  values: number[];
  target?: number;
  band?: number;
  y_label?: string;
}

export function ConvergenceView({ data }: { data: ConvergenceData }) {
  const values = data.values.filter((v) => Number.isFinite(v));
  if (!values.length) return <div className="stage-message">{t("viz.runToSee")}</div>;
  const reference = [...values, ...(data.target !== undefined ? [data.target] : [])];
  let low = Math.min(...reference);
  let high = Math.max(...reference);
  const pad = (high - low || 1) * 0.08;
  low -= pad;
  high += pad;
  const left = 56;
  const right = W - 16;
  const top = 12;
  const bottom = H - 36;
  const x = (i: number) => left + ((right - left) * i) / Math.max(values.length - 1, 1);
  const y = (v: number) => bottom - ((v - low) / (high - low)) * (bottom - top);
  const line = values.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ");
  const last = values[values.length - 1];

  return (
    <>
      <svg className="view2d" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" role="img" aria-label={t("viz.view.convergence")}>
        <line className="chart-axis" x1={left} x2={right} y1={bottom} y2={bottom} />
        <line className="chart-axis" x1={left} x2={left} y1={top} y2={bottom} />
        {data.target !== undefined && data.band !== undefined && (
          <rect className="chart-band" x={left} width={right - left} y={y(data.target + data.band)} height={Math.max(y(data.target - data.band) - y(data.target + data.band), 1.5)} />
        )}
        {data.target !== undefined && (
          <>
            <line className="chart-target" x1={left} x2={right} y1={y(data.target)} y2={y(data.target)} />
            <text className="chart-tick" x={right} y={y(data.target) + 14} textAnchor="end">
              {t("viz.target")} {niceNumber(data.target)}
            </text>
          </>
        )}
        <path className="chart-line is-accent" d={line} />
        <circle className="chart-dot is-one" cx={x(values.length - 1)} cy={y(last)} r={4} />
        <text className="chart-value" x={x(values.length - 1) - 6} y={y(last) - 9} textAnchor="end">{niceNumber(last)}</text>
        <text className="chart-tick" x={left - 6} y={top + 8} textAnchor="end">{niceNumber(high)}</text>
        <text className="chart-tick" x={left - 6} y={bottom} textAnchor="end">{niceNumber(low)}</text>
        <text className="chart-label" x={(left + right) / 2} y={H - 10} textAnchor="middle">
          {t("viz.step")} 0 … {values.length - 1}
        </text>
        {data.y_label && (
          <text className="chart-label" x={14} y={(top + bottom) / 2} textAnchor="middle" transform={`rotate(-90 14 ${(top + bottom) / 2})`}>
            {data.y_label}
          </text>
        )}
      </svg>
      <div className="stage-footer">{data.band !== undefined ? t("viz.bandNote") : t("viz.convergenceNote")}</div>
    </>
  );
}

// --------------------------------------------------------------------------- //
// Curva de dissociação
// --------------------------------------------------------------------------- //

export interface DissociationData {
  x: number[];
  exact: number[];
  hartree_fock?: number[];
  point?: [number, number] | null;
  x_label?: string;
  y_label?: string;
}

export function DissociationView({ data }: { data: DissociationData }) {
  const all = [...data.exact, ...(data.hartree_fock ?? []), ...(data.point ? [data.point[1]] : [])];
  const low = Math.min(...all) - 0.03;
  const high = Math.max(...all) + 0.03;
  const left = 56;
  const right = W - 16;
  const top = 12;
  const bottom = H - 40;
  const x = (v: number) => left + ((v - data.x[0]) / (data.x[data.x.length - 1] - data.x[0])) * (right - left);
  const y = (v: number) => bottom - ((v - low) / (high - low)) * (bottom - top);
  const curve = (values: number[]) => values.map((v, i) => `${i ? "L" : "M"}${x(data.x[i])},${y(v)}`).join(" ");

  return (
    <>
      <svg className="view2d" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" role="img" aria-label={t("viz.view.dissociation")}>
        <line className="chart-axis" x1={left} x2={right} y1={bottom} y2={bottom} />
        <line className="chart-axis" x1={left} x2={left} y1={top} y2={bottom} />
        {data.hartree_fock && <path className="chart-line is-dashed" d={curve(data.hartree_fock)} />}
        <path className="chart-line is-accent" d={curve(data.exact)} />
        {data.point && (
          <>
            <circle className="chart-dot is-highlight" cx={x(data.point[0])} cy={y(data.point[1])} r={5} />
            <text className="chart-value" x={x(data.point[0]) + 9} y={y(data.point[1]) + 4}>
              {t("viz.yourResult")}: {niceNumber(data.point[1])}
            </text>
          </>
        )}
        <text className="chart-tick" x={left - 6} y={top + 8} textAnchor="end">{niceNumber(high)}</text>
        <text className="chart-tick" x={left - 6} y={bottom} textAnchor="end">{niceNumber(low)}</text>
        <text className="chart-tick" x={left} y={bottom + 16} textAnchor="middle">{niceNumber(data.x[0])}</text>
        <text className="chart-tick" x={right} y={bottom + 16} textAnchor="middle">{niceNumber(data.x[data.x.length - 1])}</text>
        <text className="chart-label" x={(left + right) / 2} y={H - 8} textAnchor="middle">{data.x_label ?? "x"}</text>
        {data.y_label && (
          <text className="chart-label" x={14} y={(top + bottom) / 2} textAnchor="middle" transform={`rotate(-90 14 ${(top + bottom) / 2})`}>
            {data.y_label}
          </text>
        )}
        <g transform={`translate(${right - 150}, ${top + 6})`}>
          <line className="chart-line is-accent" x1={0} x2={18} y1={0} y2={0} />
          <text className="chart-tick" x={24} y={4}>{t("viz.exact")}</text>
          {data.hartree_fock && (
            <>
              <line className="chart-line is-dashed" x1={0} x2={18} y1={16} y2={16} />
              <text className="chart-tick" x={24} y={20}>Hartree-Fock</text>
            </>
          )}
        </g>
      </svg>
      <div className="stage-footer">{t("viz.dissociationNote")}</div>
    </>
  );
}
