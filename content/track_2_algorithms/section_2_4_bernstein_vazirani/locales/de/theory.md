## Das Problem

Jetzt ist die geheime Funktion das bitweise Produkt von $x$ mit einer geheimen Bitfolge $s$ aus $n$ Bits, modulo 2:

$$
f(x) = s \cdot x = s_0x_0 \oplus s_1x_1 \oplus \dots \oplus s_{n-1}x_{n-1}
$$

Reihenfolge-Konvention: Qubit $i$ trägt das Bit $x_i$, und Qubit 0 ist das **letzte** Zeichen der Folge. Für $s = 1000$ ist nur $s_3 = 1$ und $f(x) = x_3$; der Endzustand ist $|1000\rangle$, mit Qubit 3 in $|1\rangle$.

Das Orakel kann zusätzlich einen Bias $b$ addieren: $f(x) = s \cdot x \oplus b$. Das $b$ multipliziert den Zustand nur mit einer globalen Phase $(-1)^b$ und ändert die Antwort nicht.

Klassisch verrät jede Abfrage ein Bit von $s$ (durch Abfragen von $x = 0001$, $0010$, …), also braucht man $n$ Abfragen. Zufall hilft nicht: Jede Abfrage liefert höchstens 1 Bit Information, und $s$ hat $n$ Bits; mit weniger als $n$ Abfragen kann man also nicht mit hoher Wahrscheinlichkeit richtig liegen. Der Bernstein-Vazirani-Algorithmus gewinnt ganz $s$ mit **einer**.

## Derselbe Schaltkreis, eine andere Lesart

Der Schaltkreis ist der von Deutsch-Jozsa. Nach dem Orakel ist das Eingaberegister in

$$
\frac{1}{\sqrt{2^n}}\sum_x (-1)^{s\cdot x}|x\rangle
$$

und das ist genau der Zustand, den die Hadamards aus $|s\rangle$ erzeugen:

$$
H^{\otimes n}|s\rangle = \frac{1}{\sqrt{2^n}}\sum_x (-1)^{s\cdot x}|x\rangle
$$

Da das Hadamard sich selbst aufhebt ($HH = I$), liefert die letzte Hadamard-Schicht $|s\rangle$ zurück. Die Messung ergibt mit Sicherheit $s$.

## Wie das Orakel aufgebaut ist

Für jedes Bit $s_i = 1$ wendet das Orakel ein CNOT von Qubit $i$ auf das Hilfsqubit an. Mit dem Hilfsqubit in $|-\rangle$ gibt jedes dieser CNOTs das Vorzeichen $(-1)^{x_i}$ an Qubit $i$ zurück: wieder Phase Kickback.

## Im Labor

Im Tab **Amplituden** ist nach dem Orakel die Hälfte der Vorzeichen negativ, in einem Muster, das $s$ codiert. Nach den Hadamards konzentriert sich die gesamte Amplitude auf einen einzigen Zustand. Lies $s$ mit Qubit 0 rechts ab. Bei der Validierung wird der Schaltkreis mit mehreren geheimen Bitfolgen getestet.

## Hinweis zur Notation

Viele Lehrbücher schreiben Qubit 0 **links** in die Bezeichnung, etwa $|x_0 x_1 x_2\rangle$. Qiskit, und damit dieses Labor, schreibt Qubit 0 **rechts**: $|q_2 q_1 q_0\rangle$. Beim Vergleich mit einem Lehrbuch können die Bezeichnungen daher vertauscht erscheinen.
