/**
 * The generic `curve` view: line and point charts drawn from the lesson's analysis.py.
 * Data contract: see cleanCurves in lib/curve.ts and docs/adding-a-lesson.md.
 */
import { cleanCurves, formatTick, makeAxis, seriesStats, type CurveChart } from "../lib/curve";
import { modKey } from "../lib/platform";
import { t } from "../strings";

const W = 470;
const H = 250;
const LEFT = 50;
const RIGHT = W - 18;
const TOP = 14;
const BOTTOM = H - 44;

/** Series are told apart by color, dash pattern and marker shape, never by color alone. */
const DASHES = ["", "7 4", "2 4", "10 4 2 4"];

function Marker({ shape, x, y, className }: { shape: number; x: number; y: number; className: string }) {
  if (shape === 1) return <rect className={className} x={x - 3.5} y={y - 3.5} width={7} height={7} />;
  if (shape === 2) return <path className={className} d={`M${x},${y - 4.5} L${x + 4.5},${y} L${x},${y + 4.5} L${x - 4.5},${y} Z`} />;
  if (shape === 3) return <path className={className} d={`M${x},${y - 4.5} L${x + 4.5},${y + 3.5} L${x - 4.5},${y + 3.5} Z`} />;
  return <circle className={className} cx={x} cy={y} r={3.5} />;
}

function Chart({ chart, index }: { chart: CurveChart; index: number }) {
  const xs = chart.series.flatMap((s) => s.x).concat((chart.markers ?? []).map((m) => m.x));
  const ys = chart.series.flatMap((s) => s.y).concat((chart.markers ?? []).map((m) => m.y));
  const xAxis = makeAxis(Math.min(...xs), Math.max(...xs), chart.log_x === true, LEFT, RIGHT);
  const yAxis = makeAxis(Math.min(...ys), Math.max(...ys), chart.log_y === true, BOTTOM, TOP);
  const title = chart.title ?? `${chart.y_label} / ${chart.x_label}`;
  const titleId = `curve-title-${index}`;
  const descId = `curve-desc-${index}`;
  // Reference lines and measured series: only the latter get a color, a dash pattern and a marker.
  const measured = chart.series.filter((s) => !s.dashed);
  const measuredCount = measured.length;
  const styleOf = (s: CurveChart["series"][number]) => measured.indexOf(s);

  return (
    <figure className="curve-chart" aria-labelledby={titleId} aria-describedby={descId}>
      <figcaption id={titleId} className="curve-title">{title}</figcaption>
      {chart.series.length > 1 && (
        <ul className="curve-legend" aria-label={t("viz.curve.legend")}>
          {chart.series.map((s) => {
            const k = styleOf(s);
            return (
              <li key={s.label}>
                <svg width="30" height="12" aria-hidden="true">
                  <line className={s.dashed ? "curve-line is-reference" : `curve-line is-s${k}`} x1="1" x2="29" y1="6" y2="6" strokeDasharray={s.dashed ? undefined : DASHES[k % 4] || undefined} />
                  {!s.dashed && <Marker shape={k % 4} x={15} y={6} className={`curve-dot is-s${k % 4}`} />}
                </svg>
                {s.label}
              </li>
            );
          })}
        </ul>
      )}
      <svg className="curve-svg" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby={titleId} aria-describedby={descId}>
        {yAxis.ticks.map((v) => (
          <g key={`y${v}`}>
            <line className="curve-grid" x1={LEFT} x2={RIGHT} y1={yAxis.scale(v)} y2={yAxis.scale(v)} />
            <text className="chart-tick" x={LEFT - 7} y={yAxis.scale(v) + 4} textAnchor="end">{formatTick(v)}</text>
          </g>
        ))}
        {xAxis.ticks.map((v) => (
          <g key={`x${v}`}>
            <line className="chart-axis" x1={xAxis.scale(v)} x2={xAxis.scale(v)} y1={BOTTOM} y2={BOTTOM + 4} />
            <text className="chart-tick" x={xAxis.scale(v)} y={BOTTOM + 17} textAnchor="middle">{formatTick(v)}</text>
          </g>
        ))}
        <line className="chart-axis" x1={LEFT} x2={RIGHT} y1={BOTTOM} y2={BOTTOM} />
        <line className="chart-axis" x1={LEFT} x2={LEFT} y1={TOP} y2={BOTTOM} />
        {chart.series.map((s) => {
          const k = styleOf(s);
          const d = s.x.map((x, i) => `${i ? "L" : "M"}${xAxis.scale(x).toFixed(1)},${yAxis.scale(s.y[i]).toFixed(1)}`).join(" ");
          const showLine = s.points !== true || s.dashed;
          return (
            <g key={s.label}>
              {showLine && (
                <path
                  className={s.dashed ? "curve-line is-reference" : `curve-line is-s${k % 4}`}
                  d={d}
                  strokeDasharray={s.dashed ? undefined : DASHES[k % 4] || undefined}
                />
              )}
              {!s.dashed && (s.points === true || s.x.length <= 40) &&
                s.x.map((x, i) => (
                  <Marker key={i} shape={k % 4} x={xAxis.scale(x)} y={yAxis.scale(s.y[i])} className={`curve-dot is-s${k % 4}`} />
                ))}
            </g>
          );
        })}
        {(chart.markers ?? []).map((m) => {
          const px = xAxis.scale(m.x);
          const py = yAxis.scale(m.y);
          const flip = px > LEFT + (RIGHT - LEFT) * 0.6;
          const below = py < TOP + 26;
          return (
            <g key={`${m.x}-${m.y}-${m.label}`}>
              <circle className="curve-marker" cx={px} cy={py} r={6} />
              <text className="chart-value curve-marker-label" x={flip ? px - 10 : px + 10} y={below ? py + 18 : py - 14} textAnchor={flip ? "end" : "start"}>{m.label}</text>
            </g>
          );
        })}
        <text className="chart-label" x={(LEFT + RIGHT) / 2} y={H - 8} textAnchor="middle">{chart.x_label}{chart.log_x ? ` (${t("viz.curve.log")})` : ""}</text>
        <text className="chart-label" x={13} y={(TOP + BOTTOM) / 2} textAnchor="middle" transform={`rotate(-90 13 ${(TOP + BOTTOM) / 2})`}>
          {chart.y_label}{chart.log_y ? ` (${t("viz.curve.log")})` : ""}
        </text>
      </svg>
      <div id={descId} className="curve-summary">
        {chart.series.filter((s) => !s.dashed).map((s) => {
          const stats = seriesStats(s);
          return (
            <p key={s.label}>
              {measuredCount > 1 && <strong>{s.label}: </strong>}
              {t("viz.curve.summary", {
                count: stats.count,
                first: formatTick(stats.first),
                last: formatTick(stats.last),
                min: formatTick(stats.min),
                max: formatTick(stats.max),
              })}
            </p>
          );
        })}
        {(chart.markers ?? []).map((m) => (
          <p key={`${m.x}-${m.label}`}>{m.label}: {chart.x_label} = {formatTick(m.x)}, {chart.y_label} = {formatTick(m.y)}.</p>
        ))}
      </div>
    </figure>
  );
}

/** `live`: the code runs as it is typed (no Run button), so the chart waits for the values, not for Run. */
export function CurveView({ data, live = false }: { data: unknown; live?: boolean }) {
  const charts = cleanCurves(data);
  if (charts.length === 0) {
    return (
      <div className="curve-empty">
        <svg width="40" height="32" viewBox="0 0 40 32" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" aria-hidden="true">
          <path d="M3 2v27h35" />
          <path d="M8 22c5-1 7-12 12-12s7 8 15 6" strokeDasharray="3 3" />
        </svg>
        <p>{live ? t("viz.curve.emptyLive") : t("viz.curve.empty", { key: modKey })}</p>
      </div>
    );
  }
  return <>{charts.map((chart, i) => <Chart key={i} chart={chart} index={i} />)}</>;
}
