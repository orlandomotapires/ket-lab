import type { LessonProgress, Note, Notes } from "../engine/types";
import { importLocalProgress, loadLocalProgress } from "../lib/localProgress";
import { loadLocalNotes, mergeNotes, NOTE_LIMIT, saveLocalNotes } from "../lib/notes";
import {
  base64ToBlob,
  blobToBase64,
  byNote,
  deleteLocalImage,
  getLocalImage,
  listLocalImages,
  MAX_IMAGES_PER_NOTE,
  newImageId,
  prepareImage,
  putLocalImage,
  readBackupImages,
  type NoteImage,
  type NoteImageData,
} from "../lib/noteImages";
import { engine } from "./engine";
import type { Get, NotesSlice, Set } from "./types";

const SAVE_DEBOUNCE_MS = 1000;
const SAVED_SHOWN_MS = 2500;

/** Notes: held in memory, saved after a pause in typing, in the engine or in this browser. */
export function notesSlice(set: Set, get: Get): NotesSlice {
  const timers = new Map<string, number>();
  let savedTimer: number | undefined;
  // Images live with the notes; an engine that does not keep them (hosted, or older) leaves them in the browser.
  let imagesInBrowser = false;
  const urls = new Map<string, string>();

  async function fetchImage(id: string): Promise<Blob | null> {
    if (imagesInBrowser) return getLocalImage(id);
    const response = await engine().call<{ image: NoteImageData | null }>("notes.image.get", { image_id: id });
    return response.ok && response.image ? base64ToBlob(response.image.data, response.image.mime) : null;
  }

  /** Stores one image (new, or from a backup with its own id). */
  async function storeImage(image: Omit<NoteImageData, "data"> & { blob: Blob }): Promise<NoteImage | null> {
    if (imagesInBrowser) return putLocalImage(image);
    const response = await engine().call<{ image: NoteImage }>("notes.image.save", {
      key: image.key, mime: image.mime, data: await blobToBase64(image.blob), image_id: image.id, created_at: image.created_at,
    });
    return response.ok ? response.image : null;
  }

  function addToState(image: NoteImage): void {
    const all = { ...get().noteImages };
    const list = all[image.key] ?? [];
    if (list.some((item) => item.id === image.id)) return;
    all[image.key] = [...list, image];
    set({ noteImages: all });
  }

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

  /** Progress and notes of a backup file, in the engine or in this browser. */
  async function importProgressAndNotes(data: { notes?: Notes } | null, text: string): Promise<{ lessons: number; notes: number }> {
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
    imagesInBrowser = true;
    return { lessons, notes: Object.keys(incoming).length };
  }


  return {
    notes: {},
    notesStorage: "engine",
    notesStatus: "idle",
    notesOpen: false,
    noteImages: {},

    async loadNotes(storage) {
      set({ notesStorage: storage });
      void get().loadNoteImages();
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

    async loadNoteImages() {
      imagesInBrowser = get().notesStorage === "client";
      if (!imagesInBrowser) {
        try {
          const response = await engine().call<{ images: NoteImage[] }>("notes.images");
          if (response.ok) {
            set({ noteImages: byNote(response.images) });
            return;
          }
          // Hosted engine, or one from before note images: they stay in the browser.
          if (response.error?.kind !== "unavailable" && response.error?.kind !== "protocol") return;
        } catch {
          return;
        }
        imagesInBrowser = true;
      }
      set({ noteImages: byNote(await listLocalImages()) });
    },

    async addNoteImage(key, file) {
      if ((get().noteImages[key]?.length ?? 0) >= MAX_IMAGES_PER_NOTE) return "full";
      const prepared = await prepareImage(file);
      if (!prepared) return "invalid";
      try {
        const image = await storeImage({ id: newImageId(), key, mime: prepared.mime, blob: prepared.blob, created_at: new Date().toISOString() });
        if (!image) return "error";
        urls.set(image.id, URL.createObjectURL(prepared.blob));
        addToState(image);
        return "ok";
      } catch {
        return "error";
      }
    },

    async removeNoteImage(id) {
      const all: Record<string, NoteImage[]> = {};
      for (const [key, list] of Object.entries(get().noteImages)) {
        const kept = list.filter((image) => image.id !== id);
        if (kept.length) all[key] = kept;
      }
      set({ noteImages: all });
      const url = urls.get(id);
      if (url) URL.revokeObjectURL(url);
      urls.delete(id);
      try {
        if (imagesInBrowser) await deleteLocalImage(id);
        else await engine().call("notes.image.delete", { image_id: id });
      } catch {
        // connection notice already visible
      }
    },

    async noteImageUrl(id) {
      const known = urls.get(id);
      if (known) return known;
      try {
        const blob = await fetchImage(id);
        if (!blob) return null;
        const url = URL.createObjectURL(blob);
        urls.set(id, url);
        return url;
      } catch {
        return null;
      }
    },

    async exportNoteImages() {
      const images = Object.values(get().noteImages).flat();
      const out: NoteImageData[] = [];
      for (const image of images) {
        const blob = await fetchImage(image.id).catch(() => null);
        if (blob) out.push({ id: image.id, key: image.key, mime: image.mime, created_at: image.created_at, data: await blobToBase64(blob) });
      }
      return out;
    },

    setNotesOpen(open) {
      if (!open) get().flushNotes();
      set({ notesOpen: open });
    },

    async importBackup(text) {
      let data: { notes?: Notes; note_images?: unknown } | null = null;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error("invalid file");
      }
      // Images go one by one after the rest (a single message would be too big for the engine).
      const images = readBackupImages(data?.note_images);
      if (data && typeof data === "object") delete data.note_images;
      const imported = await importProgressAndNotes(data, text);
      for (const image of images) {
        try {
          const stored = await storeImage({ ...image, blob: base64ToBlob(image.data, image.mime) });
          if (stored) addToState(stored);
        } catch {
          // A broken or refused image does not stop the others.
        }
      }
      return imported;
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
