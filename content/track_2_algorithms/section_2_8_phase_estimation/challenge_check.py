"""Challenge for lesson 2.8: phases θ that are not multiples of 1/8. For each one, the circuit
has 4 qubits and uses c_u and qft_dagger; `theta` is the best estimate (the most likely
multiple of 1/8) and `p_best` is the measured probability of that outcome, with an error of up to 0.03
relative to the exact value."""

from qiskit import QuantumCircuit

from qlp_engine import simulator

PHASES = [0.3, 0.2, 0.7, 0.45]
TOLERANCE = 0.03


def check(ns, run_case):
    for phase in PHASES:
        case_ns = run_case(phase)
        qc = case_ns.get("qc")
        if not isinstance(qc, QuantumCircuit):
            return {"passed": False, "key": "no_circuit"}
        if qc.num_qubits != 4:
            return {"passed": False, "key": "wrong_qubits", "params": {"count": qc.num_qubits}}
        names = {i.operation.name for i in qc.data}
        if not {"c_u", "qft_dagger"} <= names:
            return {"passed": False, "key": "gates"}
        distribution = simulator.register_distribution(qc, [0, 1, 2])
        best = max(distribution, key=distribution.get)
        exact_theta = int(best, 2) / 8
        exact_p = distribution[best]
        for name in ("theta", "p_best"):
            if name not in case_ns:
                return {"passed": False, "key": "variable_missing", "params": {"name": name}}
        if abs(float(case_ns["theta"]) - exact_theta) > 1e-9:
            return {"passed": False, "key": "wrong_theta", "params": {"phase": phase, "found": float(case_ns["theta"]), "expected": exact_theta}}
        if abs(float(case_ns["p_best"]) - exact_p) > TOLERANCE:
            return {"passed": False, "key": "wrong_probability", "params": {"phase": phase, "found": float(case_ns["p_best"]), "expected": exact_p}}
    return {"passed": True, "key": "ok", "params": {"total": len(PHASES)}}
