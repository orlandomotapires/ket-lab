import { t, useLocale } from "../i18n";
import { useStore } from "../state/store";
import { CircuitDiagram } from "./CircuitDiagram";
import { CodeEditor } from "./CodeEditor";
import { OracleBar } from "./OracleBar";
import { TheoryPanel } from "./TheoryPanel";
import { Timeline } from "./Timeline";
import { Visualizer } from "./Visualizer";

export function Lab() {
  useLocale();
  const lesson = useStore((s) => s.lesson);
  const key = lesson?.id ?? "sandbox";
  return (
    <div className={`lab${lesson ? "" : " is-sandbox"}`}>
      <TheoryPanel />
      <div className="column">
        <section className="panel editor-panel" aria-label={t("lab.codeAria")}>
          <div className="panel-head">
            <h2>{t("lab.code")}</h2>
            <span className="grow" />
            <span className="muted small">{t("lab.followHint")}</span>
          </div>
          {/* A chave recria o editor ao trocar de lição (cursor e histórico de desfazer). */}
          <CodeEditor key={key} />
        </section>
        <section className="panel circuit-panel" aria-label={t("lab.circuit")}>
          <div className="panel-head">
            <h2>{t("lab.circuit")}</h2>
          </div>
          <CircuitDiagram />
          <Timeline />
        </section>
      </div>
      <Visualizer key={key} lesson={lesson} />
      <OracleBar />
    </div>
  );
}
