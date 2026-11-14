"""Validação da lição 4.6: síndrome de uma cadeia de erros X no código tórico,
classe lógica de laços e distância (L = 3).

A referência usa vetores binários: cada plaqueta é um vetor sobre os 2L² qubits e
a síndrome é o produto com o vetor do erro, módulo 2.
"""

import random

import numpy as np


def index(L, edge):
    kind, r, c = edge
    return (0 if kind == "h" else L * L) + (r % L) * L + (c % L)


def plaquette_matrix(L):
    """Linha p = r·L + c: Z em h(r,c), h(r+1,c), v(r,c), v(r,c+1)."""
    rows = np.zeros((L * L, 2 * L * L), dtype=int)
    for r in range(L):
        for c in range(L):
            for edge in (("h", r, c), ("h", r + 1, c), ("v", r, c), ("v", r, c + 1)):
                rows[r * L + c, index(L, edge)] ^= 1
    return rows


def ref_defects(L, chain):
    e = np.zeros(2 * L * L, dtype=int)
    for edge in chain:
        e[index(L, edge)] ^= 1
    s = plaquette_matrix(L) @ e % 2
    return [(p // L, p % L) for p in range(L * L) if s[p]]


def star(L, r, c):
    return {("h", r, c), ("h", r, (c - 1) % L), ("v", r, c), ("v", (r - 1) % L, c)}


def all_edges(L):
    return [(t, r, c) for t in "hv" for r in range(L) for c in range(L)]


def short(chain):
    text = str(sorted(chain))
    return text if len(text) <= 110 else text[:107] + "..."


def fail(key, **params):
    return {"passed": False, "key": key, "params": params}


def as_pairs(value):
    return sorted((int(p[0]), int(p[1])) for p in value)


def defect_cases():
    rng = random.Random(7)
    for L in (3, 4):
        edges = all_edges(L)
        for e in edges:
            yield L, {e}
        for _ in range(12):
            yield L, set(rng.sample(edges, 2))
        for _ in range(25):
            yield L, set(rng.sample(edges, rng.randint(3, 7)))


def class_cases():
    for L in (3, 4):
        row = lambda r0: {("v", r0, c) for c in range(L)}  # laço horizontal no dual: classe (0, 1)
        col = lambda c0: {("h", r, c0) for r in range(L)}  # laço vertical no dual: classe (1, 0)
        yield L, set(), (0, 0)
        yield L, star(L, 0, 0), (0, 0)
        yield L, star(L, 1, 2) ^ star(L, 0, 1), (0, 0)
        yield L, star(L, 0, 0) ^ star(L, 0, 1) ^ star(L, 1, 1), (0, 0)
        yield L, row(0), (0, 1)
        yield L, row(1), (0, 1)
        yield L, col(0), (1, 0)
        yield L, col(2), (1, 0)
        yield L, row(1) | col(1), (1, 1)
        yield L, row(0) ^ star(L, 0, 0) ^ star(L, 1, 1), (0, 1)
        yield L, col(1) ^ star(L, 0, 1), (1, 0)


def check(ns, run_case):
    for name in ("defects", "logical_class"):
        if not callable(ns.get(name)):
            return fail("missing_function", name=name)
    defects, logical_class = ns["defects"], ns["logical_class"]

    for L, chain in defect_cases():
        expected = ref_defects(L, chain)
        got = as_pairs(defects(L, set(chain)))
        if got != expected:
            return fail("defects_wrong", L=L, chain=short(chain), expected=expected, got=got)

    for L, chain, expected in class_cases():
        assert not ref_defects(L, chain)
        got = tuple(int(x) for x in logical_class(L, set(chain)))
        if got != expected:
            return fail("class_wrong", L=L, chain=short(chain), expected=expected, got=got)

    if "distance" not in ns:
        return fail("missing", name="distance")
    distance = ns["distance"]
    if distance != 3:
        return fail("distance_wrong", got=distance)
    return {"passed": True, "key": "ok", "params": {"L": 3, "distance": 3}}
