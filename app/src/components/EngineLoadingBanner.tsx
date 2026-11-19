import type { EngineLoading } from "../engine/client";
import { t, type MessageKey } from "../strings";

const STAGE_TEXT: Record<EngineLoading["stage"], MessageKey> = {
  runtime: "engineLoading.runtime",
  packages: "engineLoading.packages",
  libraries: "engineLoading.libraries",
  lessons: "engineLoading.lessons",
  starting: "engineLoading.starting",
};

const TITLE: Record<EngineLoading["reason"], MessageKey> = {
  start: "engineLoading.title",
  restart: "engineLoading.restart",
  memory: "engineLoading.memory",
};

/** Browser mode: the engine downloads and starts Python in the page; shows which step it is on. */
export function EngineLoadingBanner({ loading }: { loading: EngineLoading }) {
  const label = t(STAGE_TEXT[loading.stage]);
  return (
    <div className="banner engine-loading" role="status">
      <div className="engine-loading-text">
        <strong>{t(TITLE[loading.reason])}</strong>
        <span>
          {t("engineLoading.step", { step: loading.step, total: loading.total })}: {label}
        </span>
      </div>
      <progress
        className="engine-loading-bar"
        max={loading.total}
        value={loading.step - 1}
        aria-label={t("engineLoading.progress")}
      />
      {loading.reason === "start" && <p className="engine-loading-note">{t("engineLoading.note")}</p>}
    </div>
  );
}
