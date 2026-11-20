"""Challenge for lesson 4.1: amplitude damping as a Kraus channel.

Kraus operators are not unique, so the learner's operators are judged by what they do: the
completeness relation, and the output for several input states against the reference channel.
The state of the learner's QNode is rebuilt from its gates, not read from what it returns.
"""

import numpy as np

from ket_lab_engine import pl, simulator

GAMMAS = [0.0, 0.1, 0.36, 0.7, 1.0]
GAMMA = 0.36
INPUTS = [
    np.array([[1, 0], [0, 0]], dtype=complex),
    np.array([[0, 0], [0, 1]], dtype=complex),
    np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex),
    np.array([[0.5, -0.5j], [0.5j, 0.5]], dtype=complex),
    np.eye(2, dtype=complex) / 2,
]
PAULI = (np.array([[0, 1], [1, 0]], dtype=complex), np.array([[0, -1j], [1j, 0]]), np.diag([1, -1]).astype(complex))


def reference(rho, gamma):
    k0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
    k1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)
    return k0 @ rho @ k0.conj().T + k1 @ rho @ k1.conj().T


def bloch(rho):
    return [float(np.real(np.trace(rho @ p))) for p in PAULI]


def fail(key, **params):
    return {"passed": False, "key": key, "params": params}


def check(ns, run_case):
    kraus, damped = ns.get("damping_kraus"), ns.get("damped")
    if not callable(kraus):
        return fail("ch_missing_function", name="damping_kraus")
    for gamma in GAMMAS:
        try:
            ops = [np.array(k, dtype=complex) for k in kraus(gamma)]
            total = sum(k.conj().T @ k for k in ops)
        except Exception:
            return fail("ch_kraus_format", gamma=gamma)
        if total.shape != (2, 2):
            return fail("ch_kraus_format", gamma=gamma)
        if not np.allclose(total, np.eye(2), atol=1e-9):
            return fail("ch_not_complete", gamma=gamma, diag=f"{float(np.real(total[0, 0])):.3f}, {float(np.real(total[1, 1])):.3f}")
        for rho in INPUTS:
            out = sum(k @ rho @ k.conj().T for k in ops)
            if not np.allclose(out, reference(rho, gamma), atol=1e-8):
                got, want = float(np.real(out[0, 0])), float(np.real(reference(rho, gamma)[0, 0]))
                return fail("ch_wrong_channel", gamma=gamma, got=got, want=want)

    if damped is None or not pl.is_qnode(damped):
        return fail("ch_no_qnode")
    plus = np.full((2, 2), 0.5, dtype=complex)
    for gamma in GAMMAS:
        ops, lines, n = pl.trace_qnode(damped, [gamma])
        if n != 1:
            return fail("ch_qnode_qubits", count=n)
        state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
        if state.ndim == 1:
            state = np.outer(state, state.conj())
        if not np.allclose(state, reference(plus, gamma), atol=1e-8):
            return fail("ch_qnode_wrong", gamma=gamma, got=float(np.real(state[1, 1])), want=float(np.real(reference(plus, gamma)[1, 1])))

    rho = reference(plus, GAMMA)
    want_bloch = bloch(rho)
    want = {
        "purity_plus": float(np.real(np.trace(rho @ rho))),
        "z_from_mixed": bloch(reference(INPUTS[-1], GAMMA))[2],
    }
    for name in ("bloch_plus", "purity_plus", "z_from_mixed"):
        if name not in ns:
            return fail("ch_missing", name=name)
    try:
        got_bloch = [float(np.real(v)) for v in ns["bloch_plus"]]
        if len(got_bloch) != 3:
            raise ValueError
    except (TypeError, ValueError):
        return fail("ch_missing", name="bloch_plus")
    if not np.allclose(got_bloch, want_bloch, atol=1e-6):
        return fail("ch_wrong_value", name="bloch_plus", actual=", ".join(f"{v:.3f}" for v in got_bloch))
    for name, value in want.items():
        try:
            actual = float(np.real(ns[name]))
        except (TypeError, ValueError):
            return fail("ch_missing", name=name)
        if abs(actual - value) > 1e-6:
            return fail("ch_wrong_value", name=name, actual=actual)
    return {"passed": True, "key": "ch_ok", "params": {"x": want_bloch[0], "z": want_bloch[2], "purity": want["purity_plus"]}}
