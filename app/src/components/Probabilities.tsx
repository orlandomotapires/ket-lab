import type { Complex, ShotsResult } from "../engine/types";
import { basisLabel, formatAmplitude, formatPercent, formatPhase, phaseColor, phaseOf, probability } from "../lib/quantum";
import { t, useLocale } from "../i18n";
import { useTheme } from "../theme/theme";

const MAX_ROWS = 32;
const EPSILON = 1e-9;

function PhaseDial({ phase, color }: { phase: number; color: string }) {
  // Ponteiro como num relógio matemático: 0 aponta para a direita, sentido anti-horário.
  return (
    <svg className="dial" width="18" height="18" viewBox="-9 -9 18 18" aria-hidden="true">
      <circle r="7.5" />
      <line x1="0" y1="0" x2={7.5 * Math.cos(phase)} y2={-7.5 * Math.sin(phase)} style={{ stroke: color }} />
    </svg>
  );
}

export function Probabilities({ amplitudes, numQubits }: { amplitudes: Complex[]; numQubits: number }) {
  useLocale();
  const dark = useTheme() === "dark";
  const all = amplitudes.map((amplitude, index) => ({ amplitude, index, p: probability(amplitude) }));
  // Com poucos estados mostra todos; com muitos, só os que têm amplitude.
  const candidates = amplitudes.length <= 8 ? all : all.filter((row) => row.p > EPSILON);
  const rows = candidates.slice(0, MAX_ROWS);

  return (
    <div className="probs">
      <table>
        <thead>
          <tr>
            <th scope="col">{t("probs.state")}</th>
            <th scope="col">{t("probs.probability")}</th>
            <th scope="col" className="num">{t("probs.amplitude")}</th>
            <th scope="col">{t("probs.phase")}</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(({ amplitude, index, p }) => {
            const hasPhase = p > EPSILON;
            const phase = phaseOf(amplitude);
            const color = phaseColor(phase, dark);
            return (
              <tr key={index} className={hasPhase ? "" : "is-zero"}>
                <th scope="row" className="mono">{basisLabel(index, numQubits)}</th>
                <td className="bar-col">
                  <div className="bar-cell">
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: `${p * 100}%`, background: hasPhase ? color : undefined }} />
                    </div>
                    <span className="bar-value">{formatPercent(p)}</span>
                  </div>
                </td>
                <td className="num mono">{formatAmplitude(amplitude)}</td>
                <td>
                  {hasPhase ? (
                    <span className="phase">
                      <PhaseDial phase={phase} color={color} />
                      <span className="mono">{formatPhase(phase)}</span>
                    </span>
                  ) : (
                    <span className="muted">—</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {candidates.length > rows.length && (
        <p className="footnote">{t("probs.more", { count: candidates.length - rows.length })}</p>
      )}
      {numQubits > 1 && (
        <p className="footnote">{t("probs.order", { last: numQubits - 1 })}</p>
      )}
    </div>
  );
}

export function ShotsHistogram({ shots }: { shots: ShotsResult }) {
  const entries = Object.entries(shots.counts);
  return (
    <div className="probs">
      <h3 className="section-label">
        {t("shots.title", { shots: shots.shots })}
        {shots.measured === "clbits" ? t("shots.clbits") : ""}
      </h3>
      <table>
        <tbody>
          {entries.map(([bits, count]) => (
            <tr key={bits}>
              <th scope="row" className="mono">{bits}</th>
              <td className="bar-col">
                <div className="bar-cell">
                  <div className="bar-track">
                    <div className="bar-fill is-neutral" style={{ width: `${(count / shots.shots) * 100}%` }} />
                  </div>
                  <span className="bar-value">{count}</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="footnote">{t("shots.note")}</p>
    </div>
  );
}
