"""Validation for lesson 6.4: minor embedding of the triangle problem on a square.

The check builds the reference embedding and the brute force itself. It reads the
learner's embed(F) and tests it against the reference, then compares the lists."""

import itertools
import math

H = [1 / 3, 2 / 3, 1]
J = {(0, 1): 1 / 6, (0, 2): 1 / 4, (1, 2): 1 / 2}
EDGES = {(0, 1), (1, 2), (2, 3), (0, 3)}
F_VALUES = [0.1, 0.2, 0.4, 0.8]
TOL = 1e-9


def ref_embed(F):
    fields = [H[0], H[1], H[2], 0.0]
    coup = {(0, 1): J[(0, 1)], (1, 2): J[(1, 2)], (0, 3): J[(0, 2)], (2, 3): -F}
    return fields, coup


def ref_energy(s, fields, coup):
    return sum(c * s[i] * s[j] for (i, j), c in coup.items()) + sum(f * x for f, x in zip(fields, s))


def ref_ground(F):
    fields, coup = ref_embed(F)
    states = sorted(itertools.product([1, -1], repeat=4), key=lambda s: ref_energy(s, fields, coup))
    low = ref_energy(states[0], fields, coup)
    return [s for s in states if ref_energy(s, fields, coup) < low + 1e-9], low


def fail(key, **params):
    return {"passed": False, "key": key, "params": params}


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def normalize(couplings):
    """Return {(i, j): value} with i < j, from a dict or a 4x4 array; None if not readable."""
    out = {}
    try:
        if isinstance(couplings, dict):
            for (i, j), v in couplings.items():
                i, j = int(i), int(j)
                if i == j or not (0 <= i < 4 and 0 <= j < 4):
                    return None
                key = (min(i, j), max(i, j))
                out[key] = out.get(key, 0.0) + float(v)
        else:
            for i in range(4):
                for j in range(4):
                    v = float(couplings[i][j])
                    if i == j:
                        if abs(v) > TOL:
                            return None
                    elif v != 0:
                        key = (min(i, j), max(i, j))
                        out[key] = out.get(key, 0.0) + v
    except Exception:
        return None
    return out


def check(ns, run_case):
    if not callable(ns.get("embed")):
        return fail("missing_function", name="embed")

    # Test the learner's embedding for several chain strengths.
    for F in (0.1, 0.5, 1.0, 2.0):
        res = None
        try:
            res = ns["embed"](F)
            fields, couplings = res
            fields = [float(x) for x in fields]
        except Exception:
            return fail("embed_shape", F=F, got=repr(res))
        coup = normalize(couplings)
        if len(fields) != 4 or coup is None:
            return fail("embed_shape", F=F, got=repr(res))

        for pair, v in coup.items():
            if pair not in EDGES and abs(v) > TOL:
                return fail("bad_edge", pair=f"{pair[0]}–{pair[1]}")

        chain = coup.get((2, 3), 0.0)
        if abs(chain - F) < TOL and abs(F) > TOL:
            return fail("chain_sign")
        if abs(chain + F) > TOL:
            return fail("chain_value", got=round(chain, 6), F=F)

        if abs(fields[2] - H[2]) < TOL and abs(fields[3] - H[2]) < TOL:
            return fail("field_twice")
        if abs(fields[2] + fields[3] - H[2]) < TOL and abs(fields[3]) > TOL:
            return fail("field_split")
        want_fields, want_coup = ref_embed(F)
        if any(abs(a - b) > TOL for a, b in zip(fields, want_fields)):
            return fail("field_wrong", got=[round(x, 4) for x in fields], F=F)

        for pair in ((0, 1), (1, 2), (0, 3)):
            if abs(coup.get(pair, 0.0) - want_coup[pair]) > TOL:
                return fail("coupling_wrong", pair=f"{pair[0]}–{pair[1]}",
                            got=round(coup.get(pair, 0.0), 6), want=round(want_coup[pair], 6))

    for name in ("chain_intact", "decoded", "F_min"):
        if name not in ns:
            return fail("missing", name=name)

    try:
        intact = list(ns["chain_intact"])
        dec = list(ns["decoded"])
    except TypeError:
        return fail("missing", name="chain_intact")
    if len(intact) != len(F_VALUES) or len(dec) != len(F_VALUES):
        return fail("intact_wrong", F=F_VALUES, got=intact, want="one entry per F in F_values")

    want_min = None
    broken_F = []
    energy_min = None
    for k, F in enumerate(F_VALUES):
        grounds, low = ref_ground(F)
        # Chain intact only if every lowest state has an intact chain; mixed ties do not occur here.
        want_intact = all(g[2] == g[3] for g in grounds)
        if bool(intact[k]) != want_intact:
            return fail("intact_wrong", F=F, got=bool(intact[k]),
                        want="intact" if want_intact else "broken")
        if want_intact:
            want_dec = grounds[0][:3]
            if dec[k] is None:
                return fail("decoded_wrong", F=F, got=None, want=want_dec)
            try:
                got = tuple(int(round(float(x))) for x in dec[k])
            except (TypeError, ValueError):
                return fail("decoded_wrong", F=F, got=dec[k], want=want_dec)
            if got != want_dec:
                return fail("decoded_wrong", F=F, got=got, want=want_dec)
            if want_min is None and want_dec == (1, -1, -1):
                want_min = F
                energy_min = low
        else:
            broken_F.append(F)
            if dec[k] is not None:
                return fail("decoded_wrong", F=F, got=dec[k], want=None)

    got_min = num(ns["F_min"])
    if got_min is None or want_min is None or abs(got_min - want_min) > TOL:
        return fail("fmin_wrong", got=ns["F_min"], want=want_min)

    return {"passed": True, "key": "ok",
            "params": {"broken": broken_F[0] if broken_F else "none", "F_min": want_min,
                       "energy": round(energy_min, 4)}}
