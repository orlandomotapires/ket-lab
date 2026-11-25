import { useEffect, useRef } from "react";
import { lessonNoteKey } from "../lib/notes";
import { t } from "../strings";
import { useStore } from "../state/store";
import { NoteField, NoteStatus } from "./NoteField";
import { NoteWithImages } from "./NoteImages";

export const NOTES_BUTTON_ID = "notes-button";

/** Narrow drawer with the note of the open lesson (a sheet at the bottom on small screens). */
export function NotesDrawer() {
  const open = useStore((s) => s.notesOpen);
  const lesson = useStore((s) => s.lesson);
  if (!open || !lesson) return null;
  return <Drawer lessonId={lesson.id} title={lesson.title} />;
}

function Drawer({ lessonId, title }: { lessonId: string; title: string }) {
  const field = useRef<HTMLTextAreaElement>(null);
  useEffect(() => {
    field.current?.focus();
    return () => {
      // Closed from inside the drawer: focus goes back to the button that opened it.
      if (document.activeElement === document.body || document.activeElement === null) {
        document.getElementById(NOTES_BUTTON_ID)?.focus();
      }
    };
  }, []);
  return (
    <aside
      id="notes-drawer"
      className="panel notes-drawer"
      aria-label={t("notes.drawerAria")}
      onKeyDown={(event) => {
        if (event.key === "Escape") {
          event.stopPropagation();
          useStore.getState().setNotesOpen(false);
        }
      }}
    >
      <div className="panel-head">
        <h2>{t("notes.title")}</h2>
        <span className="notes-lesson">{lessonId}</span>
        <span className="grow" />
        <NoteStatus text={{ saving: t("notes.saving"), saved: t("notes.saved"), error: t("notes.failed") }} />
        <button className="btn btn-ghost btn-sm" onClick={() => useStore.getState().setNotesOpen(false)}>
          {t("notes.close")}
        </button>
      </div>
      <div className="notes-body">
        <NoteWithImages key={lessonId} noteKey={lessonNoteKey(lessonId)} label={lessonId} className="is-drawer">
          <NoteField
            ref={field}
            noteKey={lessonNoteKey(lessonId)}
            label={t("notes.fieldLabel", { id: lessonId, title })}
            placeholder={t("notes.placeholder")}
            className="is-drawer"
          />
        </NoteWithImages>
      </div>
    </aside>
  );
}
