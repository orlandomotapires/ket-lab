export type Complex = [re: number, im: number];
export type Vec3 = [x: number, y: number, z: number];

export interface Snapshot {
  /** null em estados mistos (circuitos com ruído). */
  amplitudes: Complex[] | null;
  probabilities: number[];
  /** Tr(ρ²) do estado inteiro: 1 para estados puros. */
  state_purity: number;
  bloch: Vec3[];
  purity: number[];
}

export interface Step {
  index: number;
  line: number;
  kind: "gate" | "measure" | "reset" | "noop" | "conditional";
  name: string;
  label: string;
  qubits: number[];
  clbits: number[];
  num_ctrl: number;
  outcome: number | null;
  applied: boolean | null;
}

export interface RunResult {
  num_qubits: number;
  num_clbits: number;
  steps: Step[];
  snapshots: Snapshot[];
  /** Dados das visualizações de treino, gerados pelo analysis.py da lição. */
  analysis?: Record<string, unknown> & { error?: string };
  clbits: number[];
  has_measurement: boolean;
  stdout: string;
}

export interface EngineError {
  message: string;
  line: number | null;
  kind: string;
}

export interface ValidationResult {
  passed: boolean;
  code: string;
  message: string;
  fidelity: number | null;
  line: number | null;
}

export interface ShotsResult {
  shots: number;
  counts: Record<string, number>;
  measured: "clbits" | "qubits";
  width: number;
}

export interface CatalogSection {
  id: string;
  title: string;
  summary: string;
  available: boolean;
}

export interface CatalogTrack {
  id: number;
  title: string;
  level: string;
  sections: CatalogSection[];
}

export interface Catalog {
  tracks: CatalogTrack[];
}

export interface LessonProgress {
  code: string | null;
  completed: boolean;
  hints_used: number;
}

export interface Prediction {
  question: string;
  options: string[];
  answer: number;
  explanation: string;
}

export interface SearchResult {
  id: string;
  track: number;
  title: string;
  snippet: string;
}

export interface Reference {
  kind: "book" | "paper" | "course" | "tutorial";
  title: string;
  authors: string;
  year?: number;
  section?: string;
  url: string;
}

export type VisualizerKind =
  | "bloch" | "qsphere" | "compare" | "amplitudes" | "dials" | "histogram" | "modular"
  | "landscape" | "convergence" | "dissociation" | "graph" | "boundary" | "threshold";

export interface LessonControl {
  id: string;
  options: (string | number | null)[];
  default: string | number | null;
  label: string;
  option_labels: Record<string, string>;
}

export interface Comparison {
  source_qubit: number;
  /** Trecho de código: o estado de origem é o da linha onde ele aparece. */
  source_marker: string;
  target_qubit: number;
  source_label: string;
  target_label: string;
}

export interface Lesson {
  id: string;
  track: number;
  title: string;
  summary: string;
  estimated_minutes?: number;
  num_qubits: number;
  mission: string;
  prediction?: Prediction;
  hints: string[];
  theory: string;
  starter_code: string;
  default_visualizer: VisualizerKind;
  available_visualizers: VisualizerKind[];
  comparison?: Comparison;
  /** Qubits mostrados nas visualizações de amplitudes, fases e histograma. */
  register?: { qubits: number[] };
  modular?: { a: number; N: number };
  framework?: "qiskit" | "pennylane";
  /** false: o código roda só pelo botão Executar (treinos demorados). */
  live?: boolean;
  controls?: LessonControl[];
  references?: Reference[];
  lang: string;
}
