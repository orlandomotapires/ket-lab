import { forwardRef } from "react";
import { NOTE_LIMIT } from "../lib/notes";
import { useStore } from "../state/store";

/** Plain text box of one note, saved as the learner types. */
export const NoteField = forwardRef<HTMLTextAreaElement, {
  noteKey: string;
  label: string;
  placeholder: string;
  className?: string;
}>(function NoteField({ noteKey, label, placeholder, className = "" }, ref) {
  const body = useStore((s) => s.notes[noteKey]?.body ?? "");
  return (
    <textarea
      ref={ref}
      className={`note-field ${className}`}
      aria-label={label}
      placeholder={placeholder}
      value={body}
      maxLength={NOTE_LIMIT}
      spellCheck
      onChange={(event) => useStore.getState().setNote(noteKey, event.target.value)}
      onBlur={() => useStore.getState().flushNotes()}
    />
  );
});

/** "Saving…" and "Saved", quiet and read out politely. */
export function NoteStatus({ text }: { text: Record<"saving" | "saved" | "error", string> }) {
  const status = useStore((s) => s.notesStatus);
  return (
    <span className={`note-status${status === "error" ? " is-error" : ""}`} role="status" aria-live="polite">
      {status === "idle" ? "" : text[status]}
    </span>
  );
}
