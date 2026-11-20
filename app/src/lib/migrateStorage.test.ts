import { describe, expect, it } from "vitest";
import { migrateStorage } from "./migrateStorage";

/** The part of Storage the migration uses, over a Map. */
function memoryStorage(entries: Record<string, string>): Storage {
  const map = new Map(Object.entries(entries));
  return {
    get length() {
      return map.size;
    },
    key: (index: number) => [...map.keys()][index] ?? null,
    getItem: (key: string) => map.get(key) ?? null,
    setItem: (key: string, value: string) => void map.set(key, value),
    removeItem: (key: string) => void map.delete(key),
    clear: () => map.clear(),
  };
}

describe("migrateStorage", () => {
  it("moves every qlp. key to its ket-lab. name and leaves other keys alone", () => {
    const storage = memoryStorage({
      "qlp.progress.v1": '{"1.1":{"completed":true}}',
      "qlp.notes.v1": "my notes",
      "qlp.hub.track.2": "1",
      "other.key": "x",
    });
    migrateStorage(storage);
    expect(storage.getItem("ket-lab.progress.v1")).toBe('{"1.1":{"completed":true}}');
    expect(storage.getItem("ket-lab.notes.v1")).toBe("my notes");
    expect(storage.getItem("ket-lab.hub.track.2")).toBe("1");
    expect(storage.getItem("qlp.progress.v1")).toBeNull();
    expect(storage.getItem("other.key")).toBe("x");
    expect(storage.length).toBe(4);
  });

  it("keeps a value already saved under the new name", () => {
    const storage = memoryStorage({ "qlp.theme": "light", "ket-lab.theme": "dark" });
    migrateStorage(storage);
    expect(storage.getItem("ket-lab.theme")).toBe("dark");
    expect(storage.getItem("qlp.theme")).toBeNull();
  });
});
