# Setup oculto da lição 1.11: final_state(circuit, seed=0) devolve o vetor de estado
# final de UMA execução do circuito (medições no meio, portas condicionadas por
# if_test), como qiskit.quantum_info.Statevector. A seed escolhe o ramo de medição.
def _criar_final_state():
    import numpy as _np
    from qiskit.quantum_info import Statevector as _Statevector

    def _aplicar(estado, circuito, qubits, bits, clbits, rng):
        indice = {q: i for i, q in enumerate(circuito.qubits)}
        indice_cl = {c: i for i, c in enumerate(circuito.clbits)}
        for item in circuito.data:
            nome = item.operation.name
            alvo = [qubits[indice[q]] for q in item.qubits]
            if nome == "barrier":
                continue
            if nome == "measure":
                prob1 = float(_np.real(estado.probabilities([alvo[0]])[1]))
                resultado = int(rng.random() < prob1)
                projetor = _np.diag([1 - resultado, resultado]).astype(complex)
                estado = estado.evolve(projetor, alvo)
                estado = _Statevector(estado.data / _np.linalg.norm(estado.data))
                bits[clbits[indice_cl[item.clbits[0]]]] = resultado
            elif nome == "if_else":
                alvo_cl, valor = item.operation.condition
                bit = alvo_cl if not hasattr(alvo_cl, "__iter__") else alvo_cl[0]
                if bits[clbits[indice_cl[bit]]] == valor:
                    corpo = item.operation.blocks[0]
                    estado = _aplicar(estado, corpo, alvo, bits,
                                      [clbits[indice_cl[c]] for c in item.clbits], rng)
            else:
                estado = estado.evolve(item.operation, alvo)
        return estado

    def final_state(circuit, seed=0):
        """Estado final de uma execução; a seed escolhe os resultados das medições."""
        rng = _np.random.default_rng(seed)
        bits = [0] * circuit.num_clbits
        estado = _Statevector.from_label("0" * circuit.num_qubits)
        return _aplicar(estado, circuit, list(range(circuit.num_qubits)), bits,
                        list(range(circuit.num_clbits)), rng)

    return final_state


final_state = _criar_final_state()
del _criar_final_state
