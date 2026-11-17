"""Challenge for lesson 2.9: the base a is secret (a in {2, 7, 4, 11, 13, 8}, N = 15). The circuit
has 8 qubits and uses c_mod_mult and qft_dagger; the variable `order` must be the order
of a modulo 15."""

from qiskit import QuantumCircuit

BASES = [2, 7, 4, 11, 13, 8]


def true_order(a, n=15):
    r, value = 1, a % n
    while value != 1:
        value = value * a % n
        r += 1
    return r


def check(ns, run_case):
    for base in BASES:
        case_ns = run_case(base)
        qc = case_ns.get("qc")
        if not isinstance(qc, QuantumCircuit):
            return {"passed": False, "key": "no_circuit"}
        if qc.num_qubits != 8:
            return {"passed": False, "key": "wrong_qubits", "params": {"count": qc.num_qubits}}
        names = {i.operation.name for i in qc.data}
        if not {"c_mod_mult", "qft_dagger"} <= names:
            return {"passed": False, "key": "gates"}
        if "order" not in case_ns:
            return {"passed": False, "key": "variable_missing"}
        expected = true_order(base)
        if case_ns["order"] != expected:
            return {"passed": False, "key": "wrong_order", "params": {"found": str(case_ns["order"])}}
    return {"passed": True, "key": "ok", "params": {"total": len(BASES)}}
