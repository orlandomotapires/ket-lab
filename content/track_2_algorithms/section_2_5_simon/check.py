"""Validation for lesson 2.5: for each secret s (including 000), the circuit queries the
oracle once, the input register only produces y with y·s = 0 (mod 2), with the
exact uniform distribution over those y, and the variable s_found equals s."""

from qiskit import QuantumCircuit

from qlp_engine import simulator

SECRETS = ["110", "101", "011", "111", "001", "100", "010", "000"]
TOLERANCE = 0.02


def orthogonal(y: int, s: int) -> bool:
    return bin(y & s).count("1") % 2 == 0


def check(ns, run_case):
    for secret in SECRETS:
        case_ns = run_case(secret)
        qc = case_ns.get("qc")
        if not isinstance(qc, QuantumCircuit):
            return {"passed": False, "key": "no_circuit"}
        if qc.num_qubits != 6:
            return {"passed": False, "key": "wrong_qubits", "params": {"count": qc.num_qubits}}
        queries = sum(1 for i in qc.data if i.operation.name == "oracle")
        if queries != 1:
            return {"passed": False, "key": "queries", "params": {"count": queries}}
        if not any(i.operation.name == "measure" for i in qc.data):
            return {"passed": False, "key": "no_measurement"}
        observed = simulator.register_distribution(qc, [0, 1, 2])
        allowed = [y for y in range(8) if orthogonal(y, int(secret, 2))]
        expected = {format(y, "03b"): 1 / len(allowed) for y in allowed}
        keys = set(observed) | set(expected)
        tv = 0.5 * sum(abs(observed.get(k, 0.0) - expected.get(k, 0.0)) for k in keys)
        if tv > TOLERANCE:
            bad = sorted(k for k in observed if k not in expected and observed[k] > TOLERANCE)
            return {"passed": False, "key": "wrong_distribution", "params": {"secret": secret, "bad": ", ".join(bad) or "none"}}
        if "s_found" not in case_ns:
            return {"passed": False, "key": "variable_missing"}
        found = case_ns["s_found"]
        if found != secret:
            return {"passed": False, "key": "wrong_secret", "params": {"found": str(found), "secret": secret}}
    return {"passed": True, "key": "ok", "params": {"total": len(SECRETS)}}
