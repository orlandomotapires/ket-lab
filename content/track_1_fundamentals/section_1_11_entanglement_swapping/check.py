"""Validação do projeto 1.11 (troca de emaranhamento).

Rubrica: (1) tamanho do circuito; (2) nenhuma porta atua em 0 e 3 ao mesmo
tempo; (3) os qubits 0 e 3 não são medidos; (4) o estado reduzido de (0, 3) é
|Φ+⟩ em todos os ramos de medição; (5) c_before ≈ 0 e c_after ≈ 1, a
concorrência de (0, 3), conferidas contra o cálculo feito aqui.
"""

import numpy as np

from qlp_engine import simulator

BRANCHES = 40
FIDELITY = 0.999
PHI_PLUS = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)


def pair_state(state, n=4):
    """Matriz densidade de (0, 3), com a convenção de ordem do Qiskit (qubit 0 à direita)."""
    tensor = np.asarray(state).reshape((2,) * n)  # eixo k = qubit n-1-k
    moved = np.moveaxis(tensor, [0, n - 1], [0, 1])  # eixos: qubit 3, qubit 0, o resto
    matrix = moved.reshape(4, -1)
    return matrix @ matrix.conj().T


def concurrence(rho):
    sy = np.array([[0, -1j], [1j, 0]])
    yy = np.kron(sy, sy)
    flipped = yy @ rho.conj() @ yy
    roots = np.sqrt(np.clip(np.sort(np.linalg.eigvals(rho @ flipped).real)[::-1], 0, None))
    return float(max(0.0, roots[0] - roots[1] - roots[2] - roots[3]))


def check(ns, run_case):
    circuit = ns.get("qc")
    if circuit is None or circuit.num_qubits != 4:
        return {"passed": False, "key": "wrong_size"}

    index = {bit: i for i, bit in enumerate(circuit.qubits)}
    for item in circuit.data:
        touched = {index[q] for q in item.qubits}
        if item.operation.name == "barrier":
            continue
        if {0, 3} <= touched:
            return {"passed": False, "key": "forbidden_pair"}
        if item.operation.name == "measure" and touched & {0, 3}:
            return {"passed": False, "key": "measured_end", "params": {"qubit": min(touched & {0, 3})}}
    if not any(i.operation.name == "measure" for i in circuit.data):
        return {"passed": False, "key": "no_measurement"}

    worst, good, outcomes = 1.0, 0, set()
    for seed in range(BRANCHES):
        trajectory = simulator.run_trajectory(circuit, seed=seed)
        rho = pair_state(trajectory.states[-1])
        fidelity = float(np.real(PHI_PLUS.conj() @ rho @ PHI_PLUS))
        worst = min(worst, fidelity)
        good += fidelity >= FIDELITY
        outcomes.add(tuple(trajectory.clbits))
    if good < BRANCHES:
        key = "branch_wrong" if good == 0 else "branch_partial"
        return {
            "passed": False, "key": key, "fidelity": worst,
            "params": {"good": good, "total": BRANCHES, "outcomes": len(outcomes), "fidelity": worst},
        }

    before, after = ns.get("c_before"), ns.get("c_after")
    if not isinstance(before, (int, float)) or not isinstance(after, (int, float)):
        return {"passed": False, "key": "no_record"}
    if abs(float(before)) > 0.05:
        return {"passed": False, "key": "before_wrong", "params": {"value": float(before)}}
    if abs(float(after) - 1.0) > 0.05:
        return {"passed": False, "key": "after_wrong", "params": {"value": float(after)}}
    return {
        "passed": True, "key": "ok", "fidelity": worst,
        "params": {"total": BRANCHES, "outcomes": len(outcomes), "before": float(before), "after": float(after)},
    }
