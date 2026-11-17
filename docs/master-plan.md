# Ket Lab: Master Plan

Version of 16 Nov 2026. **The project's single document**: it describes the platform as it is today, records what has been done and says what comes next. It replaces the old `roadmap.md` and `plano-de-revisao.md`.

The platform is a web application for **one person to study quantum computing alone**, from complex numbers to error correction and running on real hardware. The learner writes Qiskit or PennyLane code and sees the quantum state change at every gate, as they type. Each lesson has theory, a mathematically validated mission, hints and references with exact section and pages. There are no teachers, classes or accounts.

| Part | Content |
| :-- | :-- |
| [1 to 5](#1-architecture) | The platform today: architecture, study experience, curriculum, validation and content structure |
| [6](#6-history) | History, with the November 2026 roadmap item by item |
| [7](#7-current-situation) | Current situation in numbers |
| [8](#8-audit-of-16-nov-2026) | Audit of 16 Nov 2026: what is missing and what could be better, area by area |
| [9](#9-risks-and-open-decisions) | Risks and open decisions |
| [10](#10-next-steps) | Next steps, with the goal, work, done criterion and effort of each item |

Supporting documents: [writing guide](writing-guide.md), [adding a lesson](adding-a-lesson.md), [verified references](verified-references.md), [decision on the engine on the web](web-engine-decision.md) and the [deploy guide](../deploy/README.md).

---

## 1. Architecture

### 1.1 Layers

| Layer | Technology | Responsibility |
| :-- | :-- | :-- |
| Interface (`app/`) | React, TypeScript, Zustand, Monaco, Three.js (React Three Fiber), KaTeX | Track hub, lab (theory, editor, circuit, visualizations), reference pages. Runs in the browser. |
| Engine (`engine/`) | Python, Qiskit 2.6, PennyLane 0.45, NumPy, `websockets` | Runs the learner's code in an isolated process, simulates (state vector and density matrix), validates, searches, stores progress. |
| Content (`content/`) | JSON, Markdown with LaTeX, Python | Catalog, lessons, glossary, sources. The engine loads it at startup. |

Decisions that shape the architecture:

- **Web only.** There used to be a desktop shell (Tauri, with the engine packaged by PyInstaller); it was removed: for studying, the browser is enough.
- **The engine does not run in the browser.** Qiskit and rustworkx (a PennyLane dependency) have no WebAssembly build; a compatible substitute would move the learner away from the real Qiskit. Details in [web-engine-decision.md](web-engine-decision.md).
- **Own simulator.** State vector and density matrix in NumPy, fed by Qiskit instructions and by the operations of a PennyLane QNode. This gives one snapshot per instruction, which is what the interface shows; Qiskit Aer is not needed.
- **No FastAPI.** The engine only speaks WebSocket; the `websockets` library is enough.
- **Pinned versions** in `engine/pyproject.toml`: the lessons depend on the Qiskit and PennyLane APIs.
- **English only** in the interface, the messages and the content. The texts are centralized (`app/src/strings.ts`, `engine/qlp_engine/messages.py`), so other languages can come back later.

### 1.2 Engine modes

| | Local (`npm run dev`) | Single user in a container (`deploy/local.yml`) | Hosted (`deploy/docker-compose.yml`) |
| :-- | :-- | :-- | :-- |
| Where it runs | On the learner's machine, at 127.0.0.1 | In one container on the learner's machine; the engine also serves the interface (`--single-user`, `--static-dir`) | On a server, behind the site (nginx proxies `/engine`) |
| Access | Session token + list of origins | No token; list of origins; port published to this machine only | No token; the Origin must be the site's (`--public`) |
| Progress and notes | SQLite in the user's data directory, with a dated copy per day and export and import | SQLite in a Docker volume | In the browser (localStorage), with export and import |
| Parallelism | One worker | One worker | `--workers N`, with a connection cap |
| Real IBM hardware | Available (extra `engine[hardware]`) | Available | Off: a shared server does not receive third-party keys |

The container mode has been written but never run (P2.2).

The hosted mode is not yet ready for the public: it lacks per-session isolation (gVisor or microVM), a security review and a load test. See [deploy/README.md](../deploy/README.md).

### 1.3 The real-time cycle

1. **Capture.** 200 ms after the last keystroke, the interface sends the whole code.
2. **Single traced execution.** The code runs once; each instruction added to the circuit is recorded with the module-level line that originated it. In a PennyLane QNode, tracing happens inside the QNode function.
3. **Per-instruction simulation.** The engine keeps the state after each instruction and returns all snapshots at once.
4. **Geometric translation.** For each snapshot: amplitudes (or probabilities, for mixed states), Bloch vector and purity of each qubit, from the reduced state.
5. **Local navigation.** Moving the cursor or the timeline only switches the displayed snapshot.
6. **Interpolation.** The vector rotates on the sphere to the new state.

**Per instruction, not per line.** The cursor on line $L$ selects the last instruction, in execution order, whose source line is $\le L$. Instructions inside a function belong to the line that called it.

**Mid-circuit measurement.** The engine draws a branch with a seeded generator (the same seed reproduces the trajectory; "draw again" changes the branch). Gates with `if_test` follow the drawn branch. Statistics come from a separate *shots* operation.

**Invalid code.** The interface keeps the last valid state, marked as outdated, and shows the error on the line.

**Training runs.** Code that calls `report(...)` (free lab) and training lessons (`live: false`) run only through the Run button, with a 120 s limit. The `report` metrics arrive in batches while the code runs and draw the convergence curve live; the Stop button kills the worker.

**Lessons without a circuit** (`framework: "python"`: Track 0, 3.6, 3.7, 4.5 to 4.7, 5.4 and 5.5): the engine runs the code and returns the table of the learner's numeric variables in place of the state.

### 1.4 Isolation and security

| Risk | Protection |
| :-- | :-- |
| Infinite loop | The code runs in a worker process; past the time limit (5 s, or the lesson's), the worker is killed and another is created. |
| Memory overflow | Qubit cap (10 by default, adjustable per lesson) and a 4 GB virtual memory limit on the worker (Linux). |
| Web page talking to the local engine | Listens only on 127.0.0.1, per-session token, list of origins. |
| Stale runs | Only the most recent edit runs; earlier ones in the queue are discarded. |
| Accidents (`open`, `input`, `import os`) | Static check with an allowed-module list. It is not a sandbox: it exists to give clear messages. |
| Code coming from a share link | Opens in review mode: nothing runs or is saved until the learner confirms. |
| IBM key | Sent with each request, kept only in memory during the call, never logged or stored on the server; in the browser, only if the learner asks. |

In local mode the learner runs their own code on their own machine. In hosted mode the container is the security boundary (unprivileged user, read-only filesystem, no capabilities, no internet, CPU, memory and PID limits).

### 1.5 Qubit ordering convention

The platform follows Qiskit: qubit 0 is the least significant bit and the label is $|q_{n-1} \dots q_1 q_0\rangle$, everywhere (labels, targets, diagrams). Nielsen & Chuang use the opposite order; the lessons warn where it matters (1.5, 2.3, 2.4, 2.7, 2.8) and Track 0 teaches the convention (0.4).

### 1.6 Protocol

JSON messages with an `id` over WebSocket; each request gets one response (a training run first sends `progress` events with the same `id`).

| Request | Response |
| :-- | :-- |
| `catalog` | Curriculum, progress, where progress is kept (`engine` or `client`) and the glossary |
| `lesson` | Theory, starter code, objectives, mission, hints, challenge, references (never the solution) |
| `search` | Lessons that contain all the words, with an excerpt; also the learner's own notes |
| `bibliography` | All lesson references, the lecture material and the software |
| `run` | Steps and snapshots (or variables); with `train`, progress events and a larger limit |
| `shots` | Counts from 1024 executions |
| `validate` | Passed or not, and the message; with `challenge`, validates the challenge |
| `solution` | The commented solution of the mission or the challenge, on explicit request; records that it was seen |
| `review` | The end-of-track review questions |
| `export` | The circuit in OpenQASM 2 or 3 |
| `cancel` | Stops a training run in progress |
| `progress.save` | Code and hints used (ignored in hosted mode) |
| `progress.import` | Merges an exported backup (progress and notes) into the engine's database (local modes only) |
| `notes.list`, `notes.save`, `notes.delete` | The learner's notes: one general note and one per lesson (local modes; in hosted mode they stay in the browser) |
| `hardware.available`, `hardware.submit`, `hardware.status` | Execution on an IBM quantum computer (local mode only) |

---

## 2. The study experience

### 2.1 Hub

Map of the 7 tracks with the progress of each, the suggested next lesson (outside Track 0, which is optional), the free lab, the references page and the export of progress as a backup. Lessons mark challenge and project; each track header shows lessons done, challenges done and the time left, and completed tracks get a mark. "Continue" points to the last lesson opened. Each track from 1 on ends with a "Track review" row, and completed tracks can be collapsed. The side panel also opens the Glossary page (all terms in alphabetical order, with a filter and the lesson that introduces each), the Notes page, and a Backup dialog that exports or imports progress and notes. The search also finds glossary terms. An "i" button in the top bar opens a short About text for newcomers. The top-bar search (Ctrl+K) finds lessons by word, ignoring accents and treating hyphen and dash as equal.

### 2.2 The lesson screen

1. **Theory (left).** At the top, fixed: title, learning objectives, mission and hints (one at a time), and the offer of the solution once the hints are used; after the mission, the optional challenge. Since the round of 16 Nov 2026 the mission is a card pinned at the top of the panel, always fully visible; the objectives are a collapsible line and the whole panel has one scroll. Below, the theory in Markdown with LaTeX, the prediction question and the references with section and pages. Glossary terms appear underlined, with the definition in a tooltip; clicking one opens its entry on the Glossary page, and Back returns to the lesson as it was.
2. **Editor (center).** Monaco with autocompletion of the gates and a description of each. Ctrl+Enter runs.
3. **Circuit (center, below).** Diagram generated from the code; clicking a gate (or using the arrow keys) goes to the step. The composer writes gates into the code with clicks. Export to OpenQASM and, in local mode, run on IBM hardware.
4. **State (right).** The lesson's visualizations (section 2.4), with the tables of Bloch vectors and amplitudes.
5. **Bottom bar.** Errors, validation result and one main action (Check, then Next lesson); running shots is a quiet button and Reset code sits behind "More", with a confirmation.
6. **Notes.** A drawer on the right (a sheet on narrow screens) with a plain text area for the open lesson, saved as you type.

On narrow screens (below 1080 px), Theory, Code and State become tabs. The first lesson opened shows a 4-step guide; the "?" button reopens it and lists the keyboard shortcuts.

### 2.3 Free lab

Qiskit or PennyLane code without a mission, with ready examples (Bell state, variational training), training with a live curve, export and share links (the code goes in the URL fragment).

### 2.4 Visualizations

| Visualization | Use |
| :-- | :-- |
| Bloch spheres | One vector per qubit; it shrinks when the qubit state is mixed (entanglement or noise) |
| Q-Sphere | The global state of up to 5 qubits, with phase by color and a pointer |
| Comparator | Source qubit × target qubit (teleportation, no-cloning) |
| Amplitudes | Signed bars, phase color and mean (Deutsch–Jozsa, Bernstein–Vazirani, Grover) |
| Phases | One dial per basis state (QFT) |
| Register | Probability of each value, also as a fraction (phase estimation, Shor, codes) |
| Period | The sequence $a^x \bmod N$ with the period (Shor) |
| Landscape and Convergence | Cost as a function of the parameters with the optimizer trajectory; value at each step (Track 3, free lab) |
| Dissociation | Energy × distance between the atoms (VQE) |
| Graph | The most probable cut (QAOA) |
| Decision boundary | Classifier output on the plane (3.4) |
| Threshold | Probability of recovering the state × error probability (4.2) |
| Variables | Table of numeric variables (lessons without a circuit) |

Phase is never conveyed by color alone: there is always a pointer and the angle value.

### 2.5 Visual direction and accessibility

Sober and modern, like a scientific tool: neutral palette with a cobalt-blue accent, rounded cards and subtle shadows, no gradients, glows or emojis. IBM Plex Sans and Mono, served with the interface. Light and dark themes.

WCAG 2.1 AA contrast on all text (checked with axe in both themes), scrollable areas and circuit reachable by keyboard, current step announced to screen readers, text description of the 3D scene and respect for reduced motion.

---

## 3. Curriculum

53 lessons in 7 tracks, about 25 hours of study. Each lesson has learning objectives, theory, a validated mission, 3 progressive hints and at least two references (a book or article and a course or tutorial) with the exact place to read. Every track from 1 to 6 has optional challenges (34 in all); each track from 1 on ends with a project (rubric of 5 or 6 criteria). The names follow Nielsen & Chuang and the IBM Quantum Learning courses.

### Track 0: Mathematical Toolkit (optional)

| Lesson | Content | Framework | Validation | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **0.1 Complex Numbers and Phases** | Complex arithmetic, modulus, polar form and the difference between global and relative phase. | Python (no circuit) | Custom (check.py) |  |
| **0.2 Vectors and Inner Products** | Column vectors in C² and C⁴, the inner product with conjugation, normalization and the computational and ± bases. | Python (no circuit) | Custom (check.py) |  |
| **0.3 Matrices, Unitaries and Eigenvalues** | Matrix–vector products, the conjugate transpose, unitarity, the Pauli matrices, eigenvalues and expectation values of Hermitian matrices. | Python (no circuit) | Custom (check.py) |  |
| **0.4 Tensor Products** | The Kronecker product of vectors and matrices, product and entangled states, and Qiskit's qubit ordering. | Python (no circuit) | Custom (check.py) |  |

### Track 1: Basics of Quantum Information (beginner)

| Lesson | Content | Framework | Validation | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **1.1 Qubits and the Computational Basis** | State vector, normalization and the X gate on the Bloch sphere. | Qiskit | State fidelity | Challenge |
| **1.2 Superposition and the Hadamard Gate** | The states |+⟩ and |−⟩, measurement and a quantum random number generator. | Qiskit | Measurement distribution | Challenge |
| **1.3 Relative Phase and Rotation Operators** | Z, S, T and Rz gates: same probabilities, different states. | Qiskit | Several inputs | Challenge |
| **1.4 Interference and Measurement in Other Bases** | HH = I, HZH = X and how the relative phase decides a measurement outcome. | Qiskit | Secret oracles | Challenge |
| **1.5 Entanglement and the Bell States** | Tensor products, the CNOT gate, Bell states and qubit ordering. | Qiskit | State fidelity | Challenge |
| **1.6 Quantum Teleportation** | Bell pair, mid-circuit measurement and classically controlled corrections. | Qiskit | Reduced state per branch | Challenge |
| **1.7 Controlled Operations** | Build the controlled-S gate from CNOT and T gates, and identities between gates. | Qiskit | Several inputs | Challenge |
| **1.8 The No-Cloning Theorem** | No unitary operation copies an unknown quantum state; the CNOT copier works only for basis states. | Qiskit | Several inputs | Challenge |
| **1.9 Superdense Coding** | Two classical bits travel in one qubit when sender and receiver share a Bell pair. | Qiskit | Custom (check.py) | Challenge |
| **1.10 The CHSH Game** | A shared Bell pair wins the CHSH game with probability cos²(π/8) ≈ 0.854, above the classical limit of 3/4. | Qiskit | Custom (check.py) | Challenge |
| **1.11 Project: Entanglement Swapping** | Entangle two qubits that never interacted by measuring their partners in the Bell basis. | Qiskit | Custom (check.py) | Project |

### Track 2: Fundamentals of Quantum Algorithms (intermediate)

| Lesson | Content | Framework | Validation | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **2.1 Phase Kickback** | A controlled gate acting on an eigenstate of its target changes the control, not the target. | Qiskit | State fidelity | Challenge |
| **2.2 Deutsch's Algorithm** | One query decides whether a one-bit function is constant or balanced. | Qiskit | Secret oracles | Challenge |
| **2.3 The Deutsch–Jozsa Algorithm** | Decide constant or balanced for an n-bit function with one query. | Qiskit | Secret oracles | Challenge |
| **2.4 The Bernstein–Vazirani Algorithm** | Find a whole secret string with one query. | Qiskit | Secret oracles | Challenge |
| **2.5 Simon's Algorithm** | Recover a hidden XOR mask from outcomes that are orthogonal to it. | Qiskit | Custom (check.py) | Challenge |
| **2.6 Grover's Algorithm** | Amplitude amplification by an oracle and inversion about the mean. | Qiskit | Secret oracles | Challenge |
| **2.7 The Quantum Fourier Transform** | Moves the information about x from the basis states into the phases. | Qiskit | Several inputs | Challenge |
| **2.8 Phase Estimation** | Read an eigenvalue phase with controlled powers of U and an inverse QFT. | Qiskit | Secret oracles | Challenge |
| **2.9 Shor's Algorithm** | Factor 15 by reducing the problem to order finding. | Qiskit | Measurement distribution | Challenge |
| **2.10 Hamiltonian Simulation** | Approximate the evolution under a sum of terms with Trotter steps. | Qiskit | Custom (check.py) | Challenge |
| **2.11 Project: Design a Grover Oracle** | Build the oracle for a three-variable Boolean formula, then search its solutions with Grover's algorithm. | Qiskit | Custom (check.py) | Project |

### Track 3: Variational Algorithms (advanced)

| Lesson | Content | Framework | Validation | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **3.1 Variational Circuits and the Parameter-Shift Rule** | Ansatz, parameter-shift gradients and gradient descent. | PennyLane | Custom (check.py) |  |
| **3.2 The Variational Quantum Eigensolver** | Ground-state energy of H₂ with a variational circuit. | PennyLane | Custom (check.py) |  |
| **3.3 QAOA for Max-Cut** | Max-Cut on a 5-vertex graph with a two-layer QAOA. | PennyLane | Custom (check.py) |  |
| **3.4 Variational Quantum Classifiers** | Classify points in the plane with two qubits and data re-uploading. | PennyLane | Custom (check.py) |  |
| **3.5 Ansatz Design: Expressivity and Entanglement** | Compare variational forms by number of parameters, entangling layers and the states they can reach. | PennyLane | Custom (check.py) |  |
| **3.6 Optimizers and the Cost of a Gradient** | Gradient descent, SPSA and COBYLA compared by the number of circuit evaluations they need. | Python | Custom (check.py), with an evaluation counter |  |
| **3.7 Barren Plateaus** | Gradients of random deep circuits vanish exponentially with the number of qubits. | Python | Custom (check.py), against a reference simulation |  |
| **3.8 VQE with a Hardware-Efficient Ansatz** | Find the H₂ ground state with a general multi-parameter ansatz instead of a chemistry-inspired one. | PennyLane | Custom (check.py) |  |
| **3.9 Project: A Variational Dissociation Curve** | Compute the H₂ ground-state energy with VQE at several bond lengths and locate the equilibrium distance. | PennyLane | Custom (check.py) | Project |

### Track 4: Quantum Noise and Error Correction (advanced)

| Lesson | Content | Framework | Validation | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **4.1 Density Operators and Quantum Noise** | Density operators, Kraus operators, and the difference between error probability and wrong-answer probability. | PennyLane | Custom (check.py) |  |
| **4.2 The Three-Qubit Bit-Flip Code** | The three-qubit bit-flip code, syndrome measurement and the threshold. | PennyLane | Custom (check.py) |  |
| **4.3 The Three-Qubit Phase-Flip Code** | A phase flip is a bit flip in the Hadamard basis: the three-qubit phase-flip code and its X⊗X stabilizers. | PennyLane | Custom (check.py) |  |
| **4.4 The Shor Code** | Shor's nine-qubit code concatenates the phase-flip and bit-flip codes and corrects an arbitrary error on one qubit. | PennyLane | Custom (check.py) |  |
| **4.5 The Stabilizer Formalism** | Describe a code by commuting Pauli operators and read the syndrome from commutation with them. | Python (no circuit) | Custom (check.py) |  |
| **4.6 The Toric Code** | A stabilizer code on a torus: errors are strings, syndromes are their endpoints, logical operators are loops. | Python (no circuit) | Custom (check.py) |  |
| **4.7 The Threshold Theorem** | Concatenated codes push the logical error rate down doubly exponentially when the physical rate is below a threshold. | Python (no circuit) | Custom (check.py) |  |
| **4.8 Project: The Shor Code Under Noise** | Build the nine-qubit Shor code, compute its logical failure probability under depolarizing noise exactly, and find the physical error rate below which encoding helps. | PennyLane | Custom (check.py) | Project |

### Track 5: Running on Quantum Hardware (advanced)

| Lesson | Content | Framework | Validation | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **5.1 Transpilation and Qubit Connectivity** | Basis gates, coupling maps, SWAP insertion, and why the number of two-qubit gates is the cost of a circuit on hardware. | Qiskit | Custom (check.py) |  |
| **5.2 The Qiskit Primitives** | Sampler returns counts from shots, Estimator returns expectation values of observables, and the statistical error falls as 1/√shots. | Qiskit | Custom (check.py) |  |
| **5.3 Noise on Real Devices** | T1 relaxation, T2 dephasing, readout and gate errors, and how an idle qubit loses population and coherence. | PennyLane | Custom (check.py) |  |
| **5.4 Error Mitigation** | Readout mitigation by inverting the assignment matrix and zero-noise extrapolation by folding gates, and why neither is error correction. | Python (no circuit) | Custom (check.py) |  |
| **5.5 Project: A Mitigated Estimate on a Noisy Device** | Estimate a GHZ correlator on a noisy three-qubit device with readout mitigation and zero-noise extrapolation, and report the value with its uncertainty. | Python (no circuit) | Custom (check.py) | Project |

### Track 6: Adiabatic Computing and Quantum Annealing (advanced)

| Lesson | Content | Framework | Validation | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **6.1 Optimization as Energy: Ising Models and QUBO** | Write number partitioning and Max-Cut as the energy of spins, convert between the Ising and QUBO forms, and find the ground state by brute force. | Python (no circuit) | Custom (check.py) |  |
| **6.2 The Adiabatic Theorem and the Energy Gap** | Interpolate slowly from an easy Hamiltonian to the problem Hamiltonian; the minimum gap sets how slow is slow enough. | Python (no circuit) | Custom (check.py), against a finer reference evolution |  |
| **6.3 Quantum Annealing as a Circuit** | Cut the anneal into Trotter steps on three qubits and compare it with QAOA and with thermal simulated annealing. | Qiskit | Custom (check.py), from the learner's circuit |  |
| **6.4 Annealing Hardware: Embedding and Limits** | Map a problem onto sparse hardware with chains of qubits, choose the chain strength, and see what is and is not known about speedups. | Python (no circuit) | Custom (check.py) |  |
| **6.5 Project: A Constrained Choice by Annealing** | Choose two of four jobs with the best total value: write the constraint as a penalty, check the QUBO by brute force, and anneal it. | Python (no circuit) | Custom (check.py), a rubric of 6 criteria | Project |

The four lessons share one example: number partitioning, which becomes a three-qubit Ising problem with a unique ground state |110⟩. The track has a review, a project (6.5) and challenges in 6.1 and 6.3. It builds on 2.10 (the transverse-field Ising model and Trotter steps) and 3.3 (QAOA). Nothing runs on a real annealer.

---

## 4. The validation oracle

Validation compares mathematics, not text: equivalent solutions are accepted.

- **The target comes from the reference solution.** Each lesson has a `solution.py`; the target is computed by running that file.
- **Against shortcuts.** `allowed_gates`, `max_gates`, `gate_counts` and `forbidden_pairs` prevent, for example, solving with `qc.initialize(target)` or connecting qubits that should stay separate; `required_gates` demands the gate that is the subject of the lesson.
- **Variables.** `expected_variables` checks values the learner computes after running the circuit (with `run_shots`).
- **Secret cases.** The hidden setup (`hidden_setup.py`) receives each case in `_QLP_INPUT`: oracles, inputs, messages. The helpers appear in the diagram as opaque gates (`U_f`, `QFT†`).

| Type | Use |
| :-- | :-- |
| `state_fidelity` | $F \ge 0.999$, invariant under global phase; if only the relative phase is wrong, the message says so |
| `counts_distribution` | Distribution of the measurements against the solution's (total variation distance) |
| `reduced_state` | State of one qubit at the end, for several inputs and all measurement branches (teleportation) |
| `oracle_cases` | Distribution of a register against several secret oracles |
| `state_cases` | Final state for several inputs, including superpositions with phase |
| `custom` | The lesson's `check.py`: `check(ns, run_case)` with its own messages (training runs, lessons without a circuit, challenges and projects) |

**Challenges.** `manifest.challenge.validation` with `challenge_solution.py` (and, if needed, `challenge_check.py` and `challenge_hidden_setup.py`). The suite requires the challenge solution to pass and the starter code and the mission solution not to pass. Challenge progress is kept under the key `<id>:challenge`.

**Projects.** `manifest.project: true`; validation is a rubric in a `check.py` that reports the first criterion that fails, each with its own message.

---

## 5. Content structure

```text
/content
  catalog.json                  # tracks and lessons: titles, levels, summaries
  glossary.json                 # terms, definition and the lesson that introduces them
  sources.json                  # lecture material and software used in development
  /schema                       # JSON Schema for the manifest and the texts
  /track_N_.../review.json     # end-of-track review questions (Tracks 1 to 6)
  /track_N_.../section_N_M_.../
    manifest.json               # structure: framework, visualizations, validation, challenge, references (no text)
    text.json                   # title, summary, objectives, mission, hints, prediction, challenge, messages
    theory.md                   # theory in Markdown with LaTeX
    starter_code.py             # starter code
    solution.py                 # reference solution (defines the target)
    hidden_setup.py             # optional: oracles, inputs, helpers
    check.py, analysis.py       # optional: own validation; data for the training visualizations
    challenge_*.py              # optional: challenge solution, validation and setup
```

Writing rules in [writing-guide.md](writing-guide.md); references only from [verified-references.md](verified-references.md); the steps to add a lesson in [adding-a-lesson.md](adding-a-lesson.md).

**Content suite** (for every lesson): schemas; texts, theory, starter code and objectives present; title equal to the catalog's; solution passes; starter code runs without passing; challenge solvable and harder than the mission; references with a verified location (no `TODO`) and https links without repetition; the response to the interface does not contain the solution. There are also independent physics tests per track, glossary and bibliography tests, a test that every solution is commented and that every review is well formed, and end-to-end tests in the browser (Playwright), including opening every lesson.

---

## 6. History

| Stage | What went in |
| :-- | :-- |
| Vertical slice | Engine with per-instruction tracing, isolated worker, authenticated WebSocket, lesson 1.1, free lab |
| Tracks 1 and 2 | State, distribution, reduced-state, oracle and input validators; amplitude, phase, register and period visualizations |
| Original Track 3 | PennyLane, density matrix and Kraus channels, training lessons, landscapes and convergence; training with a live curve and OpenQASM export in the free lab |
| Review with the lectures | Exercises revised with the lectures of Wegewijs and Müller (Quantum Information 2025) and Willsch (Quantum Computing: Concepts and Algorithms, Jülich 2026); new lessons 1.7, 2.2 and the one on density matrices |
| Simplification | The desktop app and the Portuguese and German languages are removed; texts rewritten (didactic and concise) and names aligned with Nielsen & Chuang and IBM; references with exact location |
| November 2026 roadmap | See the table below |
| After the roadmap | The class report is removed (the platform is for individual study); references page with a reading guide to the books; hub side panel redone; interface dependencies updated (from 9 to 3 vulnerabilities, only in test tooling) |
| 16 Nov 2026 | P2.1 (show the solution), P2.3 (hub progress per track), P2.4 (Track 3 review questions added; all tracks 1 to 5 now have questions, but the screen was not built: reopened by the audit), P3.1 and P3.2 (Track 3 now has 9 lessons: new 3.6 optimizers/SPSA with an evaluation budget, 3.7 barren plateaus validated against a NumPy reference, 3.8 hardware-efficient VQE; the project became 3.9), P4.1 (lazy-loaded lab, initial bundle 4.0 MB to 196 KB) and P4.3 (Node 22, Vite 7, Vitest 4, Playwright 1.65, CI on Node 22, `npm audit` clean, lockfile regenerated) finished. E2E helper fixed (it skips `review.json`) and the "show solution" e2e test moved to lesson 1.7 to avoid a test-order dependency. The whole repository (docs, code comments, tests, schema descriptions) translated into English, with the docs renamed to `master-plan.md`, `writing-guide.md`, `verified-references.md` and `web-engine-decision.md`. Tests: 729 engine, 21 app unit, 20 e2e, all passing. P2.2 (Docker) written but still unverified: Docker was not running. |
| Audit, 16 Nov 2026 | Whole repository read (engine, interface with headless screenshots, the 48 lessons, tests, deploy, this document). Findings in section 8; this plan rewritten from section 7 on, with the owner's three goals (natural text, cleaner screens, notes) as items P3.3, P2.6 and P2.5. Fixed on the spot: the errors in the new lessons 3.6, 3.7 and 3.8, a rounding slip in 4.7, a Portuguese error message in the engine, and the challenge solution now offered as soon as the challenge hints are open. `scripts/dev.mjs` stops with a clear message below Node 22. |
| Implementation round, 16 Nov 2026 | After the audit, with the owner's decisions (MIT, rewrite everything, notes in their own table, rebalance predictions). **Text:** new writing guide; all 48 lessons, the reviews and the glossary (102 to 133 terms) rewritten; predictions rebalanced. **Screens:** mission card always visible, collapsible objectives and readouts, one main action in the bottom bar, collapsible tracks; styles split into nine files. **New features:** notes (drawer, page, search, backup), the end-of-track review screen, restorable backups, "Continue" for the last lesson opened, keyboard shortcuts, printed output shown on errors. **Engine:** always replies, survives `SystemExit`, migrates challenge and note keys, WAL, daily database copies, fairer validation. **Infra:** MIT license, setup script with version checks, CI timeouts and a Docker build job, `adding-a-lesson.md`. Tests: 821 engine, 29 interface, 41 end-to-end, all passing. Not committed. |
| Glossary page, 16 Nov 2026 | The glossary was only reachable through the tooltip of an underlined term. Added a Glossary page (hub side panel): the 133 terms in alphabetical order with letter links, a filter, aliases and a link to the lesson that introduces each. Clicking a term in a lesson opens its entry and Back returns to the lesson with the code untouched; the top-bar search lists matching terms. Unit, end-to-end and axe tests. |
| About dialog, 16 Nov 2026 | An "i" button in the top bar, left of the theme switch, opens a short text about the platform: what it is, who it is for, how a lesson goes, the six tracks (titles, sizes and times read from the catalog), what one can build afterwards, where the theory comes from (with a link to the references), what it is not, and where the data lives (the text differs in hosted mode). End-to-end and axe tests. |
| Track 6, 16 Nov 2026 | The owner missed quantum annealing: the curriculum followed gate-model sources and never mentioned it. Added Track 6, Adiabatic Computing and Quantum Annealing, as a track of its own (appending to Track 3 would have meant renumbering its project again): 6.1 Ising and QUBO, 6.2 the adiabatic theorem and the gap, 6.3 the anneal as a Trotterized circuit, compared with QAOA and simulated annealing, 6.4 minor embedding, chain strength and the evidence on speedups. A 12-question review, 8 glossary terms, and references checked on the web (how each was checked is recorded in `verified-references.md`; three could only be confirmed from bibliographic records or search results). Every number in the theories was computed. Written by AI agents and not yet read by a person. |
| Development round, 17 Nov 2026 | **Content:** project 6.5 (constraints as penalties) and 14 new challenges in Tracks 3 to 6, each with a commented solution and a check that tells the usual mistakes apart; charts for lessons without a circuit (a generic `curve` view, used in 3.6, 3.7 and 6.2). **Engine:** stable lesson keys, so renumbering a lesson needs no database migration (the stored progress was migrated once, after the daily backup); run replies bounded for large circuits (51.9 MB to 5.8 MB on a 10-qubit, 1,560-gate circuit); Check can be stopped; lesson files cached (search 80 ms to 2 ms); module-level loops traced about twice as fast; the hidden setup's private data no longer reaches the learner's code, and the static check closes the known bypasses; distribution checks with mid-circuit measurement enumerate the branches exactly; timeouts on the IBM calls; ruff. **Interface:** the theory has a contents list and remembers where you stopped reading; lighter hardware dialog and reference rows; a Stop button during a Check; the notice for steps of large circuits. **Infra:** Dependabot, a constraints file for the Python dependencies in CI, a lint step, `THIRD_PARTY_NOTICES.md`, `CHANGELOG.md`. Not committed. |
| Hub redesign, 17 Nov 2026 | After a design critique of the hub: only the track holding the next lesson starts open (the index opens the track it jumps to); each track in the index has a small progress bar, with the overall bar under the index; the "Learning tracks" heading and its subtitle are gone from the screen (the subtitle moved to the About dialog); on tablets and phones the tracks come before the References, Glossary, Notes and Backup links, both main buttons span the width and the search box says just "Search"; lesson summaries are capped at a readable line length. |
| Name, 17 Nov 2026 | The platform is now called **Ket Lab** ("Ket Lab – Learn Quantum Computing" in the top bar). The code keeps its internal names (`qlp_engine`, `QLP_*` variables) and the data folder keeps `quantum-learning-platform`, so existing progress is still found. The repository name and the Docker image name are unchanged. |

The reference lectures stay on disk, outside the repository (`Lecture Muller/`, `lecture (1)/`): they are third-party material. The lessons use the ideas and examples, with original text.

### 6.1 November 2026 roadmap, item by item

Done on the `roadmap` branch, in phases: safety net, delivery form, curriculum, design, real hardware, practice and extra resources.

| Item | Status | Notes |
| :-- | :-- | :-- |
| 0.1 CI on the current work | Done in the repository, not yet run | CI now runs on pushes to any branch (before, only `main` and pull requests). Windows and macOS are only tested once the branch is pushed (see P1.1). |
| 0.2 End-to-end tests | Done | Playwright: lesson flows, oracles, training, export, themes, narrow screens, accessibility, guide, links, composer, hardware, progress export and references, plus hosted mode; all 48 lessons opened in the browser. Job in CI. |
| 1.1 Engine-in-the-browser spike (Pyodide) | Done: not viable | Qiskit and rustworkx (PennyLane) have no WebAssembly build. Numbers in [web-engine-decision.md](web-engine-decision.md). |
| 1.2a Static web version | Not applicable | Dropped by 1.1. |
| 1.2b Hosted engine | Done up to deploy | `--public` mode, several workers, progress in the browser, `deploy/` (Dockerfiles, nginx, hardened compose). Missing what needs real infrastructure: gVisor on the server, one sandbox per session, security review and load test (see P5.1). |
| 1.3 Accounts and sync | Not done | Needs a login provider (OAuth) and a database on the server. Exporting and importing progress covers switching devices (see P5.2). |
| 2.1 Learning objectives | Done | Required in every lesson. Gaps found (theory topic that the mission does not exercise) in P3.1. |
| 2.2 New Track 1 lessons | Done | 1.8 no-cloning, 1.9 superdense coding, 1.10 CHSH game. |
| 2.3 Simon's algorithm | Done | 2.5. |
| 2.4 Splitting Track 3 | Done | Track 3, Variational Algorithms; Track 4, Quantum Noise and Error Correction (4.1 to 4.7). |
| 2.5 Hamiltonian simulation | Done | 2.10. |
| 2.6 Track 0, math kit | Done | 0.1 to 0.4, lessons without a circuit (variable table). |
| 3.1 Responsive layout | Done | Tabs below 1080 px; tested at 768 and 390 px. |
| 3.2 Accessibility | Done (automatic) | axe WCAG 2.1 A/AA with no serious violations in both themes; circuit by keyboard; text description of the state. Manual screen reader testing is missing (see P4.5). |
| 3.3 First-lesson guide | Done | |
| 4.1 Hardware track | Done | Track 5 (5.1 to 5.4, plus the project 5.5), with Qiskit's own transpiler and primitives; device noise simulated by density matrix, without Qiskit Aer. |
| 4.2 Execution on an IBM computer | Done, no real execution | Tested with a simulated IBM service; a real execution needs the learner's key. Local engine only. |
| 5.1 Challenges | Done in Tracks 1 and 2 | 20 challenges. |
| 5.2 End-of-track projects | Done | 1.11 entanglement swapping, 2.11 Grover oracle, 3.9 dissociation curve (3.5 at the time), 4.8 Shor code under noise, 5.5 mitigated estimate; each with a rubric of 5 or 6 criteria and its own messages. Track 0 has none (it is optional). |
| 5.3 Glossary | Done | 102 terms. |
| 6.1 Circuit composer | Done | Click-based (works by keyboard), with the Track 1 gates; 1.1, 1.2 and 1.5 solved with it alone. |
| 6.2 Share links | Done | Code in the link fragment; opens in review mode and only runs once confirmed. |
| 6.3 Class mode | Removed | Out of scope: the platform is for one person studying alone, not for teachers and classes. |

---

## 7. Current situation

Numbers checked against the repository on 16 Nov 2026, after the implementation round described in section 6.

| Aspect | Situation |
|---|---|
| Language | The whole repository is in English: docs, code comments, tests, schema descriptions, interface and lessons |
| Content | 53 lessons in 7 tracks (4, 11, 11, 9, 8, 5, 5), about 25 h of study; 34 challenges (Tracks 1 and 2 in every lesson; 3.1, 3.2, 3.5, 3.8, 4.1, 4.5, 4.6, 5.1, 5.3, 5.4, 6.1, 6.3); 6 projects (1.11, 2.11, 3.9, 4.8, 5.5, 6.5); glossary of 142 terms; references with section and pages |
| Depth per track | Words of theory: Track 0, 2,078. Track 1, 5,943. Track 2, 4,944. Track 3, 5,436. Track 4, 5,499. Track 5, 2,773. Track 6, 3,119. Total 29,792 |
| Frameworks | Qiskit: 24 lessons (Tracks 1 and 2, 5.1, 5.2). PennyLane: 13 (3.1 to 3.5, 3.8, 3.9, 4.1 to 4.4, 4.8, 5.3). Python without a circuit: 11 (Track 0, 3.6, 3.7, 4.5 to 4.7, 5.4, 5.5) |
| End-of-track reviews | 71 questions (Tracks 1 to 6), with a review screen opened from the hub and the best score kept |
| Tests | 963 engine, 39 interface, 52 end-to-end flows plus the hosted mode; all pass on Node 22; `ruff` clean |
| Interface bundle | Initial `index.js` of 211 KB (69 KB compressed); the lab (`Lab.js`, with Monaco and KaTeX), 3.8 MB (1.0 MB compressed), is downloaded when a lesson opens; the review and notes pages are small separate chunks |
| Code | Styles in eleven files in `app/src/styles/`. The store composes slices in `app/src/state/`. The engine caches lesson files, keeps progress and notes under stable lesson keys (`content/lesson_keys.json`) and bounds the size of a run's reply |
| Text | All lessons, the glossary and the interface strings rewritten by the new guide. No em dashes. The correct prediction option is spread evenly over the three positions (16 each), guarded by a test. A read by a person is still missing (P3.3) |
| Dependencies | Interface: React 18.3, Vite 7.3, Vitest 4.1, Playwright 1.65, TypeScript 5.6; `npm audit` clean; needs Node 22. Engine: Qiskit 2.6.2, PennyLane 0.45.1, NumPy 2.2+, websockets 17.4, Python 3.11+ |
| Development machine | Node 22 installed. `npm run setup` checks Node and Python first and works on any system |
| Git | **Nothing from the last weeks is backed up.** `roadmap` was never pushed (38 commits exist only on this disk) and the working tree has about 400 changed files: everything described in the last three rows of the history table. The remote has only `main` (first commit) and an old `trilha-3` |
| Release | MIT license. No tags and no CHANGELOG yet; version 0.1.0 everywhere |

---

## 8. Audit of 16 Nov 2026

The whole repository was read on 16 Nov 2026: the engine, the interface (with headless screenshots at 1600, 1366 and 390 px), the 48 lessons, the tests, the deploy files and this document. This section records what was found. Each finding points to the item of section 10 that resolves it. Findings marked *confirmed* were reproduced by running code or by looking at a screenshot; the rest come from reading.

The section is kept as written on the day of the audit. Much of it was resolved in the implementation round that followed; the status of each item is in section 10, and what remains open is summarized at the start of section 9.

### 8.1 Lesson text: why it reads as machine-written

The owner's request is text that sounds more natural. The audit's main conclusion is that the problem is no longer the wording. The writing guide already removed hype, em dashes, rhetorical questions and bold overuse. What gives the text away is that every lesson has the same shape. A new phrase list will not fix it; the lessons need a rewrite one at a time (P3.3).

| Pattern | Evidence | Where |
|---|---|---|
| Same skeleton in every lesson | Opens with a definition ("A **term** is…"), then a table or a bold list, then an "In the lab" list that describes the screen | "In the lab" closes 33 of 48 lessons; the qubit-ordering paragraph is pasted into 2.3, 2.4, 2.5, 2.7 and 2.8; 4.2, 4.3 and 4.4 share the heading "What the code does not correct" |
| Definition first, motivation never | 2.7 starts with the formula of the Fourier transform before saying why anyone wants it; 0.3 lists definitions; the projects 1.11 and 2.11 read like specification sheets ("What to build", "Rubric") | Most of Tracks 0, 2, 4 and the new 3.5 to 3.8 |
| No worked numbers | 3.6 gives the SPSA formula and never runs one step; 3.7 states the scaling with no worked case; 1.6 asserts the table of Bob's four states without deriving one | 1.6, 2.2 to 2.5, 2.7, 2.8, 3.6 to 3.8, 4.5, 4.8 |
| No human voice | No lesson says what is easy to get wrong, what usually confuses people or what is surprising. Hard spots are not flagged as hard | All tracks |
| Tidy tables, lists of three and one-line morals | Tables that repeat the prose above them (3.5 to 3.8); "The effect depends on three things:"; closers such as "The ceiling comes from the ansatz." | About 20 of the 22 lessons of Tracks 3 to 5 |
| Hints from one template | Hint 1 restates the concept, hint 2 names the function, hint 3 is the solution written out (0.1 to 0.4, 2.1, 2.9, 3.6, 3.8). Always exactly three | 47 of 48 lessons |
| Predictions that test recall, with a guessable answer | The correct option is the middle one in 39 of 48 lessons and the longest in 23; the paragraph above often states the answer (5.2, 3.3, 4.1); several wrong options are absurd (2.8, 2.9, 5.5) | All tracks |
| Robotic messages and objectives | "X should be E, but it is A. Use f(…)" in every Track 0 message and about 48 of the 174 messages of Tracks 3 to 5; objectives are lists of "Explain…", "Build…", "Compute…" that sometimes just repeat the mission | Track 0 messages; all objectives |
| Glossary | Dictionary tone, every entry ending with the same kind of "so what" sentence. Terms used in lessons but missing: fidelity, eigenstate, expectation value, commutator, reduced state, projector, Born rule, Schmidt coefficient | `glossary.json` |
| Interface text | About 40 strings in `strings.ts` are stiff or inconsistent: "Section 1.5" in the lesson but "lesson" everywhere else; done, complete and completed mixed; shots and measurements mixed; click and press mixed; three near-identical "Show a solution" labels; one broken template (`viz.compareMarker`) | `app/src/strings.ts` |

Lessons that already read well and should be the models: 0.1, 1.4, 1.8, 1.10, 2.5, 2.9, 3.1, 3.3, 3.4, 4.1 and 5.3. They work a small case with real numbers, say where an argument fails and admit limits. The ones that need the most work: 2.11, 1.11, 2.10, 2.8, 1.1, 1.2, 0.3, and the new 3.5 to 3.8, 4.5, 4.7 and 4.8.

### 8.2 Screens with too much on them

The owner's request is a cleaner screen where it floods. Quantum computing needs a lot on screen, so the aim is to hide what is secondary at each moment, not to remove information. Findings from the screenshots, in order of harm (P2.6):

1. **The mission is cut off** *(confirmed)*. The lesson header holds the title, the objectives, the mission, the hints and the solution offer, and is limited to 55% of the panel with its own scroll. At 1366×768 the mission shows two lines; with three hints open, the hint text is cramped into a strip and the theory keeps about a quarter of the panel. In lesson 3.6 the mission is cut mid-sentence even at 1600×900, and at 390 px after one line. The most important element of the screen is the one that gets hidden.
2. **The challenge inherits the mission's objectives**, so the challenge text, its hints and the solution offer compete for the same clipped header.
3. **The state panel shows everything at once**: tabs, caption, sphere, entanglement meter with a footnote, the Bloch table and the amplitude table, whatever the active view. After a training run the cost curve sits above tables that have nothing to do with it.
4. **The bottom bar mixes three kinds of action**: the message, Reset code (destructive and rare), Simulate (exploration) and Check. At 390 px it stacks into about 130 px and covers the tables.
5. **The circuit panel takes half the middle column while it is empty**, and the editor has no word wrap, so long comments run off the screen.
6. **The hub is one long list of 48 rows.** Every row of Tracks 1 and 2 carries a "Challenge" pill, which says nothing until it is done.
7. **Long theory has no outline** and does not remember where the learner stopped reading.
8. **Dialogs and the references page** are dense but acceptable: the hardware dialog opens with a four-sentence note, and reference rows wrap their lesson chips onto a second line.

### 8.3 Features that are missing

| Finding | Detail | Item |
|---|---|---|
| The end-of-track review has no screen *(confirmed)* | The 58 questions, the engine request and the store code exist, but no component renders them, the hub has no entry and there is no test. Opening the "review" view would show an empty lab. This document used to mark P2.4 as done; that was wrong | P2.4 |
| No place for notes | Requested by the owner. Nothing exists yet | P2.5 |
| "Continue" is not a resume | The hub offers the first lesson not completed, not the last one opened. Someone who finished only Track 0 sees "Continue" on 1.1 | P2.7 |
| Few keyboard shortcuts | Only search, run and the circuit arrows. No shortcut for Check, next lesson or switching panels | P2.7 |
| A backup cannot be restored in local mode | Progress can be exported, but the import button only appears when progress lives in the browser. With the local engine, the SQLite file is the only copy | P2.8 |
| Lessons without a circuit cannot show charts *(confirmed)* | They always show the Variables table. Lesson 3.6 declared a convergence curve that never appeared (its manifest was corrected to say Variables). 3.6 and 3.7 would teach better with a curve | P3.8 |
| Tracks 3 to 5 have no challenges | Tracks 1 and 2 have 20. Someone studying alone gains the most from extension problems | P3.6 |

### 8.4 Engine

Confirmed by running small scripts, unless marked otherwise.

| Finding | Consequence for the learner | Item |
|---|---|---|
| An unexpected exception inside a request never gets a reply | The interface waits forever, with no message. Triggers: a locked database, a wrong field type, a disk error | P1.3 |
| `raise SystemExit` in the learner's code kills the worker | The message blames memory, and the next run waits for the libraries to load again | P1.3 |
| Output printed before an error is discarded | `print` debugging, a beginner's first tool, vanishes exactly when the code fails | P1.3 |
| The progress migration ignores `<id>:challenge` keys | After a renumbering, a completed challenge ends up attributed to another lesson. Numeric ids as keys make every renumbering risky (Track 3 was renumbered this month) | P1.3, P4.6 |
| No limit on the size of a run's reply | A 10-qubit circuit with 1,500 gates produces 29.5 MB of JSON, serialized on the event loop. With noise (density matrix) it can reach the memory limit | P4.6 |
| Check cannot be stopped | In a training lesson it may hold the only worker for up to 6 minutes | P4.6 |
| Lesson files are read from disk again on every request, and search loads all lessons on every query | Delay added to every keystroke-driven run | P4.6 |
| Line tracing makes module-level loops about 5 times slower | A loop of a few hundred thousand iterations times out only because of the tracing | P4.6 |
| Simulating shots on a circuit with mid-circuit measurement runs the whole circuit once per shot; a timeout there is reported as "infinite loop" | Wrong diagnosis for a heavy but correct circuit | P4.6 |
| A correct solution built with a sub-circuit (`qc.append(sub.to_gate(), …)`) is rejected | The message complains about a gate called `circuit-48` | P4.7 |
| Variable checks are too loose for lists (`[3.9, 5.2]` passes as `[3, 5]`) and too strict for decimals (tolerance of 1e-9) | A wrong answer can pass; a rounded right answer fails | P4.7 |
| The reference solution always runs with the default cap of 10 qubits | No effect today (largest lesson: 9). A future lesson above 10 would fail its own solution | P4.7 |
| *Not verified:* distribution checks with mid-circuit measurement compare two samples of 4,096 shots against a fixed tolerance | A correct solution with many outcomes could fail by sampling noise | P4.7 |
| The static check is easy to bypass (`random._os`), and NumPy can read and write files | Only matters for public hosting; locally it is accident prevention, as section 1.4 says | P4.4 |
| *Not verified:* hardware status logs in to IBM on every poll, and network calls have no timeout | A hung network would block the request forever | P4.6 |
| Test gaps: no tests for the static check, malformed messages, database locks, the challenge-key migration | The bugs above went unnoticed | P4.9 |

In good shape: worker isolation (kill on timeout, restart, covered by tests); access control of the WebSocket (local address, token compared in constant time, origin list); the validation design (target computed from the reference solution, global phase ignored, a dedicated message for "right probabilities, wrong phase"); the consistency of the qubit order between Qiskit and PennyLane; and the split between content loading and the worker, which keeps startup fast.

### 8.5 Lesson correctness and teaching

No physics error was found in Tracks 0 to 2 or in the older lessons of Tracks 3 to 5; the worked numbers that were recomputed all hold (2.10, 1.10, 3.2, 3.3, 5.3, 5.4, the Shor-code counts of 4.8). The errors were in the lessons written on 16 Nov, and were fixed the same day:

- 3.6: the option marked as correct in the prediction was the wrong one.
- 3.7: the mission asked for "a factor of at least 3" while the check required 0.3; the correct prediction option said 500 times more shots where the right figure is about 260,000.
- 3.8: the theory said that zero angles give the Hartree–Fock state. With zero angles the CNOT ladders produce |1010⟩, at −0.531 Ha, and the gradient is zero for all 16 angles. Rewritten.
- 4.7: a rounding slip (2.65 for 2.66 × 10⁻⁷).

Still open (P3.5):

- 2.6 presents k = ⌊(π/4)√(N/M)⌋ as the best number of iterations without saying it only holds when M is much smaller than N.
- 1.2 states an interpretation as a fact ("the randomness is a feature of the theory, not a consequence of missing information").
- 1.11 defines concurrence for pure states and applies it to a reduced state.
- 4.2 and 4.7 call p = 1/2 "the threshold"; 4.8 correctly says pseudo-threshold. 4.7 teaches the threshold theorem with a repetition-style model and does not say what fault tolerance adds.
- Terms used before they are defined: fidelity, reduced state and maximally mixed state (1.6, 1.8, 1.9, 1.11), outer product (2.6), commutator (2.10), Schmidt coefficient (3.5); Hartree–Fock and Jordan–Wigner in 3.7 and 3.8 without pointing back to 3.2.
- Steep steps: 1.5 to 1.6 (teleportation right after Bell states), 1.6 to 1.7, 2.8 to 2.9 (continued fractions, gcd and order finding in one lesson) and above all 2.9 to 2.10 (matrix exponentials and commutators never introduced; the model is the transverse-field Ising model and is never named).
- Missions that do not exercise the theory: 3.6 uses an exact cost, so the real advantage of SPSA (shot noise) is not felt; 3.8 is a recipe; 3.3 promises to explain why one layer is not enough and only states the numbers.
- Reviews: several questions copy a lesson's prediction almost word for word (Track 3 questions 2, 7 and 8; Track 4 question 11; Track 5 question 11); Track 3 question 1 is confusing; 3.4 and 3.9 have no question.
- 5.5 switches the qubit order of the count keys "in this lesson only".

Curriculum gaps, compared with Nielsen & Chuang and the IBM courses (backlog, P3.7):

- Track 0: outer products and projectors, matrix exponentials, commutators, modular arithmetic and gcd (needed in 2.9), XOR algebra (needed in 2.3 to 2.5).
- Track 1: the measurement postulate with projectors and partial measurement, the GHZ state, the Pauli algebra, Toffoli and other multi-qubit gates, any single-qubit unitary as rotations.
- Track 2: building oracles in general, quantum counting and amplitude amplification, the accuracy of phase estimation, complexity classes.
- Track 3: a cost with shot noise, measurement grouping, a molecule beyond H₂, excited states.
- Track 4: depolarizing and amplitude-damping channels with worked examples, the Knill–Laflamme conditions, CSS codes and the Steane code, a decoder for the toric code.
- Track 5: dynamical decoupling, twirling, a lesson built around the real-hardware run.

### 8.6 Interface code

- The store split of P4.2 is done; only `styles.css` remains (2,536 lines, with the narrow-screen rules of one component spread over the file).
- The tab bars (`Lab`, `Visualizer`, export dialog) announce themselves as tabs but have no arrow-key behavior and no tab panels, so a screen reader promises something the keyboard does not deliver (P4.5).
- Small leftovers: a duplicated function in `OracleBar.tsx`; the search hint shows "Ctrl K" on macOS as well.
- End-to-end gaps: nothing checks that the mission is visible (a test at 1366×768 would have caught finding 1 of 8.2); the narrow-screen tests check horizontal scroll, not clipping; axe runs on the hub and one lesson only, not on the references page, the dialogs or challenge mode (P4.9).

### 8.7 Repository, setup and delivery

| Finding | Detail | Item |
|---|---|---|
| No backup | See "Git" in section 7. The lecture folders (about 280 MB, never committed, one of them not publicly available) and the learner's `progress.sqlite3` also exist only on this disk | P1.1, P2.8 |
| The README gives the wrong Node version | It says Node 18 or newer; the project needs 22. `npm run setup` does not check versions, runs `npm install` at the root (which has no dependencies) and assumes Unix paths for the virtual environment. The README's summary of Track 3, its validation table and its "create a lesson" section are behind the content | P1.4 |
| The Docker path was never run | `deploy/local.yml` points to an image that was never published (the workflow only runs on `v*` tags, and none exists; a new package is private by default). The engine accepts every flag the Dockerfile passes. Possible runtime problems: no writable home directory with a read-only filesystem, no health check, no arm64 build. `Dockerfile.web` still uses Node 20 | P2.2 |
| CI | No timeouts, no cancelling of superseded runs, no browser cache, no lint, no job that builds the Docker images, no lock file for the Python dependencies (only the top level is pinned), full matrix even for docs-only changes. `npm ci` was never run on npm 10 | P4.8 |
| No license | Without a LICENSE file the code is legally closed to use and contribution. The lessons quote no third-party text or figures; references are citations only | P4.8 |
| No release process | No tags, no changelog | P4.8 |
| Hosted deploy details | The nginx `/assets/` block drops the security headers; four workers of up to 4 GB each under a 6 GB container limit; `deploy/README.md` speaks of "a class or a trusted group", which the platform no longer targets | P5.1 |
| Docs | The writing guide does not cover reviews, challenges or projects; `verified-references.md` has no "checked on" dates. All 122 references in the manifests match the verified list | P3.3 |

---

## 9. Risks and open decisions

What the implementation round of 16 Nov 2026 left open, each pointing to its item:

1. **Loss of work.** Weeks of work, now including the rewrite of every lesson, exist only on one disk, uncommitted and unpushed (P1.1). This remains the most urgent item.
2. **The rewritten text has not been read by a person.** All 52 lessons (Track 6 included, which is new), the glossary and the reviews were rewritten by AI agents following the new guide. Every number added was computed, the content and physics tests pass, and all 48 predictions were checked by hand against their explanations (two had the wrong option marked and were fixed). What no test can tell is whether the result reads as the owner wants. The owner should read at least Track 1 before the rest is taken as final (P3.3).
3. **The Docker path has still never been run** on a real machine: Docker was not running on the development machine. CI now builds the images and checks that the local one serves the interface, but only once the branch is pushed (P2.2, P1.1).
4. **Lesson ids as storage keys.** Progress and notes are keyed by the lesson number. The migration now renames challenge and note keys together with their lesson, but a renumbering still needs a migration step (P4.6).
5. **Reply size and long runs.** A long circuit can still produce a very large reply, Check still cannot be stopped, and lesson files are still read from disk on every request (P4.6).
6. **Memory limit outside Linux.** On Windows and macOS only the qubit cap applies.
7. **CI outside Linux.** Windows and macOS are only tested once the branches are pushed (P1.1).
8. **Real hardware never executed.** The IBM integration was tested with a simulated service; the first real run needs a key and may reveal API differences.
9. **Public hosting.** Needs per-session isolation, a security review and a load test; the static check is not a sandbox (P5.1, P4.4).
10. **Hidden data.** The learner's code can read the secret cases; since study is individual, it only hurts whoever cheats (P4.4).
11. **Keyboard shortcuts in real browsers.** Alt+1, 2, 3 may collide with the browser's own tab switching on some systems; this cannot be seen in the automated tests (P2.7).

Decisions taken by the owner on 16 Nov 2026: MIT license; rewrite all 48 lessons; notes in a table of their own; rebalance the prediction answers. The copyright line of `LICENSE` uses the name "Orlando Mota Pires", inferred from the git user: correct it if needed.

---

## 10. Next steps

Each item gives the goal, the work, the done criterion and the effort (S ≤ 2 days, M ≤ 1 week, L ≤ 3 weeks). Items are named P1.1, P2.1… so they are not confused with lesson ids. Items marked **(owner)** come from the owner's requests of 16 Nov 2026. An item is done only when a learner can use the result and a test covers it.

### Phase 1: Secure and close what exists

#### P1.1 Commit, push and run CI (S, urgent)

- **Status: not done.** Nothing was committed or pushed in the implementation round: both need the owner's ok.
- **Goal:** stop depending on one disk, validate the work on the three systems and consolidate `main`.
- **Work:** commit the working tree in logical groups (Track 3 lessons and renumbering; reviews; store split; show-solution; Docker files; Node 22 and lockfile; translation and renamed docs; this plan); push `roadmap` (an external action: needs the owner's ok); follow the `engine` (Linux, Windows, macOS), `app` and `e2e` jobs and fix what fails outside Linux; open the `roadmap → main` pull request and merge it; tag `v0.1.0`. Copy the two lecture folders to an external drive.
- **Done when:** CI is green on the three systems, `main` has the current platform and nothing important lives only on this disk.

#### P1.2 Coherent documentation (S)

- **Status: done.** One planning document; the README points to it. Kept up to date by this revision.

#### P1.3 Engine fixes a learner would hit (S)

- **Status: done.** Every request now gets a reply (unexpected errors answer with kind `internal` and are logged); message fields are validated; `raise SystemExit` no longer kills the worker and has its own message; output printed before an error comes back with the error and the interface shows it under "Program output"; challenge and note keys migrate with their lesson; SQLite uses WAL and a busy timeout. 27 new tests (`test_robustness.py`).

#### P1.4 A README and a setup that tell the truth (S)

- **Status: done.** `scripts/setup.mjs` checks Node 22 and Python 3.11 before installing anything, creates the virtual environment on any system and uses `npm ci`; `scripts/dev.mjs` refuses old Node with a clear message. The README states the real requirements and the current Track 3, and "create a lesson" moved to [adding-a-lesson.md](adding-a-lesson.md).

---

### Phase 2: Experience of studying alone

#### P2.1 See the solution when stuck (M)

- **Status: done.** In a mission, "Show a solution" appears after the 3 hints are open and after 3 Check attempts; in a challenge, as soon as all of the challenge's hints are open. Both ask for confirmation first. All lessons, challenges and projects have a commented solution. Progress records that the solution was seen, and the hub marks "Completed with the solution" and "Challenge done with the solution". End-to-end tests cover both.

#### P2.2 Start without installing Python and Node (M)

- **Status: still never run.** Changes made without being able to run them (Docker was not running): a writable home and a health check in `Dockerfile.local`, Node 22 in `Dockerfile.web`, and a CI job that builds the three images and checks that the local one serves the interface. Missing: build and run it once, the arm64 build, publishing the image, the README with two paths.
- **Goal:** remove the biggest entry barrier.
- **Work:** build and run the image once; give the container a writable home (`HOME=/tmp`), a health check and an arm64 build; move `Dockerfile.web` to Node 22; publish the image (tag, public package); a CI job that builds the three Dockerfiles and smoke-tests the local image (open `/`, open the WebSocket); README with two paths, "just use it" (Docker) and "develop".
- **Done when:** on a machine with only Docker, one command opens the platform and progress survives restarting the container.

#### P2.3 More complete progress in the hub (S)

- **Status: done.** Each track header shows completed lessons, completed challenges and the estimated time left.

#### P2.4 Review at the end of each track (M)

- **Status: done.** A review screen (one question at a time, explanation after answering, the lessons to revisit at the end, best score kept) opens from a "Track review" row at the end of Tracks 1 to 5 in the hub. 59 questions; those that copied a lesson's prediction were replaced. Completed lessons now say "Revisit". End-to-end and accessibility tests cover it.

#### P2.5 Notes (M) **(owner)**

- **Status: done.** In the lab, a "Notes" button (Alt+N) opens a drawer with one plain text area for the open lesson; it saves by itself. The hub has a Notes page with a general note and every lesson note grouped by track. A dot marks lessons that have a note. Notes live in their own table in the engine's SQLite (requests `notes.list`, `notes.save`, `notes.delete`; 64 KB per note), or in the browser in hosted mode; they are part of the exported backup, come back on import (when both sides differ, both texts are kept) and appear in search. Not done: live sync between two open tabs.

#### P2.6 Cleaner screens (M to L, in steps) **(owner)**

- **Status: steps 1 to 6 and 8 done; 7 (focus mode) open.** The mission is a card pinned at the top of the theory panel; objectives, readouts and finished tracks collapse; one main action in the bottom bar; the theory has a contents list and remembers the reading position; the hardware dialog and the reference rows are lighter. A test opens every lesson at 1366×768 and checks that the mission and the hint button are visible. Open: focus mode.
- **Status: steps 1 to 5 done; 6, 7 and 8 open.** Done: the mission is a card pinned at the top of the theory panel, always fully visible, with hints opening inside it; the objectives are a collapsible line, open on the first visit; the panel has one scroll; the challenge hides the mission's objectives. The bottom bar has one main action, with Reset code behind "More" and a confirmation, and is one line at 390 px. The numeric readouts of the state panel collapse and are hidden under training views. The empty circuit panel is a short strip and the editor wraps long lines. In the hub, the Challenge pill appears only after the mission, and completed tracks collapse. A test opens all 48 lessons at 1366×768 and checks that the mission and the hint button are visible. Open: remembering the reading position and an outline of the theory (step 6), focus mode (7), shorter dialogs and reference rows (8).
- **Goal:** show at each moment what the learner needs for the current step, and keep the rest one click away. Nothing is removed. Every choice of open or closed is remembered.
- **Work, in order of value:**
  1. **Mission always visible (M).** Take the mission out of the clipped header: a short mission strip pinned at the top of the theory panel (one or two lines, with "more"), and one scroll for the whole panel. The objectives become a collapsed line ("What you will learn (4)"), open the first time a lesson is visited. Hints open inside the strip, one at a time. In challenge mode the mission's objectives are hidden.
  2. **Bottom bar (S).** One main action (Check, then Next lesson); Simulate as a quiet button; Reset code in a "more" menu, with confirmation, since it discards the learner's code. One line at 390 px.
  3. **State panel (S to M).** The numeric readouts (entanglement, Bloch vectors, amplitudes) become sections that can be collapsed, remembered per kind of view, and hidden while a cost curve is on screen. Footnotes move to "?" tooltips.
  4. **Middle column (S).** The circuit panel stays small until the first gate exists; word wrap in the editor.
  5. **Hub (S to M).** The "Challenge" pill only appears once the lesson is done; completed tracks collapse to their header; the track with the next lesson starts open.
  6. **Theory (S to M).** Remember the reading position per lesson; a small outline built from the headings.
  7. **Focus mode (M, optional).** A toggle that leaves only the editor and the state.
  8. **Dialogs and references (S).** Shorter hardware note, with the key explanation behind "About the key"; at most two lesson chips per reference row, plus a counter.
- **Done when:** at 1366×768 and at 390 px the full mission and the hint button are visible without scrolling inside the header, in every lesson (an end-to-end test checks all 48); both themes checked; the axe audit still passes.

#### P2.7 Pick up where you left off, and shortcuts (S)

- **Status: done.** The hub button is "Continue: …" for the last lesson opened, and "Start" before any lesson was opened. Ctrl+Shift+Enter checks, Alt+1, 2, 3 go to Theory, Code and State, Alt+N opens the notes; the "?" button lists them. ⌘ replaces Ctrl on macOS. To verify by hand: Alt+digit may collide with the browser's own shortcuts on some systems.

#### P2.8 Backups that can be restored (S)

- **Status: done.** `progress.import` merges an exported backup into the engine's SQLite, and the import button appears in local mode too. At startup the engine keeps a dated copy of the database, one per day, the last five.

---

### Phase 3: Content

#### P3.1 Gaps between objectives and missions (S)

- **Status: done.** Lessons 1.1, 1.2, 1.3, 1.5 and 4.2.

#### P3.2 Deepen Track 3 (L)

- **Status: done.** Track 3 has 9 lessons: 3.5 ansatz design, 3.6 optimizers, 3.7 barren plateaus and 3.8 hardware-efficient VQE are new; the project became 3.9. The errors the audit found in them are fixed (section 8.5). They are also the lessons that most need the rewrite of P3.3.

#### P3.3 Natural text: rewrite the lessons one by one (L) **(owner)**

- **Status: rewritten; the read by a person is missing.** All 48 lessons (theory, objectives, missions, hints, predictions, messages), the five reviews and the glossary (133 entries) were rewritten on 16 Nov 2026 by the new [writing guide](writing-guide.md): each lesson opens on a concrete problem, has a worked example whose numbers were computed, flags what usually goes wrong, has its own structure and has hints that no longer give the solution. The interface strings went through the same pass. The rewrite was done by AI agents working from the checklist below, one track each; it has not been read by a person, which was part of the done criterion. Next: the owner reads Track 1 end to end and says what still sounds wrong; that feedback goes into the guide and into a second pass.
- **Goal:** lessons that read as written by a person who teaches the subject. This item replaces the former "human read" (P3.3) and "English review" (P3.4).
- **Method.** One lesson at a time, with the lesson's real result in hand (a run, a worked number). Not a regeneration by a model: the diagnosis of section 8.1 is that uniformity is the problem, and regenerating produces uniformity again. For each lesson:
  1. Open with the problem the lesson solves, on a small concrete case. The definition comes when the word is needed.
  2. One worked example with numbers that can be checked by hand.
  3. One honest sentence on where people go wrong or what is surprising.
  4. Prose by default. A table only for three or more items compared on three or more aspects. Bold only where a term is defined.
  5. The qubit-ordering note once, where it first matters. "In the lab" becomes a predict-then-check task or goes away; it never describes the screen.
  6. Hints as a ladder: a question to ask yourself, then the idea, then code only where the code is trivial. The number of hints may vary. The last hint is not the solution; the solution has its own button.
  7. Messages that name the probable mistake in the learner's terms.
  8. Objectives as one or two plain sentences.
  9. Vary sentence length; no closing one-line moral.
- **Order:** Track 1 (the entrance, and the most templated), then Track 0 (hints and messages), then 3.5 to 3.8 and 4.5, 4.7, 4.8, then Track 2, then the rest. Each track is read end to end by the owner, or by someone in the field, before it is closed.
- **Also:** update `writing-guide.md` with these rules, with the patterns of section 8.1 as things to avoid, and with rules for reviews, challenges and projects; rewrite the glossary entries in the same voice and add the missing terms.
- **Effort:** about 75 hours in total. Tracks 0 to 2: 1 to 2.5 h per lesson. Tracks 3 to 5: 6 light (30 min), 9 medium (1 h), 7 heavy (2 h).
- **Done when:** every lesson has been rewritten against the checklist and read by a person; the content suite passes; the guide describes the new rules.

#### P3.4 Predictions and reviews worth answering (M)

- **Status: done.** Every prediction was rewritten to ask for a consequence, with wrong options that are real misconceptions. The correct option is at each of the three positions in 16 lessons, and a test fails if one position takes more than 45% or if the correct option is the longest in more than half of the lessons.

#### P3.5 Open content corrections (S)

- **Status: done.** Fixed in the rewrite: the Grover iteration rule with its condition and the exact formula (2.6), the interpretation no longer stated as fact (1.2), concurrence for mixed states (1.11), "pseudo-threshold" used consistently and a section on what fault tolerance adds (4.2, 4.7, 4.8), terms defined where first used, the Ising model named and the exponential and commutator introduced (2.10), continued fractions explained before they are used (2.9), the order of rotations (3.5), the controlled-R_z matrix in the platform's qubit order (1.7), and why the gradient vanishes at zero angles in 3.8 (the state |1010⟩ is an eigenstate of the Hamiltonian). Open: 3.6 still uses an exact cost, so SPSA's advantage under shot noise is not felt (P3.7).

#### P3.6 Challenges for Tracks 3 to 5 (M to L)

- **Status: done for 12 lessons.** Challenges in 3.1 (a sinusoid from three runs), 3.2 (single excitations cannot lower the energy), 3.5 (one angle is enough), 3.8 (the stuck all-zero start), 4.1 (amplitude damping), 4.5 (the Steane code), 4.6 (a minimum-weight decoder), 5.1 (GHZ on a T-shaped device), 5.3 (T1 and T2 from data), 5.4 (line or parabola for extrapolation), 6.1 (weighted Max-Cut), 6.3 (a schedule that slows down at the gap: 273 gates for 0.92 against 903 for 0.77). The other lessons of Tracks 3 to 6 have none.
- **Goal:** extension problems where the tracks are most open-ended.
- **Work:** one challenge per lesson where it adds something. Candidates: fit a cos θ + b sin θ + c from three evaluations (3.1); a deliberately poor ansatz and its plateau energy (3.2); SPSA against parameter-shift with the same budget on 12 angles (3.6); the barren-plateau experiment with a local cost (3.7); explain the stuck run at zero angles (3.8); amplitude damping as a Kraus channel (4.1); the Steane code's stabilizers (4.5); a minimum-weight decoder on a small torus (4.6); the smallest CNOT count for a GHZ state on a T-shaped device (5.1); T1 and T2 from idle data (5.3).
- **Done when:** Tracks 3 to 5 have at least 10 challenges, each with a solution and tests, as in Tracks 1 and 2.

#### P3.7 Curriculum gaps (L, backlog)

- **Done from this list and beyond it:** quantum annealing, which the audit had missed, is now Track 6. Still open there: a project for Track 6, challenges, and a lesson that uses a real annealer's SDK (it would need an account with the manufacturer).

- **Work:** new lessons from the list of section 8.5, chosen by what blocks understanding first: Track 0 lessons on projectors, exponentials and commutators and on modular arithmetic (they remove the steep step into 2.9 and 2.10); a Track 1 lesson on measurement with projectors and partial measurement; split 2.9 in two; a Track 3 lesson with shot noise; a Track 4 lesson on noise channels and one on the Steane code.
- **Done when:** decided item by item; this is a list to draw from, not a commitment.

#### P3.8 Charts in lessons without a circuit (S)

- **Status: done.** A `curve` view draws line and point charts from a lesson's `analysis.py`, for lessons with or without a circuit (format in [adding-a-lesson.md](adding-a-lesson.md)). Used in 3.6 (cost per SPSA step), 3.7 (gradient variance against qubits, log scale) and 6.2 (the gap along the sweep and success against total time).

---

### Phase 4: Technical quality

#### P4.1 Lighter loading (M)

- **Status: done.** The lab and the references load on demand; the initial bundle dropped from 4.0 MB to 196 KB.

#### P4.2 Code organization (M)

- **Status: done.** The store is in slices and `styles.css` became nine files in `app/src/styles/` (base, hub, lab, viz, dialogs, references, tour, review, notes), each with its own narrow-screen rules. The split was checked by comparing the computed style of every element before and after.

#### P4.3 Node 22 and the last development vulnerabilities (S)

- **Status: done.** `engines.node >= 22`, Vite 7, Vitest 4, Playwright 1.65, CI on Node 22, `npm audit` clean. `package-lock.json` was regenerated and `npm ci` works; it still has to run on npm 10 in CI (first push).

#### P4.4 The static check and hidden data (S, low priority)

- **Status: done.** The static check rejects private attributes (closing `random._os`), names starting with `_QLP` and NumPy's file functions; the hidden setup runs in its own namespace and only its public names reach the learner's code, while the lesson's check still sees everything. `test_guard.py`. It remains accident prevention, not a sandbox: public hosting still needs P5.1.

#### P4.5 Accessibility beyond the automatic audit (S)

- **Status: automatic part done.** The narrow-screen tabs follow the tab pattern (arrow keys, Home, End, tab panels); the other switchers became plain pressed buttons. axe now also runs on the references page, the notes page and drawer and the review screen, in both themes. Missing: the manual pass with a screen reader.
- **Work:** implement the tab pattern (arrow keys, tab panels) or drop the tab roles in `Lab`, `Visualizer` and the export dialog; run axe on the references page, the dialogs and challenge mode; go through a lesson with NVDA or VoiceOver and fix what is found.
- **Done when:** the tab bars behave as announced and the manual pass is recorded.

#### P4.6 Engine robustness and speed (M)

- **Status: done.** Run replies are bounded (full state kept for evenly spaced steps when a circuit is large, with a notice; Bloch spheres for every step); large replies are serialized off the event loop; Check can be stopped; lesson files are cached by modification time; tracing no longer scans the whole namespace on every line; the shots job skips the trajectory and a heavy run gets its own message; IBM calls have timeouts. **Stable lesson keys:** progress and notes are stored under a slug from `content/lesson_keys.json`, and backups carry the keys, so renumbering a lesson means editing the catalog, the manifest id and that file, with no migration. The existing progress was migrated once at startup, after the daily backup. Open: an id freed by a renumbering and later reused could meet an old row stored under that id.

#### P4.7 Fairer validation (S to M)

- **Status: done.** Sub-circuits are opened before the gate checks, list values compared exactly, a tolerance per variable, the lesson's qubit cap for the reference run, and distribution checks with mid-circuit measurement enumerate the branches exactly (sampling with a tolerance sized by outcomes and shots only above 512 branches).

#### P4.8 CI, license and releases (M)

- **Status: mostly done.** MIT license; CI with timeouts, cancellation of superseded runs, a lint step (`ruff`), pinned indirect dependencies (`engine/constraints.txt`), a job that builds and smoke-tests the Docker images; Dependabot; `THIRD_PARTY_NOTICES.md` and `CHANGELOG.md`. Open: type checking of the engine, path filters for docs-only changes, the first tag.
- **Status: partly done.** Done: MIT license (`LICENSE`, package metadata); CI with timeouts, cancellation of superseded runs and a job that builds and smoke-tests the Docker images. Open: lint and type check for the engine, a lock file for the Python dependencies, Dependabot or Renovate, path filters, third-party notices, tags and a CHANGELOG.
- **Work:** job timeouts, cancellation of superseded runs, a cached browser, path filters for docs-only changes; lint (ruff, eslint) and a type check for the engine; a lock or constraints file for the Python dependencies; Dependabot or Renovate; the Docker build job of P2.2; a LICENSE for the code and one for the lessons (the owner's decision), with third-party notices; tags and a short CHANGELOG, with the version shown in the interface.
- **Done when:** CI covers lint, tests on three systems and the image build; the repository has a license and a first tagged release.

#### P4.9 Tests the audit missed (S to M)

- **Status: done.** Layout and clipping tests, engine tests for malformed messages, `SystemExit`, migrations, backups, notes, stable keys, the content cache, the static check, distribution checks, a database lock and cancelling a queued job (98 more engine tests in this round).

---

### Phase 5: Only if the platform is published

#### P5.1 Public hosting (L)

- **Goal:** open the platform to anyone over the internet.
- **Work:** the pending items in [deploy/README.md](../deploy/README.md): gVisor on the server, one sandbox per session, a security review, a load test and per-IP limits; plus the deploy details of section 8.7 (security headers on `/assets/`, workers against the memory limit, wording of the deploy guide).
- **Done when:** the security review passes and the load test sustains the expected number of people.
- **Note:** for personal use (local or with the Docker of P2.2), none of this is needed.

#### P5.2 Accounts and progress sync (M, optional)

- **Goal:** progress and notes follow the learner between devices without exporting and importing files.
- **Depends on:** P5.1.

---

### Recommended order

| Order | Item | Effort | Why |
| :-- | :-- | :-- | :-- |
| 1 | P1.1 Commit, push and run CI | S | Two days of work exist only on this disk; CI will also be the first run on Windows, macOS and Docker |
| 2 | P3.3 Read Track 1 and Track 6 (owner) and a second pass on the text | M | The text was written by agents; only a person can say whether it reads right |
| 3 | P2.2 Run the Docker path once and publish the image | S to M | Removes the installation barrier |
| 4 | P3.6 Challenges for the remaining lessons of Tracks 3 to 6 | M | 3.3, 3.4, 3.6, 3.7, 4.2 to 4.4, 4.7, 5.2, 6.2, 6.4 |
| 5 | P3.7 Curriculum gaps | L | Backlog, item by item |
| 6 | P4.5 Screen reader pass, P2.6 step 7 (focus mode), P4.8 remaining | S to M | |
| 7 | P5.1 Public hosting, P5.2 Accounts | L | Only if the platform is published |

Done: P1.2, P1.3, P1.4, P2.1, P2.3, P2.4, P2.5, P2.7, P2.8, P3.1, P3.2, P3.4, P3.5, P3.8, P4.1, P4.2, P4.3, P4.4, P4.6, P4.7, P4.9; most of P2.6, P3.6 and P4.8. Written and waiting for a human read: P3.3.
