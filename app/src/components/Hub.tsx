import type { CatalogSection, LessonProgress } from "../engine/types";
import { t, useLocale } from "../i18n";
import { useStore } from "../state/store";
import { CheckIcon, ChevronRightIcon } from "./icons";

type Status = "done" | "started" | "available" | "soon";

function statusOf(section: CatalogSection, progress: LessonProgress | undefined): Status {
  if (!section.available) return "soon";
  if (progress?.completed) return "done";
  if (progress?.code != null) return "started";
  return "available";
}

function Meter({ value }: { value: number }) {
  return (
    <div className="meter" role="presentation">
      <span style={{ width: `${Math.round(value * 100)}%` }} />
    </div>
  );
}

export function Hub() {
  useLocale();
  const catalog = useStore((s) => s.catalog);
  const progress = useStore((s) => s.progress);
  const loadError = useStore((s) => s.loadError);
  const connection = useStore((s) => s.connection);
  const openLesson = useStore((s) => s.openLesson);
  const openSandbox = useStore((s) => s.openSandbox);

  if (!catalog) {
    return (
      <div className="hub-scroll">
        <main className="hub">
          <p className="muted">{loadError ?? t("hub.loading")}</p>
        </main>
      </div>
    );
  }

  const sections = catalog.tracks.flatMap((track) => track.sections);
  const done = sections.filter((section) => progress[section.id]?.completed).length;
  // Próxima lição sugerida: a primeira disponível ainda não concluída.
  const next = sections.find((section) => section.available && !progress[section.id]?.completed);
  const offline = connection !== "open";
  const action: Record<Status, string> = {
    done: t("hub.action.done"),
    started: t("hub.action.started"),
    available: t("hub.action.available"),
    soon: "",
  };

  return (
    <div className="hub-scroll">
      <main className="hub">
        {/* Painel lateral fixo: resumo, próxima lição e índice das trilhas. */}
        <aside className="hub-side">
          <h1>{t("hub.title")}</h1>
          <p className="hub-subtitle">{t("hub.subtitle")}</p>
          <div className="hub-progress">
            <Meter value={done / sections.length} />
            <span>{t("hub.progress", { done, total: sections.length })}</span>
          </div>
          <div className="hub-actions">
            {next && (
              <button className="btn btn-primary hub-next" onClick={() => void openLesson(next.id)} disabled={offline}>
                <span className="hub-next-label">
                  {t(progress[next.id]?.code != null || done > 0 ? "hub.continueShort" : "hub.startShort")}
                </span>
                <span className="hub-next-title">
                  {next.id} {next.title}
                </span>
              </button>
            )}
            <button className="btn" onClick={openSandbox} disabled={offline}>
              {t("hub.sandbox")}
            </button>
          </div>
          <nav className="hub-index" aria-label={t("topbar.tracks")}>
            {catalog.tracks.map((track) => {
              const trackDone = track.sections.filter((section) => progress[section.id]?.completed).length;
              return (
                <button
                  key={track.id}
                  className="hub-index-item"
                  onClick={() => document.getElementById(`track-${track.id}`)?.scrollIntoView({ behavior: "smooth", block: "start" })}
                >
                  <span className="hub-index-number">{track.id}</span>
                  <span className="hub-index-text">
                    <span className="hub-index-title">{track.title}</span>
                    <span className="hub-index-level">{track.level}</span>
                  </span>
                  <span className="hub-index-count">
                    {trackDone}/{track.sections.length}
                  </span>
                </button>
              );
            })}
          </nav>
          {loadError && <p className="error-text">{loadError}</p>}
        </aside>

        <div className="hub-tracks">

        {catalog.tracks.map((track) => {
          const trackDone = track.sections.filter((section) => progress[section.id]?.completed).length;
          return (
            <section key={track.id} id={`track-${track.id}`} className="track" aria-labelledby={`track-title-${track.id}`}>
              <header className="track-head">
                <div>
                  <div className="track-eyebrow">
                    {t("hub.track", { id: track.id })}
                    <span className="pill">{track.level}</span>
                  </div>
                  <h2 id={`track-title-${track.id}`}>{track.title}</h2>
                </div>
                <div className="track-progress">
                  <Meter value={trackDone / track.sections.length} />
                  {trackDone}/{track.sections.length}
                </div>
              </header>
              <ol className="section-list">
                {track.sections.map((section) => {
                  const status = statusOf(section, progress[section.id]);
                  return (
                    <li key={section.id}>
                      <button
                        className="section-row"
                        disabled={status === "soon" || offline}
                        onClick={() => void openLesson(section.id)}
                      >
                        <span className={`section-mark is-${status}`} aria-hidden="true">
                          {status === "done" && <CheckIcon size={13} />}
                        </span>
                        <span className="section-text">
                          <span className="section-title">
                            <span className="section-id">{section.id}</span>
                            {section.title}
                          </span>
                          <span className="section-summary">{section.summary}</span>
                        </span>
                        {status === "soon" ? (
                          <span className="pill">{t("hub.soon")}</span>
                        ) : (
                          <span className="section-action">
                            {action[status]} <ChevronRightIcon />
                          </span>
                        )}
                      </button>
                    </li>
                  );
                })}
              </ol>
            </section>
          );
        })}
        </div>
      </main>
    </div>
  );
}
