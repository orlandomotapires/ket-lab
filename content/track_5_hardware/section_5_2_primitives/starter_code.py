import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator, StatevectorSampler

# The Bell state (|00⟩ + |11⟩)/√2. Keep qc free of measurements.
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

# Estimator: one PUB is (circuit, observable). The result holds the expectation value in .data.evs.
estimator = StatevectorEstimator()
zz_est = float(estimator.run([(qc, SparsePauliOp("ZZ"))]).result()[0].data.evs)
xx_est = 0.0  # ⟨X⊗X⟩ with the Estimator

# Sampler: it only measures in the computational basis and returns counts.
shots = 4096
sampler = StatevectorSampler(default_shots=shots, seed=1)
zz_samp = 0.0  # ⟨Z⊗Z⟩ from counts
xx_samp = 0.0  # ⟨X⊗X⟩ from counts
z0_samp = 0.0  # ⟨Z⟩ of qubit 0 from counts (the exact value is 0)
sigma = 0.0  # statistical error of a Z expectation value from `shots` shots
