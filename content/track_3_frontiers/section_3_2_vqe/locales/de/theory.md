## Chemie auf einem Quantencomputer

Die Eigenschaften eines Moleküls (wie es bindet, reagiert, Licht absorbiert) ergeben sich aus der Energie seiner Elektronen. Diese Energie exakt zu berechnen kostet auf einem klassischen Computer einen Aufwand, der exponentiell mit der Größe des Moleküls wächst. Die Simulation von Quantensystemen ist die natürlichste Anwendung eines Quantencomputers.

## Vom Hamilton-Operator zu den Qubits

Die Energie ergibt sich aus dem **Hamilton-Operator** $H$ der Elektronen. In der minimalen Basis STO-3G hat H₂ 4 Spinorbitale; jedes wird zu einem Qubit (besetzt = $|1\rangle$). Die **Jordan-Wigner-Abbildung** schreibt $H$ als Summe von Produkten von Pauli-Matrizen um:

$$
H = \sum_j c_j\, P_j, \qquad P_j \in \{I, X, Y, Z\}^{\otimes 4}
$$

Im Labor ist `H` bereits fertig: Es sind 15 Terme, berechnet für den Gleichgewichtsabstand von 0,74 Å.

## Das Variationsprinzip

Für jeden Zustand $|\psi\rangle$ gilt:

$$
E(\vec\theta) = \langle \psi(\vec\theta) | H | \psi(\vec\theta) \rangle \;\ge\; E_0
$$

Die Energie jedes Zustands ist größer oder gleich der des Grundzustands $E_0$. Es genügt also, Zustände mit einem parametrisierten Schaltkreis zu präparieren und $E(\vec\theta)$ zu minimieren: Je kleiner die Energie, desto näher am Grundzustand. Das ist der **VQE** (*variational quantum eigensolver*).

## Der chemische Ansatz

1. **Hartree-Fock**: die beiden Elektronen in den beiden Orbitalen mit der niedrigsten Energie, `hf_state = [1, 1, 0, 0]`. Das ist eine gute Näherung, ignoriert aber die Korrelation zwischen den Elektronen.
2. **Doppelanregung**: `qml.DoubleExcitation(θ)` mischt den Hartree-Fock-Zustand mit dem Zustand, in dem beide Elektronen gemeinsam in die leeren Orbitale springen:

$$
\cos\tfrac{\theta}{2}\,|1100\rangle \;-\; \sin\tfrac{\theta}{2}\,|0011\rangle
$$

(in der PennyLane-Notation, mit Wire 0 links). Für H₂ in dieser Basis genügt ein einziger Parameter, um die exakte Energie zu erreichen.

## Chemische Genauigkeit

Die Hartree-Fock-Energie beträgt $-1{,}1168$ Ha und die exakte $-1{,}1373$ Ha (die Gesamtenergie des Grundzustands, in Hartree). Der Unterschied wirkt klein, entscheidet aber über die Chemie. Der Standard ist, bis auf $1{,}6$ mHa an den exakten Wert heranzukommen (etwa 1 kcal/mol): die **chemische Genauigkeit**.

## Im Labor

- Der Tab **Konvergenz** zeigt die Energie bei jedem Schritt, mit der Linie der exakten Energie und dem Band der chemischen Genauigkeit.
- Der Tab **Dissoziation** zeigt, wie sich die Energie mit dem Abstand zwischen den Atomen ändert: die exakte Kurve, die Hartree-Fock-Kurve und dein Ergebnis bei 0,74 Å.
- In der **Q-Sphere** erscheinen die beiden Zustände, die der Ansatz mischt.

Klicke auf **Ausführen** (oder Ctrl+Enter), um zu trainieren.
