"""Teste de fumaça do executável empacotado: sobe, conecta, simula e valida.

Uso:  python packaging/smoke_test.py [caminho_do_executavel]
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from websockets.asyncio.client import connect

ENGINE = Path(__file__).resolve().parents[1]
DEFAULT = ENGINE / "dist" / "qlp-engine" / ("qlp-engine.exe" if sys.platform == "win32" else "qlp-engine")
CODE = "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nqc.x(0)\n"


async def exercise(port: int, token: str) -> None:
    async with connect(f"ws://127.0.0.1:{port}/?token={token}") as websocket:
        async def call(**message):
            await websocket.send(json.dumps(message))
            return json.loads(await websocket.recv())

        started = time.perf_counter()
        run = await call(id=1, type="run", code=CODE, lesson_id="1.1")
        first = time.perf_counter() - started
        assert run["ok"] and run["snapshots"][-1]["bloch"] == [[0.0, 0.0, -1.0]], run

        started = time.perf_counter()
        await call(id=2, type="run", code=CODE)
        warm = time.perf_counter() - started

        validation = await call(id=3, type="validate", code=CODE, lesson_id="1.1")
        assert validation["passed"], validation
        print(f"primeira execução: {first:.2f} s | execução aquecida: {warm * 1000:.1f} ms")


def main() -> None:
    executable = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    with tempfile.TemporaryDirectory() as data_dir:
        started = time.perf_counter()
        process = subprocess.Popen(
            [str(executable), "--data-dir", data_dir], stdout=subprocess.PIPE, text=True
        )
        try:
            ready = json.loads(process.stdout.readline())
            print(f"pronto em {time.perf_counter() - started:.2f} s na porta {ready['port']}")
            asyncio.run(exercise(ready["port"], ready["token"]))
            print("OK")
        finally:
            process.terminate()
            process.wait(timeout=10)


if __name__ == "__main__":
    main()
