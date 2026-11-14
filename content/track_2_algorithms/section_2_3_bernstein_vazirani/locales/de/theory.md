## Das Problem

Jetzt ist die geheime Funktion das bitweise Produkt von $x$ mit einer geheimen Bitfolge $s$ aus $n$ Bits, modulo 2:

$$
f(x) = s \cdot x = s_0x_0 \oplus s_1x_1 \oplus \dots \oplus s_{n-1}x_{n-1}
$$

Klassisch verrät jede Abfrage ein Bit von $s$ (durch Abfragen von $x = 0001$, $0010$, …), also braucht man $n$ Abfragen. Der Bernstein-Vazirani-Algorithmus gewinnt ganz $s$ mit **einer**.

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
