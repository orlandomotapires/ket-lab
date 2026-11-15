import numpy as np

ghz = [("h", 0), ("cx", 0, 1), ("cx", 1, 2)]


def fold(gates, scale):
    gates = list(gates)
    return gates + (gates[::-1] + gates) * ((scale - 1) // 2)


shots = 20000

# Assignment matrix: column j is the readout distribution of the prepared state j.
A = np.zeros((8, 8))
for prepared, counts in calibrate(shots).items():
    for read, n in counts.items():
        A[int(read, 2), int(prepared, 2)] = n / shots

SIGN = np.array([(-1) ** (int(format(i, "03b")[0]) + int(format(i, "03b")[2])) for i in range(8)])


def distribution(counts):
    p = np.zeros(8)
    for key, n in counts.items():
        p[int(key, 2)] = n / shots
    return p


def zz(p):
    return float(SIGN @ p)


def estimate(seed):
    scales = [1, 3, 5]
    values = [zz(np.linalg.solve(A, distribution(run_device(fold(ghz, s), shots, seed)))) for s in scales]
    return float(np.polyval(np.polyfit(scales, values, 1), 0))


raw = zz(distribution(run_device(ghz, shots, 0)))
mitigated = estimate(0)
sigma = float(np.std([estimate(seed) for seed in range(10)], ddof=1))
