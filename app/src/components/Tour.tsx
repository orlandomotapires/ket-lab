import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { t, type MessageKey } from "../strings";
import { useStore } from "../state/store";

/** Guide for the first lesson: four steps, shown once (reopens via the "?" button). */
const STEPS: { target: string; title: MessageKey; body: MessageKey }[] = [
  { target: ".editor-panel", title: "tour.code.title", body: "tour.code.body" },
  { target: ".circuit-panel", title: "tour.timeline.title", body: "tour.timeline.body" },
  { target: ".mission", title: "tour.mission.title", body: "tour.mission.body" },
  { target: ".oracle-actions", title: "tour.check.title", body: "tour.check.body" },
];
const SEEN_KEY = "qlp.tour.v1";
const OPEN_EVENT = "qlp:tour";

export function openTour(): void {
  window.dispatchEvent(new Event(OPEN_EVENT));
}

function seen(): boolean {
  try {
    return localStorage.getItem(SEEN_KEY) === "1";
  } catch {
    return true;
  }
}

function markSeen(): void {
  try {
    localStorage.setItem(SEEN_KEY, "1");
  } catch {
    // no storage: the guide comes back on the next visit
  }
}

/** Steps whose target is visible (on narrow screens, some panels live in other tabs). */
function visibleSteps() {
  return STEPS.filter((step) => {
    const element = document.querySelector<HTMLElement>(step.target);
    return element !== null && element.offsetParent !== null;
  });
}

export function Tour() {
  const lesson = useStore((s) => s.lesson);
  const [open, setOpen] = useState(false);
  const [index, setIndex] = useState(0);
  const [steps, setSteps] = useState(STEPS);
  const [box, setBox] = useState<DOMRect | null>(null);
  const card = useRef<HTMLDivElement>(null);

  const start = useCallback(() => {
    const available = visibleSteps();
    if (!available.length) return;
    setSteps(available);
    setIndex(0);
    setOpen(true);
  }, []);

  // First lesson opened: the guide shows up by itself, after the lesson mounts.
  useEffect(() => {
    if (!lesson || seen()) return;
    const timer = window.setTimeout(start, 600);
    return () => window.clearTimeout(timer);
  }, [lesson, start]);

  useEffect(() => {
    window.addEventListener(OPEN_EVENT, start);
    return () => window.removeEventListener(OPEN_EVENT, start);
  }, [start]);

  const step = steps[index];
  useLayoutEffect(() => {
    if (!open || !step) return;
    const element = document.querySelector<HTMLElement>(step.target);
    const update = () => setBox(element ? element.getBoundingClientRect() : null);
    update();
    element?.classList.add("tour-target");
    window.addEventListener("resize", update);
    card.current?.focus();
    return () => {
      element?.classList.remove("tour-target");
      window.removeEventListener("resize", update);
    };
  }, [open, step]);

  if (!open || !step) return null;

  const close = () => {
    setOpen(false);
    markSeen();
  };
  const last = index === steps.length - 1;
  const next = () => (last ? close() : setIndex(index + 1));

  // The card sits next to the target, inside the screen.
  const width = 320;
  let left = box ? box.right + 12 : 24;
  if (box && left + width > window.innerWidth - 12) left = Math.max(12, box.left - width - 12);
  if (box && left < 12) left = Math.max(12, Math.min(box.left, window.innerWidth - width - 12));
  let top = box ? box.top : 80;
  if (box && box.left - width - 12 < 12 && box.right + width + 12 > window.innerWidth) top = Math.max(12, box.top - 170);
  top = Math.min(Math.max(12, top), window.innerHeight - 200);

  return (
    <div className="tour-layer" onKeyDown={(event) => {
      if (event.key === "Escape") close();
      if (event.key === "ArrowRight") next();
      if (event.key === "ArrowLeft" && index > 0) setIndex(index - 1);
    }}>
      <div
        ref={card}
        className="tour-card"
        role="dialog"
        aria-modal="false"
        aria-labelledby="tour-title"
        tabIndex={-1}
        style={{ left, top, width }}
      >
        <p className="tour-count muted small">{t("tour.count", { n: index + 1, total: steps.length })}</p>
        <h2 id="tour-title">{t(step.title)}</h2>
        <p>{t(step.body)}</p>
        <div className="tour-actions">
          <button className="btn btn-ghost btn-sm" onClick={close}>{t("tour.skip")}</button>
          <span className="grow" />
          {index > 0 && (
            <button className="btn btn-sm" onClick={() => setIndex(index - 1)}>{t("tour.back")}</button>
          )}
          <button className="btn btn-primary btn-sm" onClick={next}>{last ? t("tour.done") : t("tour.next")}</button>
        </div>
      </div>
    </div>
  );
}
