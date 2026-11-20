# Hidden setup for the lesson 2.2 challenge: only the table [f(0), f(1)]; the oracle is the learner's.
try:
    table = _KET_LAB_INPUT
    del _KET_LAB_INPUT
except NameError:
    table = [0, 1]
