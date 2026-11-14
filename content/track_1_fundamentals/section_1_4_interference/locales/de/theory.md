## Amplituden können sich auslöschen

Wahrscheinlichkeiten addieren sich nur. Amplituden haben ein Vorzeichen (und eine Phase), also können sie sich auch **auslöschen**. Das ist die Interferenz, und aus ihr ziehen Quantenalgorithmen ihren Vorteil.

Betrachte zwei Hadamard-Gatter hintereinander. Das erste bringt $|0\rangle$ nach $|+\rangle$. Das zweite wirkt auf jeden Summanden:

$$
H|+\rangle = \frac{H|0\rangle + H|1\rangle}{\sqrt{2}}
= \frac{(|0\rangle + |1\rangle) + (|0\rangle - |1\rangle)}{2}
= |0\rangle
$$

Die beiden Beiträge zu $|1\rangle$ haben entgegengesetzte Vorzeichen und verschwinden: **destruktive Interferenz**. Die beiden zu $|0\rangle$ verstärken sich: **konstruktive Interferenz**. Das Ergebnis ist $HH = I$.

## Die Phase wählt, was ausgelöscht wird

Wird die relative Phase auf halbem Weg umgekehrt, wechselt die Auslöschung die Seite. So kommt es, dass ein Gatter, das „die Wahrscheinlichkeiten nicht ändert“, das Messergebnis bestimmt.

Darum ist die Phase aus der vorigen Lektion wichtig: Für sich allein ist sie für die Messung unsichtbar, aber ein Hadamard danach verwandelt sie in Wahrscheinlichkeit.

## In einer anderen Basis messen

Die Standardmessung unterscheidet $|0\rangle$ von $|1\rangle$ (die **Z-Basis**), kann aber $|+\rangle$ nicht von $|-\rangle$ unterscheiden. Um sie zu unterscheiden, wendet man vor der Messung ein Hadamard an: Es bringt $|+\rangle$ nach $|0\rangle$ und $|-\rangle$ nach $|1\rangle$. Das entspricht einer Messung in der **X-Basis**.

## Im Labor

Gehe den Schaltkreis mit der Zeitleiste durch und verfolge die Amplitudentabelle: Beobachte das Vorzeichen jeder Amplitude vor dem letzten Hadamard und was danach übrig bleibt.
