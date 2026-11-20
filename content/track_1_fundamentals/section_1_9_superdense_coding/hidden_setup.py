# Hidden setup for lesson 1.9: Alice's message, two bits as a string "ab".
# The validator swaps the message (via _KET_LAB_INPUT) to test all four.
try:
    message = _KET_LAB_INPUT
    del _KET_LAB_INPUT
except NameError:
    message = "10"
