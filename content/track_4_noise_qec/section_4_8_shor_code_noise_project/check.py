"""Validação do projeto 4.8 (código de Shor sob ruído): rubrica com cinco critérios.

1. decodificador: qubit 0 volta a |ψ⟩ após X, Y ou Z em qualquer um dos nove qubits;
2. logical_pauli concorda com a referência em muitos padrões de erro;
3. logical_failure(p) concorda com a enumeração exata dos 4^9 padrões;
4. logical_failure(p) < bare_failure(p) para p pequeno;
5. p_star perto do cruzamento exato.
A referência calcula o Pauli lógico por propagação clássica dos bits X e Z e conta os
padrões que falham por peso, o que dá p_L(p) = soma_w N_w (p/3)^w (1-p)^(9-w).
"""

import itertools

import numpy as np

from qlp_engine import pl, simulator

INPUTS = [(1.1, 0.7), (2.4, -1.3)]
TOLERANCE = 0.999
P_VALUES = [0.005, 0.02, 0.05, 0.1, 0.3]
P_SMALL = [0.001, 0.01, 0.03, 0.05]
VALUE_TOLERANCE = 1e-6
CROSSOVER_TOLERANCE = 0.003
BLOCKS = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
LETTERS = "IXYZ"


def reference_pauli(error):
    """Pauli lógico para um padrão de erro (lista de nove letras)."""
    x = [c in "XY" for c in error]
    z = [c in "YZ" for c in error]
    leader_x, leader_z = [], []
    for block in BLOCKS:
        leader_x.append(sum(x[q] for q in block) >= 2)  # voto interno falha: X no líder
        leader_z.append(sum(z[q] for q in block) % 2 == 1)  # Z em qualquer qubit chega ao líder
    logical_z = sum(leader_x) % 2 == 1  # X em um líder (base +/−) é um Z lógico
    logical_x = sum(leader_z) >= 2  # o voto entre líderes erra
    return {
        (False, False): "I", (True, False): "X", (False, True): "Z", (True, True): "Y"}[(logical_x, logical_z)]


def failing_counts():
    """N_w: quantos dos 4^9 padrões de peso w deixam um Pauli lógico diferente de I."""
    counts = [0] * 10
    for pattern in itertools.product(LETTERS, repeat=9):
        if reference_pauli(pattern) != "I":
            counts[sum(c != "I" for c in pattern)] += 1
    return counts


_COUNTS = []


def reference_failure(p):
    if not _COUNTS:
        _COUNTS.extend(failing_counts())
    return sum(n * (p / 3) ** w * (1 - p) ** (9 - w) for w, n in enumerate(_COUNTS))


def reference_crossover():
    low, high = 0.02, 0.2
    for _ in range(60):
        mid = (low + high) / 2
        if reference_failure(mid) < mid:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def qubit0_state(state, n):
    if state.ndim == 2:
        tensor = state.reshape((2,) * (2 * n))
        axes = "abcdefghi"[: n - 1]
        return np.einsum(f"{axes}x{axes}y->xy", tensor)
    matrix = state.reshape(-1, 2)
    return matrix.T @ matrix.conj()


def fidelity(run_case, theta, phi, error):
    ns = run_case({"input": [theta, phi], "error": error})
    ops, lines, n = pl.trace_qnode(ns.get("circuit"), [])
    state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    psi = np.array([np.cos(theta / 2) * np.exp(-1j * phi / 2), np.sin(theta / 2) * np.exp(1j * phi / 2)])
    return float(np.real(psi.conj() @ qubit0_state(state, n) @ psi))


def number(value):
    try:
        return float(np.real(value))
    except (TypeError, ValueError):
        return None


def patterns():
    rng = np.random.default_rng(7)
    fixed = ["XXIIIIIII", "ZIIZIIIII", "XIIZIIIII", "YYIIIIIII", "ZZIIIIIII", "XIIXIIIII", "IIIIIIZZZ", "ZIIZIIZII", "IIXIIXIIX"]
    found = [list(f) for f in fixed]
    for _ in range(40):
        weight = int(rng.integers(1, 5))
        pattern = ["I"] * 9
        for q in rng.choice(9, size=weight, replace=False):
            pattern[int(q)] = "XYZ"[int(rng.integers(3))]
        found.append(pattern)
    return found


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "no_circuit"}
    _, _, n = pl.trace_qnode(circuit, [])
    if n != 9:
        return {"passed": False, "key": "wrong_qubits", "params": {"count": n}}
    for theta, phi in INPUTS:
        for error in ["none"] + [f"{kind}{q}" for kind in "xyz" for q in range(9)]:
            f = fidelity(run_case, theta, phi, error)
            if f < TOLERANCE:
                return {"passed": False, "key": "decoder", "params": {"error": error.upper(), "fidelity": f}}
    for name in ("logical_pauli", "logical_failure", "bare_failure"):
        if not callable(ns.get(name)):
            return {"passed": False, "key": "missing", "params": {"name": name}}
    for pattern in patterns():
        try:
            actual = ns["logical_pauli"](list(pattern))
        except Exception:  # noqa: BLE001
            actual = None
        expected = reference_pauli(pattern)
        if actual != expected:
            return {"passed": False, "key": "model", "params": {"pattern": "".join(pattern), "actual": actual, "expected": expected}}
    for p in P_VALUES:
        actual, expected = number(ns["logical_failure"](p)), reference_failure(p)
        if actual is None or abs(actual - expected) > VALUE_TOLERANCE:
            return {"passed": False, "key": "values", "params": {"p": p, "actual": actual, "expected": expected}}
    for p in P_SMALL:
        actual, bare = number(ns["logical_failure"](p)), number(ns["bare_failure"](p))
        if bare is None or actual is None or not actual < bare:
            return {"passed": False, "key": "below", "params": {"p": p, "actual": actual, "bare": bare}}
    expected = reference_crossover()
    actual = number(ns.get("p_star"))
    if actual is None or abs(actual - expected) > CROSSOVER_TOLERANCE:
        return {"passed": False, "key": "crossover", "params": {"actual": actual, "expected": expected}}
    return {"passed": True, "key": "ok", "params": {"p_star": actual, "reference": expected}}
