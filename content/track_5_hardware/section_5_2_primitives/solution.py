import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator, StatevectorSampler

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

estimator = StatevectorEstimator()
zz_est = float(estimator.run([(qc, SparsePauliOp("ZZ"))]).result()[0].data.evs)
xx_est = float(estimator.run([(qc, SparsePauliOp("XX"))]).result()[0].data.evs)

shots = 4096
sampler = StatevectorSampler(default_shots=shots, seed=1)


def expectation(counts, qubits):
    # Each outcome contributes (-1)^(sum of the measured bits on `qubits`).
    total = sum(counts.values())
    signed = 0
    for bits, n in counts.items():
        parity = sum(int(bits[-1 - q]) for q in qubits)  # bits[-1] is qubit 0
        signed += n * (-1) ** parity
    return signed / total


# To measure X, rotate each qubit into the Z basis with a Hadamard gate first.
z_circuit = qc.copy()
z_circuit.measure_all()
x_circuit = qc.copy()
x_circuit.h([0, 1])
x_circuit.measure_all()

counts_z = sampler.run([z_circuit]).result()[0].data.meas.get_counts()
counts_x = sampler.run([x_circuit]).result()[0].data.meas.get_counts()

zz_samp = expectation(counts_z, [0, 1])
xx_samp = expectation(counts_x, [0, 1])
z0_samp = expectation(counts_z, [0])
sigma = 1 / np.sqrt(shots)
