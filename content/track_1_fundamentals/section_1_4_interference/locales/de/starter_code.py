from qiskit import QuantumCircuit

qc = QuantumCircuit(1, 1)
prepare_unknown(qc)  # |+⟩ oder |−⟩, du weißt nicht welcher

# Deine Aufgabe: Füge Gatter und eine Messung hinzu, sodass |+⟩ immer 0
# und |−⟩ immer 1 liefert.
