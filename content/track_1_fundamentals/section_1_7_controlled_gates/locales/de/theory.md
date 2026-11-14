## Kontrollierte Gatter

Ein kontrolliertes Gatter wendet eine Operation auf das **Ziel** nur an, wenn die **Kontrolle** $1$ ist. $CS$ wendet $S$ auf das Ziel an, was dem Multiplizieren der Amplitude von $|11\rangle$ mit $i$ entspricht:

$$
CS = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & i \end{pmatrix}
$$

Die Phase liegt auf einem Basiszustand von **zwei** Qubits. Bei Basiseingaben wie $|01\rangle$ oder $|10\rangle$ ändert sich nichts, und bei $|11\rangle$ erscheint nur eine globale Phase; deshalb nutzt der Validator Superpositionen, bei denen die relative Phase zu einem beobachtbaren Unterschied wird.

## Wie die Lösung funktioniert

Der Trick ist, zu ändern, was das Gatter sieht. Sind $a$ und $b$ die Werte der beiden Qubits, enthält Qubit 1 nach `qc.cx(0, 1)` den Wert $a \oplus b$ (die Parität). Jedes $T$ addiert $\pi/4$ pro Qubit in $1$; das $T^{\dagger}$ auf der Parität zieht $\pi/4$ ab. Die Gesamtphase ist

$$
\frac{\pi}{4}\bigl(a + b - (a \oplus b)\bigr) = \frac{\pi}{4}\cdot 2ab = \frac{\pi}{2}\,ab
$$

also $\pi/2$ nur für $a = b = 1$: genau $CS$.

## Nützliche Identitäten

- $S = T^2$ und $Z = S^2 = T^4$: Phasengatter, deren Winkel sich addieren.
- $HZH = X$ und $HXH = Z$: Das Hadamard-Gatter vertauscht die $X$- und die $Z$-Achse.
- $CZ = H_{\text{Ziel}}\,\text{CNOT}\,H_{\text{Ziel}}$: Ein Hadamard auf dem Ziel vor und nach dem CNOT ergibt das CZ. In Qiskit `qc.h(1); qc.cx(0, 1); qc.h(1)`.
- Hadamard auf beiden Qubits vor und nach einem CNOT kehrt ihre Rollen um: Es entsteht ein CNOT von 1 auf 0.
- $\text{SWAP}$ = drei CNOTs: `qc.cx(0, 1); qc.cx(1, 0); qc.cx(0, 1)`.

## Universalität

Das CNOT und die Ein-Qubit-Gatter bilden eine **universelle Menge**: Mit ihnen lässt sich jedes Mehr-Qubit-Gatter beliebig genau aufbauen. Operationen in CNOTs und einfache Gatter zu zerlegen, wie hier, ist das, was echte Maschinen tun, um einen Schaltkreis auszuführen.

## Kontrolliertes Rz und CS

In Lektion 1.3 haben wir gesehen, dass sich $R_z(\theta)$ und $P(\theta)$ nur durch eine globale Phase unterscheiden. Ist das Gatter **kontrolliert**, ist diese Phase nicht mehr global: Sie wird zu einer relativen Phase, und das Gatter wirkt auch auf das Kontrollqubit. Deshalb ist $CS$ nicht dasselbe wie ein kontrolliertes $R_z$.
