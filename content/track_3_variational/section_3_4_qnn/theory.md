## Two circles that no line separates

Take 80 points in the plane on two concentric circles, radius 1 for class $+1$ and radius 0.45 for class $-1$. No straight line separates them, so a model that only draws straight boundaries fails. A circuit can do this job too: in a **variational quantum classifier** the point $\vec x$ enters as rotation angles, trainable weights are other rotation angles, and the class is the sign of a measured expectation value. The weights are trained by gradient descent as in lesson 3.1.

## Getting the numbers into the circuit

Classical data has to become a quantum state. The simplest choice is angle encoding: each coordinate is the angle of a rotation, $R_X(x_0)$ and $R_Y(x_1)$. Amplitude encoding stores $2^n$ numbers in the amplitudes of $n$ qubits, which is compact, but preparing such a state is expensive in general. Phase encoding puts the data in relative phases. This lesson uses angle encoding.

If $\vec x$ enters once, the output is a trigonometric polynomial of degree 1 in each coordinate. That is too stiff for a curved boundary. **Data re-uploading** loads $\vec x$ again between trainable blocks:

$$
U(\vec x, \vec w) = W_L\, S(\vec x)\, W_{L-1}\, S(\vec x) \cdots W_1\, S(\vec x)\, W_0 ,
$$

where $S(\vec x)$ is the encoding block and each $W_l$ a trainable block.

Why one upload is limited: $R_X(x)$ contains $\cos\frac{x}{2}$ and $\sin\frac{x}{2}$, and an expectation value is quadratic in the amplitudes, so one upload gives $\cos x$, $\sin x$ and a constant (the argument of lesson 3.1). Trainable gates before and after change the coefficients, never the frequency. With two uploads the amplitudes contain products of two such factors and the output gains $\cos 2x$ and $\sin 2x$. With $L$ uploads of $R_X(x)$ the highest frequency is $L$.

Here is a case you can follow on the Bloch sphere. One qubit starts in $|0\rangle$ and gets $R_X(x)$, then a trainable $R_Y(\pi/2)$, then $R_X(x)$ again. $R_X(x)$ takes $(0,0,1)$ to $(0,-\sin x,\cos x)$, $R_Y(\pi/2)$ takes that to $(\cos x,-\sin x,0)$, and the second $R_X(x)$ takes it to $(\cdot,\,-\sin x\cos x,\,-\sin^2 x)$. So

$$
\langle Z\rangle = -\sin^2 x = \tfrac{1}{2}\left(\cos 2x - 1\right),
$$

which has frequency 2, out of reach for a single upload.

## Reading the answer, and trusting it

The output is $\langle Z_0\rangle \in [-1, 1]$ and its sign is the predicted class. The loss is the mean squared error between $\langle Z_0\rangle$ and the labels, $\frac{1}{N}\sum_n (\langle Z_0\rangle_n - y_n)^2$, minimized with the Adam optimizer. A loss of 0 means every output equals its label, and a constant output 0 gives a loss of 1. With $x$ of shape $(N, 2)$ PennyLane evaluates all $N$ points in one call (broadcasting).

What counts is accuracy on points the model has not seen, so the check uses a separate test set. If the training accuracy is high and the test accuracy is low, the model has memorized the 80 training points and its noise: overfitting. Each layer adds $3\times 2$ weights and one more upload, which gives a more flexible model that also fits noise more easily. This is the case that usually goes wrong with more layers than the data justify.

Before training, predict the accuracy of a single-upload circuit (`LAYERS = 1`) on the circles, then run it and compare. Then raise `LAYERS` and watch the test accuracy, not only the loss.
