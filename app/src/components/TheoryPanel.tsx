import { useState } from "react";
import { openExternal } from "../engine/client";
import type { Prediction, Reference } from "../engine/types";
import { t } from "../strings";
import { useStore } from "../state/store";
import { TargetIcon } from "./icons";
import { Markdown } from "./Markdown";

function PredictionCard({ prediction }: { prediction: Prediction }) {
  const [choice, setChoice] = useState<number | null>(null);
  const answered = choice !== null;
  return (
    <section className="card">
      <h3 className="card-title">{t("theory.predict")}</h3>
      <p>{prediction.question}</p>
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
              {option}
            </button>
          );
        })}
      </div>
      {answered && (
        <p className="card-note">
          <strong>{choice === prediction.answer ? t("theory.correct") : t("theory.wrong")}</strong> {prediction.explanation}
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
              {ref.section ? ` · ${t("ref.section", { section: ref.section })}` : ""}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export function TheoryPanel() {
  const lesson = useStore((s) => s.lesson);
  const hintsShown = useStore((s) => s.hintsShown);
  const showNextHint = useStore((s) => s.showNextHint);
  if (!lesson) return null;

  return (
    <aside className="panel theory" aria-label={t("theory.aria")}>
      <div className="panel-scroll">
        <p className="lesson-eyebrow">
          {t("theory.section", { id: lesson.id })}
          {lesson.estimated_minutes ? ` · ${t("theory.minutes", { minutes: lesson.estimated_minutes })}` : ""}
        </p>
        <h1 className="lesson-title">{lesson.title}</h1>
        <Markdown>{lesson.theory}</Markdown>
        {lesson.prediction && <PredictionCard key={lesson.id} prediction={lesson.prediction} />}
        {lesson.references?.length ? <References items={lesson.references} /> : null}
      </div>

      {/* A missão fica fixa no rodapé do painel: sempre visível, mesmo com a teoria rolada. */}
      <div className="mission">
        <h3 className="card-title">
          <TargetIcon /> {t("theory.mission")}
        </h3>
        <p>{lesson.mission}</p>
        {hintsShown > 0 && (
          <ol className="hints">
            {lesson.hints.slice(0, hintsShown).map((hint, index) => (
              <li key={index}>{hint}</li>
            ))}
          </ol>
        )}
        {hintsShown < lesson.hints.length && (
          <button className="btn btn-sm" onClick={showNextHint}>
            {t("theory.hint", { n: hintsShown + 1, total: lesson.hints.length })}
          </button>
        )}
      </div>
    </aside>
  );
}
