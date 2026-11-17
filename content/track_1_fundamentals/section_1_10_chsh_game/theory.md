## The game

A referee picks two bits $x$ and $y$ at random and gives $x$ to Alice and $y$ to Bob. Alice answers a bit $a$ and Bob answers a bit $b$. They cannot communicate once the game starts, but they may agree on a strategy beforehand. They win when

$$a \oplus b = x \wedge y ,$$

that is, $a = b$ unless $x = y = 1$, in which case the answers must differ. This is the **CHSH game**, named after Clauser, Horne, Shimony and Holt.

## Classical strategies

A deterministic strategy fixes $a$ as a function of $x$ and $b$ as a function of $y$. Four question pairs have to satisfy $a(x) \oplus b(y) = x \wedge y$. Add the four conditions modulo 2: the left side adds to $0$, since each $a(x)$ and each $b(y)$ appears twice, while the right side adds to $1$. So at most 3 of the 4 pairs can be won, and always answering $a = b = 0$ wins exactly 3.

Shared randomness only chooses among deterministic strategies, so it cannot raise the average. The classical winning probability is at most $3/4$.

## Quantum strategy

Alice and Bob share $|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}$. Each measures their qubit along an axis in the $x$–$z$ plane that depends on their question bit. Measuring along the axis at angle $\theta$ means the observable

$$A(\theta) = \cos\theta\, Z - \sin\theta\, X ,$$

which Qiskit implements as $R_y(\theta)$ followed by a computational-basis measurement. For $|\Phi^+\rangle$ the expectation value of the product of two such observables is

$$E(\theta_A, \theta_B) = \langle A(\theta_A) \otimes A(\theta_B) \rangle = \cos(\theta_A - \theta_B),$$

because $|\Phi^+\rangle$ has $\langle Z\otimes Z\rangle = \langle X\otimes X\rangle = 1$.

The answers $a, b$ are bits and $(-1)^{a\oplus b}$ has expectation $E$, so for a question pair the probability that $a = b$ is $(1+E)/2$. Averaging the winning probability over the four question pairs gives

$$P_\text{win} = \frac{1}{2} + \frac{1}{8}\left(E_{00} + E_{01} + E_{10} - E_{11}\right).$$

The bracket is the CHSH quantity $S$. With Alice's angles $0$ and $\pi/2$ and Bob's angles $\pi/4$ and $-\pi/4$, three correlations equal $\cos(\pi/4) = 1/\sqrt{2}$ and the fourth equals $-1/\sqrt{2}$, so $S = 2\sqrt{2}$ and

$$P_\text{win} = \frac{1}{2} + \frac{\sqrt{2}}{4} = \cos^2\frac{\pi}{8} \approx 0.854 .$$

## Bell's theorem and the Tsirelson bound

A local hidden-variable model gives $S \le 2$ in absolute value, the CHSH inequality, which is the same bound as $P_\text{win} \le 3/4$. Quantum mechanics predicts $S = 2\sqrt{2}$ for this state and these measurements, which violates the inequality. Bell's theorem is the statement that no local hidden-variable theory reproduces all the predictions of quantum mechanics. Experiments that close the main loopholes have measured violations of the CHSH inequality.

Quantum theory has its own limit: for any state and any observables with outcomes $\pm 1$ on two separated systems, $|S| \le 2\sqrt{2}$, the **Tsirelson bound**. So $\cos^2(\pi/8)$ is the largest winning probability of any strategy that uses quantum states and measurements. The no-signaling condition alone would allow $S = 4$ and $P_\text{win} = 1$ (a Popescu–Rohrlich box). Quantum mechanics does not reach it.

The shared pair does not let Alice and Bob communicate. Each marginal distribution of $a$ or $b$ is uniform and independent of the other player's question, which is the no-signaling condition.

## Check it

In the editor, `play(x, y)` builds the circuit for one question pair, with qubit 0 for Alice and qubit 1 for Bob, and `outcome_probabilities(circuit)` returns the exact probabilities of the answer pairs $(a, b)$. Before choosing angles, predict the winning probability for all angles equal to $0$ (three question pairs out of four), then confirm it. The validator computes the winning probability itself and also checks that Alice's rotation depends only on $x$ and Bob's only on $y$.
