import { EngineClient, resolveEndpoint } from "../engine/client";
import type { Catalog, GlossaryEntry, LessonProgress, NoteHit, SearchResult } from "../engine/types";
import type { BibliographyData } from "../components/Bibliography";
import { loadLocalProgress } from "../lib/localProgress";
import { searchLocalNotes } from "../lib/notes";
import { t } from "../strings";
import { engine, hasEngine, setEngine } from "./engine";
import type { Execution } from "./execution";
import type { ConnectionSlice, Get, Set } from "./types";

export function connectionSlice(set: Set, get: Get, execution: Execution): ConnectionSlice {
  async function loadCatalog(): Promise<void> {
    try {
      const response = await engine().call<{
        catalog: Catalog;
        progress: Record<string, LessonProgress>;
        progress_storage?: "engine" | "client";
        notes_storage?: "engine" | "client";
        glossary?: GlossaryEntry[];
      }>("catalog");
      if (response.ok) {
        const storage = response.progress_storage ?? "engine";
        const progress = storage === "client" ? loadLocalProgress() : response.progress;
        set({ catalog: response.catalog, progress, progressStorage: storage, glossary: response.glossary ?? [], loadError: null });
        void get().loadNotes(response.notes_storage ?? storage);
      } else set({ loadError: response.error?.message ?? t("hub.loadCatalogFailed") });
    } catch {
      // No connection: the connection notice already shows; retries on reconnect.
    }
  }

  return {
    connection: "connecting",
    view: "hub",
    catalog: null,
    glossary: [],
    loadError: null,

    init() {
      if (hasEngine()) return;
      const client = new EngineClient(
        resolveEndpoint,
        (status) => {
          const previous = get().connection;
          set({ connection: status });
          if (status === "open" && previous !== "open") {
            void loadCatalog();
            void engine()
              .call<{ available: boolean }>("hardware.available")
              .then((response) => set({ hardwareAvailable: response.ok && response.available }))
              .catch(() => undefined);
            if (get().view === "lab") execution.scheduleRun(0);
          }
        },
        (message) => set({ loadError: message }),
      );
      setEngine(client);
      void client.connect().catch(() => undefined);
    },

    backToHub() {
      execution.cancelScheduled();
      get().flushNotes();
      set({ view: "hub", notesOpen: false });
      void loadCatalog();
    },

    openReferences() {
      execution.cancelScheduled();
      get().flushNotes();
      set({ view: "references", notesOpen: false });
    },

    openNotesPage() {
      execution.cancelScheduled();
      get().flushNotes();
      set({ view: "notes", notesOpen: false });
    },

    glossaryFocus: null,
    glossaryReturn: "hub",

    openGlossary(term) {
      execution.cancelScheduled();
      get().flushNotes();
      // From a lesson, the glossary is a side trip: the lesson stays loaded and Back returns to it.
      const fromLesson = get().view === "lab" && get().lesson !== null;
      set({ view: "glossary", notesOpen: false, glossaryFocus: term ?? null, glossaryReturn: fromLesson ? "lab" : "hub" });
    },

    closeGlossary() {
      if (get().glossaryReturn === "lab" && get().lesson !== null) set({ view: "lab", glossaryFocus: null });
      else get().backToHub();
    },

    async loadBibliography() {
      try {
        const response = await engine().call<BibliographyData>("bibliography");
        return response.ok ? response : null;
      } catch {
        return null;
      }
    },

    async search(query) {
      const none = { results: [], notes: [] };
      if (get().connection !== "open" || !query.trim()) return none;
      try {
        const response = await engine().call<{ results: SearchResult[]; notes?: NoteHit[] }>("search", { query });
        if (!response.ok) return none;
        let notes = response.notes ?? [];
        if (get().notesStorage === "client") {
          const titles = new Map((get().catalog?.tracks ?? []).flatMap((track) => track.sections.map((s) => [s.id, s.title] as const)));
          notes = searchLocalNotes(get().notes, query, titles);
        }
        return { results: response.results, notes };
      } catch {
        return none;
      }
    },
  };
}
