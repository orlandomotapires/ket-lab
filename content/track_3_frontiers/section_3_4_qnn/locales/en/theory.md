## Machine learning with circuits

A classifier receives a point $\vec x$ and returns a class. In a **quantum classifier**, the point enters the circuit as rotation angles, and the class comes out of a measurement. The trainable weights are other angles, adjusted by gradient as in the previous lessons.

## Encoding the data

Before processing classical data, you have to put it into a quantum state. The most common ways:

- **Angle encoding**: each coordinate becomes the angle of a rotation, such as $R_X(x_0)$ and $R_Y(x_1)$. It is simple to prepare, but uses one qubit (or one gate) per coordinate.
- **Amplitude encoding**: the $2^n$ numbers of the data become the amplitudes of $n$ qubits. It is compact, but hard to prepare.
- **Phase encoding**: the data enter as relative phases.

Here we use angle encoding.

## Data re-uploading

If the data enter only once, the circuit's output is a simple trigonometric function of $\vec x$ and cannot draw complicated boundaries. The way out is to **re-upload** the data several times, interleaving them with trainable layers:

$$
U(\vec x, \vec w) = W_L\, S(\vec x)\, W_{L-1}\, S(\vec x) \cdots W_1\, S(\vec x)\, W_0
$$

Each re-upload enriches the function the circuit represents, like the extra terms of a Fourier series.

## The classifier

- **Input:** points $(x_0, x_1)$ on two concentric circles; the outer ones have class $+1$ and the inner ones $-1$. A straight line does not separate the two classes.
- **Output:** $\langle Z_0 \rangle$, between $-1$ and $+1$; the sign is the predicted class.
- **Training:** minimize the mean squared error between $\langle Z_0\rangle$ and the labels, with the Adam optimizer.

The circuit processes all the points at once: when `x` has shape $(N, 2)$, PennyLane runs the $N$ versions of the circuit in parallel (*broadcasting*).

## Generalize, don't memorize

What matters is getting right the points the model has **not seen**. That is why validation uses a separate test set. High accuracy on the training set and low accuracy on the test set is a sign that the model memorized the examples (*overfitting*).

## In the lab

- The **Decision boundary** tab shows the circuit's output over the whole plane, with the training points on top.
- The **Convergence** tab shows the loss at every epoch.

The starting code loads the data only once. Click **Run** (or Ctrl+Enter) to train.
