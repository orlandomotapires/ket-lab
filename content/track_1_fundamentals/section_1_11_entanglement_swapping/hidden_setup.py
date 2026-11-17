# Hidden setup for lesson 1.11: final_state(circuit, seed=0) returns the final
# state vector of ONE run of the circuit (mid-circuit measurements, gates
# conditioned by if_test), as qiskit.quantum_info.Statevector. The seed picks the
# measurement branch.
def _build_final_state():
    import numpy as _np
    from qiskit.quantum_info import Statevector as _Statevector

    def _apply(state, sub_circuit, qubits, bits, clbits, rng):
        qubit_index = {q: i for i, q in enumerate(sub_circuit.qubits)}
        clbit_index = {c: i for i, c in enumerate(sub_circuit.clbits)}
        for item in sub_circuit.data:
            name = item.operation.name
            target = [qubits[qubit_index[q]] for q in item.qubits]
            if name == "barrier":
                continue
            if name == "measure":
                prob1 = float(_np.real(state.probabilities([target[0]])[1]))
                outcome = int(rng.random() < prob1)
                projector = _np.diag([1 - outcome, outcome]).astype(complex)
                state = state.evolve(projector, target)
                state = _Statevector(state.data / _np.linalg.norm(state.data))
                bits[clbits[clbit_index[item.clbits[0]]]] = outcome
            elif name == "if_else":
                target_cl, value = item.operation.condition
                bit = target_cl if not hasattr(target_cl, "__iter__") else target_cl[0]
                if bits[clbits[clbit_index[bit]]] == value:
                    body = item.operation.blocks[0]
                    state = _apply(state, body, target, bits,
                                   [clbits[clbit_index[c]] for c in item.clbits], rng)
            else:
                state = state.evolve(item.operation, target)
        return state

    def final_state(circuit, seed=0):
        """Final state of one run; the seed picks the measurement outcomes."""
        rng = _np.random.default_rng(seed)
        bits = [0] * circuit.num_clbits
        state = _Statevector.from_label("0" * circuit.num_qubits)
        return _apply(state, circuit, list(range(circuit.num_qubits)), bits,
                       list(range(circuit.num_clbits)), rng)

    return final_state


final_state = _build_final_state()
del _build_final_state
