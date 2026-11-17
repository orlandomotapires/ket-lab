import { useEffect, useState } from "react";

/** True while the media query matches; follows window resizes. */
export function useMediaQuery(query: string): boolean {
  const get = () => (typeof window !== "undefined" && typeof window.matchMedia === "function" ? window.matchMedia(query).matches : false);
  const [matches, setMatches] = useState(get);
  useEffect(() => {
    if (typeof window.matchMedia !== "function") return;
    const list = window.matchMedia(query);
    const onChange = () => setMatches(list.matches);
    onChange();
    list.addEventListener("change", onChange);
    return () => list.removeEventListener("change", onChange);
  }, [query]);
  return matches;
}

/** The layout switches to one column below this width (see styles/hub.css and lab.css). */
export const NARROW = "(max-width: 1080px)";
/** Phone width. */
export const PHONE = "(max-width: 560px)";
