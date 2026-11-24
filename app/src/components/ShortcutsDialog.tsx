import { useEffect, useRef } from "react";
import { altKey, modKey } from "../lib/platform";
import { t, type MessageKey } from "../strings";

const ROWS: { keys: string; label: MessageKey }[] = [
  { keys: `${modKey} K`, label: "shortcuts.search" },
  { keys: `${modKey} Enter`, label: "shortcuts.run" },
  { keys: `${modKey} Shift Enter`, label: "shortcuts.check" },
  { keys: `${altKey} 1`, label: "shortcuts.code" },
  { keys: `${altKey} 2`, label: "shortcuts.state" },
  { keys: `${altKey} N`, label: "shortcuts.notes" },
  { keys: "← →", label: "shortcuts.circuit" },
  { keys: "Esc", label: "shortcuts.close" },
];

/** List of keyboard shortcuts, opened from the help menu. */
export function ShortcutsDialog({ onClose }: { onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const element = dialog.current;
    if (element && !element.open) element.showModal();
  }, []);
  return (
    <dialog
      ref={dialog}
      className="dialog shortcuts-dialog"
      aria-labelledby="shortcuts-title"
      onClose={onClose}
      onClick={(event) => event.target === dialog.current && dialog.current?.close()}
    >
      <div className="dialog-head">
        <h2 id="shortcuts-title">{t("shortcuts.title")}</h2>
      </div>
      <dl className="shortcuts-list">
        {ROWS.map((row) => (
          <div key={row.label} className="shortcut-row">
            <dt>
              {row.keys.split(" ").map((key) => (
                <kbd key={key}>{key}</kbd>
              ))}
            </dt>
            <dd>{t(row.label)}</dd>
          </div>
        ))}
      </dl>
      <div className="dialog-actions">
        <span className="grow" />
        <button className="btn" autoFocus onClick={() => dialog.current?.close()}>{t("export.close")}</button>
      </div>
    </dialog>
  );
}
