import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { BrowserEngineSocket } from "./socket";

/** A Web Worker that does nothing on its own: the test sends its messages. */
class FakeWorker {
  static all: FakeWorker[] = [];
  onmessage: ((event: { data: unknown }) => void) | null = null;
  onerror: ((event: unknown) => void) | null = null;
  terminated = false;
  constructor() {
    FakeWorker.all.push(this);
  }
  postMessage(): void {}
  terminate(): void {
    this.terminated = true;
  }
  say(data: Record<string, unknown>): void {
    this.onmessage?.({ data });
  }
}

const loading = (step: number) => ({ kind: "loading", step, total: 5, stage: "packages" });
const texts = { cancelled: { ok: false }, crash: { ok: false } };

describe("BrowserEngineSocket: a start that gets stuck", () => {
  beforeEach(() => {
    FakeWorker.all = [];
    vi.useFakeTimers();
    vi.stubGlobal("window", globalThis);
    vi.stubGlobal("Worker", FakeWorker);
    vi.spyOn(console, "error").mockImplementation(() => undefined);
    vi.spyOn(console, "info").mockImplementation(() => undefined);
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("replaces a worker stuck on one step, then gives the next one twice as long", () => {
    const socket = new BrowserEngineSocket("http://site/");
    FakeWorker.all[0].say(loading(2));
    vi.advanceTimersByTime(59_999);
    expect(FakeWorker.all).toHaveLength(1);
    vi.advanceTimersByTime(1);
    expect(FakeWorker.all[0].terminated).toBe(true);
    expect(FakeWorker.all).toHaveLength(2);
    // The second worker gets 120 s, not 60 s.
    vi.advanceTimersByTime(119_999);
    expect(FakeWorker.all).toHaveLength(2);
    vi.advanceTimersByTime(1);
    expect(FakeWorker.all).toHaveLength(3);
    // It still opens once a worker gets there.
    const onopen = vi.fn();
    socket.onopen = onopen;
    FakeWorker.all[2].say({ kind: "ready", texts });
    expect(onopen).toHaveBeenCalledOnce();
  });

  it("leaves a start alone while its steps keep moving, and once it is ready", () => {
    new BrowserEngineSocket("http://site/");
    const worker = FakeWorker.all[0];
    for (let step = 1; step <= 5; step++) {
      worker.say(loading(step));
      vi.advanceTimersByTime(50_000);
    }
    worker.say({ kind: "ready", texts });
    vi.advanceTimersByTime(10 * 60_000);
    expect(FakeWorker.all).toHaveLength(1);
    expect(worker.terminated).toBe(false);
  });
});
