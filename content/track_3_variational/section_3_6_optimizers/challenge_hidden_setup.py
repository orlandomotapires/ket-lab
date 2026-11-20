# The mission's hidden setup comes first (its `cost` stays defined), then the challenge's own costs.
# Hidden setup for lesson 3.6: the -F cost (fidelity with |Φ⁺⟩) of a fixed 4-angle ansatz,
# wrapped in a counter that records how many times the circuit is evaluated.
def _build_cost():
    import pennylane as _qml
    from pennylane import numpy as _np

    _dev = _qml.device("default.qubit", wires=2)

    @_qml.qnode(_dev)
    def _circuit(p):
        _qml.RY(p[0], wires=0)
        _qml.RY(p[1], wires=1)
        _qml.CNOT(wires=[0, 1])
        _qml.RY(p[2], wires=0)
        _qml.RY(p[3], wires=1)
        _p00 = _qml.Projector(_np.array([1, 0, 0, 1]) / _np.sqrt(2), wires=[0, 1])
        return _qml.expval(-_p00)

    class Cost:
        """cost(params) returns -F; calls counts the evaluations."""

        def __init__(self):
            self.calls = 0

        def __call__(self, params):
            self.calls += 1
            return float(_circuit(_np.asarray(params, dtype=float)))

    return Cost()


cost = _build_cost()
del _build_cost


# Hidden setup for the challenge of lesson 3.6: a 12-angle cost, the energy of the four-spin ring
# H = Σ Z_i Z_{i+1} + Σ X_i (indices mod 4) in the state of three layers of RY on four qubits, each layer
# followed by CNOTs 0→1, 1→2, 2→3. Two separate counted copies, cost_ps and cost_spsa, so that each run
# has its own tally of evaluations; theta0 is the common starting point. The mission's cost stays defined.
def _build():
    import numpy as _np

    def _ry(a):
        c, s = _np.cos(a / 2), _np.sin(a / 2)
        return _np.array([[c, -s], [s, c]])

    def _kron_all(mats):
        out = _np.eye(1)
        for m in mats:
            out = _np.kron(out, m)
        return out

    def _cnot(control, target):
        m = _np.zeros((16, 16))
        for b in range(16):
            bits = [(b >> (3 - k)) & 1 for k in range(4)]
            if bits[control]:
                bits[target] ^= 1
            m[sum(v << (3 - k) for k, v in enumerate(bits)), b] = 1.0
        return m

    z, x, i2 = _np.diag([1.0, -1.0]), _np.array([[0.0, 1.0], [1.0, 0.0]]), _np.eye(2)

    def _site(m, k):
        return _kron_all([m if q == k else i2 for q in range(4)])

    h = sum(_site(z, k) @ _site(z, (k + 1) % 4) for k in range(4)) + sum(_site(x, k) for k in range(4))
    ent = _cnot(2, 3) @ _cnot(1, 2) @ _cnot(0, 1)

    def _energy(p):
        p = _np.asarray(p, dtype=float).reshape(3, 4)
        state = _np.zeros(16)
        state[0] = 1.0
        for layer in range(3):
            state = ent @ (_kron_all([_ry(a) for a in p[layer]]) @ state)
        return float(state @ h @ state)

    class Cost:
        """cost(params) returns the energy for 12 angles; calls counts the evaluations."""

        def __init__(self):
            self.calls = 0

        def __call__(self, params):
            self.calls += 1
            return _energy(params)

    start = _np.random.default_rng(29).uniform(-3, 3, 12)
    return Cost(), Cost(), start


cost_ps, cost_spsa, theta0 = _build()
del _build
