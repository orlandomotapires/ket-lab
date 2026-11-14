import { t, useLocale } from "../i18n";
import { selectNextLessonId, useStore } from "../state/store";
import { AlertIcon, CheckIcon, DotIcon } from "./icons";

export function OracleBar() {
  useLocale();
  const lesson = useStore((s) => s.lesson);
  const error = useStore((s) => s.error);
  const resultIsCurrent = useStore((s) => s.resultIsCurrent);
  const validation = useStore((s) => s.validation);
  const validating = useStore((s) => s.validating);
  const connection = useStore((s) => s.connection);
  const nextLessonId = useStore(selectNextLessonId);
  const { validate, runShots, resetCode, openLesson, backToHub } = useStore.getState();

  let tone: "neutral" | "success" | "warn" | "error" = "neutral";
  let message = lesson ? t("oracle.idleLesson") : t("oracle.idleSandbox");
  if (error && !resultIsCurrent) {
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
        <button className="btn" onClick={() => void runShots()} disabled={offline}>{t("oracle.shots")}</button>
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
