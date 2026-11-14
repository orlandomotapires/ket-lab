## Gleiche Wahrscheinlichkeiten, verschiedene Zustände

Vergleiche die beiden Zustände, die das Hadamard erzeugt:

$$
|+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}
\qquad
|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}
$$

Gemessen liefern beide $0$ oder $1$ mit je $50\%$ Wahrscheinlichkeit. Trotzdem sind es verschiedene Zustände, auf gegenüberliegenden Seiten des Äquators. Der Unterschied liegt im Vorzeichen zwischen den beiden Summanden: der **relativen Phase**.

Allgemein lautet ein Zustand auf dem Äquator

$$
\frac{|0\rangle + e^{i\phi}|1\rangle}{\sqrt{2}}
$$

und der Winkel $\phi$ gibt an, an welcher Stelle des Äquators der Vektor liegt: $\phi = 0$ ist $|+\rangle$ und $\phi = \pi$ ist $|-\rangle$.

## Phasengatter

Die Gatter dieser Lektion drehen den Vektor um die $Z$-Achse. Sie verändern $\phi$ und lassen die Wahrscheinlichkeiten unangetastet:

| Gatter | Drehung um Z |
| :-- | :-- |
| $Z$ | $180°$ |
| $S$ | $90°$ |
| $T$ | $45°$ |
| $R_z(\theta)$ | $\theta$, beliebiger Winkel |

## Warum das wichtig ist

Eine gewöhnliche Messung sieht die Phase nicht. Aber die nachfolgenden Gatter sehen sie: Die Phase entscheidet, ob sich Amplituden addieren oder auslöschen. Das ist das Thema der nächsten Lektion.

## Im Labor

Beobachte die Spalte **Phase** in der Tabelle rechts, den Zeiger neben jeder Amplitude und die Farbe des Vektors. Die Wahrscheinlichkeitsbalken bewegen sich nicht, solange du um $Z$ drehst.
