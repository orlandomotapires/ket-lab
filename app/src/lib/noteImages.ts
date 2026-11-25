/** Images attached to notes: shrinking them before they are saved, and keeping them in this
 *  browser (IndexedDB) when the engine does not keep the notes. */

/** Description of one image (no data). `key` is the note's key ("general", "lesson:<id>"). */
export interface NoteImage {
  id: string;
  key: string;
  mime: string;
  size: number;
  created_at: string;
}

/** An image with its data, in base64 (what the engine and the backup file carry). */
export interface NoteImageData extends Omit<NoteImage, "size"> {
  data: string;
}

/** Same limits as the engine: one WebSocket message per image. */
export const MAX_IMAGE_BYTES = 340 * 1024;
export const MAX_IMAGES_PER_NOTE = 12;
const IMAGE_TYPES = new Set(["image/png", "image/jpeg", "image/webp", "image/gif"]);
/** Longest side of a stored image, in pixels; larger pictures are scaled down. */
const MAX_SIDE = 1600;

export function newImageId(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(12));
  return btoa(String.fromCharCode(...bytes)).replace(/\+/g, "-").replace(/\//g, "_");
}

export function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).replace(/^data:[^,]*,/, ""));
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(blob);
  });
}

export function base64ToBlob(data: string, mime: string): Blob {
  const binary = atob(data);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return new Blob([bytes], { type: mime });
}

function canvasBlob(canvas: HTMLCanvasElement, mime: string, quality: number): Promise<Blob | null> {
  return new Promise((resolve) => canvas.toBlob(resolve, mime, quality));
}

/** A pasted or chosen picture, ready to store: kept as it is when small enough, otherwise
 *  scaled down and re-encoded (WebP, falling back to JPEG) until it fits. Null when it is not
 *  a picture the browser can read. */
export async function prepareImage(file: Blob): Promise<{ mime: string; blob: Blob } | null> {
  if (!file.type.startsWith("image/")) return null;
  let bitmap: ImageBitmap;
  try {
    bitmap = await createImageBitmap(file);
  } catch {
    return null;
  }
  const fits = Math.max(bitmap.width, bitmap.height) <= MAX_SIDE;
  if (IMAGE_TYPES.has(file.type) && file.size <= MAX_IMAGE_BYTES && fits) {
    bitmap.close();
    return { mime: file.type, blob: file };
  }
  let scale = Math.min(1, MAX_SIDE / Math.max(bitmap.width, bitmap.height));
  const canvas = document.createElement("canvas");
  try {
    for (let attempt = 0; attempt < 6; attempt++) {
      canvas.width = Math.max(1, Math.round(bitmap.width * scale));
      canvas.height = Math.max(1, Math.round(bitmap.height * scale));
      canvas.getContext("2d")?.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
      for (const quality of [0.86, 0.72]) {
        let blob = await canvasBlob(canvas, "image/webp", quality);
        // Browsers without a WebP encoder hand back a PNG.
        if (!blob || blob.type !== "image/webp") blob = await canvasBlob(canvas, "image/jpeg", quality);
        if (blob && blob.size <= MAX_IMAGE_BYTES) return { mime: blob.type, blob };
      }
      scale *= 0.75;
    }
    return null;
  } finally {
    bitmap.close();
  }
}

// -- browser storage ---------------------------------------------------------------------------

const DB_NAME = "ket-lab";
const STORE = "noteImages";

interface StoredImage {
  id: string;
  key: string;
  mime: string;
  blob: Blob;
  created_at: string;
}

let opening: Promise<IDBDatabase> | null = null;

function database(): Promise<IDBDatabase> {
  opening ??= new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1);
    request.onupgradeneeded = () => request.result.createObjectStore(STORE, { keyPath: "id" });
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => {
      opening = null;
      reject(request.error);
    };
  });
  return opening;
}

async function run<T>(mode: IDBTransactionMode, work: (store: IDBObjectStore) => IDBRequest<T>): Promise<T> {
  const db = await database();
  return new Promise((resolve, reject) => {
    const request = work(db.transaction(STORE, mode).objectStore(STORE));
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

const describe = (image: StoredImage): NoteImage => ({
  id: image.id, key: image.key, mime: image.mime, size: image.blob.size, created_at: image.created_at,
});

export async function listLocalImages(): Promise<NoteImage[]> {
  try {
    const all = await run<StoredImage[]>("readonly", (store) => store.getAll());
    return all.map(describe).sort((a, b) => a.created_at.localeCompare(b.created_at) || a.id.localeCompare(b.id));
  } catch {
    return [];
  }
}

export async function getLocalImage(id: string): Promise<Blob | null> {
  try {
    return (await run<StoredImage | undefined>("readonly", (store) => store.get(id)))?.blob ?? null;
  } catch {
    return null;
  }
}

/** Stores an image; an id that is already there is left as it is. */
export async function putLocalImage(image: Omit<StoredImage, "blob"> & { blob: Blob }): Promise<NoteImage> {
  const existing = await run<StoredImage | undefined>("readonly", (store) => store.get(image.id));
  if (existing) return describe(existing);
  await run("readwrite", (store) => store.put(image));
  return describe(image);
}

export async function deleteLocalImage(id: string): Promise<void> {
  try {
    await run("readwrite", (store) => store.delete(id));
  } catch {
    // Nothing to delete.
  }
}

/** Images grouped by note key. */
export function byNote(images: NoteImage[]): Record<string, NoteImage[]> {
  const grouped: Record<string, NoteImage[]> = {};
  for (const image of images) (grouped[image.key] ??= []).push(image);
  return grouped;
}

/** The `note_images` list of a backup file, keeping only well-formed entries. */
export function readBackupImages(raw: unknown): NoteImageData[] {
  if (!Array.isArray(raw)) return [];
  return raw.filter(
    (entry): entry is NoteImageData =>
      !!entry && typeof entry === "object" &&
      typeof entry.id === "string" && typeof entry.key === "string" &&
      typeof entry.mime === "string" && IMAGE_TYPES.has(entry.mime) &&
      typeof entry.data === "string" && typeof entry.created_at === "string",
  );
}
