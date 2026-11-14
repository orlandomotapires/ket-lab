import type { GlossaryEntry } from "../engine/types";

/** Nó hast mínimo (o suficiente para o plugin abaixo). */
interface HastNode {
  type: string;
  tagName?: string;
  value?: string;
  properties?: Record<string, unknown>;
  children?: HastNode[];
}

const SKIP_TAGS = new Set(["code", "pre", "a", "h1", "h2", "h3", "h4", "glossary-term"]);

function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Plugin rehype: marca a primeira ocorrência de cada termo do glossário no texto
 * da teoria (fora de código, títulos, links e fórmulas) com <glossary-term>.
 */
export function rehypeGlossary(entries: GlossaryEntry[]) {
  // Termos mais longos primeiro: "Bell states" antes de "state".
  const names = entries
    .flatMap((entry) => [entry.term, ...(entry.aliases ?? [])].map((name) => ({ name, term: entry.term })))
    .sort((a, b) => b.name.length - a.name.length);
  if (!names.length) return () => undefined;
  const pattern = new RegExp(`\\b(${names.map((n) => escapeRegExp(n.name)).join("|")})\\b`, "i");
  const termOf = (match: string) => names.find((n) => n.name.toLowerCase() === match.toLowerCase())?.term;

  return () => (tree: HastNode) => {
    const used = new Set<string>();
    const walk = (node: HastNode) => {
      if (!node.children) return;
      const classes = (node.properties?.className as string[] | undefined) ?? [];
      if ((node.tagName && SKIP_TAGS.has(node.tagName)) || classes.some((c) => c.startsWith("katex"))) return;
      const next: HastNode[] = [];
      for (const child of node.children) {
        if (child.type !== "text" || !child.value) {
          walk(child);
          next.push(child);
          continue;
        }
        let rest = child.value;
        let match = pattern.exec(rest);
        while (match) {
          const term = termOf(match[1]);
          if (!term || used.has(term)) {
            // Já marcado nesta lição: segue procurando depois deste trecho.
            const cut = match.index + match[1].length;
            next.push({ type: "text", value: rest.slice(0, cut) });
            rest = rest.slice(cut);
          } else {
            used.add(term);
            if (match.index > 0) next.push({ type: "text", value: rest.slice(0, match.index) });
            next.push({ type: "element", tagName: "glossary-term", properties: { dataTerm: term }, children: [{ type: "text", value: match[1] }] });
            rest = rest.slice(match.index + match[1].length);
          }
          match = pattern.exec(rest);
        }
        if (rest) next.push({ type: "text", value: rest });
      }
      node.children = next;
    };
    walk(tree);
  };
}
