from qiskit import QuantumCircuit

qc = QuantumCircuit(1)
prepare_input(qc)  # ein unbekannter Zustand auf Qubit 0

# Eine Gatterfolge wurde bereits angewendet:
qc.x(0)
qc.h(0)
qc.s(0)
qc.t(0)
qc.h(0)

# Deine Aufgabe: Hänge Gatter an, damit das Qubit in seinen Eingangszustand
# zurückkehrt, egal welcher es ist.
