# Hidden setup for the lesson 1.5 challenge: `bell` picks the state (0 to 3: Bell; 4 and 5: product, with qubit order).
try:
    bell = _KET_LAB_INPUT
    del _KET_LAB_INPUT
except NameError:
    bell = 3
