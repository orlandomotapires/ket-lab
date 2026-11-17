import numpy as np

# 3-qubit device on a line (0-1-2) with hidden noise:
#   depolarizing after each gate (1 qubit: 0.01; 2 qubits: 0.03), which grows with folding;
#   readout error per qubit: P(1|0) = 0.02, P(0|1) = 0.06.
# Accepted gates: ("h", q), ("x", q), ("cx", control, target), with cx only between neighbors.
# Count labels write qubit 0 on the left ("q0 q1 q2"), unlike Qiskit.
_P1, _P2 = 0.01, 0.03
_READ = np.array([[0.98, 0.06], [0.02, 0.94]])  # _READ[i, j] = P(ler i | verdadeiro j)
_MAX_SHOTS = 200000


def _unitary(gate):
    h = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    x = np.array([[0, 1], [1, 0]])
    eye = np.eye(2)
    kind = gate[0]
    if kind in ("h", "x"):
        q = gate[1]
        ops = [eye, eye, eye]
        ops[q] = h if kind == "h" else x
        return np.kron(np.kron(ops[0], ops[1]), ops[2]).astype(complex), (q,)
    if kind == "cx":
        c, t = gate[1], gate[2]
        if abs(c - t) != 1:
            raise ValueError(f"cx({c}, {t}): the qubits are not neighbours on the line 0-1-2")
        u = np.zeros((8, 8), dtype=complex)
        for i in range(8):
            bits = [(i >> 2) & 1, (i >> 1) & 1, i & 1]
            if bits[c]:
                bits[t] ^= 1
            u[(bits[0] << 2) | (bits[1] << 1) | bits[2], i] = 1
        return u, (c, t)
    raise ValueError(f"unknown gate {gate!r}")


def _depolarize(rho, qubits, p):
    """rho -> (1 - p) rho + p Tr_qubits(rho) ⊗ I/d over the given qubits."""
    tensor = rho.reshape((2,) * 6)
    keep = [q for q in range(3) if q not in qubits]
    traced = np.einsum(_trace_spec(qubits), tensor)
    mixed = np.zeros_like(tensor)
    d = 2 ** len(qubits)
    for idx in np.ndindex(*(2,) * len(qubits)):
        sel = [slice(None)] * 6
        for q, b in zip(qubits, idx):
            sel[q], sel[q + 3] = b, b
        mixed[tuple(sel)] = traced / d
    return ((1 - p) * tensor + p * mixed).reshape(8, 8)


def _trace_spec(qubits):
    rows, cols = list("abc"), list("def")
    for q in qubits:
        cols[q] = rows[q]
    out = [rows[q] for q in range(3) if q not in qubits] + [cols[q] for q in range(3) if q not in qubits]
    return "".join(rows + cols) + "->" + "".join(out)


def _probabilities(gates, noisy=True):
    rho = np.zeros((8, 8), dtype=complex)
    rho[0, 0] = 1
    for gate in gates:
        u, qubits = _unitary(gate)
        rho = u @ rho @ u.conj().T
        if noisy:
            p = _P1 if len(qubits) == 1 else _P2
            rho = _depolarize(rho, qubits, p)
    probs = np.real(np.diag(rho)).clip(min=0)
    probs = probs / probs.sum()
    if noisy:
        a = np.kron(np.kron(_READ, _READ), _READ)
        probs = a @ probs
    return probs


def _counts(probs, shots, seed):
    if shots > _MAX_SHOTS:
        raise ValueError(f"at most {_MAX_SHOTS} shots")
    sample = np.random.default_rng(seed).multinomial(int(shots), probs)
    return {format(i, "03b"): int(n) for i, n in enumerate(sample) if n}


def run_device(gates, shots=20000, seed=0):
    """Run the gate list on the noisy device and return the counts {"000": n, ...}.
    Changing `seed` gives another sample of shots."""
    return _counts(_probabilities(list(gates)), shots, seed)


def calibrate(shots=20000, seed=0):
    """Readout counts when each basis state is prepared with no gate error:
    {"000": {"000": n, ...}, "001": {...}, ...}."""
    a = np.kron(np.kron(_READ, _READ), _READ)
    return {format(j, "03b"): _counts(a[:, j], shots, seed + j) for j in range(8)}
