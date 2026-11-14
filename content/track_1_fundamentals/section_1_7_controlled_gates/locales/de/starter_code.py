from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
prepare_input(qc)  # eine Zwei-Qubit-Eingabe, du weißt nicht welche

# Deine Aufgabe: Baue das kontrollierte S-Gatter (CS = diag(1, 1, 1, i)) nur
# mit cx, t und tdg. Die 90°-Phase darf nur erscheinen, wenn beide Qubits 1 sind.
