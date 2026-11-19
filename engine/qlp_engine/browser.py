"""The engine inside the learner's browser (Pyodide, in a Web Worker).

Same protocol as the WebSocket server (dispatch.py), in public mode: progress and notes
stay in the browser, and there is no IBM hardware. The page's script (the "host",
app/src/engine/browser/) passes each request to `BrowserEngine.handle` and gets the reply.

Pyodide cannot start processes or interrupt running Python, so jobs run right here, one
at a time, and the host enforces the limits from outside: before each job it is told the
time limit and the reply to give if it has to terminate the Web Worker (timeout or Stop).

The host object provides:
  job_started(seconds, timeout_reply_json)   a job starts; terminate after `seconds`
  job_phase(timeout_reply_json)              the job changed phase; a timeout now means this
  job_finished()                             the job returned
  send_event(event_json)                     a progress event of a training run
"""

from __future__ import annotations

import json

from . import worker
from .content import ContentLibrary
from .dispatch import Dispatcher, _error, shots_heavy_error
from .messages import t
from .pool import DEFAULT_JOB_TIMEOUT_S


class InlinePool:
    """Runs each job at once, in this process; same `submit` interface as pool.WorkerPool."""

    def __init__(self, host, job_timeout: float = DEFAULT_JOB_TIMEOUT_S):
        self.host = host
        self.job_timeout = job_timeout

    async def submit(self, job: dict, timeout: float | None = None, is_stale=None, on_event=None, tag=None) -> dict:
        if is_stale is not None and is_stale():
            return {"ok": False, "stale": True}
        seconds = timeout or self.job_timeout
        self.host.job_started(seconds, json.dumps(timeout_reply(job, seconds, None)))

        def emit(event: dict) -> None:
            if event.get("event") == "phase":
                self.host.job_phase(json.dumps(timeout_reply(job, seconds, event.get("name"))))
            elif on_event is not None:
                on_event(event)

        try:
            return worker.handle(job, emit)
        finally:
            self.host.job_finished()

    def cancel(self, tag) -> None:
        """Nothing to do here: the host stops a running job by terminating the Web Worker."""


def timeout_reply(job: dict, seconds: float, phase: str | None) -> dict:
    """The reply for a job that ran out of time, as the server would give it."""
    if job.get("type") == "shots" and phase == "sampling":
        return shots_heavy_error(seconds)
    reply = _error(t("run.timeout", seconds=f"{seconds:.0f}"), "timeout")
    if phase:
        reply["error"]["phase"] = phase
    return reply


class BrowserEngine(Dispatcher):
    def __init__(self, content_dir: str, host):
        super().__init__(ContentLibrary(content_dir), None, InlinePool(host), public=True)
        self.host = host
        self.latest_run = {"seq": 0}

    def _progress_sender(self, connection, request_id):
        return lambda event: self.host.send_event(json.dumps(event))

    async def handle(self, raw: str) -> str:
        """The JSON reply to one JSON request."""
        return json.dumps(await self.respond(raw, self.latest_run), ensure_ascii=False)

    @staticmethod
    def warm_up() -> None:
        """Imports the heavy libraries now, so the learner's first run does not wait for them."""
        import pennylane  # noqa: F401
        import qiskit  # noqa: F401
        from qiskit import transpile  # noqa: F401
        from qiskit.quantum_info import Statevector  # noqa: F401

    @staticmethod
    def texts() -> str:
        """Replies the host gives on its own (it terminated the worker), in the engine's words."""
        return json.dumps({
            "cancelled": _error(t("run.cancelled"), "cancelled"),
            "crash": _error(t("run.crash"), "crash"),
        })
