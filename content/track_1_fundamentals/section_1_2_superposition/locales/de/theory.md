## Jenseits der Pole

In der vorigen Lektion hat das Qubit nur $|0\rangle$ und $|1\rangle$ besucht. Das **Hadamard**-Gatter ($H$) bringt den Vektor auf den Äquator der Kugel:

$$
H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}} = |+\rangle
$$

$$
H|1\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}} = |-\rangle
$$

In $|+\rangle$ haben beide Amplituden den Wert $\frac{1}{\sqrt{2}}$, also hat jedes Ergebnis die Wahrscheinlichkeit $\left|\frac{1}{\sqrt{2}}\right|^2 = \frac{1}{2}$. Das ist eine **gleichmäßige Superposition**.

## Was die Messung bewirkt

Messen enthüllt keinen Wert, der schon vorher da war. Die Messung **würfelt** ein Ergebnis aus, mit den Wahrscheinlichkeiten, die durch die Amplituden gegeben sind, und der Zustand wird zum ausgewürfelten Ergebnis: Der Vektor springt vom Äquator zu einem der Pole. Dieser Sprung ist der **Kollaps**.

Deshalb ist ein Qubit in $|+\rangle$ mit anschließender Messung ein Zufallsbit-Generator. Der Zufall kommt nicht daher, dass uns irgendein Detail des Systems unbekannt ist: Er ist Teil der Theorie.

## Im Labor

- `QuantumCircuit(1, 1)` erzeugt 1 Qubit und 1 klassisches Bit, in dem das Messergebnis gespeichert wird.
- Mit dem Cursor in der Messzeile zeigt die Kugel **ein** ausgewürfeltes Ergebnis. Mit „Erneut würfeln“ siehst du ein anderes.
- „1024 Messungen simulieren“ wiederholt den gesamten Schaltkreis 1024-mal und zeigt die Anzahl jedes Ergebnisses.
