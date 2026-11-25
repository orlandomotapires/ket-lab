import { useMemo, useRef } from "react";
import { GENERAL_NOTE, lessonNoteKey, lessonOfKey } from "../lib/notes";
import { altKey } from "../lib/platform";
import { t } from "../strings";
import { useStore } from "../state/store";
import { ArrowLeftIcon } from "./icons";
import { NoteField, NoteStatus } from "./NoteField";
import { NoteWithImages } from "./NoteImages";

/** Every note in one place: the general note on top, then the lesson notes by track. */
export function NotesPage() {
  const catalog = useStore((s) => s.catalog);
  const notes = useStore((s) => s.notes);
  const noteImages = useStore((s) => s.noteImages);
  const { backToHub, openLesson } = useStore.getState();
  // A note that is emptied stays on the page until the learner leaves, so it can be typed again.
  const seen = useRef(new Set<string>());
  for (const key of Object.keys(notes)) seen.current.add(key);
  // A note with only images is a note too.
  for (const key of Object.keys(noteImages)) seen.current.add(key);

  const groups = useMemo(() => {
    const known = new Set<string>();
    const result = (catalog?.tracks ?? [])
      .map((track) => ({
        id: String(track.id),
        title: track.title,
        items: track.sections
          .filter((section) => seen.current.has(lessonNoteKey(section.id)))
          .map((section) => {
            known.add(lessonNoteKey(section.id));
            return { key: lessonNoteKey(section.id), lessonId: section.id, title: section.title };
          }),
      }))
      .filter((group) => group.items.length > 0);
    // Notes of lessons that no longer exist (renumbered): kept, so nothing is lost.
    const orphans = [...seen.current]
      .filter((key) => key !== GENERAL_NOTE && !known.has(key))
      .map((key) => ({ key, lessonId: lessonOfKey(key) ?? key, title: "" }));
    return orphans.length ? [...result, { id: "other", title: t("notes.other"), items: orphans }] : result;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [catalog, notes, noteImages]);

  const hasLessonNotes = groups.length > 0;
  return (
    <div className="hub-scroll">
      <main className="notes-page">
        <button className="btn btn-sm btn-back" onClick={backToHub}><ArrowLeftIcon /> {t("notes.back")}</button>
        <div className="notes-page-head">
          <h1>{t("notes.title")}</h1>
          <NoteStatus text={{ saving: t("notes.saving"), saved: t("notes.saved"), error: t("notes.failed") }} />
        </div>
        <p className="muted">{t("notes.intro")}</p>

        <section className="note-card">
          <h2 className="note-card-title">{t("notes.general")}</h2>
          <NoteWithImages noteKey={GENERAL_NOTE} label={t("notes.general")}>
            <NoteField
              noteKey={GENERAL_NOTE}
              label={t("notes.general")}
              placeholder={t("notes.generalPlaceholder")}
              className="is-large"
            />
          </NoteWithImages>
        </section>

        {!hasLessonNotes && <p className="notes-empty">{t("notes.empty", { key: `${altKey}+N` })}</p>}
        {groups.map((group) => (
          <section key={group.id} aria-labelledby={`notes-track-${group.id}`}>
            <h2 id={`notes-track-${group.id}`} className="notes-track">
              {group.id === "other" ? group.title : `${t("hub.track", { id: group.id })}: ${group.title}`}
            </h2>
            {group.items.map((item) => (
              <article key={item.key} className="note-card">
                <header className="note-card-head">
                  <h3 className="note-card-title">
                    <span className="section-id">{item.lessonId}</span>
                    {item.title}
                  </h3>
                  {item.title && (
                    <button className="link small" onClick={() => void openLesson(item.lessonId)}>
                      {t("notes.openLesson")}
                    </button>
                  )}
                </header>
                <NoteWithImages noteKey={item.key} label={item.lessonId}>
                  <NoteField
                    noteKey={item.key}
                    label={t("notes.fieldLabel", { id: item.lessonId, title: item.title })}
                    placeholder={t("notes.placeholder")}
                  />
                </NoteWithImages>
              </article>
            ))}
          </section>
        ))}
      </main>
    </div>
  );
}
