import { useState } from "react";
import { t } from "../strings";
import { useStore } from "../state/store";
import { CircuitDiagram } from "./CircuitDiagram";
import { CodeEditor } from "./CodeEditor";
import { ExportButton } from "./ExportDialog";
import { exampleCode, SANDBOX_EXAMPLES, type SandboxExample } from "../lib/examples";
import { OracleBar } from "./OracleBar";
import { TheoryPanel } from "./TheoryPanel";
import { Timeline } from "./Timeline";
import { Tour } from "./Tour";
import { Visualizer } from "./Visualizer";

export function Lab() {
  const lesson = useStore((s) => s.lesson);
  const key = lesson?.id ?? "sandbox";
  // Lições sem circuito (kit de matemática) não têm painel de circuito.
  const hasCircuit = lesson?.framework !== "python";
  // Telas estreitas: um painel por vez, escolhido nas abas (em telas largas as abas somem).
  const panes: Pane[] = lesson ? ["theory", "code", "state"] : ["code", "state"];
  const [chosen, setPane] = useState<Pane>(lesson ? "theory" : "code");
  const pane = panes.includes(chosen) ? chosen : panes[0];
  const paneClass = (name: Pane) => `pane${pane === name ? " is-active" : ""}`;
  return (
    <div className={`lab${lesson ? "" : " is-sandbox"}`}>
      <div className="lab-tabs segmented" role="tablist" aria-label={t("lab.panes")}>
        {panes.map((name) => (
          <button key={name} role="tab" aria-selected={pane === name} onClick={() => setPane(name)}>
            {t(`lab.pane.${name}`)}
          </button>
        ))}
      </div>
      {lesson && (
        <div className={paneClass("theory")}>
          <TheoryPanel />
        </div>
      )}
      <div className={paneClass("code")}>
      <div className="column">
        <section className="panel editor-panel" aria-label={t("lab.codeAria")}>
          <div className="panel-head">
            <h2>{t("lab.code")}</h2>
            <span className="grow" />
            {!lesson && <ExamplePicker />}
          </div>
          {/* A chave recria o editor ao trocar de lição (cursor e histórico de desfazer). */}
          <CodeEditor key={key} />
        </section>
        {hasCircuit && <section className="panel circuit-panel" aria-label={t("lab.circuit")}>
          <div className="panel-head">
            <h2>{t("lab.circuit")}</h2>
            <span className="grow" />
            <ExportButton />
          </div>
          <CircuitDiagram />
          <Timeline />
        </section>}
      </div>
      </div>
      <div className={paneClass("state")}>
        <Visualizer key={key} lesson={lesson} />
      </div>
      <OracleBar />
      <Tour />
    </div>
  );
}

type Pane = "theory" | "code" | "state";

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
