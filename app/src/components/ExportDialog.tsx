import { useEffect, useRef, useState } from "react";
import { saveTextFile } from "../engine/client";
import type { ExportFormat } from "../engine/types";
import { t, useLocale } from "../i18n";
import { useStore } from "../state/store";
import { ExportIcon } from "./icons";

const FORMATS: { id: ExportFormat; label: string }[] = [
  { id: "qasm3", label: "OpenQASM 3" },
  { id: "qasm2", label: "OpenQASM 2" },
];

/** Botão do painel do circuito: abre a exportação em OpenQASM. */
export function ExportButton() {
  useLocale();
  const [open, setOpen] = useState(false);
  const offline = useStore((s) => s.connection !== "open");
  return (
    <>
      <button className="btn btn-ghost btn-sm" onClick={() => setOpen(true)} disabled={offline} title={t("export.hint")}>
        <ExportIcon />
        {t("export.button")}
      </button>
      {open && <ExportDialog onClose={() => setOpen(false)} />}
    </>
  );
}

type Status = { kind: "idle" | "loading" | "copied" | "saved" } | { kind: "error"; message: string };

function ExportDialog({ onClose }: { onClose: () => void }) {
  useLocale();
  const dialog = useRef<HTMLDialogElement>(null);
  const [format, setFormat] = useState<ExportFormat>("qasm3");
  const [text, setText] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>({ kind: "loading" });
  const lessonId = useStore((s) => s.lesson?.id);

  useEffect(() => {
    const element = dialog.current;
    if (element && !element.open) element.showModal();
  }, []);

  useEffect(() => {
    let cancelled = false;
    setStatus({ kind: "loading" });
    useStore
      .getState()
      .exportCircuit(format)
      .then((response) => {
        if (cancelled) return;
        if (response.ok) {
          setText(response.text);
          setStatus({ kind: "idle" });
        } else {
          setText(null);
          setStatus({ kind: "error", message: response.error?.message ?? t("export.failed") });
        }
      })
      .catch(() => !cancelled && setStatus({ kind: "error", message: t("export.failed") }));
    return () => {
      cancelled = true;
    };
  }, [format]);

  const fileName = `${t("export.fileName")}${lessonId ? `-${lessonId}` : ""}.qasm`;

  async function copy() {
    if (text === null) return;
    try {
      await navigator.clipboard.writeText(text);
      setStatus({ kind: "copied" });
    } catch {
      setStatus({ kind: "error", message: t("export.copyFailed") });
    }
  }

  async function save() {
    if (text === null) return;
    try {
      if (saveTextFile(text, fileName)) setStatus({ kind: "saved" });
    } catch (error) {
      setStatus({ kind: "error", message: String(error instanceof Error ? error.message : error) });
    }
  }

  return (
    <dialog
      ref={dialog}
      className="dialog export-dialog"
      aria-labelledby="export-title"
      onClose={onClose}
      onClick={(event) => event.target === dialog.current && dialog.current?.close()}
    >
      <div className="dialog-head">
        <h2 id="export-title">{t("export.title")}</h2>
        <span className="grow" />
        <div className="segmented" role="tablist" aria-label={t("export.format")}>
          {FORMATS.map((option) => (
            <button key={option.id} role="tab" aria-selected={format === option.id} onClick={() => setFormat(option.id)}>
              {option.label}
            </button>
          ))}
        </div>
      </div>
      <p className="muted small dialog-note">{t(format === "qasm3" ? "export.note3" : "export.note2")}</p>
      {status.kind === "error" ? (
        <p className="notice notice-error">{status.message}</p>
      ) : (
        <pre className={`export-code${status.kind === "loading" ? " is-loading" : ""}`} tabIndex={0}>
          {text ?? t("export.loading")}
        </pre>
      )}
      <div className="dialog-actions">
        <span className="muted small" role="status" aria-live="polite">
          {status.kind === "copied" ? t("export.copied") : status.kind === "saved" ? t("export.saved") : ""}
        </span>
        <span className="grow" />
        <button className="btn btn-ghost" onClick={() => dialog.current?.close()}>{t("export.close")}</button>
        <button className="btn" onClick={() => void copy()} disabled={text === null || status.kind === "loading"}>
          {t("export.copy")}
        </button>
        <button className="btn btn-primary" onClick={() => void save()} disabled={text === null || status.kind === "loading"}>
          {t("export.save")}
        </button>
      </div>
    </dialog>
  );
}
