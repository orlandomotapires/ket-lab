import { useEffect, useRef, useState, type CSSProperties, type KeyboardEvent } from "react";
import { useStoredFlag, useStoredNumber } from "../lib/storedFlag";
import { t } from "../strings";
import { useStore } from "../state/store";
import { CircuitDiagram } from "./CircuitDiagram";
import { Composer, composerSupported } from "./Composer";
import { CodeEditor } from "./CodeEditor";
import { ExportButton } from "./ExportDialog";
import { HardwareButton } from "./HardwareDialog";
import { exampleCode, SANDBOX_EXAMPLES, type SandboxExample } from "../lib/examples";
import { shareLink } from "../lib/share";
import { NotesDrawer } from "./NotesDrawer";
import { Splitter } from "./Splitter";
import { OracleBar } from "./OracleBar";
import { MissionBar } from "./MissionBar";
import { Timeline } from "./Timeline";
import { Tour } from "./Tour";
import { Visualizer } from "./Visualizer";

export function Lab() {
  const lesson = useStore((s) => s.lesson);
  const key = lesson?.id ?? "sandbox";
  // Narrow screens: one panel at a time, chosen in the tabs (on wide screens the tabs disappear).
  const panes: Pane[] = ["code", "state"];
  const [pane, setPane] = useState<Pane>("code");
  const paneProps = (name: Pane) => ({
    className: `pane${pane === name ? " is-active" : ""}`,
    role: "tabpanel" as const,
    id: `pane-${name}`,
    "aria-labelledby": `pane-tab-${name}`,
  });
  const notesOpen = useStore((s) => s.notesOpen && lesson !== null);
  useLabShortcuts(panes, setPane);
  // Width of the code column, in percent of the lab; the state column takes the rest.
  const labRef = useRef<HTMLDivElement>(null);
  const [split, setSplit] = useStoredNumber("ket-lab.lab.split", SPLIT);

  // Arrow keys move between the tabs (the tab in focus is the chosen one).
  const onTabKey = (event: KeyboardEvent<HTMLDivElement>) => {
    const index = panes.indexOf(pane);
    const target =
      event.key === "ArrowRight" ? panes[(index + 1) % panes.length]
      : event.key === "ArrowLeft" ? panes[(index - 1 + panes.length) % panes.length]
      : event.key === "Home" ? panes[0]
      : event.key === "End" ? panes[panes.length - 1]
      : null;
    if (!target) return;
    event.preventDefault();
    setPane(target);
    document.getElementById(`pane-tab-${target}`)?.focus();
  };
  return (
    <div
      ref={labRef}
      className={`lab${lesson ? "" : " is-sandbox"}${notesOpen ? " has-notes" : ""}`}
      style={{ "--split": `${split}%` } as CSSProperties}
    >
      <div className="lab-tabs segmented" role="tablist" aria-label={t("lab.panes")} onKeyDown={onTabKey}>
        {panes.map((name) => (
          <button
            key={name}
            role="tab"
            id={`pane-tab-${name}`}
            aria-selected={pane === name}
            aria-controls={`pane-${name}`}
            tabIndex={pane === name ? 0 : -1}
            onClick={() => setPane(name)}
          >
            {t(`lab.pane.${name}`)}
          </button>
        ))}
      </div>
      {lesson && <MissionBar key={key} />}
      <div {...paneProps("code")}>
        <Workspace editorKey={key} />
      </div>
      <Splitter
        orientation="vertical"
        className="column-splitter"
        value={split}
        min={28}
        max={68}
        initial={SPLIT}
        onChange={setSplit}
        label={t("lab.resizeColumns")}
        container={() => labRef.current}
      />
      <div {...paneProps("state")}>
        <Visualizer key={key} lesson={lesson} />
      </div>
      <NotesDrawer />
      <OracleBar />
      <Tour />
    </div>
  );
}

/** Code and circuit share one panel: either one, or both splitting the space. The choice is remembered. */
function Workspace({ editorKey }: { editorKey: string }) {
  const lesson = useStore((s) => s.lesson);
  // Lessons without a circuit (math kit) only have the code.
  const hasCircuit = lesson?.framework !== "python";
  const code = useStore((s) => s.code);
  const canCompose = composerSupported(code, lesson?.framework);
  const [composing, setComposing] = useState(false);
  const [codeOn, setCodeOn] = useStoredFlag("ket-lab.lab.showCode", true);
  const [circuitOn, setCircuitOn] = useStoredFlag("ket-lab.lab.showCircuit", false);
  // With both open: the code's share of the height, in percent.
  const [codeShare, setCodeShare] = useStoredNumber("ket-lab.lab.codeShare", CODE_SHARE);
  const bodyRef = useRef<HTMLDivElement>(null);
  const showCircuit = hasCircuit && circuitOn;
  // At least one view stays open.
  const showCode = codeOn || !showCircuit;
  const toggle = (view: "code" | "circuit") => {
    if (view === "code" && !(showCode && !showCircuit)) setCodeOn(!showCode);
    if (view === "circuit" && !(showCircuit && !showCode)) setCircuitOn(!showCircuit);
  };
  return (
    <section className="panel work-panel" aria-label={t("lab.workAria")}>
      <div className="panel-head">
        {hasCircuit ? (
          <div className="segmented" role="group" aria-label={t("lab.workViews")}>
            <button aria-pressed={showCode} onClick={() => toggle("code")}>{t("lab.code")}</button>
            <button aria-pressed={showCircuit} onClick={() => toggle("circuit")}>{t("lab.circuit")}</button>
          </div>
        ) : (
          <h2>{t("lab.code")}</h2>
        )}
        <span className="grow" />
        {showCode && !lesson && <ShareButton />}
        {showCode && !lesson && <ExamplePicker />}
        {showCircuit && canCompose && (
          <button
            className="btn btn-ghost btn-sm"
            aria-pressed={composing}
            onClick={() => setComposing(!composing)}
            title={t("composer.toggleHint")}
          >
            {composing ? t("composer.close") : t("composer.open")}
          </button>
        )}
        {showCircuit && <HardwareButton />}
        {showCircuit && <ExportButton />}
      </div>
      <div className="work-body" ref={bodyRef}>
        {showCode && (
          <div className="editor-panel" role="region" aria-label={t("lab.codeAria")} style={showCircuit ? { flexGrow: codeShare } : undefined}>
            <SharedCodeNotice />
            {/* The key recreates the editor when switching lessons (cursor and undo history). */}
            <CodeEditor key={editorKey} />
          </div>
        )}
        {showCode && showCircuit && (
          <Splitter
            orientation="horizontal"
            value={codeShare}
            min={20}
            max={85}
            initial={CODE_SHARE}
            onChange={setCodeShare}
            label={t("lab.resizeCode")}
            container={() => bodyRef.current}
          />
        )}
        {showCircuit && (
          <div className="circuit-panel" role="region" aria-label={t("lab.circuit")} style={showCode ? { flexGrow: 100 - codeShare } : undefined}>
            {composing && canCompose && <Composer />}
            <CircuitDiagram />
            <Timeline />
          </div>
        )}
      </div>
    </section>
  );
}

type Pane = "code" | "state";

/** Starting sizes: the code column's width and, with the circuit open too, the code's height (percent). */
const SPLIT = 45;
const CODE_SHARE = 60;

const PANE_KEYS: Record<string, Pane> = { Digit1: "code", Digit2: "state" };

/** Moves the keyboard to a panel (on narrow screens, switching to its tab first). */
function focusPane(name: Pane): void {
  const find = (): HTMLElement | null =>
    name === "code"
      ? (document.querySelector<HTMLElement>(".editor textarea") ?? document.querySelector<HTMLElement>(".work-panel [aria-pressed]"))
      : (document.querySelector<HTMLElement>(".visualizer .panel-scroll") ??
        document.querySelector<HTMLElement>('.visualizer [aria-pressed="true"]') ??
        document.querySelector<HTMLElement>(".visualizer"));
  window.setTimeout(() => {
    const element = find();
    if (!element) return;
    if (element.tabIndex < 0) element.tabIndex = -1;
    element.focus();
  }, 60);
}

/** Lab shortcuts: Check, panel switching and the notes drawer. They work while typing in the editor. */
function useLabShortcuts(panes: Pane[], setPane: (pane: Pane) => void) {
  const latest = useRef({ panes, setPane });
  latest.current = { panes, setPane };
  useEffect(() => {
    const onKey = (event: globalThis.KeyboardEvent) => {
      const mod = event.ctrlKey || event.metaKey;
      const state = useStore.getState();
      if (mod && event.shiftKey && !event.altKey && event.key === "Enter") {
        event.preventDefault();
        event.stopPropagation();
        if (state.lesson && state.connection === "open" && !state.validating && !state.validation?.passed) void state.validate();
        return;
      }
      if (!event.altKey || mod || event.shiftKey) return;
      const name = PANE_KEYS[event.code];
      if (name) {
        event.preventDefault();
        event.stopPropagation();
        if (!latest.current.panes.includes(name)) return;
        latest.current.setPane(name);
        focusPane(name);
      } else if (event.code === "KeyN" && state.lesson) {
        event.preventDefault();
        event.stopPropagation();
        state.setNotesOpen(!state.notesOpen);
      }
    };
    // Capture phase: the editor would otherwise use some of these keys itself.
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, []);
}

/** Copies a link with the free lab code. */
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

/** Code opened by link: does not run until the learner reads and confirms. */
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

/** Free lab: swaps the code for a ready example (circuit or training). */
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
