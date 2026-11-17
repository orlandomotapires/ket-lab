"""Validation for project 2.11 (design a Grover oracle).

Rubric: (1) `oracle(qc)` exists and is unitary; (2) on its own, the oracle gives phase −1
exactly on the solutions of f and +1 on the others, with the ancillas back in |0⟩;
(3) `iterations` is the optimum for N = 8 and M = 2; (4) the success probability
of the full circuit is at least 0.95; (5) `solutions` lists the solutions
found by run_shots.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

SOLUTIONS = {"010", "101"}
OPTIMAL_ITERATIONS = 1
THRESHOLD = 0.95


def f(x):
    a, b, c = x & 1, (x >> 1) & 1, (x >> 2) & 1
    return bool((a or b) and ((not a) or c) and ((not b) or (not c)))


def check(ns, run_case):
    oracle = ns.get("oracle")
    if not callable(oracle):
        return {"passed": False, "key": "no_oracle"}
    probe = QuantumCircuit(5)
    try:
        oracle(probe)
        unitary = Operator(probe).data
    except Exception as exc:  # noqa: BLE001 - learner error while building the oracle
        return {"passed": False, "key": "oracle_error", "params": {"detail": str(exc)[:120]}}

    wrong_sign, not_diagonal = [], []
    for x in range(8):
        column = unitary[:, x]  # input |x⟩ with the ancillas in |0⟩ (index x)
        sign = -1.0 if f(x) else 1.0
        if abs(column[x] - sign) < 1e-6:
            continue
        if abs(abs(column[x]) - 1) < 1e-6 and abs(column[x] + sign) < 1e-6:
            wrong_sign.append(format(x, "03b"))
        else:
            not_diagonal.append(format(x, "03b"))
    if not_diagonal:
        return {"passed": False, "key": "oracle_not_clean", "params": {"states": ", ".join(not_diagonal)}}
    if wrong_sign:
        marked = {format(x, "03b") for x in range(8) if f(x)}
        flipped = {s for s in wrong_sign if s not in marked}
        missing = sorted(set(wrong_sign) - flipped)
        if flipped:
            return {"passed": False, "key": "oracle_extra", "params": {"states": ", ".join(sorted(flipped))}}
        return {"passed": False, "key": "oracle_missing", "params": {"states": ", ".join(missing)}}

    iterations = ns.get("iterations")
    if iterations != OPTIMAL_ITERATIONS:
        return {"passed": False, "key": "iterations", "params": {"value": iterations}}

    circuit = ns.get("qc")
    if not isinstance(circuit, QuantumCircuit) or circuit.num_qubits < 3:
        return {"passed": False, "key": "no_circuit"}
    try:
        unmeasured = circuit.remove_final_measurements(inplace=False)
        probabilities = Statevector(unmeasured).probabilities([0, 1, 2])
    except Exception as exc:  # noqa: BLE001
        return {"passed": False, "key": "circuit_error", "params": {"detail": str(exc)[:120]}}
    success = float(sum(probabilities[int(s, 2)] for s in SOLUTIONS))
    if success < THRESHOLD:
        return {"passed": False, "key": "success_low", "fidelity": success, "params": {"probability": success}}

    reported = ns.get("solutions")
    try:
        found = {str(s) for s in reported}
    except TypeError:
        found = None
    if found != SOLUTIONS:
        shown = ", ".join(sorted(found)) if found else "none"
        return {"passed": False, "key": "solutions", "params": {"found": shown}}
    return {"passed": True, "key": "ok", "fidelity": success, "params": {"probability": success, "found": ", ".join(sorted(found))}}
