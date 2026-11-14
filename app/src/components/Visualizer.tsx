import { lazy, Suspense, useMemo, useState } from "react";
import type { Comparison, Lesson, RunResult, Snapshot, VisualizerKind } from "../engine/types";
import { t, useLocale } from "../i18n";
import {
  blochFidelity,
  concurrence,
  describeStep,
  entanglementWithRest,
  formatPercent,
  formatPhase,
  rotationAxis,
  vectorLength,
} from "../lib/quantum";
import { stepForLine } from "../lib/steps";
import { selectCurrentStep, useStore } from "../state/store";
import { MixedProbabilities, Probabilities, ShotsHistogram } from "./Probabilities";
import { AmplitudesView, amplitudeScale, DialsView, HistogramView, ModularView } from "./views2d";
import {
  ConvergenceView,
  DissociationView,
  BoundaryView,
  GraphView,
  type BoundaryData,
  type GraphData,
  LandscapeView,
  type ConvergenceData,
  type DissociationData,
  type LandscapeData,
} from "./viewsTraining";

// As cenas 3D são o módulo mais pesado; carregam separadas do resto da interface.
const BlochScene = lazy(() => import("./scene3d").then((module) => ({ default: module.BlochScene })));
const QSphereScene = lazy(() => import("./scene3d").then((module) => ({ default: module.QSphereScene })));

const MAX_BLOCH_QUBITS = 9;
const MAX_QSPHERE_QUBITS = 5;
const MAX_REGISTER_QUBITS = 6;
const SANDBOX_VIEWS: VisualizerKind[] = ["bloch", "qsphere", "amplitudes", "dials"];

function fixed(value: number): string {
  return (Math.abs(value) < 5e-4 ? 0 : value).toFixed(2).replace("-", "−");
}

function tabLabel(kind: VisualizerKind, comparison: Comparison | undefined): string {
  if (kind === "compare" && comparison?.source_label && comparison.target_label) {
    const short = (label: string) => label.split("·")[0].trim();
    return `${short(comparison.source_label)} × ${short(comparison.target_label)}`;
  }
  return t(`viz.view.${kind}`);
}

export function Visualizer({ lesson }: { lesson: Lesson | null }) {
  useLocale();
  const result = useStore((s) => s.result);
  const resultIsCurrent = useStore((s) => s.resultIsCurrent);
  const shots = useStore((s) => s.shots);
  const reseed = useStore((s) => s.reseed);
  const code = useStore((s) => s.code);
  const current = useStore(selectCurrentStep);
  const hasError = useStore((s) => s.error !== null);

  const views = lesson ? lesson.available_visualizers : SANDBOX_VIEWS;
  const [view, setView] = useState<VisualizerKind>(lesson?.default_visualizer ?? "bloch");

  const header = (
    <div className="panel-head">
      <h2>{t("viz.title")}</h2>
      <span className="grow" />
      {views.length > 1 && (
        <div className="segmented" role="tablist" aria-label={t("viz.views")}>
          {views.map((kind) => (
            <button key={kind} role="tab" aria-selected={view === kind} onClick={() => setView(kind)}>
              {tabLabel(kind, lesson?.comparison)}
            </button>
          ))}
        </div>
      )}
    </div>
  );

  if (!result) {
    return (
      <aside className="panel visualizer" aria-label={t("viz.aria")}>
        {header}
        <p className="muted pad">{hasError ? t("viz.fixError") : t("viz.waiting")}</p>
      </aside>
    );
  }

  const snapshot = result.snapshots[Math.min(current, result.snapshots.length - 1)];
  const step = current > 0 ? result.steps[current - 1] : undefined;
  const measured = result.steps.slice(0, current).filter((s) => s.kind === "measure");

  return (
    <aside className={`panel visualizer${resultIsCurrent ? "" : " is-stale"}`} aria-label={t("viz.aria")}>
      {header}
      {lesson?.controls?.length ? <Controls lesson={lesson} /> : null}
      <div className="stage">
        <div className="stage-caption">
          <span>
            {current === 0 ? (
              <strong>{t("viz.initial")}</strong>
            ) : (
              <>
                {t("viz.afterStep")} <strong>{current}</strong>
                {step && (
                  <>
                    {" · "}
                    <span className="mono">{describeStep(step)}</span>
                  </>
                )}
              </>
            )}
          </span>
          <span className="grow" />
          {!resultIsCurrent && <span className="pill pill-warn">{t("viz.stale")}</span>}
        </div>
        <Suspense fallback={null}>
          <Stage view={view} result={result} snapshot={snapshot} current={current} code={code} lesson={lesson} />
        </Suspense>
      </div>

      <div className="panel-scroll">
        {snapshot.amplitudes === null ? (
          <StatePurity value={snapshot.state_purity} />
        ) : (
          result.num_qubits >= 2 && <Entanglement snapshot={snapshot} numQubits={result.num_qubits} />
        )}

        <h3 className="section-label">{t("viz.blochVectors")}</h3>
        <table className="readout">
          <thead>
            <tr>
              <th scope="col">{t("viz.qubit")}</th>
              <th scope="col" className="num">x</th>
              <th scope="col" className="num">y</th>
              <th scope="col" className="num">z</th>
              <th scope="col" className="num">|r|</th>
              <th scope="col" className="num">{t("viz.phase")}</th>
            </tr>
          </thead>
          <tbody>
            {snapshot.bloch.map((vector, qubit) => {
              const length = vectorLength(vector);
              const equatorial = Math.hypot(vector[0], vector[1]);
              return (
                <tr key={qubit}>
                  <th scope="row" className="mono">q{qubit}</th>
                  <td className="num mono">{fixed(vector[0])}</td>
                  <td className="num mono">{fixed(vector[1])}</td>
                  <td className="num mono">{fixed(vector[2])}</td>
                  <td className="num mono">{fixed(length)}</td>
                  <td className="num mono">{equatorial > 0.05 ? formatPhase(Math.atan2(vector[1], vector[0])) : "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {snapshot.bloch.some((vector) => vectorLength(vector) < 0.995) && <p className="footnote">{t("viz.mixedNote")}</p>}

        {measured.length > 0 && (
          <p className="notice">
            {t("viz.measured", { list: measured.map((s) => `q${s.qubits[0]} = ${s.outcome}`).join(", ") })}{" "}
            <button className="link" onClick={reseed}>{t("viz.redraw")}</button>
          </p>
        )}

        <h3 className="section-label">{t("viz.amplitudes")}</h3>
        {snapshot.amplitudes ? (
          <Probabilities amplitudes={snapshot.amplitudes} numQubits={result.num_qubits} />
        ) : (
          <MixedProbabilities probabilities={snapshot.probabilities} numQubits={result.num_qubits} />
        )}
        {shots && <ShotsHistogram shots={shots} />}
        {result.stdout && (
          <>
            <h3 className="section-label">{t("viz.stdout")}</h3>
            <pre className="stdout">{result.stdout}</pre>
          </>
        )}
      </div>
    </aside>
  );
}

function Stage({ view, result, snapshot, current, code, lesson }: {
  view: VisualizerKind; result: RunResult; snapshot: Snapshot; current: number; code: string; lesson: Lesson | null;
}) {
  const n = result.num_qubits;
  const register = useMemo(() => {
    const qubits = lesson?.register?.qubits ?? [...Array(Math.min(n, MAX_REGISTER_QUBITS)).keys()];
    return qubits.filter((q) => q < n);
  }, [lesson, n]);
  const scale = useMemo(
    () => (view === "amplitudes" && register.length ? amplitudeScale(result.snapshots, n, register) : 1),
    [view, result, n, register],
  );

  if (view === "landscape" || view === "convergence" || view === "dissociation" || view === "graph" || view === "boundary") {
    const analysis = result.analysis;
    if (!analysis) return <div className="stage-message">{t("viz.runToSee")}</div>;
    if (analysis.error) return <div className="stage-message">{t("viz.analysisError", { error: analysis.error })}</div>;
    const data = analysis[view];
    if (!data) return <div className="stage-message">{t("viz.runToSee")}</div>;
    if (view === "landscape") return <LandscapeView data={data as LandscapeData} />;
    if (view === "convergence") return <ConvergenceView data={data as ConvergenceData} />;
    if (view === "dissociation") return <DissociationView data={data as DissociationData} />;
    if (view === "graph") return <GraphView data={data as GraphData} />;
    if (view === "boundary") return <BoundaryView data={data as BoundaryData} />;
    return <div className="stage-message">{t("viz.runToSee")}</div>;
  }
  if (view === "modular" && lesson?.modular) {
    return <ModularView a={lesson.modular.a} N={lesson.modular.N} />;
  }
  if (view === "amplitudes" || view === "dials" || view === "histogram") {
    if (!register.length) return <div className="stage-message">{t("viz.waiting")}</div>;
    // Depois de medir o registrador, o estado colapsou num único valor. O que interessa
    // (os picos da QPE e do Shor) é o estado logo antes da primeira medição dele.
    const firstMeasure = result.steps.findIndex((s) => s.kind === "measure" && register.includes(s.qubits[0]));
    const collapsed = firstMeasure >= 0 && current > firstMeasure;
    const source = collapsed ? result.snapshots[firstMeasure] : snapshot;
    const amplitudes = source.amplitudes;
    const note = collapsed ? t("viz.beforeMeasurement") : undefined;
    if (view === "histogram") return <HistogramView probabilities={source.probabilities} register={register} note={note} />;
    if (!amplitudes) return <div className="stage-message">{t("viz.mixedState")}</div>;
    if (view === "amplitudes") return <AmplitudesView amplitudes={amplitudes} numQubits={n} register={register} scale={scale} note={note} />;
    if (view === "dials") return <DialsView amplitudes={amplitudes} numQubits={n} register={register} note={note} />;
  }
  if (view === "qsphere") {
    if (n > MAX_QSPHERE_QUBITS) return <div className="stage-message">{t("viz.tooManyQsphere", { limit: MAX_QSPHERE_QUBITS })}</div>;
    if (!snapshot.amplitudes) return <div className="stage-message">{t("viz.mixedState")}</div>;
    return <QSphereScene amplitudes={snapshot.amplitudes} numQubits={n} />;
  }
  if (view === "compare" && lesson?.comparison) {
    return <CompareStage result={result} snapshot={snapshot} code={code} comparison={lesson.comparison} />;
  }
  if (n > MAX_BLOCH_QUBITS) return <div className="stage-message">{t("viz.tooManyBloch", { limit: MAX_BLOCH_QUBITS })}</div>;
  const step = current > 0 ? result.steps[current - 1] : undefined;
  const axis = rotationAxis(step);
  const axes = snapshot.bloch.map((_, qubit) => (step && step.qubits[0] === qubit ? axis : null));
  return <BlochScene vectors={snapshot.bloch} axes={axes} />;
}

function CompareStage({ result, snapshot, code, comparison }: {
  result: RunResult; snapshot: Snapshot; code: string; comparison: Comparison;
}) {
  const { source_qubit: source, target_qubit: target } = comparison;
  if (result.num_qubits <= Math.max(source, target)) {
    return <div className="stage-message">{t("viz.compareQubits", { count: Math.max(source, target) + 1 })}</div>;
  }
  const markerLine = code.split("\n").findIndex((line) => line.includes(comparison.source_marker)) + 1;
  if (markerLine === 0) {
    return (
      <div className="stage-message">
        <span>{t("viz.compareMarker", { marker: comparison.source_marker })}</span>
      </div>
    );
  }
  const original = result.snapshots[stepForLine(result.steps, markerLine)].bloch[source];
  const now = snapshot.bloch[target];
  const fidelity = blochFidelity(original, now);
  return (
    <>
      <BlochScene vectors={[original, now]} axes={[null, null]} labels={[comparison.source_label, comparison.target_label]} />
      <div className="stage-footer">
        {t("viz.fidelity")} <strong>{formatPercent(fidelity)}</strong>
        {fidelity >= 0.999 ? ` · ${t("viz.identical")}` : ""}
      </div>
    </>
  );
}

function StatePurity({ value }: { value: number }) {
  return (
    <>
      <h3 className="section-label">{t("viz.statePurity")}</h3>
      <div className="entanglement">
        <span>Tr(ρ²)</span>
        <div className="meter" role="meter" aria-label={t("viz.statePurity")} aria-valuemin={0} aria-valuemax={1} aria-valuenow={value}>
          <span style={{ width: `${value * 100}%` }} />
        </div>
        <span className="value">{value.toFixed(2)}</span>
      </div>
      <p className="footnote">{t("viz.statePurityNote")}</p>
    </>
  );
}

function Entanglement({ snapshot, numQubits }: { snapshot: Snapshot; numQubits: number }) {
  const rows =
    numQubits === 2 && snapshot.amplitudes
      ? [{ label: t("viz.concurrence"), value: concurrence(snapshot.amplitudes) }]
      : snapshot.purity.map((purity, qubit) => ({ label: t("viz.withRest", { qubit }), value: entanglementWithRest(purity) }));
  return (
    <>
      <h3 className="section-label">{t("viz.entanglement")}</h3>
      <div className="entanglement">
        {rows.map(({ label, value }) => (
          <div key={label} style={{ display: "contents" }}>
            <span>{label}</span>
            <div className="meter" role="meter" aria-label={label} aria-valuemin={0} aria-valuemax={1} aria-valuenow={value}>
              <span style={{ width: `${value * 100}%` }} />
            </div>
            <span className="value">{value.toFixed(2)}</span>
          </div>
        ))}
      </div>
      <p className="footnote">{numQubits === 2 ? t("viz.concurrenceNote") : t("viz.withRestNote")}</p>
    </>
  );
}

function Controls({ lesson }: { lesson: Lesson }) {
  const values = useStore((s) => s.controls);
  const setControl = useStore((s) => s.setControl);
  const running = useStore((s) => s.running);
  return (
    <div className="controls" aria-label={t("viz.controls")}>
      {lesson.controls!.map((control) => (
        <div key={control.id} className="control">
          <span className="control-label">{control.label}</span>
          <div className="segmented" role="radiogroup" aria-label={control.label}>
            {control.options.map((option) => {
              const key = String(option);
              return (
                <button
                  key={key}
                  role="radio"
                  aria-checked={values[control.id] === option}
                  aria-selected={values[control.id] === option}
                  disabled={running}
                  onClick={() => setControl(control.id, option)}
                >
                  {control.option_labels[key] ?? key}
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
