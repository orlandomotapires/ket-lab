# Adding a lesson

A lesson is a folder under `content/track_N_.../section_X_Y_name/`. The engine loads it at startup, so restart `npm run dev` to see a new or changed lesson. The quickest way to start is to copy a lesson of the same kind and change it.

In the current lab layout (mission on top, since 23 Nov 2026) the learner sees the mission, "Before you start" and the prediction; `theory.md`, the hints and "Show solution" are not on screen for now. Keep writing them in full: the tests check them and they come back with the theory panel.

## Checklist

1. **Catalog.** Add the lesson to `content/catalog.json` with its `id`, `title` and `summary`. The title must equal the one in the lesson's `text.json`.
2. **Files** (below).
3. **Text** written by the rules of the [writing guide](writing-guide.md).
4. **References** in the manifest: at least one book or article and one course or tutorial, each with the exact place to read in `location`. The first course or tutorial and the first paper (or book, if there is no paper) are what "Before you start" shows above the code, so put the best first read first. Use only sources listed in [verified-references.md](../../docs/verified-references.md); to cite something new, verify it and add it there first.
5. **Glossary.** New terms go into `content/glossary.json`, with the lesson that introduces them. Every term must appear in some theory.
6. **Review.** Add one or two questions about the lesson to the track's `review.json`.
7. **Prediction position.** The index of the correct option is `prediction_answer` in the manifest. A test keeps the three positions balanced over the platform, so check which position is least used.
8. **Run** `npm run test:engine`. The content suite checks every item of this list that can be checked by a machine.

## Files

| File | Required | What it holds |
| :-- | :-- | :-- |
| `manifest.json` | yes | Structure, no text: `id`, `track`, `estimated_minutes`, `framework` (`qiskit` by default, `pennylane` or `python`), visualizations, `validation`, `prediction_answer`, `references`; optional `challenge`, `project`, `controls`, `timeout`, `max_qubits` |
| `text.json` | yes | `title`, `summary`, `objectives`, `mission`, `hints`, `prediction` (three options), `messages`; `challenge` text when the manifest has a challenge |
| `theory.md` | yes | Theory in Markdown with KaTeX |
| `starter_code.py` | yes | What the editor shows at first. It must run without passing |
| `solution.py` | yes | The reference solution. The validation target is computed by running it. It is also what "Show solution" displays, so it starts with a comment giving the idea and explains each step |
| `hidden_setup.py` | no | Code run before the learner's: oracles, inputs, helpers. Each secret case arrives in `_KET_LAB_INPUT` |
| `check.py` | for `custom` validation | `check(ns, run_case)` returns `{"passed", "key", "params"}`; `key` selects a message in `text.json` and `params` fills its placeholders |
| `analysis.py` | no | `analyze(ns)` returns the data of the training visualizations (convergence, landscape and others) |
| `challenge_solution.py`, `challenge_check.py`, `challenge_hidden_setup.py` | for a challenge | The same roles, for the optional challenge |

## Validation types

Validation compares mathematics, not text, so any equivalent solution passes.

| Type | Checks | Example |
| :-- | :-- | :-- |
| `state_fidelity` | The final state, up to a global phase | 1.1 |
| `counts_distribution` | The statistics of the measurements | 1.2, 2.9 |
| `reduced_state` | The state of one qubit, for several inputs and every measurement branch | 1.6 |
| `oracle_cases` | The distribution of a register against several secret oracles | 1.4, 2.2, 2.3 |
| `state_cases` | The final state for several inputs | 1.3, 1.7, 2.7 |
| `custom` | Whatever the lesson's `check.py` decides, with its own messages | Tracks 0, 3, 4 and 5; projects |

Constraints against shortcuts go in the manifest's `validation`: `allowed_gates`, `required_gates`, `max_gates`, `gate_counts`, `forbidden_pairs`. `expected_variables` checks values the learner computes after the circuit; a variable may carry its own tolerance, as in `"theta": {"value": 0.375, "tolerance": 0.02}`.

## Kinds of lesson

- **Qiskit circuit** (Tracks 1 and 2). The code runs as the learner types and the state is shown after each instruction.
- **PennyLane** (`framework: "pennylane"`). Declare which QNode to draw in `qnode`. With `live: false` the code runs only from the Run button, which suits training loops.
- **No circuit** (`framework: "python"`). The learner defines numeric variables and the interface shows them in a table. Such a lesson can also show charts: see "Charts" below.
- **Challenge.** An optional harder task after the mission, under `challenge` in the manifest and in `text.json`. The suite requires that the challenge solution passes and that the mission's solution does not.
- **Project** (`"project": true`). The last lesson of a track. Its `check.py` is a rubric that reports the first criterion that fails, each with its own message.

## Charts

Any lesson can draw line or point charts from the learner's variables. List `"curve"` in the manifest's `available_visualizers` (next to `"variables"` in a lesson without a circuit) and add an `analysis.py` whose `analyze(ns)` returns `{"curve": CHART}`, or `{"curve": [CHART, CHART]}` for charts stacked one under the other:

```text
CHART = {
  "title": str,                 # optional
  "x_label": str, "y_label": str,
  "log_x": bool, "log_y": bool, # optional
  "series": [{"label": str, "x": [numbers], "y": [numbers],
              "points": bool,   # optional: markers only, no line
              "dashed": bool}], # optional: a muted reference line
  "markers": [{"x": number, "y": number, "label": str}]   # optional: a ringed point with a short label
}
```

`ns` is the learner's namespace after the run. Write `analyze` defensively: when a variable is missing or malformed, return `{}` and never raise, because the learner's code is unfinished most of the time. Points that are not finite are dropped (also non-positive ones on a log axis), and with nothing left the interface shows "No data yet". Up to four series are told apart by color, dash pattern and marker shape. Lessons 3.6, 3.7 and 6.2 are examples.

Lesson 4.2 (the bit-flip code) uses most of these pieces at once and is a good one to read.
