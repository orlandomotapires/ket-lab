"""Execução num computador quântico real da IBM (Qiskit Runtime).

O token do aluno chega em cada requisição, fica só na memória durante a chamada
e nunca é registrado nem gravado. Fica desligado no modo público: um motor
compartilhado não deve receber credenciais de terceiros.

Depende do pacote opcional `qiskit-ibm-runtime` (extra `hardware` do motor).
"""

from __future__ import annotations

from .messages import t

CHANNEL = "ibm_quantum_platform"
MAX_SHOTS = 4096


class HardwareError(Exception):
    pass


def _fake() -> bool:
    import os

    return os.environ.get("QLP_FAKE_IBM") == "1"


def available() -> bool:
    if _fake():
        return True
    try:
        import qiskit_ibm_runtime  # noqa: F401
    except ImportError:
        return False
    return True


def _service(token: str, instance: str | None):
    if not token or not isinstance(token, str):
        raise HardwareError(t("hw.no_token"))
    if _fake():
        from .fake_ibm import Service as QiskitRuntimeService
    else:
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
        except ImportError:
            raise HardwareError(t("hw.not_installed")) from None
    try:
        return QiskitRuntimeService(channel=CHANNEL, token=token, instance=instance or None)
    except Exception as exc:  # noqa: BLE001 - token inválido, sem rede, conta sem acesso
        raise HardwareError(t("hw.login_failed", detail=_short(exc))) from None


def submit(qasm3: str, token: str, instance: str | None = None, shots: int = 1024) -> dict:
    """Envia o circuito ao backend real menos ocupado; devolve o id do job."""
    from qiskit import qasm3 as qasm3_module
    from qiskit.transpiler import generate_preset_pass_manager

    service = _service(token, instance)
    try:
        circuit = qasm3_module.loads(qasm3)
    except Exception as exc:  # noqa: BLE001
        raise HardwareError(t("hw.bad_circuit", detail=_short(exc))) from None
    if not any(instruction.operation.name == "measure" for instruction in circuit.data):
        circuit.measure_all()
    try:
        backend = service.least_busy(operational=True, simulator=False, min_num_qubits=circuit.num_qubits)
    except Exception as exc:  # noqa: BLE001
        raise HardwareError(t("hw.no_backend", detail=_short(exc))) from None

    if _fake():
        from .fake_ibm import Sampler as SamplerV2
    else:
        from qiskit_ibm_runtime import SamplerV2

    isa = generate_preset_pass_manager(backend=backend, optimization_level=1).run(circuit)
    job = SamplerV2(mode=backend).run([isa], shots=max(1, min(int(shots), MAX_SHOTS)))
    return {"job_id": job.job_id(), "backend": backend.name, "shots": shots}


def status(job_id: str, token: str, instance: str | None = None) -> dict:
    """Estado do job; quando terminado, as contagens (todos os registradores juntos)."""
    service = _service(token, instance)
    try:
        job = service.job(job_id)
    except Exception as exc:  # noqa: BLE001
        raise HardwareError(t("hw.no_job", detail=_short(exc))) from None
    raw = job.status()
    state = str(getattr(raw, "name", raw)).split(".")[-1].upper()
    result = {"job_id": job_id, "status": state}
    if state == "DONE":
        data = job.result()[0].data
        counts = data.join_data().get_counts() if hasattr(data, "join_data") else {}
        result["counts"] = dict(sorted(counts.items()))
    elif state in ("ERROR", "CANCELLED"):
        result["error"] = _short(getattr(job, "error_message", lambda: state)() or state)
    return result


def _short(exc) -> str:
    text = str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__
    return text[:200]
