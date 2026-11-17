import type { ReviewQuestion } from "../engine/types";
import { t } from "../strings";
import { engine } from "./engine";
import type { Execution } from "./execution";
import type { ProgressTools } from "./progress";
import type { Get, ReviewSlice, Set } from "./types";

/** Progress key of a track's review. */
export function reviewKey(track: number): string {
  return `review:${track}`;
}

/** Saved score ("9/12") as a number of correct answers, or null. */
export function reviewScore(saved: string | null | undefined): { score: number; total: number } | null {
  const match = /^(\d+)\/(\d+)$/.exec(saved ?? "");
  return match ? { score: Number(match[1]), total: Number(match[2]) } : null;
}

export function reviewSlice(set: Set, get: Get, execution: Execution, saver: ProgressTools): ReviewSlice {
  return {
    reviewTrack: null,
    reviewQuestions: [],

    async openReview(track) {
      try {
        const response = await engine().call<{ questions: ReviewQuestion[] }>("review", { track });
        if (!response.ok || !response.questions?.length) {
          set({ loadError: t("review.loadFailed") });
          return;
        }
        set({ loadError: null });
        execution.cancelScheduled();
        get().flushNotes();
        set({ view: "review", notesOpen: false, reviewTrack: track, reviewQuestions: response.questions });
      } catch {
        // Connection notice already visible.
      }
    },

    saveReviewScore(score) {
      const track = get().reviewTrack;
      const total = get().reviewQuestions.length;
      if (track === null || !total) return;
      const key = reviewKey(track);
      const best = reviewScore(get().progress[key]?.code);
      if (best && best.total === total && best.score >= score) return; // the best score stays
      const code = `${score}/${total}`;
      saver.patch(key, { code, completed: true });
      if (get().progressStorage === "engine") {
        void engine().call("progress.save", { lesson_id: key, code, completed: true }).catch(() => undefined);
      }
    },
  };
}
