# Idea: the Sampler measures only in the Z basis, so each letter of the label is turned into a Z
# measurement by a gate on its qubit, and the estimate is the average of (-1)^(parity of the bits
# on the qubits that carry X, Y or Z).
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def pauli_from_counts(qc, pauli, sampler):
    n = qc.num_qubits
    circuit = qc.copy()  # the caller's circuit stays free of measurements
    measured = []
    for position, letter in enumerate(pauli):
        qubit = n - 1 - position  # Qiskit labels put qubit 0 on the right
        if letter == "I":
            continue  # this qubit does not enter the product
        measured.append(qubit)
        if letter == "Y":
            # S† maps the Y eigenstates (|0⟩ ± i|1⟩)/√2 onto (|0⟩ ± |1⟩)/√2; H then maps them to |0⟩, |1⟩.
            circuit.sdg(qubit)
        if letter in "XY":
            # H X H = Z, so after H a Z measurement reads X (or Y, after S†).
            circuit.h(qubit)
    circuit.measure_all()
    counts = sampler.run([circuit]).result()[0].data.meas.get_counts()
    # Each outcome counts +1 for an even number of 1s on the measured qubits and −1 for an odd number.
    total = sum(counts.values())
    signed = sum(n_ * (-1) ** sum(int(bits[-1 - q]) for q in measured) for bits, n_ in counts.items())
    return signed / total


qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

# Testing on the Bell state: ⟨YY⟩ = −1 and ⟨XY⟩ = 0, up to shot noise.
print(pauli_from_counts(qc, "YY", StatevectorSampler(default_shots=4096, seed=1)))
print(pauli_from_counts(qc, "XY", StatevectorSampler(default_shots=4096, seed=1)))
