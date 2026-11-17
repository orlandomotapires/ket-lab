# Idea: both decays are exponentials, so the logarithm of the data is a straight line in the delay
# and its slope is minus the decay rate. The pure dephasing rate is what T2 has beyond relaxation.
import numpy as np

# The population of |1⟩ is (1/2)·e^{-t/T1}: log p1 = log(1/2) − t/T1. The intercept absorbs the
# factor 1/2 by itself, so only the slope matters, and the rate is minus the slope.
rate_1 = -np.polyfit(delays, np.log(p1_data), 1)[0]
# The coherence |ρ01| is (1/2)·e^{-t/T2}, the same shape with the rate 1/T2.
rate_2 = -np.polyfit(delays, np.log(coh_data), 1)[0]
T1_fit = 1 / rate_1
T2_fit = 1 / rate_2

# Rates add, times do not: 1/T2 = 1/(2·T1) + 1/Tφ, so Tφ comes from the difference of rates.
Tphi_fit = 1 / (rate_2 - rate_1 / 2)
print(T1_fit, T2_fit, Tphi_fit)
