## Schaltkreise mit Parametern

Bisher hatte jedes Gatter einen festen Winkel. Ein **variationeller Schaltkreis** hat einstellbare Winkel $\vec\theta$, und das Ergebnis einer Messung wird zu einer Funktion davon:

$$
f(\vec\theta) = \langle \psi(\vec\theta) |\, O \,| \psi(\vec\theta) \rangle
$$

wobei $O$ eine Observable ist, zum Beispiel $Z$. Ein klassischer Computer wählt die Winkel, der Quantencomputer wertet $f$ aus, und der klassische passt die Winkel an, um $f$ zu minimieren. Diese hybride Schleife ist die Grundlage von VQE, QAOA und den Quantum-Neural-Networks der nächsten Lektionen.

Der Schaltkreis mit Parametern heißt **Ansatz**. Ein guter Ansatz erreicht genug Zustände, um die Lösung zu enthalten (**Ausdrucksstärke**), ohne so groß zu sein, dass er sich nicht mehr trainieren lässt.

## PennyLane

In diesem Lernpfad sind die Schaltkreise in PennyLane geschrieben, das Gradienten von Quantenschaltkreisen berechnet:

- `qml.device("default.qubit", wires=1)` erstellt einen 1-Qubit-Simulator;
- `@qml.qnode(dev)` macht aus einer Python-Funktion einen ausführbaren Schaltkreis, den **QNode**;
- die Funktion wendet Gatter an, etwa `qml.RX(θ, wires=0)`, und gibt eine Messung zurück, etwa `qml.expval(qml.PauliZ(0))`;
- `from pennylane import numpy as np` liefert ein NumPy, das PennyLane ableiten kann.

Die Plattform zeigt die Qubits in derselben Reihenfolge wie die anderen Lernpfade: Qubit 0 steht in den Beschriftungen rechts.

## Die Parameter-Shift-Regel

Um $f$ zu minimieren, braucht man den Gradienten. Auf einem echten Quantencomputer kann man nicht in den Schaltkreis „hineinschauen“, und finite Differenzen, $[f(\theta + \epsilon) - f(\theta)]/\epsilon$, gehen im Messrauschen unter. Für Rotationsgatter wie $R_X$ und $R_Y$ ist die Ableitung jedoch exakt aus zwei Ausführungen des Schaltkreises selbst:

$$
\frac{\partial f}{\partial \theta_i} = \frac{f\!\left(\theta_i + \frac{\pi}{2}\right) - f\!\left(\theta_i - \frac{\pi}{2}\right)}{2}
$$

wobei die übrigen Parameter fest bleiben. Die Verschiebungen sind groß, $\pm\pi/2$, daher fällt das Messrauschen wenig ins Gewicht. Das ist die **Parameter-Shift-Regel**.

## Gradientenabstieg

Mit dem Gradienten geht jeder Schritt ein Stück in Abstiegsrichtung:

$$
\vec\theta \;\leftarrow\; \vec\theta - \eta\, \nabla f(\vec\theta)
$$

Die **Lernrate** $\eta$ steuert die Schrittgröße: Zu klein macht das Training langsam; zu groß lässt den Optimierer über das Minimum springen.

## In diesem Labor

Die Kostenfunktion ist $\langle Z\rangle$ nach $R_X(\theta_0)$ und $R_Y(\theta_1)$ und ergibt $\cos\theta_0 \cos\theta_1$. Das Minimum, $-1$, ist der Südpol der Bloch-Kugel.

- Der Tab **Landschaft** zeigt die Kostenfunktion für alle Winkel, mit der Trajektorie deines Optimierers.
- Der Tab **Konvergenz** zeigt die Kostenfunktion Schritt für Schritt.
- Die **Bloch-Kugeln** zeigen den Zustand mit den endgültigen Parametern.

Da das Training einige Augenblicke dauert, läuft der Code, wenn du auf **Ausführen** klickst oder Ctrl+Enter drückst.
