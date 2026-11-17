import { useEffect, useMemo, useRef, useState } from "react";
import { t } from "../strings";
import { reviewKey, reviewScore, useStore } from "../state/store";
import { InlineText } from "./InlineText";

/** End-of-track review: one question at a time, with the explanation after each answer. */
export function ReviewView() {
  const track = useStore((s) => s.reviewTrack);
  const questions = useStore((s) => s.reviewQuestions);
  const catalog = useStore((s) => s.catalog);
  const savedBest = useStore((s) => (track === null ? null : (s.progress[reviewKey(track)]?.code ?? null)));
  const best = reviewScore(savedBest);
  const { backToHub, openLesson, saveReviewScore } = useStore.getState();

  const [index, setIndex] = useState(0);
  const [choice, setChoice] = useState<number | null>(null);
  const [answers, setAnswers] = useState<(number | null)[]>([]);
  const [finished, setFinished] = useState(false);
  const heading = useRef<HTMLHeadingElement>(null);
  const next = useRef<HTMLButtonElement>(null);
  const summary = useRef<HTMLHeadingElement>(null);

  const titles = useMemo(
    () => new Map((catalog?.tracks ?? []).flatMap((tr) => tr.sections.map((s) => [s.id, s.title] as const))),
    [catalog],
  );
  const trackTitle = catalog?.tracks.find((tr) => tr.id === track)?.title ?? "";
  const question = questions[index];
  const answered = choice !== null;

  const score = answers.filter((answer, i) => answer === questions[i]?.answer).length;
  const toRevisit = useMemo(() => {
    const seen = new Set<string>();
    questions.forEach((q, i) => {
      if (answers[i] !== undefined && answers[i] !== q.answer) seen.add(q.lesson);
    });
    return [...seen].sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  }, [answers, questions]);

  // Focus: the question when it appears, the "next" button once it is answered, the result at the end.
  useEffect(() => {
    if (!finished) heading.current?.focus();
  }, [index, finished]);
  useEffect(() => {
    if (answered) next.current?.focus();
  }, [answered]);
  useEffect(() => {
    if (finished) summary.current?.focus();
  }, [finished]);

  if (track === null || (!question && !finished)) {
    return (
      <div className="hub-scroll">
        <main className="review">
          <button className="btn btn-ghost btn-sm" onClick={backToHub}>{t("review.back")}</button>
          <p className="muted">{t("review.loadFailed")}</p>
        </main>
      </div>
    );
  }

  const choose = (option: number) => {
    if (answered) return;
    setChoice(option);
  };
  const advance = () => {
    const nextAnswers = [...answers];
    nextAnswers[index] = choice;
    setAnswers(nextAnswers);
    setChoice(null);
    if (index + 1 >= questions.length) {
      const total = nextAnswers.filter((answer, i) => answer === questions[i].answer).length;
      saveReviewScore(total);
      setFinished(true);
    } else setIndex(index + 1);
  };
  const retry = () => {
    setIndex(0);
    setChoice(null);
    setAnswers([]);
    setFinished(false);
  };

  if (finished) {
    return (
      <div className="hub-scroll">
        <main className="review">
          <p className="review-eyebrow">{t("review.title", { id: track })}</p>
          <h1 ref={summary} tabIndex={-1}>{t("review.score", { score, total: questions.length })}</h1>
          {best && <p className="muted">{t("review.best", { score: best.score, total: best.total })}</p>}
          {toRevisit.length === 0 ? (
            <p>{t("review.allRight")}</p>
          ) : (
            <section aria-labelledby="revisit-title">
              <h2 id="revisit-title" className="review-sub">{t("review.revisit")}</h2>
              <p className="muted">{t("review.revisitNote")}</p>
              <ul className="review-lessons">
                {toRevisit.map((id) => (
                  <li key={id}>
                    <button className="section-row" onClick={() => void openLesson(id)}>
                      <span className="section-text">
                        <span className="section-title">
                          <span className="section-id">{id}</span>
                          {titles.get(id) ?? ""}
                        </span>
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          )}
          <div className="review-actions">
            <button className="btn btn-primary" onClick={retry}>{t("review.retry")}</button>
            <button className="btn" onClick={backToHub}>{t("review.back")}</button>
          </div>
        </main>
      </div>
    );
  }

  const last = index + 1 >= questions.length;
  return (
    <div className="hub-scroll">
      <main
        className="review"
        onKeyDown={(event) => {
          const n = Number(event.key);
          if (!event.ctrlKey && !event.metaKey && !event.altKey && n >= 1 && n <= question.options.length) choose(n - 1);
        }}
      >
        <button className="btn btn-ghost btn-sm" onClick={backToHub}>{t("review.back")}</button>
        <p className="review-eyebrow">
          {t("review.title", { id: track })}
          {trackTitle ? `: ${trackTitle}` : ""}
        </p>
        <div className="review-progress">
          <span>{t("review.progress", { n: index + 1, total: questions.length })}</span>
          <div className="meter" role="presentation"><span style={{ width: `${(index / questions.length) * 100}%` }} /></div>
        </div>
        <section className="card review-card" aria-labelledby="review-question">
          <h1 id="review-question" className="review-question" ref={heading} tabIndex={-1}>
            <InlineText text={question.question} />
          </h1>
          <div className="options" role="group" aria-labelledby="review-question">
            {question.options.map((option, i) => {
              const state = !answered ? "" : i === question.answer ? " is-correct" : i === choice ? " is-wrong" : "";
              return (
                <button
                  key={i}
                  className={`option${state}`}
                  aria-disabled={answered}
                  onClick={() => choose(i)}
                >
                  <span className="option-text"><InlineText text={option} /></span>
                  {answered && i === question.answer && <span className="option-tag">{t("review.rightAnswer")}</span>}
                  {answered && i === choice && i !== question.answer && <span className="option-tag">{t("review.yourAnswer")}</span>}
                </button>
              );
            })}
          </div>
          <div role="status" aria-live="polite">
            {answered && (
              <p className="card-note">
                <strong>{choice === question.answer ? t("review.correct") : t("review.wrong")}</strong>{" "}
                <InlineText text={question.explanation} />
              </p>
            )}
          </div>
          <div className="review-actions">
            <button ref={next} className="btn btn-primary" disabled={!answered} onClick={advance}>
              {last ? t("review.finish") : t("review.next")}
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}
