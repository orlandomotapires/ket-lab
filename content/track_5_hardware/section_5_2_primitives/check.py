"""Validation for lesson 5.2: Estimator and Sampler values for the Bell state,
and the statistical error 1/√shots."""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity


def bell():
    bell = QuantumCircuit(2)
    bell.h(0)
    bell.cx(0, 1)
    return Statevector(bell)


def number(ns, name):
    try:
        return float(np.real(ns[name]))
    except (KeyError, TypeError, ValueError):
        return None


def check(ns, run_case):
    qc = ns.get("qc")
    if not isinstance(qc, QuantumCircuit):
        return {"passed": False, "key": "no_circuit"}
    try:
        state = Statevector(qc.remove_final_measurements(inplace=False))
    except Exception:  # noqa: BLE001
        return {"passed": False, "key": "wrong_state", "params": {"fidelity": 0.0}}
    fidelity = float(state_fidelity(state, bell()))
    if qc.num_qubits != 2 or fidelity < 0.999:
        return {"passed": False, "key": "wrong_state", "params": {"fidelity": fidelity}}
    values = {name: number(ns, name) for name in ("zz_est", "xx_est", "zz_samp", "xx_samp", "z0_samp", "shots", "sigma")}
    for name, value in values.items():
        if value is None:
            return {"passed": False, "key": "missing", "params": {"name": name}}
    for name in ("zz_est", "xx_est"):
        if abs(values[name] - 1) > 1e-6:
            return {"passed": False, "key": "wrong_est", "params": {"name": name, "actual": values[name]}}
    shots = values["shots"]
    if not 1000 <= shots <= 100_000:
        return {"passed": False, "key": "bad_shots", "params": {"shots": shots}}
    if abs(values["sigma"] - 1 / np.sqrt(shots)) > 1e-6:
        return {"passed": False, "key": "wrong_sigma", "params": {"actual": values["sigma"], "want": 1 / np.sqrt(shots)}}
    for name in ("zz_samp", "xx_samp"):
        if abs(values[name] - 1) > 4 / np.sqrt(shots):
            return {"passed": False, "key": "wrong_samp", "params": {"name": name, "actual": values[name]}}
    if abs(values["z0_samp"]) > 4 / np.sqrt(shots):
        return {"passed": False, "key": "wrong_z0", "params": {"actual": values["z0_samp"], "limit": 4 / np.sqrt(shots)}}
    return {"passed": True, "key": "ok", "params": {"sigma": values["sigma"], "z0": values["z0_samp"]}, "fidelity": fidelity}
