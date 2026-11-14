import { t, useLocale } from "../i18n";
import { useStore } from "../state/store";
import { CircuitDiagram } from "./CircuitDiagram";
import { CodeEditor } from "./CodeEditor";
import { ExportButton } from "./ExportDialog";
import { exampleCode, SANDBOX_EXAMPLES, type SandboxExample } from "../lib/examples";
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
            {lesson ? (
              <span className="muted small">{t("lab.followHint")}</span>
            ) : (
              <ExamplePicker />
            )}
          </div>
          {/* A chave recria o editor ao trocar de lição (cursor e histórico de desfazer). */}
          <CodeEditor key={key} />
        </section>
        <section className="panel circuit-panel" aria-label={t("lab.circuit")}>
          <div className="panel-head">
            <h2>{t("lab.circuit")}</h2>
            <span className="grow" />
            <ExportButton />
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

/** Laboratório livre: troca o código por um exemplo pronto (circuito ou treino). */
function ExamplePicker() {
  return (
    <label className="example-picker">
      <span className="muted small">{t("lab.examples")}</span>
      <select
        className="select"
        value=""
        onChange={(event) => {
          const example = event.target.value as SandboxExample;
          if (example) useStore.getState().setCode(exampleCode(example));
        }}
      >
        <option value="" disabled>{t("lab.examplePick")}</option>
        {SANDBOX_EXAMPLES.map((example) => (
          <option key={example} value={example}>{t(`lab.example.${example}`)}</option>
        ))}
      </select>
    </label>
  );
}
