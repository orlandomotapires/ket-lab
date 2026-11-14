# Setup oculto da lição 3.4: o conjunto de treino (o de teste só existe no validador).
def make_circles(n, seed):
    """Dois círculos concêntricos: raio 1,0 (classe +1) e 0,45 (classe −1), com ruído radial."""
    import numpy as _np

    rng = _np.random.default_rng(seed)
    labels = _np.where(_np.arange(n) % 2 == 0, 1.0, -1.0)
    radius = _np.where(labels > 0, 1.0, 0.45) + rng.normal(0, 0.08, n)
    angle = rng.uniform(0, 2 * _np.pi, n)
    points = _np.stack([radius * _np.cos(angle), radius * _np.sin(angle)], axis=1)
    return points, labels


def _criar_dados():
    from pennylane import numpy as _pnp

    points, labels = make_circles(80, seed=7)
    return _pnp.array(points, requires_grad=False), _pnp.array(labels, requires_grad=False)


X_train, y_train = _criar_dados()
x_example = X_train[:1]
del _criar_dados, make_circles
