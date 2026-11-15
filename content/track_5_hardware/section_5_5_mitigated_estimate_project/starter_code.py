import numpy as np

# The device (hidden) provides:
#   run_device(gates, shots, seed)  counts such as {"000": 9021, "111": ...}, qubit 0 first
#   calibrate(shots)                {prepared bitstring: counts} for the 8 basis states
# Gates: ("h", q), ("x", q), ("cx", control, target); cx only between neighbours on the line 0-1-2.
# The exact value of <Z0 Z2> for the GHZ state is 1.

ghz = []  # gate list of the GHZ circuit


def fold(gates, scale):
    # scale = 1, 3, 5, ...: gates, then (reversed gates, gates) repeated (scale - 1) // 2 times.
    return list(gates)


shots = 20000

A = np.eye(8)  # assignment matrix from calibrate(shots)

raw = 0.0  # unmitigated <Z0 Z2> of ghz, run_device with seed 0
mitigated = 0.0  # readout mitigation at scales 1, 3, 5, then extrapolation to scale 0
sigma = 0.0  # standard deviation of the mitigated estimate over several seeds
