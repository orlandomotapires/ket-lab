# Hidden setup for lesson 3.4: the training set (the test set exists only in the validator).
def make_circles(n, seed):
    """Two concentric circles: radius 1.0 (class +1) and 0.45 (class -1), with radial noise."""
    import numpy as _np

    rng = _np.random.default_rng(seed)
    labels = _np.where(_np.arange(n) % 2 == 0, 1.0, -1.0)
    radius = _np.where(labels > 0, 1.0, 0.45) + rng.normal(0, 0.08, n)
    angle = rng.uniform(0, 2 * _np.pi, n)
    points = _np.stack([radius * _np.cos(angle), radius * _np.sin(angle)], axis=1)
    return points, labels


def _build_data():
    from pennylane import numpy as _pnp

    points, labels = make_circles(80, seed=7)
    return _pnp.array(points, requires_grad=False), _pnp.array(labels, requires_grad=False)


X_train, y_train = _build_data()
x_example = X_train[:1]
del _build_data, make_circles
