import { useEffect, useState } from "react";
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

function ExternalLink({ url, children }: { url: string; children: string }) {
  return (
    <a
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

/** Lições que citam a obra: cada uma abre a lição. */
function CitedIn({ lessons }: { lessons: string[] }) {
  const openLesson = useStore((s) => s.openLesson);
  return (
    <span className="bib-cited">
      {t("bib.citedIn")}{" "}
      {lessons.map((id, index) => (
        <span key={id}>
          {index > 0 && ", "}
          <button className="link" onClick={() => void openLesson(id)}>{id}</button>
        </span>
      ))}
    </span>
  );
}

/** Página com todas as referências da plataforma, agrupadas por tipo. */
export function Bibliography() {
  const backToHub = useStore((s) => s.backToHub);
  const loadBibliography = useStore((s) => s.loadBibliography);
  const [data, setData] = useState<BibliographyData | null>(null);

  useEffect(() => {
    void loadBibliography().then(setData);
  }, [loadBibliography]);

  const of = (kind: Work["kind"]) => data?.works.filter((work) => work.kind === kind) ?? [];
  // Páginas de um mesmo curso da IBM ficam juntas, sob o nome do curso.
  const courses = new Map<string, Work[]>();
  for (const work of of("course")) courses.set(work.authors, [...(courses.get(work.authors) ?? []), work]);

  return (
    <div className="hub-scroll">
      <main className="bibliography">
        <button className="btn btn-ghost btn-sm" onClick={backToHub}>{t("bib.back")}</button>
        <h1>{t("bib.title")}</h1>
        <p className="muted">{t("bib.intro")}</p>
        {!data ? (
          <p className="muted">{t("hub.loading")}</p>
        ) : (
          <>
            <section>
              <h2>{t("bib.books")}</h2>
              <ul className="bib-list">
                {of("book").map((work) => (
                  <li key={work.url + work.title}>
                    <span className="bib-authors">{work.authors}{work.year ? ` (${work.year})` : ""}.</span>{" "}
                    <ExternalLink url={work.url}>{work.title}</ExternalLink>. <CitedIn lessons={work.lessons} />
                  </li>
                ))}
              </ul>
            </section>
            <section>
              <h2>{t("bib.papers")}</h2>
              <ul className="bib-list">
                {of("paper").map((work) => (
                  <li key={work.url}>
                    <span className="bib-authors">{work.authors}{work.year ? ` (${work.year})` : ""}.</span>{" "}
                    <ExternalLink url={work.url}>{work.title}</ExternalLink>. <CitedIn lessons={work.lessons} />
                  </li>
                ))}
              </ul>
            </section>
            <section>
              <h2>{t("bib.courses")}</h2>
              {[...courses.entries()].map(([course, pages]) => (
                <div key={course} className="bib-course">
                  <h3>{course}</h3>
                  <ul className="bib-list">
                    {pages.map((work) => (
                      <li key={work.url}>
                        <ExternalLink url={work.url}>{work.title}</ExternalLink>. <CitedIn lessons={work.lessons} />
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </section>
            <section>
              <h2>{t("bib.tutorials")}</h2>
              <ul className="bib-list">
                {of("tutorial").map((work) => (
                  <li key={work.url}>
                    <span className="bib-authors">{work.authors}.</span>{" "}
                    <ExternalLink url={work.url}>{work.title}</ExternalLink>. <CitedIn lessons={work.lessons} />
                  </li>
                ))}
              </ul>
            </section>
            <section>
              <h2>{t("bib.lectures")}</h2>
              <ul className="bib-list">
                {data.lectures.map((source) => (
                  <li key={source.title}>
                    <span className="bib-authors">{source.authors}{source.year ? ` (${source.year})` : ""}.</span>{" "}
                    {source.url ? <ExternalLink url={source.url}>{source.title}</ExternalLink> : <em>{source.title}</em>}.{" "}
                    <span className="muted">{source.note}</span>
                  </li>
                ))}
              </ul>
            </section>
            <section>
              <h2>{t("bib.software")}</h2>
              <ul className="bib-list">
                {data.software.map((source) => (
                  <li key={source.title}>
                    {source.url ? <ExternalLink url={source.url}>{source.title}</ExternalLink> : source.title}{" "}
                    <span className="muted">({source.authors}). {source.note}</span>
                  </li>
                ))}
              </ul>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
