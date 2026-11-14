import { create } from "zustand";
import { EngineClient, resolveEndpoint, type ConnectionStatus } from "../engine/client";
import type {
  Catalog,
  EngineError,
  Lesson,
  LessonProgress,
  RunResult,
  ShotsResult,
  ValidationResult,
} from "../engine/types";
import { onLocaleChange, t } from "../i18n";
import { clampStep, stepForLine } from "../lib/steps";

const RUN_DEBOUNCE_MS = 200;
const SAVE_DEBOUNCE_MS = 1500;
export const SANDBOX_ID = "sandbox";

/** Código inicial do laboratório livre, com o comentário no idioma atual. */
export function sandboxCode(): string {
  return `from qiskit import QuantumCircuit

${t("lab.sandboxCode")}
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
`;
}

interface State {
  connection: ConnectionStatus;
  view: "hub" | "lab";
  catalog: Catalog | null;
  progress: Record<string, LessonProgress>;
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
  /** Valores dos controles da lição (ex.: erro injetado). */
  controls: Record<string, string | number | null>;
  running: boolean;

  init(): void;
  runNow(): void;
  setControl(id: string, value: string | number | null): void;
  openLesson(id: string): Promise<void>;
  openSandbox(): void;
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

function engine(): EngineClient {
  if (!client) throw new Error("Motor não inicializado.");
  return client;
}

export const useStore = create<State>((set, get) => {
  async function loadCatalog(): Promise<void> {
    try {
      const response = await engine().call<{ catalog: Catalog; progress: Record<string, LessonProgress> }>("catalog");
      if (response.ok) set({ catalog: response.catalog, progress: response.progress, loadError: null });
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
        .call<RunResult>("run", { code, seed, lesson_id: lesson?.id ?? null, controls: get().controls })
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

  /** Troca de idioma: recarrega catálogo e textos da lição. O código do aluno fica,
   *  a menos que ainda seja o código inicial intocado (aí vem o do novo idioma). */
  async function reloadForLocale(): Promise<void> {
    if (get().connection !== "open") return;
    await loadCatalog();
    const current = get().lesson;
    if (get().view !== "lab") return;
    if (!current) {
      if (get().code.startsWith("from qiskit import QuantumCircuit\n\n#") && get().code.endsWith("qc.cx(0, 1)\n")) {
        set({ code: sandboxCode() });
      }
      scheduleRun(0);
      return;
    }
    try {
      const response = await engine().call<{ lesson: Lesson }>("lesson", { lesson_id: current.id });
      if (!response.ok || get().lesson?.id !== current.id) return;
      const pristine = get().code === current.starter_code;
      set({ lesson: response.lesson, validation: null, ...(pristine ? { code: response.lesson.starter_code } : {}) });
      scheduleRun(0); // mensagens de erro do motor também mudam de idioma
    } catch {
      // Sem conexão: os textos antigos ficam até a próxima troca.
    }
  }

  function scheduleRun(delay = RUN_DEBOUNCE_MS): void {
    window.clearTimeout(runTimer);
    runTimer = window.setTimeout(() => void run(), delay);
  }

  function scheduleSave(): void {
    const lessonId = get().lesson?.id ?? SANDBOX_ID;
    window.clearTimeout(saveTimer);
    saveTimer = window.setTimeout(() => {
      void engine()
        .call("progress.save", { lesson_id: lessonId, code: get().code, hints_used: get().hintsShown })
        .catch(() => undefined);
    }, SAVE_DEBOUNCE_MS);
  }

  function defaultControls(lesson: Lesson | null): Record<string, string | number | null> {
    return Object.fromEntries((lesson?.controls ?? []).map((control) => [control.id, control.default]));
  }

  /** Lições de treino (live: false) rodam só pelo botão; as demais, a cada pausa na digitação. */
  function isLive(): boolean {
    return get().lesson?.live !== false;
  }

  function enterLab(lesson: Lesson | null, code: string, hintsShown: number): void {
    set({
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
      controls: defaultControls(lesson),
      running: false,
    });
    scheduleRun(0);
  }

  return {
    connection: "connecting",
    view: "hub",
    catalog: null,
    progress: {},
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
    controls: {},
    running: false,

    init() {
      if (client) return;
      client = new EngineClient(
        resolveEndpoint,
        (status) => {
          const previous = get().connection;
          set({ connection: status });
          if (status === "open" && previous !== "open") {
            void loadCatalog();
            if (get().view === "lab") scheduleRun(0);
          }
        },
        (message) => set({ loadError: message }),
      );
      onLocaleChange(() => void reloadForLocale());
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

    backToHub() {
      window.clearTimeout(runTimer);
      set({ view: "hub" });
      void loadCatalog();
    },

    setCode(code) {
      if (code === get().code) return;
      set({ code, resultIsCurrent: false, validation: null, shots: null });
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
      scheduleRun(0);
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
        const response = await engine().call<ValidationResult>("validate", { code, lesson_id: lesson.id });
        if (response.ok) {
          set({ validation: response });
          if (response.passed) {
            set({ progress: { ...get().progress, [lesson.id]: { code, completed: true, hints_used: get().hintsShown } } });
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
      try {
        const response = await engine().call<ShotsResult>("shots", {
          code,
          shots: 1024,
          seed: seed + Math.floor(Math.random() * 1e6),
          lesson_id: lesson?.id ?? null,
          controls: get().controls,
        });
        if (response.ok) set({ shots: response });
        else if (response.error) set({ error: response.error });
      } catch {
        // Aviso de conexão já visível.
      }
    },

    showNextHint() {
      const { lesson, hintsShown } = get();
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
