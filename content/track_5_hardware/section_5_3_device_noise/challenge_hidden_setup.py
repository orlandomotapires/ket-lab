import numpy as np

# Measurements on an idle qubit prepared in |+⟩: after each delay (in µs), the population of |1⟩
# and the size of the coherence |ρ01|, each with a little noise from the instrument.
delays = np.array([10.0, 25.0, 50.0, 75.0, 100.0, 150.0, 200.0])
_rng = np.random.default_rng(0)
p1_data = np.round(0.5 * np.exp(-delays / 120.0) + _rng.normal(0, 0.004, delays.size), 5)
coh_data = np.round(0.5 * np.exp(-delays / 70.0) + _rng.normal(0, 0.004, delays.size), 5)
