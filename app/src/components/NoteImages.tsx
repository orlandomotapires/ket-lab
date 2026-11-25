import { useEffect, useRef, useState, type ClipboardEvent, type DragEvent, type ReactNode } from "react";
import { MAX_IMAGES_PER_NOTE } from "../lib/noteImages";
import { t } from "../strings";
import { useStore } from "../state/store";
import { ImageIcon } from "./icons";

/** The image files among pasted or dropped items. */
function imageFiles(list: { files: FileList | null } | null): File[] {
  return [...(list?.files ?? [])].filter((file) => file.type.startsWith("image/"));
}

/** A note's text box with its images below: paste (Ctrl+V) or drop a picture on the note,
 *  or choose one with "Add image". `className` styles the wrapper (the drawer stretches it). */
export function NoteWithImages({ noteKey, label, className = "", children }: {
  noteKey: string;
  label: string;
  className?: string;
  children: ReactNode;
}) {
  const images = useStore((s) => s.noteImages[noteKey]) ?? [];
  const [message, setMessage] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [open, setOpen] = useState<string | null>(null);
  const input = useRef<HTMLInputElement>(null);

  const attach = async (files: File[]) => {
    setMessage(null);
    for (const file of files) {
      const result = await useStore.getState().addNoteImage(noteKey, file);
      if (result !== "ok") {
        setMessage(t(`notes.image.${result}` as const, { limit: MAX_IMAGES_PER_NOTE }));
        return;
      }
    }
  };
  const onPaste = (event: ClipboardEvent<HTMLDivElement>) => {
    const files = imageFiles(event.clipboardData);
    if (!files.length) return; // plain text pastes as usual
    event.preventDefault();
    void attach(files);
  };
  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    setDragging(false);
    const files = imageFiles(event.dataTransfer);
    if (!files.length) return;
    event.preventDefault();
    void attach(files);
  };

  return (
    <div
      className={`note-with-images${dragging ? " is-dragging" : ""} ${className}`}
      onPaste={onPaste}
      onDragOver={(event) => {
        if ([...event.dataTransfer.items].some((item) => item.kind === "file")) {
          event.preventDefault();
          setDragging(true);
        }
      }}
      onDragLeave={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setDragging(false);
      }}
      onDrop={onDrop}
    >
      {children}
      <div className="note-images">
        {images.length > 0 && (
          <ul className="note-images-list" aria-label={t("notes.image.listAria", { note: label })}>
            {images.map((image, index) => (
              <li key={image.id} className="note-image">
                <button
                  className="note-image-open"
                  aria-label={t("notes.image.open", { n: index + 1 })}
                  title={t("notes.image.open", { n: index + 1 })}
                  onClick={() => setOpen(image.id)}
                >
                  <NoteImageView id={image.id} alt="" />
                </button>
                <button
                  className="note-image-remove"
                  aria-label={t("notes.image.remove", { n: index + 1 })}
                  title={t("notes.image.removeHint")}
                  onClick={() => void useStore.getState().removeNoteImage(image.id)}
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        )}
        <div className="note-images-actions">
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => input.current?.click()}
            disabled={images.length >= MAX_IMAGES_PER_NOTE}
            title={t("notes.image.addHint")}
          >
            <ImageIcon /> {t("notes.image.add")}
          </button>
          {message && <span className="note-images-message" role="alert">{message}</span>}
        </div>
        <input
          ref={input}
          type="file"
          accept="image/png,image/jpeg,image/webp,image/gif"
          multiple
          hidden
          onChange={(event) => {
            const files = imageFiles(event.target);
            event.target.value = "";
            void attach(files);
          }}
        />
      </div>
      {open && <ImageDialog id={open} onClose={() => setOpen(null)} />}
    </div>
  );
}

/** One stored image; the data is fetched the first time it is shown. */
function NoteImageView({ id, alt }: { id: string; alt: string }) {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    let live = true;
    void useStore.getState().noteImageUrl(id).then((value) => live && setUrl(value));
    return () => {
      live = false;
    };
  }, [id]);
  return url ? <img src={url} alt={alt} draggable={false} /> : <span className="note-image-loading" />;
}

/** The image at full size; click or Escape closes it. */
function ImageDialog({ id, onClose }: { id: string; onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const element = dialog.current;
    if (element && !element.open) element.showModal();
  }, []);
  return (
    <dialog
      ref={dialog}
      className="note-image-dialog"
      aria-label={t("notes.image.viewer")}
      onClose={onClose}
      onClick={() => dialog.current?.close()}
      onKeyDown={(event) => event.stopPropagation()}
    >
      <NoteImageView id={id} alt={t("notes.image.viewer")} />
    </dialog>
  );
}
