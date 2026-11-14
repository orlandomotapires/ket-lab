## Von der Position zur Frequenz

Die diskrete Fourier-Transformation bildet eine Zahlenfolge auf ihr Frequenzspektrum ab. Die **Quanten-Fourier-Transformation** (QFT) tut dasselbe mit den Amplituden eines Zustands aus $n$ Qubits, mit $N = 2^n$:

$$
\text{QFT}\,|x\rangle = \frac{1}{\sqrt{N}}\sum_{k=0}^{N-1} e^{2\pi i\, xk/N}\,|k\rangle
$$

Alle Ausgaben haben dieselbe Wahrscheinlichkeit, $1/N$. Die Information über $x$ steckt vollständig in den **Phasen**: Die Amplitude von $|k\rangle$ dreht sich um $xk/N$ einer vollen Umdrehung.

## Die Produktform

Derselbe Ausdruck lässt sich Qubit für Qubit faktorisieren: Jedes Qubit endet auf dem Äquator der Bloch-Kugel, mit einer Phase proportional zu $x$. Eines dreht sich um $x/2$ einer Umdrehung, ein anderes um $x/4$, ein weiteres um $x/8$. Diese Form liefert den Schaltkreis: Ein Hadamard erzeugt den Äquator, und von den anderen Qubits kontrollierte Phasen fügen die kleineren Bruchteile hinzu.

## Der Schaltkreis

Für 3 Qubits, beginnend mit dem höchstwertigen (Qubit 2):

1. $H$ auf Qubit 2; danach die Phase $\pi/2$ kontrolliert von Qubit 1 und die Phase $\pi/4$ kontrolliert von Qubit 0.
2. $H$ auf Qubit 1; danach die Phase $\pi/2$ kontrolliert von Qubit 0.
3. $H$ auf Qubit 0.
4. `swap` zwischen den Qubits 0 und 2: Der Schaltkreis liefert die Qubits in umgekehrter Reihenfolge.

Die kontrollierte Phase ist `qc.cp(winkel, kontrolle, ziel)`, das Gatter

$$
R(\varphi) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\varphi} \end{pmatrix}
$$

das auf das Ziel angewendet wird, wenn die Kontrolle $1$ ist.

## Zwei Anmerkungen

**Die abschließenden Swaps.** Ohne Schritt 4 berechnet der Schaltkreis die QFT mit den Ausgabequbits in umgekehrter Reihenfolge. Manche Texte lassen die Swaps weg und lesen das Ergebnis rückwärts oder überlassen die Umordnung den Nutzern. Hier bleiben sie im Schaltkreis, damit die Ausgabe in Qiskits Konvention mit der DFT übereinstimmt.

**Hadamard und Fourier.** Die Hadamard-Transformation $H^{\otimes n}$ ist die Fourier-Transformation über der Gruppe $(\mathbb{Z}_2)^n$, deren „Charaktere" $(-1)^{s\cdot x}$ sind. Für ein einzelnes Qubit gilt $2^1 = 2$, und die QFT stimmt mit dem Hadamard überein. Darauf beruhte Bernstein-Vazirani; die QFT hier ist die Version über $\mathbb{Z}_{2^n}$ mit den Phasen $e^{2\pi i\,xk/2^n}$.

## Im Labor

Die Funktion `prepare_input(qc)` bereitet die Eingabe $|x\rangle$ vor, hier $|101\rangle = |5\rangle$. Der Tab **Phasen** zeigt pro Zustand ein Zifferblatt: Die Größe zeigt die Wahrscheinlichkeit an und der Zeiger die Phase. Nach der QFT drehen sich die Zeiger um $5k/8$ einer Umdrehung, in gleichen Schritten von einem Zustand zum nächsten. Bei der Validierung wird der Schaltkreis mit mehreren Eingaben getestet, auch mit Superpositionen.
