# Writing guide for lesson text

All learner-facing text is in English. It should read like a good lecture handout written by a physicist who teaches: didactic, concise and exact.

## Voice

- Explain one idea at a time, in the order a learner needs it. Define a term the first time it appears, then use the same word every time.
- Prefer short paragraphs (2–4 sentences) and plain verbs. Address the reader as "you" only when giving an instruction.
- Show, then generalize: a small worked example (numbers, a two-line calculation) is worth more than an adjective.
- Keep every formula, convention and claim exact. Simplify wording, never the physics. If a statement is only true under a condition (pure states, two qubits, up to a global phase), say the condition.
- Cut what does not teach: no motivation paragraphs, no summaries that repeat the section, no closing "in short".

## Things that make text read as machine-written (avoid)

- Filler and hype: "powerful", "magic", "famous", "crucial", "key insight", "it's worth noting", "in essence", "simply", "just", "Let's", "dive", "journey", "elegant".
- Rhetorical questions, and "not X, but Y" / "X isn't just Y" constructions.
- Lists of three adjectives or three parallel clauses used for rhythm.
- Em dashes as general punctuation (use a comma, colon, parentheses or a new sentence). En dashes in names (Deutsch–Jozsa) and ranges (pp. 25–27) are correct and stay.
- Bold on many phrases. Bold only a term at the point where it is defined.
- "Note:" / "Tip:" / "Important:" callouts. Keep a callout only when it is a genuine warning (for example the qubit-ordering convention), and write it as a plain sentence.
- Meta strings joined with middle dots, and labels like "Word — fragment".
- Headings that announce instead of name ("What to watch in the lab" → "In the lab"; "Why this matters" → name the actual idea).

## Terminology (follow Nielsen & Chuang and the IBM Quantum Learning courses)

computational basis; state vector; amplitude; global phase / relative phase; Bloch sphere; Hadamard gate; Pauli X, Y, Z gates; phase gate S; T gate; rotation operators R_x, R_y, R_z; controlled-NOT (CNOT) gate, control qubit, target qubit; controlled operation; tensor product; product state / entangled state; Bell states (|Φ⁺⟩, |Φ⁻⟩, |Ψ⁺⟩, |Ψ⁻⟩); measurement in the computational basis; quantum teleportation; no-cloning theorem; query, oracle (query gate U_f); phase kickback; constant / balanced function; Grover iteration, diffusion operator (inversion about the mean); quantum Fourier transform (QFT); phase estimation; order finding; period; density operator (density matrix); mixed state; purity Tr(ρ²); quantum channel; Kraus operators (operator-sum representation); bit flip, phase flip, depolarizing, amplitude damping channels; three-qubit bit-flip code; syndrome measurement; threshold; ansatz (plural ansätze); variational form; parameter-shift rule; expectation value; Hamiltonian; ground state; variational quantum eigensolver (VQE); quantum approximate optimization algorithm (QAOA); Max-Cut; cost Hamiltonian / mixer Hamiltonian; data re-uploading; variational quantum classifier.

Qubit ordering: the platform follows Qiskit (qubit 0 is the rightmost label, |q_{n-1} … q_1 q_0⟩). Nielsen & Chuang write qubit 0 on the left. Keep this warning wherever a lesson relies on it.

## Format rules (the tests depend on them)

- `text.json`: keep every key. Keep the number of hints and the number of prediction options. The correct prediction option must stay at the same index (it is stored in `manifest.json` as `prediction_answer`). Keys in `messages` must stay, with the same `{placeholders}`. Keys in `views`, `controls` and `comparison` must stay.
- `title` in `text.json` must equal the title in `content/catalog.json`.
- The mission must keep exactly the same requirement the validator checks.
- `starter_code.py`: change comments only. Every line of code stays identical (same names, values, order).
- `theory.md`: Markdown with KaTeX (`$…$`, `$$…$$`). Use `##` headings in sentence case.
