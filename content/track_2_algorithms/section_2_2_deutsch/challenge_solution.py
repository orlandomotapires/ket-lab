from qiskit import QuantumCircuit

f0, f1 = table

qc = QuantumCircuit(2)
qc.x(1)
qc.h(1)
qc.h(0)

# Oracle U_f: |x⟩|y⟩ -> |x⟩|y ⊕ f(x)⟩
if f0 == f1:
    if f0:
        qc.x(1)
else:
    qc.cx(0, 1)
    if f0:
        qc.x(1)

qc.h(0)
