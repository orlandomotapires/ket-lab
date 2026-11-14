## Das Problem

Eine Funktion $f:\{0,1\} \to \{0,1\}$ steckt in einer Black Box. Es gibt vier Möglichkeiten:

| $f$ | $f(0)$ | $f(1)$ | Typ |
| :-- | :-: | :-: | :-- |
| $0$ | 0 | 0 | konstant |
| $1$ | 1 | 1 | konstant |
| $x$ | 0 | 1 | balanciert |
| $\text{NOT } x$ | 1 | 0 | balanciert |

Die Frage lautet nicht, welche Funktion es ist, sondern ob sie **konstant** oder **balanciert** ist. Klassisch braucht man zwei Abfragen, $f(0)$ und $f(1)$. Der Deutsch-Algorithmus antwortet mit **einer**.

## Das Orakel

$$
U_f\,|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle
$$

Hier ist $x$ das Qubit 0 und $y$ das Hilfsqubit (Qubit 1). Im Labor ist das Orakel `oracle(qc)`, sein Inhalt ist geheim.

## Warum Parallelität allein nicht genügt

Mit der Eingabe in $|+\rangle$ und dem Hilfsqubit in $|0\rangle$ wertet das Orakel $f$ an beiden Eingaben gleichzeitig aus:

$$
\frac{1}{\sqrt2}\big(|0\rangle|f(0)\rangle + |1\rangle|f(1)\rangle\big)
$$

Eine Messung zerstört aber die Superposition und liefert nur den Wert von $f$ an einer zufällig gewählten Eingabe. Es fehlt die Interferenz.

## Der Algorithmus

1. Hilfsqubit in $|-\rangle$, Eingabe in $|+\rangle$.
2. Eine Abfrage. Durch Phase Kickback ist die Eingabe danach
$$
\frac{1}{\sqrt2}\big((-1)^{f(0)}|0\rangle + (-1)^{f(1)}|1\rangle\big)
$$
3. Hadamard auf die Eingabe. Gilt $f(0) = f(1)$, sind die Vorzeichen gleich, der Zustand ist $\pm|+\rangle$ und das Hadamard führt ihn nach $|0\rangle$. Gilt $f(0) \neq f(1)$, ist der Zustand $\pm|-\rangle$ und das Hadamard führt ihn nach $|1\rangle$.

Die Messung von Qubit 0 liefert sicher $f(0) \oplus f(1)$.

## Was der Algorithmus verrät

Die Funktionen $f = x$ und $f = \text{NOT } x$ liefern **dieselbe** Antwort ($|1\rangle$): Sie unterscheiden sich um ein globales Vorzeichen, das nicht beobachtbar ist. Der Algorithmus verrät weder $f(0)$ noch $f(1)$, sondern nur die globale Eigenschaft $f(0) \oplus f(1)$. Zwei Abfragen durch eine zu ersetzen geht gerade deshalb, weil die Frage weniger verlangt als „Welche Funktion ist es?".

## Im Labor

Im Tab **Amplituden** siehst du das Vorzeichen, das das Orakel auf Qubit 0 aufprägt, und wie das letzte Hadamard es in $|0\rangle$ oder $|1\rangle$ verwandelt. Bei der Prüfung wird dein Schaltkreis gegen alle vier Funktionen getestet.
