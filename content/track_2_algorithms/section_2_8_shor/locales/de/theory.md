## Faktorisieren heißt, eine Periode zu finden

Die Sicherheit der RSA-Verschlüsselung beruht darauf, dass große Zahlen schwer zu faktorisieren sind. Shor zeigte, dass sich das Faktorisieren einer zusammengesetzten Zahl $N$ darauf zurückführen lässt, die **Periode** der Funktion

$$
f(x) = a^x \bmod N
$$

zu finden, für ein zufällig gewähltes $a$ ohne gemeinsame Teiler mit $N$. Die Periode $r$ ist die kleinste positive ganze Zahl mit $a^r \bmod N = 1$.

Mit $N = 15$ und $a = 7$ lautet die Folge $7^x \bmod 15$: $1, 7, 4, 13, 1, 7, 4, 13, \dots$, und die Periode ist $r = 4$.

## Von der Periode zu den Faktoren

Wenn $r$ gerade ist, ist $a^r - 1 = (a^{r/2} - 1)(a^{r/2} + 1)$ ein Vielfaches von $N$, und jeder der beiden Faktoren hat mit $N$ einen gemeinsamen Teiler:

$$
\text{ggT}(a^{r/2} - 1,\, N) \qquad \text{und} \qquad \text{ggT}(a^{r/2} + 1,\, N)
$$

Mit $r = 4$: $7^2 = 49$, $\text{ggT}(48, 15) = 3$ und $\text{ggT}(50, 15) = 5$.

## Der Quantenteil

Die modulare Multiplikation $U|y\rangle = |7y \bmod 15\rangle$ ist eine unitäre Operation mit Eigenwerten $e^{2\pi i\,s/r}$. Beginnt man das Arbeitsregister in $|1\rangle$ und wendet die Phasenschätzung aus der vorigen Lektion an, misst das Zählregister $s/r$ für ein zufällig gezogenes $s$ zwischen $0$ und $r - 1$. Mit 4 Zählqubits sind die möglichen Ergebnisse $16 \cdot s/4 = 0,\ 4,\ 8,\ 12$.

## Klassische Nachbearbeitung

Für jedes Ergebnis $m$ ist die Phase $m/16$. Der nächstgelegene Bruch mit kleinem Nenner verrät $r$:

```python
from fractions import Fraction
Fraction(12 / 16).limit_denominator(15)   # 3/4, also r = 4
```

Nicht jedes Ergebnis taugt: $m = 0$ liefert keine Information, und $m = 8$ ergibt $r = 2$, was nicht die Periode ist (Probe: $7^2 \bmod 15 = 4 \neq 1$). Deshalb steht die Prüfung `pow(a, r, N) == 1` vor der Verwendung von $r$, und deshalb kombiniert der Algorithmus mehrere Messungen.

## Wie man $a$ wählt und wann es scheitert

Wähle $a$ zufällig mit $1 < a < N$. Gilt $\text{ggT}(a, N) \neq 1$, ist der ggT bereits ein Faktor, und es braucht keinen Quantenschritt. Andernfalls scheitert ein Versuch, wenn:

- $r$ **ungerade** ist: $a^r - 1$ lässt sich nicht in zwei Faktoren zerlegen;
- $a^{r/2} \equiv -1 \pmod N$ gilt: Dann ist $a^{r/2} + 1$ ein Vielfaches von $N$, und die beiden ggT sind $1$ und $N$. Beispiel: $a = 14 \equiv -1 \pmod{15}$ hat $r = 2$ und $14^1 \equiv -1$, man lernt nichts.

Für ein zufällig gezogenes $a$ gelingt jeder Lauf mit Wahrscheinlichkeit über 50 %; scheitert er, zieht man ein neues $a$ und wiederholt.

## Der Kettenbruch-Schritt

Das Ergebnis $m$ nähert $s/r$ durch $m/2^t$ an. Um $r$ zurückzugewinnen, entwickelt man $m/2^t$ in einen Kettenbruch und nimmt den Näherungsbruch mit Nenner höchstens $N$. Genau das tut `limit_denominator(N)`. Mit $2^t \geq N^2$ ist der richtige Näherungsbruch garantiert (für $N = 15$ wären das $t = 8$ Zählqubits); hier, mit $N = 15$ und 4 Qubits, ist das Problem klein genug, dass es trotzdem funktioniert.

## Im Labor

- `apply_controlled_mod_mult(qc, kontrolle, potenz)` multipliziert das Arbeitsregister (Qubits 4 bis 7) mit $7^{\text{Potenz}} \bmod 15$, kontrolliert vom angegebenen Qubit.
- `inverse_qft(qc, qubits)` ist die inverse QFT.
- `run_shots(qc)` führt den Schaltkreis 1024-mal aus und liefert die Zählungen.

Der Tab **Periode** zeigt $7^x \bmod 15$; der Tab **Register** zeigt die Spitzen des Zählregisters.
