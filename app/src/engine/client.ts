import type { EngineError } from "./types";

export interface EngineEndpoint {
  port: number;
  token: string;
}

/** Abre um link externo numa aba nova. */
export function openExternal(url: string): void {
  window.open(url, "_blank", "noopener,noreferrer");
}

/** Salva um arquivo de texto (vira um download no navegador). */
export function saveTextFile(contents: string, fileName: string): boolean {
  const url = URL.createObjectURL(new Blob([contents], { type: "text/plain;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  return true;
}

/** Onde o motor está escutando: porta e token vêm do ambiente do Vite (o `npm run dev` os define). */
export async function resolveEndpoint(): Promise<EngineEndpoint> {
  return {
    port: Number(import.meta.env.VITE_ENGINE_PORT ?? 8765),
    token: String(import.meta.env.VITE_ENGINE_TOKEN ?? "dev"),
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

/** Uma requisição em andamento: o id serve para cancelá-la. */
export interface Request<T> {
  id: number;
  done: Promise<EngineResponse<T>>;
}

const RECONNECT_DELAY_MS = 1500;
const OPEN_TIMEOUT_MS = 5000;

/** Cliente RPC sobre WebSocket: cada requisição leva um id e recebe uma resposta. */
export class EngineClient {
  private socket: WebSocket | null = null;
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
      throw new Error("O motor de simulação não iniciou.");
    }
    await new Promise<void>((resolve, reject) => {
      const socket = new WebSocket(`ws://127.0.0.1:${endpoint.port}/?token=${encodeURIComponent(endpoint.token)}`);
      this.socket = socket;
      // Um handshake que nunca termina deixaria a interface presa em "conectando".
      const timeout = window.setTimeout(() => {
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
        this.failAll(new Error("Conexão com o motor encerrada."));
        reject(new Error("Não foi possível conectar ao motor de simulação."));
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

  /** Como `call`, mas devolve o id e repassa eventos intermediários (progresso de treino). */
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
