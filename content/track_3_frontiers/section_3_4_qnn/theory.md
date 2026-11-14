## Classification with a circuit

A classifier maps a point $\vec x$ to a class. In a **variational quantum classifier**, the point enters the circuit as rotation angles, trainable weights are other rotation angles, and the class is read from a measurement. The weights are trained by gradient descent, as in lesson 3.1.

## Encoding the data

Classical data must be loaded into a quantum state. Common choices:

- Angle encoding: each coordinate is the angle of a rotation, such as $R_X(x_0)$ and $R_Y(x_1)$. It is easy to prepare and uses one gate per coordinate.
- Amplitude encoding: $2^n$ numbers become the amplitudes of $n$ qubits. It is compact, but preparing the state is costly in general.
- Phase encoding: the data become relative phases.

This lesson uses angle encoding.

## Data re-uploading

If $\vec x$ enters the circuit once, the output is a trigonometric polynomial of degree 1 in each coordinate, which is too restrictive for a curved boundary. **Data re-uploading** loads $\vec x$ several times, alternating with trainable layers:

$$
U(\vec x, \vec w) = W_L\, S(\vec x)\, W_{L-1}\, S(\vec x) \cdots W_1\, S(\vec x)\, W_0
$$

Here $S(\vec x)$ is the encoding block and each $W_l$ is a trainable block. Each upload adds higher frequencies to the function the circuit can represent, like extra terms in a Fourier series.

## The classifier

- Input: points $(x_0, x_1)$ on two concentric circles. The outer circle has class $+1$ and the inner one $-1$. No straight line separates them.
- Output: $\langle Z_0\rangle \in [-1, 1]$. Its sign is the predicted class.
- Training: minimize the mean squared error between $\langle Z_0\rangle$ and the labels, using the Adam optimizer.

When `x` has shape $(N, 2)$, PennyLane evaluates the circuit for all $N$ points in one call (broadcasting).

## Generalization

A classifier is judged on points it has not seen, so validation uses a separate test set. High training accuracy with low test accuracy means the model has memorized the training points (overfitting).

## In the lab

- Decision boundary: the circuit output over the plane, with the training points on top.
- Convergence: the loss at each epoch.

The starter code uses a single upload (`LAYERS = 1`). Click Run (or press Ctrl+Enter) to train.
