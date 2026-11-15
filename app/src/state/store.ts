import { create } from "zustand";
import { EngineClient, resolveEndpoint, type ConnectionStatus, type EngineResponse } from "../engine/client";
import type {
  Catalog,
  EngineError,
  ExportFormat,
  GlossaryEntry,
  ExportResult,
  Lesson,
  LessonProgress,
  RunResult,
  SearchResult,
  ShotsResult,
  ValidationResult,
} from "../engine/types";
import { t } from "../strings";
import { loadLocalProgress, saveLocalProgress } from "../lib/localProgress";
import { clampStep, stepForLine } from "../lib/steps";

const RUN_DEBOUNCE_MS = 200;
const SAVE_DEBOUNCE_MS = 1500;
export const SANDBOX_ID = "sandbox";

/** Código inicial do laboratório livre. */
export function sandboxCode(): string {
  return `from qiskit import QuantumCircuit

${t("lab.sandboxCode")}
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
`;
}

/** Curva do treino em andamento (ou do último), alimentada por report(...) no código. */
export interface TrainingState {
  series: Record<string, number[]>;
  active: boolean;
}

/** O código chama report(...) fora de um comentário: é um treino, roda pelo botão. */
export interface HardwareJob {
  job_id: string;
  backend?: string;
  status?: string;
  counts?: Record<string, number>;
  error?: string;
}

export function usesReport(code: string): boolean {
  return /^[^#\n]*\breport\s*\(/m.test(code);
}

/** Código que só roda pelo botão Executar: lições de treino e treinos no laboratório livre. */
export function selectManual(state: Pick<State, "lesson" | "code">): boolean {
  return state.lesson ? state.lesson.live === false : usesReport(state.code);
}

interface State {
  connection: ConnectionStatus;
  view: "hub" | "lab";
  catalog: Catalog | null;
  progress: Record<string, LessonProgress>;
  glossary: GlossaryEntry[];
  /** "client": motor hospedado, o progresso fica neste navegador. */
  progressStorage: "engine" | "client";
  reloadProgress(): void;
  loadError: string | null;

  lesson: Lesson | null; // null no laboratório livre
  code: string;
  result: RunResult | null; // último resultado válido
  resultIsCurrent: boolean; // false enquanto o código mudou e ainda não há resultado novo
  error: EngineError | null;
  cursorLine: number;
  followCursor: boolean;
  manualStep: number;
  seed: number;
  validation: ValidationResult | null;
  validating: boolean;
  shots: ShotsResult | null;
  hintsShown: number;
  /** Desafio opcional da lição (liberado depois da missão). */
  challengeMode: boolean;
  challengeHintsShown: number;
  startChallenge(): void;
  leaveChallenge(): void;
  /** Valores dos controles da lição (ex.: erro injetado). */
  controls: Record<string, string | number | null>;
  running: boolean;
  training: TrainingState | null;

  init(): void;
  runNow(): void;
  stopRun(): void;
  /** Computador quântico real (IBM): só com o motor local e o pacote opcional instalado. */
  hardwareAvailable: boolean;
  submitHardware(options: { token: string; instance: string; shots: number }): Promise<EngineResponse<HardwareJob>>;
  hardwareStatus(options: { jobId: string; token: string; instance: string }): Promise<EngineResponse<HardwareJob>>;
  simulateCounts(shots: number): Promise<EngineResponse<ShotsResult>>;
  exportCircuit(format: ExportFormat): Promise<EngineResponse<ExportResult>>;
  search(query: string): Promise<SearchResult[]>;
  setControl(id: string, value: string | number | null): void;
  openLesson(id: string): Promise<void>;
  openSandbox(): void;
  /** Código vindo de um link: abre no laboratório sem executar até o aluno confirmar. */
  openShared(code: string): void;
  trustShared(): void;
  /** false enquanto o código de um link não foi revisado e aceito. */
  codeTrusted: boolean;
  backToHub(): void;
  setCode(code: string): void;
  resetCode(): void;
  setCursorLine(line: number): void;
  setStep(step: number): void;
  setFollowCursor(follow: boolean): void;
  reseed(): void;
  validate(): Promise<void>;
  runShots(): Promise<void>;
  showNextHint(): void;
}

let client: EngineClient | null = null;
let runTimer: number | undefined;
let saveTimer: number | undefined;
let runToken = 0;
let trainRequest: number | null = null;

function engine(): EngineClient {
  if (!client) throw new Error("Motor não inicializado.");
  return client;
}

export const useStore = create<State>((set, get) => {
  async function loadCatalog(): Promise<void> {
    try {
      const response = await engine().call<{
        catalog: Catalog;
        progress: Record<string, LessonProgress>;
        progress_storage?: "engine" | "client";
        glossary?: GlossaryEntry[];
      }>("catalog");
      if (response.ok) {
        const storage = response.progress_storage ?? "engine";
        const progress = storage === "client" ? loadLocalProgress() : response.progress;
        set({ catalog: response.catalog, progress, progressStorage: storage, glossary: response.glossary ?? [], loadError: null });
      }
      else set({ loadError: response.error?.message ?? t("hub.loadCatalogFailed") });
    } catch {
      // Sem conexão: o aviso de conexão já aparece; nova tentativa ao reconectar.
    }
  }

  async function run(): Promise<void> {
    const token = ++runToken;
    const { code, lesson, seed } = get();
    try {
      set({ running: true });
      const response = await engine()
        .call<RunResult>("run", { code, seed, lesson_id: lesson?.id ?? null, controls: get().controls, challenge: get().challengeMode })
        .finally(() => {
          if (token === runToken) set({ running: false });
        });
      if (token !== runToken) return; // chegou uma edição mais nova
      if (response.ok) {
        set({ result: response, resultIsCurrent: true, error: null });
      } else if (!response.stale) {
        set({ error: response.error ?? null, resultIsCurrent: false });
      }
    } catch {
      // Conexão caiu: mantém o último estado válido na tela.
    }
  }

  /** Execução pelo botão: as métricas de report(...) chegam em lotes enquanto o código roda. */
  async function train(): Promise<void> {
    const token = ++runToken;
    window.clearTimeout(runTimer);
    const { code, lesson, seed } = get();
    set({ running: true, training: { series: {}, active: true } });
    try {
      const request = await engine().start<RunResult>(
        "run",
        { code, seed, lesson_id: lesson?.id ?? null, controls: get().controls, challenge: get().challengeMode, train: true },
        (event) => {
          if (token !== runToken) return;
          const series = { ...(get().training?.series ?? {}) };
          for (const [name, values] of Object.entries(event.series as Record<string, number[]>)) {
            series[name] = [...(series[name] ?? []), ...values];
          }
          set({ training: { series, active: true } });
        },
      );
      trainRequest = request.id;
      const response = await request.done;
      if (token !== runToken) return;
      if (response.ok) {
        set({
          result: response,
          resultIsCurrent: true,
          error: null,
          training: response.training ? { series: response.training.series, active: false } : null,
        });
      } else if (!response.stale) {
        const partial = get().training;
        set({
          error: response.error ?? null,
          resultIsCurrent: false,
          training: partial && Object.keys(partial.series).length ? { ...partial, active: false } : null,
        });
      }
    } catch {
      // Conexão caiu: mantém o último estado válido na tela.
    } finally {
      trainRequest = null;
      if (token === runToken) set({ running: false });
    }
  }

  function scheduleRun(delay = RUN_DEBOUNCE_MS): void {
    window.clearTimeout(runTimer);
    // Um treino no laboratório livre pode levar minutos: só roda pelo botão.
    if (!get().lesson && usesReport(get().code)) return;
    // Código de um link roda na máquina de quem abre: só depois de revisado.
    if (!get().codeTrusted) return;
    runTimer = window.setTimeout(() => void run(), delay);
  }

  function scheduleSave(): void {
    if (!get().codeTrusted) return; // código de um link só é salvo depois de aceito
    const lessonId = get().lesson?.id ?? SANDBOX_ID;
    window.clearTimeout(saveTimer);
    saveTimer = window.setTimeout(() => {
      if (get().progressStorage === "client") {
        set({ progress: saveLocalProgress(lessonId, { code: get().code, hints_used: get().hintsShown }) });
        return;
      }
      void engine()
        .call("progress.save", { lesson_id: lessonId, code: get().code, hints_used: get().hintsShown })
        .catch(() => undefined);
    }, SAVE_DEBOUNCE_MS);
  }

  function defaultControls(lesson: Lesson | null): Record<string, string | number | null> {
    return Object.fromEntries((lesson?.controls ?? []).map((control) => [control.id, control.default]));
  }

  /** Treinos rodam só pelo botão; o resto, a cada pausa na digitação. */
  function isLive(): boolean {
    return !selectManual(get());
  }

  function enterLab(lesson: Lesson | null, code: string, hintsShown: number, trusted = true): void {
    set({
      codeTrusted: trusted,
      view: "lab",
      lesson,
      code,
      result: null,
      resultIsCurrent: false,
      error: null,
      cursorLine: code.split("\n").length,
      followCursor: true,
      manualStep: 0,
      seed: 0,
      validation: null,
      shots: null,
      hintsShown,
      challengeMode: false,
      challengeHintsShown: 0,
      controls: defaultControls(lesson),
      running: false,
      training: null,
    });
    scheduleRun(0);
  }

  return {
    connection: "connecting",
    view: "hub",
    catalog: null,
    progress: {},
    glossary: [],
    progressStorage: "engine",
    codeTrusted: true,
    hardwareAvailable: false,
    loadError: null,
    lesson: null,
    code: "",
    result: null,
    resultIsCurrent: false,
    error: null,
    cursorLine: 1,
    followCursor: true,
    manualStep: 0,
    seed: 0,
    validation: null,
    validating: false,
    shots: null,
    hintsShown: 0,
    challengeMode: false,
    challengeHintsShown: 0,
    controls: {},
    running: false,
    training: null,

    reloadProgress() {
      if (get().progressStorage === "client") set({ progress: loadLocalProgress() });
    },

    init() {
      if (client) return;
      client = new EngineClient(
        resolveEndpoint,
        (status) => {
          const previous = get().connection;
          set({ connection: status });
          if (status === "open" && previous !== "open") {
            void loadCatalog();
            void engine()
              .call<{ available: boolean }>("hardware.available")
              .then((response) => set({ hardwareAvailable: response.ok && response.available }))
              .catch(() => undefined);
            if (get().view === "lab") scheduleRun(0);
          }
        },
        (message) => set({ loadError: message }),
      );
      void client.connect().catch(() => undefined);
    },

    async openLesson(id) {
      const response = await engine().call<{ lesson: Lesson }>("lesson", { lesson_id: id });
      if (!response.ok) {
        set({ loadError: response.error?.message ?? t("hub.openLessonFailed") });
        return;
      }
      const saved = get().progress[id];
      enterLab(response.lesson, saved?.code ?? response.lesson.starter_code, saved?.hints_used ?? 0);
    },

    openSandbox() {
      enterLab(null, get().progress[SANDBOX_ID]?.code ?? sandboxCode(), 0);
    },

    openShared(code) {
      enterLab(null, code, 0, false);
    },

    trustShared() {
      set({ codeTrusted: true });
      scheduleRun(0);
    },

    backToHub() {
      window.clearTimeout(runTimer);
      set({ view: "hub" });
      void loadCatalog();
    },

    setCode(code) {
      if (code === get().code) return;
      set({ code, resultIsCurrent: false, validation: null, shots: null });
      // Laboratório livre: sem report(...) no código, a curva do treino anterior sai de cena.
      if (!get().lesson && get().training && !get().training!.active && !usesReport(code)) set({ training: null });
      if (isLive()) scheduleRun();
      scheduleSave();
    },

    resetCode() {
      const { lesson } = get();
      get().setCode(lesson ? lesson.starter_code : sandboxCode());
    },

    setCursorLine(line) {
      if (line !== get().cursorLine || !get().followCursor) set({ cursorLine: line, followCursor: true });
    },

    setStep(step) {
      const count = get().result?.steps.length ?? 0;
      set({ manualStep: clampStep(step, count), followCursor: false });
    },

    setFollowCursor(follow) {
      set({ followCursor: follow, manualStep: selectCurrentStep(get()) });
    },

    runNow() {
      if (!get().codeTrusted) return;
      if (selectManual(get())) {
        // Uma execução ao vivo (de antes de o código virar treino) pode estar em andamento: o treino a substitui.
        if (!get().training?.active) void train();
      }
      else scheduleRun(0);
    },

    submitHardware({ token, instance, shots }) {
      const { code, lesson, controls } = get();
      return engine().call<HardwareJob>("hardware.submit", { code, lesson_id: lesson?.id ?? null, controls, token, instance, shots, challenge: get().challengeMode });
    },

    hardwareStatus({ jobId, token, instance }) {
      return engine().call<HardwareJob>("hardware.status", { job_id: jobId, token, instance });
    },

    simulateCounts(shots) {
      const { code, lesson, controls } = get();
      return engine().call<ShotsResult>("shots", { code, shots, seed: 0, lesson_id: lesson?.id ?? null, controls, challenge: get().challengeMode });
    },

    stopRun() {
      if (trainRequest !== null) void engine().call("cancel", { target: trainRequest }).catch(() => undefined);
    },

    exportCircuit(format) {
      const { code, lesson, controls } = get();
      return engine().call<ExportResult>("export", { code, format, lesson_id: lesson?.id ?? null, controls, challenge: get().challengeMode });
    },

    async search(query) {
      if (get().connection !== "open" || !query.trim()) return [];
      try {
        const response = await engine().call<{ results: SearchResult[] }>("search", { query });
        return response.ok ? response.results : [];
      } catch {
        return [];
      }
    },

    setControl(id, value) {
      set({ controls: { ...get().controls, [id]: value }, shots: null, validation: null });
      scheduleRun(0);
    },

    reseed() {
      set({ seed: get().seed + 1, shots: null });
      scheduleRun(0);
    },

    async validate() {
      const { lesson, code } = get();
      if (!lesson) return;
      set({ validating: true });
      try {
        const challenge = get().challengeMode;
        const response = await engine().call<ValidationResult>("validate", { code, lesson_id: lesson.id, challenge });
        if (response.ok) {
          set({ validation: response });
          if (response.passed) {
            // O desafio tem progresso próprio, na chave "<id>:challenge".
            const key = challenge ? `${lesson.id}:challenge` : lesson.id;
            const entry = { code, completed: true, hints_used: challenge ? get().challengeHintsShown : get().hintsShown };
            set({
              progress: get().progressStorage === "client"
                ? saveLocalProgress(key, entry)
                : { ...get().progress, [key]: entry },
            });
          }
        } else if (response.error) {
          set({ error: response.error });
        }
      } catch {
        // Aviso de conexão já visível.
      } finally {
        set({ validating: false });
      }
    },

    async runShots() {
      const { code, lesson, seed } = get();
      if (!get().codeTrusted) return;
      try {
        const response = await engine().call<ShotsResult>("shots", {
          code,
          shots: 1024,
          seed: seed + Math.floor(Math.random() * 1e6),
          lesson_id: lesson?.id ?? null,
          controls: get().controls,
          challenge: get().challengeMode,
        });
        if (response.ok) set({ shots: response });
        else if (response.error) set({ error: response.error });
      } catch {
        // Aviso de conexão já visível.
      }
    },

    startChallenge() {
      set({ challengeMode: true, challengeHintsShown: 0, validation: null });
      scheduleRun(0);
    },

    leaveChallenge() {
      set({ challengeMode: false, validation: null });
      scheduleRun(0);
    },

    showNextHint() {
      const { lesson, hintsShown, challengeMode, challengeHintsShown } = get();
      if (challengeMode) {
        if (lesson?.challenge && challengeHintsShown < lesson.challenge.hints.length) {
          set({ challengeHintsShown: challengeHintsShown + 1 });
        }
        return;
      }
      if (lesson && hintsShown < lesson.hints.length) {
        set({ hintsShown: hintsShown + 1 });
        scheduleSave();
      }
    },
  };
});

/** Índice do snapshot em exibição: segue o cursor ou a linha do tempo. */
export function selectCurrentStep(state: Pick<State, "result" | "followCursor" | "cursorLine" | "manualStep">): number {
  if (!state.result) return 0;
  const count = state.result.steps.length;
  return state.followCursor ? stepForLine(state.result.steps, state.cursorLine) : clampStep(state.manualStep, count);
}

/** Próxima lição disponível depois da atual, se houver. */
export function selectNextLessonId(state: Pick<State, "catalog" | "lesson">): string | null {
  if (!state.catalog || !state.lesson) return null;
  const sections = state.catalog.tracks.flatMap((track) => track.sections);
  const index = sections.findIndex((section) => section.id === state.lesson!.id);
  const next = sections.slice(index + 1).find((section) => section.available);
  return next?.id ?? null;
}
