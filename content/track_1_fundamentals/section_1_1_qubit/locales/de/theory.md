## Vom Bit zum Qubit

Ein klassisches Bit kann nur einen von zwei Werten annehmen: $0$ oder $1$. Ein **Qubit** hat ebenfalls zwei Referenzzustände, geschrieben $|0\rangle$ und $|1\rangle$, kann aber in jeder Kombination aus beiden sein:

$$
|\psi\rangle = \alpha|0\rangle + \beta|1\rangle
$$

Die Zahlen $\alpha$ und $\beta$ sind die **Amplituden**. Sie sind keine Wahrscheinlichkeiten, bestimmen sie aber: Wenn du das Qubit misst, erhältst du $0$ mit der Wahrscheinlichkeit $|\alpha|^2$ und $1$ mit der Wahrscheinlichkeit $|\beta|^2$. Da immer irgendein Ergebnis eintritt, gilt

$$
|\alpha|^2 + |\beta|^2 = 1
$$

## Die Bloch-Kugel

Jeder Zustand eines Qubits entspricht einem Punkt auf der Oberfläche einer Kugel. Der Nordpol ist $|0\rangle$ und der Südpol ist $|1\rangle$. Rechts zeigt der Vektor, wo sich dein Qubit gerade befindet.

In dieser Lektion besucht der Vektor nur die beiden Pole. Die übrigen Punkte der Kugel kommen ab der nächsten Lektion vor.

## Das X-Gatter

Quantengatter bewegen den Vektor über die Kugel. Das **Pauli-X** dreht ihn um $180°$ um die $X$-Achse:

$$
X|0\rangle = |1\rangle \qquad X|1\rangle = |0\rangle
$$

Es macht mit dem Qubit, was `NOT` mit einem Bit macht.

## So benutzt du das Labor

- Die Visualisierung folgt der **Zeile, in der sich der Cursor befindet**: Sie zeigt den Zustand des Qubits nach allem, was bis dorthin ausgeführt wurde.
- Du musst nicht auf „Ausführen“ klicken. Der Zustand wird neu berechnet, sobald du aufhörst zu tippen.
- Probiere ruhig aus, was passiert, wenn du zum Beispiel `qc.x(0)` zweimal anwendest.
