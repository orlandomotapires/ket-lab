## Unstrukturierte Suche

Unter $N$ Elementen sind einige markiert (insgesamt $M$), und nur ein Orakel weiß, welche. Ein klassischer Algorithmus muss im Mittel $N/2$ Elemente testen. Der Grover-Algorithmus findet das markierte mit etwa $\frac{\pi}{4}\sqrt{N}$ Abfragen: eine quadratische Beschleunigung.

## Das Phasenorakel

Hier kehrt das Orakel nur das Vorzeichen des markierten Zustands $|\omega\rangle$ um:

$$
U_\omega|x\rangle = \begin{cases} -|x\rangle & \text{falls } x = \omega \\ \phantom{-}|x\rangle & \text{falls } x \neq \omega \end{cases}
$$

Allein ändert diese Umkehrung keine Wahrscheinlichkeit.

## Der Diffusor: Spiegelung am Mittelwert

Der **Diffusor** $D = 2|s\rangle\langle s| - I$, wobei $|s\rangle$ die gleichmäßige Superposition ist, spiegelt jede Amplitude am Mittelwert aller Amplituden:

$$
a_x \;\longrightarrow\; 2\bar{a} - a_x
$$

Nach dem Orakel ist die markierte Amplitude negativ und zieht den Mittelwert ein wenig nach unten. Die Spiegelung wirft sie weit über den Mittelwert, und die übrigen schrumpfen ein wenig.

Im Schaltkreis ist $D = H^{\otimes n}\,(2|0\rangle\langle 0| - I)\,H^{\otimes n}$. Die Spiegelung an $|0000\rangle$ wird, bis auf eine globale Phase, mit $X$ auf allen Qubits, einem mehrfach kontrollierten $Z$ und erneut $X$ umgesetzt. Das mehrfach kontrollierte $Z$ entsteht aus einem verallgemeinerten Toffoli zwischen zwei Hadamards:

```python
qc.h(3)
qc.mcx([0, 1, 2], 3)
qc.h(3)
```

## Wie viele Iterationen

Bei $M$ markierten Elementen unter $N$ gilt $\sin\theta = \sqrt{M/N}$. Jede Iteration (Orakel und Diffusor) dreht den Zustand um den Winkel $2\theta$ in Richtung des Unterraums der markierten Elemente; nach $k$ Iterationen ist die Erfolgswahrscheinlichkeit $\sin^2\big((2k+1)\theta\big)$. Das beste $k$ ist

$$
k = \left\lfloor \frac{\pi}{4}\sqrt{\frac{N}{M}} \right\rfloor
$$

Für $N = 16$:

| $M$ | $k$ | Erfolgswahrscheinlichkeit |
| :-: | :-: | :-: |
| 1 | 3 | $96{,}1\,\%$ |
| 2 | 2 | $94{,}5\,\%$ |
| 4 | 1 | $100\,\%$ |

Mehr Iterationen als ideal schießen über das Ziel hinaus, und die Wahrscheinlichkeit sinkt wieder. Wer $M$ nicht kennt, muss es daher zuerst schätzen (etwa mit Quantenzählen, das die Phasenschätzung nutzt).

## Grenzen

Die Beschleunigung ist **quadratisch** ($\sqrt{N}$ gegen $N$), nicht exponentiell, und für unstrukturierte Suche optimal. Grover macht NP-vollständige Probleme auch **nicht** leicht: Dafür sind weiterhin $2^{n/2}$ Abfragen nötig, was in $n$ exponentiell bleibt.

## Im Labor

Der Tab **Amplituden** zeigt die 16 Amplituden mit Vorzeichen und die gestrichelte Linie des Mittelwerts. Gehe Schritt für Schritt vor: Das Orakel wirft den markierten Balken nach unten, und der Diffusor wirft ihn über den Mittelwert. Das markierte Element ist hier geheim; bei der Validierung wird der Schaltkreis mit mehreren markierten Elementen getestet.
