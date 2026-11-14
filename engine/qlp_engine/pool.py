"""Gerencia o processo worker: pré-aquecimento, timeout com kill e reinício."""

from __future__ import annotations

import asyncio
import multiprocessing
import threading
import time

from .i18n import t
from .worker import worker_main

STARTUP_TIMEOUT_S = 120.0
DEFAULT_JOB_TIMEOUT_S = 5.0
POLL_INTERVAL_S = 0.05


class WorkerPool:
    """Um worker aquecido, um job por vez. Jobs que estouram o tempo matam o worker."""

    def __init__(self, job_timeout: float = DEFAULT_JOB_TIMEOUT_S):
        self.job_timeout = job_timeout
        self._context = multiprocessing.get_context("spawn")
        self._process = None
        self._connection = None
        self._ready = False
        self._thread_lock = threading.Lock()
        self._async_lock = asyncio.Lock()
        self._closed = False
        # Cancelamento: o job em execução (pela etiqueta) e etiquetas canceladas ainda na fila.
        self._running_tag = None
        self._cancel = threading.Event()
        self._cancelled: set = set()
        self._queued: set = set()

    # -- ciclo de vida ------------------------------------------------------ #

    def _spawn(self) -> None:
        parent, child = self._context.Pipe()
        process = self._context.Process(target=worker_main, args=(child,), daemon=True)
        process.start()
        child.close()
        self._process, self._connection, self._ready = process, parent, False

    def _kill(self) -> None:
        if self._process is not None:
            self._process.kill()
            self._process.join(timeout=2)
        if self._connection is not None:
            self._connection.close()
        self._process = self._connection = None
        self._ready = False

    def _ensure_ready(self) -> None:
        if self._process is None or not self._process.is_alive():
            self._kill()
            self._spawn()
        if not self._ready:
            if not self._connection.poll(STARTUP_TIMEOUT_S):
                self._kill()
                raise RuntimeError(t("run.engine_start"))
            self._connection.recv()
            self._ready = True

    def warm_up(self) -> None:
        """Inicia o worker em segundo plano para a primeira execução não esperar o import."""
        threading.Thread(target=self._warm, daemon=True).start()

    def _warm(self) -> None:
        with self._thread_lock:
            if self._closed:
                return
            try:
                self._ensure_ready()
            except Exception:  # noqa: BLE001 - nova tentativa no próximo job
                pass

    def close(self) -> None:
        with self._thread_lock:
            self._closed = True
            self._kill()

    # -- execução ----------------------------------------------------------- #

    def _roundtrip(self, job: dict, timeout: float, on_event=None) -> dict:
        with self._thread_lock:
            if self._closed:
                return _failure(t("run.engine_closed"), "internal")
            try:
                self._ensure_ready()
                self._connection.send(job)
                deadline = time.monotonic() + timeout
                while True:
                    if self._cancel.is_set():
                        self._restart()
                        return _failure(t("run.cancelled"), "cancelled")
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        self._restart()
                        return _failure(t("run.timeout", seconds=f"{timeout:.0f}"), "timeout")
                    if not self._connection.poll(min(POLL_INTERVAL_S, remaining)):
                        continue
                    message = self._connection.recv()
                    if isinstance(message, dict) and message.get("event") == "progress":
                        if on_event is not None:
                            on_event(message)
                        continue
                    return message
            except (EOFError, OSError, BrokenPipeError):
                self._restart()
                return _failure(t("run.crash"), "crash")
            except RuntimeError as exc:
                return _failure(str(exc), "internal")

    def _restart(self) -> None:
        self._kill()
        self._spawn()  # já deixa o próximo aquecendo

    async def submit(self, job: dict, timeout: float | None = None, is_stale=None, on_event=None, tag=None) -> dict:
        """Executa um job. `is_stale()` é consultado ao chegar a vez: se True, o job é descartado.

        `on_event` recebe os eventos de progresso do worker (em outra thread).
        `tag` identifica o job para `cancel(tag)`.
        """
        if tag is not None:
            self._queued.add(tag)
        try:
            async with self._async_lock:
                self._queued.discard(tag)
                if is_stale is not None and is_stale():
                    return {"ok": False, "stale": True}
                if tag is not None and tag in self._cancelled:
                    return _failure(t("run.cancelled"), "cancelled")
                self._running_tag = tag
                self._cancel.clear()
                try:
                    return await asyncio.to_thread(self._roundtrip, job, timeout or self.job_timeout, on_event)
                finally:
                    self._running_tag = None
                    self._cancel.clear()
        finally:
            self._queued.discard(tag)
            self._cancelled.discard(tag)

    def cancel(self, tag) -> None:
        """Interrompe o job com essa etiqueta (matando o worker) ou o tira da fila."""
        if tag is None:
            return
        if self._running_tag == tag:
            self._cancel.set()
        elif tag in self._queued:
            self._cancelled.add(tag)


def _failure(message: str, kind: str) -> dict:
    return {"ok": False, "error": {"message": message, "line": None, "kind": kind}}
