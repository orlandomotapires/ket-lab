# Idea: the Estimator returns ⟨O⟩ directly. The Sampler only measures in the Z basis, so for X we
# rotate with Hadamard gates first and turn the counts into ±1 averages by the parity of the bits.
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator, StatevectorSampler

# Bell state (|00⟩ + |11⟩)/√2, without measurements so the Estimator can use it.
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

# The Estimator takes the observable as part of the PUB and does any basis change internally.
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


# Z needs no rotation. For X, H X H = Z, so a Hadamard on each qubit before measuring turns X into Z.
z_circuit = qc.copy()
z_circuit.measure_all()
x_circuit = qc.copy()
x_circuit.h([0, 1])
x_circuit.measure_all()

counts_z = sampler.run([z_circuit]).result()[0].data.meas.get_counts()
counts_x = sampler.run([x_circuit]).result()[0].data.meas.get_counts()

# ZZ and XX use the parity of both bits; Z on qubit 0 uses bit 0 only, so its exact value is 0 plus shot noise.
zz_samp = expectation(counts_z, [0, 1])
xx_samp = expectation(counts_x, [0, 1])
z0_samp = expectation(counts_z, [0])
# An average of N results of ±1 has error 1/√N when the mean is 0.
sigma = 1 / np.sqrt(shots)
