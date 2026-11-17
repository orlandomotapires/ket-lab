"""Validation for lesson 1.9 (superdense coding).

For each of the four messages: (1) the circuit has exactly two
two-qubit gates, the one that creates the pair and the one that starts the
decoding; (2) Alice acts only on qubit 1, between the two; (3) the pair and
Bob's decoding do not depend on the message; (4) the result in |q1 q0⟩ is the
message.
"""

from qiskit import QuantumCircuit

from qlp_engine import simulator

MESSAGES = ["00", "01", "10", "11"]
TOLERANCE = 0.999


def signature(circuit, instructions):
    """Name, qubits and parameters of each instruction, ignoring barriers and measurements."""
    result = []
    for item in instructions:
        name = item.operation.name
        if name in ("barrier", "measure"):
            continue
        qubits = tuple(circuit.find_bit(q).index for q in item.qubits)
        params = tuple(round(float(p), 9) for p in item.operation.params if isinstance(p, (int, float)))
        result.append((name, qubits, params))
    return result


def check(ns, run_case):
    reference = None
    for message in MESSAGES:
        circuit = run_case(message).get("qc")
        if not isinstance(circuit, QuantumCircuit) or circuit.num_qubits != 2:
            return {"passed": False, "key": "wrong_size"}
        data = list(circuit.data)
        two_qubit = [i for i, item in enumerate(data) if len(item.qubits) == 2 and item.operation.name != "barrier"]
        if len(two_qubit) != 2:
            return {"passed": False, "key": "gate_count", "params": {"count": len(two_qubit)}}
        first, second = two_qubit
        pair, alice, bob = data[: first + 1], data[first + 1 : second], data[second:]
        if any(qubit != (1,) for _, qubit, _ in signature(circuit, alice)):
            return {"passed": False, "key": "alice_local"}
        fixed = (signature(circuit, pair), signature(circuit, bob))
        if reference is None:
            reference = fixed
        elif fixed != reference:
            return {"passed": False, "key": "protocol_fixed", "params": {"message": message}}
        distribution = simulator.register_distribution(circuit, [0, 1])
        if distribution.get(message, 0.0) < TOLERANCE:
            observed = max(distribution, key=distribution.get)
            return {"passed": False, "key": "wrong_message", "params": {"message": message, "observed": observed}}
    return {"passed": True, "key": "ok"}
