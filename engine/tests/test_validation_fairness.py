"""P4.7: sub-circuits are opened before the rules, variable checks are exact for lists, cap is passed."""

import pytest

from ket_lab_engine import validation

HEADER = "from qiskit import QuantumCircuit\n"


def lesson(solution_body, vtype="state_fidelity", **rules):
    return {"id": "t", "solution": HEADER + solution_body, "validation": {"type": vtype, **rules}}


BELL_SOLUTION = "qc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n"
SUB = (
    "sub = QuantumCircuit(2)\nsub.h(0)\nsub.cx(0, 1)\n"
    "qc = QuantumCircuit(2)\nqc.append(sub.to_gate(), [0, 1])\n"
)
SUB_INSTRUCTION = SUB.replace("to_gate", "to_instruction")
COMPOSED = "sub = QuantumCircuit(2)\nsub.h(0)\nsub.cx(0, 1)\nqc = QuantumCircuit(2)\nqc.compose(sub, inplace=True)\n"
RULES = dict(allowed_gates=["h", "cx"], required_gates=["h", "cx"], gate_counts={"cx": 1}, max_gates=2)


@pytest.mark.parametrize("body", [SUB, SUB_INSTRUCTION, COMPOSED, BELL_SOLUTION])
def test_solution_built_with_a_subcircuit_is_accepted(body):
    result = validation.validate(HEADER + body, lesson(BELL_SOLUTION, **RULES))
    assert result["passed"], result


def test_nested_subcircuits_and_qubit_mapping():
    body = (
        "inner = QuantumCircuit(2)\ninner.h(0)\ninner.cx(0, 1)\n"
        "outer = QuantumCircuit(3)\nouter.append(inner.to_gate(), [2, 0])\n"
        "qc = QuantumCircuit(3)\nqc.append(outer.to_gate(), [0, 1, 2])\n"
    )
    far = lesson("qc = QuantumCircuit(3)\nqc.h(2)\nqc.cx(2, 0)\n", forbidden_pairs=[[0, 1]], allowed_gates=["h", "cx"])
    assert validation.validate(HEADER + body, far)["passed"]
    pair = lesson("qc = QuantumCircuit(3)\nqc.h(2)\nqc.cx(2, 0)\n", forbidden_pairs=[[0, 2]])
    assert validation.validate(HEADER + body, pair)["code"] == "forbidden_pair"


def test_forbidden_gate_hidden_in_a_subcircuit_is_still_rejected():
    body = "sub = QuantumCircuit(2)\nsub.h(0)\nsub.swap(0, 1)\nqc = QuantumCircuit(2)\nqc.append(sub.to_gate(), [0, 1])\n"
    result = validation.validate(HEADER + body, lesson(BELL_SOLUTION, allowed_gates=["h", "cx"]))
    assert result["code"] == "forbidden_gate" and "swap" in result["message"] and "circuit-" not in result["message"]


def test_gate_counts_and_max_gates_count_what_is_inside():
    body = "sub = QuantumCircuit(2)\nsub.h(0)\nsub.cx(0, 1)\nsub.cx(0, 1)\nsub.cx(0, 1)\nqc = QuantumCircuit(2)\nqc.append(sub.to_gate(), [0, 1])\n"
    assert validation.validate(HEADER + body, lesson(BELL_SOLUTION, gate_counts={"cx": 1}))["code"] == "gate_count"
    assert validation.validate(HEADER + body, lesson(BELL_SOLUTION, max_gates=2))["code"] == "too_many_gates"


def test_lesson_defined_gates_stay_opaque():
    # a gate named by the lesson's setup (not "circuit-N") is still one gate to the rules
    setup = "def oracle():\n    s = QuantumCircuit(1, name='oracle')\n    s.x(0)\n    return s.to_gate()\n"
    data = {**lesson("qc = QuantumCircuit(1)\nqc.append(oracle(), [0])\n", required_gates=["oracle"], allowed_gates=["oracle"]),
            "hidden_setup": HEADER + setup}
    assert validation.validate("qc = QuantumCircuit(1)\nqc.append(oracle(), [0])\n", data)["passed"]


# -- expected_variables -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "actual, expected, tolerance, ok",
    [
        ([3.9, 5.2], [3, 5], None, False),
        ([5, 3], [3, 5], None, True),
        ([3, 5, 7], [3, 5], None, False),
        ((3, 5), [3, 5], None, True),
        ([3.0, 5.0], [3, 5], None, True),
        (None, [3, 5], None, False),
        (0.375, 0.375, None, True),
        (0.3750004, 0.375, None, True),   # 1e-6 relative
        (0.3751, 0.375, None, False),
        (0.37, 0.375, 0.02, True),        # per-variable tolerance
        (0.37, 0.375, 0.001, False),
        (1e-8, 0.0, None, True),          # absolute near zero
        (0.5000001, 0.5, None, True),     # a rounded right answer used to fail at 1e-9
        ("a", "a", None, True),
        ([3.5, 5.0], [3, 5], 0.05, False),
        ([3.01, 5.0], [3, 5], 0.05, True),
    ],
)
def test_same_value(actual, expected, tolerance, ok):
    assert validation._same_value(actual, expected, tolerance) is ok


def variables_lesson(expected):
    return lesson("qc = QuantumCircuit(1)\nqc.x(0)\n", expected_variables=expected)


def test_variable_check_end_to_end_with_manifest_tolerance():
    code = HEADER + "qc = QuantumCircuit(1)\nqc.x(0)\nfactors = [3.9, 5.2]\ntheta = 0.37\n"
    wrong = validation.validate(code, variables_lesson({"factors": [3, 5]}))
    assert wrong["code"] == "variable_wrong"
    plain = validation.validate(code, variables_lesson({"theta": 0.375}))
    assert plain["code"] == "variable_wrong"
    loose = validation.validate(code, variables_lesson({"theta": {"value": 0.375, "tolerance": 0.02}}))
    assert loose["passed"] and "0.375" in loose["message"]
    assert validation.validate(code, variables_lesson({"missing": 1}))["code"] == "variable_missing"


# -- max_qubits for the reference solution ---------------------------------------------------------------


def test_reference_solution_runs_with_the_lessons_qubit_cap():
    big = "qc = QuantumCircuit(12)\nqc.x(11)\n"
    data = {**lesson(big), "max_qubits": 12}
    result = validation.validate(HEADER + big, data)
    assert result["passed"], result
    counts = {**lesson(big + "qc.measure_all()\n", "counts_distribution"), "max_qubits": 12}
    assert validation.validate(HEADER + big + "qc.measure_all()\n", counts)["passed"]
    cases = {**lesson(big, "state_cases", cases=[0]), "max_qubits": 12}
    assert validation.validate(HEADER + big, cases)["passed"]
