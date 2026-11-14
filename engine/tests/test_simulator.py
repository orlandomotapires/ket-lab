import numpy as np
import pytest
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit.random import random_circuit
from qiskit.quantum_info import Statevector

from qlp_engine import geometry, simulator


@pytest.mark.parametrize("seed", range(8))
def test_matches_qiskit_statevector_on_random_circuits(seed):
    circuit = random_circuit(4, depth=6, max_operands=3, seed=seed)
    ours = simulator.run_trajectory(circuit).states[-1]
    reference = Statevector.from_instruction(circuit).data
    assert np.allclose(ours, reference, atol=1e-9)


def test_little_endian_ordering():
    circuit = QuantumCircuit(2)
    circuit.x(0)
    state = simulator.run_trajectory(circuit).states[-1]
    # |q1 q0> = |01> -> índice 1
    assert np.allclose(np.abs(state) ** 2, [0, 1, 0, 0])


def test_one_snapshot_per_instruction():
    circuit = QuantumCircuit(1)
    circuit.h(0)
    circuit.z(0)
    trajectory = simulator.run_trajectory(circuit, lines=[3, 4])
    assert len(trajectory.states) == 3
    assert [step.line for step in trajectory.steps] == [3, 4]


def test_bloch_vectors_of_basic_states():
    circuit = QuantumCircuit(3)
    circuit.x(0)  # |1>  -> -z
    circuit.h(1)  # |+>  -> +x
    circuit.h(2)
    circuit.s(2)  # |+i> -> +y
    vectors, purities = geometry.bloch_vectors(simulator.run_trajectory(circuit).states[-1], 3)
    assert np.allclose(vectors, [[0, 0, -1], [1, 0, 0], [0, 1, 0]], atol=1e-6)
    assert np.allclose(purities, 1.0)


def test_bell_state_collapses_local_bloch_vectors():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    vectors, purities = geometry.bloch_vectors(simulator.run_trajectory(circuit).states[-1], 2)
    assert np.allclose(vectors, 0.0, atol=1e-6)
    assert np.allclose(purities, 0.5, atol=1e-6)


def test_measurement_collapses_and_is_reproducible():
    circuit = QuantumCircuit(1, 1)
    circuit.h(0)
    circuit.measure(0, 0)
    outcomes = set()
    for seed in range(20):
        first = simulator.run_trajectory(circuit, seed=seed)
        again = simulator.run_trajectory(circuit, seed=seed)
        assert first.clbits == again.clbits
        bit = first.clbits[0]
        assert np.isclose(abs(first.states[-1][bit]), 1.0)
        outcomes.add(bit)
    assert outcomes == {0, 1}


def _teleport(theta: float, phi: float) -> QuantumCircuit:
    q, c = QuantumRegister(3), ClassicalRegister(2)
    circuit = QuantumCircuit(q, c)
    circuit.ry(theta, 0)
    circuit.rz(phi, 0)
    circuit.h(1)
    circuit.cx(1, 2)
    circuit.cx(0, 1)
    circuit.h(0)
    circuit.measure(0, 0)
    circuit.measure(1, 1)
    with circuit.if_test((c[1], 1)):
        circuit.x(2)
    with circuit.if_test((c[0], 1)):
        circuit.z(2)
    return circuit


@pytest.mark.parametrize("seed", range(6))
def test_teleportation_with_classical_control(seed):
    theta, phi = 0.7 + seed * 0.3, 1.1 - seed * 0.2
    alice = QuantumCircuit(1)
    alice.ry(theta, 0)
    alice.rz(phi, 0)
    expected, _ = geometry.bloch_vectors(simulator.run_trajectory(alice).states[-1], 1)

    trajectory = simulator.run_trajectory(_teleport(theta, phi), seed=seed)
    vectors, purities = geometry.bloch_vectors(trajectory.states[-1], 3)
    assert np.allclose(vectors[2], expected[0], atol=1e-6)
    assert np.isclose(purities[2], 1.0, atol=1e-6)


def test_register_condition_and_else_branch():
    q, c = QuantumRegister(2), ClassicalRegister(2)
    circuit = QuantumCircuit(q, c)
    circuit.x(0)
    circuit.measure(0, 0)
    with circuit.if_test((c, 3)) as otherwise:
        circuit.x(1)
    with otherwise:
        circuit.h(1)
    trajectory = simulator.run_trajectory(circuit)
    vectors, _ = geometry.bloch_vectors(trajectory.states[-1], 2)
    assert trajectory.steps[-1].applied is False
    assert np.allclose(vectors[1], [1, 0, 0], atol=1e-6)


def test_reset_and_initialize():
    circuit = QuantumCircuit(1)
    circuit.x(0)
    circuit.reset(0)
    assert np.isclose(abs(simulator.run_trajectory(circuit).states[-1][0]), 1.0)

    target = np.array([1, 1j]) / np.sqrt(2)
    circuit = QuantumCircuit(1)
    circuit.initialize(target, 0)
    assert np.isclose(abs(np.vdot(target, simulator.run_trajectory(circuit).states[-1])), 1.0)


def test_counts_without_measure_sample_all_qubits():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    result = simulator.sample_counts(circuit, shots=2000, seed=7)
    assert result["measured"] == "qubits"
    assert set(result["counts"]) == {"00", "11"}
    assert abs(result["counts"]["00"] - 1000) < 150


def test_counts_with_terminal_measures_use_clbit_order():
    circuit = QuantumCircuit(2, 2)
    circuit.x(0)
    circuit.measure(0, 1)  # qubit 0 -> bit clássico 1
    circuit.measure(1, 0)
    assert simulator.sample_counts(circuit, shots=50)["counts"] == {"10": 50}


def test_counts_with_mid_circuit_measurement():
    result = simulator.sample_counts(_teleport(0.0, 0.0), shots=400, seed=3)
    assert sum(result["counts"].values()) == 400
    assert set(result["counts"]) == {"00", "01", "10", "11"}


def test_qubit_cap():
    with pytest.raises(simulator.SimulationError, match="limit"):
        simulator.run_trajectory(QuantumCircuit(11))
    with pytest.raises(simulator.SimulationError):
        simulator.run_trajectory(QuantumCircuit(4), max_qubits=3)


def test_angle_formatting():
    assert geometry.format_angle(np.pi / 2) == "π/2"
    assert geometry.format_angle(-3 * np.pi / 4) == "-3π/4"
    assert geometry.format_angle(np.pi) == "π"
    assert geometry.format_angle(0.3) == "0.300"


def test_exact_distribution():
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    assert simulator.exact_distribution(circuit) == pytest.approx({"00": 0.5, "11": 0.5})
    assert simulator.exact_distribution(QuantumCircuit(1)) is None  # sem medição
    assert simulator.exact_distribution(_teleport(0.3, 0.1)) is None  # medição no meio
