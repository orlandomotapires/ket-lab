import type { GlossaryEntry } from "../engine/types";

/** Lowercase and without accents, so "Schrodinger" finds "Schrödinger". */
export function fold(text: string): string {
  return text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

/** Terms sorted as a dictionary would list them, ignoring case and symbols at the start. */
export function sortTerms(entries: GlossaryEntry[]): GlossaryEntry[] {
  const key = (entry: GlossaryEntry) => fold(entry.term).replace(/^[^a-z0-9]+/, "");
  return [...entries].sort((a, b) => key(a).localeCompare(key(b)));
}

/**
 * Entries that contain every word of the query. A match in the name or an alias
 * comes before a match that is only in the definition.
 */
export function filterTerms(entries: GlossaryEntry[], query: string, { names = false } = {}): GlossaryEntry[] {
  const words = fold(query).split(/\s+/).filter(Boolean);
  if (words.length === 0) return entries;
  const inName: GlossaryEntry[] = [];
  const inText: GlossaryEntry[] = [];
  for (const entry of entries) {
    const name = fold([entry.term, ...(entry.aliases ?? [])].join(" "));
    if (words.every((word) => name.includes(word))) inName.push(entry);
    else if (!names && words.every((word) => (name + " " + fold(entry.definition)).includes(word))) inText.push(entry);
  }
  return [...inName, ...inText];
}

/** The letter under which a term is listed ("#" for anything that does not start with a letter). */
export function initial(entry: GlossaryEntry): string {
  const first = fold(entry.term).replace(/^[^a-z0-9]+/, "").charAt(0).toUpperCase();
  return /[A-Z]/.test(first) ? first : "#";
}

/** Stable DOM id of an entry, used to scroll to it. */
export function termId(term: string): string {
  return `glossary-${fold(term).replace(/[^a-z0-9]+/g, "-")}`;
}
