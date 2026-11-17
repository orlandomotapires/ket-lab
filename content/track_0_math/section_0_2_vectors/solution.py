# Idea: np.vdot is the inner product with the conjugation on the first vector. Norms, probabilities
# and expansion coefficients in an orthonormal basis are all built from it.
import numpy as np

v = np.array([1 + 1j, 1 - 1j])
a = np.array([1, 1j]) / np.sqrt(2)
b = np.array([1, 1]) / np.sqrt(2)
plus = np.array([1, 1]) / np.sqrt(2)
psi = np.array([0.6, 0.8j])
phi_plus = np.array([1, 0, 0, 1]) / np.sqrt(2)
q = np.array([1, 1, 1, 1]) / 2

# ‖v‖ = √(Σ|vₖ|²) = √4 = 2.
norm = np.linalg.norm(v)
# Dividing by the norm gives a vector of norm 1, a valid state.
v_hat = v / norm
# ⟨a|b⟩ = Σ aₖ* bₖ: vdot conjugates the first argument, np.dot would not.
inner = np.vdot(a, b)
# The probability of finding |a⟩ in |b⟩ is the squared modulus of the inner product.
prob = abs(inner) ** 2
# |−⟩ = (|0⟩ − |1⟩)/√2: flipping the sign of the second entry makes ⟨+|−⟩ = 0, and 1/√2 keeps norm 1.
minus = np.array([1, -1]) / np.sqrt(2)
# Expansion coefficient c_k = ⟨e_k|ψ⟩ in the ± basis; the basis vector is the conjugated one.
amp_plus = np.vdot(plus, psi)
amp_minus = np.vdot(minus, psi)
# The same formula holds in C⁴, now with four entries per vector.
inner4 = np.vdot(phi_plus, q)
