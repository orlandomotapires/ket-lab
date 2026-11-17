import { useCallback, useState } from "react";

/** Open/closed choices of the interface, remembered in the browser. Storage can be missing
 *  or blocked (private window): then the choice only lasts for the session. */
export function readFlag(key: string): boolean | null {
  try {
    const value = localStorage.getItem(key);
    return value === "1" ? true : value === "0" ? false : null;
  } catch {
    return null;
  }
}

export function writeFlag(key: string, value: boolean): void {
  try {
    localStorage.setItem(key, value ? "1" : "0");
  } catch {
    // Not remembered.
  }
}

/** A boolean remembered under `key`. When the key changes, the value is read again. */
export function useStoredFlag(key: string, fallback: boolean): [boolean, (value: boolean) => void] {
  const [state, setState] = useState<{ key: string; value: boolean }>(() => ({ key, value: readFlag(key) ?? fallback }));
  const value = state.key === key ? state.value : (readFlag(key) ?? fallback);
  const set = useCallback(
    (next: boolean) => {
      writeFlag(key, next);
      setState({ key, value: next });
    },
    [key],
  );
  return [value, set];
}
