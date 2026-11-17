/** Share links for the free lab: the code goes compressed in the fragment (#lab=…). */
const PREFIX = "#lab=";
const MAX_CODE = 20_000;

function toBase64Url(bytes: Uint8Array): string {
  let binary = "";
  bytes.forEach((byte) => (binary += String.fromCharCode(byte)));
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromBase64Url(text: string): Uint8Array {
  const binary = atob(text.replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

async function pipe(bytes: Uint8Array, stream: CompressionStream | DecompressionStream): Promise<Uint8Array> {
  const output = new Blob([bytes]).stream().pipeThrough(stream);
  return new Uint8Array(await new Response(output).arrayBuffer());
}

/** Link with the code (the fragment does not go to the server hosting the page). */
export async function shareLink(code: string): Promise<string> {
  const compressed = await pipe(new TextEncoder().encode(code), new CompressionStream("deflate-raw"));
  const url = new URL(window.location.href);
  url.hash = PREFIX.slice(1) + toBase64Url(compressed);
  return url.toString();
}

/** Code from the link opened right now, or null. */
export async function readSharedCode(hash = window.location.hash): Promise<string | null> {
  if (!hash.startsWith(PREFIX)) return null;
  try {
    const bytes = await pipe(fromBase64Url(hash.slice(PREFIX.length)), new DecompressionStream("deflate-raw"));
    const code = new TextDecoder().decode(bytes);
    return code.length <= MAX_CODE ? code : null;
  } catch {
    return null;
  }
}
