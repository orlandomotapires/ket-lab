import type { LessonProgress, Note, Notes } from "../engine/types";
import { importLocalProgress, loadLocalProgress } from "../lib/localProgress";
import { loadLocalNotes, mergeNotes, NOTE_LIMIT, saveLocalNotes } from "../lib/notes";
import { engine } from "./engine";
import type { Get, NotesSlice, Set } from "./types";

const SAVE_DEBOUNCE_MS = 1000;
const SAVED_SHOWN_MS = 2500;

/** Notes: held in memory, saved after a pause in typing, in the engine or in this browser. */
export function notesSlice(set: Set, get: Get): NotesSlice {
  const timers = new Map<string, number>();
  let savedTimer: number | undefined;

  function markSaved(): void {
    set({ notesStatus: "saved" });
    window.clearTimeout(savedTimer);
    savedTimer = window.setTimeout(() => {
      if (timers.size === 0) set({ notesStatus: "idle" });
    }, SAVED_SHOWN_MS);
  }

  async function persist(key: string): Promise<void> {
    timers.delete(key);
    const note: Note | undefined = get().notes[key];
    if (get().notesStorage === "client") {
      saveLocalNotes(get().notes);
      if (timers.size === 0) markSaved();
      return;
    }
    try {
      const response = note
        ? await engine().call<{ note: Note | null }>("notes.save", { key, body: note.body })
        : await engine().call("notes.delete", { key });
      if (!response.ok) {
        // Hosted engine: the notes stay in the browser from now on.
        if (response.error?.kind === "unavailable") {
          set({ notesStorage: "client" });
          saveLocalNotes(get().notes);
        } else {
          set({ notesStatus: "error" });
          return;
        }
      }
      if (timers.size === 0) markSaved();
    } catch {
      set({ notesStatus: "error" }); // connection notice already visible
    }
  }

  return {
    notes: {},
    notesStorage: "engine",
    notesStatus: "idle",
    notesOpen: false,

    async loadNotes(storage) {
      set({ notesStorage: storage });
      if (storage === "engine") {
        try {
          const response = await engine().call<{ notes: Notes }>("notes.list");
          if (response.ok) {
            if (timers.size === 0) set({ notes: response.notes });
            return;
          }
          if (response.error?.kind !== "unavailable") return;
          set({ notesStorage: "client" });
        } catch {
          return;
        }
      }
      if (timers.size === 0) set({ notes: loadLocalNotes() });
    },

    setNote(key, body) {
      const text = body.slice(0, NOTE_LIMIT);
      const notes = { ...get().notes };
      if (text.trim()) notes[key] = { body: text, updated_at: new Date().toISOString() };
      else delete notes[key];
      set({ notes, notesStatus: "saving" });
      window.clearTimeout(timers.get(key));
      timers.set(key, window.setTimeout(() => void persist(key), SAVE_DEBOUNCE_MS));
    },

    flushNotes() {
      for (const [key, timer] of [...timers]) {
        window.clearTimeout(timer);
        void persist(key);
      }
    },

    setNotesOpen(open) {
      if (!open) get().flushNotes();
      set({ notesOpen: open });
    },

    async importBackup(text) {
      let data: { notes?: Notes } | null = null;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error("invalid file");
      }
      if (get().progressStorage === "engine") {
        const response = await engine().call<{
          progress: Record<string, LessonProgress>;
          notes: Notes;
          imported: { lessons: number; notes: number };
        }>("progress.import", { data });
        if (response.ok) {
          set({ progress: response.progress, notes: response.notes ?? get().notes });
          return response.imported;
        }
        if (response.error?.kind !== "unavailable") throw new Error(response.error?.message ?? "invalid file");
        set({ progressStorage: "client" });
      }
      const lessons = importLocalProgress(text);
      const incoming = data?.notes && typeof data.notes === "object" ? data.notes : {};
      const merged = mergeNotes(loadLocalNotes(), incoming);
      saveLocalNotes(merged);
      set({ progress: loadLocalProgress(), notes: merged, notesStorage: "client" });
      return { lessons, notes: Object.keys(incoming).length };
    },
  };
}

/** Writes pending notes when the page is hidden or closed. */
export function flushNotesOnHide(get: Get): void {
  if (typeof window === "undefined") return;
  const flush = () => get().flushNotes();
  window.addEventListener("pagehide", flush);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") flush();
  });
}
