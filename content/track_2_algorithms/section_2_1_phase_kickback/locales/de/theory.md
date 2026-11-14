## Eigenzustände

Ein Zustand ist **Eigenzustand** eines Gatters, wenn das Gatter ihn nicht verändert, abgesehen von einem Faktor:

$$
U|\psi\rangle = e^{i\varphi}|\psi\rangle
$$

Der Faktor $e^{i\varphi}$ ist der **Eigenwert**. Der Zustand $|-\rangle$ ist Eigenzustand des Gatters $X$, mit Eigenwert $-1$:

$$
X|-\rangle = \frac{|1\rangle - |0\rangle}{\sqrt{2}} = -|-\rangle
$$

Für sich allein ist dieses Vorzeichen eine globale Phase und ändert nichts, was sich messen ließe.

## Das CNOT aus einem anderen Blickwinkel

Zur Übersichtlichkeit steht die Kontrolle links: Mit dem Ziel in $|-\rangle$ wendet das CNOT $X$ nur dann auf das Ziel an, wenn die Kontrolle $1$ ist, und jede Anwendung erzeugt das Vorzeichen $-1$:

$$
\text{CNOT}\,|x\rangle|-\rangle = (-1)^x\,|x\rangle|-\rangle
$$

Das Ziel bleibt in $|-\rangle$. Das Vorzeichen ist beim Term der Kontrolle geblieben. Wenn die Kontrolle in Superposition ist, ist das Vorzeichen nicht mehr global, sondern wird zur relativen Phase:

$$
\text{CNOT}\,|+\rangle|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}\,|-\rangle = |-\rangle|-\rangle
$$

## Phase Kickback

Das Gatter wirkt „auf das Ziel“, aber es ändert sich die Kontrolle. Dieser Effekt heißt **Phase Kickback** und gilt für jedes kontrollierte Gatter: Ist das Ziel Eigenzustand von $U$ mit Eigenwert $e^{i\varphi}$, kehrt die Phase $e^{i\varphi}$ zum Term $|1\rangle$ der Kontrolle zurück.

## Warum das wichtig ist

Es ist der Mechanismus fast aller Algorithmen dieses Tracks. Deutsch-Jozsa und Bernstein-Vazirani verwenden ein Hilfsqubit in $|-\rangle$, um die Antwort einer Funktion in eine Phase zu verwandeln. Die Phasenschätzung nutzt denselben Trick mit einem beliebigen Gatter, und der Shor-Algorithmus baut darauf auf.

## Im Labor

In den **Bloch-Kugeln** springt der Vektor der Kontrolle im Schritt des CNOT von $+x$ nach $-x$, während der des Ziels stillsteht. Vergleiche das mit dem, was passiert, wenn das Ziel in $|0\rangle$ oder $|1\rangle$ ist: Dann verschränkt das CNOT die Qubits, wie in der Lektion zu den Bell-Zuständen.
