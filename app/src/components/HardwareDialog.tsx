import { useEffect, useRef, useState } from "react";
import { t } from "../strings";
import { useStore, type HardwareJob } from "../state/store";

const KEY_STORAGE = "qlp.ibm.key";
const JOB_STORAGE = "qlp.ibm.job";
const POLL_MS = 15_000;
const SHOTS = 1024;

function read(key: string): string {
  try {
    return localStorage.getItem(key) ?? "";
  } catch {
    return "";
  }
}

function write(key: string, value: string | null): void {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    // no storage: valid only for this session
  }
}

/** Circuit panel button: only shows up with the local engine and the hardware package installed. */
export function HardwareButton() {
  const available = useStore((s) => s.hardwareAvailable);
  const offline = useStore((s) => s.connection !== "open");
  const [open, setOpen] = useState(false);
  if (!available) return null;
  return (
    <>
      <button className="btn btn-ghost btn-sm" onClick={() => setOpen(true)} disabled={offline} title={t("hw.hint")}>
        {t("hw.button")}
      </button>
      {open && <HardwareDialog onClose={() => setOpen(false)} />}
    </>
  );
}

interface Saved {
  job_id: string;
  backend: string;
  instance: string;
}

function HardwareDialog({ onClose }: { onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const { submitHardware, hardwareStatus, simulateCounts } = useStore.getState();
  const [token, setToken] = useState(read(KEY_STORAGE));
  const [remember, setRemember] = useState(read(KEY_STORAGE) !== "");
  const [instance, setInstance] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [job, setJob] = useState<HardwareJob | null>(null);
  const [saved, setSaved] = useState<Saved | null>(() => {
    try {
      return JSON.parse(read(JOB_STORAGE) || "null");
    } catch {
      return null;
    }
  });
  const [simulated, setSimulated] = useState<Record<string, number> | null>(null);

  useEffect(() => {
    if (dialog.current && !dialog.current.open) dialog.current.showModal();
  }, []);

  // Follows the saved job until it finishes (a real computer's queue can take minutes).
  useEffect(() => {
    if (!saved || !token) return;
    let stopped = false;
    const poll = async () => {
      const response = await hardwareStatus({ jobId: saved.job_id, token, instance: saved.instance }).catch(() => null);
      if (stopped || !response) return;
      if (!response.ok) {
        setError(response.error?.message ?? t("hw.failed"));
        return;
      }
      setJob(response);
      if (response.status === "DONE" || response.status === "ERROR" || response.status === "CANCELLED") return;
      timer = window.setTimeout(poll, POLL_MS);
    };
    let timer = window.setTimeout(poll, 0);
    return () => {
      stopped = true;
      window.clearTimeout(timer);
    };
  }, [saved, token, hardwareStatus]);

  useEffect(() => {
    if (job?.status !== "DONE") return;
    void simulateCounts(SHOTS).then((response) => response.ok && setSimulated(response.counts));
  }, [job?.status, simulateCounts]);

  async function submit() {
    setBusy(true);
    setError(null);
    setJob(null);
    setSimulated(null);
    write(KEY_STORAGE, remember ? token : null);
    const response = await submitHardware({ token, instance, shots: SHOTS }).catch(() => null);
    setBusy(false);
    if (!response || !response.ok) {
      setError(response?.error?.message ?? t("hw.failed"));
      return;
    }
    const next = { job_id: response.job_id, backend: response.backend ?? "", instance };
    write(JOB_STORAGE, JSON.stringify(next));
    setSaved(next);
  }

  function forget() {
    write(JOB_STORAGE, null);
    setSaved(null);
    setJob(null);
    setSimulated(null);
  }

  const done = job?.status === "DONE" && job.counts;
  return (
    <dialog
      ref={dialog}
      className="dialog hardware-dialog"
      aria-labelledby="hw-title"
      onClose={onClose}
      onClick={(event) => event.target === dialog.current && dialog.current?.close()}
    >
      <div className="dialog-head">
        <h2 id="hw-title">{t("hw.title")}</h2>
      </div>
      <p className="muted small dialog-note">{t("hw.note")}</p>

      {!saved && (
        <form
          className="hw-form"
          onSubmit={(event) => {
            event.preventDefault();
            void submit();
          }}
        >
          <details className="hw-about">
            <summary>{t("hw.aboutKey")}</summary>
            <p className="muted small">{t("hw.keyNote")}</p>
          </details>
          <label>
            <span>{t("hw.key")}</span>
            <input type="password" autoComplete="off" value={token} onChange={(event) => setToken(event.target.value)} required />
          </label>
          <label>
            <span>{t("hw.instance")}</span>
            <input type="text" value={instance} placeholder={t("hw.instancePlaceholder")} onChange={(event) => setInstance(event.target.value)} />
          </label>
          <label className="check">
            <input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} />
            {t("hw.remember")}
          </label>
          <div className="dialog-actions">
            <span className="grow" />
            <button type="button" className="btn btn-ghost" onClick={() => dialog.current?.close()}>{t("export.close")}</button>
            <button type="submit" className="btn btn-primary" disabled={busy || !token}>
              {busy ? t("hw.submitting") : t("hw.submit", { shots: SHOTS })}
            </button>
          </div>
        </form>
      )}

      {saved && (
        <div className="hw-job">
          <p className="small">
            {t("hw.job", { id: saved.job_id, backend: saved.backend || "…" })}{" "}
            <strong>{job?.status ? t("hw.status", { status: job.status.toLowerCase() }) : t("hw.checking")}</strong>
          </p>
          {!token && <p className="muted small">{t("hw.needKey")}</p>}
          {done && <Comparison hardware={job.counts!} simulated={simulated} />}
          <div className="dialog-actions">
            <button className="btn btn-ghost" onClick={forget}>{t("hw.newJob")}</button>
            <span className="grow" />
            <button className="btn" onClick={() => dialog.current?.close()}>{t("export.close")}</button>
          </div>
        </div>
      )}
      {error && <p className="notice notice-error">{error}</p>}
    </dialog>
  );
}

/** Frequencies measured on hardware next to the simulated ones, per outcome. */
function Comparison({ hardware, simulated }: { hardware: Record<string, number>; simulated: Record<string, number> | null }) {
  const outcomes = [...new Set([...Object.keys(hardware), ...Object.keys(simulated ?? {})])].sort();
  const total = (counts: Record<string, number>) => Object.values(counts).reduce((a, b) => a + b, 0) || 1;
  const hw = total(hardware);
  const sim = simulated ? total(simulated) : 1;
  return (
    <table className="readout hw-compare">
      <thead>
        <tr>
          <th scope="col">{t("probs.state")}</th>
          <th scope="col">{t("hw.simulated")}</th>
          <th scope="col">{t("hw.measured")}</th>
        </tr>
      </thead>
      <tbody>
        {outcomes.map((outcome) => (
          <tr key={outcome}>
            <th scope="row" className="mono">|{outcome}⟩</th>
            <td className="num mono">{simulated ? `${((100 * (simulated[outcome] ?? 0)) / sim).toFixed(1)}%` : "…"}</td>
            <td className="num mono">{((100 * (hardware[outcome] ?? 0)) / hw).toFixed(1)}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
