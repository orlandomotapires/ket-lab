import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { lessonNoteKey } from "../lib/notes";
import { altKey } from "../lib/platform";
import { t } from "../strings";
import { useStore } from "../state/store";
import { toggleTheme, useTheme } from "../theme/theme";
import { ArrowLeftIcon, InfoIcon, LogoMark, MoonIcon, NoteIcon, SunIcon } from "./icons";
import { NOTES_BUTTON_ID } from "./NotesDrawer";
import { ShortcutsDialog } from "./ShortcutsDialog";
import { SearchBox } from "./SearchBox";
import { openTour } from "./Tour";

// The text of the About dialog is only downloaded when it is opened.
const AboutDialog = lazy(() => import("./AboutDialog").then((m) => ({ default: m.AboutDialog })));

export function TopBar() {
  const [about, setAbout] = useState(false);
  const theme = useTheme();
  const view = useStore((s) => s.view);
  const lesson = useStore((s) => s.lesson);
  const catalog = useStore((s) => s.catalog);
  const connection = useStore((s) => s.connection);
  const backToHub = useStore((s) => s.backToHub);
  const notesOpen = useStore((s) => s.notesOpen);
  const hasNote = useStore((s) => Boolean(s.lesson && s.notes[lessonNoteKey(s.lesson.id)]));

  const track = lesson && catalog?.tracks.find((item) => item.id === lesson.track);

  return (
    <header className="topbar">
      <div className="topbar-left">
      {view === "lab" ? (
        <>
          <button className="btn btn-ghost btn-sm" onClick={backToHub}>
            <ArrowLeftIcon /> {t("topbar.tracks")}
          </button>
          <span className="divider" />
          <nav className="crumbs" aria-label={t("topbar.location")}>
            {lesson ? (
              <>
                <span>{track ? track.title : t("hub.track", { id: lesson.track })}</span>
                <span className="crumb-sep">/</span>
                <strong title={`${lesson.id} ${lesson.title}`}>
                  <span className="crumb-id">{lesson.id}</span>
                  {lesson.title}
                </strong>
              </>
            ) : (
              <strong>{t("topbar.sandbox")}</strong>
            )}
          </nav>
        </>
      ) : (
        <div className="brand">
          <LogoMark />
          {t("app.name")}
        </div>
      )}
      </div>
      <SearchBox />
      <div className="topbar-right">
      {/* Only shows up when there is something to resolve; with the engine active, it takes no space in the bar. */}
      {connection !== "open" && (
        <span className={`status-chip is-${connection}`} role="status" title={t("topbar.engineTitle")}>
          <span className="status-dot" aria-hidden="true" />
          {t(`topbar.engine.${connection}`)}
        </span>
      )}
      {view === "lab" && lesson && (
        <button
          id={NOTES_BUTTON_ID}
          className="btn btn-ghost btn-sm notes-button"
          aria-expanded={notesOpen}
          aria-controls="notes-drawer"
          title={t("notes.buttonHint", { key: `${altKey}+N` })}
          onClick={() => useStore.getState().setNotesOpen(!notesOpen)}
        >
          <NoteIcon />
          {t("notes.title")}
          {hasNote && <span className="note-dot" role="img" aria-label={t("notes.hasNote")} />}
        </button>
      )}
      {view === "lab" && <HelpMenu guide={Boolean(lesson)} />}
      <button
        className="btn btn-ghost btn-icon btn-sm"
        onClick={() => setAbout(true)}
        aria-label={t("about.open")}
        title={t("about.open")}
      >
        <InfoIcon />
      </button>
      <button
        className="btn btn-ghost btn-icon btn-sm"
        onClick={toggleTheme}
        aria-label={theme === "dark" ? t("topbar.toLight") : t("topbar.toDark")}
        title={theme === "dark" ? t("topbar.light") : t("topbar.dark")}
      >
        {theme === "dark" ? <SunIcon /> : <MoonIcon />}
      </button>
      </div>
      {about && (
        <Suspense fallback={null}>
          <AboutDialog onClose={() => setAbout(false)} />
        </Suspense>
      )}
    </header>
  );
}

/** The "?" button: the first-lesson guide and the list of keyboard shortcuts. */
function HelpMenu({ guide }: { guide: boolean }) {
  const [open, setOpen] = useState(false);
  const [shortcuts, setShortcuts] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const onPointer = (event: PointerEvent) => {
      if (root.current && !root.current.contains(event.target as Node)) setOpen(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("pointerdown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);
  return (
    <div className="more-menu help-menu" ref={root}>
      <button
        className="btn btn-ghost btn-icon btn-sm"
        aria-haspopup="true"
        aria-expanded={open}
        aria-label={t("help.open")}
        title={t("help.open")}
        onClick={() => setOpen(!open)}
      >
        ?
      </button>
      {open && (
        <div className="more-popover help-popover" role="group" aria-label={t("help.open")}>
          {guide && (
            <button
              className="more-item"
              autoFocus
              onClick={() => {
                setOpen(false);
                openTour();
              }}
            >
              {t("tour.open")}
            </button>
          )}
          <button
            className="more-item"
            autoFocus={!guide}
            onClick={() => {
              setOpen(false);
              setShortcuts(true);
            }}
          >
            {t("help.shortcuts")}
          </button>
        </div>
      )}
      {shortcuts && <ShortcutsDialog onClose={() => setShortcuts(false)} />}
    </div>
  );
}
