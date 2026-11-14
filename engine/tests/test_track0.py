"""Trilha 0 (kit de matemática): valores de referência calculados de forma independente
e respostas erradas comuns rejeitadas com a mensagem pretendida."""

import cmath
import math

import numpy as np
import pytest

from qlp_engine import validation


def validate(library, lesson_id, code):
    return validation.validate(code, library.validation_bundle(lesson_id))


def solution_with(library, lesson_id, **replacements):
    """Solução de referência com as linhas `nome = ...` trocadas pelas dadas."""
    lines = library.validation_bundle(lesson_id)["solution"].splitlines()
    out = []
    for line in lines:
        name = line.split("=")[0].strip()
        if "=" in line and name in replacements and not line.startswith(" "):
            out.append(f"{name} = {replacements[name]}")
        else:
            out.append(line)
    return "\n".join(out) + "\n"


def solution_namespace(library, lesson_id):
    from qlp_engine import tracer

    code = library.validation_bundle(lesson_id)["solution"]
    return tracer.execute(code, None, None, trace=False, require_circuit=False).namespace


# ---------------------------------------------------------------- 0.1

def test_0_1_reference_values(library):
    ns = solution_namespace(library, "0.1")
    assert ns["product"] == pytest.approx(complex(3 * 1 + 4 * 2, -3 * 2 + 4 * 1))  # (3+4i)(1-2i) = 11-2i
    assert ns["modulus"] == pytest.approx(math.hypot(3, 4))
    assert ns["phi"] == pytest.approx(math.atan2(4, 3))
    assert ns["z_polar"] == pytest.approx(3 + 4j)
    assert ns["unit"] == pytest.approx(complex(0.5, math.sqrt(3) / 2))
    assert ns["unit_modulus"] == pytest.approx(1.0)
    assert ns["rel_phase"] == pytest.approx(0.5)


@pytest.mark.parametrize(
    "replacement, key",
    [
        ({"product": "z + w"}, "product_wrong"),
        ({"modulus": "z * z.conjugate()"}, "modulus_wrong"),
        ({"phi": "np.arctan(3 / 4)"}, "phi_wrong"),
        ({"z_polar": "modulus * np.exp(phi)"}, "z_polar_wrong"),
        ({"unit": "np.exp(theta)"}, "unit_wrong"),
        ({"unit_modulus": "2"}, "unit_modulus_wrong"),
        ({"rel_phase": "np.angle(b)"}, "rel_phase_single"),
        ({"rel_phase": "np.angle(a) - np.angle(b)"}, "rel_phase_wrong"),
    ],
)
def test_0_1_wrong_answers(library, replacement, key):
    result = validate(library, "0.1", solution_with(library, "0.1", **replacement))
    assert not result["passed"] and result["code"] == key, result
    assert "{" not in result["message"]


def test_0_1_accepts_cmath_and_equivalent_phase(library):
    code = solution_with(library, "0.1", phi="cmath.phase(z)", rel_phase="np.angle(b / a) + 2 * np.pi")
    assert validate(library, "0.1", code)["passed"]


def test_0_1_missing_and_non_numeric(library):
    code = solution_with(library, "0.1", unit_modulus="'five'")
    assert validate(library, "0.1", code)["code"] == "not_number"
    result = validate(library, "0.1", "import numpy as np\nz = 1\n")
    assert result["code"] == "missing"


# ---------------------------------------------------------------- 0.2

def test_0_2_reference_values(library):
    ns = solution_namespace(library, "0.2")
    assert ns["norm"] == pytest.approx(2.0)
    assert ns["v_hat"] == pytest.approx([(1 + 1j) / 2, (1 - 1j) / 2])
    # <a|b> = conj(1)*1 + conj(i)*1, over 2 (written out, without vdot)
    assert ns["inner"] == pytest.approx((1 - 1j) / 2)
    assert ns["prob"] == pytest.approx(0.5)
    assert ns["minus"] == pytest.approx([1 / math.sqrt(2), -1 / math.sqrt(2)])
    assert ns["amp_plus"] == pytest.approx((0.6 + 0.8j) / math.sqrt(2))
    assert ns["amp_minus"] == pytest.approx((0.6 - 0.8j) / math.sqrt(2))
    assert abs(ns["amp_plus"]) ** 2 + abs(ns["amp_minus"]) ** 2 == pytest.approx(1.0)
    assert ns["inner4"] == pytest.approx(1 / math.sqrt(2))


@pytest.mark.parametrize(
    "replacement, key",
    [
        ({"norm": "np.sum(abs(v))"}, "norm_wrong"),
        ({"v_hat": "v"}, "v_hat_wrong"),
        ({"inner": "np.dot(a, b)"}, "inner_conjugate"),
        ({"inner": "np.vdot(b, a)"}, "inner_conjugate"),
        ({"inner": "1"}, "inner_wrong"),
        ({"prob": "inner"}, "prob_wrong"),
        ({"minus": "np.array([1, -1])"}, "minus_not_unit"),
        ({"minus": "np.array([1, 1]) / np.sqrt(2)"}, "minus_not_orthogonal"),
        ({"minus": "np.array([-1, 1]) / np.sqrt(2)"}, "minus_wrong"),
        ({"amp_plus": "np.vdot(psi, plus)"}, "amp_plus_wrong"),
        ({"amp_minus": "np.vdot(psi, minus)"}, "amp_minus_wrong"),
        ({"inner4": "np.dot(phi_plus, q) / 2"}, "inner4_wrong"),
    ],
)
def test_0_2_wrong_answers(library, replacement, key):
    result = validate(library, "0.2", solution_with(library, "0.2", **replacement))
    assert not result["passed"] and result["code"] == key, result
    assert "{" not in result["message"]


def test_0_2_wrong_shape(library):
    result = validate(library, "0.2", solution_with(library, "0.2", v_hat="3"))
    assert result["code"] == "not_array"


# ---------------------------------------------------------------- 0.3

def test_0_3_reference_values(library):
    ns = solution_namespace(library, "0.3")
    assert ns["a_unitary"] is True or ns["a_unitary"] == True  # noqa: E712
    assert not ns["b_unitary"]
    assert ns["Y"] == pytest.approx(np.array([[0, -1j], [1j, 0]]))
    # Y squared is the identity and Y equals its adjoint
    assert ns["Y"] @ ns["Y"] == pytest.approx(np.eye(2))
    assert ns["Y"] == pytest.approx(ns["Y"].conj().T)
    assert sorted(ns["eigvals"].real) == pytest.approx([-1, 1])
    for k in range(2):
        assert ns["X"] @ ns["eigvecs"][:, k] == pytest.approx(ns["eigvals"][k] * ns["eigvecs"][:, k])
    assert ns["k_hermitian"]
    # <Z> = |alpha|^2 - |beta|^2 = 0.36 - 0.64
    assert ns["expect_z"] == pytest.approx(-0.28)
    # <Y> computed by hand: psi = (0.6, 0.8i), Y psi = (0.8, 0.6i), <psi|Y psi> = 0.48 + 0.48
    assert ns["expect_y"] == pytest.approx(0.96)


@pytest.mark.parametrize(
    "replacement, key",
    [
        ({"Y": "np.array([[0, 1j], [-1j, 0]])"}, "y_wrong"),
        ({"a_unitary": "(A.conj().T @ A == np.eye(2)).all()"}, "a_unitary_wrong"),
        ({"b_unitary": "True"}, "b_unitary_wrong"),
        ({"eigvals, eigvecs": "np.array([1.0, 2.0]), np.eye(2)"}, "eigvals_wrong"),
        ({"eigvals, eigvecs": "np.linalg.eigvals(X), np.eye(2)"}, "eigvecs_wrong"),
        ({"k_hermitian": "False"}, "k_hermitian_wrong"),
        ({"expect_z": "0.28"}, "expect_z_wrong"),
        ({"expect_y": "psi @ (Y @ psi)"}, "expect_y_no_conjugate"),
        ({"expect_y": "-0.96"}, "expect_y_wrong"),
        ({"a_unitary": "1"}, "not_bool"),
    ],
)
def test_0_3_wrong_answers(library, replacement, key):
    result = validate(library, "0.3", solution_with(library, "0.3", **replacement))
    assert not result["passed"] and result["code"] == key, result
    assert "{" not in result["message"]


def test_0_3_accepts_other_eigenvector_phases(library):
    code = solution_with(library, "0.3", **{"eigvals, eigvecs": "np.linalg.eigh(X)[0], np.linalg.eigh(X)[1] * 1j"})
    assert validate(library, "0.3", code)["passed"]


# ---------------------------------------------------------------- 0.4

def test_0_4_reference_values(library):
    ns = solution_namespace(library, "0.4")
    r = 1 / math.sqrt(2)
    assert ns["prod"] == pytest.approx([r, 0, r, 0])  # |+>_1 |0>_0: indices 00 and 10
    assert ns["op_q0"] == pytest.approx(np.array([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]))
    assert ns["op_q1"] == pytest.approx(np.array([[0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]]))
    assert ns["after"] == pytest.approx([0, r, 0, r])
    assert ns["three"] == pytest.approx(np.full(8, 1 / math.sqrt(8)))
    assert not ns["s1_product"] and ns["s2_product"]
    # independent facts: s2 = |-> (x) |+>, s1 cannot be factorized (rank 2 as a 2x2 matrix)
    s1 = np.array([1, 0, 0, 1]) / math.sqrt(2)
    s2 = np.array([1, 1, -1, -1]) / 2
    assert np.linalg.matrix_rank(s1.reshape(2, 2)) == 2
    assert np.linalg.matrix_rank(s2.reshape(2, 2)) == 1
    minus = np.array([1, -1]) / math.sqrt(2)
    plus = np.array([1, 1]) / math.sqrt(2)
    assert np.kron(minus, plus) == pytest.approx(s2)


@pytest.mark.parametrize(
    "replacement, key",
    [
        ({"prod": "np.kron(zero, plus)"}, "prod_reversed"),
        ({"prod": "np.kron(plus, one)"}, "prod_wrong"),
        ({"op_q0": "np.kron(X, I)"}, "op_q0_swapped"),
        ({"op_q0": "np.kron(X, X)"}, "op_q0_wrong"),
        ({"op_q1": "np.kron(I, X)"}, "op_q1_swapped"),
        ({"op_q1": "np.eye(4)"}, "op_q1_wrong"),
        ({"after": "op_q1 @ prod"}, "after_wrong"),
        ({"three": "np.kron(plus, plus)"}, "not_array"),
        ({"three": "np.kron(np.kron(plus, plus), zero)"}, "three_wrong"),
        ({"s1_product": "True"}, "s1_wrong"),
        ({"s2_product": "False"}, "s2_wrong"),
    ],
)
def test_0_4_wrong_answers(library, replacement, key):
    result = validate(library, "0.4", solution_with(library, "0.4", **replacement))
    assert not result["passed"] and result["code"] == key, result
    assert "{" not in result["message"]


def test_0_4_accepts_numpy_bool(library):
    code = solution_with(library, "0.4", s1_product="np.isclose(s1[0] * s1[3], s1[1] * s1[2])")
    assert validate(library, "0.4", code)["passed"]
