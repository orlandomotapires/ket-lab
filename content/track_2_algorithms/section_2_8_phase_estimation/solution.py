# Idea: controlled powers of U write the phase θ into the counting register as a QFT of |2³θ⟩,
# so the inverse QFT turns it into the integer m = 8θ, which we read by measuring.
from qiskit import QuantumCircuit

qc = QuantumCircuit(4, 3)
# |1⟩ is the eigenvector of U with eigenvalue e^{2πiθ}, the phase we want to estimate.
qc.x(3)
# Counting qubits in |+⟩, so that phase kickback shows up as relative phases on them.
for qubit in range(3):
    qc.h(qubit)
# Counting qubit j controls U^(2^j) and receives the relative phase e^{2πi·2^j·θ}.
for j in range(3):
    apply_controlled_u(qc, j, 2**j)
# The counting register is now the QFT of |8θ⟩; the inverse QFT turns the phases back into bits.
inverse_qft(qc, [0, 1, 2])
qc.measure([0, 1, 2], [0, 1, 2])

counts = run_shots(qc)
# The most frequent result is the best integer m, and θ ≈ m/8.
best = max(counts, key=counts.get)
theta = int(best, 2) / 8
