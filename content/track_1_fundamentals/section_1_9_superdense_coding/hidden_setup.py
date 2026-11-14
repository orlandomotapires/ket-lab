# Setup oculto da lição 1.9: a mensagem de Alice, dois bits como string "ab".
# O validador troca a mensagem (via _QLP_INPUT) para testar as quatro.
try:
    message = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    message = "10"
