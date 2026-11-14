## Das Max-Cut-Problem

Gegeben ist ein Graph. Teile die Knoten in zwei Gruppen, sodass möglichst viele Kanten Knoten verschiedener Gruppen verbinden („geschnittene“ Kanten). Das ist ein NP-schweres Problem: Für große Graphen kennt man keinen effizienten Algorithmus, der das Optimum garantiert. Es tritt beim Schaltungsentwurf, beim Clustern von Daten und in der statistischen Physik auf.

In diesem Graphen mit 5 Knoten und 6 Kanten beträgt der beste Schnitt 5.

## Vom Graphen zu den Qubits

Jeder Knoten wird zu einem Qubit: $|0\rangle$ und $|1\rangle$ geben die Gruppe an. Eine Kante $(i, j)$ ist geschnitten, wenn sich die Bits unterscheiden, also wenn $Z_i Z_j = -1$ gilt. Dann ist

$$
\text{Schnitt} = \sum_{(i,j)} \frac{1 - Z_i Z_j}{2}
$$

und den Schnitt zu maximieren ist dasselbe, wie die Ising-Energie $H_C = \sum_{(i,j)} Z_i Z_j$ zu **minimieren**. Im Labor ist `cost_h` dieses $H_C$.

## Das QAOA

Der *Quantum Approximate Optimization Algorithm* wechselt zwischen zwei Arten von Schichten ab und beginnt bei der gleichförmigen Superposition:

$$
|\vec\gamma, \vec\beta\rangle = U_M(\beta_p)\,U_C(\gamma_p) \cdots U_M(\beta_1)\,U_C(\gamma_1)\,|+\rangle^{\otimes n}
$$

- **Kosten**, $U_C(\gamma) = e^{-i\gamma H_C/2}$: ein `IsingZZ(γ)` auf jeder Kante. Es prägt den Amplituden eine Phase auf, die vom Schnitt abhängt.
- **Mischung**, $U_M(\beta) = e^{-i\beta \sum X}$: ein `RX(2β)` auf jedem Qubit. Es verwandelt diese Phasen durch Interferenz in Änderungen der Wahrscheinlichkeit.

Ein klassischer Optimierer passt die $2p$ Winkel an, um $\langle H_C \rangle$ zu minimieren. Das ist derselbe hybride Zyklus wie in den vorigen Lektionen.

## Das Approximationsverhältnis

Das Ergebnis wird am **Approximationsverhältnis** gemessen: dem erwarteten Schnitt des Endzustands geteilt durch den maximalen Schnitt. Ein Verhältnis von 1 würde bedeuten, immer die optimale Lösung zu messen. Je größer $p$, desto näher kann das QAOA an 1 herankommen; für $p \to \infty$ gewinnt es das Quanten-Annealing (*quantum annealing*) zurück.

## Im Labor

- Der Tab **Graph** zeigt die Knoten, eingefärbt nach dem wahrscheinlichsten Schnitt, mit hervorgehobenen geschnittenen Kanten, sowie das Approximationsverhältnis.
- Der Tab **Konvergenz** zeigt das Verhältnis bei jedem Schritt, mit der Schwelle von 0,85.
- Der Tab **Register** zeigt die Wahrscheinlichkeit jeder der 32 Aufteilungen.

Der Startcode verwendet nur eine Schicht. Klicke auf **Ausführen** (oder Ctrl+Enter), um zu trainieren.
