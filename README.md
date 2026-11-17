# Quantum Learning Platform

A web platform for learning quantum computing by writing Qiskit code and watching the quantum state change as you type. The interface and the lessons are in English.

Everything about the project (architecture, curriculum, history and next steps) is in a single document: [docs/master-plan.md](docs/master-plan.md).

## Current state

- **Seven tracks, 53 lessons** (including 6 end-of-track projects):
  - Track 0 (optional), math kit: complex numbers, vectors, matrices, tensor product.
  - Track 1, *Basics of Quantum Information*: from the qubit to teleportation, no-cloning, superdense coding and the CHSH game.
  - Track 2, *Fundamentals of Quantum Algorithms*: from Deutsch to Shor, with Simon and Hamiltonian simulation.
  - Track 3, *Variational Algorithms*: parameter-shift, VQE, QAOA, classifiers, ansatz design, optimizers (SPSA), barren plateaus and a hardware-efficient VQE.
  - Track 4, *Quantum Noise and Error Correction*: density matrix, bit-flip, phase-flip and Shor codes, stabilizers, toric code and threshold.
  - Track 5, *Running on Quantum Hardware*: transpilation, primitives, T1/T2 and error mitigation.
  - Track 6, *Adiabatic Computing and Quantum Annealing*: Ising models and QUBO, the adiabatic theorem, the anneal as a circuit, embedding and the limits of annealers.
- **Learning objectives** in every lesson and **34 optional challenges** across Tracks 1 to 6, unlocked after the mission.
- **Qiskit and PennyLane**, with density-matrix noise simulation; numerical lessons without a circuit in the math kit.
- **Lab**: code that runs as you type, a click-based circuit composer, OpenQASM 2/3 export, training runs with a live curve, share links (with a review step before running) and execution on a real IBM quantum computer (with the learner's own key; extra `engine[hardware]`).
- **Visualizations**: Bloch spheres, Q-Sphere, amplitudes, phases, register, cost landscapes, convergence, graphs, decision boundaries, variable table.
- **Notes**: a drawer in the lab for the open lesson and a notes page on the hub, saved as you type, searchable and part of the backup.
- **Review** at the end of Tracks 1 to 6: multiple-choice questions that point back to the lessons to revisit.
- **Glossary** with 141 terms, shown as tooltips in the theory and on a page of its own, with a filter; **references** with exact section and pages (Nielsen & Chuang, Griffiths & Schroeter, IBM courses).
- **Accessibility**: WCAG 2.1 AA checked with axe, circuit navigable by keyboard, text description of the state; tabbed layout on narrow screens; first-lesson guide.
- **Progress** in SQLite (local engine) or in the browser (hosted engine), with export and import as a backup; the local engine also keeps a dated copy of its database.
- **Web**: local engine (`npm run dev`) or hosted engine (`deploy/`).

Only Linux has been tested. Windows and macOS depend on CI.

## Structure

```text
app/        Interface (React + TypeScript + Three.js + Monaco); texts in app/src/strings.ts
engine/     Python engine (Qiskit): execution, simulation, validation, progress, messages
content/    Lessons (manifest, texts, theory, starter code, solution, hidden setup) and catalog
scripts/    dev.mjs: starts the engine and the interface together
docs/       Master plan, writing guide, how to add a lesson, verified references
```

## Prerequisites

- Python 3.11 or newer
- Node.js 22 or newer (Vite 7 does not run on older versions; install it with nvm or fnm)

## How to run

```bash
npm run setup   # once: creates engine/.venv and installs the dependencies
npm run dev     # engine + interface; open http://localhost:5173
```

The interface reloads on every change. The engine loads the lessons at startup, so new or changed lessons only appear after restarting `npm run dev`.

`npm run setup` checks the Node and Python versions before installing anything, and works on Linux, macOS and Windows.

Progress is kept in the user's data directory (`~/.local/share/quantum-learning-platform` on Linux). To isolate a session, set `QLP_DATA_DIR=/some/path`. With `QLP_LOG=1`, the engine logs every connection and request to the terminal.

## Just use it (Docker)

To study without installing Python or Node: `docker compose -f deploy/local.yml up`, then open http://localhost:8080. Progress is kept in a Docker volume. This path has not been verified yet (see P2.2 in [docs/master-plan.md](docs/master-plan.md)).

## Publish on the web

The web version runs the engine on a server, behind the site (`deploy/`): `SITE_ORIGIN=https://… docker compose -f deploy/docker-compose.yml up --build`. Read [deploy/README.md](deploy/README.md) first: learner code runs on the server, and what is still missing before opening to the public is listed there. The reason it does not run in the browser is in [docs/web-engine-decision.md](docs/web-engine-decision.md).

## Tests

```bash
npm test             # engine (pytest) + interface (types and vitest)
npm run test:engine
npm run test:app
npm run test:e2e     # end to end (Playwright; needs Google Chrome installed)
```

The engine suite includes:

- **content suite**: in every lesson, the solution passes the oracle and the starter code runs without passing;
- **Track 2 physics tests**: results checked independently of the solutions;
- **PennyLane tests**: the state of each QNode is compared with PennyLane's own, including with noise.

## Create a lesson

See [docs/adding-a-lesson.md](docs/adding-a-lesson.md): the files of a lesson, the validation types and a checklist. The text follows the [writing guide](docs/writing-guide.md).

## How the interface and the engine talk

`npm run dev` starts the engine (`python -m qlp_engine`) on a fixed port (8765) with a session token, and Vite passes these values to the interface (`VITE_ENGINE_PORT`, `VITE_ENGINE_TOKEN`). The interface opens a WebSocket at `ws://127.0.0.1:8765`; the engine only accepts connections with the right token and from the allowed origins (`--allow-origin`). Learner code runs in a separate process, with time and memory limits.

## License

[MIT](LICENSE). The software and fonts it depends on are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), and changes are recorded in [CHANGELOG.md](CHANGELOG.md). The lecture notes used as background during development are third-party material and are not part of this repository.
