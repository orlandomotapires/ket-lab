/**
 * Before the rename to Ket Lab, everything the app kept in the browser (progress, notes,
 * theme, the IBM key...) used "qlp." keys. This moves each one to its "ket-lab." name, once.
 * main.tsx imports this module first, so it runs before anything reads the storage.
 */
const OLD_PREFIX = "qlp.";
const NEW_PREFIX = "ket-lab.";

export function migrateStorage(storage: Storage): void {
  const old: string[] = [];
  for (let i = 0; i < storage.length; i++) {
    const key = storage.key(i);
    if (key?.startsWith(OLD_PREFIX)) old.push(key);
  }
  for (const key of old) {
    const target = NEW_PREFIX + key.slice(OLD_PREFIX.length);
    const value = storage.getItem(key);
    // A value already saved under the new name is newer: keep it.
    if (value !== null && storage.getItem(target) === null) storage.setItem(target, value);
    storage.removeItem(key);
  }
}

for (const name of ["localStorage", "sessionStorage"] as const) {
  try {
    migrateStorage(window[name]);
  } catch {
    // Storage blocked (private mode, settings): there is nothing to move.
  }
}
