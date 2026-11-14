import { useSyncExternalStore } from "react";
import { de } from "./de";
import { en } from "./en";
import { pt, type MessageKey } from "./pt";

export type Locale = "pt" | "en" | "de";
export type { MessageKey };

export const LOCALES: { id: Locale; label: string; short: string }[] = [
  { id: "pt", label: "Português", short: "PT" },
  { id: "en", label: "English", short: "EN" },
  { id: "de", label: "Deutsch", short: "DE" },
];

const DICTIONARIES: Record<Locale, Record<MessageKey, string>> = { pt, en, de };
const STORAGE_KEY = "qlp.lang";
const listeners = new Set<() => void>();

/** Idioma salvo; senão, o do sistema; senão, inglês. */
function detect(): Locale {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "pt" || saved === "en" || saved === "de") return saved;
  } catch {
    // sem armazenamento: segue para a detecção
  }
  const languages = typeof navigator === "undefined" ? [] : navigator.languages ?? [navigator.language];
  for (const language of languages) {
    const base = language.toLowerCase().split("-")[0];
    if (base === "pt" || base === "en" || base === "de") return base;
  }
  return "en";
}

let current: Locale = detect();
applyToDocument();

function applyToDocument(): void {
  if (typeof document !== "undefined") document.documentElement.lang = current === "pt" ? "pt-BR" : current;
}

export function getLocale(): Locale {
  return current;
}

export function setLocale(locale: Locale): void {
  if (locale === current) return;
  current = locale;
  applyToDocument();
  try {
    localStorage.setItem(STORAGE_KEY, locale);
  } catch {
    // vale só para esta sessão
  }
  listeners.forEach((listener) => listener());
}

export function onLocaleChange(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** Texto no idioma atual, com {parâmetros} substituídos. */
export function t(key: MessageKey, params?: Record<string, string | number>): string {
  const template = DICTIONARIES[current][key] ?? pt[key];
  return params ? template.replace(/\{(\w+)\}/g, (match, name) => (name in params ? String(params[name]) : match)) : template;
}

/** Use em componentes: faz o componente renderizar de novo quando o idioma muda. */
export function useLocale(): Locale {
  return useSyncExternalStore(onLocaleChange, getLocale);
}

/** Formata número com o separador decimal do idioma atual. */
export function formatNumber(value: number, decimals: number): string {
  const text = value.toFixed(decimals);
  return current === "en" ? text : text.replace(".", ",");
}
