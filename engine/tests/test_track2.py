"""Física da Trilha 2, verificada de forma independente das soluções de referência."""

import numpy as np
import pytest

from qlp_engine import geometry, simulator, tracer


def run(library, lesson_id, case=None, code=None):
    bundle = library.validation_bundle(lesson_id)
    inputs = {"_QLP_INPUT": case} if case is not None else None
    return tracer.execute(code or bundle["solution"], bundle["hidden_setup"], inputs)


@pytest.mark.parametrize("table", [[0, 0], [1, 1], [0, 1], [1, 0]])
def test_deutsch_reads_f0_xor_f1(library, table):
    distribution = simulator.register_distribution(run(library, "2.2", table).circuit, [0])
    assert distribution.get("1", 0.0) == pytest.approx(float(table[0] ^ table[1]), abs=1e-9)


def test_deutsch_without_interference_gives_a_coin_flip(library):
    code = "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\noracle(qc)\n"
    for table in ([0, 0], [0, 1], [1, 0], [1, 1]):
        distribution = simulator.register_distribution(run(library, "2.2", table, code).circuit, [0])
        assert distribution == pytest.approx({"0": 0.5, "1": 0.5})


@pytest.mark.parametrize(
    "case, constant",
    [
        ({"kind": "constant", "value": 0}, True),
        ({"kind": "constant", "value": 1}, True),
        ({"kind": "balanced", "mask": [1, 0, 1], "flip": 0}, False),
        ({"kind": "balanced", "mask": [0, 1, 1], "flip": 1}, False),
        ({"kind": "and"}, False),
        ({"kind": "majority"}, False),
        ({"kind": "last"}, False),
    ],
)
def test_deutsch_jozsa_separates_constant_from_balanced(library, case, constant):
    distribution = simulator.register_distribution(run(library, "2.3", case).circuit, [0, 1, 2])
    assert distribution.get("000", 0.0) == pytest.approx(1.0 if constant else 0.0, abs=1e-9)


@pytest.mark.parametrize(
    "case, secret",
    [
        ("1011", "1011"),
        ("0110", "0110"),
        ("0001", "0001"),
        ("1111", "1111"),
        ("0000", "0000"),
        ("1000", "1000"),
        ({"s": "0110", "b": 1}, "0110"),
        ({"s": "1011", "b": 1}, "1011"),
    ],
)
def test_bernstein_vazirani_recovers_the_secret(library, case, secret):
    distribution = simulator.register_distribution(run(library, "2.4", case).circuit, [0, 1, 2, 3])
    assert distribution == pytest.approx({secret: 1.0})


@pytest.mark.parametrize(
    "marked, iterations, success",
    [
        (["1011"], 3, 0.9613),
        (["0110"], 3, 0.9613),
        (["0000"], 3, 0.9613),
        (["0001", "1110"], 2, 0.9453),
        (["0011", "0101", "1010", "1111"], 1, 1.0),
    ],
)
def test_grover_amplifies_the_marked_items(library, marked, iterations, success):
    execution = run(library, "2.5", marked)
    assert execution.namespace["num_marked"] == len(marked)
    assert execution.namespace["iterations"] == iterations
    distribution = simulator.register_distribution(execution.circuit, [0, 1, 2, 3])
    assert sum(distribution.get(item, 0.0) for item in marked) == pytest.approx(success, abs=1e-3)


@pytest.mark.parametrize("x", range(8))
def test_qft_solution_is_the_discrete_fourier_transform(library, x):
    state = simulator.run_trajectory(run(library, "2.6", x).circuit).states[-1]
    expected = np.exp(2j * np.pi * x * np.arange(8) / 8) / np.sqrt(8)
    assert abs(np.vdot(expected, state)) ** 2 == pytest.approx(1.0)


@pytest.mark.parametrize("theta", [0.125, 0.375, 0.625, 0.875])
def test_phase_estimation_reads_theta(library, theta):
    execution = run(library, "2.7", theta)
    distribution = simulator.register_distribution(execution.circuit, [0, 1, 2])
    assert distribution == pytest.approx({format(round(theta * 8), "03b"): 1.0})
    assert execution.namespace["theta"] == pytest.approx(theta)


def test_phase_estimation_of_a_superposition_gives_zero_or_theta(library):
    code = library.validation_bundle("2.7")["solution"].replace("qc.x(3)", "qc.h(3)")
    distribution = simulator.register_distribution(run(library, "2.7", 0.625, code).circuit, [0, 1, 2])
    assert distribution == pytest.approx({"000": 0.5, "101": 0.5})


def test_modular_multiplication_is_multiplication_by_seven(library):
    hidden = library.validation_bundle("2.8")["hidden_setup"]
    for y in range(1, 15):
        prepare = "".join(f"qc.x({4 + bit})\n" for bit in range(4) if (y >> bit) & 1)
        code = (
            "from qiskit import QuantumCircuit\nqc = QuantumCircuit(8)\nqc.x(0)\n"
            + prepare
            + "apply_controlled_mod_mult(qc, 0, 1)\n"
        )
        circuit = tracer.execute(code, hidden).circuit
        work = simulator.register_distribution(circuit, [4, 5, 6, 7])
        assert work == pytest.approx({format(7 * y % 15, "04b"): 1.0}), y


def test_shor_finds_the_period_peaks_and_the_factors(library):
    execution = run(library, "2.8")
    distribution = simulator.register_distribution(execution.circuit, [0, 1, 2, 3])
    assert distribution == pytest.approx({"0000": 0.25, "0100": 0.25, "1000": 0.25, "1100": 0.25})
    assert execution.namespace["factors"] == [3, 5]


def test_hidden_gates_have_readable_labels(library):
    labels = lambda lesson_id: [  # noqa: E731
        geometry.describe_step(i, record)["label"]
        for i, record in enumerate(simulator.run_trajectory(run(library, lesson_id).circuit).steps)
    ]
    assert "U_f" in labels("2.3")
    assert "U_ω" in labels("2.5")
    assert {"U^1", "U^4", "QFT†"} <= set(labels("2.7"))
    assert "×7^8" in labels("2.8")


def test_run_shots_is_available_to_student_code():
    code = (
        "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1, 1)\nqc.x(0)\nqc.measure(0, 0)\n"
        "counts = run_shots(qc, 50)\n"
    )
    assert tracer.execute(code).namespace["counts"] == {"1": 50}
