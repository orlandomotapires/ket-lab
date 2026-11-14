"""Processo worker: é aqui (e só aqui) que o código do aluno é executado.

O worker importa o Qiskit ao nascer (pré-aquecimento) e depois atende um job
por vez. Se travar ou estourar a memória, o pool o mata e cria outro.
"""

from __future__ import annotations

import sys

MEMORY_LIMIT_BYTES = 4 * 1024**3


def _limit_memory() -> None:
    # RLIMIT_AS só é confiável no Linux. No Windows/macOS a proteção é o teto
    # de qubits + timeout; um Job Object no Windows fica para a fase de empacotamento.
    if sys.platform != "linux":
        return
    import resource

    _, hard = resource.getrlimit(resource.RLIMIT_AS)
    limit = MEMORY_LIMIT_BYTES if hard == resource.RLIM_INFINITY else min(MEMORY_LIMIT_BYTES, hard)
    resource.setrlimit(resource.RLIMIT_AS, (limit, hard))


def handle(job: dict) -> dict:
    """Atende um job. Erros do aluno voltam como {ok: False, error: {...}}."""
    from . import geometry, i18n, simulator, tracer, validation

    i18n.set_lang(job.get("lang"))
    kind = job.get("type")
    try:
        if kind == "run":
            execution = tracer.execute(job["code"], job.get("hidden_setup"))
            trajectory = simulator.run_trajectory(
                execution.circuit,
                execution.lines,
                seed=int(job.get("seed", 0)),
                max_qubits=int(job.get("max_qubits") or simulator.DEFAULT_MAX_QUBITS),
            )
            return {"ok": True, "stdout": execution.stdout, **geometry.describe_trajectory(trajectory)}
        if kind == "shots":
            execution = tracer.execute(job["code"], job.get("hidden_setup"))
            result = simulator.sample_counts(
                execution.circuit,
                shots=int(job.get("shots", 1024)),
                seed=int(job.get("seed", 0)),
                max_qubits=int(job.get("max_qubits") or simulator.DEFAULT_MAX_QUBITS),
            )
            return {"ok": True, **result}
        if kind == "validate":
            return {"ok": True, **validation.validate(job["code"], job["lesson"])}
        if kind == "ping":
            return {"ok": True}
        return _error(i18n.t("run.unknown_job", kind=kind), kind="internal")
    except tracer.UserCodeError as exc:
        return _error(exc.message, exc.line, exc.kind)
    except simulator.SimulationError as exc:
        return _error(exc.message, exc.line, "simulation")
    except MemoryError:
        return _error(i18n.t("run.memory"), kind="memory")
    except Exception as exc:  # noqa: BLE001 - o worker nunca deve morrer por um job
        return _error(i18n.t("run.internal", detail=f"{type(exc).__name__}: {exc}"), kind="internal")


def _error(message: str, line: int | None = None, kind: str = "runtime") -> dict:
    return {"ok": False, "error": {"message": message, "line": line, "kind": kind}}


def worker_main(connection) -> None:
    """Ponto de entrada do processo filho."""
    _limit_memory()
    from . import geometry, simulator, tracer, validation  # noqa: F401 - pré-aquecimento

    connection.send({"event": "ready"})
    while True:
        try:
            job = connection.recv()
        except (EOFError, OSError):
            return
        if job is None:
            return
        connection.send(handle(job))
