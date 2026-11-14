## Warum Fehler korrigieren

Echte Qubits machen Fehler: Das Rauschen aus der vorigen Lektion summiert sich mit jedem Gatter. Bei langen Berechnungen müssen Fehler während der Rechnung erkannt und rückgängig gemacht werden. Das erscheint aus drei Gründen unmöglich: Ein unbekannter Zustand lässt sich nicht kopieren (No-Cloning-Theorem), die Messung des Qubits zerstört die Superposition, und Fehler sind kontinuierlich. Die Quantenfehlerkorrektur umgeht alle drei.

## Redundanz ohne Kopie

Klassisch genügt Wiederholen: $0 \to 000$, und die Mehrheit gewinnt. Quantenmechanisch lässt sich $|\psi\rangle$ nicht kopieren, aber man kann die Basis verschränken:

$$
\alpha|0\rangle + \beta|1\rangle \;\longrightarrow\; \alpha|000\rangle + \beta|111\rangle
$$

mit zwei CNOTs. Das sind keine drei Kopien von $|\psi\rangle$: Es ist ein einziger logischer Zustand, verteilt auf drei Qubits.

## Den Fehler messen, nicht den Zustand

Ein Bitflip auf Qubit 1 führt zu $\alpha|010\rangle + \beta|101\rangle$. Die Qubits zu messen würde $\alpha$ und $\beta$ zerstören; die **Paritäten** (ob zwei Qubits gleich oder verschieden sind) hängen aber nicht von ihnen ab. Zwei Ancillas speichern die Paritäten der Qubits 0–1 und 1–2. Das Ergebnispaar, das **Syndrom**, zeigt den Fehler an:

| Syndrom (a₃ a₄) | Fehler | Korrektur |
| :-- | :-- | :-- |
| 00 | keiner | keine |
| 10 | X auf Qubit 0 | X auf 0 |
| 11 | X auf Qubit 1 | X auf 1 |
| 01 | X auf Qubit 2 | X auf 2 |

Die Korrektur kann ohne Messung erfolgen, mit Toffoli-Gattern, die von den Ancillas gesteuert werden (das ist das Prinzip der verzögerten Messung).

## Die Grenzen dieses Codes

- **Zwei Flips** ergeben das Syndrom eines einzelnen Flips auf dem verbleibenden Qubit: Der Code „korrigiert“ das falsche Qubit und erzeugt einen logischen Fehler.
- **Phasenflips** ($Z$) ändern keine Parität: Sie bleiben unbemerkt. Ein analoger Code in der $X$-Basis korrigiert $Z$, und der 9-Qubit-Code von Shor verbindet beide und korrigiert jeden Fehler auf einem einzelnen Qubit.

## Die Schwelle

Wenn jedes Qubit mit Wahrscheinlichkeit $p$ einen Bitflip erleidet, scheitert der Code nur, wenn zwei oder drei Qubits Fehler haben:

$$
P_{\text{Erfolg}} = 1 - 3p^2 + 2p^3
$$

Für $p < \tfrac{1}{2}$ ist das besser als $1 - p$, das einzelne Qubit. Die Idee einer **Schwelle**, unterhalb derer das Kodieren hilft, macht fehlertolerantes Quantenrechnen erst möglich.

## Im Labor

- Die Schaltflächen wählen den eingefügten Fehler. Probiere die aus, die der Code nicht korrigiert.
- Im Tab **Register** erscheinen mit dem Cursor hinter dem Syndrom die Bits der Ancillas.
- In den **Bloch-Kugeln** kannst du die Datenqubits verfolgen.
- Der Tab **Schwelle** vergleicht das geschützte mit dem ungeschützten Qubit.
