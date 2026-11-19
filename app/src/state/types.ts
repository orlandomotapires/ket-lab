import type { ConnectionStatus, EngineLoading, EngineResponse } from "../engine/client";
import type {
  Catalog,
  EngineError,
  ExportFormat,
  ExportResult,
  GlossaryEntry,
  Lesson,
  LessonProgress,
  NoteHit,
  Notes,
  ReviewQuestion,
  RunResult,
  SearchResult,
  ShotsResult,
  ValidationResult,
} from "../engine/types";
import type { BibliographyData } from "../components/Bibliography";

/** Curve of the training run in progress (or the last one), fed by report(...) in the code. */
export interface TrainingState {
  series: Record<string, number[]>;
  active: boolean;
}

export interface HardwareJob {
  job_id: string;
  backend?: string;
  status?: string;
  counts?: Record<string, number>;
  error?: string;
}

export type View = "hub" | "lab" | "references" | "review" | "notes" | "glossary";

/** Engine and connection: catalog, search, references. */
export interface ConnectionSlice {
  connection: ConnectionStatus;
  /** Browser engine only: its loading steps while it (re)starts. */
  engineLoading: EngineLoading | null;
  view: View;
  catalog: Catalog | null;
  glossary: GlossaryEntry[];
  loadError: string | null;
  init(): void;
  backToHub(): void;
  openReferences(): void;
  openNotesPage(): void;
  /** Term to show first on the glossary page, and where its Back button returns to. */
  glossaryFocus: string | null;
  glossaryReturn: "hub" | "lab";
  openGlossary(term?: string): void;
  closeGlossary(): void;
  loadBibliography(): Promise<BibliographyData | null>;
  search(query: string): Promise<{ results: SearchResult[]; notes: NoteHit[] }>;
}

/** Progress: in the local engine (SQLite) or in this browser (hosted engine). */
export interface ProgressSlice {
  progress: Record<string, LessonProgress>;
  /** "client": hosted engine, progress stays in this browser. */
  progressStorage: "engine" | "client";
  reloadProgress(): void;
}

/** Open lesson (or free lab) and the code execution. */
export interface LabSlice {
  lesson: Lesson | null; // null in the free lab
  code: string;
  result: RunResult | null; // last valid result
  resultIsCurrent: boolean; // false while the code has changed and there is no new result yet
  error: EngineError | null;
  /** What the code printed before it failed (the engine sends it with the error). */
  errorStdout: string;
  cursorLine: number;
  followCursor: boolean;
  manualStep: number;
  seed: number;
  shots: ShotsResult | null;
  /** Values of the lesson controls (e.g. injected error). */
  controls: Record<string, string | number | null>;
  running: boolean;
  training: TrainingState | null;
  /** false while the code from a link has not been reviewed and accepted. */
  codeTrusted: boolean;
  openLesson(id: string): Promise<void>;
  openSandbox(): void;
  /** Code coming from a link: opens in the lab without running until the learner confirms. */
  openShared(code: string): void;
  trustShared(): void;
  setCode(code: string): void;
  resetCode(): void;
  setCursorLine(line: number): void;
  setStep(step: number): void;
  setFollowCursor(follow: boolean): void;
  setControl(id: string, value: string | number | null): void;
  reseed(): void;
  runNow(): void;
  stopRun(): void;
  runShots(): Promise<void>;
}

/** Mission, hints, challenge and annotated solution. */
export interface MissionSlice {
  validation: ValidationResult | null;
  validating: boolean;
  /** Stops the Check in progress (the engine kills the worker; nothing is saved). */
  stopValidation(): void;
  hintsShown: number;
  /** Optional lesson challenge (unlocked after the mission). */
  challengeMode: boolean;
  challengeHintsShown: number;
  /** Annotated solution on display (of the mission or the challenge, depending on the mode). */
  solution: string | null;
  validate(): Promise<void>;
  showNextHint(): void;
  startChallenge(): void;
  leaveChallenge(): void;
  showSolution(): Promise<void>;
  hideSolution(): void;
}

/** Real quantum computer (IBM), simulated measurements and circuit export. */
export interface HardwareSlice {
  /** Only with the local engine and the optional package installed. */
  hardwareAvailable: boolean;
  submitHardware(options: { token: string; instance: string; shots: number }): Promise<EngineResponse<HardwareJob>>;
  hardwareStatus(options: { jobId: string; token: string; instance: string }): Promise<EngineResponse<HardwareJob>>;
  simulateCounts(shots: number): Promise<EngineResponse<ShotsResult>>;
  exportCircuit(format: ExportFormat): Promise<EngineResponse<ExportResult>>;
}

/** End-of-track review. */
export interface ReviewSlice {
  reviewTrack: number | null;
  reviewQuestions: ReviewQuestion[];
  openReview(track: number): Promise<void>;
  /** Saves the best score of the track (key "review:<track>"). */
  saveReviewScore(score: number): void;
}

/** Notes of the learner: one per lesson plus a general one. */
export interface NotesSlice {
  notes: Notes;
  /** "client": notes stay in this browser (hosted engine). */
  notesStorage: "engine" | "client";
  notesStatus: "idle" | "saving" | "saved" | "error";
  /** Notes drawer of the lab. */
  notesOpen: boolean;
  loadNotes(storage: "engine" | "client"): Promise<void>;
  setNote(key: string, body: string): void;
  flushNotes(): void;
  setNotesOpen(open: boolean): void;
  /** Restores an exported backup (progress and notes); throws when the file is not one. */
  importBackup(text: string): Promise<{ lessons: number; notes: number }>;
}

export type State = ConnectionSlice & ProgressSlice & LabSlice & MissionSlice & HardwareSlice & ReviewSlice & NotesSlice;

export type Set = (partial: Partial<State>) => void;
export type Get = () => State;
