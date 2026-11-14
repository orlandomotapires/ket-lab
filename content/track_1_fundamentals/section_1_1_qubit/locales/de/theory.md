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

## Normierung

Nicht jedes Zahlenpaar ist ein Zustand. Die Amplituden müssen $|\alpha|^2 + |\beta|^2 = 1$ erfüllen. Zum Beispiel ist $(0{,}6;\ 0{,}8)$ ein gültiger Zustand, denn $0{,}36 + 0{,}64 = 1$. $(0{,}6;\ 0{,}6)$ dagegen nicht: Die Summe ist $0{,}72$. Um ihn gültig zu machen, teilt man den Vektor durch seine Norm (hier $\sqrt{0{,}72}$). Quantengatter erhalten diese Summe, ein Schaltkreis erzeugt also nie einen Vektor außerhalb der Kugel.

## Globale Phase

Multipliziert man den ganzen Zustand mit $e^{i\gamma}$, ändert sich keine Wahrscheinlichkeit und kein Ergebnis irgendeiner möglichen Messung: $|\psi\rangle$ und $e^{i\gamma}|\psi\rangle$ sind physikalisch derselbe Zustand, und die Bloch-Kugel zeichnet sie am selben Punkt. Wichtig ist die **relative** Phase zwischen $\alpha$ und $\beta$, das Thema von Lektion 1.3.

Deshalb bringen $Y$ und $R_x(\pi)$ den Zustand $|0\rangle$ in denselben physikalischen Zustand wie $X$: Die Ergebnisse unterscheiden sich nur durch eine globale Phase ($Y|0\rangle = i|1\rangle$ und $R_x(\pi)|0\rangle = -i|1\rangle$).

## So benutzt du das Labor

- Die Visualisierung folgt der **Zeile, in der sich der Cursor befindet**: Sie zeigt den Zustand des Qubits nach allem, was bis dorthin ausgeführt wurde.
- Du musst nicht auf „Ausführen“ klicken. Der Zustand wird neu berechnet, sobald du aufhörst zu tippen.
- Probiere ruhig aus, was passiert, wenn du zum Beispiel `qc.x(0)` zweimal anwendest.
