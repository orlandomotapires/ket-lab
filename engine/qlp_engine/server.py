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
import mimetypes
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from websockets.asyncio.server import serve
from websockets.datastructures import Headers
from websockets.exceptions import ConnectionClosed
from websockets.http11 import Response

from .content import ContentLibrary
from .dispatch import MAX_CODE_CHARS, TRAIN_TIMEOUT_S, Dispatcher, _log  # noqa: F401 - re-exported
from .pool import WorkerPool
from .progress import ProgressStore

HOST = "127.0.0.1"
MAX_MESSAGE_BYTES = 512 * 1024
# With --static-dir, the interface takes the root and the WebSocket lives at this path (as in nginx).
ENGINE_PATH = "/engine"


class EngineServer(Dispatcher):
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
        super().__init__(
            content, progress if (single_user or not public) else None, pool, public=public, single_user=single_user
        )
        self.static_dir = Path(static_dir).resolve() if static_dir else None
        self.token = token
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
        response = await self.respond(raw, latest_run, websocket)
        try:
            await websocket.send(await _encode(response))
        except ConnectionClosed:
            pass

    def _progress_sender(self, websocket, request_id):
        loop = asyncio.get_running_loop()

        def send(event: dict) -> None:  # pool thread
            payload = json.dumps(event)
            loop.call_soon_threadsafe(lambda: asyncio.ensure_future(_send(websocket, payload)))

        return send


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


