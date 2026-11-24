import { useId, useState } from "react";
import { openExternal } from "../engine/client";
import type { Reference } from "../engine/types";
import { t } from "../strings";
import { useStore } from "../state/store";
import { BookIcon, CheckIcon, TargetIcon } from "./icons";
import { MissionText, PredictionCard } from "./TheoryPanel";

/** What to look at before starting, from the lesson's own (verified) references: the first course
 *  or tutorial page, and the first paper, or a book when there is no paper. */
function primerPicks(references: Reference[]): Reference[] {
  const practical = references.find((ref) => ref.kind === "course" || ref.kind === "tutorial");
  const reading = references.find((ref) => ref.kind === "paper") ?? references.find((ref) => ref.kind === "book");
  const picks = [practical, reading].filter((ref): ref is Reference => ref !== undefined);
  return picks.length ? picks : references.slice(0, 1);
}

/** The prediction answered in each lesson, remembered in the browser. */
function readPrediction(lessonId: string): number | null {
  try {
    const value = localStorage.getItem(`ket-lab.prediction.${lessonId}`);
    return value === null ? null : Number(value);
  } catch {
    return null;
  }
}

function writePrediction(lessonId: string, choice: number): void {
  try {
    localStorage.setItem(`ket-lab.prediction.${lessonId}`, String(choice));
  } catch {
    // Not remembered.
  }
}

function Primer({ items, id }: { items: Reference[]; id: string }) {
  return (
    <ul className="primer" id={id} aria-label={t("mission.primer")}>
      {items.map((ref) => (
        <li key={ref.url}>
          <span className="primer-kind">{t(`ref.${ref.kind}`)}</span>
          <a
            href={ref.url}
            target="_blank"
            rel="noopener noreferrer"
            title={t("mission.primerOpens")}
            onClick={(event) => {
              event.preventDefault();
              openExternal(ref.url);
            }}
          >
            {ref.title}
          </a>
          <span className="primer-where">
            {ref.authors}
            {ref.year ? `, ${ref.year}` : ""}. {ref.location}
          </span>
        </li>
      ))}
    </ul>
  );
}

/** The mission, above the code and the state: its text on the left; on the right, "Before you start"
 *  (sources to read or watch first) and "Predict before you run". Each opens under the text, inside
 *  the same box, one at a time. Lab gives it a key per lesson. */
export function MissionBar() {
  const lesson = useStore((s) => s.lesson);
  const lessonId = lesson?.id ?? null;
  const challengeMode = useStore((s) => s.challengeMode);
  const completed = useStore((s) => Boolean(s.lesson && ((!s.challengeMode && s.validation?.passed) || s.progress[s.lesson.id]?.completed)));
  const challengeDone = useStore((s) => Boolean(s.lesson && ((s.challengeMode && s.validation?.passed) || s.progress[`${s.lesson.id}:challenge`]?.completed)));
  // One panel open at a time under the mission text: the primer or the prediction.
  const [open, setOpen] = useState<"primer" | "predict" | null>(null);
  const toggle = (panel: "primer" | "predict") => setOpen(open === panel ? null : panel);
  const predictionId = useId();
  const [predicted, setPredicted] = useState<number | null>(() => (lessonId ? readPrediction(lessonId) : null));
  const primerId = useId();
  if (!lesson) return null;
  const { startChallenge, leaveChallenge } = useStore.getState();
  const inChallenge = challengeMode && Boolean(lesson.challenge);
  const done = inChallenge ? challengeDone : completed;
  const title = inChallenge
    ? t(challengeDone ? "theory.challengeDone" : "theory.challenge")
    : t(completed ? "theory.missionDone" : "theory.mission");
  const prediction = inChallenge ? undefined : lesson.prediction;
  const primer = inChallenge ? [] : primerPicks(lesson.references ?? []);
  const predictedRight = prediction !== undefined && predicted === prediction.answer;
  const choose = (index: number) => {
    setPredicted(index);
    writePrediction(lesson.id, index);
  };

  return (
    <section
      className={`mission mission-bar${inChallenge ? " is-challenge" : ""}${done ? " is-done" : ""}`}
      aria-labelledby="mission-title"
    >
      <div className="mission-main">
        <h2 className="mission-title" id="mission-title">
          {done ? <CheckIcon size={14} /> : <TargetIcon />}
          {title}
        </h2>
        <MissionText key={inChallenge ? `${lesson.id}:c` : lesson.id} text={inChallenge && lesson.challenge ? lesson.challenge.mission : lesson.mission} />
        {primer.length > 0 && open === "primer" && <Primer items={primer} id={primerId} />}
        {prediction && open === "predict" && <PredictionCard prediction={prediction} inline id={predictionId} chosen={predicted} onChoose={choose} />}
      </div>
      <div className="mission-side">
        {primer.length > 0 && (
          <button
            className={`btn btn-sm mission-toggle${open === "primer" ? " is-open" : ""}`}
            aria-expanded={open === "primer"}
            aria-controls={open === "primer" ? primerId : undefined}
            onClick={() => toggle("primer")}
          >
            <BookIcon />
            {t("mission.primer")}
          </button>
        )}
        {prediction && (
          <button
            className={`btn btn-sm mission-toggle${open === "predict" ? " is-open" : ""}${predictedRight ? " is-correct" : ""}`}
            aria-expanded={open === "predict"}
            aria-controls={open === "predict" ? predictionId : undefined}
            onClick={() => toggle("predict")}
          >
            {predictedRight && <CheckIcon size={13} />}
            {t("theory.predict")}
          </button>
        )}
        {inChallenge ? (
          <button className="link small" onClick={leaveChallenge}>{t("theory.backToMission")}</button>
        ) : (
          completed && lesson.challenge && (
            <button className="btn btn-sm btn-challenge" onClick={startChallenge}>
              {challengeDone ? t("theory.challengeAgain") : t("theory.tryChallenge")}
            </button>
          )
        )}
      </div>
    </section>
  );
}
