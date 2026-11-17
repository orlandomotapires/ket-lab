# Idea: build U_f from the truth table. A constant f needs at most an X on the auxiliary qubit,
# a balanced f copies x with a CNOT and flips the result when f(0) = 1.
from qiskit import QuantumCircuit

f0, f1 = table

qc = QuantumCircuit(2)
# Same preparation as Deutsch's circuit: auxiliary qubit in |−⟩, input in |+⟩.
qc.x(1)
qc.h(1)
qc.h(0)

# Oracle U_f: |x⟩|y⟩ -> |x⟩|y ⊕ f(x)⟩
# Constant f: y ⊕ f(0) does not depend on x, so only an X (when f(0) = 1) is needed.
if f0 == f1:
    if f0:
        qc.x(1)
else:
    # Balanced f: y ⊕ x is a CNOT, and y ⊕ NOT x adds an X on the auxiliary qubit.
    qc.cx(0, 1)
    if f0:
        qc.x(1)

# Final Hadamard on the input: interference gives |0⟩ for constant, |1⟩ for balanced.
qc.h(0)
