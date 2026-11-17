import { useSyncExternalStore } from "react";

export type ThemeName = "light" | "dark";

const STORAGE_KEY = "qlp.theme";
const listeners = new Set<() => void>();

function current(): ThemeName {
  return document.documentElement.dataset.theme === "dark" ? "dark" : "light";
}

export function setTheme(theme: ThemeName): void {
  document.documentElement.dataset.theme = theme;
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // No storage available: the theme only applies to this session.
  }
  listeners.forEach((listener) => listener());
}

export function toggleTheme(): void {
  setTheme(current() === "dark" ? "light" : "dark");
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useTheme(): ThemeName {
  return useSyncExternalStore(subscribe, current);
}

/** Colors used outside CSS (3D scene and editor). They mirror the tokens in styles/*.css. */
export interface Palette {
  surface: string;
  stage: string;
  text: string;
  muted: string;
  line: string;
  lineStrong: string;
  accent: string;
  sphere: string;
  editorLine: string;
}

export const PALETTES: Record<ThemeName, Palette> = {
  light: {
    surface: "#ffffff",
    stage: "#f8f9fb",
    text: "#15171c",
    muted: "#646a76",
    line: "#d3d7de",
    lineStrong: "#a8aeb8",
    accent: "#2f5bd3",
    sphere: "#8a919c",
    editorLine: "#f5f6f8",
  },
  dark: {
    surface: "#16191e",
    stage: "#13161a",
    text: "#e6e8ec",
    muted: "#9aa1ad",
    line: "#383e48",
    lineStrong: "#5a626e",
    accent: "#7d9ef0",
    sphere: "#7d8591",
    editorLine: "#1c2026",
  },
};
