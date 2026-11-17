# Idea: when 8θ is not an integer the probability spreads over nearby outcomes. The estimate is
# still the most frequent one, and its probability is its count divided by the number of shots.
from qiskit import QuantumCircuit

qc = QuantumCircuit(4, 3)
# Eigenvector |1⟩ of U on qubit 3, counting qubits in |+⟩.
qc.x(3)
for qubit in range(3):
    qc.h(qubit)
# Controlled powers U^(2^j), then the inverse QFT, exactly as for an exact phase.
for j in range(3):
    apply_controlled_u(qc, j, 2**j)
inverse_qft(qc, [0, 1, 2])
qc.measure([0, 1, 2], [0, 1, 2])

# Many shots, so that the measured frequency of the best outcome is close to its probability.
counts = run_shots(qc, 4096)
best = max(counts, key=counts.get)
theta = int(best, 2) / 8
p_best = counts[best] / 4096
