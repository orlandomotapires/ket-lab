/** macOS and iOS show ⌘ and ⌥ where other systems show Ctrl and Alt. */
export const isApple: boolean = typeof navigator !== "undefined" && /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
export const modKey: string = isApple ? "⌘" : "Ctrl";
export const altKey: string = isApple ? "⌥" : "Alt";
