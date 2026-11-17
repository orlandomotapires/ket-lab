# Idea: combine the two mitigations. Measure the GHZ correlator at folding scales 1, 3, 5, correct
# the readout at each scale with the inverse of A, extrapolate to scale 0, and repeat for the scatter.
import numpy as np

# The chain respects the line 0-1-2: H makes the superposition, each CNOT extends it to the next neighbor.
ghz = [("h", 0), ("cx", 0, 1), ("cx", 1, 2)]


def fold(gates, scale):
    # G (G† G)^k: every gate here is its own inverse, so G† is the reversed list.
    gates = list(gates)
    return gates + (gates[::-1] + gates) * ((scale - 1) // 2)


shots = 20000

# Assignment matrix: column j is the readout distribution of the prepared state j.
# Count keys write qubit 0 first, so int(key, 2) indexes rows and columns consistently.
A = np.zeros((8, 8))
for prepared, counts in calibrate(shots).items():
    for read, n in counts.items():
        A[int(read, 2), int(prepared, 2)] = n / shots

# Eigenvalue of Z0 Z2 for each bitstring: (-1)^(bit 0 + bit 2), with bit 0 the first character.
SIGN = np.array([(-1) ** (int(format(i, "03b")[0]) + int(format(i, "03b")[2])) for i in range(8)])


def distribution(counts):
    p = np.zeros(8)
    for key, n in counts.items():
        p[int(key, 2)] = n / shots
    return p


def zz(p):
    return float(SIGN @ p)


def estimate(seed):
    # Readout mitigation at each scale, then a straight line through the values read at scale 0.
    scales = [1, 3, 5]
    values = [zz(np.linalg.solve(A, distribution(run_device(fold(ghz, s), shots, seed)))) for s in scales]
    return float(np.polyval(np.polyfit(scales, values, 1), 0))


# The raw value skips both mitigations, so it is lowered by readout and gate noise.
raw = zz(distribution(run_device(ghz, shots, 0)))
mitigated = estimate(0)
# The spread over seeds is the statistical uncertainty of one run; the inversion and the
# extrapolation amplify shot noise, so it exceeds 1/√shots.
sigma = float(np.std([estimate(seed) for seed in range(10)], ddof=1))
