# Changelog

Notable changes to the platform.

## Unreleased

### Added
- `scripts/run-docker.sh` starts Ket Lab with Docker in one command: it shows the download, runs the container in the background and says where to open it once it is ready. The README uses it.
- **Before you start**, next to the mission: a course page and a paper (or a book) from the lesson's references, to read or watch before writing code.
- Each Bloch arrow shows its state at the tip, as α|0⟩ + β|1⟩, or "mixed" when the qubit is entangled or noisy.
- Previous and next lesson buttons right after "Tracks", in the same place for every lesson.
- Drag handles between the code and the state, and between the code and the circuit. Double-click one to go back to the starting size.

### Changed
- A new lab layout, on trial. The mission runs across the top, and below it the code and the state sit side by side at the same height. The theory text, hints and the solution offer are hidden in this layout for now.
- Code and circuit share one panel: show either one, or both. The circuit starts hidden.
- A correct answer to "Predict before you run" turns the button green, and the answer is remembered.
- "Before you start" and "Predict before you run" open as popovers under the mission bar, over the code and the state, so the layout no longer moves. A click outside or Escape closes them.
- "What you will learn" (the "i" by the lesson name) lists the lesson's key terms instead of sentences. Each term opens its glossary entry, and hovering one shows the definition. The terms are the new `key_terms` field in each lesson's `text.json`, and a test checks that each one is in the glossary.
- The mouse wheel zooms the Bloch spheres and the Q-sphere in and out, around the pointer. Ctrl+wheel and pinch still work. Scrolling out once the spheres are back at their normal size scrolls the panel instead.
- The About button in the top bar shows the Ket Lab mark instead of an "i", so on a lesson screen the only "i" is the one by the lesson name.
- Inside a lesson, the search is a magnifier button to the left of Notes. A click, Ctrl+K or "/" opens the field in its place, and Escape or leaving it empty folds it back.
- `deploy/local.yml` only builds from the local code (`docker compose -f deploy/local.yml up --build`, image `ket-lab:local`); the published image runs with `scripts/run-docker.sh`.
- Under the Q-sphere you see entanglement and amplitudes; under the Bloch spheres, the Bloch vectors.
- A reload keeps the lesson you were in: the address now carries it (`#lesson=1.2`).
- Alt+1 and Alt+2 go to the code and the state (there is no theory panel to jump to).
- Smaller corner radii everywhere.
- The engine's start line has no token in single-user and public modes, where none is used.
- A permanent `developer` branch sits between `main` and the work branches: branches merge into `developer`, and `developer` into `main`. CI runs when a change is pushed or merged into `developer` or `main`; other branches and pull requests get no automatic run (it took too long on every commit), and "Run workflow" in the Actions tab still runs it by hand. Dependabot opens its pull requests against `developer`.

### Fixed
- Typing in the search right after a lesson opened could close the list of results while the field still had the cursor: the editor takes focus for a moment as the lesson loads.

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
- Images in notes: paste a picture (Ctrl+V) or drop it on a note, or press "Add image". Thumbnails sit under the text and open at full size. Large pictures are scaled down. The images are kept with the notes (in the engine, or in the browser on the hosted site) and go into the backup file.

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
