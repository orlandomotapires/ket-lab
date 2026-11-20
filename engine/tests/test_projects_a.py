"""End-of-track projects 1.11, 2.11 and 3.9: checks independent of the validators."""

import numpy as np
import pennylane as qml
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector, partial_trace

from ket_lab_engine import validation

from .conftest import CONTENT_DIR


def bundle(library, lesson_id):
    return library.validation_bundle(lesson_id)


def run(library, lesson_id, code):
    b = bundle(library, lesson_id)
    return validation.validate(code, b)


# --------------------------------------------------------------------------- #
# 1.11 entanglement swapping
# --------------------------------------------------------------------------- #


def test_swapping_solution_gives_phi_plus_for_every_branch():
    """Independent of the engine: for each outcome (m1, m2), post-selects and corrects by hand."""
    phi = Statevector([1, 0, 0, 1]) / np.sqrt(2)
    for m1 in (0, 1):
        for m2 in (0, 1):
            qc = QuantumCircuit(4)
            qc.h(0), qc.cx(0, 1), qc.h(2), qc.cx(2, 3)
            qc.cx(1, 2), qc.h(1)
            state = Statevector(qc)
            # project qubits 1 and 2 onto the outcome (m1, m2)
            data = state.data.reshape(2, 2, 2, 2)  # eixos: q3, q2, q1, q0
            projected = np.zeros_like(data)
            projected[:, m2, m1, :] = data[:, m2, m1, :]
            projected = Statevector(projected.reshape(-1) / np.linalg.norm(projected))
            corrected = QuantumCircuit(4)
            if m2:
                corrected.x(3)
            if m1:
                corrected.z(3)
            projected = projected.evolve(corrected)
            rho = partial_trace(projected, [1, 2])
            assert float(np.real(phi.data.conj() @ rho.data @ phi.data)) == pytest.approx(1.0, abs=1e-9)


def test_swapping_validator_accepts_solution(library):
    result = run(library, "1.11", bundle(library, "1.11")["solution"])
    assert result["passed"], result


def test_swapping_validator_rubric(library):
    solution = bundle(library, "1.11")["solution"]

    no_z = solution.replace("with qc.if_test((qc.clbits[0], 1)):\n    qc.z(3)\n", "")
    assert run(library, "1.11", no_z)["code"] == "branch_partial"

    direct = solution.replace("qc.cx(1, 2)\nqc.h(1)", "qc.cx(0, 3)\nqc.cx(1, 2)\nqc.h(1)")
    assert run(library, "1.11", direct)["code"] == "forbidden_pair"

    measure_end = solution.replace("qc.measure(2, 1)", "qc.measure(2, 1)\nqc.measure(3, 1)")
    assert run(library, "1.11", measure_end)["code"] == "measured_end"

    assert run(library, "1.11", solution.replace("c_after = float", "c_after = 0.0 * float"))["code"] == "after_wrong"
    assert run(library, "1.11", solution.replace("c_before = float", "c_before = 1.0 + float"))["code"] == "before_wrong"
    assert run(library, "1.11", solution + "\nc_after = None")["code"] == "no_record"


# --------------------------------------------------------------------------- #
# 2.11 Grover oracle
# --------------------------------------------------------------------------- #

FORMULA_SOLUTIONS = {"010", "101"}


def formula(a, b, c):
    return (a or b) and ((not a) or c) and ((not b) or (not c))


def test_formula_has_exactly_the_two_solutions():
    found = {f"{c}{b}{a}" for a in (0, 1) for b in (0, 1) for c in (0, 1) if formula(a, b, c)}
    assert found == FORMULA_SOLUTIONS


def solution_oracle(library):
    namespace = {}
    code = bundle(library, "2.11")["solution"]
    exec(code.split("N = 8")[0], namespace)  # only the oracle and diffuser definitions
    return namespace["oracle"]


def test_grover_oracle_marks_exactly_the_solutions(library):
    qc = QuantumCircuit(5)
    solution_oracle(library)(qc)
    unitary = Operator(qc).data
    for x in range(8):
        label = format(x, "03b")
        expected = -1 if label in FORMULA_SOLUTIONS else 1
        column = unitary[:, x]  # ancillas in |00⟩
        assert column[x] == pytest.approx(expected)
        assert np.allclose(np.delete(column, x), 0)


def test_grover_success_probability_by_iterations(library):
    namespace = {}
    exec(bundle(library, "2.11")["solution"].split("N = 8")[0], namespace)
    oracle, diffuser = namespace["oracle"], namespace["diffuser"]
    for k, expected in [(1, 1.0), (2, 0.25)]:
        qc = QuantumCircuit(5)
        qc.h([0, 1, 2])
        for _ in range(k):
            oracle(qc), diffuser(qc)
        p = Statevector(qc).probabilities([0, 1, 2])
        assert sum(p[int(s, 2)] for s in FORMULA_SOLUTIONS) == pytest.approx(expected, abs=1e-9)


def test_grover_validator_accepts_solution_and_rubric(library):
    solution = bundle(library, "2.11")["solution"]
    assert run(library, "2.11", solution)["passed"]

    assert run(library, "2.11", solution.replace('("010", "101")', '("010",)'))["code"] == "oracle_missing"
    assert run(library, "2.11", solution.replace('("010", "101")', '("010", "101", "111")'))["code"] == "oracle_extra"
    assert run(library, "2.11", solution.replace("iterations = floor", "iterations = 2 + 0 * floor"))["code"] == "iterations"
    leaky = solution.replace("def oracle(qc):", "def oracle(qc):\n    qc.cx(0, 3)")
    assert run(library, "2.11", leaky)["code"] == "oracle_not_clean"
    assert run(library, "2.11", solution.replace('["010"', '["000"') + "\nsolutions = ['010']")["code"] == "solutions"


# --------------------------------------------------------------------------- #
# 3.9 dissociation curve
# --------------------------------------------------------------------------- #


def exact_energy(d):
    mol = qml.qchem.Molecule(
        ["H", "H"], np.array([[0.0, 0.0, 0.0], [0.0, 0.0, d / 0.529177210903]]), basis_name="sto-3g"
    )
    h = qml.qchem.molecular_hamiltonian(mol, method="dhf")[0]
    return float(np.linalg.eigvalsh(qml.matrix(h, wire_order=range(4)))[0])


def test_validator_energy_matches_the_pennylane_circuit():
    """The validator's state cos|1100⟩ − sin|0011⟩ is the one from DoubleExcitation."""
    from importlib.util import module_from_spec, spec_from_file_location

    path = CONTENT_DIR / "track_3_variational" / "section_3_9_dissociation_project" / "check.py"
    spec = spec_from_file_location("check35", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    d = 1.2
    mol = qml.qchem.Molecule(["H", "H"], np.array([[0, 0, 0], [0, 0, d / 0.529177210903]]), basis_name="sto-3g")
    h = qml.qchem.molecular_hamiltonian(mol, method="dhf")[0]
    dev = qml.device("default.qubit", wires=4)

    @qml.qnode(dev)
    def circuit(theta):
        qml.BasisState(np.array([1, 1, 0, 0]), wires=range(4))
        qml.DoubleExcitation(theta, wires=range(4))
        return qml.expval(h)

    matrix = module.exact_hamiltonian(d)
    for theta in (0.0, 0.3, -0.7, 1.9):
        assert module.ansatz_energy(matrix, theta) == pytest.approx(float(circuit(theta)), abs=1e-9)


def test_dissociation_solution_energies_against_exact_diagonalization(library):
    from ket_lab_engine import tracer

    b = bundle(library, "3.9")
    ns = tracer.execute(b["solution"], b.get("hidden_setup"), trace=False, require_circuit=False).namespace
    assert len(ns["distances"]) >= 5
    for d, e in zip(ns["distances"], ns["energies"]):
        exact = exact_energy(d)
        assert e >= exact - 1e-9  # variacional
        assert e - exact <= 1.6e-3
    assert abs(ns["r_eq"] - 0.734) < 0.05
    assert all(len(h) - 1 <= 40 for h in ns["histories"])
    # the curve has an interior minimum near 0.74 Å and rises toward 2.0 Å
    energies = dict(zip(ns["distances"], ns["energies"]))
    assert min(energies, key=energies.get) in (0.7, 0.8)
    assert energies[2.0] > energies[1.0] > energies[0.7]


def test_dissociation_validator_rubric(library):
    solution = bundle(library, "3.9")["solution"]
    assert run(library, "3.9", solution)["passed"]

    short = solution.replace("steps = 40", "steps = 8")
    assert run(library, "3.9", short)["code"] == "accuracy"

    over = solution.replace("steps = 40", "steps = 60")
    assert run(library, "3.9", over)["code"] == "budget"

    few = solution.replace("distances = [0.5, 0.6, 0.7, 0.8, 1.0, 1.5, 2.0]", "distances = [0.5, 0.7, 1.0, 2.0]")
    assert run(library, "3.9", few)["code"] == "distances"

    cheat = solution.replace("energies = [history[-1] for history in histories]", "energies = [e - 0.01 for e in [h[-1] for h in histories]]")
    assert run(library, "3.9", cheat)["code"] in ("below_exact", "inconsistent")

    wrong_r = solution + "\nr_eq = 1.2"
    assert run(library, "3.9", wrong_r)["code"] == "r_eq_wrong"
