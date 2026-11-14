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

## Messen mittendrin

Bei $HH = I$ geschieht die Auslöschung der beiden $|1\rangle$-Anteile nur, weil beide Amplituden **gemeinsam** beim zweiten Hadamard ankommen. Misst du das Qubit zwischen den beiden Hadamards, hat die Messung bereits $0$ oder $1$ gezogen und der Zustand ist auf einen Pol kollabiert. Das zweite Hadamard erhält dann $|0\rangle$ oder $|1\rangle$ und liefert $|+\rangle$ oder $|-\rangle$, mit je $50\%$ für jedes Ergebnis: Die Interferenz ist verschwunden. Den Weg zu beobachten zerstört die Interferenz.

## Die Reihenfolge der Gatter zählt

Im Allgemeinen gilt $AB \neq BA$. $H$ und danach $S$ auf $|0\rangle$ ergibt $|{+i}\rangle$, aber $S$ und danach $H$ ergibt $|+\rangle$. Deshalb liest sich der Schaltkreis-Code von oben nach unten, in der Reihenfolge, in der die Gatter wirken, während das Matrixprodukt andersherum geschrieben wird.

## Im Labor

Gehe den Schaltkreis mit der Zeitleiste durch und verfolge die Amplitudentabelle: Beobachte das Vorzeichen jeder Amplitude vor dem letzten Hadamard und was danach übrig bleibt.
