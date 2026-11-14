import pytest

from qlp_engine import validation

HEADER = "from qiskit import QuantumCircuit\n"


def lesson(solution_body: str, **rules) -> dict:
    return {
        "id": "t",
        "solution": HEADER + solution_body,
        "validation": {"type": "state_fidelity", **rules},
    }


FLIP = lesson("qc = QuantumCircuit(1)\nqc.x(0)\n", allowed_gates=["x", "y", "z", "h", "rx"])
MINUS = lesson("qc = QuantumCircuit(1)\nqc.h(0)\nqc.z(0)\n")


@pytest.mark.parametrize(
    "body",
    [
        "qc = QuantumCircuit(1)\nqc.x(0)\n",
        "qc = QuantumCircuit(1)\nqc.h(0)\nqc.z(0)\nqc.h(0)\n",  # HZH = X
        "qc = QuantumCircuit(1)\nqc.y(0)\n",  # difere só por fase global
        "import math\nqc = QuantumCircuit(1)\nqc.rx(math.pi, 0)\n",
    ],
)
def test_equivalent_solutions_pass(body):
    result = validation.validate(HEADER + body, FLIP)
    assert result["passed"], result
    assert result["fidelity"] > 0.999


def test_wrong_state_reports_fidelity():
    result = validation.validate(HEADER + "qc = QuantumCircuit(1)\nqc.h(0)\n", FLIP)
    assert not result["passed"]
    assert result["code"] == "wrong_state"
    assert result["fidelity"] == pytest.approx(0.5)


def test_phase_diagnosis():
    result = validation.validate(HEADER + "qc = QuantumCircuit(1)\nqc.h(0)\n", MINUS)
    assert result["code"] == "phase"
    assert "fase relativa" in result["message"]


def test_forbidden_gate_blocks_shortcuts():
    result = validation.validate(HEADER + "qc = QuantumCircuit(1)\nqc.initialize([0, 1], 0)\n", FLIP)
    assert result["code"] == "forbidden_gate"
    assert "initialize" in result["message"]


def test_max_gates():
    capped = lesson("qc = QuantumCircuit(1)\nqc.x(0)\n", max_gates=1)
    result = validation.validate(HEADER + "qc = QuantumCircuit(1)\nqc.h(0)\nqc.z(0)\nqc.h(0)\n", capped)
    assert result["code"] == "too_many_gates"


def test_qubit_mismatch():
    result = validation.validate(HEADER + "qc = QuantumCircuit(2)\nqc.x(0)\n", FLIP)
    assert result["code"] == "qubit_mismatch"


def test_student_error_is_reported_not_raised():
    result = validation.validate(HEADER + "qc = QuantumCircuit(1)\nqc.x(3)\n", FLIP)
    assert result["code"] == "error"
    assert result["line"] == 3


QRNG = {
    "id": "t",
    "solution": HEADER + "qc = QuantumCircuit(1, 1)\nqc.h(0)\nqc.measure(0, 0)\n",
    "validation": {"type": "counts_distribution", "shots": 4096, "tolerance": 0.05},
}


@pytest.mark.parametrize(
    "body",
    [
        "qc = QuantumCircuit(1, 1)\nqc.h(0)\nqc.measure(0, 0)\n",
        "import math\nqc = QuantumCircuit(1, 1)\nqc.ry(math.pi / 2, 0)\nqc.measure(0, 0)\n",
        "qc = QuantumCircuit(1, 1)\nqc.x(0)\nqc.h(0)\nqc.measure(0, 0)\n",  # |-> também é 50/50
    ],
)
def test_counts_distribution_accepts_any_uniform_source(body):
    result = validation.validate(HEADER + body, QRNG)
    assert result["passed"], result


def test_counts_distribution_requires_measurement():
    result = validation.validate(HEADER + "qc = QuantumCircuit(1, 1)\nqc.h(0)\n", QRNG)
    assert result["code"] == "no_measurement"


def test_counts_distribution_rejects_biased_source():
    result = validation.validate(HEADER + "qc = QuantumCircuit(1, 1)\nqc.measure(0, 0)\n", QRNG)
    assert result["code"] == "wrong_distribution"
    assert "0: 100%" in result["message"] and "1: 50%" in result["message"]


def test_counts_distribution_checks_classical_width():
    result = validation.validate(
        HEADER + "qc = QuantumCircuit(1, 2)\nqc.h(0)\nqc.measure(0, 0)\n", QRNG
    )
    assert result["code"] == "qubit_mismatch"


def _teleport_lesson():
    from pathlib import Path

    from qlp_engine.content import ContentLibrary

    library = ContentLibrary(Path(__file__).resolve().parents[2] / "content")
    return library.validation_bundle("1.6")


TELEPORT_PREFIX = (
    "from qiskit import QuantumCircuit\n"
    "qc = QuantumCircuit(3, 2)\n"
    "prepare_alice_state(qc)\n"
    "qc.h(1)\nqc.cx(1, 2)\nqc.cx(0, 1)\nqc.h(0)\n"
    "qc.measure(0, 0)\nqc.measure(1, 1)\n"
)


def test_teleport_reference_passes_with_varied_inputs():
    lesson = _teleport_lesson()
    result = validation.validate(lesson["solution"], lesson)
    assert result["passed"], result
    assert "192 combinações" in result["message"]


def test_teleport_with_one_correction_missing_is_partial():
    lesson = _teleport_lesson()
    code = TELEPORT_PREFIX + "with qc.if_test((qc.clbits[1], 1)):\n    qc.x(2)\n"
    result = validation.validate(code, lesson)
    assert result["code"] == "partial", result


def test_teleport_correction_order_matters_only_up_to_global_phase():
    lesson = _teleport_lesson()
    code = TELEPORT_PREFIX + (
        "with qc.if_test((qc.clbits[0], 1)):\n    qc.z(2)\n"
        "with qc.if_test((qc.clbits[1], 1)):\n    qc.x(2)\n"
    )
    assert validation.validate(code, lesson)["passed"]  # ZX e XZ diferem só por fase global


def test_teleport_rejects_direct_gates_between_alice_and_bob():
    lesson = _teleport_lesson()
    code = (
        "from qiskit import QuantumCircuit\nqc = QuantumCircuit(3, 2)\nprepare_alice_state(qc)\n"
        "qc.cx(0, 2)\nqc.cx(2, 0)\nqc.cx(0, 2)\n"
    )
    result = validation.validate(code, lesson)
    assert result["code"] == "forbidden_pair", result


def test_teleport_inputs_are_hidden_from_the_student():
    lesson = _teleport_lesson()
    code = (
        "from qiskit import QuantumCircuit\nqc = QuantumCircuit(3, 2)\nprepare_alice_state(qc)\n"
        "print(prepare_alice_state.__closure__)\n"
    )
    assert validation.validate(code, lesson)["code"] == "error"


def test_gate_counts_enforce_a_single_oracle_query(library):
    bundle = library.validation_bundle("2.3")
    rules = {**bundle["validation"], "gate_counts": {"oracle": 1}}
    twice = bundle["solution"].replace("oracle(qc)\n", "oracle(qc)\noracle(qc)\n")
    result = validation.validate(twice, {**bundle, "validation": rules})
    assert result["code"] == "gate_count"
    assert "`oracle`" in result["message"] and "2" in result["message"]


def test_reduced_state_tests_fixed_inputs_first():
    lesson = _teleport_lesson()
    rules = {**lesson["validation"], "inputs": [[0.0, 0.0], [1.5707963, 0.0]], "trials": 0}
    only_x = TELEPORT_PREFIX + "with qc.if_test((qc.clbits[1], 1)):\n    qc.x(2)\n"
    result = validation.validate(only_x, {**lesson, "validation": rules})
    # Em |0⟩ a correção Z não faz falta, mas em |+⟩ faz: o erro é pego mesmo sem sorteio.
    assert result["code"] == "partial", result
