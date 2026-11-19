import type { EngineSocket } from "./browser/socket";
import type { EngineError } from "./types";

export interface EngineEndpoint {
  url: string;
  /** The engine runs in this page (Pyodide in a Web Worker); `url` is where its files are. */
  browser?: boolean;
}

/** Built with VITE_ENGINE=browser: no server, the engine runs in the learner's browser. */
export const BROWSER_ENGINE = import.meta.env.VITE_ENGINE === "browser";

/** Opens an external link in a new tab. */
export function openExternal(url: string): void {
  window.open(url, "_blank", "noopener,noreferrer");
}

/** Saves a text file (becomes a download in the browser). */
export function saveTextFile(contents: string, fileName: string): boolean {
  const url = URL.createObjectURL(new Blob([contents], { type: "text/plain;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  return true;
}

/**
 * Where the engine is listening.
 * - Browser (VITE_ENGINE=browser): in this page; its files are under <base>/browser-engine/.
 * - Hosted: VITE_ENGINE_URL (e.g. "/engine"), on the same site as the interface.
 * - Local (npm run dev): 127.0.0.1, with the port and token from VITE_ENGINE_PORT and VITE_ENGINE_TOKEN.
 */
export async function resolveEndpoint(): Promise<EngineEndpoint> {
  if (BROWSER_ENGINE) {
    return { url: new URL(`${import.meta.env.BASE_URL}browser-engine/`, window.location.href).toString(), browser: true };
  }
  const hosted = import.meta.env.VITE_ENGINE_URL as string | undefined;
  if (hosted) {
    const url = new URL(hosted, window.location.href);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    return { url: url.toString() };
  }
  const port = Number(import.meta.env.VITE_ENGINE_PORT ?? 8765);
  const token = String(import.meta.env.VITE_ENGINE_TOKEN ?? "dev");
  return {
    url: `ws://127.0.0.1:${port}/?token=${encodeURIComponent(token)}`,
  };
}

export type ConnectionStatus = "connecting" | "open" | "closed";

export type EngineResponse<T> =
  | ({ ok: true } & T)
  | { ok: false; error?: EngineError; stale?: boolean };

interface Pending {
  resolve: (value: unknown) => void;
  reject: (reason: Error) => void;
  onEvent?: (event: Record<string, unknown>) => void;
}

/** A request in flight: the id is used to cancel it. */
export interface Request<T> {
  id: number;
  done: Promise<EngineResponse<T>>;
}

const RECONNECT_DELAY_MS = 1500;
const OPEN_TIMEOUT_MS = 5000;

/** RPC client over WebSocket (or the browser engine): each request carries an id and receives a response. */
export class EngineClient {
  private socket: EngineSocket | null = null;
  private nextId = 1;
  private pending = new Map<number, Pending>();
  private opening: Promise<void> | null = null;
  private disposed = false;

  constructor(
    private resolve: () => Promise<EngineEndpoint>,
    private onStatus: (status: ConnectionStatus) => void,
    private onFailure: (message: string) => void = () => undefined,
  ) {}

  connect(): Promise<void> {
    if (this.socket?.readyState === WebSocket.OPEN) return Promise.resolve();
    if (this.opening) return this.opening;

    this.onStatus("connecting");
    this.opening = this.open().finally(() => {
      this.opening = null;
    });
    return this.opening;
  }

  private async open(): Promise<void> {
    let endpoint: EngineEndpoint;
    try {
      endpoint = await this.resolve();
    } catch (error) {
      this.onStatus("closed");
      const message = String(error instanceof Error ? error.message : error);
      this.onFailure(message);
      this.scheduleReconnect();
      throw new Error("The simulation engine did not start.");
    }
    // The browser engine downloads and starts Python first (seconds to a minute): no handshake timeout.
    const BrowserSocket = endpoint.browser ? (await import("./browser/socket")).BrowserEngineSocket : null;
    await new Promise<void>((resolve, reject) => {
      const socket: EngineSocket = BrowserSocket ? new BrowserSocket(endpoint.url) : new WebSocket(endpoint.url);
      this.socket = socket;
      // A handshake that never finishes would leave the interface stuck on "connecting".
      const timeout = BrowserSocket ? undefined : window.setTimeout(() => {
        socket.close();
      }, OPEN_TIMEOUT_MS);
      socket.onopen = () => {
        window.clearTimeout(timeout);
        this.onStatus("open");
        resolve();
      };
      socket.onmessage = (event) => this.handleMessage(String(event.data));
      socket.onclose = () => {
        window.clearTimeout(timeout);
        if (this.socket === socket) this.socket = null;
        this.onStatus("closed");
        this.failAll(new Error("Connection to the engine closed."));
        reject(new Error("Could not connect to the simulation engine."));
        this.scheduleReconnect();
      };
    });
  }

  private scheduleReconnect(): void {
    if (this.disposed) return;
    window.setTimeout(() => void this.connect().catch(() => undefined), RECONNECT_DELAY_MS);
  }

  async call<T>(type: string, payload: Record<string, unknown> = {}): Promise<EngineResponse<T>> {
    return (await this.start<T>(type, payload)).done;
  }

  /** Like `call`, but returns the id and forwards intermediate events (training progress). */
  async start<T>(
    type: string,
    payload: Record<string, unknown> = {},
    onEvent?: (event: Record<string, unknown>) => void,
  ): Promise<Request<T>> {
    await this.connect();
    const id = this.nextId++;
    const done = new Promise<EngineResponse<T>>((resolve, reject) => {
      this.pending.set(id, { resolve: resolve as (value: unknown) => void, reject, onEvent });
      this.socket!.send(JSON.stringify({ id, type, ...payload }));
    });
    return { id, done };
  }

  dispose(): void {
    this.disposed = true;
    this.socket?.close();
  }

  private handleMessage(raw: string): void {
    const message = JSON.parse(raw) as { id: number; event?: string };
    const entry = this.pending.get(message.id);
    if (!entry) return;
    if (message.event) {
      entry.onEvent?.(message);
      return;
    }
    this.pending.delete(message.id);
    entry.resolve(message);
  }

  private failAll(error: Error): void {
    for (const entry of this.pending.values()) entry.reject(error);
    this.pending.clear();
  }
}
