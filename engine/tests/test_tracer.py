import pytest

from qlp_engine import tracer


def run(code: str) -> tracer.Execution:
    return tracer.execute(code)


def test_maps_each_instruction_to_its_line():
    execution = run(
        "from qiskit import QuantumCircuit\n"
        "qc = QuantumCircuit(2)\n"
        "qc.h(0)\n"
        "\n"
        "qc.cx(0, 1)\n"
    )
    assert execution.lines == [3, 5]


def test_loop_body_lines_repeat():
    execution = run(
        "from qiskit import QuantumCircuit\n"
        "qc = QuantumCircuit(3)\n"
        "for i in range(2):\n"
        "    qc.h(i)\n"
        "    qc.cx(i, i + 1)\n"
    )
    assert execution.lines == [4, 5, 4, 5]


def test_instructions_from_a_function_belong_to_the_calling_line():
    execution = run(
        "from qiskit import QuantumCircuit\n"
        "def bell(circuit):\n"
        "    circuit.h(0)\n"
        "    circuit.cx(0, 1)\n"
        "qc = QuantumCircuit(2)\n"
        "qc.x(0)\n"
        "bell(qc)\n"
    )
    assert execution.lines == [6, 7, 7]


def test_last_circuit_is_used_when_there_is_no_qc():
    execution = run(
        "from qiskit import QuantumCircuit\n"
        "a = QuantumCircuit(1)\n"
        "a.x(0)\n"
        "b = QuantumCircuit(2)\n"
        "b.h(1)\n"
    )
    assert execution.circuit.num_qubits == 2
    assert execution.lines == [5]


def test_stdout_is_captured():
    assert run("from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nprint('oi')\n").stdout == "oi\n"


@pytest.mark.parametrize(
    "code, line, kind",
    [
        ("from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nqc.h(\n", 3, "syntax"),
        ("from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nqc.h(5)\n", 3, "runtime"),
        ("from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\n\nqc.foo(0)\n", 4, "runtime"),
        ("x = 1\n", None, "no_circuit"),
    ],
)
def test_errors_carry_the_line(code, line, kind):
    with pytest.raises(tracer.UserCodeError) as info:
        run(code)
    assert info.value.line == line
    assert info.value.kind == kind


@pytest.mark.parametrize(
    "code",
    [
        "import os\n",
        "import subprocess\n",
        "from sys import exit\n",
        "open('x', 'w')\n",
        "__import__('os')\n",
        "eval('1')\n",
        "().__class__.__bases__\n",
    ],
)
def test_guard_rejects_unsafe_constructs(code):
    with pytest.raises(tracer.UserCodeError) as info:
        run(code)
    assert info.value.kind == "guard"
    assert info.value.line == 1


def test_guard_allows_scientific_imports():
    run("import math, numpy as np\nfrom qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nqc.rx(math.pi, 0)\n")


def test_report_records_series_and_rejects_non_numbers():
    import pytest as _pytest

    code = (
        "from qiskit import QuantumCircuit\n"
        "import numpy as np\n"
        "qc = QuantumCircuit(1)\n"
        "for k in range(3):\n"
        "    report(np.float64(k) / 2)\n"
        "report(cost=9, accuracy=1)\n"
    )
    execution = tracer.execute(code)
    assert execution.reports == {"cost": [0.0, 0.5, 1.0, 9.0], "accuracy": [1.0]}
    with _pytest.raises(tracer.UserCodeError) as error:
        tracer.execute("from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nreport('x')\n")
    assert error.value.line == 3
