"""Physics of lessons 2.5 (Simon) and 2.10 (Hamiltonian simulation), verified independently
of the reference solutions."""

import numpy as np
import pytest
from scipy.linalg import expm

from ket_lab_engine import simulator, tracer, validation

SECRETS = ["110", "101", "011", "111", "001", "100", "010"]


def run(library, lesson_id, case=None, code=None):
    bundle = library.validation_bundle(lesson_id)
    inputs = {"_KET_LAB_INPUT": case} if case is not None else None
    return tracer.execute(code or bundle["solution"], bundle["hidden_setup"], inputs)


def dot(a, b):
    return bin(a & b).count("1") % 2


@pytest.mark.parametrize("secret", SECRETS + ["000"])
def test_simon_outcomes_are_orthogonal_to_the_secret(library, secret):
    s = int(secret, 2)
    distribution = simulator.register_distribution(run(library, "2.5", secret).circuit, [0, 1, 2])
    allowed = [y for y in range(8) if dot(y, s) == 0]
    for y in range(8):
        expected = 1 / len(allowed) if y in allowed else 0.0
        assert distribution.get(format(y, "03b"), 0.0) == pytest.approx(expected, abs=1e-9)


@pytest.mark.parametrize("secret", SECRETS + ["000"])
def test_simon_postprocessing_recovers_the_secret(library, secret):
    execution = run(library, "2.5", secret)
    assert execution.namespace["s_found"] == secret


@pytest.mark.parametrize("secret", SECRETS)
def test_simon_oracle_is_two_to_one_with_period_s(library, secret):
    """The hidden oracle really implements f(x) = f(x ⊕ s) and no other collision."""
    from qiskit import QuantumCircuit

    s = int(secret, 2)
    outputs = {}
    for x in range(8):
        qc = QuantumCircuit(6)
        for bit in range(3):
            if (x >> bit) & 1:
                qc.x(bit)
        bundle = library.validation_bundle("2.5")
        namespace = tracer.execute(
            "from qiskit import QuantumCircuit\nqc = QuantumCircuit(6)\noracle(qc)\n", bundle["hidden_setup"], {"_KET_LAB_INPUT": secret}
        ).namespace
        qc.compose(namespace["qc"], inplace=True)
        state = simulator.run_trajectory(qc, seed=0).states[-1]
        index = int(np.argmax(np.abs(state)))
        assert (index & 7) == x
        outputs[x] = index >> 3
    for x in range(8):
        for y in range(8):
            assert (outputs[x] == outputs[y]) == (y in (x, x ^ s))


def test_simon_starter_and_wrong_secret_fail(library):
    bundle = library.validation_bundle("2.5")
    wrong = bundle["solution"].replace("s_found = solutions[0] if len(solutions) == 1 else \"000\"", "s_found = \"110\"")
    assert not validation.validate(wrong, bundle)["passed"]


J, H_FIELD, T = 1.0, 0.8, 2.0
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.diag([1.0, -1.0]).astype(complex)
_I = np.eye(2, dtype=complex)
HAMILTONIAN = J * np.kron(_Z, _Z) + H_FIELD * (np.kron(_X, _I) + np.kron(_I, _X))
EXACT = expm(-1j * HAMILTONIAN * T)[:, 0]


def trotter_state(n, order=1):
    dt = T / n
    zz = expm(-1j * J * np.kron(_Z, _Z) * dt)
    x = expm(-1j * H_FIELD * (np.kron(_X, _I) + np.kron(_I, _X)) * dt)
    if order == 1:
        step = x @ zz
    else:
        half = expm(-1j * H_FIELD * (np.kron(_X, _I) + np.kron(_I, _X)) * dt / 2)
        step = half @ zz @ half
    return np.linalg.matrix_power(step, n)[:, 0]


def infidelity(state):
    return 1 - abs(np.vdot(EXACT, state)) ** 2


def test_trotter_error_decreases_with_the_number_of_steps():
    errors = [infidelity(trotter_state(n)) for n in (1, 2, 4, 8, 16, 32)]
    assert all(a > b for a, b in zip(errors, errors[1:]))


def test_first_order_infidelity_scales_as_one_over_n_squared():
    ratio = infidelity(trotter_state(32)) / infidelity(trotter_state(64))
    assert ratio == pytest.approx(4.0, rel=0.15)


def test_second_order_beats_first_order():
    for n in (4, 8, 16):
        assert infidelity(trotter_state(n, 2)) < infidelity(trotter_state(n, 1))


def test_reference_solution_reaches_the_target_fidelity(library):
    state = simulator.run_trajectory(run(library, "2.10").circuit, seed=0).states[-1]
    assert abs(np.vdot(EXACT, state)) ** 2 >= 0.99


def test_circuit_matches_the_numpy_trotter_product(library):
    """The solution implements exactly the first-order Trotter product with n = 10."""
    state = simulator.run_trajectory(run(library, "2.10").circuit, seed=0).states[-1]
    assert abs(np.vdot(trotter_state(10), state)) ** 2 == pytest.approx(1.0, abs=1e-9)


def test_hamiltonian_threshold_is_between_1_and_10_steps(library):
    bundle = library.validation_bundle("2.10")
    passing = []
    for n in range(1, 13):
        code = bundle["solution"].replace("n_steps = 10", f"n_steps = {n}")
        passing.append(validation.validate(code, bundle)["passed"])
    assert not passing[0] and passing[9]
    assert passing == sorted(passing)  # once it passes, larger n also passes
