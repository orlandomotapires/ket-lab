/**
 * Visualizações de treino (Trilha 3). Os dados vêm do analysis.py da lição,
 * calculados no motor depois de executar o código do aluno.
 */
import { formatNumber, t, type MessageKey } from "../i18n";

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
  /** Chaves de tradução da legenda das duas curvas e da nota (padrão: exata e Hartree-Fock). */
  legend?: [MessageKey, MessageKey];
  note?: MessageKey;
  point_label?: MessageKey;
}

/** Duas curvas e um ponto destacado: curva de dissociação (3.2) e curva de limiar (3.6). */
export function DissociationView({ data, label }: { data: DissociationData; label?: string }) {
  const [firstLegend, secondLegend] = data.legend ? data.legend.map((key) => t(key)) : [t("viz.exact"), "Hartree-Fock"];
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
      <svg className="view2d" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" role="img" aria-label={label ?? t("viz.view.dissociation")}>
        <line className="chart-axis" x1={left} x2={right} y1={bottom} y2={bottom} />
        <line className="chart-axis" x1={left} x2={left} y1={top} y2={bottom} />
        {data.hartree_fock && <path className="chart-line is-dashed" d={curve(data.hartree_fock)} />}
        <path className="chart-line is-accent" d={curve(data.exact)} />
        {data.point && (
          <>
            <circle className="chart-dot is-highlight" cx={x(data.point[0])} cy={y(data.point[1])} r={5} />
            <text className="chart-value" x={x(data.point[0]) + 9} y={y(data.point[1]) + 4}>
              {t(data.point_label ?? "viz.yourResult")}: {niceNumber(data.point[1])}
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
        <g transform={`translate(${right - 190}, ${top + 6})`}>
          <line className="chart-line is-accent" x1={0} x2={18} y1={0} y2={0} />
          <text className="chart-tick" x={24} y={4}>{firstLegend}</text>
          {data.hartree_fock && (
            <>
              <line className="chart-line is-dashed" x1={0} x2={18} y1={16} y2={16} />
              <text className="chart-tick" x={24} y={20}>{secondLegend}</text>
            </>
          )}
        </g>
      </svg>
      <div className="stage-footer">{t(data.note ?? "viz.dissociationNote")}</div>
    </>
  );
}

// --------------------------------------------------------------------------- //
// Grafo (Max-Cut)
// --------------------------------------------------------------------------- //

export interface GraphData {
  nodes: { id: number; x: number; y: number; side: number }[];
  edges: { a: number; b: number; cut: boolean }[];
  best_bits: string;
  best_cut: number;
  max_cut: number;
  ratio: number;
  top: { bits: string; probability: number; cut: number }[];
}

export function GraphView({ data }: { data: GraphData }) {
  const cx = 150;
  const cy = H / 2 - 6;
  const radius = 92;
  const at = (id: number) => {
    const node = data.nodes.find((n) => n.id === id)!;
    return { x: cx + node.x * radius, y: cy + node.y * radius };
  };
  const listX = 300;

  return (
    <>
      <svg className="view2d" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" role="img" aria-label={t("viz.view.graph")}>
        {data.edges.map((edge) => {
          const a = at(edge.a);
          const b = at(edge.b);
          return <line key={`${edge.a}-${edge.b}`} className={`graph-edge${edge.cut ? " is-cut" : ""}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} />;
        })}
        {data.nodes.map((node) => {
          const p = at(node.id);
          return (
            <g key={node.id}>
              {/* Forma e cor distinguem os grupos (não só a cor). */}
              {node.side ? (
                <rect className="graph-node is-b" x={p.x - 15} y={p.y - 15} width={30} height={30} rx={6} />
              ) : (
                <circle className="graph-node is-a" cx={p.x} cy={p.y} r={16} />
              )}
              <text className="graph-label" x={p.x} y={p.y + 4} textAnchor="middle">{node.id}</text>
            </g>
          );
        })}
        <text className="graph-title" x={listX} y={26}>{t("viz.graphBest")}</text>
        <text className="graph-text" x={listX} y={46}>
          |{data.best_bits}⟩ · {t("viz.graphBestDetail", { cut: data.best_cut, max: data.max_cut })}
        </text>
        <text className="graph-text" x={listX} y={66}>{t("viz.graphRatio", { ratio: formatNumber(data.ratio, 3) })}</text>
        <text className="graph-title" x={listX} y={98}>{t("viz.graphTop")}</text>
        {data.top.map((item, k) => (
          <g key={item.bits} transform={`translate(${listX}, ${116 + k * 22})`}>
            <text className="graph-text" x={0} y={4}>|{item.bits}⟩</text>
            <rect className="chart-bar" x={66} y={-5} width={Math.max(item.probability * 260, 1)} height={10} rx={2} />
            <text className="chart-tick" x={74 + item.probability * 260} y={4}>
              {formatNumber(item.probability * 100, 0)}% · {t("viz.graphCut", { cut: item.cut })}
            </text>
          </g>
        ))}
      </svg>
      <div className="stage-footer">{t("viz.graphNote")}</div>
    </>
  );
}

// --------------------------------------------------------------------------- //
// Fronteira de decisão (classificador)
// --------------------------------------------------------------------------- //

export interface BoundaryData {
  x: number[];
  y: number[];
  z: number[][];
  points: [number, number, number][];
  train_accuracy: number;
}

/** Divergente: azul (classe +1) ↔ laranja (classe −1), mais claro perto da fronteira. */
function divergingColor(value: number): string {
  const v = Math.max(-1, Math.min(1, value));
  const [r, g, b] = v >= 0 ? [47, 91, 211] : [214, 120, 30];
  const strength = 0.15 + 0.7 * Math.abs(v);
  return `rgba(${r}, ${g}, ${b}, ${strength.toFixed(3)})`;
}

export function BoundaryView({ data }: { data: BoundaryData }) {
  const { x, y, z } = data;
  const size = H - 30;
  const left = (W - size) / 2 - 40;
  const top = 6;
  const cellW = size / x.length;
  const cellH = size / y.length;
  const toX = (v: number) => left + ((v - x[0]) / (x[x.length - 1] - x[0])) * size;
  const toY = (v: number) => top + size - ((v - y[0]) / (y[y.length - 1] - y[0])) * size;
  const infoX = left + size + 20;

  return (
    <>
      <svg className="view2d" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" role="img" aria-label={t("viz.view.boundary")}>
        {z.map((row, j) =>
          row.map((value, i) => (
            <rect key={`${i}-${j}`} x={left + i * cellW} y={top + size - (j + 1) * cellH} width={cellW + 0.5} height={cellH + 0.5} fill={divergingColor(value)} />
          )),
        )}
        <rect className="chart-frame" x={left} y={top} width={size} height={size} />
        {data.points.map(([px, py, label], k) =>
          label > 0 ? (
            <circle key={k} className="boundary-point is-plus" cx={toX(px)} cy={toY(py)} r={3.6} />
          ) : (
            <rect key={k} className="boundary-point is-minus" x={toX(px) - 3.2} y={toY(py) - 3.2} width={6.4} height={6.4} />
          ),
        )}
        <circle className="boundary-point is-plus" cx={infoX + 6} cy={top + 14} r={4} />
        <text className="graph-text" x={infoX + 18} y={top + 18}>+1</text>
        <rect className="boundary-point is-minus" x={infoX + 2} y={top + 30} width={8} height={8} />
        <text className="graph-text" x={infoX + 18} y={top + 38}>−1</text>
        <text className="graph-text" x={infoX} y={top + 68}>{t("viz.trainAccuracy")}</text>
        <text className="graph-title" x={infoX} y={top + 88}>{formatNumber(data.train_accuracy * 100, 1)}%</text>
      </svg>
      <div className="stage-footer">{t("viz.boundaryNote")}</div>
    </>
  );
}
