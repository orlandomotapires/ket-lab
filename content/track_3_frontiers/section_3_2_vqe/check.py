# Hamiltoniano molecular do H₂ em 0,74 Å, base STO-3G, mapeamento de Jordan-Wigner
# (4 qubits). Pré-calculado com qml.qchem.molecular_hamiltonian(method="dhf") para
# não depender de química em tempo de execução. Energia exata: -1.1372838 Ha.
H2_TERMS = [
    (-0.0970662078, 'IIII'),
    (0.171412835, 'ZIII'),
    (0.171412835, 'IZII'),
    (0.1686889846, 'ZZII'),
    (-0.2234315573, 'IIZI'),
    (0.1206252378, 'ZIZI'),
    (0.1659278524, 'IZZI'),
    (0.0453026146, 'YXXY'),
    (-0.0453026146, 'YYXX'),
    (-0.0453026146, 'XXYY'),
    (0.0453026146, 'XYYX'),
    (-0.2234315573, 'IIIZ'),
    (0.1659278524, 'ZIIZ'),
    (0.1206252378, 'IZIZ'),
    (0.1744128778, 'IIZZ'),
]

"""Validação da lição 3.2: a energia do estado que o circuito prepara.

Não confia no valor que o aluno calcula: reconstrói o estado do circuito com
os parâmetros finais e calcula ⟨ψ|H|ψ⟩ com um Hamiltoniano próprio.
"""

import numpy as np
import pennylane as qml

from qlp_engine import pl, simulator

EXACT = -1.1372838351669659
CHEMICAL_ACCURACY = 1.6e-3


def _hamiltonian_matrix():
    ops = [qml.pauli.string_to_pauli_word(word) for _, word in H2_TERMS]
    return qml.matrix(qml.Hamiltonian([c for c, _ in H2_TERMS], ops), wire_order=range(4))


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "no_circuit"}
    if "theta" not in ns:
        return {"passed": False, "key": "no_theta"}
    ops, lines, n = pl.trace_qnode(circuit, [ns["theta"]])
    if n != 4:
        return {"passed": False, "key": "wrong_qubits", "params": {"count": n}}
    state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    # O simulador usa a ordem do Qiskit; a matriz do PennyLane, o fio 0 como bit mais significativo.
    state = state.reshape((2,) * n).transpose(range(n)[::-1]).reshape(-1)
    energy = float(np.real(np.vdot(state, _hamiltonian_matrix() @ state)))
    error = energy - EXACT
    params = {"energy": energy, "error": abs(error), "exact": EXACT}
    if error <= CHEMICAL_ACCURACY:
        return {"passed": True, "key": "ok", "params": params}
    return {"passed": False, "key": "not_converged", "params": params}
