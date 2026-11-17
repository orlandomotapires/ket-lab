## An annealer has no rules

You have four jobs worth 5, 4, 3 and 2, and you must run exactly two. Jobs 0 and 1 need the same machine, and jobs 1 and 2 the same person, so neither pair can run together. Ignoring the count, jobs 0, 2 and 3 are worth 10 and clash with nothing. With the rules the best choice is jobs 0 and 2, worth 8, and it is the only one: the other allowed pairs are worth 7, 6 and 5.

An annealer takes an energy over bits and returns a low one, with no place to say "exactly two" or "not both". The way out is to add a term that is zero when the rule holds and positive when it does not, so that breaking the rule costs more than it gains. That is a **penalty term**, and its weight is a number you have to choose.

## One rule by hand

Take two jobs of value 5 and 4 and require exactly one of them. The penalty is $A(x_0 + x_1 - 1)^2$, zero for one job and $A$ for none or for both. With $x^2 = x$ it expands to $A(1 - x_0 - x_1 + 2x_0x_1)$, and the total cost is

$$
-5x_0 - 4x_1 + A(1 - x_0 - x_1 + 2x_0x_1), \qquad Q = \begin{pmatrix} -5 - A & 2A \\ 0 & -4 - A \end{pmatrix}, \quad \text{offset } A.
$$

The states $x = 00, 01, 10, 11$ cost $A$, $-4$, $-5$ and $-9 + A$. Both jobs beat the first alone when $-9 + A < -5$, that is for $A < 4$: with $A = 3$ the lowest state is $11$ and the annealer is right to return it, with $A = 6$ it is $10$. A weight has to exceed the most a violation can gain, here the value of the smaller job.

## The whole instance

For the four jobs, $A(\sum x_i - 2)^2 = A(\sum x_i^2 + 2\sum_{i<j} x_ix_j - 4\sum x_i + 4)$. The diagonal of $Q$ gets $-v_i - 3A$, every pair gets $2A$, the offset is $4A$, and a conflicting pair also gets $B$, since it pays only when both jobs run. With $B = 6$ and $A = 4$:

$$
Q = \begin{pmatrix} -17 & 14 & 8 & 8 \\ & -16 & 14 & 8 \\ & & -15 & 8 \\ & & & -14 \end{pmatrix}, \qquad \text{offset } 16.
$$

Here the threshold comes from the third job. Adding job 3 to the pair $\{0, 2\}$ brings 2 and costs $A(3-2)^2 = A$, so for $A < 2$ the three jobs win (at $A = 1$ the cost is $-9$ against $-8$) and at $A = 2$ the two states tie. A tie is a failure too, since the annealer may end on either state: the weight must be strictly above 2.

With $s = 1 - 2x$, a diagonal entry $Q_{ii}$ gives $-Q_{ii}/2$ to the field $h_i$, and a pair entry $Q_{ij}$ gives the coupling $Q_{ij}/4$ and $-Q_{ij}/4$ to both fields. For job 0, $h_0 = 17/2 - (14 + 8 + 8)/4 = 1$. The result is $h = (1, -1, 0, 1)$, couplings 3.5 on the two conflicting pairs and 2 on the other four, and a constant of 0.

## Annealing it

The anneal is the one of lesson 6.2, on $16 \times 16$ matrices. Hardware couplings have a limited range, so divide $H_P$ by its largest coefficient, here 3.5, before using it in $H(s)$. The probability of the best choice is 0.228 at $T = 5$, 0.592 at $T = 20$ and 0.969 at $T = 80$. The smallest gap is 0.238.

Raise the weight to $A = 20$. The energies of the allowed choices do not move, because the penalty is zero on them, but the largest coefficient becomes 11.5 and after dividing, the differences between allowed choices shrink by a factor of about 3. The probability at $T = 80$ falls to 0.564 and the smallest gap to 0.079. A weight just above the threshold is no better: $A = 2.5$ gives 0.826 and a gap of 0.180, since a penalized state lies almost level with the answer. It is the trade of the chain strength in lesson 6.4: strong enough to hold, no stronger.

## Choosing the weight in practice

Here you find the threshold by enumeration. For a real problem you cannot, because the threshold depends on the best feasible value, which is what you are looking for. Lucas (Section 4.2) gives a safe rule for set packing: keep the objective weight below the constraint weight, so that no violation pays. Otherwise people pick a weight above the largest gain a violation could bring, anneal, check that the answer is feasible and adjust. No formula gives the best weight, and this is a practical difficulty of annealing.
