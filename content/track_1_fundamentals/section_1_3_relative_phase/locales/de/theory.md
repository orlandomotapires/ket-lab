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

## Eine Folge rückgängig machen

Jedes Quantengatter hat ein Inverses: das Gatter, das seine Wirkung aufhebt. Für eine Folge $U_3 U_2 U_1$ (angewendet in der Reihenfolge $U_1$, $U_2$, $U_3$) ist das Inverse die Folge der Inversen **in umgekehrter Reihenfolge**:

$$
(U_3 U_2 U_1)^{-1} = U_1^{\dagger}\, U_2^{\dagger}\, U_3^{\dagger}
$$

Das ist wie das Zurücknehmen von Arbeitsschritten: Was zuletzt getan wurde, wird zuerst zurückgenommen. Da $H$ und $X$ ihre eigenen Inversen sind, brauchen nur $S$ und $T$ neue Gatter:

| Gatter | Inverses | In Qiskit |
| :-- | :-- | :-- |
| $S$ (Drehung um $90°$) | $S^{\dagger}$ (Drehung um $-90°$) | `qc.sdg(0)` |
| $T$ (Drehung um $45°$) | $T^{\dagger}$ (Drehung um $-45°$) | `qc.tdg(0)` |

Das Rückgängigmachen funktioniert für **jede** Eingabe, auch für unbekannte, weil die Identität für alle Zustände gleichzeitig gilt.

## Rz und das Phasengatter

Das Phasengatter $P(\theta) = \mathrm{diag}(1, e^{i\theta})$ und die Rotation $R_z(\theta) = \mathrm{diag}(e^{-i\theta/2}, e^{i\theta/2})$ unterscheiden sich nur durch eine globale Phase ($R_z(\theta) = e^{-i\theta/2} P(\theta)$). Für ein einzelnes Qubit sind sie dasselbe Gatter. Der Unterschied zeigt sich erst, wenn eines von beiden kontrolliert wird, wie wir in Lektion 1.7 sehen.

## Im Labor

Beobachte die Spalte **Phase** in der Tabelle rechts, den Zeiger neben jeder Amplitude und die Farbe des Vektors. Die Wahrscheinlichkeitsbalken bewegen sich nicht, solange du um $Z$ drehst.
