"""Validação da lição 1.9 (codificação superdensa).

Para cada uma das quatro mensagens: (1) o circuito tem exatamente duas portas de
dois qubits, a que cria o par e a que inicia a decodificação; (2) Alice só atua
no qubit 1, entre as duas; (3) o par e a decodificação de Bob não dependem da
mensagem; (4) o resultado em |q1 q0⟩ é a mensagem.
"""

from qiskit import QuantumCircuit

from qlp_engine import simulator

MESSAGES = ["00", "01", "10", "11"]
TOLERANCE = 0.999


def signature(circuit, instructions):
    """Nome, qubits e parâmetros de cada instrução, ignorando barreiras e medições."""
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
