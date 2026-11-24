import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { Hub } from "./components/Hub";
import { EngineLoadingBanner } from "./components/EngineLoadingBanner";
import { TopBar } from "./components/TopBar";
import { BROWSER_ENGINE } from "./engine/client";
import { t } from "./strings";
import { readRoute, writeRoute, type Route } from "./lib/route";
import { readSharedCode } from "./lib/share";
import { useStore } from "./state/store";

// The lab (Monaco, KaTeX, visualizations) is only downloaded when the first lesson is opened.
const Lab = lazy(() => import("./components/Lab").then((m) => ({ default: m.Lab })));
const ReviewView = lazy(() => import("./components/ReviewView").then((m) => ({ default: m.ReviewView })));
const NotesPage = lazy(() => import("./components/NotesPage").then((m) => ({ default: m.NotesPage })));
const GlossaryPage = lazy(() => import("./components/GlossaryPage").then((m) => ({ default: m.GlossaryPage })));
const Bibliography = lazy(() => import("./components/Bibliography").then((m) => ({ default: m.Bibliography })));

export function App() {
  const view = useStore((s) => s.view);
  const connection = useStore((s) => s.connection);
  const engineLoading = useStore((s) => s.engineLoading);
  const init = useStore((s) => s.init);

  // The lesson in the address when the page loaded, opened once the engine is ready.
  const [startRoute] = useState<Route>(() => readRoute());
  useEffect(() => init(), [init]);

  const restored = useRef(false);
  useEffect(() => {
    // Only the first time the engine opens, and only if nothing else was opened meanwhile.
    if (connection !== "open" || restored.current) return;
    restored.current = true;
    const state = useStore.getState();
    if (!startRoute || state.view !== "hub") return;
    if (startRoute.kind === "lesson") void state.openLesson(startRoute.id);
    else state.openSandbox();
  }, [connection, startRoute]);

  // Keeps the address in step with the open lesson (until the first change, it is left as loaded).
  useEffect(
    () =>
      useStore.subscribe((state, previous) => {
        if (state.view === previous.view && state.lesson?.id === previous.lesson?.id) return;
        if (state.view === "lab" && !state.codeTrusted) return;
        writeRoute(state.view === "lab" ? (state.lesson ? { kind: "lesson", id: state.lesson.id } : { kind: "sandbox" }) : null);
      }),
    [],
  );

  // Share link (#lab=…): opens the lab in review mode.
  useEffect(() => {
    void readSharedCode().then((code) => {
      if (code === null) return;
      history.replaceState(null, "", window.location.pathname + window.location.search);
      useStore.getState().openShared(code);
    });
  }, []);

  // "Connecting" only becomes a notice if it takes long: on a normal start it takes milliseconds.
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    setSlow(false);
    if (connection !== "connecting") return;
    const timer = window.setTimeout(() => setSlow(true), 2000);
    return () => window.clearTimeout(timer);
  }, [connection]);

  return (
    <div className="app">
      <TopBar />
      {engineLoading && connection !== "closed" ? (
        <EngineLoadingBanner loading={engineLoading} />
      ) : (connection === "closed" || (connection === "connecting" && slow)) && (
        <div className="banner" role="status">
          {connection === "closed" ? t(BROWSER_ENGINE ? "banner.closedInBrowser" : "banner.closed") : t("banner.connecting")}
        </div>
      )}
      {view === "hub" ? (
        <Hub />
      ) : (
        <Suspense fallback={<div className="banner" role="status">{t("app.loading")}</div>}>
          {view === "references" ? <Bibliography /> : view === "review" ? <ReviewView /> : view === "notes" ? <NotesPage /> : view === "glossary" ? <GlossaryPage /> : <Lab />}
        </Suspense>
      )}
    </div>
  );
}
