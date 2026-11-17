import { useEffect, useMemo, useState } from "react";
import { filterTerms, initial, sortTerms, termId } from "../lib/glossarySearch";
import { t } from "../strings";
import { useStore } from "../state/store";

/** Every glossary term in one place: alphabetical, with a filter and the lesson that introduces each. */
export function GlossaryPage() {
  const glossary = useStore((s) => s.glossary);
  const catalog = useStore((s) => s.catalog);
  const focus = useStore((s) => s.glossaryFocus);
  const returnsToLesson = useStore((s) => s.glossaryReturn === "lab" && s.lesson !== null);
  const { closeGlossary, openLesson } = useStore.getState();
  const [query, setQuery] = useState("");

  const titles = useMemo(
    () => new Map((catalog?.tracks ?? []).flatMap((track) => track.sections).map((section) => [section.id, section.title])),
    [catalog],
  );
  const sorted = useMemo(() => sortTerms(glossary), [glossary]);
  const shown = useMemo(() => filterTerms(sorted, query), [sorted, query]);
  // With a filter the best matches come first; without one the list is alphabetical, under letter headings.
  const groups = useMemo(() => {
    if (query.trim()) return [{ letter: "", entries: shown }];
    const byLetter = new Map<string, typeof shown>();
    for (const entry of shown) byLetter.set(initial(entry), [...(byLetter.get(initial(entry)) ?? []), entry]);
    return [...byLetter].map(([letter, entries]) => ({ letter, entries }));
  }, [shown, query]);

  // Arriving from a term in a lesson or from the search: show that entry.
  useEffect(() => {
    if (!focus) return;
    const element = document.getElementById(termId(focus));
    element?.scrollIntoView({ block: "center" });
    element?.focus({ preventScroll: true });
  }, [focus, glossary]);

  return (
    <div className="hub-scroll">
      <main className="glossary-page">
        <button className="btn btn-ghost btn-sm" onClick={closeGlossary}>
          {returnsToLesson ? t("glossary.backToLesson") : t("notes.back")}
        </button>
        <h1>{t("glossary.title")}</h1>
        <p className="muted">{t("glossary.intro")}</p>

        <div className="glossary-filter">
          <input
            type="search"
            value={query}
            placeholder={t("glossary.filterPlaceholder")}
            aria-label={t("glossary.filter")}
            onChange={(event) => setQuery(event.target.value)}
          />
          <span className="glossary-count" role="status">
            {t("glossary.count", { shown: shown.length, total: glossary.length })}
          </span>
        </div>

        {!query.trim() && groups.length > 1 && (
          <nav className="glossary-letters" aria-label={t("glossary.title")}>
            {groups.map((group) => (
              <a key={group.letter} href={`#glossary-letter-${group.letter}`}>{group.letter}</a>
            ))}
          </nav>
        )}

        {shown.length === 0 && <p className="notes-empty">{t("glossary.none", { query })}</p>}

        {groups.map((group) => (
          <section key={group.letter || "matches"} aria-label={group.letter || t("glossary.title")}>
            {group.letter && <h2 className="glossary-letter" id={`glossary-letter-${group.letter}`}>{group.letter}</h2>}
            <dl className="glossary-list">
              {group.entries.map((entry) => {
                const lessonTitle = titles.get(entry.lesson);
                return (
                  <div
                    key={entry.term}
                    id={termId(entry.term)}
                    tabIndex={-1}
                    className={`glossary-entry${focus === entry.term ? " is-focus" : ""}`}
                  >
                    <dt>{entry.term}</dt>
                    <dd>
                      <p>{entry.definition}</p>
                      {entry.aliases && entry.aliases.length > 0 && (
                        <p className="glossary-aliases">{t("glossary.also", { names: entry.aliases.join(", ") })}</p>
                      )}
                      {lessonTitle && (
                        <button className="link small" onClick={() => void openLesson(entry.lesson)}>
                          {t("glossary.openLesson", { id: entry.lesson, title: lessonTitle })}
                        </button>
                      )}
                    </dd>
                  </div>
                );
              })}
            </dl>
          </section>
        ))}
      </main>
    </div>
  );
}
