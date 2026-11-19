# Ket Lab

Learn quantum computing by writing circuits and watching the state change.

I wanted a place to learn quantum computing where the equations move. This is it: you write Qiskit or PennyLane code, and while you type, the platform shows what each gate does to the state. Put the cursor on a line and the Bloch spheres and amplitudes show the state right after it.

It is built for one person studying on their own. There are no accounts, teachers or deadlines. Everything runs on your machine, and your progress stays there.

## What studying here looks like

Each lesson has three parts side by side: the theory on the left, your code in the middle, the quantum state on the right. The theory explains one idea with a worked example. Then you get a mission, for example "prepare the Bell state |Φ⁺⟩ on qubits 0 and 1", and the Check button tells you whether your circuit does it.

The check compares physics, not text, so any circuit that reaches the right state passes. If you are stuck there are hints, and after the hints a commented solution. Many lessons also have an optional, harder challenge.

The lessons follow Nielsen & Chuang and the IBM Quantum Learning courses, and each one says where to read more, down to the section and the page.

## The tracks

| Track | Topics | Lessons |
| :-- | :-- | :-- |
| 0. Mathematical toolkit (optional) | Complex numbers, vectors, matrices, tensor products | 4 |
| 1. Basics of quantum information | Qubits, phase, interference, entanglement, teleportation, no-cloning, superdense coding, the CHSH game | 11 |
| 2. Quantum algorithms | Deutsch–Jozsa, Bernstein–Vazirani, Simon, Grover, the Fourier transform, phase estimation, Shor, Hamiltonian simulation | 11 |
| 3. Variational algorithms | Parameter shift, VQE for H₂, QAOA, classifiers, ansatz design, SPSA, barren plateaus | 9 |
| 4. Noise and error correction | Density matrices, bit-flip, phase-flip and Shor codes, stabilizers, the toric code, the threshold theorem | 8 |
| 5. Running on hardware | Transpilation, Sampler and Estimator, T1 and T2, error mitigation, a run on a real IBM device | 5 |
| 6. Quantum annealing | Ising models and QUBO, the adiabatic theorem, the anneal as a circuit, embedding and what annealers can really do | 5 |

That is 53 lessons and about 25 hours. Each track from 1 on ends with a project and a short review quiz.

Around the lessons there is a free lab with ready examples and OpenQASM export, a glossary of 142 terms, a notes drawer for each lesson, and a search that covers lessons, notes and terms.

## Running it

You need Python 3.11 or newer and Node 22 or newer (nvm or fnm make Node 22 easy to install).

```bash
npm run setup   # once: checks the versions, creates engine/.venv and installs everything
npm run dev     # then open http://localhost:5173
```

Progress is saved in `~/.local/share/quantum-learning-platform` on Linux. The engine also keeps a dated copy of it every day, and the Backup button on the tracks page exports everything, notes included, to one file.

There is also a Docker setup that needs neither Python nor Node: `docker compose -f deploy/local.yml up --build`, then open <http://localhost:8080>. It has not been tried on a real machine yet, so expect rough edges.

So far the platform has only been tested on Linux.

## How it is built

```text
app/        the interface: React, TypeScript, Monaco, Three.js
engine/     the Python engine: runs your code, simulates, checks missions, stores progress
content/    the lessons, the glossary and the catalog
docs/       the verified reading list behind every lesson reference
deploy/     Docker files, for local use or a hosted server
```

The interface talks to the engine over a WebSocket on 127.0.0.1, with a session token. Your code runs in a separate process with time and memory limits, so an infinite loop only costs you a restart of that process.

A browser-only build is in progress: the same engine runs in the page through Pyodide, so the site can be served as static files on GitHub Pages. [deploy/README.md](deploy/README.md) covers the optional Docker server.

## Working on it

```bash
npm test             # engine tests and the interface's type check and unit tests
npm run test:e2e     # end-to-end tests in the browser (needs Google Chrome)
```

The engine suite runs every lesson's solution against its own check and makes sure the starter code does not pass. Independent physics tests recompute the results of each track.

Every lesson reference points to a page someone checked; the list is in [docs/verified-references.md](docs/verified-references.md).

## License

[MIT](LICENSE). The libraries and fonts the platform uses are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), and the changes in [CHANGELOG.md](CHANGELOG.md). The lecture notes used as background while writing the lessons are not part of this repository.
