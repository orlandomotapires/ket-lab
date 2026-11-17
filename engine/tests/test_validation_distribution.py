"""counts_distribution with measurements in the middle: exact branches, or a tolerance sized by sampling."""

import pytest

from qlp_engine import simulator, validation

# Teleport-like circuit: mid-circuit measurements and a classical correction.
SOLUTION = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(3, 3)
qc.ry(0.9, 0)
qc.h(1)
qc.cx(1, 2)
qc.cx(0, 1)
qc.h(0)
qc.measure(0, 0)
qc.measure(1, 1)
with qc.if_test((qc.clbits[1], 1)):
    qc.x(2)
qc.measure(2, 2)
"""
# The same circuit with independent gates written in another order.
REORDERED = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(3, 3)
qc.h(1)
qc.ry(0.9, 0)
qc.cx(1, 2)
qc.cx(0, 1)
qc.h(0)
qc.measure(1, 1)
qc.measure(0, 0)
with qc.if_test((qc.clbits[1], 1)):
    qc.x(2)
qc.measure(2, 2)
"""
WRONG = SOLUTION.replace("qc.ry(0.9, 0)", "qc.ry(2.2, 0)")


def lesson(**rules):
    return {"id": "t", "validation": {"type": "counts_distribution", **rules}, "solution": SOLUTION, "max_qubits": 4}


def test_branching_distribution_matches_sampling():
    from qlp_engine import tracer

    circuit = tracer.execute(SOLUTION).circuit
    exact = simulator.branching_distribution(circuit)
    assert exact is not None and abs(sum(exact.values()) - 1) < 1e-9
    sampled = simulator.sample_counts(circuit, 8192, seed=1)
    observed = {k: v / 8192 for k, v in sampled["counts"].items()}
    assert validation.total_variation(exact, observed) < 0.05


def test_reordered_gates_pass_exactly_and_a_wrong_angle_fails():
    assert validation.validate(REORDERED, lesson(tolerance=0.001))["passed"]
    assert not validation.validate(WRONG, lesson())["passed"]


def test_sampled_path_is_sized_by_outcomes_and_shots(monkeypatch):
    monkeypatch.setattr(simulator, "MAX_BRANCHES", 0)  # too many branches: fall back to sampling
    strict = lesson(tolerance=0.001, shots=512)
    result = validation.validate(REORDERED, strict)
    assert result["passed"], result  # a manifest value of 0.1% would fail on noise alone; the sized one does not
    assert not validation.validate(WRONG, lesson(tolerance=0.001, shots=512))["passed"]


def test_sampling_tolerance_never_below_the_manifest_value():
    assert validation.sampling_tolerance(8, 4096) == pytest.approx(3 * (8 / 4096) ** 0.5)
    assert validation.sampling_tolerance(1, 10**9) < 0.001
