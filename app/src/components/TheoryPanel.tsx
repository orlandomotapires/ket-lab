import type { ReactNode } from "react";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { readFlag, useStoredFlag, writeFlag } from "../lib/storedFlag";
import { openExternal } from "../engine/client";
import type { Prediction, Reference } from "../engine/types";
import { t } from "../strings";
import { selectSolutionOffer, useStore } from "../state/store";
import { CheckIcon, TargetIcon } from "./icons";
import { InlineText } from "./InlineText";
import { Markdown } from "./Markdown";

function PredictionCard({ prediction }: { prediction: Prediction }) {
  const [choice, setChoice] = useState<number | null>(null);
  const answered = choice !== null;
  return (
    <section className="card">
      <h3 className="card-title">{t("theory.predict")}</h3>
      <p><InlineText text={prediction.question} /></p>
      <div className="options" role="radiogroup" aria-label={t("theory.options")}>
        {prediction.options.map((option, index) => {
          const state = !answered ? "" : index === prediction.answer ? " is-correct" : index === choice ? " is-wrong" : "";
          return (
            <button
              key={index}
              role="radio"
              aria-checked={choice === index}
              className={`option${state}`}
              disabled={answered}
              onClick={() => setChoice(index)}
            >
              <InlineText text={option} />
            </button>
          );
        })}
      </div>
      {answered && (
        <p className="card-note">
          <strong>{choice === prediction.answer ? t("theory.correct") : t("theory.wrong")}</strong> <InlineText text={prediction.explanation} />
        </p>
      )}
    </section>
  );
}

function References({ items }: { items: Reference[] }) {
  return (
    <section className="references" aria-labelledby="references-title">
      <h2 id="references-title" className="references-title">{t("theory.references")}</h2>
      <p className="references-intro">{t("theory.referencesIntro")}</p>
      <ul>
        {items.map((ref) => (
          <li key={ref.url}>
            <span className={`pill ref-kind is-${ref.kind}`}>{t(`ref.${ref.kind}`)}</span>
            <a
              href={ref.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(event) => {
                event.preventDefault();
                openExternal(ref.url);
              }}
            >
              {ref.title}
            </a>
            <span className="ref-meta">
              {ref.authors}
              {ref.year ? `, ${ref.year}` : ""}
            </span>
            <span className="ref-location">{ref.location}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function Hints({ hints, shown, onMore }: { hints: string[]; shown: number; onMore: () => void }) {
  return (
    <>
      {shown > 0 && (
        <ol className="hints">
          {hints.slice(0, shown).map((hint, index) => (
            <li key={index}><InlineText text={hint} /></li>
          ))}
        </ol>
      )}
      {shown < hints.length && (
        <button className="btn btn-sm" onClick={onMore}>
          {t("theory.hint", { n: shown + 1, total: hints.length })}
        </button>
      )}
    </>
  );
}

/** "Show a solution": only after all the hints and a few attempts, and with confirmation. */
function SolutionOffer() {
  const offered = useStore((s) => selectSolutionOffer(s).offered);
  const needsConfirmation = useStore((s) => selectSolutionOffer(s).needsConfirmation);
  const shown = useStore((s) => s.solution !== null);
  const challengeMode = useStore((s) => s.challengeMode);
  const [confirming, setConfirming] = useState(false);
  const { showSolution } = useStore.getState();
  if (!offered || shown) return null;
  if (confirming) {
    return (
      <div className="solution-confirm" role="group" aria-label={t("solution.show")}>
        <p>{t(challengeMode ? "solution.confirmChallenge" : "solution.confirm")}</p>
        <div className="solution-confirm-actions">
          <button className="btn btn-sm" onClick={() => setConfirming(false)}>{t("solution.keepTrying")}</button>
          <button
            className="btn btn-sm"
            onClick={() => {
              setConfirming(false);
              void showSolution();
            }}
          >
            {t("solution.confirmShow")}
          </button>
        </div>
      </div>
    );
  }
  return (
    <button className="link small solution-offer" onClick={() => (needsConfirmation ? setConfirming(true) : void showSolution())}>
      {t("solution.show")}
    </button>
  );
}

/** The commented solution: the comments explain the idea of each step. */
function SolutionCard({ code }: { code: string }) {
  const { setCode, hideSolution } = useStore.getState();
  return (
    <section className="card solution-card" aria-labelledby="solution-title">
      <h3 className="card-title" id="solution-title">{t("solution.title")}</h3>
      <p className="card-note">{t("solution.note")}</p>
      <pre className="solution-code" tabIndex={0}>
        <code>
          {code.trimEnd().split("\n").map((line, index) => (
            <span key={index} className={line.trimStart().startsWith("#") ? "is-comment" : undefined}>
              {line}
              {"\n"}
            </span>
          ))}
        </code>
      </pre>
      <div className="solution-actions">
        <button className="btn btn-sm" onClick={() => setCode(code)}>{t("solution.copy")}</button>
        <button className="btn btn-ghost btn-sm" onClick={hideSolution}>{t("solution.hide")}</button>
      </div>
    </section>
  );
}

/** The mission text: three lines at most, with "More" when it is longer. */
function MissionText({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false);
  const [clamped, setClamped] = useState(false);
  const ref = useRef<HTMLParagraphElement>(null);
  const [lastText, setLastText] = useState(text);
  if (lastText !== text) {
    setLastText(text);
    setExpanded(false);
  }
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const measure = () => {
      if (!expanded) setClamped(el.scrollHeight > el.clientHeight + 1);
    };
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, [text, expanded]);
  return (
    <>
      <p ref={ref} className={`mission-text${expanded ? "" : " is-clamped"}`}>
        <InlineText text={text} />
      </p>
      {(clamped || expanded) && (
        <button className="link small mission-more" aria-expanded={expanded} onClick={() => setExpanded(!expanded)}>
          {t(expanded ? "theory.less" : "theory.more")}
        </button>
      )}
    </>
  );
}

/** "What you will learn (4)": open the first time a lesson is visited, then as the learner left it. */
function Objectives({ lessonId, items }: { lessonId: string; items: string[] }) {
  const key = `qlp.objectives.${lessonId}`;
  const [open, setOpen] = useStoredFlag(key, true);
  useEffect(() => {
    // From the second visit on, it starts closed (unless the learner opened it).
    if (readFlag(key) === null) writeFlag(key, false);
  }, [key]);
  return (
    <div className="objectives">
      <button className="objectives-toggle" aria-expanded={open} aria-controls="objectives-list" onClick={() => setOpen(!open)}>
        <span className="disclosure-caret" aria-hidden="true" />
        {t("theory.learn", { n: items.length })}
      </button>
      {open && (
        <ul id="objectives-list">
          {items.map((objective) => (
            <li key={objective}><InlineText text={objective} /></li>
          ))}
        </ul>
      )}
    </div>
  );
}

/** The `##` headings of a theory text, as plain text (formulas and emphasis marks removed). */
export function theoryHeadings(theory: string): string[] {
  const headings: string[] = [];
  let fenced = false;
  for (const line of theory.split("\n")) {
    if (/^\s*(```|~~~)/.test(line)) fenced = !fenced;
    const match = !fenced && /^##\s+(.+?)\s*#*\s*$/.exec(line);
    if (match) headings.push(match[1].replace(/\$([^$]*)\$/g, "$1").replace(/[`*_]/g, "").trim());
  }
  return headings;
}

/** "Contents (5)": the theory's sections; choosing one scrolls the theory to it. */
function Outline({ headings, scrollRef }: { headings: string[]; scrollRef: React.RefObject<HTMLDivElement | null> }) {
  const [open, setOpen] = useState(false);
  const go = (index: number) => {
    const scroll = scrollRef.current;
    const target = scroll?.querySelectorAll<HTMLElement>(".prose > h2")[index];
    if (!scroll || !target) return;
    // The mission card sticks to the top of the panel: leave room for it.
    const pinned = scroll.querySelector<HTMLElement>(".mission-pin")?.getBoundingClientRect().height ?? 0;
    const offset = target.getBoundingClientRect().top - scroll.getBoundingClientRect().top;
    scroll.scrollTo({ top: scroll.scrollTop + offset - pinned - 8, behavior: "auto" });
    setOpen(false);
    target.setAttribute("tabindex", "-1");
    target.focus({ preventScroll: true });
  };
  return (
    <div className="objectives outline">
      <button className="objectives-toggle" aria-expanded={open} aria-controls="outline-list" onClick={() => setOpen(!open)}>
        <span className="disclosure-caret" aria-hidden="true" />
        {t("theory.contents", { n: headings.length })}
      </button>
      {open && (
        <ul id="outline-list" className="outline-list">
          {headings.map((heading, index) => (
            <li key={`${index}-${heading}`}>
              <button className="link outline-item" onClick={() => go(index)}>{heading}</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function readScroll(key: string): number {
  try {
    const value = Number(localStorage.getItem(key));
    return Number.isFinite(value) && value > 0 ? value : 0;
  } catch {
    return 0;
  }
}

function writeScroll(key: string, value: number): void {
  try {
    localStorage.setItem(key, String(Math.round(value)));
  } catch {
    // Not remembered.
  }
}

export function TheoryPanel() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const lessonId = useStore((s) => s.lesson?.id ?? null);
  // Reading position, per lesson: restored once the theory has rendered, saved while scrolling.
  useEffect(() => {
    const el = scrollRef.current;
    if (!el || !lessonId) return;
    const key = `qlp.theory.scroll.${lessonId}`;
    const saved = readScroll(key);
    let frame = requestAnimationFrame(() => {
      frame = requestAnimationFrame(() => {
        el.scrollTop = saved;
      });
    });
    let timer: ReturnType<typeof setTimeout> | undefined;
    const onScroll = () => {
      clearTimeout(timer);
      timer = setTimeout(() => writeScroll(key, el.scrollTop), 200);
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      cancelAnimationFrame(frame);
      clearTimeout(timer);
      el.removeEventListener("scroll", onScroll);
    };
  }, [lessonId]);
  const lesson = useStore((s) => s.lesson);
  const hintsShown = useStore((s) => s.hintsShown);
  const showNextHint = useStore((s) => s.showNextHint);
  const challengeMode = useStore((s) => s.challengeMode);
  const challengeHintsShown = useStore((s) => s.challengeHintsShown);
  const solution = useStore((s) => s.solution);
  const { startChallenge, leaveChallenge } = useStore.getState();
  const completed = useStore((s) => Boolean(s.lesson && ((!s.challengeMode && s.validation?.passed) || s.progress[s.lesson.id]?.completed)));
  const challengeDone = useStore((s) => Boolean(s.lesson && ((s.challengeMode && s.validation?.passed) || s.progress[`${s.lesson.id}:challenge`]?.completed)));
  if (!lesson) return null;
  const headings = theoryHeadings(lesson.theory);
  const inChallenge = challengeMode && Boolean(lesson.challenge);

  // One scroll for the whole panel. The mission card sticks to its top, so the goal stays in
  // view while the theory scrolls; the title and the objectives scroll away.
  return (
    <aside className="panel theory" aria-label={t("theory.aria")}>
      <div className="panel-scroll theory-scroll" tabIndex={0} ref={scrollRef}>
        <header className="lesson-head">
          <p className="lesson-eyebrow">
            {t("theory.lesson", { id: lesson.id })}
            {lesson.estimated_minutes ? `, ${t("theory.minutes", { minutes: lesson.estimated_minutes })}` : ""}
          </p>
          <h1 className="lesson-title">{lesson.title}</h1>
        </header>
        <div className="mission-pin">
          {inChallenge && lesson.challenge ? (
            <section className={`mission is-challenge${challengeDone ? " is-done" : ""}`} aria-labelledby="mission-title">
              <h2 className="mission-title" id="mission-title">
                {challengeDone ? <CheckIcon size={14} /> : <TargetIcon />}
                {challengeDone ? t("theory.challengeDone") : t("theory.challenge")}
                <span className="grow" />
                <button className="link small" onClick={leaveChallenge}>{t("theory.backToMission")}</button>
              </h2>
              <MissionText key={`${lesson.id}:c`} text={lesson.challenge.mission} />
              <MissionTools>
                <Hints hints={lesson.challenge.hints} shown={challengeHintsShown} onMore={showNextHint} />
                <SolutionOffer />
              </MissionTools>
            </section>
          ) : (
            <section className={`mission${completed ? " is-done" : ""}`} aria-labelledby="mission-title">
              <h2 className="mission-title" id="mission-title">
                {completed ? <CheckIcon size={14} /> : <TargetIcon />}
                {completed ? t("theory.missionDone") : t("theory.mission")}
              </h2>
              <MissionText key={lesson.id} text={lesson.mission} />
              <MissionTools>
                <Hints hints={lesson.hints} shown={hintsShown} onMore={showNextHint} />
                <SolutionOffer />
                {completed && lesson.challenge && (
                  <button className="btn btn-sm btn-challenge" onClick={startChallenge}>
                    {challengeDone ? t("theory.challengeAgain") : t("theory.tryChallenge")}
                  </button>
                )}
              </MissionTools>
            </section>
          )}
        </div>
        {!inChallenge && lesson.objectives.length > 0 && <Objectives key={`objectives:${lesson.id}`} lessonId={lesson.id} items={lesson.objectives} />}
        {!inChallenge && headings.length >= 3 && <Outline key={`outline:${lesson.id}`} headings={headings} scrollRef={scrollRef} />}
        {solution !== null && <SolutionCard key={`${lesson.id}:${challengeMode}`} code={solution} />}
        <Markdown>{lesson.theory}</Markdown>
        {lesson.prediction && <PredictionCard key={lesson.id} prediction={lesson.prediction} />}
        {lesson.references?.length ? <References items={lesson.references} /> : null}
      </div>
    </aside>
  );
}

/** Hint list and buttons of the mission card. Only the list of opened hints scrolls, so the
 *  mission text and the hint button never leave the card. */
function MissionTools({ children }: { children: ReactNode }) {
  return <div className="mission-tools">{children}</div>;
}
