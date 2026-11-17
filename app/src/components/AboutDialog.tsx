import { useEffect, useRef } from "react";
import { t, type MessageKey } from "../strings";
import { useStore } from "../state/store";

const PROJECTS: MessageKey[] = ["about.after.1", "about.after.2", "about.after.3", "about.after.4", "about.after.5"];

function duration(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest >= 10 ? `${hours} h ${rest} min` : `${hours} h`;
}

/** What the platform is, who it is for and what it covers. Opened from the "i" button. */
export function AboutDialog({ onClose }: { onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const catalog = useStore((s) => s.catalog);
  const hosted = useStore((s) => s.progressStorage === "client");
  useEffect(() => {
    const element = dialog.current;
    if (element && !element.open) element.showModal();
  }, []);

  const tracks = catalog?.tracks ?? [];
  const sections = tracks.flatMap((track) => track.sections);
  const minutes = sections.reduce((sum, section) => sum + (section.estimated_minutes ?? 0), 0);
  const close = () => dialog.current?.close();

  return (
    <dialog
      ref={dialog}
      className="dialog about-dialog"
      aria-labelledby="about-title"
      onClose={onClose}
      onClick={(event) => event.target === dialog.current && close()}
    >
      <div className="dialog-head">
        <div>
          <h2 id="about-title">{t("about.title")}</h2>
          <p className="about-subtitle">{t("about.subtitle")}</p>
        </div>
      </div>
      <div className="about-body" tabIndex={0}>
        <p className="about-lead">{t("about.lead")}</p>

        <h3>{t("about.what.title")}</h3>
        <p>{t("about.what.body", { lessons: sections.length || 48, hours: Math.round(minutes / 60) || 22 })}</p>

        <h3>{t("about.who.title")}</h3>
        <p>{t("about.who.body")}</p>

        <h3>{t("about.how.title")}</h3>
        <p>{t("about.how.body")}</p>

        {tracks.length > 0 && (
          <>
            <h3>{t("about.tracks.title")}</h3>
            <ol className="about-tracks">
              {tracks.map((track) => {
                const key = `about.track.${track.id}` as MessageKey;
                const time = track.sections.reduce((sum, section) => sum + (section.estimated_minutes ?? 0), 0);
                return (
                  <li key={track.id}>
                    <span className="about-track-number" aria-hidden="true">{track.id}</span>
                    <div>
                      <strong>{track.title}</strong>
                      <span className="about-track-meta">
                        {t("about.tracks.meta", { level: track.level, lessons: track.sections.length, time: duration(time) })}
                      </span>
                      {track.id >= 0 && track.id <= 6 && <p>{t(key)}</p>}
                    </div>
                  </li>
                );
              })}
            </ol>
          </>
        )}

        <h3>{t("about.after.title")}</h3>
        <p>{t("about.after.body")}</p>
        <ul className="about-list">
          {PROJECTS.map((key) => (
            <li key={key}>{t(key)}</li>
          ))}
        </ul>
        <p>{t("about.after.lab")}</p>

        <h3>{t("about.sources.title")}</h3>
        <p>{t("about.sources.body")}</p>
        <button
          className="link small"
          onClick={() => {
            close();
            useStore.getState().openReferences();
          }}
        >
          {t("about.sources.link")}
        </button>

        <h3>{t("about.limits.title")}</h3>
        <p>{t("about.limits.body")}</p>

        <h3>{t("about.data.title")}</h3>
        <p>{t(hosted ? "about.data.hosted" : "about.data.local")}</p>
      </div>
      <div className="dialog-actions">
        <span className="grow" />
        <button className="btn" autoFocus onClick={close}>{t("export.close")}</button>
      </div>
    </dialog>
  );
}
