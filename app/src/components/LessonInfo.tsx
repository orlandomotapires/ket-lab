import { useEffect, useId, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { t } from "../strings";
import { useStore } from "../state/store";
import { InfoIcon } from "./icons";
import { InlineText } from "./InlineText";

/** One key term: opens its entry in the glossary; hovering it shows the definition. */
function TermLink({ term, onOpen }: { term: string; onOpen: () => void }) {
  const definition = useStore((s) => s.glossary.find((entry) => entry.term === term)?.definition);
  return (
    <button
      type="button"
      className="lesson-info-term"
      title={definition}
      aria-label={t("glossary.openTerm", { term })}
      onClick={() => {
        onOpen();
        useStore.getState().openGlossary(term);
      }}
    >
      {term}
    </button>
  );
}

/** Text of the popover: the time the lesson takes and what it teaches. With key terms, a short list
 *  of glossary links; otherwise the goals as sentences. */
function LessonInfoBody({ goals, terms, minutes, onOpen }: {
  goals: string[];
  terms?: string[];
  minutes?: number | null;
  onOpen: () => void;
}) {
  return (
    <>
      {minutes ? <p className="lesson-info-time">{t("theory.minutesLong", { minutes })}</p> : null}
      <p className="lesson-info-title">{t("theory.learnTitle")}</p>
      {terms?.length ? (
        <ul className="lesson-info-terms">
          {terms.map((term) => (
            <li key={term}><TermLink term={term} onOpen={onOpen} /></li>
          ))}
        </ul>
      ) : (
        <ul>
          {goals.map((goal) => (
            <li key={goal}><InlineText text={goal} /></li>
          ))}
        </ul>
      )}
    </>
  );
}

/** "i" next to a lesson name: hovering it (or focusing it, when `focusable`) shows the lesson's
 *  key terms, each a link to the glossary (or its goals, when it has no key terms). The popover is
 *  drawn in document.body, so the track cards and the top bar, which clip their overflow, do not
 *  cut it. The pointer can move onto it, and Escape closes it. With `focusable`, clicking the "i"
 *  (or Enter on it) moves focus to the first term.
 *
 *  Inside a button (a hub row) the "i" cannot be a button too: `focusable` is false there and the
 *  row points to `descriptionId` (aria-describedby) so screen readers still hear the terms. */
export function LessonInfo({ goals, terms, minutes, focusable = false, descriptionId }: {
  goals: string[];
  terms?: string[];
  minutes?: number | null;
  focusable?: boolean;
  descriptionId?: string;
}) {
  const [open, setOpen] = useState(false);
  const [position, setPosition] = useState<{ top: number; left: number } | null>(null);
  const triggerRef = useRef<HTMLSpanElement>(null);
  const popRef = useRef<HTMLDivElement>(null);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const popId = useId();

  const show = () => {
    clearTimeout(closeTimer.current);
    setOpen(true);
  };
  // A short delay, so the pointer can travel from the "i" to the popover.
  const hide = () => {
    clearTimeout(closeTimer.current);
    closeTimer.current = setTimeout(() => setOpen(false), 120);
  };
  useEffect(() => () => clearTimeout(closeTimer.current), []);

  // Below the "i", kept inside the window.
  useLayoutEffect(() => {
    if (!open) return;
    const trigger = triggerRef.current?.getBoundingClientRect();
    const pop = popRef.current?.getBoundingClientRect();
    if (!trigger || !pop) return;
    const margin = 8;
    const left = Math.min(Math.max(margin, trigger.left + trigger.width / 2 - pop.width / 2), window.innerWidth - pop.width - margin);
    const below = trigger.bottom + 6;
    const top = below + pop.height > window.innerHeight - margin ? Math.max(margin, trigger.top - pop.height - 6) : below;
    setPosition({ top, left });
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      // Focus inside the popover goes back to the "i" first; then the popover closes.
      if (popRef.current?.contains(document.activeElement)) triggerRef.current?.querySelector("button")?.focus();
      clearTimeout(closeTimer.current);
      setOpen(false);
    };
    const onScroll = () => setOpen(false);
    document.addEventListener("keydown", onKey);
    window.addEventListener("scroll", onScroll, true);
    return () => {
      document.removeEventListener("keydown", onKey);
      window.removeEventListener("scroll", onScroll, true);
    };
  }, [open]);

  const handlers = { onMouseEnter: show, onMouseLeave: hide };
  const close = () => {
    clearTimeout(closeTimer.current);
    setOpen(false);
  };
  const focusFirstTerm = () => {
    show();
    requestAnimationFrame(() => popRef.current?.querySelector<HTMLButtonElement>(".lesson-info-term")?.focus());
  };
  return (
    <>
      <span ref={triggerRef} className="lesson-info" {...handlers}>
        {focusable ? (
          <button
            type="button"
            className="lesson-info-button"
            aria-label={t("theory.learnTitle")}
            aria-describedby={open ? popId : undefined}
            onFocus={show}
            onBlur={hide}
            onClick={terms?.length ? focusFirstTerm : undefined}
          >
            <InfoIcon />
          </button>
        ) : (
          <span className="lesson-info-icon" aria-hidden="true"><InfoIcon /></span>
        )}
      </span>
      {/* Text for aria-describedby of the row that holds a non-focusable "i". */}
      {descriptionId && (
        <span id={descriptionId} hidden>
          {t("theory.learnTitle")}: {terms?.length ? terms.join(", ") : goals.join("; ")}
        </span>
      )}
      {open &&
        createPortal(
          <div
            ref={popRef}
            id={popId}
            role={terms?.length ? "group" : "tooltip"}
            aria-label={terms?.length ? t("theory.learnTitle") : undefined}
            className="lesson-info-pop"
            style={position ? { top: position.top, left: position.left } : { visibility: "hidden", top: 0, left: 0 }}
            {...handlers}
            // Focus moving between the terms keeps it open.
            onFocus={show}
            onBlur={hide}
            // Events from a portal still bubble through React to the hub row (a button that opens
            // the lesson): a click here only opens the glossary.
            onClick={(event) => event.stopPropagation()}
          >
            <LessonInfoBody goals={goals} terms={terms} minutes={minutes} onOpen={close} />
          </div>,
          document.body,
        )}
    </>
  );
}
