"""The engine's protocol: one JSON request in, one JSON reply out.

Shared by the WebSocket server (server.py) and the browser engine (browser.py, inside
Pyodide). Nothing here imports `websockets`, which does not run in the browser.
The transport supplies a `connection` object (the WebSocket, or None) and the way to
send progress events while a training run is going (`_progress_sender`).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys

from . import hardware, messages
from .content import ContentError, ContentLibrary, _fold, _snippet
from .progress import ProgressError

MAX_CODE_CHARS = 100_000
# Training runs (Run button in the free lab) can take much longer than a live edit.
TRAIN_TIMEOUT_S = 120.0
MAX_LESSON_ID_CHARS = 80
MAX_NOTE_HITS = 8

# QLP_LOG=1 logs the type of each request to stderr (diagnostics).
LOG_REQUESTS = os.environ.get("QLP_LOG") == "1"
logger = logging.getLogger("qlp_engine")


class Dispatcher:
    """Answers protocol requests. `progress` None means the browser keeps progress and notes."""

    def __init__(self, content: ContentLibrary, progress, pool, *, public: bool = False, single_user: bool = False):
        self.content = content
        self.progress = progress
        self.pool = pool
        self.public = public
        self.single_user = single_user
        use_keys = getattr(self.progress, "use_keys", None)
        if use_keys is not None and content is not None:
            # Progress and notes are stored under stable lesson keys; the protocol keeps speaking lesson ids.
            use_keys(content.lesson_keys)

    def _progress_sender(self, connection, request_id):
        """Returns `send(event)` for a training run's progress events (may be called from a pool thread)."""
        raise NotImplementedError

    async def respond(self, raw, latest_run: dict, connection=None) -> dict:
        """The reply to one raw request, with its id. Never raises: every request gets a reply."""
        request_id = None
        try:
            message = json.loads(raw)
            request_id = message.get("id")
            response = await self._dispatch(message, latest_run, connection)
        except ContentError as exc:
            response = _error(str(exc), "content")
        except ProgressError as exc:
            response = _error(str(exc), "protocol")
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, AttributeError) as exc:
            response = _error(messages.t("server.bad_request", detail=exc), "protocol")
        except Exception:  # noqa: BLE001 - every request gets a reply, whatever went wrong
            logger.exception("unexpected error while handling a request")
            response = _error(messages.t("server.internal"), "internal")
        response["id"] = request_id
        return response

    async def _dispatch(self, message: dict, latest_run: dict, websocket=None) -> dict:
        if not isinstance(message, dict):
            raise TypeError("the message must be a JSON object")
        kind = message["type"]
        if not isinstance(kind, str):
            raise TypeError("`type` must be text")
        bad = _bad_field(message)
        if bad:
            return _error(messages.t("server.bad_field", field=bad), "protocol")
        _log(f"{kind} {message.get('lesson_id') or ''}".rstrip())

        if kind == "catalog":
            catalog = self.content.catalog()
            glossary = self.content.glossary()
            if self.progress is None:
                return {
                    "ok": True, "catalog": catalog, "progress": {}, "progress_storage": "client",
                    "notes_storage": "client", "glossary": glossary,
                }
            return {
                "ok": True, "catalog": catalog, "progress": self.progress.all(), "progress_storage": "engine",
                "notes_storage": "engine", "glossary": glossary,
            }

        if kind == "lesson":
            return {"ok": True, "lesson": self.content.lesson(message["lesson_id"])}

        if kind == "review":
            return {"ok": True, "track": message["track"], "questions": self.content.review(message["track"])}

        if kind == "solution":
            # Explicit request from someone who is stuck; recorded for the hub ("completed with solution").
            lesson_id, challenge = message["lesson_id"], bool(message.get("challenge"))
            code = self.content.solution(lesson_id, challenge)
            if self.progress is not None:
                self.progress.save(f"{lesson_id}:challenge" if challenge else lesson_id, solution_seen=True)
            return {"ok": True, "code": code}

        if kind == "bibliography":
            return {"ok": True, **self.content.bibliography()}

        if kind == "search":
            query = str(message.get("query", ""))[:100]
            return {"ok": True, "results": self.content.search(query), "notes": self._search_notes(query)}

        if kind == "progress.save":
            if self.progress is None:  # public mode: the browser keeps the progress
                return {"ok": True}
            if not isinstance(message["lesson_id"], str) or not message["lesson_id"]:
                return _error(messages.t("server.bad_field", field="lesson_id"), "protocol")
            self.progress.save(
                message["lesson_id"],
                code=message.get("code"),
                completed=message.get("completed"),
                hints_used=message.get("hints_used"),
            )
            return {"ok": True}

        if kind == "progress.import":
            if self.progress is None:
                return _error(messages.t("server.unavailable", what="Progress"), "unavailable")
            data = message["data"]
            if isinstance(data, str):
                data = json.loads(data)
            summary = self.progress.import_backup(data)
            return {
                "ok": True, "progress": self.progress.all(), "notes": self.progress.notes_all(),
                "progress_storage": "engine", "imported": summary,
            }

        if kind == "progress.export":
            if self.progress is None:
                return _error(messages.t("server.unavailable", what="Progress"), "unavailable")
            return {"ok": True, "backup": self.progress.export_backup()}

        if kind in ("notes.list", "notes.save", "notes.delete"):
            if self.progress is None:  # public mode: the browser keeps the notes
                return _error(messages.t("server.unavailable", what="Notes are"), "unavailable")
            if kind == "notes.list":
                return {"ok": True, "notes": self.progress.notes_all()}
            if kind == "notes.save":
                return {"ok": True, "note": self.progress.note_save(message["key"], message["body"])}
            self.progress.note_delete(message["key"])
            return {"ok": True}

        if kind == "hardware.available":
            return {"ok": True, "available": self._hardware_allowed() and hardware.available()}

        if kind in ("hardware.submit", "hardware.status"):
            return await self._hardware(kind, message)

        if kind == "cancel":
            self.pool.cancel((id(websocket), message.get("target")))
            return {"ok": True}

        if kind in ("run", "shots", "validate", "export"):
            code = message["code"]
            if not isinstance(code, str) or len(code) > MAX_CODE_CHARS:
                return _error(messages.t("server.bad_code"), "protocol")
            lesson_id = message.get("lesson_id")
            job = {"type": kind, "code": code, "seed": message.get("seed", 0)}

            timeout = self.content.timeout(lesson_id)
            challenge = bool(message.get("challenge"))
            if kind == "validate":
                job["lesson"] = self.content.validation_bundle(lesson_id, challenge=challenge)
                # Validating may re-run the code several times (secret cases, training runs).
                # Tagged like a training run, so {"type": "cancel", "target": <this request's id>} stops it.
                result = await self.pool.submit(
                    job, timeout=timeout * 3 if timeout else None, tag=(id(websocket), message.get("id"))
                )
                if self.progress is not None and result.get("ok"):
                    # The challenge has its own progress: "<id>:challenge".
                    key = f"{lesson_id}:challenge" if challenge else lesson_id
                    if result.get("passed"):
                        self.progress.save(key, code=code, completed=True)
                    else:  # unsuccessful attempts unlock "Show a solution"
                        self.progress.save(key, failed_attempt=True)
                return result

            job.update(self.content.run_context(lesson_id, challenge=challenge))
            job["inputs"] = self.content.control_inputs(lesson_id, message.get("controls"))
            if kind == "export":
                # Exporting re-runs the code; a lab training run needs the training time.
                job["format"] = message.get("format")
                return await self.pool.submit(job, timeout=max(timeout or 0, TRAIN_TIMEOUT_S))
            if kind == "run" and message.get("train"):
                return await self._train(job, message, websocket, timeout)
            if kind == "shots":
                job["shots"] = message.get("shots", 1024)
                result = await self.pool.submit(job, timeout=timeout)
                error = result.get("error") or {}
                if error.get("kind") == "timeout" and error.get("phase") == "sampling":
                    return shots_heavy_error(timeout or self.pool_timeout())
                return result

            # run: only the most recent edit matters; outdated runs are discarded.
            latest_run["seq"] += 1
            seq = latest_run["seq"]
            return await self.pool.submit(job, timeout=timeout, is_stale=lambda: seq != latest_run["seq"])

        return _error(messages.t("server.unknown_type", kind=kind), "protocol")

    def pool_timeout(self) -> float:
        pools = getattr(self.pool, "pools", None) or [self.pool]
        return float(getattr(pools[0], "job_timeout", 5.0))

    def _search_notes(self, query: str) -> list[dict]:
        """The learner's own notes that contain every word of the query (not kept in hosted mode)."""
        if self.progress is None:
            return []
        terms = [term for term in _fold(query).split() if term]
        if not terms:
            return []
        hits = []
        for key, note in self.progress.notes_all().items():
            folded = _fold(note["body"])
            if not all(term in folded for term in terms):
                continue
            lesson_id = key.removeprefix("lesson:") if key.startswith("lesson:") else None
            try:
                title = self.content.lesson(lesson_id)["title"] if lesson_id else None
            except (ContentError, KeyError):
                title = None
            hits.append({
                "key": key, "lesson_id": lesson_id, "title": title,
                "snippet": _snippet(note["body"], folded, terms[0]), "updated_at": note["updated_at"],
            })
        hits.sort(key=lambda hit: hit["updated_at"], reverse=True)
        return hits[:MAX_NOTE_HITS]

    async def _hardware(self, kind: str, message: dict) -> dict:
        """Real quantum computer. The token is neither stored nor logged."""
        if not self._hardware_allowed():
            return _error(messages.t("hw.public"), "hardware")
        token, instance = message.get("token"), message.get("instance")
        try:
            if kind == "hardware.status":
                result = await asyncio.to_thread(hardware.status, str(message.get("job_id", "")), token, instance)
                return {"ok": True, **result}
            code = message.get("code")
            if not isinstance(code, str) or len(code) > MAX_CODE_CHARS:
                return _error(messages.t("server.bad_code"), "protocol")
            lesson_id = message.get("lesson_id")
            job = {"type": "export", "code": code, "format": "qasm3", "seed": 0}
            job.update(self.content.run_context(lesson_id))
            job["inputs"] = self.content.control_inputs(lesson_id, message.get("controls"))
            exported = await self.pool.submit(job, timeout=TRAIN_TIMEOUT_S)
            if not exported.get("ok"):
                return exported
            result = await asyncio.to_thread(hardware.submit, exported["text"], token, instance, int(message.get("shots", 1024)))
            return {"ok": True, **result}
        except hardware.HardwareError as exc:
            return _error(str(exc), "hardware")

    def _hardware_allowed(self) -> bool:
        """A shared server does not receive third parties' keys; a learner's own machine does."""
        return self.single_user or not self.public

    async def _train(self, job: dict, message: dict, websocket, timeout: float | None) -> dict:
        """Long run from the button: sends the metrics from `report(...)` while it runs."""
        request_id = message.get("id")
        job["stream"] = True
        send = self._progress_sender(websocket, request_id)

        def on_event(event: dict) -> None:  # may run on a pool thread
            send({"id": request_id, "event": "progress", "series": event.get("series", {})})

        return await self.pool.submit(
            job, timeout=max(timeout or 0, TRAIN_TIMEOUT_S), on_event=on_event, tag=(id(websocket), request_id)
        )


def shots_heavy_error(seconds: float) -> dict:
    """A shots job that ran out of time while sampling: the circuit is fine, the shot count is too high."""
    return _error(messages.t("run.shots_heavy", seconds=f"{seconds:.0f}"), "timeout")


def _log(text: str) -> None:
    if not LOG_REQUESTS:
        return
    try:
        print(f"[qlp-engine] {text}", file=sys.stderr, flush=True)
    except (OSError, ValueError):
        pass  # no terminal to write to (e.g. parent process ended); logging is optional


def _bad_field(message: dict) -> str | None:
    """Name of the first field with the wrong type or size, or None. Missing fields are left to the handlers."""
    lesson_id = message.get("lesson_id")
    if lesson_id is not None and not (isinstance(lesson_id, str) and len(lesson_id) <= MAX_LESSON_ID_CHARS):
        return "lesson_id"
    code = message.get("code")
    if message.get("type") == "progress.save" and code is not None and not (isinstance(code, str) and len(code) <= MAX_CODE_CHARS):
        return "code"  # (run, shots, validate and export check `code` themselves)
    for field in ("query", "key", "format"):
        value = message.get(field)
        if value is not None and not (isinstance(value, str) and len(value) <= 1000):
            return field
    if "body" in message and not isinstance(message["body"], str):
        return "body"
    for field in ("hints_used", "shots", "seed"):
        value = message.get(field)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
            return field
    controls = message.get("controls")
    if controls is not None and not isinstance(controls, dict):
        return "controls"
    for field in ("track",):
        if field in message and not isinstance(message[field], (int, str)):
            return field
    return None


def _error(message: str, kind: str) -> dict:
    return {"ok": False, "error": {"message": message, "line": None, "kind": kind}}
