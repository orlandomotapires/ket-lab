"""Challenge for lesson 5.2: any two-qubit Pauli expectation value from Sampler counts.

`pauli_from_counts(qc, pauli, sampler)` receives a two-qubit circuit without measurements, a label
such as "XY" and a Sampler, and must return the estimate of ⟨pauli⟩ for the state prepared by qc.
The label follows Qiskit's SparsePauliOp convention: its rightmost letter acts on qubit 0 and its
leftmost on qubit 1; "I" means that qubit is not measured for the product. The check calls the
function on three states and nine labels it builds itself (a hard-coded answer fails), with a
seeded StatevectorSampler of 20000 shots, and compares with Statevector.expectation_value. The
limit is 4.5 standard errors of a ±1 average, 4.5/√20000 ≈ 0.032, which a correct function
passes essentially always and which every missing or misplaced basis change on these cases
misses by more.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import SparsePauliOp, Statevector

SHOTS = 20_000
LIMIT = 4.5 / np.sqrt(SHOTS)
# (angles of the preparation, labels to test on it)
STATES = [
    ((1.0, 0.6, 2.0, 1.2, 0.8), ["YY", "YX", "IY"]),
    ((0.7, 1.1, 0.4, 0.9, -1.1), ["YI", "ZX", "YY"]),
    ((2.2, -1.2, 1.0, 0.3, 1.9), ["XY", "YZ", "XZ"]),
]


def _prepare(angles):
    a, b, c, d, e = angles
    qc = QuantumCircuit(2)
    qc.ry(a, 0)
    qc.rx(b, 1)
    qc.cx(0, 1)
    qc.rz(c, 0)
    qc.ry(d, 1)
    qc.rx(e, 0)
    return qc


def check(ns, run_case):
    function = ns.get("pauli_from_counts")
    if not callable(function):
        return {"passed": False, "key": "ch_no_function"}
    worst = 0.0
    for index, (angles, labels) in enumerate(STATES):
        for k, label in enumerate(labels):
            qc = _prepare(angles)
            size = len(qc.data)
            sampler = StatevectorSampler(default_shots=SHOTS, seed=100 * index + k)
            try:
                estimate = float(np.real(function(qc, label, sampler)))
            except Exception as error:  # noqa: BLE001
                return {"passed": False, "key": "ch_error", "params": {"label": label, "error": f"{type(error).__name__}: {error}"}}
            if not np.isfinite(estimate):
                return {"passed": False, "key": "ch_bad_return", "params": {"label": label}}
            if len(qc.data) != size:
                return {"passed": False, "key": "ch_modified", "params": {"label": label}}
            exact = float(np.real(Statevector(_prepare(angles)).expectation_value(SparsePauliOp(label))))
            error = abs(estimate - exact)
            if error > LIMIT:
                params = {"label": label, "actual": round(estimate, 3), "exact": round(exact, 3), "limit": round(LIMIT, 3)}
                if abs(estimate + exact) <= LIMIT:
                    return {"passed": False, "key": "ch_sign", "params": params}
                if "I" in label:
                    return {"passed": False, "key": "ch_identity", "params": params}
                return {"passed": False, "key": "ch_wrong", "params": params}
            worst = max(worst, error)
    return {"passed": True, "key": "ok", "params": {"worst": round(worst, 3), "limit": round(LIMIT, 3)}}
