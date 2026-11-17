import { lazy, Suspense, useEffect, useState } from "react";
import { Hub } from "./components/Hub";
import { TopBar } from "./components/TopBar";
import { t } from "./strings";
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
  const init = useStore((s) => s.init);

  useEffect(() => init(), [init]);

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
      {(connection === "closed" || (connection === "connecting" && slow)) && (
        <div className="banner" role="status">
          {connection === "closed" ? t("banner.closed") : t("banner.connecting")}
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
