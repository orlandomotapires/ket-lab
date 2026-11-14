"""Verificações físicas independentes das lições 1.8, 1.9 e 1.10."""

import json
import math

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity

from qlp_engine import validation

from .conftest import CONTENT_DIR

TRACK = CONTENT_DIR / "track_1_fundamentals"


def read(folder, name):
    return (TRACK / folder / name).read_text(encoding="utf-8")


def run(code, setup, inputs=None):
    namespace = {"__name__": "__main__"}
    namespace.update(inputs or {})
    exec(compile(setup, "<setup>", "exec"), namespace)
    exec(compile(code, "<code>", "exec"), namespace)
    return namespace


# --- 1.8 ---------------------------------------------------------------


def copier(input_state_circuit):
    qc = QuantumCircuit(2)
    qc.compose(input_state_circuit, [0], inplace=True)
    qc.cx(0, 1)
    return Statevector(qc)


@pytest.mark.parametrize("label, prep", [("0", lambda c: None), ("1", lambda c: c.x(0))])
def test_cnot_copies_basis_states(label, prep):
    pre = QuantumCircuit(1)
    prep(pre)
    assert state_fidelity(copier(pre), Statevector.from_label(label * 2)) == pytest.approx(1.0)


def test_cnot_does_not_copy_plus():
    pre = QuantumCircuit(1)
    pre.h(0)
    out = copier(pre)
    assert state_fidelity(out, Statevector.from_label("++")) == pytest.approx(0.5)
    bell = Statevector(np.array([1, 0, 0, 1]) / math.sqrt(2))
    assert state_fidelity(out, bell) == pytest.approx(1.0)


def test_no_cloning_inner_product_argument():
    # Um copiador unitário preservaria ⟨ψ|φ⟩ = ⟨ψ|φ⟩², o que só vale para 0 ou 1.
    pre = QuantumCircuit(1)
    pre.h(0)
    overlap_inputs = abs(np.vdot(Statevector.from_label("0").data, Statevector.from_label("+").data))
    out_plus = copier(pre).data
    out_zero = copier(QuantumCircuit(1)).data
    overlap_outputs = abs(np.vdot(out_zero, out_plus))
    assert overlap_inputs == pytest.approx(1 / math.sqrt(2))
    assert overlap_outputs == pytest.approx(overlap_inputs)  # CNOT é unitário
    assert overlap_outputs != pytest.approx(overlap_inputs**2)  # a cópia ideal exigiria isto


def test_solution_1_8_copy_fidelity():
    ns = run(read("section_1_8_no_cloning", "solution.py"), read("section_1_8_no_cloning", "hidden_setup.py"))
    assert ns["copy_fidelity"] == pytest.approx(0.5, abs=1e-12)


# --- 1.9 ---------------------------------------------------------------


@pytest.mark.parametrize("message", ["00", "01", "10", "11"])
def test_superdense_decoding(message):
    ns = run(
        read("section_1_9_superdense_coding", "solution.py"),
        read("section_1_9_superdense_coding", "hidden_setup.py"),
        {"_QLP_INPUT": message},
    )
    state = Statevector(ns["qc"])
    probabilities = state.probabilities_dict()  # rótulo |q1 q0⟩
    assert probabilities.get(message, 0.0) == pytest.approx(1.0)


def test_superdense_bob_alone_sees_nothing():
    for message in ["00", "01", "10", "11"]:
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        if message[0] == "1":
            qc.z(1)
        if message[1] == "1":
            qc.x(1)
        # Antes do envio, a probabilidade de Bob (qubit 0) obter 1 é 1/2.
        assert Statevector(qc).probabilities([0])[1] == pytest.approx(0.5)


def test_superdense_cheating_is_rejected(library):
    cheat = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
if message[0] == "1":
    qc.x(1)
if message[1] == "1":
    qc.x(0)
qc.cx(0, 1)
qc.cx(1, 0)
"""
    bundle = library.validation_bundle("1.9")
    assert not validation.validate(cheat, bundle)["passed"]


# --- 1.10 --------------------------------------------------------------


def win_probability(alice, bob):
    total = 0.0
    for x in (0, 1):
        for y in (0, 1):
            qc = QuantumCircuit(2)
            qc.h(0)
            qc.cx(0, 1)
            qc.ry(alice[x], 0)
            qc.ry(bob[y], 1)
            p = Statevector(qc).probabilities()
            for a in (0, 1):
                for b in (0, 1):
                    if (a ^ b) == (x & y):
                        total += p[a + 2 * b] / 4
    return total


def test_chsh_quantum_value():
    pi = math.pi
    value = win_probability({0: 0.0, 1: pi / 2}, {0: pi / 4, 1: -pi / 4})
    assert value == pytest.approx(math.cos(pi / 8) ** 2, abs=1e-9)


def test_chsh_classical_strategies_win_at_most_three_quarters():
    best = 0.0
    for a0 in (0, 1):
        for a1 in (0, 1):
            for b0 in (0, 1):
                for b1 in (0, 1):
                    a, b = (a0, a1), (b0, b1)
                    wins = sum((a[x] ^ b[y]) == (x & y) for x in (0, 1) for y in (0, 1))
                    best = max(best, wins / 4)
    assert best == 0.75


def test_chsh_no_quantum_strategy_beats_tsirelson():
    rng = np.random.default_rng(3)
    bound = math.cos(math.pi / 8) ** 2
    for _ in range(200):
        angles = rng.uniform(0, 2 * math.pi, 4)
        value = win_probability({0: angles[0], 1: angles[1]}, {0: angles[2], 1: angles[3]})
        assert value <= bound + 1e-9


def test_chsh_solution_variable_matches():
    ns = run(read("section_1_10_chsh_game", "solution.py"), read("section_1_10_chsh_game", "hidden_setup.py"))
    assert ns["win_probability"] == pytest.approx(math.cos(math.pi / 8) ** 2, abs=1e-9)


def test_chsh_cheating_with_communication_is_rejected(library):
    cheat = """
from qiskit import QuantumCircuit
def play(x, y):
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    if x and y:
        qc.x(1)
    return qc
qc = play(1, 1)
win_probability = 1.0
"""
    bundle = library.validation_bundle("1.10")
    assert not validation.validate(cheat, bundle)["passed"]
