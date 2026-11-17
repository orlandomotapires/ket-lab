import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import "katex/dist/katex.min.css";
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
  const root = useRef<HTMLDivElement>(null);
  // A formula wider than the panel scrolls sideways: it must be reachable by keyboard.
  useEffect(() => {
    const element = root.current;
    if (!element) return;
    const mark = () =>
      element.querySelectorAll<HTMLElement>(".katex-display").forEach((equation) => {
        if (equation.scrollWidth > equation.clientWidth + 1) equation.tabIndex = 0;
        else equation.removeAttribute("tabindex");
      });
    mark();
    void document.fonts?.ready.then(mark);
    const observer = new ResizeObserver(mark);
    observer.observe(element);
    return () => observer.disconnect();
  }, [children]);
  return (
    <div className="prose" ref={root}>
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

/** Glossary term: definition on hover or on keyboard focus. */
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
      role="link"
      aria-describedby={id}
      onClick={() => useStore.getState().openGlossary(entry.term)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          useStore.getState().openGlossary(entry.term);
        }
      }}
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
