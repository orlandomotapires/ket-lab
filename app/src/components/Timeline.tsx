import { t } from "../strings";
import { selectCurrentStep, useStore } from "../state/store";
import { FirstIcon, LastIcon, NextIcon, PrevIcon } from "./icons";

export function Timeline() {
  const count = useStore((s) => s.result?.steps.length ?? 0);
  const current = useStore(selectCurrentStep);
  const followCursor = useStore((s) => s.followCursor);
  const setStep = useStore((s) => s.setStep);
  const setFollowCursor = useStore((s) => s.setFollowCursor);

  // Without instructions there is nothing to walk through: the controls would only show up disabled.
  if (count === 0) return null;

  return (
    <div className="timeline">
      <div className="timeline-buttons">
        <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setStep(0)} disabled={current === 0} aria-label={t("timeline.first")}>
          <FirstIcon />
        </button>
        <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setStep(current - 1)} disabled={current === 0} aria-label={t("timeline.prev")}>
          <PrevIcon />
        </button>
        <span className="timeline-count">{t("timeline.count", { n: current, total: count })}</span>
        <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setStep(current + 1)} disabled={current >= count} aria-label={t("timeline.next")}>
          <NextIcon />
        </button>
        <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setStep(count)} disabled={current >= count} aria-label={t("timeline.last")}>
          <LastIcon />
        </button>
      </div>
      <input
        className="timeline-slider"
        type="range"
        min={0}
        max={Math.max(count, 1)}
        value={current}
        disabled={count === 0}
        onChange={(event) => setStep(Number(event.target.value))}
        aria-label={t("timeline.slider")}
      />
      <label className="check" title={t("lab.followHint")}>
        <input type="checkbox" checked={followCursor} onChange={(event) => setFollowCursor(event.target.checked)} />
        {t("timeline.follow")}
      </label>
    </div>
  );
}
