"""Challenge for lesson 4.2: a bit-flip recovery with no ancilla qubits.

`recover_compact()` must undo the encoding on the three data wires and fix qubit 0 by majority,
using wires 0, 1 and 2 only. The check builds its own three-wire circuits: five random input
states (fixed seed, so a hard-coded answer fails), the learner's `encode`, an X error on each
qubit in turn or none, then `recover_compact`. It requires that qubit 0 ends in the input state.
The recovery decodes, so the data qubits are not required to stay in the code space.
"""

import numpy as np
import pennylane as qml

ERRORS = ["none", 0, 1, 2]
TOLERANCE = 0.999


def _inputs():
    rng = np.random.default_rng(42)
    return [(float(np.arccos(rng.uniform(-1, 1))), float(rng.uniform(0, 2 * np.pi))) for _ in range(5)]


def _state(theta, phi):
    return np.array([np.cos(theta / 2) * np.exp(-1j * phi / 2), np.sin(theta / 2) * np.exp(1j * phi / 2)])


def _describe(exc):
    return f"{type(exc).__name__}: {exc}"


def _make(dev, encode, recover, theta, phi, error):
    @qml.qnode(dev)
    def circuit():
        qml.RY(theta, wires=0)
        qml.RZ(phi, wires=0)
        encode()
        if error != "none":
            qml.PauliX(wires=error)
        recover()
        return qml.density_matrix(wires=[0])

    return circuit


def check(ns, run_case):
    encode, recover = ns.get("encode"), ns.get("recover_compact")
    if not callable(encode):
        return {"passed": False, "key": "ch_no_encode"}
    if not callable(recover):
        return {"passed": False, "key": "ch_no_recover"}

    try:
        with qml.queuing.AnnotatedQueue() as queue:
            recover()
        wires = {w for op in queue.queue for w in op.wires.labels}
    except Exception as exc:  # noqa: BLE001 - the learner's code can fail in any way
        return {"passed": False, "key": "ch_error", "params": {"detail": _describe(exc)}}
    outside = sorted(w for w in wires if w not in (0, 1, 2))
    if outside:
        return {"passed": False, "key": "ch_ancilla", "params": {"wires": ", ".join(str(w) for w in outside)}}

    dev = qml.device("default.qubit", wires=3)
    worst = 1.0
    for theta, phi in _inputs():
        psi = _state(theta, phi)
        for error in ERRORS:
            circuit = _make(dev, encode, recover, theta, phi, error)

            try:
                rho = np.array(circuit())
            except Exception as exc:  # noqa: BLE001
                return {"passed": False, "key": "ch_error", "params": {"detail": _describe(exc)}}
            fidelity = float(np.real(psi.conj() @ rho @ psi))
            worst = min(worst, fidelity)
            if fidelity < TOLERANCE:
                key = "ch_idle" if error == "none" else "ch_fail"
                return {"passed": False, "key": key, "params": {"error": f"X on {error}", "fidelity": fidelity}}
    return {"passed": True, "key": "ch_ok", "params": {"worst": worst}}
