import type { ReactNode } from "react";
import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import type { Comparison, Lesson, RunResult, Snapshot, VisualizerKind } from "../engine/types";
import { t } from "../strings";
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
import { selectCurrentStep, useStore, type TrainingState } from "../state/store";
import { MixedProbabilities, Probabilities, ShotsHistogram } from "./Probabilities";
import { CurveView } from "./viewsCurve";
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

// The 3D scenes are the heaviest module; they load apart from the rest of the interface.
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
    // "Original, qubit 0 before the CNOT" -> "Original": the full labels are under the spheres.
    const short = (label: string) => label.split(/[·,]/)[0].trim();
    return `${short(comparison.source_label)} × ${short(comparison.target_label)}`;
  }
  return t(`viz.view.${kind}`);
}

export function Visualizer({ lesson }: { lesson: Lesson | null }) {
  const result = useStore((s) => s.result);
  const resultIsCurrent = useStore((s) => s.resultIsCurrent);
  const shots = useStore((s) => s.shots);
  const reseed = useStore((s) => s.reseed);
  const code = useStore((s) => s.code);
  const current = useStore(selectCurrentStep);
  const hasError = useStore((s) => s.error !== null);
  const training = useStore((s) => s.training);
  const errorStdout = useStore((s) => s.errorStdout);
  // After a failed run, what the code printed before failing; otherwise the output of the last run.
  const printed = hasError ? errorStdout : (result?.stdout ?? "");

  // In the free lab, code with report(...) gets the training curve tab.
  const sandboxTraining = !lesson && training !== null;
  const views = lesson ? lesson.available_visualizers : sandboxTraining ? ["convergence" as const, ...SANDBOX_VIEWS] : SANDBOX_VIEWS;
  const [chosen, setView] = useState<VisualizerKind>(lesson?.default_visualizer ?? "bloch");
  // When a training run starts, the curve shows up by itself; afterwards the learner switches tabs freely.
  const trainingActive = sandboxTraining && training.active;
  useEffect(() => {
    if (trainingActive) setView("convergence");
  }, [trainingActive]);
  const view: VisualizerKind = views.includes(chosen) ? chosen : views[0];

  const header = (
    <div className="panel-head">
      <h2>{lesson?.framework === "python" && views.length === 1 ? t("viz.view.variables") : t("viz.title")}</h2>
      <span className="grow" />
      {views.length > 1 && (
        <div className="segmented" role="group" aria-label={t("viz.views")}>
          {views.map((kind) => (
            <button
              key={kind}
              aria-pressed={view === kind}
              title={kind === "compare" && lesson?.comparison ? `${lesson.comparison.source_label} × ${lesson.comparison.target_label}` : undefined}
              onClick={() => setView(kind)}
            >
              {tabLabel(kind, lesson?.comparison)}
            </button>
          ))}
        </div>
      )}
    </div>
  );

  if (lesson?.framework === "python") {
    return (
      <aside className="panel visualizer" aria-label={t("viz.aria")}>
        {header}
        {view === "curve" ? (
          <div className={`panel-scroll curve-stack${resultIsCurrent ? "" : " is-stale"}`} tabIndex={0}>
            <CurveView data={result?.analysis?.error ? null : result?.analysis?.curve} live={lesson.live !== false} />
            {result?.analysis?.error && <p className="muted">{t("viz.analysisError", { error: result.analysis.error })}</p>}
            {printed && <Stdout text={printed} />}
          </div>
        ) : (
          <VariablesTable result={result} stale={!resultIsCurrent} printed={printed} />
        )}
      </aside>
    );
  }

  if (sandboxTraining && view === "convergence" && (!result || training.active)) {
    return (
      <aside className="panel visualizer" aria-label={t("viz.aria")}>
        {header}
        <div className="stage">
          <TrainingStage training={training} />
        </div>
      </aside>
    );
  }

  if (!result) {
    return (
      <aside className="panel visualizer" aria-label={t("viz.aria")}>
        {header}
        <p className="muted pad">{hasError ? t("viz.fixError") : t("viz.waiting")}</p>
        {printed && <div className="panel-scroll"><Stdout text={printed} /></div>}
      </aside>
    );
  }

  const snapshot = result.snapshots[Math.min(current, result.snapshots.length - 1)];
  const step = current > 0 ? result.steps[current - 1] : undefined;
  const measured = result.steps.slice(0, current).filter((s) => s.kind === "measure");
  const showReadouts = !TRAINING_VIEWS.includes(view);
  // The Q-sphere is read with the entanglement and the amplitudes, the Bloch spheres with their vectors.
  const showWhole = showReadouts && view !== "bloch";
  const showVectors = showReadouts && view !== "qsphere";

  return (
    <aside className={`panel visualizer${resultIsCurrent ? "" : " is-stale"}`} aria-label={t("viz.aria")}>
      {header}
      {lesson?.controls?.length ? <Controls lesson={lesson} /> : null}
      {/* The 3D scene is not read by screen readers: the same state, as text. */}
      <p id="state-description" className="sr-only">
        {t("viz.stateDescription", {
          qubits: snapshot.bloch
            .map((v, q) => t("viz.qubitDescription", { q, x: fixed(v[0]), y: fixed(v[1]), z: fixed(v[2]), r: fixed(vectorLength(v)) }))
            .join(" "),
        })}
      </p>
      <div className="stage" aria-describedby="state-description">
        {!(sandboxTraining && view === "convergence") && <div className="stage-caption">
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
        </div>}
        <Suspense fallback={null}>
          {sandboxTraining && view === "convergence" ? (
            <TrainingStage training={training} />
          ) : (
            <Stage view={view} result={result} snapshot={snapshot} current={current} code={code} lesson={lesson} />
          )}
        </Suspense>
      </div>

      {(showReadouts || measured.length > 0 || shots || printed) && (
      <div className="panel-scroll" tabIndex={0}>
        {showReadouts && snapshot.reduced && <p className="footnote">{result.notice ?? t("viz.reducedStep")}</p>}
        {showWhole && !snapshot.reduced && (snapshot.amplitudes === null ? (
          <StatePurity value={snapshot.state_purity} />
        ) : (
          result.num_qubits >= 2 && <Entanglement snapshot={snapshot} numQubits={result.num_qubits} />
        ))}

        {showVectors && (
        <ReadoutSection id="bloch" title={t("viz.blochVectors")}>
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
        </ReadoutSection>
        )}

        {measured.length > 0 && (
          <p className="notice">
            {t("viz.measured", { list: measured.map((s) => `q${s.qubits[0]} = ${s.outcome}`).join(", ") })}{" "}
            <button className="link" onClick={reseed}>{t("viz.redraw")}</button>
          </p>
        )}

        {showWhole && !snapshot.reduced && (
        <ReadoutSection id="amplitudes" title={t("viz.amplitudes")}>
          {snapshot.amplitudes ? (
            <Probabilities amplitudes={snapshot.amplitudes} numQubits={result.num_qubits} />
          ) : (
            <MixedProbabilities probabilities={snapshot.probabilities} numQubits={result.num_qubits} />
          )}
        </ReadoutSection>
        )}
        {shots && <ShotsHistogram shots={shots} />}
        {printed && <Stdout text={printed} />}
      </div>
      )}
    </aside>
  );
}

/** What the learner's code printed. */
function Stdout({ text }: { text: string }) {
  return (
    <>
      <h3 className="section-label">{t("viz.stdout")}</h3>
      <pre className="stdout">{text}</pre>
    </>
  );
}

/** Lessons without a circuit: table with the learner's numeric variables. */
function VariablesTable({ result, stale, printed }: { result: RunResult | null; stale: boolean; printed: string }) {
  const rows = result?.variables ?? [];
  return (
    <div className={`panel-scroll variables${stale ? " is-stale" : ""}`} tabIndex={0}>
      {rows.length === 0 ? (
        <p className="muted">{t("viz.variablesEmpty")}</p>
      ) : (
        <>
          <table className="readout variables-table">
            <thead>
              <tr>
                <th scope="col">{t("viz.variableName")}</th>
                <th scope="col">{t("viz.variableType")}</th>
                <th scope="col">{t("viz.variableValue")}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.name}>
                  <th scope="row" className="mono">{row.name}</th>
                  <td className="muted small">{row.type}</td>
                  <td><pre className="variable-value">{row.value}</pre></td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="footnote">{t("viz.variablesNote")}</p>
        </>
      )}
      {printed && <Stdout text={printed} />}
    </div>
  );
}

/** Curve of the report(...) metrics: live during training, with metric switching. */
function TrainingStage({ training }: { training: TrainingState }) {
  const names = Object.keys(training.series);
  const [picked, setPicked] = useState<string | null>(null);
  const name = picked && names.includes(picked) ? picked : names[0];
  if (!name) {
    return <div className="stage-message">{training.active ? t("oracle.trainingStart") : t("viz.runToSee")}</div>;
  }
  return (
    <div className="training-stage">
      <div className="training-head">
        {names.length > 1 ? (
          <div className="segmented" role="group" aria-label={t("viz.metric")}>
            {names.map((option) => (
              <button key={option} aria-pressed={option === name} onClick={() => setPicked(option)}>
                <span className="mono">{option}</span>
              </button>
            ))}
          </div>
        ) : (
          <span className="mono small">{name}</span>
        )}
        <span className="grow" />
        {training.active && <span className="pill pill-live">{t("viz.live")}</span>}
      </div>
      <ConvergenceView data={{ values: training.series[name], y_label: name }} note={t("viz.trainingNote")} />
    </div>
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

  if (["landscape", "convergence", "dissociation", "graph", "boundary", "threshold"].includes(view)) {
    const analysis = result.analysis;
    if (!analysis) return <div className="stage-message">{t("viz.runToSee")}</div>;
    if (analysis.error) return <div className="stage-message">{t("viz.analysisError", { error: analysis.error })}</div>;
    const data = analysis[view as string];
    if (!data) return <div className="stage-message">{t("viz.runToSee")}</div>;
    if (view === "landscape") return <LandscapeView data={data as LandscapeData} />;
    if (view === "convergence") return <ConvergenceView data={data as ConvergenceData} />;
    if (view === "dissociation") return <DissociationView data={data as DissociationData} />;
    if (view === "graph") return <GraphView data={data as GraphData} />;
    if (view === "boundary") return <BoundaryView data={data as BoundaryData} />;
    if (view === "threshold") return <DissociationView data={data as DissociationData} label={t("viz.view.threshold")} />;
    return <div className="stage-message">{t("viz.runToSee")}</div>;
  }
  if (view === "modular" && lesson?.modular) {
    return <ModularView a={lesson.modular.a} N={lesson.modular.N} />;
  }
  if (view === "amplitudes" || view === "dials" || view === "histogram") {
    if (!register.length) return <div className="stage-message">{t("viz.waiting")}</div>;
    // After measuring the register, the state collapsed to a single value. What matters
    // (the QPE and Shor peaks) is the state right before its first measurement.
    const firstMeasure = result.steps.findIndex((s) => s.kind === "measure" && register.includes(s.qubits[0]));
    const collapsed = firstMeasure >= 0 && current > firstMeasure;
    const source = collapsed ? result.snapshots[firstMeasure] : snapshot;
    const amplitudes = source.amplitudes;
    const note = collapsed ? t("viz.beforeMeasurement") : undefined;
    if (view === "histogram" && !source.reduced) return <HistogramView probabilities={source.probabilities} register={register} note={note} />;
    if (source.reduced) return <div className="stage-message">{result.notice ?? t("viz.reducedStep")}</div>;
    if (!amplitudes) return <div className="stage-message">{t("viz.mixedState")}</div>;
    if (view === "amplitudes") return <AmplitudesView amplitudes={amplitudes} numQubits={n} register={register} scale={scale} note={note} />;
    if (view === "dials") return <DialsView amplitudes={amplitudes} numQubits={n} register={register} note={note} />;
  }
  if (view === "qsphere") {
    if (n > MAX_QSPHERE_QUBITS) return <div className="stage-message">{t("viz.tooManyQsphere", { limit: MAX_QSPHERE_QUBITS })}</div>;
    if (snapshot.reduced) return <div className="stage-message">{result.notice ?? t("viz.reducedStep")}</div>;
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
        <span>{t("viz.compareMarker", { call: comparison.source_marker.endsWith("(") ? `${comparison.source_marker}…)` : comparison.source_marker })}</span>
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

/** Views that plot a training run: the numeric readouts of the circuit state say nothing about them. */
const TRAINING_VIEWS: VisualizerKind[] = ["convergence", "landscape", "dissociation", "graph", "boundary", "threshold"];

/** A readout under the state view (always open). */
function ReadoutSection({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <section className="readout-section" aria-labelledby={`readout-${id}`}>
      <h3 className="section-label" id={`readout-${id}`}>{title}</h3>
      {children}
    </section>
  );
}

function StatePurity({ value }: { value: number }) {
  return (
    <ReadoutSection id="purity" title={t("viz.statePurity")}>
      <div className="entanglement">
        <span>Tr(ρ²)</span>
        <div className="meter" role="meter" aria-label={t("viz.statePurity")} aria-valuemin={0} aria-valuemax={1} aria-valuenow={value}>
          <span style={{ width: `${value * 100}%` }} />
        </div>
        <span className="value">{value.toFixed(2)}</span>
      </div>
      <p className="footnote">{t("viz.statePurityNote")}</p>
    </ReadoutSection>
  );
}

function Entanglement({ snapshot, numQubits }: { snapshot: Snapshot; numQubits: number }) {
  const rows =
    numQubits === 2 && snapshot.amplitudes
      ? [{ label: t("viz.concurrence"), value: concurrence(snapshot.amplitudes) }]
      : snapshot.purity.map((purity, qubit) => ({ label: t("viz.withRest", { qubit }), value: entanglementWithRest(purity) }));
  return (
    <ReadoutSection id="entanglement" title={t("viz.entanglement")}>
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
    </ReadoutSection>
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
          <div className="segmented" role="group" aria-label={control.label}>
            {control.options.map((option) => {
              const key = String(option);
              return (
                <button
                  key={key}
                  aria-pressed={values[control.id] === option}
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
