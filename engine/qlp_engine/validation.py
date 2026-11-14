"""Oráculo de validação.

Tipos (campo `validation.type` do manifest):
  state_fidelity       estado final ≈ o da solução (Nível 1)
  counts_distribution  estatística das medições ≈ a da solução
  reduced_state        estado de UM qubit, para várias entradas e todos os ramos de medição
  oracle_cases         distribuição de um registrador, para vários oráculos secretos (Nível 2)
  state_cases          estado final, para várias entradas de teste (Nível 2)

O alvo nunca é digitado à mão: vem da execução do `solution.py` da lição com a
mesma entrada. Entradas chegam ao setup oculto pela variável `_QLP_INPUT`.
Regras comuns: allowed_gates, required_gates, max_gates, forbidden_pairs, expected_variables.
"""

from __future__ import annotations

import numpy as np

from . import simulator, tracer
from .messages import percent, t

DEFAULT_TOLERANCE = 0.999
DEFAULT_DISTRIBUTION_TOLERANCE = 0.05
DEFAULT_ORACLE_TOLERANCE = 0.02
PROBABILITY_ATOL = 1e-3
VALIDATION_SEED = 1234
DEFAULT_SHOTS = 4096
REDUCED_STATE_TRIALS = 4
BRANCH_SEEDS = 32

# Portas criadas pelos setups ocultos, mostradas pelo nome da função que o aluno chama.
FRIENDLY_NAMES = {
    "c_mod_mult": "apply_controlled_mod_mult",
    "c_u": "apply_controlled_u",
    "qft_dagger": "inverse_qft",
    "oracle": "oracle",
    "grover_oracle": "oracle",
    "prepare_input": "prepare_input",
    "psi": "prepare_alice_state",
}


def validate(code: str, lesson: dict) -> dict:
    """Valida o código do aluno contra as regras da lição. Nunca levanta exceção."""
    rules = lesson.get("validation") or {}
    kind = rules.get("type")
    checker = {
        "state_fidelity": _check_state,
        "counts_distribution": _check_counts,
        "reduced_state": _check_reduced_state,
        "oracle_cases": _check_oracle_cases,
        "state_cases": _check_state_cases,
        "custom": _check_custom,
    }.get(kind)
    if checker is None:
        return _result(False, "unsupported", t("val.unsupported", kind=kind))

    max_qubits = int(lesson.get("max_qubits") or simulator.DEFAULT_MAX_QUBITS)
    lesson = {**lesson, "code": code}
    try:
        qiskit = lesson.get("framework", "qiskit") == "qiskit"
        student = tracer.execute(
            code, lesson.get("hidden_setup"), _first_case(rules), trace=qiskit, require_circuit=qiskit
        )
        if kind == "custom":
            return _check_custom(student, lesson, rules)
        problem = _structural_problem(student.circuit, rules)
        if problem:
            return problem
        result = checker(student.circuit, lesson, rules, max_qubits)
        if result["passed"] and rules.get("expected_variables"):
            return _check_variables(result, student.namespace, rules["expected_variables"])
        return result
    except tracer.UserCodeError as exc:
        return _result(False, "error", exc.message, line=exc.line)
    except simulator.SimulationError as exc:
        return _result(False, "error", exc.message, line=exc.line)


def _first_case(rules: dict) -> dict | None:
    cases = rules.get("cases")
    return {"_QLP_INPUT": cases[0]} if cases else None


def _structural_problem(circuit, rules: dict) -> dict | None:
    forbidden = _forbidden_gates(circuit, rules.get("allowed_gates"))
    if forbidden:
        names = ", ".join(f"`{name}`" for name in forbidden)
        return _result(False, "forbidden_gate", t("val.forbidden_gate", names=names))
    missing = sorted(set(rules.get("required_gates") or []) - {i.operation.name for i in circuit.data})
    if missing:
        names = ", ".join(f"`{FRIENDLY_NAMES.get(name, 'qc.' + name)}`" for name in missing)
        return _result(False, "required_gate", t("val.required_gate", names=names))
    for name, expected in (rules.get("gate_counts") or {}).items():
        actual = sum(1 for i in circuit.data if i.operation.name == name)
        if actual != expected:
            friendly = FRIENDLY_NAMES.get(name, "qc." + name)
            return _result(False, "gate_count", t("val.gate_count", name=friendly, expected=expected, actual=actual))
    pair = _forbidden_pair(circuit, rules.get("forbidden_pairs"))
    if pair:
        return _result(False, "forbidden_pair", t("val.forbidden_pair", a=pair[0], b=pair[1]))
    max_gates = rules.get("max_gates")
    if max_gates is not None and _gate_count(circuit) > max_gates:
        return _result(False, "too_many_gates", t("val.too_many_gates", limit=max_gates, count=_gate_count(circuit)))
    return None


# --------------------------------------------------------------------------- #
# Nível 1
# --------------------------------------------------------------------------- #


def _check_state(circuit, lesson: dict, rules: dict, max_qubits: int) -> dict:
    student_state = simulator.run_trajectory(circuit, seed=VALIDATION_SEED, max_qubits=max_qubits).states[-1]
    target_state = target_statevector(lesson)
    if student_state.shape != target_state.shape:
        expected = int(np.log2(target_state.size))
        return _result(False, "qubit_mismatch", t("val.qubit_count", expected=expected, actual=circuit.num_qubits))

    fidelity = state_fidelity(target_state, student_state)
    tolerance = float(rules.get("tolerance", DEFAULT_TOLERANCE))
    if fidelity >= tolerance:
        return _result(True, "ok", t("val.state_ok", fidelity=percent(fidelity)), fidelity=fidelity)

    same_probabilities = np.allclose(np.abs(student_state) ** 2, np.abs(target_state) ** 2, atol=PROBABILITY_ATOL)
    if same_probabilities:
        return _result(False, "phase", t("val.phase"), fidelity=fidelity)
    return _result(False, "wrong_state", t("val.state_wrong", fidelity=percent(fidelity)), fidelity=fidelity)


def _check_counts(circuit, lesson: dict, rules: dict, max_qubits: int) -> dict:
    """Compara a distribuição das medições com a da solução de referência.

    Usado quando a missão termina em medição: o estado final colapsa, então o
    que caracteriza a resposta é a estatística dos resultados.
    """
    if not any(instruction.operation.name == "measure" for instruction in circuit.data):
        return _result(False, "no_measurement", t("val.no_measurement"))
    shots = int(rules.get("shots", DEFAULT_SHOTS))
    reference = tracer.execute(lesson["solution"], lesson.get("hidden_setup")).circuit
    if circuit.num_clbits != reference.num_clbits:
        return _result(
            False, "qubit_mismatch", t("val.clbit_count", expected=reference.num_clbits, actual=circuit.num_clbits)
        )
    expected = _distribution(reference, shots, VALIDATION_SEED, simulator.DEFAULT_MAX_QUBITS)
    observed = _distribution(circuit, shots, VALIDATION_SEED + 1, max_qubits)
    if total_variation(expected, observed) <= float(rules.get("tolerance", DEFAULT_DISTRIBUTION_TOLERANCE)):
        return _result(True, "ok", t("val.distribution_ok", observed=describe(observed)))
    return _result(
        False,
        "wrong_distribution",
        t("val.distribution_wrong", observed=describe(observed), expected=describe(expected)),
    )


def _check_reduced_state(circuit, lesson: dict, rules: dict, max_qubits: int) -> dict:
    """O estado de UM qubit ao final precisa coincidir com o da solução, para vários
    estados de entrada (pares de ângulos em `_QLP_INPUT`) e todos os ramos de medição.
    """
    qubit = int(rules["qubit"])
    if circuit.num_qubits <= qubit:
        return _result(False, "qubit_mismatch", t("val.reduced_qubit_missing", qubit=qubit, actual=circuit.num_qubits))
    tolerance = float(rules.get("tolerance", DEFAULT_TOLERANCE))
    rng = np.random.default_rng(VALIDATION_SEED)
    worst = 1.0
    branches_ok = branches_total = 0
    # Entradas fixas primeiro (ex.: |0⟩ e |+⟩, onde cada correção do teletransporte
    # fica invisível), depois sorteadas longe dos polos.
    fixed = [tuple(map(float, pair)) for pair in rules.get("inputs") or []]
    random_trials = [
        (float(rng.uniform(0.4, np.pi - 0.4)), float(rng.uniform(0, 2 * np.pi)))
        for _ in range(int(rules.get("trials", REDUCED_STATE_TRIALS)))
    ]
    for angles in fixed + random_trials:
        inputs = {"_QLP_INPUT": angles}
        reference = tracer.execute(lesson["solution"], lesson.get("hidden_setup"), inputs).circuit
        target = _bloch(simulator.run_trajectory(reference, seed=0).states[-1], reference.num_qubits, qubit)
        student = tracer.execute(lesson["code"], lesson.get("hidden_setup"), inputs).circuit
        for seed in range(BRANCH_SEEDS):
            state = simulator.run_trajectory(student, seed=seed, max_qubits=max_qubits).states[-1]
            fidelity = (1.0 + float(np.dot(target, _bloch(state, student.num_qubits, qubit)))) / 2.0
            worst = min(worst, fidelity)
            branches_total += 1
            branches_ok += fidelity >= tolerance
    if worst >= tolerance:
        return _result(True, "ok", t("val.reduced_ok", qubit=qubit, total=branches_total), fidelity=worst)
    if branches_ok:
        return _result(False, "partial", t("val.reduced_partial", ok=branches_ok, total=branches_total), fidelity=worst)
    return _result(False, "wrong_state", t("val.reduced_wrong", qubit=qubit, fidelity=percent(worst)), fidelity=worst)


# --------------------------------------------------------------------------- #
# Nível 2
# --------------------------------------------------------------------------- #


def _check_oracle_cases(circuit, lesson: dict, rules: dict, max_qubits: int) -> dict:
    """Para cada oráculo secreto, a distribuição do registrador precisa bater com a
    da solução. Garante que a solução é geral e não foi escrita para um caso só."""
    register = [int(q) for q in rules["register"]]
    tolerance = float(rules.get("tolerance", DEFAULT_ORACLE_TOLERANCE))
    failures = []
    for case in rules["cases"]:
        inputs = {"_QLP_INPUT": case}
        reference = tracer.execute(lesson["solution"], lesson.get("hidden_setup"), inputs).circuit
        student = tracer.execute(lesson["code"], lesson.get("hidden_setup"), inputs).circuit
        if student.num_qubits <= max(register):
            return _result(False, "qubit_mismatch", t("val.qubit_count", expected=reference.num_qubits, actual=student.num_qubits))
        expected = simulator.register_distribution(reference, register)
        observed = simulator.register_distribution(student, register, max_qubits=max_qubits)
        if total_variation(expected, observed) > tolerance:
            failures.append((expected, observed))
    total = len(rules["cases"])
    if not failures:
        return _result(True, "ok", t("val.oracle_ok", total=total))
    if len(failures) < total:
        return _result(False, "partial", t("val.oracle_partial", ok=total - len(failures), total=total))
    expected, observed = failures[0]
    return _result(False, "wrong_distribution", t("val.oracle_wrong", observed=describe(observed), expected=describe(expected)))


def _check_state_cases(circuit, lesson: dict, rules: dict, max_qubits: int) -> dict:
    """Para cada entrada de teste, o estado final precisa coincidir com o da solução."""
    tolerance = float(rules.get("tolerance", DEFAULT_TOLERANCE))
    worst, ok = 1.0, 0
    for case in rules["cases"]:
        inputs = {"_QLP_INPUT": case}
        reference = tracer.execute(lesson["solution"], lesson.get("hidden_setup"), inputs).circuit
        student = tracer.execute(lesson["code"], lesson.get("hidden_setup"), inputs).circuit
        if student.num_qubits != reference.num_qubits:
            return _result(False, "qubit_mismatch", t("val.qubit_count", expected=reference.num_qubits, actual=student.num_qubits))
        target = simulator.run_trajectory(reference, seed=VALIDATION_SEED).states[-1]
        state = simulator.run_trajectory(student, seed=VALIDATION_SEED, max_qubits=max_qubits).states[-1]
        fidelity = state_fidelity(target, state)
        worst = min(worst, fidelity)
        ok += fidelity >= tolerance
    total = len(rules["cases"])
    if ok == total:
        return _result(True, "ok", t("val.cases_ok", total=total), fidelity=worst)
    if ok:
        return _result(False, "partial", t("val.cases_partial", ok=ok, total=total), fidelity=worst)
    return _result(False, "wrong_state", t("val.state_wrong", fidelity=percent(worst)), fidelity=worst)


def _check_custom(student, lesson: dict, rules: dict) -> dict:
    """Validação própria da lição: `check.py` define check(ns, run_case).

    `ns` é o namespace do aluno; `run_case(entrada)` executa o código de novo com
    `_QLP_INPUT = entrada` e devolve o namespace. check() devolve
    {"passed", "key", "params"}; a mensagem vem de `messages[key]` no text.json
    da lição.
    """
    qiskit = lesson.get("framework", "qiskit") == "qiskit"

    def run_case(case):
        return tracer.execute(
            lesson["code"], lesson.get("hidden_setup"), {"_QLP_INPUT": case},
            trace=qiskit, require_circuit=qiskit,
        ).namespace

    module: dict = {"__name__": "qlp_check"}
    exec(compile(lesson["check"], "<check>", "exec"), module)
    try:
        outcome = module["check"](student.namespace, run_case)
    except tracer.UserCodeError:
        raise
    except Exception as exc:  # noqa: BLE001 - erro do aluno ao ser avaliado (ex.: função com assinatura errada)
        from .tracer import _describe

        return _result(False, "error", _describe(exc))
    params = {k: _format_param(v) for k, v in (outcome.get("params") or {}).items()}
    template = (lesson.get("messages") or {}).get(outcome["key"], outcome["key"])
    return _result(bool(outcome["passed"]), outcome["key"], template.format(**params), fidelity=outcome.get("fidelity"))


def _format_param(value):
    """Números com até 4 casas; o resto como texto."""
    if isinstance(value, float):
        if 0 < abs(value) < 1e-4:  # erros desprezíveis: "< 0.0001" em vez de notação científica
            return "< 0.0001"
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return value


def _check_variables(result: dict, namespace: dict, expected: dict) -> dict:
    """Confere variáveis que o aluno precisa calcular (ex.: os fatores no Shor)."""
    for name, value in expected.items():
        if name not in namespace:
            return _result(False, "variable_missing", t("val.variable_missing", name=name))
        actual = namespace[name]
        if not _same_value(actual, value):
            return _result(False, "variable_wrong", t("val.variable_wrong", name=name, actual=_show(actual), expected=_show(value)))
    name, value = next(iter(expected.items()))
    return {**result, "message": t("val.all_ok", first=result["message"], name=name, value=_show(value))}


def _same_value(actual, expected) -> bool:
    if isinstance(expected, list):
        try:
            return sorted(int(v) for v in actual) == sorted(int(v) for v in expected)
        except (TypeError, ValueError):
            return False
    try:
        return abs(float(actual) - float(expected)) < 1e-9
    except (TypeError, ValueError):
        return actual == expected


def _show(value) -> str:
    if isinstance(value, (list, tuple, set)):
        return "[" + ", ".join(str(v) for v in sorted(value)) + "]"
    return str(value)


# --------------------------------------------------------------------------- #
# Auxiliares
# --------------------------------------------------------------------------- #


def _bloch(state: np.ndarray, n: int, qubit: int) -> np.ndarray:
    from .geometry import bloch_vectors

    vectors, _ = bloch_vectors(state, n)
    return np.array(vectors[qubit])


def _forbidden_pair(circuit, pairs: list[list[int]] | None) -> tuple[int, int] | None:
    if not pairs:
        return None
    index = {bit: i for i, bit in enumerate(circuit.qubits)}
    for instruction in circuit.data:
        touched = {index[q] for q in instruction.qubits}
        for a, b in pairs:
            if a in touched and b in touched:
                return a, b
    return None


def _distribution(circuit, shots: int, seed: int, max_qubits: int) -> dict[str, float]:
    """Distribuição exata quando as medições são só no final; senão, por amostragem."""
    exact = simulator.exact_distribution(circuit, max_qubits)
    if exact is not None:
        return exact
    sampled = simulator.sample_counts(circuit, shots, seed=seed, max_qubits=max_qubits)
    return {key: count / sampled["shots"] for key, count in sampled["counts"].items()}


def total_variation(p: dict[str, float], q: dict[str, float]) -> float:
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def describe(distribution: dict[str, float], limit: int = 4) -> str:
    """Os resultados mais prováveis, ex.: '000: 100%' ou '0: 50%, 1: 50%'."""
    top = sorted(((v, k) for k, v in distribution.items() if v > 0.005), reverse=True)[:limit]
    return ", ".join(f"{key}: {percent(value, 0)}" for value, key in sorted(top, key=lambda item: item[1]))


def target_statevector(lesson: dict) -> np.ndarray:
    """Estado alvo, obtido executando a solução de referência da lição."""
    solution = lesson.get("solution")
    if not solution:
        raise ValueError(f"A lição {lesson.get('id')} não tem solution.py.")
    reference = tracer.execute(solution, lesson.get("hidden_setup"))
    return simulator.run_trajectory(reference.circuit, seed=VALIDATION_SEED).states[-1]


def state_fidelity(target: np.ndarray, state: np.ndarray) -> float:
    """F = |<alvo|estado>|^2 — invariante a fase global."""
    return float(abs(np.vdot(target, state)) ** 2)


def _forbidden_gates(circuit, allowed: list[str] | None) -> list[str]:
    if allowed is None:
        return []
    permitted = set(allowed) | {"barrier"}
    used = {instruction.operation.name for instruction in circuit.data}
    return sorted(used - permitted)


def _gate_count(circuit) -> int:
    return sum(1 for instruction in circuit.data if instruction.operation.name != "barrier")


def _result(passed: bool, code: str, message: str, fidelity: float | None = None, line: int | None = None) -> dict:
    return {
        "passed": passed,
        "code": code,
        "message": message,
        "fidelity": None if fidelity is None else round(fidelity, 6),
        "line": line,
    }
