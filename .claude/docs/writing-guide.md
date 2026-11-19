# Writing guide for lesson text

All learner-facing text is in English. It should read like a good lecture handout written by a physicist who teaches: didactic, concise and exact, and recognizably written by a person.

## Voice

The lessons should read as written by a person who teaches the subject and remembers what was hard about it. Rigor stays; uniformity goes.

- **Open with the problem, on a small concrete case.** Two or three sentences on what the lesson lets you do or what goes wrong without it, with a number or a tiny circuit. The definition comes when the word is needed, not in the first line.
- **Work one example by hand.** Every lesson has at least one calculation with real numbers that the reader can check on paper or in the lab. Show, then generalize.
- **Say what is hard.** One honest sentence per lesson on where people usually slip, or on what is surprising ("the sign is easy to lose here", "this is the case that usually goes wrong"). Do not invent drama; if nothing is hard, say nothing.
- **Explain one idea at a time**, in the order a learner needs it. Define a term the first time it appears, then use the same word every time. Do not use a term before it is defined; if it comes from another lesson, point to that lesson.
- **Prose by default.** A table only when three or more items are compared on three or more aspects. A list only for steps or genuinely parallel items. Never a table or list that repeats the prose above it.
- **Vary the rhythm.** Mix short and long sentences. Address the reader as "you" when it is natural, and always when giving an instruction.
- **Keep every formula, convention and claim exact.** Simplify wording, never the physics. If a statement holds only under a condition (pure states, two qubits, M much smaller than N, up to a global phase), say the condition. Do not state an interpretation of quantum mechanics as a fact.
- **Cut what does not teach**: no summaries that repeat the section, no closing "in short", no one-line moral at the end of a paragraph.
- **Do not copy a skeleton from another lesson.** Two lessons should not share their sequence of headings. The qubit-ordering warning appears once, where it first matters in the lesson, as a sentence.
- **"In the lab"** is optional. When present it is a task: predict something, then check it in the lab. It never describes what the screen shows.

## Things that make text read as machine-written (avoid)

- Filler and hype: "powerful", "magic", "famous", "crucial", "key insight", "it's worth noting", "in essence", "simply", "just", "Let's", "dive", "journey", "elegant".
- Rhetorical questions, and "not X, but Y" / "X isn't just Y" constructions.
- Lists of three adjectives or three parallel clauses used for rhythm; "The effect depends on three things:" followed by three bold words.
- Opening a lesson with "A **term** is …".
- A sentence that ends a paragraph with a tidy moral ("The ceiling comes from the ansatz.").
- "This is why …" / "which is why …" as a connective.
- Em dashes as general punctuation (use a comma, colon, parentheses or a new sentence). En dashes in names (Deutsch–Jozsa) and ranges (pp. 25–27) are correct and stay.
- Bold on many phrases. Bold only a term at the point where it is defined.
- "Note:" / "Tip:" / "Important:" callouts. Keep a callout only when it is a genuine warning, and write it as a plain sentence.
- Meta strings joined with middle dots, and labels like "Word — fragment".
- Headings that announce instead of name ("Why this matters" → name the actual idea).
- "The IBM course also says …" as a closing sentence. Cite something specific or leave it out; the references list already points to the course.

## Objectives, mission, hints, predictions and messages

- **Objectives**: two to four plain statements of what the learner can do afterwards, in the learner's words. They do not repeat the mission steps and do not name library functions.
- **Mission**: says exactly what the validator checks, in one short paragraph. A reason for the task comes before the instructions, in a sentence.
- **Hints** are a ladder for someone who is stuck. The first is a question to ask yourself or the place to look. The middle one gives the idea. The last gives code only where the code is the easy part, and never the whole solution: the solution has its own button. Two to four hints, as the lesson needs.
- **Prediction**: asks for a consequence of the theory, never for a sentence the reader has just read. Wrong options are mistakes a learner really makes, never absurd values. The correct option is not systematically the longest. Its position is spread evenly over the platform (a test checks this).
- **Messages** (validation feedback): name the probable mistake in the learner's terms ("the probabilities are right but the phase of |1⟩ is wrong") before suggesting what to do. Avoid the mould "X should be A, but it is B. Use f(…)". A success message says in one line what the learner has just shown.
- **Review questions** (`review.json`): 8 to 12 per track, each tied to a lesson of the track, with an explanation of at least one full sentence. They do not copy a lesson's prediction. The correct position varies.
- **Challenges and projects**: the text starts from the reason for the task. A project's rubric lives in the validator's messages; the theory does not list it as a specification.
- **Glossary**: one or two sentences in the same voice as the lessons, saying what the thing is and where it is used. No circular definitions.

## Terminology (follow Nielsen & Chuang and the IBM Quantum Learning courses)

computational basis; state vector; amplitude; global phase / relative phase; Bloch sphere; Hadamard gate; Pauli X, Y, Z gates; phase gate S; T gate; rotation operators R_x, R_y, R_z; controlled-NOT (CNOT) gate, control qubit, target qubit; controlled operation; tensor product; product state / entangled state; Bell states (|Φ⁺⟩, |Φ⁻⟩, |Ψ⁺⟩, |Ψ⁻⟩); measurement in the computational basis; quantum teleportation; no-cloning theorem; query, oracle (query gate U_f); phase kickback; constant / balanced function; Grover iteration, diffusion operator (inversion about the mean); quantum Fourier transform (QFT); phase estimation; order finding; period; density operator (density matrix); mixed state; purity Tr(ρ²); quantum channel; Kraus operators (operator-sum representation); bit flip, phase flip, depolarizing, amplitude damping channels; three-qubit bit-flip code; syndrome measurement; threshold; ansatz (plural ansätze); variational form; parameter-shift rule; expectation value; Hamiltonian; ground state; variational quantum eigensolver (VQE); quantum approximate optimization algorithm (QAOA); Max-Cut; cost Hamiltonian / mixer Hamiltonian; data re-uploading; variational quantum classifier.

Qubit ordering: the platform follows Qiskit (qubit 0 is the rightmost label, |q_{n-1} … q_1 q_0⟩). Nielsen & Chuang write qubit 0 on the left. Keep this warning wherever a lesson relies on it.

## Format rules (the tests depend on them)

- `text.json`: keep every key. Keys in `messages` must stay, with the same `{placeholders}` (the validators fill them). Keys in `views`, `controls` and `comparison` must stay. Three prediction options.
- The index of the correct prediction option is stored in `manifest.json` as `prediction_answer`. If you reorder the options, change it in the same edit.
- `title` in `text.json` must equal the title in `content/catalog.json`; `summary` likewise.
- The mission must keep exactly the same requirement the validator checks.
- `starter_code.py`: change comments only. Every line of code stays identical (same names, values, order).
- `solution.py`: starts with a comment that gives the idea, and each step has a comment explaining why, not what (a test checks this).
- `theory.md`: Markdown with KaTeX (`$…$`, `$$…$$`). Use `##` headings in sentence case.
- References only from [verified-references.md](../../docs/verified-references.md).
