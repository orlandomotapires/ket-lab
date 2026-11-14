"""Validação da lição 5.1: o circuito transpilado usa só as portas da base, respeita a
conectividade linear, prepara o GHZ de 4 qubits e usa no máximo 3 portas de dois qubits."""

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity

BASIS = {"rz", "sx", "x", "cx"}
EDGES = {(0, 1), (1, 2), (2, 3)}
BUDGET = 3


def ghz_state():
    ghz = QuantumCircuit(4)
    ghz.h(0)
    for i in range(3):
        ghz.cx(i, i + 1)
    return Statevector(ghz)


def check(ns, run_case):
    qc = ns.get("qc")
    if not isinstance(qc, QuantumCircuit):
        return {"passed": False, "key": "no_circuit"}
    if qc.num_qubits != 4:
        return {"passed": False, "key": "wrong_qubits", "params": {"count": qc.num_qubits}}
    bad = sorted({inst.operation.name for inst in qc.data} - BASIS - {"barrier"})
    if bad:
        return {"passed": False, "key": "not_basis", "params": {"gates": ", ".join(bad)}}
    two_qubit = [inst for inst in qc.data if len(inst.qubits) == 2]
    for inst in two_qubit:
        a, b = (qc.find_bit(q).index for q in inst.qubits)
        if tuple(sorted((a, b))) not in EDGES:
            return {"passed": False, "key": "not_adjacent", "params": {"a": a, "b": b}}
    try:
        state = Statevector(qc)
    except Exception:  # medições ou portas não unitárias
        return {"passed": False, "key": "not_unitary"}
    fidelity = float(state_fidelity(state, ghz_state()))
    if fidelity < 0.999:
        return {"passed": False, "key": "wrong_state", "params": {"fidelity": fidelity}, "fidelity": fidelity}
    if len(two_qubit) > BUDGET:
        return {"passed": False, "key": "too_many", "params": {"count": len(two_qubit), "budget": BUDGET}, "fidelity": fidelity}
    return {"passed": True, "key": "ok", "params": {"count": len(two_qubit), "depth": qc.depth()}, "fidelity": fidelity}
