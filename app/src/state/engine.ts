import type { EngineClient } from "../engine/client";

/** Single engine client, created in init(). */
let client: EngineClient | null = null;

export function engine(): EngineClient {
  if (!client) throw new Error("Engine not initialized.");
  return client;
}

export function hasEngine(): boolean {
  return client !== null;
}

export function setEngine(instance: EngineClient): void {
  client = instance;
}
