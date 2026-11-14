## Zwei Qubits

Mit zwei Qubits gibt es vier Basiszustände: $|00\rangle$, $|01\rangle$, $|10\rangle$ und $|11\rangle$. Ein allgemeiner Zustand ist eine Kombination aus allen vieren:

$$
|\psi\rangle = a_{00}|00\rangle + a_{01}|01\rangle + a_{10}|10\rangle + a_{11}|11\rangle
$$

Bei $n$ Qubits sind es $2^n$ Amplituden. Dieses Wachstum macht es klassischen Computern schwer, Quantencomputer zu simulieren.

## Die Reihenfolge der Qubits

Auf dieser Plattform steht, wie in Qiskit, **Qubit 0 rechts** im Label: In $|q_1 q_0\rangle$ bedeutet der Zustand $|01\rangle$, dass Qubit 0 in $1$ und Qubit 1 in $0$ ist. Die Konvention wirkt anfangs verkehrt, ist aber dieselbe wie bei einer Binärzahl: Das niederwertigste Bit steht rechts.

## Zustände, die sich trennen lassen, und solche, die es nicht tun

Wenn jedes Qubit seinen eigenen Zustand hat, ist der gemeinsame Zustand das **Tensorprodukt** der beiden:

$$
|+\rangle \otimes |0\rangle = \frac{|00\rangle + |10\rangle}{\sqrt{2}}
$$

Manche Zwei-Qubit-Zustände lassen sich **nicht** so schreiben. Der berühmteste ist der Bell-Zustand

$$
|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}
$$

Es gibt keinen Zustand von Qubit 0 und keinen Zustand von Qubit 1, deren Produkt $|\Phi^+\rangle$ ergibt. Die beiden Qubits sind **verschränkt**: Der Zustand existiert nur für das Paar.

## Das CNOT-Gatter

Das CNOT (*controlled NOT*) wirkt auf zwei Qubits: Es kehrt das **Ziel** um, wenn die **Kontrolle** $1$ ist, und tut nichts, wenn sie $0$ ist. Auf eine Superposition in der Kontrolle angewendet, erzeugt es Verschränkung:

$$
\text{CNOT}\,\frac{|00\rangle + |01\rangle}{\sqrt{2}} = \frac{|00\rangle + |11\rangle}{\sqrt{2}}
$$

## Worauf du im Labor achten solltest

- **Q-Sphere**: Jeder Punkt ist ein Basiszustand. Die Punkte liegen weiter im Süden, je mehr $1$en das Label hat; die Größe zeigt die Wahrscheinlichkeit an und die Farbe die Phase.
- **Bloch-Kugeln**: Ein verschränktes Qubit hat keinen eigenen Zustand. Sein Vektor schrumpft bis zum Mittelpunkt der Kugel ($|r| = 0$).
- **Verschränkung**: Die Concurrence reicht von $0$ (separabler Zustand) bis $1$ (maximale Verschränkung).
