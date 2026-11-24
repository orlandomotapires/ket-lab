import type { ReactNode } from "react";
import { useEffect, useId, useLayoutEffect, useRef, useState } from "react";
import { openExternal } from "../engine/client";
import type { Prediction, Reference } from "../engine/types";
import { t } from "../strings";
import { selectSolutionOffer, useStore } from "../state/store";
import { CheckIcon, ChevronRightIcon, TargetIcon } from "./icons";
import { InlineText } from "./InlineText";
import { Markdown } from "./Markdown";

/** "Predict before you run". `inline`: inside the mission bar, which already shows the title.
 *  With `onChoose`, the answer is kept by the caller (`chosen`). */
export function PredictionCard({ prediction, inline = false, id, chosen, onChoose }: {
  prediction: Prediction; inline?: boolean; id?: string; chosen?: number | null; onChoose?: (index: number) => void;
}) {
  const [own, setOwn] = useState<number | null>(null);
  const choice = onChoose ? (chosen ?? null) : own;
  const setChoice = onChoose ?? setOwn;
  const answered = choice !== null;
  return (
    <section className={inline ? "prediction-inline" : "card"} id={id} aria-label={inline ? t("theory.predict") : undefined}>
      {!inline && <h3 className="card-title">{t("theory.predict")}</h3>}
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

/** "Further reading (3)" at the end of the lesson: one line until opened, so it does not
 *  compete with the theory. The mission card links here once the lesson is solved. */
const READING_ID = "further-reading";

function References({ items, open, onToggle }: { items: Reference[]; open: boolean; onToggle: () => void }) {
  return (
    <section className="references" id={READING_ID} aria-labelledby="references-title">
      <h2 id="references-title" className="references-title">
        <button className="objectives-toggle" aria-expanded={open} aria-controls="references-list" onClick={onToggle}>
          <span className="disclosure-caret" aria-hidden="true" />
          {t("theory.referencesCount", { n: items.length })}
        </button>
      </h2>
      {open && (
        <div id="references-list">
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
        </div>
      )}
    </section>
  );
}

/** The opened hints and the button for the next one. "Hide hints" folds the list away (the hints
 *  stay counted as seen); "Hints (2)" brings it back, and so does asking for the next hint. */
function Hints({ hints, shown, onMore }: { hints: string[]; shown: number; onMore: () => void }) {
  const [hidden, setHidden] = useState(false);
  const listId = useId();
  return (
    <>
      {shown > 0 && !hidden && (
        <ol className="hints" id={listId}>
          {hints.slice(0, shown).map((hint, index) => (
            <li key={index}><InlineText text={hint} /></li>
          ))}
        </ol>
      )}
      {(shown < hints.length || shown > 0) && (
        <div className="hint-actions">
          {shown < hints.length && (
            <button
              className="btn btn-sm"
              onClick={() => {
                setHidden(false);
                onMore();
              }}
            >
              {t("theory.hint", { n: shown + 1, total: hints.length })}
            </button>
          )}
          {shown > 0 && (
            <button className="link small hints-toggle" aria-expanded={!hidden} aria-controls={listId} onClick={() => setHidden(!hidden)}>
              <span className="disclosure-caret" aria-hidden="true" />
              {hidden ? t("theory.hintsShow", { n: shown }) : t("theory.hintsHide")}
            </button>
          )}
        </div>
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
export function MissionText({ text }: { text: string }) {
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

/** "Check yourself": the lesson's objectives, read back once the theory is done. */
function Recap({ items }: { items: string[] }) {
  return (
    <section className="recap" aria-labelledby="recap-title">
      <h2 id="recap-title" className="recap-title">{t("theory.recap")}</h2>
      <p className="recap-intro">{t("theory.recapIntro")}</p>
      <ul>
        {items.map((objective) => (
          <li key={objective}>
            <span className="recap-mark" aria-hidden="true"><CheckIcon size={11} /></span>
            <span><InlineText text={objective} /></span>
          </li>
        ))}
      </ul>
    </section>
  );
}

/** Height of the pinned mission card: what the theory scrolls to sits just below it. */
function pinnedHeight(scroll: HTMLElement): number {
  return scroll.querySelector<HTMLElement>(".mission-pin")?.getBoundingClientRect().height ?? 0;
}

/** Scrolls the theory so that `target` sits right under the pinned card. */
function scrollUnderPin(scroll: HTMLElement, target: HTMLElement): void {
  const offset = target.getBoundingClientRect().top - scroll.getBoundingClientRect().top;
  scroll.scrollTo({ top: scroll.scrollTop + offset - pinnedHeight(scroll) - 8, behavior: "auto" });
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
    const key = `ket-lab.theory.scroll.${lessonId}`;
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
  // Further reading starts folded in each lesson; "Go deeper" on the solved mission opens it.
  const [reading, setReading] = useState<{ lessonId: string | null; open: boolean }>({ lessonId, open: false });
  const readingOpen = reading.lessonId === lessonId && reading.open;
  const setReadingOpen = (open: boolean) => setReading({ lessonId, open });
  const goDeeper = () => {
    setReadingOpen(true);
    requestAnimationFrame(() => {
      const scroll = scrollRef.current;
      const target = document.getElementById(READING_ID);
      if (!scroll || !target) return;
      scrollUnderPin(scroll, target);
      target.querySelector<HTMLButtonElement>("button")?.focus({ preventScroll: true });
    });
  };
  const completed = useStore((s) => Boolean(s.lesson && ((!s.challengeMode && s.validation?.passed) || s.progress[s.lesson.id]?.completed)));
  const challengeDone = useStore((s) => Boolean(s.lesson && ((s.challengeMode && s.validation?.passed) || s.progress[`${s.lesson.id}:challenge`]?.completed)));
  if (!lesson) return null;
  const inChallenge = challengeMode && Boolean(lesson.challenge);

  // One scroll for the whole panel. The mission card sticks to its top, so the goal stays in view
  // while the theory scrolls. The lesson's name, time and goals are in the top bar.
  return (
    <aside className="panel theory" aria-label={t("theory.aria")}>
      <div className="panel-scroll theory-scroll" tabIndex={0} ref={scrollRef}>
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
                <Hints key={`${lesson.id}:c`} hints={lesson.challenge.hints} shown={challengeHintsShown} onMore={showNextHint} />
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
                <Hints key={lesson.id} hints={lesson.hints} shown={hintsShown} onMore={showNextHint} />
                <SolutionOffer />
                {completed && lesson.challenge && (
                  <button className="btn btn-sm btn-challenge" onClick={startChallenge}>
                    {challengeDone ? t("theory.challengeAgain") : t("theory.tryChallenge")}
                  </button>
                )}
                {completed && lesson.references?.length ? (
                  <button className="link small go-deeper" onClick={goDeeper}>
                    {t("theory.goDeeper", { n: lesson.references.length })} <ChevronRightIcon />
                  </button>
                ) : null}
              </MissionTools>
            </section>
          )}
        </div>
        {solution !== null && <SolutionCard key={`${lesson.id}:${challengeMode}`} code={solution} />}
        <Markdown>{lesson.theory}</Markdown>
        {lesson.prediction && <PredictionCard key={lesson.id} prediction={lesson.prediction} />}
        {!inChallenge && lesson.objectives.length > 0 && <Recap items={lesson.objectives} />}
        {lesson.references?.length ? (
          <References items={lesson.references} open={readingOpen} onToggle={() => setReadingOpen(!readingOpen)} />
        ) : null}
      </div>
    </aside>
  );
}

/** Hint list and buttons of the mission card. Only the list of opened hints scrolls, so the
 *  mission text and the hint button never leave the card. */
function MissionTools({ children }: { children: ReactNode }) {
  return <div className="mission-tools">{children}</div>;
}
