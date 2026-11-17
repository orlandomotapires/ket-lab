## A triangle on a square

The three-qubit problem of lessons 6.2 and 6.3 couples every pair of its spins: $J_{01}=1/6$, $J_{02}=1/4$, $J_{12}=1/2$, with fields $h=(1/3,\,2/3,\,1)$. Its ground state is $s=(+1,-1,-1)$ with energy $-1.25$. Now suppose the machine has four qubits on a square, $0\!-\!1\!-\!2\!-\!3\!-\!0$, and a coupler only along those four edges. A square has no triangle, so there is no place for all three couplings. Real annealers have the same problem at scale: each qubit is coupled to few others.

The remedy is **minor embedding**. Represent logical qubit 2 by a **chain** of two physical qubits, 2 and 3, forced to take the same value by a ferromagnetic coupling $-F\,Z_2Z_3$ with $F>0$, the **chain strength**. Put $J_{01}$ on edge 0–1, $J_{12}$ on edge 1–2, and $J_{02}$ on edge 3–0, so that qubit 3 stands in for logical qubit 2 there, and all of $h_2$ on physical qubit 2. The embedded energy is

$$
E_\text{emb}=J_{01}s_0s_1+J_{12}s_1s_2+J_{02}s_0s_3+h_0s_0+h_1s_1+h_2s_2-F\,s_2s_3 .
$$

## Bookkeeping, by hand

With an intact chain, $s_3=s_2$, the term $J_{02}s_0s_3$ becomes $J_{02}s_0s_2$ and $-Fs_2s_3$ becomes $-F$, so $E_\text{emb}=E_\text{logical}-F$ exactly. For the logical ground state that is $-1.25-F$.

Now break the chain, $s_3=-s_2$. The chain term becomes $+F$, a change of $+2F$ from the intact value, and the term on edge 3–0 changes sign. That can pay off. In the logical problem, $s_0=s_2=-1$ costs $+J_{02}=+1/4$ on the 0–2 coupling; with $s_3=+1$ the same edge gives $-1/4$, a saving of $2J_{02}=1/2$. The state $(s_0,s_1,s_2,s_3)=(-1,-1,-1,+1)$ has energy $-1.0833-0.5+F=-1.5833+F$, where $-1.0833$ is the logical energy of $(-1,-1,-1)$. It beats the intact ground state $-1.25-F$ whenever $-1.5833+F<-1.25-F$, that is for $F<1/6$. Brute force over the 16 physical states confirms it: at $F=0.1$ the lowest energy is $-1.4833$ with a broken chain (a second broken state, with $s_1=+1$, ties with it), while at $F=0.2$ it is $-1.45$ with the chain intact and the logical ground state recovered. The threshold is $F=1/6$.

Where you put $h_2$ matters. Split half and half, the field terms cancel when the chain breaks, so breaking loses the field energy and saves nothing: for this instance the chain then holds for every $F>0$ and there is no threshold to find. That is why the mission puts all of $h_2$ on qubit 2.

**Decoding.** Read the logical spin from the chain. With an intact chain this is the common value. With a broken chain you can take the majority of its qubits (two qubits give a tie, a longer chain does not) or discard the sample.

## Why not just make F huge

The device accepts couplings and fields only inside a limited range, and the whole problem is rescaled so that its largest coefficient fits. Here the largest coefficient is $h_2=1$ as long as $F\le1$, and $F$ itself beyond that. At $F=4$ everything is divided by 4, so the gap of 1/6 between the logical ground state and the next logical state becomes about 0.04 in the machine's units, closer to what noise and temperature can blur. Above the threshold the chain holds but the problem shrinks; below it the chain breaks. In practice the threshold is not known in advance, and software sets a heuristic default.

## What a physical annealer is, and what is known

Commercial annealers use superconducting flux qubits: the qubits and their tunable couplers are superconducting circuits steered by external fluxes. A current generation has more than five thousand qubits, each coupled to up to fifteen others (D-Wave's Pegasus graph, as the manufacturer documents it). A densely connected problem therefore needs chains, and chains use up qubits, so the largest problem that fits is smaller than the qubit count suggests; how many a given problem needs depends on its graph and on the embedding found.

The device is also not the closed system of lesson 6.2. Finite temperature and noise mean it does not follow the ground state of $H(s)$ with certainty; it returns a distribution of samples, and you keep the lowest energy.

On speedups, the evidence is mixed. Rønnow and coauthors (2014) benchmarked a D-Wave Two device with up to 503 qubits on random spin-glass instances against simulated classical and quantum annealers, and found no evidence of speedup on the whole set of instances, with inconclusive results on instance-by-instance subsets. They note that this does not rule out speedup for other problem classes. Later work reports advantages of the hardware over specific classical algorithms on specific instance families; Albash and Lidar (2018), for example, report a scaling advantage over simulated annealing while not claiming a quantum speedup. Whether quantum annealing gives a general advantage for optimization is an open question.
