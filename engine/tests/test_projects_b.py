"""End-of-track projects 4.8 and 5.5: calculations independent of the rubric."""

import itertools
import time

import numpy as np
import pytest

from qlp_engine import pl, simulator, validation

from .conftest import CONTENT_DIR

SHOR = CONTENT_DIR / "track_4_noise_qec" / "section_4_8_shor_code_noise_project"
MITIGATION = CONTENT_DIR / "track_5_hardware" / "section_5_5_mitigated_estimate_project"


# ---------- 4.8: independent reference (9-qubit density matrix, without the per-block rule) ----------

PAULI = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]]), "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.diag([1, -1])}


def circuit_logical_pauli(library, pattern):
    """Logical Pauli measured in the solution's circuit: applies the pattern, decodes and compares
    <X>, <Y>, <Z> of qubit 0 with those of the input state."""
    bundle = library.validation_bundle("4.8")
    errors = "".join(f"{c.lower()}{q}" for q, c in enumerate(pattern) if c != "I") or "none"
    bloch_in = []
    bloch_out = []
    for theta, phi in [(1.1, 0.7)]:
        ns = validation.tracer.execute(
            bundle["solution"], bundle.get("hidden_setup"), {"_QLP_INPUT": {"input": [theta, phi], "error": errors}},
            trace=False, require_circuit=False,
        ).full_namespace()
        ops, lines, n = pl.trace_qnode(ns["circuit"], [])
        state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
        if state.ndim == 2:
            axes = "abcdefghi"[: n - 1]
            rho = np.einsum(f"{axes}x{axes}y->xy", state.reshape((2,) * (2 * n)))
        else:
            matrix = state.reshape(-1, 2)
            rho = matrix.T @ matrix.conj()
        bloch_out = [np.real(np.trace(rho @ PAULI[k])) for k in "XYZ"]
        bloch_in = [np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)]
    signs = tuple(int(round(o / i)) for o, i in zip(bloch_out, bloch_in))
    return {(1, 1, 1): "I", (1, -1, -1): "X", (-1, -1, 1): "Z", (-1, 1, -1): "Y"}[signs]


def enumerate_failure(p):
    """p_L by enumerating the 4^9 patterns, with the logical Pauli coming from the per-block rule
    written here in vectorized form."""
    letters = np.array(list(itertools.product(range(4), repeat=9)), dtype=np.int8)  # 0 I, 1 X, 2 Y, 3 Z
    x = (letters == 1) | (letters == 2)
    z = (letters == 2) | (letters == 3)
    blocks = [slice(0, 3), slice(3, 6), slice(6, 9)]
    vote_fail = np.stack([x[:, b].sum(axis=1) >= 2 for b in blocks], axis=1)
    z_odd = np.stack([z[:, b].sum(axis=1) % 2 == 1 for b in blocks], axis=1)
    fails = (vote_fail.sum(axis=1) % 2 == 1) | (z_odd.sum(axis=1) >= 2)
    weight = (letters != 0).sum(axis=1)
    probability = (1 - p) ** (9 - weight) * (p / 3) ** weight
    return float(probability[fails].sum())


@pytest.fixture(scope="module")
def shor_bundle(library):
    return library.validation_bundle("4.8")


def run_solution(bundle, extra=""):
    return validation.validate(bundle["solution"] + extra, bundle)


def test_model_agrees_with_the_decoder_circuit(library):
    rng = np.random.default_rng(3)
    patterns = [list("XXIIIIIII"), list("ZIIZIIIII"), list("XIIZIIIII"), list("YYIIIIIII"), list("ZZIIIIIII"), list("IIIIIIZZZ")]
    for _ in range(8):
        pattern = ["I"] * 9
        for q in rng.choice(9, size=int(rng.integers(1, 4)), replace=False):
            pattern[int(q)] = "XYZ"[int(rng.integers(3))]
        patterns.append(pattern)
    code = library.validation_bundle("4.8")["solution"]
    for pattern in patterns:
        assert circuit_logical_pauli(library, pattern) == solution_logical_pauli(code, pattern), pattern


def solution_logical_pauli(code, pattern):
    scope = {"prepare_input": lambda: None, "inject_error": lambda: None}
    # run only the solution's pure definitions (without running the device)
    header = code.split("@qml.qnode")[0]
    tail = code.split("def block_effect", 1)[1].split("def logical_failure", 1)[0]
    exec(header + "def block_effect" + tail, scope)
    return scope["logical_pauli"](pattern)


@pytest.mark.parametrize("p", [0.005, 0.05, 0.1, 0.3])
def test_logical_failure_matches_enumeration(shor_bundle, p):
    ns = {"prepare_input": lambda: None, "inject_error": lambda: None}
    code = shor_bundle["solution"]
    exec(code.split("@qml.qnode")[0] + "def block_effect" + code.split("def block_effect", 1)[1].split("def bare_failure", 1)[0], ns)
    assert ns["logical_failure"](p) == pytest.approx(enumerate_failure(p), abs=1e-12)


def test_small_p_scales_as_p_squared_and_beats_bare_qubit():
    p = 1e-3
    assert enumerate_failure(p) < p
    assert enumerate_failure(p / 10) / enumerate_failure(p) == pytest.approx(0.01, rel=0.05)


def test_crossover_from_enumeration(shor_bundle):
    low, high = 0.02, 0.2
    for _ in range(40):
        mid = (low + high) / 2
        low, high = (mid, high) if enumerate_failure(mid) < mid else (low, mid)
    p_star = (low + high) / 2
    assert 0.05 < p_star < 0.09
    from qlp_engine import tracer

    ns = tracer.execute(shor_bundle["solution"], shor_bundle.get("hidden_setup"), None, trace=False, require_circuit=False).full_namespace()
    assert ns["p_star"] == pytest.approx(p_star, abs=1e-6)


def test_shor_project_runtime(shor_bundle):
    start = time.time()
    assert run_solution(shor_bundle)["passed"]
    assert time.time() - start < 15


@pytest.mark.parametrize(
    "mutation,key",
    [
        ("\ndef bare_failure(p):\n    return 0.5 * p\n", "below"),
        ("\np_star = 0.2\n", "crossover"),
        ("\n_orig = logical_failure\n\ndef logical_failure(p):\n    return _orig(p) * 1.01\n", "values"),
        ("\n_o = logical_pauli\n\ndef logical_pauli(e):\n    return 'I' if e.count('I') == 7 else _o(e)\n", "model"),
    ],
)
def test_shor_rubric_criteria_are_independent(shor_bundle, mutation, key):
    result = run_solution(shor_bundle, mutation)
    assert not result["passed"]
    assert result["code"] == key


def test_shor_broken_decoder_is_caught(shor_bundle):
    broken = shor_bundle["solution"].replace("qml.Toffoli(wires=[3, 6, 0])", "pass")
    result = validation.validate(broken, shor_bundle)
    assert not result["passed"] and result["code"] == "decoder"


# ---------- 5.5 ----------


@pytest.fixture(scope="module")
def mit_bundle(library):
    return library.validation_bundle("5.5")


def device_namespace(bundle):
    from qlp_engine import tracer

    return tracer.execute("", bundle["hidden_setup"], None, trace=False, require_circuit=False).full_namespace()


SIGN = np.array([(-1) ** (int(format(i, "03b")[0]) + int(format(i, "03b")[2])) for i in range(8)])


def exact_zz(ns, gates, noisy=True):
    return float(SIGN @ ns["_probabilities"](gates, noisy=noisy))


def test_noisy_device_is_consistent_with_a_density_matrix_simulation(mit_bundle):
    """Independent reimplementation: depolarizing as Pauli Kraus operators (15 Paulis) + readout."""
    ns = device_namespace(mit_bundle)
    h = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    eye, x = np.eye(2), np.array([[0, 1], [1, 0]])
    paulis = [eye, x, np.array([[0, -1j], [1j, 0]]), np.diag([1, -1])]

    def on(op, q):
        mats = [eye, eye, eye]
        mats[q] = op
        return np.kron(np.kron(mats[0], mats[1]), mats[2])

    def cx(c, t):
        proj0, proj1 = np.diag([1, 0]), np.diag([0, 1])
        a = [eye, eye, eye]
        b = [eye, eye, eye]
        a[c] = proj0
        b[c], b[t] = proj1, x
        return np.kron(np.kron(a[0], a[1]), a[2]) + np.kron(np.kron(b[0], b[1]), b[2])

    def depol(rho, qubits, p):
        n = len(qubits)
        total = np.zeros_like(rho)
        for combo in itertools.product(range(4), repeat=n):
            op = np.eye(8)
            for q, c in zip(qubits, combo):
                op = op @ on(paulis[c], q)
            total += op @ rho @ op.conj().T
        return (1 - p) * rho + p * total / 4**n

    ghz = [("h", 0), ("cx", 0, 1), ("cx", 1, 2)]
    for scale in (1, 3):
        gates = ghz + (ghz[::-1] + ghz) * ((scale - 1) // 2)
        rho = np.zeros((8, 8), dtype=complex)
        rho[0, 0] = 1
        for g in gates:
            u = on(h, g[1]) if g[0] == "h" else cx(g[1], g[2])
            rho = u @ rho @ u.conj().T
            rho = depol(rho, (g[1],) if g[0] == "h" else (g[1], g[2]), 0.01 if g[0] == "h" else 0.03)
        probs = np.kron(np.kron(ns["_READ"], ns["_READ"]), ns["_READ"]) @ np.real(np.diag(rho))
        assert exact_zz(ns, gates) == pytest.approx(float(SIGN @ probs), abs=1e-9)


def test_mitigation_improves_the_estimate_by_the_claimed_factor(mit_bundle):
    ns = device_namespace(mit_bundle)
    ghz = [("h", 0), ("cx", 0, 1), ("cx", 1, 2)]
    a_inv = np.linalg.inv(np.kron(np.kron(ns["_READ"], ns["_READ"]), ns["_READ"]))
    fold = lambda s: ghz + (ghz[::-1] + ghz) * ((s - 1) // 2)  # noqa: E731
    raw = exact_zz(ns, ghz)
    values = [float(SIGN @ (a_inv @ ns["_probabilities"](fold(s)))) for s in (1, 3, 5)]
    zne = np.polyval(np.polyfit([1, 3, 5], values, 1), 0)
    assert abs(1 - raw) > 0.15
    assert abs(1 - zne) < abs(1 - raw) / 10  # the rubric only requires 1/5
    assert abs(1 - values[0]) > abs(1 - zne)  # readout alone is not enough


def test_mitigation_project_runtime(mit_bundle):
    start = time.time()
    assert validation.validate(mit_bundle["solution"], mit_bundle)["passed"]
    assert time.time() - start < 15


@pytest.mark.parametrize(
    "mutation,key",
    [
        ("\nraw = 1.0\n", "raw"),
        ("\nmitigated = raw\n", "mitigated"),
        ("\nsigma = sigma * 10\n", "sigma"),
        ("\nsigma = 0.0001\n", "sigma"),
        ("\nA = A.T\n", "readout"),
        ("\ndef fold(gates, scale):\n    return list(gates) * scale\n", "folding"),
        ("\nghz = [('h', 0), ('cx', 0, 1)]\n", "circuit"),
        ("\nghz = [('h', 0), ('cx', 0, 2)]\n", "circuit"),
    ],
)
def test_mitigation_rubric_criteria_are_independent(mit_bundle, mutation, key):
    result = validation.validate(mit_bundle["solution"] + mutation, mit_bundle)
    assert not result["passed"]
    assert result["code"] == key
