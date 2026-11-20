# Changelog

Notable changes to the platform.

## Unreleased

### Added
- `scripts/run-docker.sh` starts Ket Lab with Docker in one command: it shows the download, runs the container in the background and says where to open it once it is ready. The README uses it.

### Changed
- The engine's start line has no token in single-user and public modes, where none is used.

## 0.4.0

### Added
- Challenges for eleven more lessons, so every lesson of Tracks 3 to 6 now has one (the projects excepted): QAOA on a ring (3.3), a one-qubit classifier (3.4), SPSA against parameter shift on 12 angles (3.6), a local cost and its gradients (3.7), correction without ancillas (4.2), a code against Y errors (4.3), which pairs of errors defeat the Shor code (4.4), the threshold of a 7-qubit model (4.7), any two-qubit Pauli from counts (5.2), the Landau–Zener formula (6.2) and the exact minimum chain strength (6.4).
- Lesson 4.3 has a button for a Y error on qubit 1, and the chart of lesson 3.7 can show the local and global costs side by side.
- The Docker image is published for arm64 as well (Apple Silicon, ARM Linux), under the same tag.
- The About dialog shows the version, with a link to its release notes.

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
