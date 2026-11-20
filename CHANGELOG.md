# Changelog

Notable changes to the platform.

## 0.3.0

### Changed
- The project is called ket-lab everywhere: the repository (`orlandomotapires/ket-lab`), the site (https://orlandomotapires.github.io/ket-lab/), the Docker image (`ghcr.io/orlandomotapires/ket-lab`), the Python package (`ket_lab_engine`) and the environment variables (`KET_LAB_*`). The old repository links redirect; the old site address does not.
- Saved progress moves to the new name by itself: the progress folder (`quantum-learning-platform` to `ket-lab`) and, in the browser, the `qlp.*` keys to `ket-lab.*`.
- Docker: the progress volume is now `ket-lab-progress`. To keep progress saved with 0.2.0, run the new image with `-v qlp-progress:/data`.

## 0.2.0

### Added
- Ket Lab in the browser, on GitHub Pages: the engine (Python, Qiskit, PennyLane) runs in the page through Pyodide, with no server and no install. Progress stays in the browser.
- Track 6, Adiabatic Computing and Quantum Annealing: Ising models and QUBO, the adiabatic theorem, the anneal as a circuit, embedding and the limits of annealers.
- Track 3 lessons on ansatz design, optimizers (SPSA), barren plateaus and a hardware-efficient VQE.
- Notes: a drawer in the lab and a notes page, saved as you type, searchable and part of the backup.
- End-of-track reviews with a screen of their own, and the best score on the hub.
- Glossary page with a filter; clicking a term in a lesson opens its entry.
- About dialog, keyboard shortcuts, "Continue" for the last lesson opened.
- "Show solution" for missions and challenges, with commented solutions for every lesson.
- Backup dialog: export and import of progress and notes, also with the local engine; the engine keeps a dated copy of its database each day.
- MIT license.

### Changed
- Every lesson, the reviews and the glossary rewritten by a new writing guide; prediction answers spread evenly over the three positions.
- The lesson screen keeps the mission always visible; objectives, readouts and finished tracks collapse; one main action in the bottom bar.
- The whole repository is in English.
- A new logo, a Bloch sphere with cat ears, and a shorter README with a demo and screenshots; the longer descriptions moved to the wiki.
- Node 22, Vite 7, Vitest 4; the interface's first download dropped from 4.0 MB to about 0.2 MB.

### Fixed
- The engine always answers a request, keeps what the code printed before an error, and survives `raise SystemExit`.
- A correct solution built from a sub-circuit is accepted.
- Progress of challenges and notes follows its lesson when lessons are renumbered.

## 0.1.0

First version: Tracks 0 to 5, the lab with live state per instruction, validation by physics, the hosted mode.
