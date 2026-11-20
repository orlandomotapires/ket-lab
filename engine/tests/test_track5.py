"""Track 5: independent checks of the solutions (physics and numbers), without going through check.py."""

import numpy as np
import pytest
from qiskit import QuantumCircuit, transpile
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from qiskit.quantum_info import SparsePauliOp, Statevector, state_fidelity
from qiskit.transpiler import CouplingMap

from ket_lab_engine import tracer, worker



def namespace(lesson_id, library):
    bundle = library.validation_bundle(lesson_id)
    return tracer.execute(
        bundle["solution"], bundle["hidden_setup"], trace=bundle["framework"] == "qiskit",
        require_circuit=bundle["framework"] == "qiskit",
    ).namespace


def two_qubit_count(circuit):
    return sum(1 for inst in circuit.data if len(inst.qubits) == 2)


def test_5_1_solution_is_equivalent_and_within_budget(library):
    qc = namespace("5.1", library)["qc"]
    ghz = QuantumCircuit(4)
    ghz.h(0)
    for i in range(3):
        ghz.cx(0, i + 1)
    assert state_fidelity(Statevector(qc), Statevector(ghz)) > 0.999999
    assert two_qubit_count(qc) == 3
    assert {inst.operation.name for inst in qc.data} <= {"rz", "sx", "x", "cx"}
    edges = {(0, 1), (1, 2), (2, 3)}
    assert all(tuple(sorted(qc.find_bit(q).index for q in inst.qubits)) in edges for inst in qc.data if len(inst.qubits) == 2)


def test_5_1_star_circuit_needs_swaps():
    star = QuantumCircuit(4)
    star.h(0)
    for i in (1, 2, 3):
        star.cx(0, i)
    basis = ["rz", "sx", "x", "cx"]
    cost = {
        level: two_qubit_count(transpile(star, coupling_map=CouplingMap.from_line(4), basis_gates=basis,
                                         optimization_level=level, seed_transpiler=7))
        for level in (0, 1, 3)
    }
    assert min(cost.values()) > 3 and cost[1] == 6


def test_5_1_distance_two_cnot_costs_four():
    qc = QuantumCircuit(3)
    qc.cx(0, 2)
    out = transpile(qc, coupling_map=CouplingMap.from_line(3), basis_gates=["rz", "sx", "x", "cx"],
                    initial_layout=[0, 1, 2], optimization_level=1, seed_transpiler=1)
    assert out.count_ops()["cx"] == 4


def test_5_1_transpiled_circuit_runs_in_the_platform(library):
    bundle = library.validation_bundle("5.1")
    result = worker.handle({"type": "run", "code": bundle["solution"], "max_qubits": 5})
    assert result["ok"], result
    assert result["num_qubits"] == 4 and result["steps"]


def test_5_2_bell_values(library):
    ns = namespace("5.2", library)
    bell = QuantumCircuit(2)
    bell.h(0)
    bell.cx(0, 1)
    exact = StatevectorEstimator().run([(bell, [SparsePauliOp("ZZ"), SparsePauliOp("XX"), SparsePauliOp("YY"), SparsePauliOp("IZ")])]).result()[0].data.evs
    assert np.allclose(exact, [1, 1, -1, 0])
    assert ns["zz_est"] == pytest.approx(1) and ns["xx_est"] == pytest.approx(1)
    assert ns["zz_samp"] == pytest.approx(1) and ns["xx_samp"] == pytest.approx(1)
    assert abs(ns["z0_samp"]) < 4 / np.sqrt(ns["shots"])
    assert ns["sigma"] == pytest.approx(1 / np.sqrt(4096))


def test_5_2_statistical_error_scales_as_one_over_root_n():
    circuit = QuantumCircuit(1)
    circuit.h(0)
    circuit.measure_all()

    def spread(shots):
        values = []
        for seed in range(300):
            counts = StatevectorSampler(default_shots=shots, seed=seed).run([circuit]).result()[0].data.meas.get_counts()
            values.append((counts.get("0", 0) - counts.get("1", 0)) / shots)
        return np.std(values)

    assert spread(400) / spread(1600) == pytest.approx(2, rel=0.2)
    assert spread(400) == pytest.approx(1 / np.sqrt(400), rel=0.15)


def test_5_2_x_from_z_basis_counts_is_wrong():
    # Measuring a Bell state only in the Z basis gives ⟨XX⟩ ≈ 0 from the parity, not 1.
    bell = QuantumCircuit(2)
    bell.h(0)
    bell.cx(0, 1)
    probs = Statevector(bell).probabilities_dict()
    assert abs(sum(p * (-1) ** (k.count("1")) for k, p in probs.items()) - 1) < 1e-12  # ZZ is right
    # Hadamards before the measurement rotate X to Z.
    rotated = bell.copy()
    rotated.h([0, 1])
    probs = Statevector(rotated).probabilities_dict()
    assert sum(p * (-1) ** (k.count("1")) for k, p in probs.items()) == pytest.approx(1)


def test_5_3_decay_formulas(library):
    ns = namespace("5.3", library)
    T1, T2, t = ns["T1"], ns["T2"], ns["t_wait"]
    assert ns["p1"] == pytest.approx(0.5 * np.exp(-t / T1))
    assert ns["coherence"] == pytest.approx(0.5 * np.exp(-t / T2))
    assert ns["coherence"] <= 0.5  # |ρ01| never grows
    # Independent density matrix: amplitude damping then pure dephasing.
    gamma = 1 - np.exp(-t / T1)
    lam = 1 - np.exp(-2 * t * (1 / T2 - 1 / (2 * T1)))
    k0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]])
    k1 = np.array([[0, np.sqrt(gamma)], [0, 0]])
    rho = np.full((2, 2), 0.5)
    rho = k0 @ rho @ k0.T + k1 @ rho @ k1.T
    rho[0, 1] *= np.sqrt(1 - lam)
    rho[1, 0] *= np.sqrt(1 - lam)
    assert abs(rho[1, 1] - ns["p1"]) < 1e-12 and abs(rho[0, 1] - ns["coherence"]) < 1e-12


def test_5_3_t2_equal_to_two_t1_is_pure_amplitude_damping():
    T1, T2, t = 50.0, 100.0, 30.0
    assert 1 / T2 - 1 / (2 * T1) == 0
    assert np.exp(-t / T2) == pytest.approx(np.sqrt(np.exp(-t / T1)))


def test_5_4_readout_mitigation_improves_the_estimate(library):
    ns = namespace("5.4", library)
    raw = ns["p_meas"][0] - ns["p_meas"][1]
    assert abs(raw - 0.6) > 0.03
    assert ns["z_readout"] == pytest.approx(0.6)
    assert np.allclose(np.linalg.inv(ns["A"]) @ ns["p_meas"], [0.8, 0.2])


def test_5_4_zne_improves_the_estimate(library):
    ns = namespace("5.4", library)
    ideal = np.cos(0.9)
    raw = ns["values"][0]
    assert ns["values"][0] > ns["values"][1] > ns["values"][2]  # more folding, more noise
    assert abs(ns["zne"] - ideal) < abs(raw - ideal) / 5
    quadratic = np.polyval(np.polyfit([1, 3, 5], ns["values"], 2), 0)
    assert abs(quadratic - ideal) < abs(raw - ideal) / 3


def test_5_4_folding_keeps_the_ideal_circuit(library):
    # G G† G equals G, so the same circuit without noise has the same ⟨Z⟩ at any scale.
    c = np.cos(0.45)
    s = np.sin(0.45)
    g = np.array([[c, -s], [s, c]])
    state = np.array([1, 0])
    folded = g @ g.T @ g @ state
    assert np.allclose(folded, g @ state)


def test_5_4_variance_of_extrapolation_exceeds_data_variance():
    x = np.array([1.0, 3.0, 5.0])
    design = np.vander(x, 2)
    weights = np.linalg.pinv(design)[1]  # intercept weights of the line fit
    assert np.sqrt(np.sum(weights**2)) == pytest.approx(np.sqrt(1 / 3 + 9 / 8))
    lagrange = np.linalg.inv(np.vander(x, 3))[2]
    assert np.sqrt(np.sum(lagrange**2)) > 2.2
