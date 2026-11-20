"""PennyLane circuits and noisy simulation."""

import numpy as np
import pytest

from ket_lab_engine import geometry, pl, simulator, tracer

HEADER = "import pennylane as qml\nfrom pennylane import numpy as np\n"


def trace(code: str, qnode: str | None = None, args: list[str] | None = None):
    execution = tracer.execute(HEADER + code, trace=False, require_circuit=False)
    node = pl.find_qnode(execution.namespace, qnode)
    ops, lines, n = pl.trace_qnode(node, pl.qnode_arguments(node, execution.namespace, args))
    return execution, ops, lines, n


def test_lines_come_from_the_qnode_body():
    _, ops, lines, n = trace(
        "dev = qml.device('default.qubit', wires=2)\n"
        "@qml.qnode(dev)\n"
        "def circuit():\n"
        "    qml.Hadamard(0)\n"
        "    qml.CNOT(wires=[0, 1])\n"
        "    return qml.state()\n"
    )
    assert [op.name for op in ops] == ["h", "cx"]
    assert lines == [6, 7]  # HEADER ocupa 2 linhas
    assert n == 2
    assert ops[1].num_ctrl == 1 and ops[1].qubits == (0, 1)


@pytest.mark.parametrize("seed", range(4))
def test_state_matches_pennylane_in_qiskit_order(seed):
    rng = np.random.default_rng(seed)
    a, b, c = rng.uniform(0, np.pi, 3)
    code = (
        "dev = qml.device('default.qubit', wires=3)\n"
        "@qml.qnode(dev)\n"
        "def circuit():\n"
        f"    qml.RY({a}, wires=0)\n"
        f"    qml.RX({b}, wires=2)\n"
        "    qml.CNOT(wires=[0, 1])\n"
        f"    qml.IsingZZ({c}, wires=[1, 2])\n"
        "    qml.Toffoli(wires=[0, 2, 1])\n"
        "    return qml.state()\n"
    )
    execution, ops, lines, n = trace(code)
    ours = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    theirs = np.asarray(execution.namespace["circuit"]())  # wire 0 = most significant bit
    reordered = theirs.reshape((2,) * n).transpose(range(n)[::-1]).reshape(-1)
    assert abs(np.vdot(reordered, ours)) == pytest.approx(1.0)


def test_templates_are_decomposed_into_gates():
    _, ops, _, _ = trace(
        "dev = qml.device('default.qubit', wires=2)\n"
        "@qml.qnode(dev)\n"
        "def circuit(weights):\n"
        "    qml.BasicEntanglerLayers(weights, wires=[0, 1])\n"
        "    return qml.expval(qml.PauliZ(0))\n"
        "w = np.array([[0.1, 0.2]])\n",
        args=["w"],
    )
    assert {op.name for op in ops} <= {"rx", "cx"}


def test_noise_channels_switch_to_density_matrix():
    execution, ops, lines, n = trace(
        "dev = qml.device('default.mixed', wires=2)\n"
        "@qml.qnode(dev)\n"
        "def circuit():\n"
        "    qml.Hadamard(0)\n"
        "    qml.CNOT(wires=[0, 1])\n"
        "    qml.DepolarizingChannel(0.3, wires=1)\n"
        "    return qml.density_matrix(wires=[0, 1])\n"
    )
    trajectory = simulator.run_ops_trajectory(ops, lines, n)
    rho = trajectory.states[-1]
    theirs = np.asarray(execution.namespace["circuit"]())
    swap = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])  # wire order
    assert np.allclose(rho, swap @ theirs @ swap, atol=1e-9)
    snap = geometry.snapshot(rho, n)
    assert snap["amplitudes"] is None
    assert snap["state_purity"] < 1
    assert sum(snap["probabilities"]) == pytest.approx(1.0)


def test_bit_flip_shrinks_the_bloch_vector():
    _, ops, lines, n = trace(
        "dev = qml.device('default.mixed', wires=1)\n"
        "@qml.qnode(dev)\n"
        "def circuit():\n"
        "    qml.BitFlip(0.25, wires=0)\n"
        "    return qml.density_matrix(wires=0)\n"
    )
    snap = geometry.snapshot(simulator.run_ops_trajectory(ops, lines, n).states[-1], n)
    assert snap["bloch"][0] == pytest.approx([0.0, 0.0, 0.5])


def test_missing_qnode_and_argument_errors():
    with pytest.raises(tracer.UserCodeError) as info:
        trace("x = 1\n")
    assert info.value.kind == "no_circuit"
    with pytest.raises(tracer.UserCodeError):
        trace("dev = qml.device('default.qubit', wires=1)\n@qml.qnode(dev)\ndef c(p):\n    qml.RX(p, 0)\n    return qml.state()\n", args=["params"])


def test_error_inside_qnode_points_to_the_line():
    with pytest.raises(tracer.UserCodeError) as info:
        trace(
            "dev = qml.device('default.qubit', wires=1)\n"
            "@qml.qnode(dev)\n"
            "def circuit():\n"
            "    qml.RX(0.1, wires=5)\n"
            "    return qml.state()\n"
        )
    assert info.value.line == 6


SANDBOX_QNODE = HEADER + (
    "dev = qml.device('default.qubit', wires=2)\n"
    "@qml.qnode(dev)\n"
    "def bell():\n"
    "    qml.Hadamard(0)\n"
    "    qml.CNOT(wires=[0, 1])\n"
    "    return qml.probs()\n"
)


def test_sandbox_runs_a_qnode_when_there_is_no_qiskit_circuit():
    from ket_lab_engine import worker

    result = worker.handle({"type": "run", "code": SANDBOX_QNODE})
    assert result["ok"], result
    assert [s["label"] for s in result["steps"]] == ["H", "X"]
    assert result["snapshots"][-1]["probabilities"] == pytest.approx([0.5, 0, 0, 0.5])

    shots = worker.handle({"type": "shots", "code": SANDBOX_QNODE, "shots": 400})
    assert set(shots["counts"]) == {"00", "11"}


def test_pennylane_lesson_runs_analysis_with_student_variables():
    from ket_lab_engine import worker

    code = SANDBOX_QNODE + "history = [1.0, 0.5, np.array(0.25)]\n"
    analysis = "def analyze(ns):\n    return {'values': ns['history'], 'n': len(ns['history'])}\n"
    result = worker.handle({"type": "run", "code": code, "framework": "pennylane", "qnode": {"name": "bell"}, "analysis": analysis})
    assert result["analysis"] == {"values": [1.0, 0.5, 0.25], "n": 3}

    broken = worker.handle({"type": "run", "code": code, "framework": "pennylane", "analysis": "def analyze(ns):\n    return ns['nope']\n"})
    assert broken["ok"] and "KeyError" in broken["analysis"]["error"]


def test_noisy_snapshots_have_no_amplitudes():
    from ket_lab_engine import worker

    code = HEADER + (
        "dev = qml.device('default.mixed', wires=1)\n"
        "@qml.qnode(dev)\n"
        "def circuit():\n"
        "    qml.Hadamard(0)\n"
        "    qml.PhaseDamping(0.5, wires=0)\n"
        "    return qml.density_matrix(0)\n"
    )
    result = worker.handle({"type": "run", "code": code, "framework": "pennylane"})
    last = result["snapshots"][-1]
    assert last["amplitudes"] is None
    assert last["bloch"][0][0] < 0.99 and last["state_purity"] < 1
