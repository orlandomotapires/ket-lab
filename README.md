<div align="center">

<img src=".github/assets/logo.svg" width="88" height="88" alt="">

# Ket Lab

**Learn quantum computing by writing circuits and watching the state change.**

[Open Ket Lab in your browser](https://orlandomotapires.github.io/quantum_learning_plataform/) &nbsp;|&nbsp; [Wiki](https://github.com/orlandomotapires/quantum_learning_plataform/wiki) &nbsp;|&nbsp; [Changelog](CHANGELOG.md)

</div>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/demo-dark.gif">
  <img src=".github/assets/demo-light.gif" alt="Lesson 1.5: typing qc.h(0) and qc.cx(0, 1) draws the circuit and moves the state to the Bell state; Check confirms it with a fidelity of 100%.">
</picture>

Write Qiskit or PennyLane. Each line you type shows up in the circuit, and the state after it shows up on the right: Bloch spheres, the Q-sphere, amplitudes, entanglement. When the mission is done, **Check** compares the physics, not the text, so any circuit that gets the right state passes.

No accounts, no teachers, no deadlines. It's built for one person studying alone, and your progress stays with you.

## 53 lessons, from qubits to annealing

| | Track | Lessons |
| :-: | :-- | :-: |
| 0 | Mathematical toolkit *(optional)* | 4 |
| 1 | Basics of quantum information | 11 |
| 2 | Quantum algorithms | 11 |
| 3 | Variational algorithms | 9 |
| 4 | Noise and error correction | 8 |
| 5 | Running on hardware | 5 |
| 6 | Quantum annealing | 5 |

About 25 hours in all. Every lesson cites Nielsen & Chuang or the IBM Quantum Learning courses, down to the section and page. [See every topic in the wiki.](https://github.com/orlandomotapires/quantum_learning_plataform/wiki/Curriculum)

## A closer look

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/lab-dark.png">
  <img src=".github/assets/lab-light.png" alt="The free lab: three qubits with H, RY(π/3), H and S, each one's Bloch vector on its own sphere, and the Bloch vector table below.">
</picture>

<p align="center"><sub>The free lab. Put the cursor on any line to see the state at that point.</sub></p>

<table>
  <tr>
    <td width="50%">
      <picture>
        <source media="(prefers-color-scheme: dark)" srcset=".github/assets/tracks-dark.png">
        <img src=".github/assets/tracks-light.png" alt="The tracks page: progress across the seven tracks and the lessons of track 1.">
      </picture>
    </td>
    <td width="50%">
      <picture>
        <source media="(prefers-color-scheme: dark)" srcset=".github/assets/search-dark.png">
        <img src=".github/assets/search-light.png" alt="Search for Grover: two lessons and two glossary terms.">
      </picture>
    </td>
  </tr>
  <tr>
    <td align="center"><sub>Your progress across the tracks</sub></td>
    <td align="center"><sub>One search for lessons, notes and the 142-term glossary</sub></td>
  </tr>
</table>

## Run it

The quickest way is [the browser version](https://orlandomotapires.github.io/quantum_learning_plataform/). There's nothing to install: Python runs inside the page.

To run it on your own machine, you need Python 3.11+ and Node 22+:

```bash
npm run setup   # once
npm run dev     # then open http://localhost:5173
```

The wiki explains [running it locally and with Docker](https://github.com/orlandomotapires/quantum_learning_plataform/wiki/Running-locally), [how it's built](https://github.com/orlandomotapires/quantum_learning_plataform/wiki/Architecture) and [how to work on it](https://github.com/orlandomotapires/quantum_learning_plataform/wiki/Development).

## License

[MIT](LICENSE). Third-party libraries and fonts are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Each lesson reference comes from the checked [reading list](docs/verified-references.md).
