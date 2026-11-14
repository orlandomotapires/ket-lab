"""Empacota o motor em uma pasta autocontida (PyInstaller, modo onedir).

Uso:  python packaging/build.py
Saída: engine/dist/qlp-engine/  (executável + bibliotecas + conteúdo das lições)

onedir, e não onefile: o onefile se descompacta em pasta temporária a cada
inicialização, o que deixa o arranque lento e dispara mais falsos positivos de
antivírus.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
CONTENT = ENGINE.parent / "content"
DIST = ENGINE / "dist" / "qlp-engine"


def main() -> None:
    subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm", "--clean", "--onedir",
            "--name", "qlp-engine",
            "--distpath", str(ENGINE / "dist"),
            "--workpath", str(ENGINE / "build"),
            "--specpath", str(ENGINE / "build"),
            "--collect-submodules", "qlp_engine",
            # O Qiskit carrega partes de si mesmo dinamicamente.
            "--collect-all", "qiskit",
            # O PennyLane descobre dispositivos (default.qubit, default.mixed) por entry
            # points: os metadados dos pacotes precisam ir junto.
            "--collect-all", "pennylane",
            "--copy-metadata", "pennylane",
            "--collect-all", "autoray",
            "--collect-submodules", "autograd",
            "--exclude-module", "tkinter",
            "--exclude-module", "matplotlib",
            "--exclude-module", "IPython",
            "--exclude-module", "pytest",
            str(ENGINE / "packaging" / "entry.py"),
        ],
        check=True,
        cwd=ENGINE,
    )
    target = DIST / "content"
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(CONTENT, target)
    print(f"Motor empacotado em {DIST}")


if __name__ == "__main__":
    main()
