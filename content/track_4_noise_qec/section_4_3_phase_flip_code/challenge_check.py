"""Challenge for lesson 4.3: a three-qubit code against Y errors.

The learner changes `encode` and `recover` of the mission so that they correct a Y error on any
one of the three data qubits. The check builds its own five-qubit circuits (data qubits 0, 1, 2 and
ancillas 3, 4): four random input states (fixed seed, so a hard-coded answer fails), the learner's
`encode`, a Y error on one qubit or none, then `recover`. The reference is the state that `encode`
alone produces, so any choice of code space is accepted; the data qubits must return to it.
"""

import numpy as np
import pennylane as qml

ERRORS = ["none", 0, 1, 2]
TOLERANCE = 0.999


def _inputs():
    rng = np.random.default_rng(7)
    return [(float(np.arccos(rng.uniform(-1, 1))), float(rng.uniform(0, 2 * np.pi))) for _ in range(4)]


def _describe(exc):
    return f"{type(exc).__name__}: {exc}"


def _reference(dev, encode, theta, phi):
    @qml.qnode(dev)
    def circuit():
        qml.RY(theta, wires=0)
        qml.RZ(phi, wires=0)
        encode()
        return qml.density_matrix(wires=[0, 1, 2])

    return circuit


def _noisy(dev, encode, recover, theta, phi, error):
    @qml.qnode(dev)
    def circuit():
        qml.RY(theta, wires=0)
        qml.RZ(phi, wires=0)
        encode()
        if error != "none":
            qml.PauliY(wires=error)
        recover()
        return qml.density_matrix(wires=[0, 1, 2])

    return circuit


def check(ns, run_case):
    encode, recover = ns.get("encode"), ns.get("recover")
    if not callable(encode) or not callable(recover):
        return {"passed": False, "key": "ch_missing", "params": {"name": "encode" if not callable(encode) else "recover"}}

    dev = qml.device("default.qubit", wires=5)
    worst = 1.0
    for theta, phi in _inputs():
        try:
            ref = np.array(_reference(dev, encode, theta, phi)())
        except Exception as exc:  # noqa: BLE001 - the learner's code can fail in any way
            return {"passed": False, "key": "ch_error", "params": {"detail": _describe(exc)}}
        for error in ERRORS:
            try:
                rho = np.array(_noisy(dev, encode, recover, theta, phi, error)())
            except Exception as exc:  # noqa: BLE001
                return {"passed": False, "key": "ch_error", "params": {"detail": _describe(exc)}}
            # `ref` is pure (the ancillas start in |00⟩ and encode leaves them alone), so the
            # fidelity is Tr(ref · rho).
            fidelity = float(np.real(np.trace(ref @ rho)))
            worst = min(worst, fidelity)
            if fidelity < TOLERANCE:
                key = "ch_idle" if error == "none" else "ch_fail"
                return {"passed": False, "key": key, "params": {"error": f"Y on {error}", "fidelity": fidelity}}
    return {"passed": True, "key": "ch_ok", "params": {"worst": worst}}
