## Das Problem

Alice hat ein Qubit in einem Zustand $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$, den sie **nicht kennt**, und möchte es Bob übergeben, der weit entfernt ist. Sie kann das Qubit nicht messen und ihm die Zahlen schicken: Eine Messung liefert nur ein Bit und zerstört die Superposition. Sie kann es auch nicht kopieren: Das **No-Cloning-Theorem** verbietet das Kopieren eines unbekannten Quantenzustands.

## Die Ressource: ein verschränktes Paar

Bevor sie sich trennten, haben Alice und Bob ein Bell-Paar erzeugt: Qubit 1 blieb bei Alice und Qubit 2 bei Bob. Mit diesem Paar und **zwei Bits klassischer Kommunikation** lässt sich der Zustand übertragen.

## Das Protokoll

1. **Bell-Paar** zwischen den Qubits 1 und 2: $H$ auf Qubit 1 und CNOT von 1 nach 2.
2. **Alice verschränkt** ihren Zustand mit ihrer Hälfte des Paares: CNOT von 0 nach 1, dann $H$ auf Qubit 0.
3. **Alice misst** die Qubits 0 und 1 und schickt die beiden Bits an Bob.
4. **Bob korrigiert**: Er wendet $X$ an, wenn das Bit von Qubit 1 den Wert $1$ hat, und danach $Z$, wenn das Bit von Qubit 0 den Wert $1$ hat.

Nach Schritt 3 ist Bobs Qubit je nach Messergebnis in einem von vier Zuständen. Jeder ist $|\psi\rangle$ mit einem bekannten „Fehler“, und die Korrektur aus Schritt 4 macht genau diesen Fehler rückgängig:

| Gemessene Bits (q1 q0) | Bobs Zustand | Korrektur |
| :-- | :-- | :-- |
| 00 | $\alpha|0\rangle + \beta|1\rangle$ | keine |
| 01 | $\alpha|0\rangle - \beta|1\rangle$ | $Z$ |
| 10 | $\beta|0\rangle + \alpha|1\rangle$ | $X$ |
| 11 | $\beta|0\rangle - \alpha|1\rangle$ | $X$, dann $Z$ |

## Bedingte Korrekturen in Qiskit

Ein Gatter, das von einem gemessenen Bit abhängt, schreibt man so:

```python
with qc.if_test((qc.clbits[1], 1)):
    qc.x(2)
```

## Nichts reist schneller als das Licht

Ohne die beiden Bits hat Bob mit je 25 % Wahrscheinlichkeit einen der vier Zustände, und diese Mischung enthält keinerlei Information über $|\psi\rangle$. Die Teleportation hängt von der klassischen Nachricht ab, die sich höchstens mit Lichtgeschwindigkeit ausbreitet.

## Im Labor

Der Tab **Alice × Bob** vergleicht den ursprünglichen Zustand von Alice mit dem aktuellen Zustand von Bob. Verfolge das Protokoll mit der Zeitleiste Schritt für Schritt und nutze „Erneut würfeln“, um andere Messergebnisse zu sehen: Mit den richtigen Korrekturen endet Bob in allen Fällen gleich wie Alice.
