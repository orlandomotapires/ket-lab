import { useState } from "react";
import { t } from "../strings";
import { useStore } from "../state/store";
import { CircuitDiagram } from "./CircuitDiagram";
import { CodeEditor } from "./CodeEditor";
import { ExportButton } from "./ExportDialog";
import { HardwareButton } from "./HardwareDialog";
import { exampleCode, SANDBOX_EXAMPLES, type SandboxExample } from "../lib/examples";
import { shareLink } from "../lib/share";
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
            {!lesson && <ShareButton />}
            {!lesson && <ExamplePicker />}
          </div>
          <SharedCodeNotice />
          {/* A chave recria o editor ao trocar de lição (cursor e histórico de desfazer). */}
          <CodeEditor key={key} />
        </section>
        {hasCircuit && <section className="panel circuit-panel" aria-label={t("lab.circuit")}>
          <div className="panel-head">
            <h2>{t("lab.circuit")}</h2>
            <span className="grow" />
            <HardwareButton />
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

/** Copia um link com o código do laboratório livre. */
function ShareButton() {
  const [copied, setCopied] = useState(false);
  return (
    <button
      className="btn btn-ghost btn-sm"
      title={t("share.hint")}
      onClick={async () => {
        const link = await shareLink(useStore.getState().code);
        try {
          await navigator.clipboard.writeText(link);
        } catch {
          window.prompt(t("share.copyManually"), link);
        }
        setCopied(true);
        window.setTimeout(() => setCopied(false), 2000);
      }}
    >
      {copied ? t("share.copied") : t("share.button")}
    </button>
  );
}

/** Código aberto por link: não roda até o aluno ler e confirmar. */
function SharedCodeNotice() {
  const trusted = useStore((s) => s.codeTrusted);
  if (trusted) return null;
  return (
    <div className="shared-notice" role="alert">
      <p>{t("share.review")}</p>
      <button className="btn btn-primary btn-sm" onClick={() => useStore.getState().trustShared()}>
        {t("share.run")}
      </button>
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
