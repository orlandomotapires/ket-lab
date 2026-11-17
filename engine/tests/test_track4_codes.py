"""Lessons 4.3 (phase-flip) and 4.4 (Shor): the codes, computed by hand with numpy
(own convention: qubit i is the i-th factor of the Kronecker product), and the
reference solutions run by the engine with errors beyond those the validator uses."""

import itertools
import json

import numpy as np
import pytest

from qlp_engine import pl, simulator, tracer

from .conftest import CONTENT_DIR

I2 = np.eye(2)
PAULI = {
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]]),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}
H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)


def op(n, gates):
    """Kronecker product with `gates` = {qubit: 2x2 matrix} and identity on the rest."""
    result = np.array([[1.0 + 0j]])
    for q in range(n):
        result = np.kron(result, gates.get(q, I2))
    return result


def kron_all(vectors):
    out = np.array([1.0 + 0j])
    for v in vectors:
        out = np.kron(out, v)
    return out


def random_qubit(rng):
    v = rng.normal(size=2) + 1j * rng.normal(size=2)
    return v / np.linalg.norm(v)


def pauli_string(n, label):
    """label: {qubit: 'X'|'Y'|'Z'}"""
    return op(n, {q: PAULI[p] for q, p in label.items()})


_TABLES = {}


def correction_table(n, stabilizers, kinds):
    """Syndrome -> correction Pauli, built from the single-qubit errors in `kinds`."""
    key = (n, len(stabilizers), kinds)
    if key not in _TABLES:
        def signs(e):
            return tuple(0 if np.allclose(s @ e, e @ s) else 1 for s in stabilizers)

        table = {tuple([0] * len(stabilizers)): np.eye(2**n)}
        for q in range(n):
            for p in kinds:
                e = pauli_string(n, {q: p})
                table.setdefault(signs(e), e)
        _TABLES[key] = table
    return _TABLES[key]


def recovery_fidelity(n, stabilizers, logical, error, amplitudes, kinds="XYZ"):
    """Fidelity after measuring the syndrome (projecting) and applying the code's correction:
    sum, over the syndromes, of |⟨ψ_L| R_s P_s E |ψ_L⟩|²."""
    alpha, beta = amplitudes
    psi_l = alpha * logical[0] + beta * logical[1]
    damaged = error @ psi_l
    total = 0.0
    for syndrome, recovery in correction_table(n, stabilizers, kinds).items():
        branch = damaged
        for s, bit in zip(stabilizers, syndrome):
            branch = (branch + (-1) ** bit * (s @ branch)) / 2
        total += abs(np.vdot(psi_l, recovery @ branch)) ** 2
    return total


# --------------------------------------------------------------------------- #
# Codes in numpy
# --------------------------------------------------------------------------- #

PLUS = np.array([1, 1]) / np.sqrt(2)
MINUS = np.array([1, -1]) / np.sqrt(2)
PHASE_FLIP = {
    "n": 3,
    "stabilizers": [pauli_string(3, {0: "X", 1: "X"}), pauli_string(3, {1: "X", 2: "X"})],
    "logical": [kron_all([PLUS] * 3), kron_all([MINUS] * 3)],
}
BLOCK_0 = np.array([1, 0, 0, 0, 0, 0, 0, 1]) / np.sqrt(2)
BLOCK_1 = np.array([1, 0, 0, 0, 0, 0, 0, -1]) / np.sqrt(2)
SHOR_STABILIZERS = []
for b in range(3):
    SHOR_STABILIZERS += [pauli_string(9, {3 * b: "Z", 3 * b + 1: "Z"}), pauli_string(9, {3 * b + 1: "Z", 3 * b + 2: "Z"})]
SHOR_STABILIZERS += [
    pauli_string(9, {q: "X" for q in range(0, 6)}),
    pauli_string(9, {q: "X" for q in range(3, 9)}),
]
SHOR = {
    "n": 9,
    "stabilizers": SHOR_STABILIZERS,
    "logical": [kron_all([BLOCK_0] * 3), kron_all([BLOCK_1] * 3)],
}


def test_phase_flip_code_corrects_every_single_z():
    rng = np.random.default_rng(1)
    for _ in range(5):
        state = random_qubit(rng)
        for q in range(3):
            f = recovery_fidelity(3, PHASE_FLIP["stabilizers"], PHASE_FLIP["logical"], pauli_string(3, {q: "Z"}), state, "Z")
            assert f == pytest.approx(1.0)


def test_phase_flip_code_fails_for_x_and_for_two_z():
    state = np.array([1, 1j]) / np.sqrt(2)
    for error in (pauli_string(3, {0: "X"}), pauli_string(3, {0: "Z", 1: "Z"})):
        f = recovery_fidelity(3, PHASE_FLIP["stabilizers"], PHASE_FLIP["logical"], error, state, "Z")
        assert f < 0.5 + 1e-9
    # X is a logical Z: |0⟩ + |1⟩ becomes |0⟩ − |1⟩ and the fidelity is 0
    plus_state = np.array([1, 1]) / np.sqrt(2)
    f = recovery_fidelity(3, PHASE_FLIP["stabilizers"], PHASE_FLIP["logical"], pauli_string(3, {0: "X"}), plus_state, "Z")
    assert f == pytest.approx(0.0)


def test_shor_code_corrects_every_single_qubit_pauli_and_arbitrary_unitary():
    rng = np.random.default_rng(2)
    for _ in range(2):
        state = random_qubit(rng)
        for q in range(9):
            for p in "XYZ":
                f = recovery_fidelity(9, SHOR["stabilizers"], SHOR["logical"], pauli_string(9, {q: p}), state)
                assert f == pytest.approx(1.0), (q, p)
            a = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
            unitary, _ = np.linalg.qr(a)
            f = recovery_fidelity(9, SHOR["stabilizers"], SHOR["logical"], op(9, {q: unitary}), state)
            assert f == pytest.approx(1.0), q


def test_shor_code_two_qubit_errors():
    state = np.array([0.6, 0.8j])
    args = (9, SHOR["stabilizers"], SHOR["logical"])
    # two X in the same block: X⊗X⊗X is left in the block, a logical Z (fidelity |⟨ψ|Z|ψ⟩|² = 0.0784)
    assert recovery_fidelity(*args, pauli_string(9, {0: "X", 1: "X"}), state) == pytest.approx(0.0784)
    # two Z in different blocks: logical X, fails on |0⟩
    assert recovery_fidelity(*args, pauli_string(9, {0: "Z", 3: "Z"}), np.array([1, 0])) == pytest.approx(0.0)


# --------------------------------------------------------------------------- #
# Reference solutions in the engine
# --------------------------------------------------------------------------- #


def _lesson_files(folder):
    path = CONTENT_DIR / "track_4_noise_qec" / folder
    return (path / "solution.py").read_text(encoding="utf-8"), (path / "hidden_setup.py").read_text(encoding="utf-8")


def _final_state(folder, theta, phi, error):
    code, hidden = _lesson_files(folder)
    ns = tracer.execute(code, hidden, {"_QLP_INPUT": {"input": [theta, phi], "error": error}}, trace=False, require_circuit=False).namespace
    ops, lines, n = pl.trace_qnode(ns["circuit"], [])
    state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    return state if state.ndim == 2 else np.outer(state, state.conj()), n


def _psi(theta, phi):
    return np.array([np.cos(theta / 2) * np.exp(-1j * phi / 2), np.sin(theta / 2) * np.exp(1j * phi / 2)])


def _phase_flip_fidelity(theta, phi, error):
    rho, n = _final_state("section_4_3_phase_flip_code", theta, phi, error)
    # High bits = high-index qubits (Qiskit): data qubits 0, 1 and 2 are the 3 least significant bits.
    tensor = rho.reshape(4, 8, 4, 8)
    data = np.einsum("axay->xy", tensor)
    a, b = _psi(theta, phi)
    # In plain numpy: |+++⟩ and |−−−⟩ are symmetric under qubit exchange, so the order does not matter.
    target = a * kron_all([PLUS] * 3) + b * kron_all([MINUS] * 3)
    return float(np.real(target.conj() @ data @ target))


@pytest.mark.parametrize("error", ["none", "z0", "z1", "z2"])
def test_phase_flip_solution_recovers(error):
    for theta, phi in [(0.4, 0.2), (2.0, 2.5)]:
        assert _phase_flip_fidelity(theta, phi, error) == pytest.approx(1.0)


def test_phase_flip_solution_does_not_correct_x_or_two_z():
    # X is a logical Z (with |+⟩ the fidelity is 0); two Z are a logical X (with |0⟩ the fidelity is 0)
    assert _phase_flip_fidelity(np.pi / 2, 0.0, "x0") == pytest.approx(0.0, abs=1e-9)
    assert _phase_flip_fidelity(0.0, 0.0, "z0z1") == pytest.approx(0.0, abs=1e-9)


def _shor_fidelity(theta, phi, error):
    rho, n = _final_state("section_4_4_shor_code", theta, phi, error)
    assert n == 9
    tensor = rho.reshape(2**8, 2, 2**8, 2)
    qubit0 = np.einsum("axay->xy", tensor)
    psi = _psi(theta, phi)
    return float(np.real(psi.conj() @ qubit0 @ psi))


@pytest.mark.parametrize("error", ["none", "x4", "y4", "z4", "u4", "x0z3", "z8", "y0"])
def test_shor_solution_recovers(error):
    assert _shor_fidelity(1.1, 0.7, error) == pytest.approx(1.0)


def test_shor_solution_all_single_pauli_errors():
    for kind, q in itertools.product("xyzu", range(9)):
        assert _shor_fidelity(2.2, -0.4, f"{kind}{q}") == pytest.approx(1.0), (kind, q)


def test_shor_solution_fails_for_two_flips_in_one_block():
    # Logical Z: with |+⟩ the fidelity is 0
    assert _shor_fidelity(np.pi / 2, 0.0, "x0x1") == pytest.approx(0.0, abs=1e-9)


def test_shor_solution_fails_for_two_phase_flips_in_different_blocks():
    assert _shor_fidelity(0.0, 0.0, "z0z3") == pytest.approx(0.0, abs=1e-9)


def test_prediction_answers_match_the_physics():
    for folder, expected in [("section_4_3_phase_flip_code", 2), ("section_4_4_shor_code", 2)]:
        manifest = json.loads((CONTENT_DIR / "track_4_noise_qec" / folder / "manifest.json").read_text())
        assert manifest["prediction_answer"] == expected
