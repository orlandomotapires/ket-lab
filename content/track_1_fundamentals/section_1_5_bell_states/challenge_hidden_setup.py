# Setup oculto do desafio da lição 1.5: `bell` escolhe o estado de Bell (0 a 3).
try:
    bell = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    bell = 3
