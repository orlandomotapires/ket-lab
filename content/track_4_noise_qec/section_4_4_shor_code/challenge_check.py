"""Challenge for lesson 4.4: which pairs of errors break the Shor code.

The learner writes `survives(errors)`, with `errors` a list of (qubit, "X" or "Z") pairs, and stores
the failing pairs in `bad_xx`, `bad_zz` and `bad_xz`. The check has its own state-vector simulation of
the nine-qubit code and a failure means that one of four input states (|0>, |1>, |+>, |+i>) does not
come back: a logical X leaves |+> alone and a logical Z leaves |0> alone, so one state is not enough.
It calls `survives` on a few patterns of its own and compares the three lists with the simulation.
The check runs the learner's code only through `survives`: 11 calls of its own, on top of the
144 simulations of the learner's scan. Its own simulation is plain NumPy.
"""

import itertools

import numpy as np

BLOCKS = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
PAULI = {"X": np.array([[0, 1], [1, 0]], dtype=complex), "Z": np.diag([1, -1]).astype(complex)}
HADAMARD = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
STATES = [
    np.array([1, 0], dtype=complex),
    np.array([0, 1], dtype=complex),
    np.array([1, 1], dtype=complex) / np.sqrt(2),
    np.array([1, 1j], dtype=complex) / np.sqrt(2),
]
PATTERNS = [
    [],
    [(4, "X")],
    [(5, "Z")],
    [(2, "X"), (1, "X")],
    [(0, "Z"), (8, "Z")],
    [(4, "Z"), (5, "Z")],
    [(1, "X"), (7, "X")],
    [(3, "X"), (8, "Z")],
    [(5, "Z"), (0, "X")],
    [(6, "Z"), (2, "Z")],
    [(7, "X"), (6, "X")],
]
TOLERANCE = 0.999
N = 9


def _gate(tensor, matrix, q):
    return np.moveaxis(np.tensordot(matrix, tensor, axes=([1], [q])), 0, q)


def _cnot(tensor, control, target):
    index = [slice(None)] * N
    index[control] = 1
    tensor[tuple(index)] = np.flip(tensor[tuple(index)], axis=target if target < control else target - 1)


def _toffoli(tensor, c1, c2, target):
    index = [slice(None)] * N
    index[c1] = index[c2] = 1
    axis = target - (target > c1) - (target > c2)
    tensor[tuple(index)] = np.flip(tensor[tuple(index)], axis=axis)


def _survives(errors):
    """True when every test state comes back after the Shor encoding, the errors and the decoding."""
    for psi in STATES:
        t = np.zeros((2,) * N, dtype=complex)
        t[(0,) * N] = psi[0]
        t[(1,) + (0,) * (N - 1)] = psi[1]
        _cnot(t, 0, 3)
        _cnot(t, 0, 6)
        for leader in (0, 3, 6):
            t = _gate(t, HADAMARD, leader)
        for a, b, c in BLOCKS:
            _cnot(t, a, b)
            _cnot(t, a, c)
        for qubit, kind in errors:
            t = _gate(t, PAULI[kind], qubit)
        for a, b, c in BLOCKS:
            _cnot(t, a, b)
            _cnot(t, a, c)
            _toffoli(t, b, c, a)
        for leader in (0, 3, 6):
            t = _gate(t, HADAMARD, leader)
        _cnot(t, 0, 3)
        _cnot(t, 0, 6)
        _toffoli(t, 3, 6, 0)
        m = t.reshape(2, -1)
        if float(np.real(psi.conj() @ (m @ m.conj().T) @ psi)) < TOLERANCE:
            return False
    return True


def _truth():
    pairs = list(itertools.combinations(range(N), 2))
    xx = {p for p in pairs if not _survives([(p[0], "X"), (p[1], "X")])}
    zz = {p for p in pairs if not _survives([(p[0], "Z"), (p[1], "Z")])}
    xz = {(i, j) for i in range(N) for j in range(N) if i != j and not _survives([(i, "X"), (j, "Z")])}
    return {"bad_xx": xx, "bad_zz": zz, "bad_xz": xz}


def _normalize(name, value):
    """The learner's list as a set of pairs, or None when it is malformed."""
    try:
        pairs = [tuple(int(v) for v in pair) for pair in value]
    except (TypeError, ValueError):
        return None
    if any(len(p) != 2 or p[0] == p[1] or not all(0 <= v < N for v in p) for p in pairs):
        return None
    if name != "bad_xz":
        pairs = [tuple(sorted(p)) for p in pairs]
    return set(pairs)


def _describe(exc):
    return f"{type(exc).__name__}: {exc}"


def check(ns, run_case):
    survives = ns.get("survives")
    if not callable(survives):
        return {"passed": False, "key": "ch_no_survives"}

    for errors in PATTERNS:
        try:
            got = bool(survives(list(errors)))
        except Exception as exc:  # noqa: BLE001 - the learner's code can fail in any way
            return {"passed": False, "key": "ch_survives_error", "params": {"detail": _describe(exc)}}
        want = _survives(errors)
        if got != want:
            key = "ch_says_survives" if got else "ch_says_fails"
            return {"passed": False, "key": key, "params": {"errors": str(list(errors))}}

    truth = _truth()
    for name in ("bad_xx", "bad_zz", "bad_xz"):
        if name not in ns:
            return {"passed": False, "key": "ch_missing", "params": {"name": name}}
        pairs = _normalize(name, ns[name])
        if pairs is None:
            return {"passed": False, "key": "ch_bad_format", "params": {"name": name}}
        extra, missing = sorted(pairs - truth[name]), sorted(truth[name] - pairs)
        if extra:
            return {"passed": False, "key": "ch_listed", "params": {"name": name, "pair": str(extra[0])}}
        if missing:
            return {"passed": False, "key": "ch_unlisted", "params": {"name": name, "pair": str(missing[0])}}
    return {
        "passed": True,
        "key": "ch_ok",
        "params": {"xx": len(truth["bad_xx"]), "zz": len(truth["bad_zz"]), "xz": N * (N - 1)},
    }
