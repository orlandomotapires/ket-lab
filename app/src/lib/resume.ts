import type { CatalogTrack, LessonProgress } from "../engine/types";

export interface Resume {
  /** Lesson the main button of the hub opens, if any is left. */
  lessonId: string | null;
  /** "continue" once the learner has been in a lesson outside Track 0, "start" before that. */
  label: "start" | "continue";
}

/**
 * The lesson opened last, if it is not completed; otherwise the first lesson not completed outside
 * Track 0 (optional). Track 0 alone never turns "Start" into "Continue".
 */
export function resumeTarget(
  tracks: CatalogTrack[],
  progress: Record<string, LessonProgress>,
  lastId: string | null,
): Resume {
  const open = tracks.flatMap((track) => track.sections.map((section) => ({ ...section, track: track.id }))).filter((s) => s.available);
  const last = lastId ? open.find((section) => section.id === lastId) : undefined;
  const first = open.find((section) => section.track !== 0 && !progress[section.id]?.completed);
  const target = last && !progress[last.id]?.completed ? last : first;
  const started =
    (last !== undefined && last.track !== 0) ||
    open.some((section) => section.track !== 0 && (progress[section.id]?.code != null || progress[section.id]?.completed));
  return { lessonId: target?.id ?? null, label: started || (target !== undefined && target === last) ? "continue" : "start" };
}

/** Last lesson opened (not the free lab), to pick up where the learner left off. */
const LAST_KEY = "ket-lab.lastLesson";

export function readLastLesson(): string | null {
  try {
    return localStorage.getItem(LAST_KEY);
  } catch {
    return null;
  }
}

export function writeLastLesson(id: string): void {
  try {
    localStorage.setItem(LAST_KEY, id);
  } catch {
    // Not remembered.
  }
}
