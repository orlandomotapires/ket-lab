## Das Problem

Ein unitärer Operator $U$ hat einen Eigenvektor $|\psi\rangle$ mit Eigenwert $e^{2\pi i\theta}$:

$$
U|\psi\rangle = e^{2\pi i\theta}|\psi\rangle, \qquad 0 \le \theta < 1
$$

Die **Phasenschätzung** findet $\theta$ heraus. Sie ist das Herzstück des Shor-Algorithmus und vieler Simulationen in der Chemie.

## Die Idee

Durch den Phase Kickback gibt ein kontrolliertes $U$ mit dem Ziel in $|\psi\rangle$ die Phase $e^{2\pi i\theta}$ an die Kontrolle zurück. Wendet man $U^{2^j}$ kontrolliert vom Zählqubit $j$ an, erhält dieses Qubit die Phase $e^{2\pi i\,2^j\theta}$. Mit $t$ Zählqubits ist das Register in

$$
\frac{1}{\sqrt{2^t}}\sum_{k=0}^{2^t-1} e^{2\pi i\,\theta k}\,|k\rangle
$$

und das ist genau die QFT der Zahl $2^t\theta$. Die inverse QFT liefert diese Zahl zurück.

## Der Schaltkreis

1. Hadamard auf die Zählqubits (0, 1 und 2) und der Eigenvektor auf Qubit 3.
2. Für jedes Zählqubit $j$ die kontrollierte Potenz $U^{2^j}$: `apply_controlled_u(qc, j, 2**j)`.
3. Die inverse QFT aus der vorigen Lektion: `inverse_qft(qc, [0, 1, 2])`.
4. Das Zählregister messen. Der gelesene Wert $m$ ergibt $\theta \approx m/2^t$.

Mit $t = 3$ beträgt die Genauigkeit $1/8$. Wenn $\theta$ kein Vielfaches von $1/8$ ist, verteilt sich das Ergebnis um den nächstgelegenen Wert; mehr Zählqubits verengen diese Spitze.

## In diesem Labor

$U$ ist ein Phasengatter, $U = \begin{pmatrix} 1 & 0 \\ 0 & e^{2\pi i\theta} \end{pmatrix}$, dessen Eigenvektor $|1\rangle$ ist. Der Wert von $\theta$ ist geheim. Nach dem Messen führt `run_shots(qc)` den Schaltkreis 1024-mal aus und liefert die Zählungen; berechne mit ihnen `theta` in Python. Der Tab **Register** zeigt die Wahrscheinlichkeit jedes Werts des Zählregisters, mit dem zugehörigen Bruch.
