"""Execution on a real IBM quantum computer (Qiskit Runtime).

The student's token arrives with each request, stays only in memory during the call
and is never logged or stored. It is disabled in public mode: a shared
engine must not receive third parties' credentials.

Depends on the optional package `qiskit-ibm-runtime` (the engine's `hardware` extra).
"""

from __future__ import annotations

import hashlib
import threading
import time

from .messages import t

CHANNEL = "ibm_quantum_platform"
MAX_SHOTS = 4096
# Seconds each call to IBM may take before the learner gets a message instead of a frozen screen.
LOGIN_TIMEOUT_S = 20.0
CALL_TIMEOUT_S = 20.0
RESULT_TIMEOUT_S = 30.0
SUBMIT_TIMEOUT_S = 40.0
# A logged-in service is reused for this long: the interface polls the status every few seconds and
# logging in each time is slow and counts against IBM's rate limits.
SERVICE_TTL_S = 120.0
_service_cache: dict = {}
_cache_lock = threading.Lock()


class HardwareError(Exception):
    pass


def _fake() -> bool:
    import os

    return os.environ.get("KET_LAB_FAKE_IBM") == "1"


def available() -> bool:
    if _fake():
        return True
    try:
        import qiskit_ibm_runtime  # noqa: F401
    except ImportError:
        return False
    return True


def clear_cache() -> None:
    with _cache_lock:
        _service_cache.clear()


def _call(function, seconds: float, what: str):
    """Runs a network call with a time limit. The call itself cannot be interrupted, so on a timeout its
    thread is left to finish by itself (daemon) and the learner gets a clear message right away."""
    outcome: dict = {}

    def run() -> None:
        try:
            outcome["value"] = function()
        except BaseException as exc:  # noqa: BLE001 - handed back to the caller's thread
            outcome["error"] = exc

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(seconds)
    if worker.is_alive():
        raise HardwareError(t("hw.timeout", seconds=f"{seconds:.0f}", what=what))
    if "error" in outcome:
        raise outcome["error"]
    return outcome["value"]


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
    # The key of the cache is a digest, not the token; the service object (which holds the token, as
    # it must) is dropped after SERVICE_TTL_S, when the login fails, or when a call on it fails.
    key = (hashlib.sha256(token.encode()).hexdigest(), instance or None, id(QiskitRuntimeService))
    now = time.monotonic()
    with _cache_lock:
        cached = _service_cache.get(key)
        if cached is not None and now - cached[0] < SERVICE_TTL_S:
            return cached[1]
        _service_cache.clear()  # one learner, one account: never more than one entry
    try:
        service = _call(
            lambda: QiskitRuntimeService(channel=CHANNEL, token=token, instance=instance or None),
            LOGIN_TIMEOUT_S, "logging in",
        )
    except HardwareError:
        raise
    except Exception as exc:  # noqa: BLE001 - invalid token, no network, account without access
        raise HardwareError(t("hw.login_failed", detail=_short(exc))) from None
    with _cache_lock:
        _service_cache[key] = (now, service)
    return service


def submit(qasm3: str, token: str, instance: str | None = None, shots: int = 1024) -> dict:
    """Submits the circuit to the least busy real backend; returns the job id."""
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
        backend = _call(
            lambda: service.least_busy(operational=True, simulator=False, min_num_qubits=circuit.num_qubits),
            CALL_TIMEOUT_S, "looking for a device",
        )
    except HardwareError:
        clear_cache()
        raise
    except Exception as exc:  # noqa: BLE001
        raise HardwareError(t("hw.no_backend", detail=_short(exc))) from None

    if _fake():
        from .fake_ibm import Sampler as SamplerV2
    else:
        from qiskit_ibm_runtime import SamplerV2

    isa = generate_preset_pass_manager(backend=backend, optimization_level=1).run(circuit)
    job = _call(
        lambda: SamplerV2(mode=backend).run([isa], shots=max(1, min(int(shots), MAX_SHOTS))),
        SUBMIT_TIMEOUT_S, "sending the job",
    )
    return {"job_id": job.job_id(), "backend": backend.name, "shots": shots}


def status(job_id: str, token: str, instance: str | None = None) -> dict:
    """Job status; when finished, the counts (all registers together)."""
    service = _service(token, instance)
    try:
        job = _call(lambda: service.job(job_id), CALL_TIMEOUT_S, "looking up the job")
    except HardwareError:
        clear_cache()
        raise
    except Exception as exc:  # noqa: BLE001
        clear_cache()  # the cached login may have expired: the next poll logs in again
        raise HardwareError(t("hw.no_job", detail=_short(exc))) from None
    try:
        raw = _call(job.status, CALL_TIMEOUT_S, "reading the job status")
    except HardwareError:
        clear_cache()
        raise
    state = str(getattr(raw, "name", raw)).split(".")[-1].upper()
    result = {"job_id": job_id, "status": state}
    if state == "DONE":
        data = _call(lambda: job.result()[0].data, RESULT_TIMEOUT_S, "downloading the result")
        counts = data.join_data().get_counts() if hasattr(data, "join_data") else {}
        result["counts"] = dict(sorted(counts.items()))
    elif state in ("ERROR", "CANCELLED"):
        result["error"] = _short(getattr(job, "error_message", lambda: state)() or state)
    return result


def _short(exc) -> str:
    text = str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__
    return text[:200]
