"""The engine's local WebSocket server.

Local mode (default): a WebSocket on localhost is NOT protected by the same-origin
policy, and any page open in the student's browser can try to connect. Therefore:
  * listens only on 127.0.0.1, on a random port by default;
  * requires one token per session (query string `?token=`);
  * refuses connections whose Origin header is not in the allowed list.

Public mode (`--public`, engine hosted behind the site): there is no token, but the
Origin is required and must be the site's; there is a connection cap; and
progress is not stored on the server (it stays in each student's browser). The
isolation of the student's code is the container's responsibility (deploy/).

Single-user mode (`--single-user`, the local container from deploy/local.yml): like
public mode for access (no token, Origin required), but it is the learner's own machine:
progress is kept on the server and IBM hardware stays available. With
`--static-dir`, the engine also serves the built interface on the same port, and the
WebSocket lives at /engine.
"""

from __future__ import annotations

import asyncio
import hmac
import http
import json
import logging
import mimetypes
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from websockets.asyncio.server import serve
from websockets.datastructures import Headers
from websockets.exceptions import ConnectionClosed
from websockets.http11 import Response

from . import hardware, messages
from .content import ContentError, ContentLibrary, _fold, _snippet
from .pool import WorkerPool
from .progress import ProgressError, ProgressStore

HOST = "127.0.0.1"
MAX_MESSAGE_BYTES = 512 * 1024
MAX_CODE_CHARS = 100_000
# Training runs (Run button in the free lab) can take much longer than a live edit.
TRAIN_TIMEOUT_S = 120.0
# With --static-dir, the interface takes the root and the WebSocket lives at this path (as in nginx).
ENGINE_PATH = "/engine"

# QLP_LOG=1 logs the type of each request to stderr (diagnostics).
LOG_REQUESTS = os.environ.get("QLP_LOG") == "1"
MAX_LESSON_ID_CHARS = 80
MAX_NOTE_HITS = 8
logger = logging.getLogger("qlp_engine")



class EngineServer:
    def __init__(
        self,
        content: ContentLibrary,
        progress: ProgressStore,
        pool: WorkerPool,
        token: str,
        allowed_origins: tuple[str, ...] = (),
        *,
        public: bool = False,
        max_connections: int = 0,
        host: str = HOST,
        single_user: bool = False,
        static_dir: Path | None = None,
    ):
        public = public or single_user  # single user: same access control as public mode
        self.content = content
        self.progress = progress if (single_user or not public) else None
        use_keys = getattr(self.progress, "use_keys", None)
        if use_keys is not None and content is not None:
            # Progress and notes are stored under stable lesson keys; the protocol keeps speaking lesson ids.
            use_keys(content.lesson_keys)
        self.single_user = single_user
        self.static_dir = Path(static_dir).resolve() if static_dir else None
        self.pool = pool
        self.token = token
        self.public = public
        self.max_connections = max_connections
        self.host = host
        self.connections = 0
        # Local: None allows clients without Origin (they are not browsers), and the token is still required.
        # Public: with no token, the site's Origin is the only credential, so it is required.
        if public and not allowed_origins:
            raise ValueError("public mode requires at least one --allow-origin")
        self.origins = [*allowed_origins] if public else [*allowed_origins, None]

    async def start(self, port: int = 0):
        return await serve(
            self._handle_connection,
            self.host,
            port,
            origins=self.origins,
            process_request=self._check_token,
            max_size=MAX_MESSAGE_BYTES,
        )

    def _check_token(self, connection, request):
        if self.static_dir is not None:
            path = urlparse(request.path).path
            if path.rstrip("/") != ENGINE_PATH:
                return self._static(path)
        if self.max_connections and self.connections >= self.max_connections:
            return connection.respond(http.HTTPStatus.SERVICE_UNAVAILABLE, "too many connections\n")
        if self.public:
            return None
        query = parse_qs(urlparse(request.path).query)
        supplied = (query.get("token") or [""])[0]
        if not hmac.compare_digest(supplied.encode(), self.token.encode()):
            return connection.respond(http.HTTPStatus.UNAUTHORIZED, "invalid token\n")
        return None

    def _static(self, path: str) -> Response:
        """Serves a file of the built interface; unknown routes fall back to index.html."""
        target = (self.static_dir / unquote(path).lstrip("/")).resolve()
        inside = target == self.static_dir or self.static_dir in target.parents
        if not inside or not target.is_file():
            if path.startswith("/assets/") or not inside:
                return _http(http.HTTPStatus.NOT_FOUND, b"not found\n", "text/plain")
            target = self.static_dir / "index.html"
        kind = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if kind.startswith("text/") or kind in ("application/javascript", "application/json"):
            kind += "; charset=utf-8"
        # Files under /assets have the content hash in their name: they can be cached forever.
        cache = "public, max-age=31536000, immutable" if path.startswith("/assets/") else "no-cache"
        return _http(http.HTTPStatus.OK, target.read_bytes(), kind, cache)

    async def _handle_connection(self, websocket) -> None:
        _log(f"connection opened ({websocket.request.headers.get('Origin')})")
        latest_run = {"seq": 0}
        tasks: set[asyncio.Task] = set()
        self.connections += 1
        try:
            async for raw in websocket:
                task = asyncio.create_task(self._handle_message(websocket, raw, latest_run))
                tasks.add(task)
                task.add_done_callback(tasks.discard)
        except ConnectionClosed:
            pass
        finally:
            self.connections -= 1
            _log(f"connection closed (code {websocket.close_code}, reason {websocket.close_reason!r})")
            for task in tasks:
                task.cancel()

    async def _handle_message(self, websocket, raw, latest_run: dict) -> None:
        request_id = None
        try:
            message = json.loads(raw)
            request_id = message.get("id")
            response = await self._dispatch(message, latest_run, websocket)
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
        try:
            await websocket.send(await _encode(response))
        except ConnectionClosed:
            pass

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
                    seconds = f"{timeout or self.pool_timeout():.0f}"
                    return _error(messages.t("run.shots_heavy", seconds=seconds), "timeout")
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
        loop = asyncio.get_running_loop()
        request_id = message.get("id")
        job["stream"] = True

        def on_event(event: dict) -> None:  # pool thread
            payload = json.dumps({"id": request_id, "event": "progress", "series": event.get("series", {})})
            loop.call_soon_threadsafe(lambda: asyncio.ensure_future(_send(websocket, payload)))

        return await self.pool.submit(
            job, timeout=max(timeout or 0, TRAIN_TIMEOUT_S), on_event=on_event, tag=(id(websocket), request_id)
        )


def _http(status: http.HTTPStatus, body: bytes, content_type: str, cache: str = "no-cache") -> Response:
    headers = Headers({
        "Content-Type": content_type,
        "Content-Length": str(len(body)),
        "Cache-Control": cache,
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "X-Frame-Options": "DENY",
        "Connection": "close",
    })
    return Response(status.value, status.phrase, headers, body)


async def _send(websocket, payload: str) -> None:
    try:
        await websocket.send(payload)
    except ConnectionClosed:
        pass


# Replies bigger than this (snapshots x 2^qubits) are serialized on a thread, not on the event loop.
THREAD_ENCODE_ELEMENTS = 20_000


async def _encode(response: dict) -> str:
    """JSON text of a reply; a large one is built off the event loop so other requests keep moving."""
    snapshots = response.get("snapshots")
    if isinstance(snapshots, list) and len(snapshots) << min(int(response.get("num_qubits") or 0), 24) > THREAD_ENCODE_ELEMENTS:
        return await asyncio.to_thread(json.dumps, response, ensure_ascii=False)
    return json.dumps(response, ensure_ascii=False)


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
