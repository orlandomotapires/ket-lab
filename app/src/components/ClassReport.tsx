import { useState } from "react";
import type { LessonProgress } from "../engine/types";
import { parseProgressFile } from "../lib/localProgress";
import { t } from "../strings";
import { useStore } from "../state/store";

interface Student {
  name: string;
  progress: Record<string, LessonProgress>;
}

/**
 * Relatório da turma sem servidor: o professor carrega os arquivos de progresso
 * que os alunos exportaram e vê uma tabela lição × aluno. Nada sai do navegador.
 */
export function ClassReport() {
  const catalog = useStore((s) => s.catalog);
  const backToHub = useStore((s) => s.backToHub);
  const [students, setStudents] = useState<Student[]>([]);
  const [skipped, setSkipped] = useState<string[]>([]);

  const lessons = (catalog?.tracks ?? []).flatMap((track) => track.sections.filter((section) => section.available));

  async function load(files: FileList | null) {
    if (!files) return;
    const loaded: Student[] = [];
    const bad: string[] = [];
    for (const file of Array.from(files)) {
      try {
        loaded.push({ name: file.name.replace(/\.json$/i, ""), progress: parseProgressFile(await file.text()) });
      } catch {
        bad.push(file.name);
      }
    }
    setStudents((current) => [...current.filter((s) => !loaded.some((l) => l.name === s.name)), ...loaded].sort((a, b) => a.name.localeCompare(b.name)));
    setSkipped(bad);
  }

  return (
    <div className="hub-scroll">
      <main className="class-report">
        <button className="btn btn-ghost btn-sm" onClick={backToHub}>{t("class.back")}</button>
        <h1>{t("class.title")}</h1>
        <p className="muted">{t("class.intro")}</p>
        <label className="btn">
          {t("class.load")}
          <input type="file" accept="application/json,.json" multiple hidden onChange={(event) => void load(event.target.files)} />
        </label>
        {skipped.length > 0 && <p className="notice notice-error">{t("class.invalid", { files: skipped.join(", ") })}</p>}

        {students.length === 0 ? (
          <p className="muted">{t("class.empty")}</p>
        ) : (
          <div className="class-table-wrap" tabIndex={0}>
            <table className="readout class-table">
              <thead>
                <tr>
                  <th scope="col">{t("class.student")}</th>
                  {lessons.map((lesson) => (
                    <th key={lesson.id} scope="col" title={lesson.title} className="mono">{lesson.id}</th>
                  ))}
                  <th scope="col">{t("class.done")}</th>
                </tr>
              </thead>
              <tbody>
                {students.map((student) => {
                  const done = lessons.filter((lesson) => student.progress[lesson.id]?.completed).length;
                  return (
                    <tr key={student.name}>
                      <th scope="row">{student.name}</th>
                      {lessons.map((lesson) => {
                        const entry = student.progress[lesson.id];
                        const mark = entry?.completed ? "✓" : entry?.code != null ? "○" : "";
                        return (
                          <td key={lesson.id} className={`class-cell${entry?.completed ? " is-done" : ""}`}>
                            {mark}
                            {entry?.hints_used ? <sup>{entry.hints_used}</sup> : null}
                          </td>
                        );
                      })}
                      <td className="num mono">{done}/{lessons.length}</td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr>
                  <th scope="row">{t("class.done")}</th>
                  {lessons.map((lesson) => {
                    const done = students.filter((student) => student.progress[lesson.id]?.completed).length;
                    return (
                      <td key={lesson.id} className="num mono small" title={t("class.lessonRate", { done, total: students.length })}>
                        {Math.round((100 * done) / students.length)}%
                      </td>
                    );
                  })}
                  <td />
                </tr>
              </tfoot>
            </table>
          </div>
        )}
        <p className="footnote">{t("class.legend")}</p>
      </main>
    </div>
  );
}
