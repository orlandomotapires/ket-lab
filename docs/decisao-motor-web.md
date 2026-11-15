# Decision: where the engine runs on the web (item 1.1 of the November 2026 roadmap; history in plano-diretor.md, section 6.1)

**Decision: no-go for running the whole engine in the browser. The web version uses a hosted engine (item 1.2b of the same roadmap; see docs/plano-diretor.md).**

## What was measured

Pyodide in Node (same WebAssembly runtime as the browser), on the development machine, November 2026.

| Step | Pyodide 0.26.4 | Pyodide 0.27.5 |
|---|---|---|
| Load the runtime | 1.2 s | 1.2 s |
| NumPy + micropip | 0.4 s | 1.0 s |
| `qiskit==2.6.2` | fails: no pure-Python wheel (Rust core) | same |
| `pennylane==0.45.1` | fails: needs NumPy ≥ 2 (runtime has 1.26) | fails: needs `rustworkx`, which has no WebAssembly build |
| `rustworkx` | fails: no pure-Python wheel | same |
| `autograd`, `networkx`, `scipy` | install (0.2–2 s each) | install |
| 200 single-qubit gates on 10 qubits (NumPy state vector) | 0.40 s | 0.30 s |

The engine's own code (tracer, simulator, validation) is NumPy-based and would run, at roughly 5–10× native speed. The blockers are the two libraries the lessons teach:

- **Qiskit** (Tracks 1–2, and the planned hardware track) has a compiled Rust core.
- **PennyLane** (Track 3) depends on `rustworkx`, also compiled Rust, and lesson 3.2 uses `qml.qchem`.

## Why not a compatible shim

A browser version would need a re-implementation of the subset of `QuantumCircuit` the lessons use, plus PennyLane's QNode, optimizers, autodiff and `qchem`. That is several weeks of work, and learners would then write code against a look-alike API instead of real Qiskit and PennyLane. That breaks the point of aligning the platform with the IBM courses: code learned here should run unchanged in Qiskit.

## Consequences

- The web version runs the real engine on a server (`deploy/`): the browser loads the static interface and talks to the engine over a WebSocket on the same site.
- On a hosted engine, learner code runs on the server, so the container is the security boundary (the AST check in `guard.py` is not). See `deploy/README.md` for the hardening applied and what remains before a public launch.
- Progress is stored in the learner's browser in hosted mode (one shared engine must not mix learners' progress).
- Revisit if Qiskit or rustworkx publish WebAssembly wheels (Pyodide's package index is the place to check).
