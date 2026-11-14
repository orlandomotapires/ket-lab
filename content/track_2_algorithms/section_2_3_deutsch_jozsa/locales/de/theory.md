## Das Problem

Du bekommst eine Funktion $f:\{0,1\}^n \to \{0,1\}$ als Black Box, mit einer Zusicherung: Sie ist entweder **konstant** (dieselbe Ausgabe für alle Eingaben) oder **balanciert** (Ausgabe $0$ für die Hälfte der Eingaben und $1$ für die andere Hälfte). Welche von beiden?

Ein klassischer Algorithmus braucht im schlechtesten Fall $2^{n-1} + 1$ Abfragen: Wenn die ersten $2^{n-1}$ denselben Wert liefern, kann die Funktion immer noch balanciert sein. Der Deutsch-Jozsa-Algorithmus antwortet mit **einer einzigen Abfrage** und ohne Fehler.

Die Trennung gilt gegenüber *exakten* klassischen Algorithmen. Ein **randomisierter** klassischer Algorithmus fragt die Funktion an wenigen zufälligen Eingaben ab: Liefern alle denselben Wert, antwortet er „konstant". Er irrt sich nur, wenn die Funktion balanciert ist und alle $k$ Abfragen übereinstimmen, mit Wahrscheinlichkeit etwa $2^{1-k}$; nach wenigen Abfragen ist der Fehler vernachlässigbar. Der Quantenvorteil ist hier echt, aber ein Vorteil gegenüber dem deterministischen Fall.

## Das Orakel

Die Funktion geht als Gatter in den Schaltkreis ein, das **Orakel**:

$$
U_f\,|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle
$$

Hier ist $x$ das Eingaberegister (Qubits 0 bis 2) und $y$ ein Hilfsqubit (Qubit 3). Im Labor ist das Orakel die Funktion `oracle(qc)`, und ihr Inhalt ist geheim.

## Der Algorithmus

1. Hilfsqubit in $|-\rangle$ und Eingabe in gleichmäßiger Superposition, mit Hadamards.
2. Eine Abfrage an das Orakel. Durch den Phase Kickback erhält jeder Term das Vorzeichen $(-1)^{f(x)}$:

$$
\frac{1}{\sqrt{2^n}}\sum_x |x\rangle \;\longrightarrow\; \frac{1}{\sqrt{2^n}}\sum_x (-1)^{f(x)}|x\rangle
$$

3. Wieder Hadamards auf der Eingabe. Die Endamplitude von $|00\dots0\rangle$ ist der Mittelwert der Vorzeichen:

$$
\frac{1}{2^n}\sum_x (-1)^{f(x)}
$$

Wenn $f$ konstant ist, beträgt dieser Mittelwert $\pm 1$, und die Eingabe endet mit Sicherheit in $|000\rangle$. Wenn sie balanciert ist, löschen sich die Vorzeichen aus, und $|000\rangle$ hat die Wahrscheinlichkeit null. Eine Messung entscheidet.

## Im Labor

Der Tab **Amplituden** zeigt den Zustand des Eingaberegisters, mit Vorzeichen. Sieh dir vor der letzten Hadamard-Schicht die Vorzeichen an, die das Orakel aufgeprägt hat; danach sieh, wie die Interferenz die gesamte Amplitude in $|000\rangle$ konzentriert oder auf null bringt. Das Orakel in diesem Labor ist balanciert. Bei der Validierung wird dein Schaltkreis gegen mehrere geheime Orakel getestet, konstante und balancierte.

## Hinweis zur Notation

Viele Lehrbücher schreiben Qubit 0 **links** in die Bezeichnung, etwa $|x_0 x_1 x_2\rangle$. Qiskit, und damit dieses Labor, schreibt Qubit 0 **rechts**: $|q_2 q_1 q_0\rangle$. Beim Vergleich mit einem Lehrbuch können die Bezeichnungen daher vertauscht erscheinen.
