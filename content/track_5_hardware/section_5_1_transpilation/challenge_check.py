"""Challenge for lesson 5.1: a 5-qubit GHZ state on a T-shaped device with edges 0-1, 1-2, 1-3 and
3-4. The transpiled circuit must use only the basis gates, only connected pairs, prepare the GHZ
state and use 4 two-qubit gates, the minimum for 5 qubits (each CNOT can reach one new qubit)."""

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity

BASIS = {"rz", "sx", "x", "cx"}
EDGES = {(0, 1), (1, 2), (1, 3), (3, 4)}
BUDGET = 4


def ghz_state():
    ghz = QuantumCircuit(5)
    ghz.h(0)
    for i in range(4):
        ghz.cx(i, i + 1)
    return Statevector(ghz)


def check(ns, run_case):
    qc = ns.get("qc")
    if not isinstance(qc, QuantumCircuit):
        return {"passed": False, "key": "ch_no_circuit"}
    if qc.num_qubits != 5:
        return {"passed": False, "key": "ch_wrong_qubits", "params": {"count": qc.num_qubits}}
    bad = sorted({inst.operation.name for inst in qc.data} - BASIS - {"barrier"})
    if bad:
        return {"passed": False, "key": "ch_not_basis", "params": {"gates": ", ".join(bad)}}
    two_qubit = [inst for inst in qc.data if len(inst.qubits) == 2]
    for inst in two_qubit:
        a, b = (qc.find_bit(q).index for q in inst.qubits)
        if tuple(sorted((a, b))) not in EDGES:
            return {"passed": False, "key": "ch_not_connected", "params": {"a": a, "b": b}}
    try:
        state = Statevector(qc)
    except Exception:  # measurements or non-unitary gates
        return {"passed": False, "key": "ch_not_unitary"}
    fidelity = float(state_fidelity(state, ghz_state()))
    if fidelity < 0.999:
        return {"passed": False, "key": "ch_wrong_state", "params": {"fidelity": fidelity}, "fidelity": fidelity}
    if len(two_qubit) > BUDGET:
        return {"passed": False, "key": "ch_too_many", "params": {"count": len(two_qubit), "budget": BUDGET}, "fidelity": fidelity}
    return {"passed": True, "key": "ch_ok", "params": {"count": len(two_qubit), "depth": qc.depth()}, "fidelity": fidelity}
