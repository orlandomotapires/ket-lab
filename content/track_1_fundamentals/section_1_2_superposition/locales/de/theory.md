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

## Statistische Schwankung

Hat ein Ergebnis die Wahrscheinlichkeit $p$ und gibt es $N$ Wiederholungen, ist die erwartete Anzahl $N p$, die tatsächliche Anzahl schwankt aber mit der Standardabweichung $\sigma = \sqrt{N p (1-p)}$ darum herum. Für $N = 100$ und $p = \tfrac{1}{2}$ ist $\sigma = 5$: $56$ Nullen statt $50$ sind normal. Der relative Anteil schwankt wie $1/\sqrt{N}$, mit mehr Messungen kommt der Anteil also näher an $50\%$. Bei drei Qubits hat jedes der $8$ Ergebnisse die Wahrscheinlichkeit $\tfrac{1}{8}$, und die Zählungen schwanken ebenfalls von Lauf zu Lauf.

## Anderer Eingang, andere Phase

Das Hadamard-Gatter auf $|1\rangle$ liefert $|-\rangle$, mit denselben $50/50$-Wahrscheinlichkeiten wie $|+\rangle$. Der Unterschied ist nur das Vorzeichen der $|1\rangle$-Amplitude, das eine direkte Messung nicht sieht. Lektion 1.3 behandelt diese Phase.

## Im Labor

- `QuantumCircuit(3, 3)` erzeugt 3 Qubits und 3 klassische Bits, in denen die Messergebnisse gespeichert werden.
- Mit dem Cursor in der Messzeile zeigt die Kugel **ein** ausgewürfeltes Ergebnis. Mit „Erneut würfeln“ siehst du ein anderes.
- „1024 Messungen simulieren“ wiederholt den gesamten Schaltkreis 1024-mal und zeigt die Anzahl jedes Ergebnisses.
