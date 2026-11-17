import { useEffect, useRef, useState, type KeyboardEvent } from "react";
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
import { OracleBar } from "./OracleBar";
import { TheoryPanel } from "./TheoryPanel";
import { Timeline } from "./Timeline";
import { Tour } from "./Tour";
import { Visualizer } from "./Visualizer";

export function Lab() {
  const lesson = useStore((s) => s.lesson);
  const key = lesson?.id ?? "sandbox";
  // Lessons without a circuit (math kit) have no circuit panel.
  const hasCircuit = lesson?.framework !== "python";
  const code = useStore((s) => s.code);
  const canCompose = composerSupported(code, lesson?.framework);
  const [composing, setComposing] = useState(false);
  // Narrow screens: one panel at a time, chosen in the tabs (on wide screens the tabs disappear).
  const panes: Pane[] = lesson ? ["theory", "code", "state"] : ["code", "state"];
  const [chosen, setPane] = useState<Pane>(lesson ? "theory" : "code");
  const pane = panes.includes(chosen) ? chosen : panes[0];
  const paneProps = (name: Pane) => ({
    className: `pane${pane === name ? " is-active" : ""}`,
    role: "tabpanel" as const,
    id: `pane-${name}`,
    "aria-labelledby": `pane-tab-${name}`,
  });
  const notesOpen = useStore((s) => s.notesOpen && lesson !== null);
  useLabShortcuts(panes, setPane);

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
    <div className={`lab${lesson ? "" : " is-sandbox"}${notesOpen ? " has-notes" : ""}`}>
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
      {lesson && (
        <div {...paneProps("theory")}>
          <TheoryPanel />
        </div>
      )}
      <div {...paneProps("code")}>
      <div className="column">
        <section className="panel editor-panel" aria-label={t("lab.codeAria")}>
          <div className="panel-head">
            <h2>{t("lab.code")}</h2>
            <span className="grow" />
            {!lesson && <ShareButton />}
            {!lesson && <ExamplePicker />}
          </div>
          <SharedCodeNotice />
          {/* The key recreates the editor when switching lessons (cursor and undo history). */}
          <CodeEditor key={key} />
        </section>
        {hasCircuit && <section className="panel circuit-panel" aria-label={t("lab.circuit")}>
          <div className="panel-head">
            <h2>{t("lab.circuit")}</h2>
            <span className="grow" />
            {canCompose && (
              <button
                className="btn btn-ghost btn-sm"
                aria-pressed={composing}
                onClick={() => setComposing(!composing)}
                title={t("composer.toggleHint")}
              >
                {composing ? t("composer.close") : t("composer.open")}
              </button>
            )}
            <HardwareButton />
            <ExportButton />
          </div>
          {composing && canCompose && <Composer />}
          <CircuitDiagram />
          <Timeline />
        </section>}
      </div>
      </div>
      <div {...paneProps("state")}>
        <Visualizer key={key} lesson={lesson} />
      </div>
      <NotesDrawer />
      <OracleBar />
      <Tour />
    </div>
  );
}

type Pane = "theory" | "code" | "state";

const PANE_KEYS: Record<string, Pane> = { Digit1: "theory", Digit2: "code", Digit3: "state" };

/** Moves the keyboard to a panel (on narrow screens, switching to its tab first). */
function focusPane(name: Pane): void {
  const find = (): HTMLElement | null =>
    name === "theory"
      ? document.querySelector<HTMLElement>(".theory-scroll")
      : name === "code"
        ? document.querySelector<HTMLElement>(".editor textarea")
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
