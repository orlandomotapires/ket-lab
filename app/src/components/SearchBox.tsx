import { useEffect, useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import type { SearchResult } from "../engine/types";
import { t } from "../strings";
import { useStore } from "../state/store";

const DEBOUNCE_MS = 120;

/** Minúsculas e sem acentos, preservando o comprimento (para achar as posições no original). */
function fold(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

/** Destaca no trecho as palavras buscadas, ignorando acentos e maiúsculas. */
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
  const [results, setResults] = useState<SearchResult[]>([]);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const input = useRef<HTMLInputElement>(null);

  // Ctrl+K (ou Cmd+K) e "/" abrem a busca de qualquer tela.
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
    // Fase de captura: o editor Monaco usa Ctrl+K como início de atalhos e consumiria a tecla.
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, []);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    let cancelled = false;
    const timer = window.setTimeout(async () => {
      const found = await search(query);
      if (!cancelled) {
        setResults(found);
        setActive(0);
      }
    }, DEBOUNCE_MS);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [query, search]);

  const choose = (result: SearchResult | undefined) => {
    if (!result) return;
    setQuery("");
    setOpen(false);
    input.current?.blur();
    void openLesson(result.id);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActive((i) => Math.min(i + 1, results.length - 1));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActive((i) => Math.max(i - 1, 0));
    } else if (event.key === "Enter") {
      event.preventDefault();
      choose(results[active]);
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
        aria-activedescendant={showPanel && results[active] ? `search-${results[active].id}` : undefined}
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
      {!query && <kbd className="search-kbd">Ctrl K</kbd>}
      {showPanel && (
        <div className="search-panel" id="search-results" role="listbox">
          {results.length === 0 ? (
            <p className="search-empty">{t("search.empty", { query })}</p>
          ) : (
            results.map((result, index) => (
              <button
                key={result.id}
                id={`search-${result.id}`}
                role="option"
                aria-selected={index === active}
                className={`search-result${index === active ? " is-active" : ""}`}
                onMouseDown={(event) => event.preventDefault()}
                onMouseEnter={() => setActive(index)}
                onClick={() => choose(result)}
              >
                <span className="search-result-id">{result.id}</span>
                <span className="search-result-text">
                  <span className="search-result-title">{highlight(result.title, query)}</span>
                  <span className="search-result-snippet">{highlight(result.snippet, query)}</span>
                </span>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
