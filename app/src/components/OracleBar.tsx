import { t } from "../strings";
import { selectManual, selectNextLessonId, useStore, type TrainingState } from "../state/store";
import { AlertIcon, CheckIcon, DotIcon } from "./icons";

export function OracleBar() {
  const lesson = useStore((s) => s.lesson);
  const error = useStore((s) => s.error);
  const resultIsCurrent = useStore((s) => s.resultIsCurrent);
  const validation = useStore((s) => s.validation);
  const validating = useStore((s) => s.validating);
  const connection = useStore((s) => s.connection);
  const nextLessonId = useStore(selectNextLessonId);
  const running = useStore((s) => s.running);
  const resultIsCurrentForManual = useStore((s) => s.resultIsCurrent);
  const training = useStore((s) => s.training);
  const manual = useStore(selectManual);
  const { validate, runShots, resetCode, openLesson, backToHub, runNow, stopRun } = useStore.getState();

  let tone: "neutral" | "success" | "warn" | "error" = "neutral";
  let message = manual
    ? lesson ? t("oracle.idleManual") : t("oracle.idleTraining")
    : lesson ? t("oracle.idleLesson") : t("oracle.idleSandbox");
  if (running && training?.active) {
    message = trainingMessage(training, "oracle.training");
  } else if (training && !training.active && resultIsCurrent && !error) {
    message = trainingMessage(training, "oracle.trainingDone");
  } else if (error?.kind === "cancelled" && !resultIsCurrent) {
    message = error.message;
  } else if (error && !resultIsCurrent) {
    tone = "error";
    message = error.line != null ? t("oracle.atLine", { line: error.line, message: error.message }) : error.message;
  } else if (validation) {
    tone = validation.passed ? "success" : "warn";
    message = validation.message;
  }

  const offline = connection !== "open";

  return (
    <footer className={`oracle is-${tone}`}>
      <p className="oracle-message" role="status" aria-live="polite">
        <span className="oracle-icon" aria-hidden="true">
          {tone === "success" ? <CheckIcon size={13} /> : tone === "neutral" ? <DotIcon /> : <AlertIcon />}
        </span>
        {message}
      </p>
      <div className="oracle-actions">
        <button className="btn btn-ghost" onClick={resetCode}>{t("oracle.reset")}</button>
        {manual && running && training?.active ? (
          <button className="btn" onClick={stopRun} title={t("oracle.stopTitle")}>{t("oracle.stop")}</button>
        ) : manual ? (
          <button
            className={`btn${resultIsCurrentForManual ? "" : " btn-primary"}`}
            onClick={runNow}
            disabled={offline || running}
            title={t("oracle.runTitle")}
          >
            {running ? t("oracle.running") : t("oracle.run")}
          </button>
        ) : lesson?.framework === "python" ? null : (
          <button className="btn" onClick={() => void runShots()} disabled={offline}>{t("oracle.shots")}</button>
        )}
        {lesson && !validation?.passed && (
          <button className="btn btn-primary" onClick={() => void validate()} disabled={offline || validating}>
            {validating ? t("oracle.validating") : t("oracle.validate")}
          </button>
        )}
        {lesson && validation?.passed && (
          nextLessonId ? (
            <button className="btn btn-primary" onClick={() => void openLesson(nextLessonId)}>{t("oracle.next")}</button>
          ) : (
            <button className="btn btn-primary" onClick={backToHub}>{t("oracle.back")}</button>
          )
        )}
      </div>
    </footer>
  );
}

function trainingMessage(training: TrainingState, key: "oracle.training" | "oracle.trainingDone"): string {
  const [name, values] = Object.entries(training.series)[0] ?? [];
  if (!name || !values?.length) return t("oracle.trainingStart");
  const value = values[values.length - 1];
  const shown = Math.abs(value) >= 1e4 || (value !== 0 && Math.abs(value) < 1e-3) ? value.toExponential(3) : value.toFixed(4);
  return t(key, { step: values.length, name, value: shown.replace("-", "−") });
}
