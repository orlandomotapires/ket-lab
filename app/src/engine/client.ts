import { getLocale } from "../i18n";
import type { EngineError } from "./types";

export interface EngineEndpoint {
  port: number;
  token: string;
}

interface TauriGlobal {
  core: { invoke<T>(command: string, args?: Record<string, unknown>): Promise<T> };
}

declare global {
  interface Window {
    /** Presente quando a interface roda dentro do shell desktop (Tauri). */
    __TAURI__?: TauriGlobal;
  }
}

export function isDesktop(): boolean {
  return window.__TAURI__ !== undefined;
}

/**
 * Abre um link externo no navegador do sistema. Na janela desktop, um link comum
 * não sai do app; o plugin opener do Tauri faz isso.
 */
export function openExternal(url: string): void {
  if (window.__TAURI__) {
    void window.__TAURI__.core.invoke("plugin:opener|open_url", { url }).catch(() => undefined);
  } else {
    window.open(url, "_blank", "noopener,noreferrer");
  }
}

/** No desktop, envia uma linha de diagnóstico ao terminal do shell. */
export function reportToShell(message: string): void {
  void window.__TAURI__?.core.invoke("client_log", { message }).catch(() => undefined);
}

/**
 * Onde o motor está escutando. No desktop, o shell inicia o motor e informa a
 * porta e o token sorteados; no navegador (desenvolvimento), vêm do ambiente.
 */
export async function resolveEndpoint(): Promise<EngineEndpoint> {
  if (window.__TAURI__) return window.__TAURI__.core.invoke<EngineEndpoint>("engine_endpoint");
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
      // O shell não conseguiu iniciar o motor: mostra o motivo e tenta de novo.
      this.onStatus("closed");
      const message = String(error instanceof Error ? error.message : error);
      reportToShell(`motor indisponível: ${message}`);
      this.onFailure(message);
      this.scheduleReconnect();
      throw new Error("O motor de simulação não iniciou.");
    }
    await new Promise<void>((resolve, reject) => {
      const socket = new WebSocket(`ws://127.0.0.1:${endpoint.port}/?token=${encodeURIComponent(endpoint.token)}`);
      this.socket = socket;
      // Um handshake que nunca termina deixaria a interface presa em "conectando".
      const timeout = window.setTimeout(() => {
        reportToShell(`WebSocket sem resposta em ${OPEN_TIMEOUT_MS} ms (porta ${endpoint.port})`);
        socket.close();
      }, OPEN_TIMEOUT_MS);
      socket.onopen = () => {
        window.clearTimeout(timeout);
        this.onStatus("open");
        resolve();
      };
      socket.onmessage = (event) => this.handleMessage(String(event.data));
      socket.onclose = (event) => {
        window.clearTimeout(timeout);
        reportToShell(`conexão encerrada (código ${event.code})`);
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
    await this.connect();
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve: resolve as (value: unknown) => void, reject });
      // O idioma vai em toda requisição: o motor responde mensagens e conteúdo nele.
      this.socket!.send(JSON.stringify({ id, type, lang: getLocale(), ...payload }));
    });
  }

  dispose(): void {
    this.disposed = true;
    this.socket?.close();
  }

  private handleMessage(raw: string): void {
    const message = JSON.parse(raw) as { id: number };
    const entry = this.pending.get(message.id);
    if (!entry) return;
    this.pending.delete(message.id);
    entry.resolve(message);
  }

  private failAll(error: Error): void {
    for (const entry of this.pending.values()) entry.reject(error);
    this.pending.clear();
  }
}
