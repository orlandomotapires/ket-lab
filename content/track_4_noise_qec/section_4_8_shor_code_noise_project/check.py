"""Validation for project 4.8 (Shor code under noise): rubric with five criteria.

1. decoder: qubit 0 returns to |ψ⟩ after X, Y or Z on any of the nine qubits;
2. logical_pauli agrees with the reference on many error patterns;
3. logical_failure(p) agrees with the exact enumeration of the 4^9 patterns;
4. logical_failure(p) < bare_failure(p) for small p;
5. p_star close to the exact crossover.
The reference computes the logical Pauli by classical propagation of the X and Z bits and counts the
patterns that fail by weight, which gives p_L(p) = soma_w N_w (p/3)^w (1-p)^(9-w).
"""

import itertools

import numpy as np

from qlp_engine import pl, simulator

INPUTS = [(1.1, 0.7), (2.4, -1.3)]
TOLERANCE = 0.999
P_VALUES = [0.005, 0.02, 0.05, 0.1, 0.3]
P_SMALL = [0.001, 0.01, 0.03, 0.05]
VALUE_TOLERANCE = 1e-6
CROSSOVER_TOLERANCE = 0.003
BLOCKS = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
LETTERS = "IXYZ"


def reference_pauli(error):
    """Logical Pauli for an error pattern (list of nine letters)."""
    x = [c in "XY" for c in error]
    z = [c in "YZ" for c in error]
    leader_x, leader_z = [], []
    for block in BLOCKS:
        leader_x.append(sum(x[q] for q in block) >= 2)  # inner vote fails: X on the leader
        leader_z.append(sum(z[q] for q in block) % 2 == 1)  # Z on any qubit reaches the leader
    logical_z = sum(leader_x) % 2 == 1  # X on a leader (+/− basis) is a logical Z
    logical_x = sum(leader_z) >= 2  # the vote among leaders fails
    return {
        (False, False): "I", (True, False): "X", (False, True): "Z", (True, True): "Y"}[(logical_x, logical_z)]


def failing_counts():
    """N_w: how many of the 4^9 patterns of weight w leave a logical Pauli different from I."""
    counts = [0] * 10
    for pattern in itertools.product(LETTERS, repeat=9):
        if reference_pauli(pattern) != "I":
            counts[sum(c != "I" for c in pattern)] += 1
    return counts


_COUNTS = []


def reference_failure(p):
    if not _COUNTS:
        _COUNTS.extend(failing_counts())
    return sum(n * (p / 3) ** w * (1 - p) ** (9 - w) for w, n in enumerate(_COUNTS))


def reference_crossover():
    low, high = 0.02, 0.2
    for _ in range(60):
        mid = (low + high) / 2
        if reference_failure(mid) < mid:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def qubit0_state(state, n):
    if state.ndim == 2:
        tensor = state.reshape((2,) * (2 * n))
        axes = "abcdefghi"[: n - 1]
        return np.einsum(f"{axes}x{axes}y->xy", tensor)
    matrix = state.reshape(-1, 2)
    return matrix.T @ matrix.conj()


def fidelity(run_case, theta, phi, error):
    ns = run_case({"input": [theta, phi], "error": error})
    ops, lines, n = pl.trace_qnode(ns.get("circuit"), [])
    state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    psi = np.array([np.cos(theta / 2) * np.exp(-1j * phi / 2), np.sin(theta / 2) * np.exp(1j * phi / 2)])
    return float(np.real(psi.conj() @ qubit0_state(state, n) @ psi))


def number(value):
    try:
        return float(np.real(value))
    except (TypeError, ValueError):
        return None


def patterns():
    rng = np.random.default_rng(7)
    fixed = ["XXIIIIIII", "ZIIZIIIII", "XIIZIIIII", "YYIIIIIII", "ZZIIIIIII", "XIIXIIIII", "IIIIIIZZZ", "ZIIZIIZII", "IIXIIXIIX"]
    found = [list(f) for f in fixed]
    for _ in range(40):
        weight = int(rng.integers(1, 5))
        pattern = ["I"] * 9
        for q in rng.choice(9, size=weight, replace=False):
            pattern[int(q)] = "XYZ"[int(rng.integers(3))]
        found.append(pattern)
    return found


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "no_circuit"}
    _, _, n = pl.trace_qnode(circuit, [])
    if n != 9:
        return {"passed": False, "key": "wrong_qubits", "params": {"count": n}}
    for theta, phi in INPUTS:
        for error in ["none"] + [f"{kind}{q}" for kind in "xyz" for q in range(9)]:
            f = fidelity(run_case, theta, phi, error)
            if f < TOLERANCE:
                return {"passed": False, "key": "decoder", "params": {"error": error.upper(), "fidelity": f}}
    for name in ("logical_pauli", "logical_failure", "bare_failure"):
        if not callable(ns.get(name)):
            return {"passed": False, "key": "missing", "params": {"name": name}}
    for pattern in patterns():
        try:
            actual = ns["logical_pauli"](list(pattern))
        except Exception:  # noqa: BLE001
            actual = None
        expected = reference_pauli(pattern)
        if actual != expected:
            return {"passed": False, "key": "model", "params": {"pattern": "".join(pattern), "actual": actual, "expected": expected}}
    for p in P_VALUES:
        actual, expected = number(ns["logical_failure"](p)), reference_failure(p)
        if actual is None or abs(actual - expected) > VALUE_TOLERANCE:
            return {"passed": False, "key": "values", "params": {"p": p, "actual": actual, "expected": expected}}
    for p in P_SMALL:
        actual, bare = number(ns["logical_failure"](p)), number(ns["bare_failure"](p))
        if bare is None or actual is None or not actual < bare:
            return {"passed": False, "key": "below", "params": {"p": p, "actual": actual, "bare": bare}}
    expected = reference_crossover()
    actual = number(ns.get("p_star"))
    if actual is None or abs(actual - expected) > CROSSOVER_TOLERANCE:
        return {"passed": False, "key": "crossover", "params": {"actual": actual, "expected": expected}}
    return {"passed": True, "key": "ok", "params": {"p_star": actual, "reference": expected}}
