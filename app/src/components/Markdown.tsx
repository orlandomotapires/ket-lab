import { useMemo, useState, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import { rehypeGlossary } from "../lib/glossary";
import { t } from "../strings";
import { useStore } from "../state/store";

export function Markdown({ children }: { children: string }) {
  const glossary = useStore((s) => s.glossary);
  const plugin = useMemo(() => rehypeGlossary(glossary), [glossary]);
  return (
    <div className="prose">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex, plugin]}
        components={{ "glossary-term": GlossaryTerm } as Record<string, unknown> as never}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}

/** Termo do glossário: definição ao passar o mouse ou focar com o teclado. */
function GlossaryTerm(props: { "data-term"?: string; children?: ReactNode }) {
  const term = props["data-term"];
  const entry = useStore((s) => s.glossary.find((e) => e.term === term));
  const lessonTitle = useStore((s) =>
    s.catalog?.tracks.flatMap((track) => track.sections).find((section) => section.id === entry?.lesson)?.title,
  );
  const current = useStore((s) => s.lesson?.id);
  const [open, setOpen] = useState(false);
  if (!entry) return <>{props.children}</>;
  const id = `term-${entry.term.replace(/\W+/g, "-").toLowerCase()}`;
  return (
    <span
      className="glossary-term"
      tabIndex={0}
      aria-describedby={id}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
    >
      {props.children}
      <span id={id} role="tooltip" className={`glossary-tip${open ? " is-open" : ""}`}>
        <strong>{entry.term}.</strong> {entry.definition}
        {entry.lesson !== current && lessonTitle && (
          <span className="glossary-source">{t("glossary.introduced", { id: entry.lesson, title: lessonTitle })}</span>
        )}
      </span>
    </span>
  );
}
