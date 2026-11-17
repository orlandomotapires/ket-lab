import { useEffect, useMemo, useState } from "react";
import { openExternal } from "../engine/client";
import { t } from "../strings";
import { useStore } from "../state/store";

interface Work {
  kind: "book" | "paper" | "course" | "tutorial";
  title: string;
  authors: string;
  year?: number | null;
  url: string;
  lessons: string[];
  /** Books: each cited passage (section, title, pages), in book order. */
  sections?: { location: string; lessons: string[] }[];
}

interface Source {
  title: string;
  authors: string;
  year?: number;
  note: string;
  url?: string;
}

export interface BibliographyData {
  works: Work[];
  lectures: Source[];
  software: Source[];
}

/** Up to this number of lessons, each one shows with its title; above it, only the number. */
const SPELL_OUT = 2;
/** Chips shown before the "+N" button. */
const CHIPS_SHOWN = 2;

function ExternalLink({ url, children }: { url: string; children: string }) {
  return (
    <a
      className="bib-link"
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      onClick={(event) => {
        event.preventDefault();
        openExternal(url);
      }}
    >
      {children}
    </a>
  );
}

/** Lessons that cite the work; each opens the lesson (the title shows in the tooltip or in full). */
function Lessons({ ids, titles }: { ids: string[]; titles: Map<string, string> }) {
  const openLesson = useStore((s) => s.openLesson);
  const [expanded, setExpanded] = useState(false);
  const spell = ids.length <= SPELL_OUT;
  const hidden = ids.length - CHIPS_SHOWN;
  const visible = expanded || hidden <= 0 ? ids : ids.slice(0, CHIPS_SHOWN);
  return (
    <span className="bib-lessons">
      {visible.map((id) => (
        <button key={id} className="bib-lesson" title={titles.get(id)} onClick={() => void openLesson(id)}>
          <span className="mono">{id}</span>
          {spell && titles.get(id) ? <span className="bib-lesson-title">{titles.get(id)}</span> : null}
        </button>
      ))}
      {hidden > 0 && (
        <button className="bib-lesson bib-more" aria-expanded={expanded} onClick={() => setExpanded(!expanded)}>
          {expanded ? t("bib.fewer") : t("bib.more", { n: hidden })}
        </button>
      )}
    </span>
  );
}

/** Page with every reference of the platform, grouped by type. */
export function Bibliography() {
  const backToHub = useStore((s) => s.backToHub);
  const loadBibliography = useStore((s) => s.loadBibliography);
  const catalog = useStore((s) => s.catalog);
  const [data, setData] = useState<BibliographyData | null>(null);
  const [track, setTrack] = useState<number | null>(null);

  useEffect(() => {
    void loadBibliography().then(setData);
  }, [loadBibliography]);

  const titles = useMemo(
    () => new Map((catalog?.tracks ?? []).flatMap((tr) => tr.sections.map((s) => [s.id, s.title] as const))),
    [catalog],
  );

  // Track filter: only the lessons of that track (and, in books, only the passages it uses).
  const inTrack = (id: string) => track === null || id.split(".")[0] === String(track);
  const works = useMemo(() => {
    if (!data) return [];
    return data.works
      .map((work) => ({
        ...work,
        lessons: work.lessons.filter(inTrack),
        sections: work.sections
          ?.map((section) => ({ ...section, lessons: section.lessons.filter(inTrack) }))
          .filter((section) => section.lessons.length > 0),
      }))
      .filter((work) => work.lessons.length > 0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, track]);

  const of = (kind: Work["kind"]) => works.filter((work) => work.kind === kind);
  const courses = new Map<string, Work[]>();
  for (const work of of("course")) courses.set(work.authors, [...(courses.get(work.authors) ?? []), work]);

  const groups = [
    { id: "books", label: t("bib.books"), count: of("book").length },
    { id: "papers", label: t("bib.papers"), count: of("paper").length },
    { id: "courses", label: t("bib.courses"), count: of("course").length },
    { id: "tutorials", label: t("bib.tutorials"), count: of("tutorial").length },
    ...(track === null
      ? [
          { id: "lectures", label: t("bib.lecturesShort"), count: data?.lectures.length ?? 0 },
          { id: "software", label: t("bib.software"), count: data?.software.length ?? 0 },
        ]
      : []),
  ].filter((group) => group.count > 0);

  const jump = (id: string) => document.getElementById(`bib-${id}`)?.scrollIntoView({ behavior: "smooth", block: "start" });

  return (
    <div className="hub-scroll">
      <main className="bibliography">
        <button className="btn btn-ghost btn-sm" onClick={backToHub}>{t("bib.back")}</button>
        <h1>{t("bib.title")}</h1>
        <p className="muted">{t("bib.intro")}</p>

        <div className="bib-toolbar">
          <nav className="bib-toc" aria-label={t("bib.contents")}>
            {groups.map((group) => (
              <button key={group.id} className="bib-toc-item" onClick={() => jump(group.id)}>
                {group.label} <span className="bib-count">{group.count}</span>
              </button>
            ))}
          </nav>
          <label className="bib-filter">
            <span className="muted small">{t("bib.filter")}</span>
            <select className="select" aria-label={t("bib.filter")} value={track ?? ""} onChange={(event) => setTrack(event.target.value === "" ? null : Number(event.target.value))}>
              <option value="">{t("bib.allTracks")}</option>
              {(catalog?.tracks ?? []).map((tr) => (
                <option key={tr.id} value={tr.id}>{t("hub.track", { id: tr.id })}: {tr.title}</option>
              ))}
            </select>
          </label>
        </div>

        {!data ? (
          <p className="muted">{t("hub.loading")}</p>
        ) : (
          <>
            {of("book").length > 0 && (
              <section id="bib-books">
                <h2>{t("bib.books")}</h2>
                <p className="muted small">{t("bib.booksNote")}</p>
                {of("book").map((work) => (
                  <article key={work.title} className="bib-book">
                    <h3>
                      <ExternalLink url={work.url}>{work.title}</ExternalLink>
                      <span className="bib-authors"> {work.authors}{work.year ? `, ${work.year}` : ""}</span>
                    </h3>
                    <ol className="bib-sections">
                      {work.sections?.map((section) => (
                        <li key={section.location}>
                          <span className="bib-location">{section.location}</span>
                          <Lessons ids={section.lessons} titles={titles} />
                        </li>
                      ))}
                    </ol>
                  </article>
                ))}
              </section>
            )}

            {of("paper").length > 0 && (
              <section id="bib-papers">
                <h2>{t("bib.papers")}</h2>
                <ul className="bib-list">
                  {of("paper").map((work) => (
                    <li key={work.url}>
                      <span className="bib-authors">{work.authors}{work.year ? ` (${work.year})` : ""}.</span>{" "}
                      <ExternalLink url={work.url}>{work.title}</ExternalLink>
                      <Lessons ids={work.lessons} titles={titles} />
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {courses.size > 0 && (
              <section id="bib-courses">
                <h2>{t("bib.courses")}</h2>
                {[...courses.entries()].map(([course, pages]) => (
                  <div key={course} className="bib-course">
                    <h3>{course}</h3>
                    <ul className="bib-list">
                      {pages.map((work) => (
                        <li key={work.url}>
                          <ExternalLink url={work.url}>{work.title}</ExternalLink>
                          <Lessons ids={work.lessons} titles={titles} />
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </section>
            )}

            {of("tutorial").length > 0 && (
              <section id="bib-tutorials">
                <h2>{t("bib.tutorials")}</h2>
                <ul className="bib-list">
                  {of("tutorial").map((work) => (
                    <li key={work.url}>
                      <span className="bib-authors">{work.authors}.</span>{" "}
                      <ExternalLink url={work.url}>{work.title}</ExternalLink>
                      <Lessons ids={work.lessons} titles={titles} />
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {track === null && (
              <>
                <section id="bib-lectures">
                  <h2>{t("bib.lectures")}</h2>
                  <ul className="bib-list">
                    {data.lectures.map((source) => (
                      <li key={source.title}>
                        <span className="bib-authors">{source.authors}{source.year ? ` (${source.year})` : ""}.</span>{" "}
                        {source.url ? <ExternalLink url={source.url}>{source.title}</ExternalLink> : <em>{source.title}</em>}
                        <span className="bib-note">{source.note}</span>
                      </li>
                    ))}
                  </ul>
                </section>
                <section id="bib-software">
                  <h2>{t("bib.software")}</h2>
                  <ul className="bib-list">
                    {data.software.map((source) => (
                      <li key={source.title}>
                        {source.url ? <ExternalLink url={source.url}>{source.title}</ExternalLink> : source.title}{" "}
                        <span className="bib-authors">({source.authors})</span>
                        <span className="bib-note">{source.note}</span>
                      </li>
                    ))}
                  </ul>
                </section>
              </>
            )}
          </>
        )}
      </main>
    </div>
  );
}
