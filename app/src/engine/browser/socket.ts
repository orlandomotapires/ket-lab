/**
 * The browser engine behind the same small interface as a WebSocket, so EngineClient can
 * use it unchanged. It speaks the same JSON protocol as the engine server.
 *
 * Python in the Web Worker runs one job at a time and cannot be interrupted, so this class
 * does what the server's worker pool does, from outside:
 * - sends one request at a time and keeps the rest in a queue;
 * - an edit replaces a queued, not yet started run (the older one gets {stale: true});
 * - a job past its time limit, or stopped with {type: "cancel"}, ends by terminating the
 *   worker; the job gets the engine's own timeout/cancel reply, and a new worker starts
 *   (from the browser cache, a few seconds) to serve the queue;
 * - a job that leaves the worker's memory large gets a new worker too: WebAssembly memory
 *   only grows, so this is the way to give it back to the system.
 */

/** Where the browser engine is while it starts; null once it is ready. */
export interface EngineLoading {
  step: number;
  total: number;
  stage: "runtime" | "packages" | "libraries" | "lessons" | "starting";
  /** first start; new worker after a timeout, Stop or crash; new worker to free memory */
  reason: "start" | "restart" | "memory";
}

export interface EngineSocket {
  readonly readyState: number;
  onopen: ((event: Event) => void) | null;
  onmessage: ((event: MessageEvent) => void) | null;
  onclose: ((event: CloseEvent) => void) | null;
  send(data: string): void;
  close(): void;
}

interface Queued {
  id: number;
  type: string;
  train: boolean;
  raw: string;
}

type Reply = Record<string, unknown>;

interface WorkerMessage {
  kind: "loading" | "ready" | "reply" | "event" | "job" | "phase" | "finished" | "fatal" | "crashed";
  step?: number;
  total?: number;
  stage?: EngineLoading["stage"];
  heapMB?: number;
  raw?: string;
  reply?: string;
  seconds?: number;
  message?: string;
  texts?: { cancelled: Reply; crash: Reply };
}

const CONNECTING = 0;
const OPEN = 1;
const CLOSED = 3;
/** A worker whose memory grew past this after a job is replaced (memory cannot shrink). */
const HEAP_RESTART_MB = 1024;

export class BrowserEngineSocket implements EngineSocket {
  readyState = CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onloading: ((loading: EngineLoading | null) => void) | null = null;

  private reason: EngineLoading["reason"] = "start";
  private worker: Worker | null = null;
  private ready = false;
  private queue: Queued[] = [];
  private inFlight: Queued | null = null;
  private timer: number | undefined;
  private timeoutReply: Reply | null = null;
  private texts: { cancelled: Reply; crash: Reply } | null = null;

  constructor(private base: string) {
    this.startWorker();
  }

  send(data: string): void {
    if (this.readyState !== OPEN) throw new Error("The browser engine is not running.");
    const message = JSON.parse(data) as { id: number; type: string; train?: boolean; target?: number };
    if (message.type === "cancel") {
      this.cancel(message.target);
      this.deliver({ id: message.id, ok: true });
      return;
    }
    const train = Boolean(message.train);
    if (message.type === "run" && !train) {
      // Only the latest edit matters (as on the server): a waiting run is outdated now.
      for (const old of this.queue.filter((item) => item.type === "run" && !item.train)) {
        this.deliver({ id: old.id, ok: false, stale: true });
      }
      this.queue = this.queue.filter((item) => item.type !== "run" || item.train);
    }
    this.queue.push({ id: message.id, type: message.type, train, raw: data });
    this.pump();
  }

  close(): void {
    if (this.readyState === CLOSED) return;
    this.stopWorker();
    this.readyState = CLOSED;
    queueMicrotask(() => this.onclose?.(new CloseEvent("close")));
  }

  // -- worker lifecycle --------------------------------------------------- //

  private startWorker(): void {
    this.ready = false;
    const worker = new Worker(new URL("./worker.ts", import.meta.url), { type: "module" });
    this.worker = worker;
    worker.onmessage = (event: MessageEvent<WorkerMessage>) => {
      if (this.worker === worker) this.fromWorker(event.data);
    };
    worker.onerror = (event) => {
      event.preventDefault();
      if (this.worker === worker) this.workerBroke(event.message);
    };
    worker.postMessage({ kind: "init", base: this.base });
  }

  private stopWorker(): void {
    window.clearTimeout(this.timer);
    this.worker?.terminate();
    this.worker = null;
    this.ready = false;
  }

  /** Ends the running job with `reply` and starts a fresh worker for the queue. */
  private restart(reply: Reply | null, reason: EngineLoading["reason"] = "restart"): void {
    this.reason = reason;
    const job = this.inFlight;
    this.inFlight = null;
    this.timeoutReply = null;
    this.stopWorker();
    if (job && reply) this.deliver({ ...reply, id: job.id });
    this.startWorker();
  }

  private workerBroke(message: string): void {
    console.error("[browser engine]", message);
    if (!this.texts) {
      // It never started (download failed, browser without WebAssembly...): report the
      // connection as closed; EngineClient tries again a little later.
      this.close();
      return;
    }
    this.restart(this.texts.crash);
  }

  private fromWorker(message: WorkerMessage): void {
    switch (message.kind) {
      case "loading":
        this.onloading?.({ step: message.step!, total: message.total!, stage: message.stage!, reason: this.reason });
        return;
      case "ready":
        this.texts = message.texts ?? null;
        this.ready = true;
        this.onloading?.(null);
        if (this.readyState === CONNECTING) {
          this.readyState = OPEN;
          this.onopen?.(new Event("open"));
        }
        this.pump();
        return;
      case "job":
        this.timeoutReply = JSON.parse(message.reply!) as Reply;
        window.clearTimeout(this.timer);
        this.timer = window.setTimeout(() => this.restart(this.timeoutReply), message.seconds! * 1000);
        return;
      case "phase":
        this.timeoutReply = JSON.parse(message.reply!) as Reply;
        return;
      case "finished":
        window.clearTimeout(this.timer);
        return;
      case "event":
        this.deliverRaw(message.raw!);
        return;
      case "reply":
        window.clearTimeout(this.timer);
        this.inFlight = null;
        this.deliverRaw(message.raw!);
        if ((message.heapMB ?? 0) > HEAP_RESTART_MB) this.restart(null, "memory");
        else this.pump();
        return;
      case "fatal":
      case "crashed":
        this.workerBroke(message.message ?? "unknown error");
        return;
    }
  }

  // -- queue -------------------------------------------------------------- //

  private pump(): void {
    if (!this.ready || this.inFlight || this.queue.length === 0) return;
    this.inFlight = this.queue.shift()!;
    this.worker!.postMessage({ kind: "request", raw: this.inFlight.raw });
  }

  private cancel(target: number | undefined): void {
    const cancelled = this.texts?.cancelled ?? { ok: false };
    if (this.inFlight?.id === target) {
      this.restart(cancelled);
      return;
    }
    const queued = this.queue.find((item) => item.id === target);
    if (queued) {
      this.queue = this.queue.filter((item) => item !== queued);
      this.deliver({ ...cancelled, id: queued.id });
    }
  }

  private deliver(reply: Reply): void {
    this.deliverRaw(JSON.stringify(reply));
  }

  private deliverRaw(raw: string): void {
    this.onmessage?.(new MessageEvent("message", { data: raw }));
  }
}
