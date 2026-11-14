import { useState } from "react";
import type { Prediction } from "../engine/types";
import { t, useLocale } from "../i18n";
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

export function TheoryPanel() {
  useLocale();
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
        {/* A escolha da previsão sobrevive à troca de idioma (mesma chave). */}
        {lesson.prediction && <PredictionCard key={lesson.id} prediction={lesson.prediction} />}
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
