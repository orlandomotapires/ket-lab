"""Lições 4.5 a 4.7: verificações independentes dos números e das regras ensinadas."""

import itertools
import runpy
from functools import reduce

import numpy as np
import pytest

from qlp_engine import validation

from .conftest import CONTENT_DIR

TRACK = CONTENT_DIR / "track_4_noise_qec"


def solution(folder):
    return runpy.run_path(str(TRACK / folder / "solution.py"))


def validate(library, lesson_id, code):
    return validation.validate(code, library.validation_bundle(lesson_id))


# ---- 4.5: formalismo dos estabilizadores -----------------------------------

P = {
    "I": np.eye(2),
    "X": np.array([[0, 1], [1, 0]]),
    "Y": np.array([[0, -1j], [1j, 0]]),
    "Z": np.diag([1, -1]),
}


def op(s):
    return reduce(np.kron, [P[c] for c in s])


def test_bit_flip_syndrome_table_is_the_known_one():
    table = solution("section_4_5_stabilizer_formalism")["table"]
    expected = {(0, 0, 1): (1, 0), (0, 1, 1): (1, 1), (1, 0, 1): (0, 1)}  # (posição, tipo) abaixo
    for i, pauli in itertools.product(range(3), "XYZ"):
        error = "I" * i + pauli + "I" * (2 - i)
        want = (0, 0) if pauli == "Z" else [(1, 0), (1, 1), (0, 1)][i]
        assert tuple(table[error]) == want, error
    assert expected  # tabela de 4.2: X0 → 10, X1 → 11, X2 → 01


def test_syndrome_matches_the_eigenvalues_on_the_code_space():
    """O erro leva |000⟩ a um autoestado de cada gerador com autovalor (−1)^s."""
    ns = solution("section_4_5_stabilizer_formalism")
    zero = np.zeros(8)
    zero[0] = 1
    for error in ns["ERRORS"]:
        state = op(error) @ zero
        for g, bit in zip(ns["STABILIZERS"], ns["syndrome"](error, ns["STABILIZERS"])):
            assert np.allclose(op(g) @ state, (-1) ** bit * state), (error, g)


def test_five_qubit_code_has_distinct_nonzero_syndromes():
    ns = solution("section_4_5_stabilizer_formalism")
    gens = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]
    seen = set()
    for i, pauli in itertools.product(range(5), "XYZ"):
        s = ns["syndrome"]("I" * i + pauli + "I" * (4 - i), gens)
        assert any(s)
        seen.add(s)
    assert len(seen) == 15


def test_logical_operators_of_the_bit_flip_code():
    ns = solution("section_4_5_stabilizer_formalism")
    for logical in (ns["logical_X"], ns["logical_Z"]):
        for g in ns["STABILIZERS"]:
            assert np.allclose(op(logical) @ op(g), op(g) @ op(logical))
    assert np.allclose(op(ns["logical_X"]) @ op(ns["logical_Z"]), -op(ns["logical_Z"]) @ op(ns["logical_X"]))


# ---- 4.6: código tórico ------------------------------------------------------

def test_single_edge_error_lights_two_plaquettes_and_chain_moves_one_end():
    ns = solution("section_4_6_toric_code")
    for L in (3, 4):
        for t, r, c in itertools.product("hv", range(L), range(L)):
            assert len(ns["defects"](L, {(t, r, c)})) == 2
    # cadeia vertical de duas arestas na mesma linha: defeitos só nas pontas
    assert ns["defects"](3, {("v", 0, 1), ("v", 0, 2)}) == [(0, 0), (0, 2)]


def test_stars_and_plaquettes_commute_and_loops_have_no_defects():
    ns = solution("section_4_6_toric_code")
    L = 4
    for r, c in itertools.product(range(L), repeat=2):
        star = {("h", r, c), ("h", r, (c - 1) % L), ("v", r, c), ("v", (r - 1) % L, c)}
        assert ns["defects"](L, star) == []
        assert ns["logical_class"](L, star) == (0, 0)
    assert ns["logical_class"](L, {("v", 2, c) for c in range(L)}) == (0, 1)
    assert ns["logical_class"](L, {("h", r, 1) for r in range(L)}) == (1, 0)
    assert ns["defects"](L, {("v", 2, c) for c in range(L)}) == []


def test_toric_distance_equals_L_for_L_2_and_3():
    ns = solution("section_4_6_toric_code")
    for L in (2, 3):
        edges = [(t, r, c) for t in "hv" for r in range(L) for c in range(L)]
        d = next(
            w
            for w in range(1, len(edges) + 1)
            if any(
                not ns["defects"](L, set(ch)) and ns["logical_class"](L, set(ch)) != (0, 0)
                for ch in itertools.combinations(edges, w)
            )
        )
        assert d == L
    assert ns["distance"] == 3


# ---- 4.7: teorema do limiar -------------------------------------------------

def test_threshold_is_one_half_and_is_a_repelling_fixed_point():
    f = solution("section_4_7_threshold_theorem")["f"]
    assert f(0.5) == pytest.approx(0.5)
    assert f(0.4) < 0.4 and f(0.6) > 0.6
    assert solution("section_4_7_threshold_theorem")["p_th"] == 0.5


def test_concatenated_error_rates():
    ns = solution("section_4_7_threshold_theorem")
    assert ns["f"](0.01) == pytest.approx(2.98e-4)
    assert ns["concatenated"](0.01, 2) == pytest.approx(2.66359e-7, rel=1e-5)
    assert ns["concatenated"](0.01, 4) == pytest.approx(1.35904e-25, rel=1e-5)
    assert ns["concatenated"](0.6, 3) > 0.6
    assert ns["k_needed"] == 4 and ns["qubits"] == 81
    assert ns["levels_needed"](0.01, 1e-15) == 4
    assert ns["levels_needed"](0.01, 1e-13) == 4  # p_3 = 2.1e-13 > 1e-13
    assert ns["levels_needed"](0.01, 2.2e-13) == 3
    assert ns["levels_needed"](0.5, 1e-3) is None and ns["levels_needed"](0.7, 0.5) is None


def test_generic_model_matches_exact_map_for_small_p():
    ns = solution("section_4_7_threshold_theorem")
    assert ns["generic_rate"](0.01, 3, 1) == pytest.approx(3e-4)
    for p in (1e-3, 1e-2):
        assert ns["generic_rate"](p, 3, 3) == pytest.approx(ns["concatenated"](p, 3), rel=0.05)


# ---- validadores: o que a solução passa, uma resposta errada não ------------

@pytest.mark.parametrize(
    "lesson_id, folder, old, new",
    [
        ("4.5", "section_4_5_stabilizer_formalism", "clashes % 2 == 0", "clashes == 0"),
        ("4.5", "section_4_5_stabilizer_formalism", 'logical_Z = "ZII"', 'logical_Z = "ZZI"'),
        ("4.6", "section_4_6_toric_code", "count % 2 == 1", "count >= 1"),
        ("4.6", "section_4_6_toric_code", "e[0] == \"v\" and e[2] == 0", "e[0] == \"v\" and e[1] == 0"),
        ("4.7", "section_4_7_threshold_theorem", "3 * p**2 - 2 * p**3", "3 * p**2"),
        ("4.7", "section_4_7_threshold_theorem", "p_th = 0.5", "p_th = 1 / 3"),
        ("4.7", "section_4_7_threshold_theorem", "qubits = 3**k_needed", "qubits = 2**k_needed"),
    ],
)
def test_validators_reject_plausible_mistakes(library, lesson_id, folder, old, new):
    code = (TRACK / folder / "solution.py").read_text(encoding="utf-8")
    assert old in code
    assert validate(library, lesson_id, code)["passed"]
    assert not validate(library, lesson_id, code.replace(old, new))["passed"]
