# Setup oculto do desafio da lição 2.2: só a tabela [f(0), f(1)]; o oráculo é do aluno.
try:
    table = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    table = [0, 1]
