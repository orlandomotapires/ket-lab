import { describe, expect, it } from "vitest";
import type { GlossaryEntry } from "../engine/types";
import { filterTerms, initial, sortTerms, termId } from "./glossarySearch";

const entry = (term: string, definition = "A definition.", aliases: string[] = []): GlossaryEntry => ({ term, aliases, definition, lesson: "1.1" });

describe("glossary search", () => {
  const terms = [
    entry("qubit", "A two-level quantum system."),
    entry("Bell states", "Four entangled states of two qubits.", ["Bell state", "Bell pair"]),
    entry("amplitude", "The complex number in front of a basis state."),
    entry("T gate", "A phase gate of π/4."),
  ];

  it("sorts like a dictionary, ignoring case", () => {
    expect(sortTerms(terms).map((t) => t.term)).toEqual(["amplitude", "Bell states", "qubit", "T gate"]);
  });

  it("puts name matches before definition matches and requires every word", () => {
    expect(filterTerms(terms, "qubit").map((t) => t.term)).toEqual(["qubit", "Bell states"]);
    expect(filterTerms(terms, "bell pair").map((t) => t.term)).toEqual(["Bell states"]);
    expect(filterTerms(terms, "bell amplitude")).toEqual([]);
    expect(filterTerms(terms, "  ")).toHaveLength(4);
  });

  it("can match names and aliases only", () => {
    expect(filterTerms(terms, "qubit", { names: true }).map((t) => t.term)).toEqual(["qubit"]);
    expect(filterTerms(terms, "BELL", { names: true }).map((t) => t.term)).toEqual(["Bell states"]);
  });

  it("gives each term a letter and a DOM id", () => {
    expect(initial(entry("Bell states"))).toBe("B");
    expect(initial(entry("|+⟩ state"))).toBe("S");
    expect(termId("Hartree–Fock state")).toBe("glossary-hartree-fock-state");
  });
});
