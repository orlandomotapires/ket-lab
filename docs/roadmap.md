# Roadmap

Prioritized plan for the next stages of the platform. Each item has a goal, the work, what "done" means and a rough effort (S ≤ 2 days, M ≤ 1 week, L ≤ 3 weeks, XL > 3 weeks, for one developer). Items within a phase can run in parallel unless a dependency is listed.

The order follows one rule: protect what exists, decide how the platform reaches learners, then fill the curriculum, then polish and extend.

---

## Phase 0: Safety net

Everything after this changes a lot of code and content. These two items make regressions visible.

### 0.1 Run CI on the current work (S)

- **Goal:** the 60+ commits on `trilha-3` have never run in CI, which only triggers on `main` and on pull requests.
- **Work:** open a pull request `trilha-3 → main`; fix whatever fails on Windows and macOS (the engine job runs on three systems); merge.
- **Done when:** the CI is green on all three systems and `main` holds the current platform.

### 0.2 End-to-end tests in CI (M)

- **Goal:** the interface has 21 unit tests; real flows were checked by hand with headless scripts.
- **Work:** add Playwright; start engine and Vite in the test job; cover: hub loads and search opens a lesson; a Track 1 lesson solved and checked; a Track 2 lesson with secret oracles; a Track 3 training run with live curve and Stop; OpenQASM export; both themes; no console errors.
- **Done when:** the suite runs in CI in under 5 minutes and fails on a broken flow.
- **Depends on:** 0.1.

---

## Phase 1: How the platform reaches learners

Today it runs only after `npm run setup` and `npm run dev` on the learner's machine. This decision changes what is possible in later phases (accounts, real hardware, Qiskit Aer), so it comes early.

### 1.1 Spike: the engine in the browser with Pyodide (M, time-boxed to 5 days)

- **Goal:** find out whether the whole engine can run client-side, which would make the platform a static website with no server and no code-execution risk.
- **Work:** load the simulator, tracer, validation and PennyLane in Pyodide inside a Web Worker. Qiskit is the blocker (its core is compiled Rust): test whether a thin Qiskit-compatible `QuantumCircuit` API (the subset the lessons use: gates, measure, `if_test`, classical bits) can replace it in the browser. Measure load time and run time for lessons 1.1, 2.5, 2.8 and 3.3.
- **Done when:** a written decision with numbers: first load under ~10 s, a live run under ~300 ms for Tracks 1–2, training lessons still usable. Either "go" with known gaps or "no-go" with the reason.

### 1.2a If the spike succeeds: static web version (L)

- **Work:** engine in a Web Worker; WebSocket client replaced by worker messages (same protocol); progress in IndexedDB with export/import; deploy as a static site (GitHub Pages or similar). Keep the local Python engine as the development and testing path.
- **Done when:** the platform opens from a URL with no install, and all content tests also run against the browser engine.

### 1.2b If the spike fails: hosted engine with real isolation (XL)

- **Work:** one sandbox per session (container with gVisor or Firecracker microVM), CPU/memory/time limits, no network, short-lived; a gateway that authenticates sessions and routes WebSocket traffic; autoscaling and cost limits. The AST check in `guard.py` stays as a source of clear error messages, not as the security boundary.
- **Done when:** a security review of the sandbox passes and a load test holds the expected number of learners.

### 1.3 Accounts and progress sync (M, only for 1.2b or if multi-device sync is wanted)

- **Work:** sign-in (GitHub/Google OAuth), progress stored server-side, migration from the local SQLite file.
- **Done when:** progress follows the learner between devices.
- **Depends on:** 1.2a or 1.2b.

---

## Phase 2: Close the curriculum gaps

Compared with the IBM Quantum Learning courses and Nielsen & Chuang, the platform misses a few topics that the existing tracks lead up to. These have the highest learning value per effort. Each new lesson follows `docs/guia-de-escrita.md` and the existing lesson format (manifest, text, theory, starter code, solution, references with exact locations).

### 2.1 Learning objectives in every lesson (S)

- **Goal:** state what the learner will be able to do, and make sure the mission checks it.
- **Work:** add `objectives` (2–3 lines) to `text.json`; show them under the lesson title; content test requiring them; review each mission against its objectives.
- **Done when:** all lessons have objectives, and each objective is exercised by the mission, a hint or the prediction question.

### 2.2 Track 1 additions (M)

- **Superdense coding:** send two classical bits with one qubit and a shared Bell pair (IBM, "Entanglement in action"; N&C §2.3).
- **The CHSH game:** entanglement as a resource, with the 85% vs 75% win probability (IBM, "Entanglement in action"; Griffiths §12.2).
- **The no-cloning theorem:** a short lesson with a mission that shows CNOT copies basis states but not |+⟩ (IBM, "Limitations on quantum information"; Griffiths §12.4).
- **Done when:** three lessons pass the content suite; the hub shows Track 1 with 10 lessons.

### 2.3 Simon's algorithm in Track 2 (M)

- **Goal:** the missing step between Bernstein–Vazirani and Shor: period finding over bit strings, with exponential separation from classical query complexity.
- **Work:** a new lesson after 2.4, with a validator that runs several secret strings s and checks the learner's classical post-processing (solving the linear system mod 2).
- **Done when:** the lesson passes the suite with several secret strings; Track 2 numbering is updated.

### 2.4 Split Track 3 into two tracks (L)

- **Goal:** Track 3 mixes two subjects. Splitting gives each the depth the IBM courses have.
- **Track 3, Variational Algorithms:** current lessons 3.1 to 3.4, plus "Ansätze and variational forms" and "Barren plateaus" as theory sections.
- **Track 4, Quantum Noise and Error Correction:** current 3.5 and 3.6, plus:
  - the phase-flip code (N&C §10.1.2);
  - the 9-qubit Shor code (N&C §10.2; IBM "The 9-qubit Shor code");
  - the stabilizer formalism (N&C §10.5; IBM "The stabilizer formalism");
  - an intuition for the surface code (IBM "Toric code"), as theory with a small simulation;
  - the threshold theorem as a lesson (N&C §10.6.1; IBM "The threshold theorem").
- **Done when:** both tracks are in the catalog with official names; the new lessons pass the suite.

### 2.5 Hamiltonian simulation (M)

- **Goal:** the most important practical application not covered.
- **Work:** a Track 2 lesson on Trotterization: evolve a two-qubit Ising Hamiltonian, compare first- and second-order Trotter error with the exact evolution (N&C §4.7).
- **Done when:** the validator checks the error bound for the learner's step count.

### 2.6 Track 0: mathematical toolkit (L)

- **Goal:** learners without linear algebra struggle from lesson 1.5 onward.
- **Work:** 4–5 short lessons with numeric missions (no circuits): complex numbers and phases; vectors, inner products and normalization; matrices, unitarity and eigenvalues; tensor products. The validator checks Python/NumPy answers.
- **Done when:** the track is optional in the hub, and lessons 1.x link to the relevant toolkit lesson.

---

## Phase 3: Ready for more learners (design)

Before opening the platform widely (after Phase 1), it has to work for more people and more devices.

### 3.1 Responsive layout (M)

- **Work:** under ~1100 px, the lab switches to tabs (Theory, Code, State) with the bottom bar fixed; the hub stacks the side panel above the tracks; test at 768 px and 390 px.
- **Done when:** a lesson can be completed on a tablet; Playwright covers two viewport sizes.

### 3.2 Accessibility beyond contrast (M)

- **Work:** keyboard navigation of the circuit (arrow keys move between gates and sync the timeline); a text description of the Bloch sphere and Q-Sphere linked to the 3D view with `aria-describedby`; focus order audit; screen reader test (NVDA, VoiceOver).
- **Done when:** a WCAG 2.1 AA audit has no open issues on the hub and the lab.

### 3.3 First-run guide (S)

- **Work:** a 4-step walkthrough the first time a learner opens a lesson: the cursor drives the state, the timeline, the mission and hints, Check. Dismissible and never shown again.
- **Done when:** it appears once, can be reopened from the help menu, and works with the keyboard.

---

## Phase 4: Real hardware

This is where the platform connects to the IBM Quantum ecosystem in practice. Part of it depends on Phase 1: Qiskit Aer (noise models from real devices) is compiled C++ and needs a server engine.

### 4.1 Track 5, Running on Quantum Hardware (L)

- **Lessons:**
  - transpilation, basis gates and qubit connectivity (why a CNOT between distant qubits costs SWAPs);
  - the Qiskit primitives, Sampler and Estimator;
  - T1, T2 and readout error, simulated with fake backends;
  - basic error mitigation: readout mitigation and zero-noise extrapolation.
- **Done when:** the lessons pass the suite with simulated noise; references point to the IBM courses ("Quantum computing in practice", "Utility-scale quantum computing") with exact sections.
- **Depends on:** 1.2b, or a server-side job runner if 1.2a is chosen.

### 4.2 Run on a real IBM device (M)

- **Work:** the learner pastes their own IBM Quantum token; a "Run on hardware" button submits the current circuit as a Sampler job and shows the measured histogram next to the simulated one. The token stays on the learner's side, never stored on our servers.
- **Done when:** a Track 1 circuit runs on a real backend and the two histograms are shown side by side.
- **Depends on:** 4.1.

---

## Phase 5: Deeper practice and assessment

### 5.1 A second, harder mission per lesson (L)

- **Work:** an optional "challenge" mission per lesson (for example, Grover with two marked items and an unknown count; teleportation of a two-qubit state). Shown after the main mission is complete.
- **Done when:** at least one challenge in every lesson of Tracks 1 and 2.

### 5.2 A project at the end of each track (M per track)

- **Work:** a larger open task with a rubric checked by the validator: build and analyze your own Grover oracle (Track 2); VQE for LiH with a chosen ansatz (Track 3); decode the Shor code under noise (Track 4).
- **Done when:** each track ends with a project and the hub marks track completion.

### 5.3 Glossary (S)

- **Work:** terms from the writing guide become a glossary; hovering a term in the theory shows its definition and the lesson that introduces it.
- **Done when:** every term of the writing guide's terminology list has an entry.

---

## Phase 6: Further features

Valuable, but not needed for learning the current content. Each needs a decision before it starts.

### 6.1 Circuit composer (L)

- **Work:** drag gates onto wires; the code updates, and editing the code updates the diagram (two-way sync for the gate subset the Track 1 lessons use).
- **Done when:** lessons 1.1 to 1.5 can be solved with the composer alone.

### 6.2 Shareable lab snippets (M)

- **Work:** share a free-lab circuit by link. Needs the trust model listed in the master plan's open risks (shared code executes on someone else's engine); trivial with the browser engine (1.2a), serious with a server engine.
- **Depends on:** Phase 1 decision.

### 6.3 Classroom mode (L)

- **Work:** a teacher creates a class; sees each student's progress, hints used and failed checks per lesson.
- **Depends on:** 1.3 (accounts).

---

## Summary

| Order | Item | Effort | Depends on |
|---|---|---|---|
| 1 | 0.1 Run CI on current work | S | |
| 2 | 0.2 End-to-end tests in CI | M | 0.1 |
| 3 | 1.1 Pyodide spike (5 days) | M | |
| 4 | 2.1 Learning objectives | S | |
| 5 | 2.3 Simon's algorithm | M | |
| 6 | 2.2 Superdense coding, CHSH, no-cloning | M | |
| 7 | 1.2a Static web version, or 1.2b hosted engine | L / XL | 1.1 |
| 8 | 3.1 Responsive layout | M | |
| 9 | 3.2 Accessibility | M | |
| 10 | 3.3 First-run guide | S | |
| 11 | 2.4 Split Track 3; Noise and Error Correction track | L | |
| 12 | 2.5 Hamiltonian simulation | M | |
| 13 | 2.6 Track 0, math toolkit | L | |
| 14 | 1.3 Accounts and sync (if needed) | M | 1.2 |
| 15 | 4.1 Running on quantum hardware track | L | 1.2 |
| 16 | 4.2 Run on a real IBM device | M | 4.1 |
| 17 | 5.1 Challenge missions | L | |
| 18 | 5.2 Track projects | M each | |
| 19 | 5.3 Glossary | S | |
| 20 | 6.1 Circuit composer | L | |
| 21 | 6.2 Shareable snippets | M | 1.2 |
| 22 | 6.3 Classroom mode | L | 1.3 |

Phases 0–3 make the platform complete for its current scope and reachable without installing anything; Phases 4–6 extend it toward real hardware and teaching at scale.
