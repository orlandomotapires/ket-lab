import { Fragment, useEffect, useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import type { GlossaryEntry, NoteHit, SearchResult } from "../engine/types";
import { filterTerms } from "../lib/glossarySearch";
import { modKey } from "../lib/platform";
import { t } from "../strings";
import { useStore } from "../state/store";

const DEBOUNCE_MS = 120;

type Entry =
  | { kind: "lesson"; id: string; result: SearchResult }
  | { kind: "note"; id: string; note: NoteHit }
  | { kind: "term"; id: string; term: GlossaryEntry };

/** Glossary terms shown in the search: only matches in the name, and only a few. */
const MAX_TERMS = 4;

/** Lowercase and without accents, preserving the length (to find positions in the original). */
function fold(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[\u2010-\u2014\u2212]/g, "-");
}

/** Highlights the searched words in the snippet, ignoring accents and case. */
function highlight(text: string, query: string): ReactNode {
  const terms = fold(query).split(/\s+/).filter(Boolean);
  const folded = fold(text);
  if (!terms.length || folded.length !== text.length) return text;
  const marks: [number, number][] = [];
  for (const term of terms) {
    for (let at = folded.indexOf(term); at >= 0; at = folded.indexOf(term, at + term.length)) {
      marks.push([at, at + term.length]);
    }
  }
  marks.sort((a, b) => a[0] - b[0]);
  const parts: ReactNode[] = [];
  let cursor = 0;
  for (const [start, end] of marks) {
    if (start < cursor) continue;
    parts.push(text.slice(cursor, start), <mark key={start}>{text.slice(start, end)}</mark>);
    cursor = end;
  }
  parts.push(text.slice(cursor));
  return parts;
}

function isTyping(target: EventTarget | null): boolean {
  const element = target as HTMLElement | null;
  return !!element && (element.tagName === "INPUT" || element.tagName === "TEXTAREA" || element.isContentEditable);
}

export function SearchBox() {
  const search = useStore((s) => s.search);
  const openLesson = useStore((s) => s.openLesson);
  const connection = useStore((s) => s.connection);
  const [query, setQuery] = useState("");
  const [found, setFound] = useState<{ results: SearchResult[]; notes: NoteHit[] }>({ results: [], notes: [] });
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const input = useRef<HTMLInputElement>(null);
  const glossary = useStore((s) => s.glossary);
  // The query the lesson results belong to: glossary terms wait for them, so the list never
  // shows a term first and then pushes it down when the lessons arrive.
  const [answered, setAnswered] = useState("");
  const terms = answered === query && query.trim().length >= 2 ? filterTerms(glossary, query, { names: true }).slice(0, MAX_TERMS) : [];
  // One list for the keyboard: lessons first, then notes, then glossary terms.
  const entries: Entry[] = [
    ...found.results.map((result): Entry => ({ kind: "lesson", id: `search-${result.id}`, result })),
    ...found.notes.map((note): Entry => ({ kind: "note", id: `search-note-${note.key.replace(/[^\w-]/g, "_")}`, note })),
    ...terms.map((term): Entry => ({ kind: "term", id: `search-term-${term.term.replace(/[^\w-]/g, "_")}`, term })),
  ];

  // Ctrl+K (or Cmd+K) and "/" open the search from any screen.
  useEffect(() => {
    const onKey = (event: globalThis.KeyboardEvent) => {
      const shortcut = (event.key === "k" && (event.ctrlKey || event.metaKey)) || (event.key === "/" && !isTyping(event.target));
      if (shortcut) {
        event.preventDefault();
        event.stopPropagation();
        input.current?.focus();
        input.current?.select();
      }
    };
    // Capture phase: the Monaco editor uses Ctrl+K to start shortcuts and would swallow the key.
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, []);

  useEffect(() => {
    if (!query.trim()) {
      setFound({ results: [], notes: [] });
      return;
    }
    let cancelled = false;
    const timer = window.setTimeout(async () => {
      const response = await search(query);
      if (!cancelled) {
        setFound(response);
        setAnswered(query);
        setActive(0);
      }
    }, DEBOUNCE_MS);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [query, search]);

  const choose = (entry: Entry | undefined) => {
    if (!entry) return;
    setQuery("");
    setOpen(false);
    input.current?.blur();
    if (entry.kind === "lesson") {
      void openLesson(entry.result.id);
    } else if (entry.kind === "term") {
      useStore.getState().openGlossary(entry.term.term);
    } else if (entry.note.lesson_id) {
      // The note opens beside its lesson.
      void openLesson(entry.note.lesson_id).then(() => useStore.getState().setNotesOpen(true));
    } else {
      useStore.getState().openNotesPage();
    }
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActive((i) => Math.min(i + 1, entries.length - 1));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActive((i) => Math.max(i - 1, 0));
    } else if (event.key === "Enter") {
      event.preventDefault();
      choose(entries[active]);
    } else if (event.key === "Escape") {
      setOpen(false);
      input.current?.blur();
    }
  };

  const showPanel = open && query.trim().length > 0;

  return (
    <div className="search" role="search">
      <svg className="search-icon" width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
        <circle cx="7" cy="7" r="4.5" />
        <path d="m10.5 10.5 3.5 3.5" strokeLinecap="round" />
      </svg>
      <input
        ref={input}
        type="search"
        value={query}
        placeholder={t("search.placeholder")}
        aria-label={t("search.label")}
        aria-expanded={showPanel}
        aria-controls="search-results"
        aria-activedescendant={showPanel && entries[active] ? entries[active].id : undefined}
        role="combobox"
        disabled={connection !== "open"}
        onChange={(event) => {
          setQuery(event.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => window.setTimeout(() => setOpen(false), 120)}
        onKeyDown={onKeyDown}
      />
      {!query && <kbd className="search-kbd">{modKey} K</kbd>}
      {showPanel && (
        <div className="search-panel" id="search-results" role="listbox">
          {entries.length === 0 ? (
            <p className="search-empty">{t("search.empty", { query })}</p>
          ) : (
            <>
              {entries.map((entry, index) => {
                const common = {
                  id: entry.id,
                  role: "option" as const,
                  "aria-selected": index === active,
                  className: `search-result${index === active ? " is-active" : ""}`,
                  onMouseDown: (event: React.MouseEvent) => event.preventDefault(),
                  onMouseEnter: () => setActive(index),
                  onClick: () => choose(entry),
                };
                const heading = entry.kind !== "lesson" && (index === 0 || entries[index - 1].kind !== entry.kind) && (
                  <div className="search-group" role="presentation">{t(entry.kind === "note" ? "search.notes" : "search.glossary")}</div>
                );
                return (
                  <Fragment key={entry.id}>
                    {heading}
                    {entry.kind === "lesson" ? (
                      <button {...common}>
                        <span className="search-result-id">{entry.result.id}</span>
                        <span className="search-result-text">
                          <span className="search-result-title">{highlight(entry.result.title, query)}</span>
                          <span className="search-result-snippet">{highlight(entry.result.snippet, query)}</span>
                        </span>
                      </button>
                    ) : entry.kind === "term" ? (
                      <button {...common}>
                        <span className="search-result-id">{entry.term.lesson}</span>
                        <span className="search-result-text">
                          <span className="search-result-title">{highlight(entry.term.term, query)}</span>
                          <span className="search-result-snippet">{entry.term.definition}</span>
                        </span>
                      </button>
                    ) : (
                      <button {...common}>
                        <span className="search-result-id">{entry.note.lesson_id ?? t("search.noteGeneral")}</span>
                        <span className="search-result-text">
                          <span className="search-result-title">{entry.note.title ?? t("notes.general")}</span>
                          <span className="search-result-snippet">{highlight(entry.note.snippet, query)}</span>
                        </span>
                      </button>
                    )}
                  </Fragment>
                );
              })}
            </>
          )}
        </div>
      )}
    </div>
  );
}
