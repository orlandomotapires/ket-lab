from qiskit import QuantumCircuit

qc = QuantumCircuit(1, 1)
prepare_unknown(qc)  # |+⟩ ou |−⟩, você não sabe qual

# Sua missão: acrescente portas e uma medição para que |+⟩ dê sempre 0
# e |−⟩ dê sempre 1.
