"""Manages the worker process: warm-up, timeout with kill, and restart."""

from __future__ import annotations

import asyncio
import multiprocessing
import threading
import time

from .messages import t
from .worker import worker_main

STARTUP_TIMEOUT_S = 120.0
DEFAULT_JOB_TIMEOUT_S = 5.0
POLL_INTERVAL_S = 0.05


class WorkerPool:
    """A warmed-up worker, one job at a time. Jobs that exceed the time limit kill the worker."""

    def __init__(self, job_timeout: float = DEFAULT_JOB_TIMEOUT_S):
        self.job_timeout = job_timeout
        self._context = multiprocessing.get_context("spawn")
        self._process = None
        self._connection = None
        self._ready = False
        self._thread_lock = threading.Lock()
        self._async_lock = asyncio.Lock()
        self._closed = False
        # Cancellation: the running job (by tag) and cancelled tags still in the queue.
        self._running_tag = None
        self._cancel = threading.Event()
        self._cancelled: set = set()
        self._queued: set = set()

    # -- lifecycle ------------------------------------------------------ #

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
        """Starts the worker in the background so the first run does not wait for the import."""
        threading.Thread(target=self._warm, daemon=True).start()

    def _warm(self) -> None:
        with self._thread_lock:
            if self._closed:
                return
            try:
                self._ensure_ready()
            except Exception:  # noqa: BLE001 - retry on the next job
                pass

    def close(self) -> None:
        with self._thread_lock:
            self._closed = True
            self._kill()

    # -- execution ----------------------------------------------------------- #

    def _roundtrip(self, job: dict, timeout: float, on_event=None) -> dict:
        with self._thread_lock:
            if self._closed:
                return _failure(t("run.engine_closed"), "internal")
            try:
                self._ensure_ready()
                self._connection.send(job)
                deadline = time.monotonic() + timeout
                phase = None  # last phase the worker announced ("sampling"), to explain a timeout
                while True:
                    if self._cancel.is_set():
                        self._restart()
                        return _failure(t("run.cancelled"), "cancelled")
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        self._restart()
                        failure = _failure(t("run.timeout", seconds=f"{timeout:.0f}"), "timeout")
                        if phase:
                            failure["error"]["phase"] = phase
                        return failure
                    if not self._connection.poll(min(POLL_INTERVAL_S, remaining)):
                        continue
                    message = self._connection.recv()
                    if isinstance(message, dict) and "event" in message:  # not the final reply
                        if message["event"] == "phase":
                            phase = message.get("name")
                        elif on_event is not None:
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
        self._spawn()  # already leave the next one warming up

    async def submit(self, job: dict, timeout: float | None = None, is_stale=None, on_event=None, tag=None) -> dict:
        """Runs a job. `is_stale()` is consulted when its turn comes: if True, the job is discarded.

        `on_event` receives the worker's progress events (on another thread).
        `tag` identifies the job for `cancel(tag)`.
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
        """Interrupts the job with this tag (killing the worker) or removes it from the queue."""
        if tag is None:
            return
        if self._running_tag == tag:
            self._cancel.set()
        elif tag in self._queued:
            self._cancelled.add(tag)


def _failure(message: str, kind: str) -> dict:
    return {"ok": False, "error": {"message": message, "line": None, "kind": kind}}


class WorkerGroup:
    """Several WorkerPools in parallel (hosted engine with several students).

    Each job goes to a free worker; the rest wait in the queue. The interface is the
    same as WorkerPool's, so the server does not need to know how many there are.
    """

    def __init__(self, size: int, job_timeout: float = DEFAULT_JOB_TIMEOUT_S):
        self.pools = [WorkerPool(job_timeout=job_timeout) for _ in range(max(1, size))]
        self._idle: asyncio.Queue | None = None
        self._waiting: set = set()  # tags of jobs waiting for a free worker
        self._cancelled_waiting: set = set()

    def _queue(self) -> asyncio.Queue:
        if self._idle is None:  # created inside the server loop
            self._idle = asyncio.Queue()
            for pool in self.pools:
                self._idle.put_nowait(pool)
        return self._idle

    def warm_up(self) -> None:
        for pool in self.pools:
            pool.warm_up()

    async def submit(self, job: dict, timeout: float | None = None, is_stale=None, on_event=None, tag=None) -> dict:
        idle = self._queue()
        if tag is not None:
            self._waiting.add(tag)
        try:
            pool = await idle.get()
        finally:
            self._waiting.discard(tag)
            cancelled = tag in self._cancelled_waiting
            self._cancelled_waiting.discard(tag)
        try:
            if cancelled:
                return _failure(t("run.cancelled"), "cancelled")
            return await pool.submit(job, timeout=timeout, is_stale=is_stale, on_event=on_event, tag=tag)
        finally:
            idle.put_nowait(pool)

    def cancel(self, tag) -> None:
        if tag in self._waiting:  # still queued for a worker: no pool knows about it yet
            self._cancelled_waiting.add(tag)
        for pool in self.pools:
            pool.cancel(tag)

    def close(self) -> None:
        for pool in self.pools:
            pool.close()
