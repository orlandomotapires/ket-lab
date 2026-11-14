import { useState } from "react";
import { openExternal } from "../engine/client";
import type { Prediction, Reference } from "../engine/types";
import { t } from "../strings";
import { useStore } from "../state/store";
import { CheckIcon, TargetIcon } from "./icons";
import { Markdown } from "./Markdown";

/** Texto curto com `código` entre crases (missões, dicas, objetivos, previsões). */
function InlineText({ text }: { text: string }) {
  const parts = text.split(/(`[^`]+`)/g);
  return (
    <>
      {parts.map((part, index) =>
        part.startsWith("`") && part.endsWith("`") && part.length > 2 ? <code key={index}>{part.slice(1, -1)}</code> : part,
      )}
    </>
  );
}

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

export function TheoryPanel() {
  const lesson = useStore((s) => s.lesson);
  const hintsShown = useStore((s) => s.hintsShown);
  const showNextHint = useStore((s) => s.showNextHint);
  const challengeMode = useStore((s) => s.challengeMode);
  const challengeHintsShown = useStore((s) => s.challengeHintsShown);
  const { startChallenge, leaveChallenge } = useStore.getState();
  const completed = useStore((s) => Boolean(s.lesson && ((!s.challengeMode && s.validation?.passed) || s.progress[s.lesson.id]?.completed)));
  const challengeDone = useStore((s) => Boolean(s.lesson && ((s.challengeMode && s.validation?.passed) || s.progress[`${s.lesson.id}:challenge`]?.completed)));
  if (!lesson) return null;

  return (
    <aside className="panel theory" aria-label={t("theory.aria")}>
      {/* Título e missão ficam fixos no topo: o objetivo da tela vem antes da teoria. */}
      <header className="lesson-head">
        <p className="lesson-eyebrow">
          {t("theory.section", { id: lesson.id })}
          {lesson.estimated_minutes ? `, ${t("theory.minutes", { minutes: lesson.estimated_minutes })}` : ""}
        </p>
        <h1 className="lesson-title">{lesson.title}</h1>
        {lesson.objectives.length > 0 && (
          <div className="objectives">
            <h2 className="objectives-title">{t("theory.objectives")}</h2>
            <ul>
              {lesson.objectives.map((objective) => (
                <li key={objective}><InlineText text={objective} /></li>
              ))}
            </ul>
          </div>
        )}
        {challengeMode && lesson.challenge ? (
          <section className={`mission is-challenge${challengeDone ? " is-done" : ""}`} aria-labelledby="mission-title">
            <h2 className="mission-title" id="mission-title">
              {challengeDone ? <CheckIcon size={14} /> : <TargetIcon />}
              {challengeDone ? t("theory.challengeDone") : t("theory.challenge")}
              <span className="grow" />
              <button className="link small" onClick={leaveChallenge}>{t("theory.backToMission")}</button>
            </h2>
            <p><InlineText text={lesson.challenge.mission} /></p>
            <Hints hints={lesson.challenge.hints} shown={challengeHintsShown} onMore={showNextHint} />
          </section>
        ) : (
          <section className={`mission${completed ? " is-done" : ""}`} aria-labelledby="mission-title">
            <h2 className="mission-title" id="mission-title">
              {completed ? <CheckIcon size={14} /> : <TargetIcon />}
              {completed ? t("theory.missionDone") : t("theory.mission")}
            </h2>
            <p><InlineText text={lesson.mission} /></p>
            <Hints hints={lesson.hints} shown={hintsShown} onMore={showNextHint} />
            {completed && lesson.challenge && (
              <button className="btn btn-sm btn-challenge" onClick={startChallenge}>
                {challengeDone ? t("theory.challengeAgain") : t("theory.tryChallenge")}
              </button>
            )}
          </section>
        )}
      </header>
      <div className="panel-scroll" tabIndex={0}>
        <Markdown>{lesson.theory}</Markdown>
        {lesson.prediction && <PredictionCard key={lesson.id} prediction={lesson.prediction} />}
        {lesson.references?.length ? <References items={lesson.references} /> : null}
      </div>
    </aside>
  );
}
