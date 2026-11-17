from qiskit import QuantumCircuit

# Qubits 0 to 2: input register. Qubits 3 to 5: output register.
# Three classical bits receive the measurement of the input register.
qc = QuantumCircuit(6, 3)

# Hadamard on the input register.

oracle(qc)  # f(x) = f(y) if and only if y = x or y = x ⊕ s, with s hidden

# Hadamard on the input register again, then measure qubits 0 to 2 into bits 0 to 2.

counts = run_shots(qc)  # {"y2y1y0": number of times}

# Every outcome y satisfies y·s = 0 (mod 2). Find s from the outcomes.
s_found = "000"
