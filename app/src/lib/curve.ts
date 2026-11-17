/** Scales, ticks and data cleaning for the generic `curve` chart. */

export interface CurveSeries {
  label: string;
  x: number[];
  y: number[];
  points?: boolean;
  /** A reference line: muted, dashed, no points. */
  dashed?: boolean;
}

export interface CurveMarker {
  x: number;
  y: number;
  label: string;
}

export interface CurveChart {
  title?: string;
  x_label: string;
  y_label: string;
  log_x?: boolean;
  log_y?: boolean;
  series: CurveSeries[];
  markers?: CurveMarker[];
}

const isNumber = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value);

/**
 * Turns what analysis.py returned into charts that are safe to draw: one chart or a list of them;
 * points that are not finite (or not positive on a log axis) are dropped; a chart without any
 * point is dropped. Returns an empty list when nothing can be drawn.
 */
export function cleanCurves(raw: unknown): CurveChart[] {
  const list = Array.isArray(raw) ? raw : raw && typeof raw === "object" ? [raw] : [];
  const charts: CurveChart[] = [];
  for (const item of list) {
    if (!item || typeof item !== "object") continue;
    const chart = item as Partial<CurveChart>;
    const logX = chart.log_x === true;
    const logY = chart.log_y === true;
    const usable = (value: unknown, log: boolean): value is number => isNumber(value) && (!log || value > 0);
    const series: CurveSeries[] = [];
    for (const entry of Array.isArray(chart.series) ? chart.series : []) {
      if (!entry || !Array.isArray(entry.x) || !Array.isArray(entry.y)) continue;
      const count = Math.min(entry.x.length, entry.y.length);
      const x: number[] = [];
      const y: number[] = [];
      for (let i = 0; i < count; i++) {
        if (usable(entry.x[i], logX) && usable(entry.y[i], logY)) {
          x.push(entry.x[i]);
          y.push(entry.y[i]);
        }
      }
      if (x.length > 0) series.push({ label: String(entry.label ?? ""), x, y, points: entry.points === true, dashed: entry.dashed === true });
    }
    if (series.length === 0) continue;
    const markers = (Array.isArray(chart.markers) ? chart.markers : [])
      .filter((m) => m && usable(m.x, logX) && usable(m.y, logY))
      .map((m) => ({ x: m.x, y: m.y, label: String(m.label ?? "") }));
    charts.push({
      title: chart.title ? String(chart.title) : undefined,
      x_label: String(chart.x_label ?? ""),
      y_label: String(chart.y_label ?? ""),
      log_x: logX,
      log_y: logY,
      series,
      markers,
    });
  }
  return charts;
}

/** About `count` round tick values (1, 2 or 5 times a power of ten) covering [low, high]. */
export function niceTicks(low: number, high: number, count = 5): number[] {
  if (!(high > low)) return [low];
  const rough = (high - low) / Math.max(count - 1, 1);
  const power = 10 ** Math.floor(Math.log10(rough));
  const ratio = rough / power;
  const step = (ratio <= 1.5 ? 1 : ratio <= 3 ? 2 : ratio <= 7 ? 5 : 10) * power;
  const first = Math.ceil(low / step - 1e-9) * step;
  const ticks: number[] = [];
  for (let value = first; value <= high + step * 1e-9; value += step) {
    ticks.push(Number(value.toPrecision(12)));
  }
  return ticks;
}

/** Tick values for a log axis: every power of ten, plus 2 and 5 when the range is short. */
export function logTicks(low: number, high: number): number[] {
  const first = Math.floor(Math.log10(low) + 1e-9);
  const last = Math.ceil(Math.log10(high) - 1e-9);
  const decades = last - first;
  const multipliers = decades >= 3 ? [1] : decades >= 2 ? [1, 3] : [1, 2, 5];
  const ticks: number[] = [];
  for (let power = first; power <= last; power++) {
    for (const m of multipliers) {
      const value = Number((m * 10 ** power).toPrecision(12));
      if (value >= low * (1 - 1e-9) && value <= high * (1 + 1e-9)) ticks.push(value);
    }
  }
  return ticks;
}

export interface Axis {
  /** Data to pixel position. */
  scale: (value: number) => number;
  ticks: number[];
  low: number;
  high: number;
}

/**
 * Builds an axis for the data range [min, max] drawn between the pixel positions `from` and `to`.
 * Linear axes extend to the surrounding round ticks; log axes to the surrounding powers of ten.
 */
export function makeAxis(min: number, max: number, log: boolean, from: number, to: number): Axis {
  let low = min;
  let high = max;
  let ticks: number[];
  if (log) {
    low = 10 ** Math.floor(Math.log10(min) + 1e-9);
    high = 10 ** Math.ceil(Math.log10(max) - 1e-9);
    if (high <= low) high = low * 10;
    ticks = logTicks(low, high);
    const a = Math.log10(low);
    const b = Math.log10(high);
    return { scale: (v) => from + ((Math.log10(v) - a) / (b - a)) * (to - from), ticks, low, high };
  }
  if (!(high > low)) {
    const pad = Math.abs(low) * 0.1 || 1;
    low -= pad;
    high += pad;
  }
  ticks = niceTicks(low, high, 5);
  if (ticks.length >= 2) {
    // Extend the range to round values, so both ends of the axis carry a label.
    const step = ticks[1] - ticks[0];
    const niceLow = Number((Math.floor(low / step + 1e-9) * step).toPrecision(12));
    const niceHigh = Number((Math.ceil(high / step - 1e-9) * step).toPrecision(12));
    ticks = niceTicks(niceLow, niceHigh, Math.round((niceHigh - niceLow) / step) + 1);
    low = niceLow;
    high = niceHigh;
  }
  return { scale: (v) => from + ((v - low) / (high - low)) * (to - from), ticks, low, high };
}

/** Compact number for tick labels and summaries, with a real minus sign. */
export function formatTick(value: number): string {
  if (value === 0) return "0";
  const abs = Math.abs(value);
  let text: string;
  if (abs >= 1e5 || abs < 1e-3) {
    const [mantissa, exponent] = value.toExponential(0).split("e");
    text = `${mantissa}e${exponent.replace("+", "")}`;
  } else if (abs >= 100) text = value.toFixed(0);
  else if (abs >= 10) text = String(Number(value.toFixed(1)));
  else text = String(Number(value.toPrecision(3)));
  return text.replace("-", "−");
}

/** First, last, minimum and maximum of a series, for the text summary. */
export function seriesStats(series: CurveSeries) {
  return {
    count: series.y.length,
    first: series.y[0],
    last: series.y[series.y.length - 1],
    min: Math.min(...series.y),
    max: Math.max(...series.y),
  };
}
