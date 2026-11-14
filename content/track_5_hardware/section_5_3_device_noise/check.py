"""Validação da lição 5.3: o QNode `idle(T1, T2, t_wait)` deve reproduzir a matriz densidade
de um qubit em |+⟩ após t_wait: ρ11 = e^(-t/T1)/2 e |ρ01| = e^(-t/T2)/2. O estado é
reconstruído das portas e canais do aluno."""

import numpy as np

from qlp_engine import pl, simulator

CASES = [(100.0, 80.0, 50.0), (100.0, 200.0, 30.0), (50.0, 30.0, 100.0)]  # (T1, T2, t) em µs


def reference(T1, T2, t):
    p1 = 0.5 * np.exp(-t / T1)
    coherence = 0.5 * np.exp(-t / T2)
    return np.array([[1 - p1, coherence], [coherence, p1]], dtype=complex)


def student_rho(circuit, T1, T2, t):
    ops, lines, n = pl.trace_qnode(circuit, [T1, T2, t])
    state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    if state.ndim == 1:
        state = np.outer(state, state.conj())
    return state, n


def check(ns, run_case):
    circuit = ns.get("idle")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "no_circuit"}
    for T1, T2, t in CASES:
        rho, n = student_rho(circuit, T1, T2, t)
        if n != 1:
            return {"passed": False, "key": "wrong_qubits", "params": {"count": n}}
        expected = reference(T1, T2, t)
        if np.max(np.abs(rho - expected)) > 1e-6:
            if abs(np.real(np.trace(rho @ rho)) - 1) < 1e-9:
                return {"passed": False, "key": "no_noise"}
            got_p1, want_p1 = float(np.real(rho[1, 1])), float(np.real(expected[1, 1]))
            got_c, want_c = float(abs(rho[0, 1])), float(abs(expected[0, 1]))
            key = "wrong_population" if abs(got_p1 - want_p1) > 1e-6 else "wrong_coherence"
            return {"passed": False, "key": key, "params": {"T1": T1, "T2": T2, "t": t, "got_p1": got_p1, "want_p1": want_p1, "got_c": got_c, "want_c": want_c}}
    try:
        T1, T2, t = (float(ns[name]) for name in ("T1", "T2", "t_wait"))
    except (KeyError, TypeError, ValueError):
        return {"passed": False, "key": "missing", "params": {"name": "T1, T2 and t_wait"}}
    if T1 <= 0 or t < 0 or T2 <= 0 or T2 > 2 * T1:
        return {"passed": False, "key": "unphysical", "params": {"T1": T1, "T2": T2}}
    expected = reference(T1, T2, t)
    values = {"p1": float(np.real(expected[1, 1])), "coherence": float(abs(expected[0, 1]))}
    for name, value in values.items():
        if name not in ns:
            return {"passed": False, "key": "missing", "params": {"name": name}}
        try:
            actual = float(np.real(ns[name]))
        except (TypeError, ValueError):
            return {"passed": False, "key": "missing", "params": {"name": name}}
        if abs(actual - value) > 1e-6:
            return {"passed": False, "key": "wrong_value", "params": {"name": name, "actual": actual}}
    return {"passed": True, "key": "ok", "params": {"p1": values["p1"], "coherence": values["coherence"]}}
