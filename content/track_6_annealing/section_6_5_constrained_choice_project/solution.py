# Idea: write the constraint as a penalty in a QUBO, check the QUBO against the cost on all 16
# choices, find the smallest weight that makes the feasible optimum the ground state, turn the QUBO
# into an Ising model with s = 1 - 2x, anneal it with the evolution of lesson 6.2, and decode.
import itertools
import numpy as np

v = [5, 4, 3, 2]
conflicts = [(0, 1), (1, 2)]
B = 6
A_used = 4
A_big = 20
penalties = [0.5, 1, 1.5, 2, 2.5, 3, 4, 6]
T_values = [5, 20, 80]
n = 4
choices = list(itertools.product([0, 1], repeat=n))


def cost(x, A):
    # The definition of the problem: the objective plus the two penalty terms.
    count = sum(x)
    conflict = sum(x[i] * x[j] for i, j in conflicts)
    return -sum(vi * xi for vi, xi in zip(v, x)) + A * (count - 2) ** 2 + B * conflict


def qubo(A):
    # A (sum x - 2)^2 = A (sum x_i^2 + 2 sum_{i<j} x_i x_j - 4 sum x_i + 4), and x^2 = x,
    # so the diagonal gets A (1 - 4) = -3A, every pair gets 2A, and the constant is 4A.
    Q = np.zeros((n, n))
    for i in range(n):
        Q[i, i] = -v[i] - 3 * A
        for j in range(i + 1, n):
            Q[i, j] = 2 * A
    # A conflicting pair pays B only when both jobs run, which is a product x_i x_j.
    for i, j in conflicts:
        Q[i, j] += B
    return Q, 4 * A


Q, offset = qubo(A_used)

# Brute force over the 16 choices; feasible means exactly two jobs and no conflicting pair.
feasible = [x for x in choices if sum(x) == 2 and all(x[i] * x[j] == 0 for i, j in conflicts)]
best = min(feasible, key=lambda x: -sum(vi * xi for vi, xi in zip(v, x)))
best_jobs = [i for i in range(n) if best[i]]
best_value = sum(v[i] for i in best_jobs)


def is_ground(A):
    # The minimum must be reached by the feasible optimum alone: a tie is not enough,
    # because the anneal would then end on either state.
    energies = sorted((cost(x, A), x) for x in choices)
    return energies[0][1] == best and energies[1][0] > energies[0][0] + 1e-9


A_min = min(A for A in penalties if is_ground(A))


def ising(Q, offset):
    # With x = (1 - s) / 2: a diagonal term Q_ii x_i gives -Q_ii/2 s_i + Q_ii/2, and a pair term
    # Q_ij x_i x_j gives Q_ij/4 (s_i s_j - s_i - s_j + 1).
    h = np.zeros(n)
    J = np.zeros((n, n))
    const = offset
    for i in range(n):
        h[i] -= Q[i, i] / 2
        const += Q[i, i] / 2
        for j in range(i + 1, n):
            J[i, j] = Q[i, j] / 4
            h[i] -= Q[i, j] / 4
            h[j] -= Q[i, j] / 4
            const += Q[i, j] / 4
    return h, J, const


h, J, const = ising(Q, offset)

I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]])
Z = np.diag([1, -1])


def on(op, q):
    # Qiskit order: qubit 0 is the rightmost factor of the tensor product.
    factors = [I2] * n
    factors[q] = op
    m = factors[n - 1]
    for k in range(n - 2, -1, -1):
        m = np.kron(m, factors[k])
    return m


H_B = -sum(on(X, i) for i in range(n))


def problem_hamiltonian(h, J):
    H = sum(h[i] * on(Z, i) for i in range(n))
    for i in range(n):
        for j in range(i + 1, n):
            H = H + J[i, j] * on(Z, i) @ on(Z, j)
    # Dividing by the largest coefficient mimics hardware, whose couplings have a fixed range.
    return H / max(np.abs(h).max(), np.abs(J).max())


def anneal(H_P, T, steps=400):
    psi = np.ones(2**n, dtype=complex) / 2**(n / 2)
    for k in range(steps):
        # Midpoint rule: the Hamiltonian is frozen at the middle of each short step.
        s = (k + 0.5) / steps
        w, V = np.linalg.eigh((1 - s) * H_B + s * H_P)
        psi = V @ (np.exp(-1j * w * T / steps) * (V.conj().T @ psi))
    return np.abs(psi) ** 2


target = sum(1 << i for i in best_jobs)  # job i is bit i of the basis index
H_P = problem_hamiltonian(h, J)
success = [anneal(H_P, T)[target] for T in T_values]

# The oversized weight needs its own QUBO and Ising model, then the same anneal.
h_big, J_big, _ = ising(*qubo(A_big))
H_big = problem_hamiltonian(h_big, J_big)
success_big = [anneal(H_big, T)[target] for T in T_values]

# Decode the most probable basis state at the longest time: bit i = 1 means job i runs.
final = int(np.argmax(anneal(H_P, T_values[-1])))
jobs = [i for i in range(n) if (final >> i) & 1]
