## Maschinelles Lernen mit Schaltkreisen

Ein Klassifikator erhält einen Punkt $\vec x$ und gibt eine Klasse zurück. Bei einem **Quantenklassifikator** gelangt der Punkt als Rotationswinkel in den Schaltkreis, und die Klasse kommt aus einer Messung. Die trainierbaren Gewichte sind weitere Winkel, die wie in den vorigen Lektionen per Gradient angepasst werden.

## Die Daten kodieren

Bevor klassische Daten verarbeitet werden können, müssen sie in einen Quantenzustand gebracht werden. Die gängigsten Arten:

- **Winkelkodierung**: Jede Koordinate wird zum Winkel einer Rotation, etwa $R_X(x_0)$ und $R_Y(x_1)$. Sie ist einfach vorzubereiten, braucht aber ein Qubit (oder ein Gatter) pro Koordinate.
- **Amplitudenkodierung**: Die $2^n$ Zahlen der Daten werden zu den Amplituden von $n$ Qubits. Sie ist kompakt, aber schwer vorzubereiten.
- **Phasenkodierung**: Die Daten gehen als relative Phasen ein.

Hier verwenden wir die Winkelkodierung.

## Data Re-Uploading

Gehen die Daten nur einmal ein, ist die Ausgabe des Schaltkreises eine einfache trigonometrische Funktion von $\vec x$ und kann keine komplizierten Grenzen zeichnen. Der Ausweg ist, die Daten mehrmals **erneut zu laden** und mit trainierbaren Schichten abzuwechseln:

$$
U(\vec x, \vec w) = W_L\, S(\vec x)\, W_{L-1}\, S(\vec x) \cdots W_1\, S(\vec x)\, W_0
$$

Jedes erneute Laden bereichert die Funktion, die der Schaltkreis darstellt, wie die zusätzlichen Terme einer Fourier-Reihe.

## Der Klassifikator

- **Eingabe:** Punkte $(x_0, x_1)$ auf zwei konzentrischen Kreisen; die äußeren haben die Klasse $+1$ und die inneren $-1$. Eine Gerade trennt die beiden Klassen nicht.
- **Ausgabe:** $\langle Z_0 \rangle$ zwischen $-1$ und $+1$; das Vorzeichen ist die vorhergesagte Klasse.
- **Training:** den mittleren quadratischen Fehler zwischen $\langle Z_0\rangle$ und den Labels minimieren, mit dem Adam-Optimierer.

Der Schaltkreis verarbeitet alle Punkte auf einmal: Hat `x` die Form $(N, 2)$, führt PennyLane die $N$ Versionen des Schaltkreises parallel aus (*Broadcasting*).

## Verallgemeinern, nicht auswendig lernen

Entscheidend ist, Punkte richtig zu erkennen, die das Modell **nicht gesehen** hat. Deshalb verwendet die Validierung einen separaten Testdatensatz. Hohe Genauigkeit im Training und niedrige im Test ist ein Zeichen dafür, dass das Modell die Beispiele auswendig gelernt hat (*Overfitting*, Überanpassung).

## Im Labor

- Der Tab **Entscheidungsgrenze** zeigt die Ausgabe des Schaltkreises über die ganze Ebene, mit den Trainingspunkten darüber.
- Der Tab **Konvergenz** zeigt den Verlust in jeder Epoche.

Der Startcode lädt die Daten nur einmal. Klicke auf **Ausführen** (oder Ctrl+Enter), um zu trainieren.
