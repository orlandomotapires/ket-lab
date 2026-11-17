# Hidden setup for lesson 1.9: Alice's message, two bits as a string "ab".
# The validator swaps the message (via _QLP_INPUT) to test all four.
try:
    message = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    message = "10"
