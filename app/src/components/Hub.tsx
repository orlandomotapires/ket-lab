import { useEffect, useRef, useState } from "react";
import { saveTextFile } from "../engine/client";
import type { CatalogSection, LessonProgress } from "../engine/types";
import { t } from "../strings";
import { exportLocalProgress } from "../lib/localProgress";
import { backupFile, lessonKeys, lessonNoteKey } from "../lib/notes";
import { readLastLesson, resumeTarget } from "../lib/resume";
import { useStoredFlag } from "../lib/storedFlag";
import { reviewKey, reviewScore, useStore } from "../state/store";
import { BookIcon, CheckIcon, ChevronRightIcon, ExportIcon, GlossaryIcon, ImportIcon, NoteIcon } from "./icons";

type Status = "done" | "started" | "available" | "soon";

function statusOf(section: CatalogSection, progress: LessonProgress | undefined): Status {
  if (!section.available) return "soon";
  if (progress?.completed) return "done";
  if (progress?.code != null) return "started";
  return "available";
}

/** Lessons, challenges and time remaining of a track (counts only what is already available). */
function trackStats(sections: CatalogSection[], progress: Record<string, LessonProgress>) {
  const available = sections.filter((section) => section.available);
  const lessonsDone = available.filter((section) => progress[section.id]?.completed).length;
  const withChallenge = available.filter((section) => section.has_challenge);
  const challengesDone = withChallenge.filter((section) => progress[`${section.id}:challenge`]?.completed).length;
  const minutesLeft = available
    .filter((section) => !progress[section.id]?.completed)
    .reduce((sum, section) => sum + (section.estimated_minutes ?? 0), 0);
  return { lessons: available.length, lessonsDone, challenges: withChallenge.length, challengesDone, minutesLeft };
}

function formatMinutes(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m === 0 ? `${h} h` : `${h} h ${m} min`;
}

function Meter({ value }: { value: number }) {
  return (
    <div className="meter" role="presentation">
      <span style={{ width: `${Math.round(value * 100)}%` }} />
    </div>
  );
}

export function Hub() {
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

  const sections = catalog.tracks.flatMap((track) => track.sections).filter((section) => section.available);
  const done = sections.filter((section) => progress[section.id]?.completed).length;
  // Where the main button goes: the lesson opened last, or the first one not completed.
  const resume = resumeTarget(catalog.tracks, progress, readLastLesson());
  const next = sections.find((section) => section.id === resume.lessonId);
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
        {/* Fixed side panel: summary, next lesson and track index. */}
        <aside className="hub-side">
          <h1>{t("hub.title")}</h1>
          <p className="hub-subtitle">{t("hub.subtitle")}</p>
          <div className="hub-progress">
            <Meter value={done / sections.length} />
            <span>{t("hub.progress", { done, total: sections.length })}</span>
          </div>
          <div className="hub-actions">
            {next && (
              <button
                className="btn btn-primary hub-next"
                onClick={() => void openLesson(next.id)}
                disabled={offline}
              >
                <span className="hub-next-label">
                  {t(resume.label === "continue" ? "hub.continueShort" : "hub.startShort")}
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
                  </span>
                  <span className="hub-index-count">
                    {trackDone}/{track.sections.length}
                  </span>
                </button>
              );
            })}
          </nav>
          {loadError && <p className="error-text">{loadError}</p>}
          <HubExtras />
        </aside>

        <div className="hub-tracks">

        {catalog.tracks.map((track) => (
          <Track key={track.id} track={track} progress={progress} next={next} offline={offline} action={action} openLesson={openLesson} />
        ))}
        </div>
      </main>
    </div>
  );
}

type TrackData = NonNullable<ReturnType<typeof useStore.getState>["catalog"]>["tracks"][number];

/** One track: its header and the lesson rows. A finished track folds to its header, and the
 *  track that holds the next lesson stays open; the learner's choice is remembered. */
function Track({ track, progress, next, offline, action, openLesson }: {
  track: TrackData;
  progress: Record<string, LessonProgress>;
  next: CatalogSection | undefined;
  offline: boolean;
  action: Record<Status, string>;
  openLesson: (id: string) => Promise<void> | void;
}) {
  const notes = useStore((s) => s.notes);
  const openReview = useStore((s) => s.openReview);
  const stats = trackStats(track.sections, progress);
  const best = reviewScore(progress[reviewKey(track.id)]?.code);
  // The completed mark is for a good score; a lower one shows only the score.
  const reviewPassed = best !== null && best.total > 0 && best.score / best.total >= 0.8;
  const allDone =
    stats.lessons > 0 && stats.lessonsDone === stats.lessons && stats.challengesDone === stats.challenges;
  const holdsNext = Boolean(next && track.sections.some((section) => section.id === next.id));
  const [open, setOpen] = useStoredFlag(`qlp.hub.track.${track.id}`, holdsNext || !allDone);
  const listId = `track-list-${track.id}`;
  return (
    <section id={`track-${track.id}`} className={`track${open ? "" : " is-collapsed"}`} aria-labelledby={`track-title-${track.id}`}>
      <header className="track-head">
        <div>
          <div className="track-eyebrow">
            {t("hub.track", { id: track.id })}
            <span className="pill">{track.level}</span>
          </div>
          <h2 id={`track-title-${track.id}`}>{track.title}</h2>
          {stats.lessons > 0 && (
            <p className="track-stats">
              {t("hub.trackLessons", { done: stats.lessonsDone, total: stats.lessons })}
              {stats.challenges > 0 && ` · ${t("hub.trackChallenges", { done: stats.challengesDone, total: stats.challenges })}`}
              {stats.minutesLeft > 0 && ` · ${t("hub.trackRemaining", { time: formatMinutes(stats.minutesLeft) })}`}
            </p>
          )}
          {allDone && <span className="pill pill-success">{t("hub.trackDone")}</span>}
        </div>
        <button className="btn btn-ghost btn-sm track-toggle" aria-expanded={open} aria-controls={listId} onClick={() => setOpen(!open)}>
          {t(open ? "hub.hideLessons" : "hub.showLessons")}
          <span className="disclosure-caret" aria-hidden="true" />
        </button>
      </header>
      {open && <ol className="section-list" id={listId}>
        {track.sections.map((section) => {
          const status = statusOf(section, progress[section.id]);
          const isNext = section.id === next?.id;
          // The "Challenge" pill says nothing until the lesson is done.
          const challengeProgress = progress[`${section.id}:challenge`];
          const showChallengePill = section.has_challenge && Boolean(progress[section.id]?.completed || challengeProgress?.completed);
          return (
            <li key={section.id}>
              <button
                className={`section-row is-${status}${isNext ? " is-next" : ""}`}
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
                    {notes[lessonNoteKey(section.id)] && <span className="note-dot" role="img" aria-label={t("notes.hasNote")} />}
                  </span>
                  <span className="section-summary">{section.summary}</span>
                  {(section.project || showChallengePill || progress[section.id]?.with_solution) && (
                    <span className="section-tags">
                      {section.project && <span className="pill pill-accent">{t("hub.project")}</span>}
                      {progress[section.id]?.with_solution && <span className="pill">{t("hub.withSolution")}</span>}
                      {showChallengePill && (
                        <span className="pill">
                          {challengeProgress?.completed
                            ? t(challengeProgress.with_solution ? "hub.challengeWithSolution" : "hub.challengeDone")
                            : t("hub.challenge")}
                        </span>
                      )}
                    </span>
                  )}
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
        {track.review && (
          <li>
            <button className={`section-row review-row is-${reviewPassed ? "done" : "available"}`} disabled={offline} onClick={() => void openReview(track.id)}>
              <span className={`section-mark is-${reviewPassed ? "done" : "available"}`} aria-hidden="true">
                {reviewPassed && <CheckIcon size={13} />}
              </span>
              <span className="section-text">
                <span className="section-title">{t("review.row")}</span>
                <span className="section-summary">{t("review.rowNote")}</span>
                {best && (
                  <span className="section-tags">
                    <span className="pill">{t("review.best", { score: best.score, total: best.total })}</span>
                  </span>
                )}
              </span>
              <span className="section-action">
                {t(best ? "review.again" : "review.start")} <ChevronRightIcon />
              </span>
            </button>
          </li>
        )}
      </ol>}
    </section>
  );
}

/** Side panel shortcuts: references and progress copy, in the style of the track index. */
function HubExtras() {
  const notes = useStore((s) => s.notes);
  const noteCount = Object.keys(notes).length;
  const glossaryCount = useStore((s) => s.glossary.length);
  const [backup, setBackup] = useState(false);

  return (
    <nav className="hub-extras" aria-label={t("hub.extras")}>
      <button className="hub-index-item hub-extra" onClick={() => useStore.getState().openReferences()}>
        <span className="hub-index-number" aria-hidden="true"><BookIcon /></span>
        <span className="hub-index-text">
          <span className="hub-index-title">{t("bib.title")}</span>
          <span className="hub-index-level">{t("hub.referencesNote")}</span>
        </span>
      </button>
      <button className="hub-index-item hub-extra" onClick={() => useStore.getState().openGlossary()}>
        <span className="hub-index-number" aria-hidden="true"><GlossaryIcon /></span>
        <span className="hub-index-text">
          <span className="hub-index-title">{t("glossary.title")}</span>
          <span className="hub-index-level">{t("hub.glossaryNote", { count: glossaryCount })}</span>
        </span>
      </button>
      <button className="hub-index-item hub-extra" onClick={() => useStore.getState().openNotesPage()}>
        <span className="hub-index-number" aria-hidden="true"><NoteIcon /></span>
        <span className="hub-index-text">
          <span className="hub-index-title">{t("notes.title")}</span>
          <span className="hub-index-level">{noteCount > 0 ? t("hub.notesCount", { count: noteCount }) : t("hub.notesNote")}</span>
        </span>
      </button>
      <button className="hub-index-item hub-extra" aria-haspopup="dialog" onClick={() => setBackup(true)}>
        <span className="hub-index-number" aria-hidden="true"><ExportIcon /></span>
        <span className="hub-index-text">
          <span className="hub-index-title">{t("hub.backup")}</span>
          <span className="hub-index-level">{t("hub.backupHint")}</span>
        </span>
      </button>
      {backup && <BackupDialog onClose={() => setBackup(false)} />}
    </nav>
  );
}

/** One place for the backup: download a copy of progress and notes, or restore one. */
function BackupDialog({ onClose }: { onClose: () => void }) {
  const catalog = useStore((s) => s.catalog);
  const storage = useStore((s) => s.progressStorage);
  const progress = useStore((s) => s.progress);
  const notes = useStore((s) => s.notes);
  const [status, setStatus] = useState<{ text: string; error: boolean } | null>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => {
    const element = dialog.current;
    if (element && !element.open) element.showModal();
  }, []);

  return (
    <dialog
      ref={dialog}
      className="dialog backup-dialog"
      aria-labelledby="backup-title"
      onClose={onClose}
      onClick={(event) => event.target === dialog.current && dialog.current?.close()}
    >
      <div className="dialog-head">
        <h2 id="backup-title">{t("hub.backup")}</h2>
      </div>
      <p className="muted dialog-note">{storage === "client" ? t("hub.backupNote") : t("hub.backupNoteEngine")}</p>

      <section className="backup-option">
        <div>
          <h3>{t("hub.backupExport")}</h3>
          <p>{t("hub.exportNote")}</p>
        </div>
        <button
          className="btn"
          onClick={() => {
            saveTextFile(backupFile(notes, exportLocalProgress(progress), lessonKeys(catalog)), "quantum-learning-progress.json");
            setStatus({ text: t("hub.backupExported"), error: false });
          }}
        >
          <ExportIcon /> {t("hub.backupExport")}
        </button>
      </section>

      <section className="backup-option">
        <div>
          <h3>{t("hub.backupImport")}</h3>
          <p>{t("hub.importNote")}</p>
        </div>
        <button className="btn" onClick={() => input.current?.click()}>
          <ImportIcon /> {t("hub.backupImport")}
        </button>
        <input
          ref={input}
          type="file"
          accept="application/json,.json"
          hidden
          onChange={async (event) => {
            const file = event.target.files?.[0];
            event.target.value = "";
            if (!file) return;
            try {
              const imported = await useStore.getState().importBackup(await file.text());
              setStatus({ text: t("hub.backupImported", imported), error: false });
            } catch {
              setStatus({ text: t("hub.backupInvalid"), error: true });
            }
          }}
        />
      </section>

      <p className={`backup-status${status?.error ? " is-error" : ""}`} role="status">{status?.text}</p>
      <div className="dialog-actions">
        <span className="grow" />
        <button className="btn" autoFocus onClick={() => dialog.current?.close()}>{t("export.close")}</button>
      </div>
    </dialog>
  );
}
