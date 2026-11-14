## Wenn wir den Zustand nicht kennen

Bisher befand sich das Qubit immer in einem wohldefinierten Zustand $|\psi\rangle$: einem **reinen Zustand**. Auf einem echten Computer wirkt das Rauschen zufällig: Manchmal macht ein Gatter einen Fehler, manchmal nicht. Danach wissen wir nur noch, dass das Qubit mit Wahrscheinlichkeit $p_1$ in $|\psi_1\rangle$ ist, mit Wahrscheinlichkeit $p_2$ in $|\psi_2\rangle$ und so weiter. Das ist ein **gemischter Zustand**.

Ein gemischter Zustand ist keine Superposition. Die Superposition $\frac{|0\rangle + |1\rangle}{\sqrt2}$ ist ein reiner Zustand mit wohldefinierter Phase; eine Münze, die mit je 50 % $|0\rangle$ oder $|1\rangle$ liefert, hat überhaupt keine Phase.

## Die Dichtematrix

Beide Fälle passen in dieselbe Beschreibung, die **Dichtematrix**:

$$
\rho = \sum_i p_i\, |\psi_i\rangle\langle\psi_i|
$$

- Die Diagonale gibt die Messwahrscheinlichkeiten an: $P(0) = \rho_{00}$ und $P(1) = \rho_{11}$.
- Die **Reinheit** $\mathrm{Tr}(\rho^2)$ ist $1$ für einen reinen Zustand und kleiner als $1$ für einen gemischten; bei 1 Qubit ist das Minimum $1/2$.
- Auf der Bloch-Kugel liegen reine Zustände auf der Oberfläche und gemischte im Inneren, mit verkürztem Vektor.

Die verschränkten Qubits aus Lernpfad 1 schrumpften auf der Kugel aus demselben Grund: Der Zustand eines Qubits eines Bell-Paares ist, für sich betrachtet, gemischt. Man erhält ihn durch die **partielle Spur**, die das andere Qubit verwirft.

## Rauschkanäle

Eine verrauschte Operation wirkt auf $\rho$ durch **Kraus-Operatoren** $K_k$:

$$
\rho \;\longrightarrow\; \sum_k K_k\, \rho\, K_k^\dagger, \qquad \sum_k K_k^\dagger K_k = I
$$

Ein Fehler, der $X$ mit Wahrscheinlichkeit $p_x$, $Z$ mit $p_z$ und sonst nichts anwendet, hat $K_0 = \sqrt{1-p_x-p_z}\,I$, $K_1 = \sqrt{p_x}\,X$ und $K_2 = \sqrt{p_z}\,Z$. Die gängigsten Kanäle haben Namen: Bitflip, Phasenflip, depolarisierend, Amplitudendämpfung.

## Ein Fehler ist nicht dasselbe wie eine falsche Antwort

Die Wahrscheinlichkeit, dass **ein Fehler auftritt**, ist nicht die Wahrscheinlichkeit, dass **die Antwort falsch ausfällt**. Die Wirkung eines Fehlers hängt davon ab, wo er auftritt und was danach kommt: Ein $Z$ gefolgt von einem Hadamard wird zu einem vollständigen $X$, während ein $X$ zwischen $T$ und $T^\dagger$ zu einer Rotation wird, die das Ergebnis nur manchmal ändert. Deshalb betrachtet die Fehlerkorrektur in der nächsten Lektion die Art des Fehlers und nicht nur seine Häufigkeit.

## Im Labor

Das Gerät `default.mixed` simuliert die Dichtematrix. Beobachte in den **Bloch-Kugeln**, wie der Vektor im Fehlerschritt schrumpft; das Panel zeigt die Reinheit des Zustands. Der Tab **Register** zeigt $P(0)$ und $P(1)$.
