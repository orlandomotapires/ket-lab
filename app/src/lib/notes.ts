import type { Note, NoteHit, Notes } from "../engine/types";

/** Key of the free note. Lesson notes use "lesson:<id>". */
export const GENERAL_NOTE = "general";
const KEY = "ket-lab.notes.v1";
/** The engine refuses bigger notes (64 KB); the text box stops a bit earlier. */
export const NOTE_LIMIT = 60_000;

export function lessonNoteKey(lessonId: string): string {
  return `lesson:${lessonId}`;
}

/** Lesson id of a note key, or null for the general note. */
export function lessonOfKey(key: string): string | null {
  return key.startsWith("lesson:") ? key.slice("lesson:".length) : null;
}

function clean(raw: unknown): Notes {
  const notes: Notes = {};
  if (!raw || typeof raw !== "object") return notes;
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    const note = value as Partial<Note> | null;
    if (note && typeof note.body === "string" && note.body.trim()) {
      notes[key] = { body: note.body, updated_at: typeof note.updated_at === "string" ? note.updated_at : "" };
    }
  }
  return notes;
}

/** Notes kept in this browser (hosted engine, or storage the engine cannot provide). */
export function loadLocalNotes(): Notes {
  try {
    return clean(JSON.parse(localStorage.getItem(KEY) ?? "{}"));
  } catch {
    return {};
  }
}

export function saveLocalNotes(notes: Notes): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(notes));
  } catch {
    // Storage full or blocked: notes only last for this session.
  }
}

/** Same rule as the engine: when both sides have text, both are kept. */
export function mergeNotes(ours: Notes, theirs: Notes): Notes {
  const merged: Notes = { ...ours };
  for (const [key, note] of Object.entries(clean(theirs))) {
    const mine = merged[key];
    if (!mine) merged[key] = note;
    else if (mine.body.trim() === note.body.trim()) continue;
    else merged[key] = { body: `${mine.body}\n\n--- imported ---\n${note.body}`, updated_at: mine.updated_at > note.updated_at ? mine.updated_at : note.updated_at };
  }
  return merged;
}

function fold(text: string): string {
  return text.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
}

/** Notes that contain every word of the query (browser storage: the engine cannot search them). */
export function searchLocalNotes(notes: Notes, query: string, titles: Map<string, string>): NoteHit[] {
  const terms = fold(query).split(/\s+/).filter(Boolean);
  if (!terms.length) return [];
  const hits: NoteHit[] = [];
  for (const [key, note] of Object.entries(notes)) {
    const folded = fold(note.body);
    if (!terms.every((term) => folded.includes(term))) continue;
    const at = Math.max(0, folded.indexOf(terms[0]) - 30);
    const snippet = (at > 0 ? "…" : "") + note.body.slice(at, at + 120).replace(/\s+/g, " ").trim();
    const lessonId = lessonOfKey(key);
    hits.push({ key, lesson_id: lessonId, title: lessonId ? (titles.get(lessonId) ?? null) : null, snippet, updated_at: note.updated_at });
  }
  return hits.sort((a, b) => b.updated_at.localeCompare(a.updated_at)).slice(0, 8);
}

/** Backup file: progress and notes. */
/** Lesson id → stable key, from the catalog (empty with an older engine that sends no keys). */
export function lessonKeys(catalog: { tracks: { sections: { id: string; key?: string }[] }[] } | null): Record<string, string> {
  const keys: Record<string, string> = {};
  for (const track of catalog?.tracks ?? []) for (const section of track.sections) if (section.key) keys[section.id] = section.key;
  return keys;
}

export function backupFile(notes: Notes, progressJson: string, keys: Record<string, string> = {}): string {
  const data = JSON.parse(progressJson) as Record<string, unknown>;
  // The stable key of each lesson lets an import after a renumbering land on the right lesson.
  return JSON.stringify({ ...data, notes: clean(notes), ...(Object.keys(keys).length ? { keys } : {}) }, null, 2);
}
