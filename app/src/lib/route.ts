/** The open lesson lives in the address (#lesson=1.2, or #free-lab), so a reload lands back on it.
 *  The address is replaced, not pushed: the browser history does not fill up with lessons. */
export type Route = { kind: "lesson"; id: string } | { kind: "sandbox" } | null;

export function readRoute(hash = window.location.hash): Route {
  const lesson = /^#lesson=([\w.-]+)$/.exec(hash);
  if (lesson) return { kind: "lesson", id: decodeURIComponent(lesson[1]) };
  return hash === "#free-lab" ? { kind: "sandbox" } : null;
}

export function routeHash(route: Route): string {
  if (!route) return "";
  return route.kind === "lesson" ? `#lesson=${encodeURIComponent(route.id)}` : "#free-lab";
}

export function writeRoute(route: Route): void {
  const hash = routeHash(route);
  if (hash === window.location.hash) return;
  history.replaceState(null, "", window.location.pathname + window.location.search + hash);
}
