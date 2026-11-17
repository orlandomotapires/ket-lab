# Third-party notices

The Quantum Learning Platform is released under the [MIT license](LICENSE). It uses the following software and fonts, each under its own license. They are installed as dependencies and are not copied into this repository.

## Engine (Python)

| Package | License | Use |
| :-- | :-- | :-- |
| Qiskit | Apache-2.0 | Circuits, transpiler and primitives in the lessons |
| PennyLane | Apache-2.0 | Variational circuits and noise channels |
| NumPy, SciPy | BSD-3-Clause | Simulation and numerics |
| websockets | BSD-3-Clause | Connection between the interface and the engine |
| qiskit-ibm-runtime (optional extra) | Apache-2.0 | Running a circuit on IBM hardware with the learner's key |

## Interface (JavaScript)

| Package | License | Use |
| :-- | :-- | :-- |
| React, React DOM | MIT | Interface |
| Zustand | MIT | State |
| Monaco Editor | MIT | Code editor |
| KaTeX, react-markdown, remark and rehype plugins | MIT | Theory text and formulas |
| three.js, React Three Fiber, drei | MIT | Bloch sphere and Q-Sphere |
| Vite, Vitest, Playwright, TypeScript, axe-core | MIT, Apache-2.0, MPL-2.0 | Build and tests (development only) |

## Fonts

IBM Plex Sans and IBM Plex Mono, by IBM, under the SIL Open Font License 1.1, served with the interface through the `@fontsource` packages.

## Sources of the lessons

The lesson text is original. The books, papers and courses it cites are listed on the References page of the platform and in [docs/verified-references.md](docs/verified-references.md); nothing from them is reproduced beyond short formulas and standard results. The lecture notes used as background during development are third-party material and are not part of this repository.

The license of each installed package can be checked with `pip show <package>` and in `app/node_modules/<package>/package.json`.
