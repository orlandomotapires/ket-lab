import { describe, expect, it } from "vitest";
import type { CatalogTrack } from "../engine/types";
import { backupFile, lessonKeys, lessonNoteKey, lessonOfKey, mergeNotes, searchLocalNotes } from "./notes";
import { resumeTarget } from "./resume";

const note = (body: string, updated_at = "2026-11-01T10:00:00Z") => ({ body, updated_at });

describe("notes", () => {
  it("maps lesson ids to keys and back", () => {
    expect(lessonNoteKey("1.5")).toBe("lesson:1.5");
    expect(lessonOfKey("lesson:1.5")).toBe("1.5");
    expect(lessonOfKey("general")).toBeNull();
  });

  it("merge keeps both texts when they differ and does not repeat equal ones", () => {
    const merged = mergeNotes(
      { "lesson:1.1": note("mine"), general: note("same") },
      { "lesson:1.1": note("theirs", "2026-12-01T10:00:00Z"), general: note("same"), "lesson:1.2": note("new"), "lesson:1.3": note("  ") },
    );
    expect(merged["lesson:1.1"].body).toBe("mine\n\n--- imported ---\ntheirs");
    expect(merged.general.body).toBe("same");
    expect(merged["lesson:1.2"].body).toBe("new");
    expect(merged["lesson:1.3"]).toBeUndefined();
  });

  it("searches local notes ignoring accents and case, with every word required", () => {
    const titles = new Map([["1.1", "Qubit"]]);
    const notes = { "lesson:1.1": note("Lembrar a esfera de Bloch"), general: note("outra coisa") };
    expect(searchLocalNotes(notes, "esfera BLOCH", titles).map((hit) => hit.key)).toEqual(["lesson:1.1"]);
    expect(searchLocalNotes(notes, "esfera zzz", titles)).toEqual([]);
    expect(searchLocalNotes(notes, "outra", titles)[0].lesson_id).toBeNull();
  });
});

describe("resumeTarget", () => {
  const tracks: CatalogTrack[] = [
    { id: 0, title: "Math", level: "", sections: [{ id: "0.1", title: "a", summary: "", available: true }] },
    { id: 1, title: "Basics", level: "", sections: [
      { id: "1.1", title: "b", summary: "", available: true },
      { id: "1.2", title: "c", summary: "", available: true },
    ] },
  ];
  const done = { code: null, completed: true, hints_used: 0 };
  it("starts at the first lesson outside Track 0", () => {
    expect(resumeTarget(tracks, {}, null)).toEqual({ lessonId: "1.1", label: "start" });
  });
  it("Track 0 alone does not turn Start into Continue", () => {
    expect(resumeTarget(tracks, { "0.1": done }, "0.1")).toEqual({ lessonId: "1.1", label: "start" });
  });
  it("continues the lesson opened last while it is not completed", () => {
    expect(resumeTarget(tracks, {}, "1.2")).toEqual({ lessonId: "1.2", label: "continue" });
  });
  it("moves on to the first lesson left when the last one is completed", () => {
    expect(resumeTarget(tracks, { "1.1": done }, "1.1")).toEqual({ lessonId: "1.2", label: "continue" });
  });
  it("has nothing to offer when everything is completed", () => {
    expect(resumeTarget(tracks, { "1.1": done, "1.2": done }, "1.2").lessonId).toBeNull();
  });

  it("a backup carries the stable lesson keys when the catalog has them", () => {
    const catalog = { tracks: [{ sections: [{ id: "1.5", key: "bell_states" }, { id: "1.6" }] }] };
    expect(lessonKeys(catalog)).toEqual({ "1.5": "bell_states" });
    const file = JSON.parse(backupFile({}, JSON.stringify({ format: "qlp-progress", version: 2, progress: {} }), lessonKeys(catalog)));
    expect(file.keys).toEqual({ "1.5": "bell_states" });
    expect("keys" in JSON.parse(backupFile({}, JSON.stringify({ format: "qlp-progress" })))).toBe(false);
  });
});
