import { useEffect, useState } from "react";
import { ClassReport } from "./components/ClassReport";
import { Hub } from "./components/Hub";
import { Lab } from "./components/Lab";
import { TopBar } from "./components/TopBar";
import { t } from "./strings";
import { readSharedCode } from "./lib/share";
import { useStore } from "./state/store";

export function App() {
  const view = useStore((s) => s.view);
  const connection = useStore((s) => s.connection);
  const init = useStore((s) => s.init);

  useEffect(() => init(), [init]);

  // Link de compartilhamento (#lab=…): abre o laboratório em modo de revisão.
  useEffect(() => {
    void readSharedCode().then((code) => {
      if (code === null) return;
      history.replaceState(null, "", window.location.pathname + window.location.search);
      useStore.getState().openShared(code);
    });
  }, []);

  // "Conectando" só vira aviso se demorar: na abertura normal leva milissegundos.
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
      {view === "hub" ? <Hub /> : view === "class" ? <ClassReport /> : <Lab />}
    </div>
  );
}
