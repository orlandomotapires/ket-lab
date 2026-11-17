"""Engine entry point: `python -m qlp_engine` (`npm run dev` starts it).

When ready, prints ONE JSON line to stdout with the port and the token:
    {"event": "ready", "port": 51234, "token": "..."}
"""

from __future__ import annotations

import argparse
import asyncio
import json
import secrets
import sys
from pathlib import Path

from .content import ContentLibrary
from .pool import WorkerGroup, WorkerPool
from .progress import ProgressStore, default_data_dir
from .server import EngineServer


def _default_content_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "content"


class _TolerantStream:
    """Wraps stdout/stderr so that writing to a closed pipe does not bring down the engine.

    If the process that reads the engine's output dies, any warning printed (by the
    engine itself or by a library) would raise BrokenPipeError in the middle of
    a request.
    """

    def __init__(self, stream):
        self._stream = stream

    def write(self, text):
        try:
            return self._stream.write(text)
        except (OSError, ValueError):
            return len(text)

    def flush(self):
        try:
            self._stream.flush()
        except (OSError, ValueError):
            pass

    def __getattr__(self, name):
        return getattr(self._stream, name)


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="qlp-engine", description="Quantum Learning Platform engine")
    parser.add_argument("--port", type=int, default=0, help="local port (0 = random)")
    parser.add_argument("--token", default=None, help="session token (default: random)")
    parser.add_argument(
        "--allow-origin",
        action="append",
        default=[],
        help="additional allowed origin (e.g. http://localhost:5173 in development)",
    )
    parser.add_argument("--content-dir", type=Path, default=None)
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--job-timeout", type=float, default=5.0, help="seconds per run")
    parser.add_argument(
        "--public",
        action="store_true",
        help="hosted engine: no token, Origin required, progress kept in the browser (see deploy/)",
    )
    parser.add_argument(
        "--single-user",
        action="store_true",
        help="local container: no token and Origin required, but with progress kept on the server (see deploy/local.yml)",
    )
    parser.add_argument("--static-dir", type=Path, default=None, help="built interface to serve on the same port (WebSocket at /engine)")
    parser.add_argument("--host", default="127.0.0.1", help="network interface (0.0.0.0 inside a container)")
    parser.add_argument("--workers", type=int, default=1, help="processes that run code in parallel")
    parser.add_argument("--max-connections", type=int, default=0, help="cap on simultaneous connections (0 = no cap)")
    return parser.parse_args(argv)


async def serve_forever(args: argparse.Namespace) -> None:
    token = args.token or secrets.token_urlsafe(32)
    content = ContentLibrary(args.content_dir or _default_content_dir())
    progress = None if args.public and not args.single_user else ProgressStore(args.data_dir or default_data_dir(), lesson_keys=content.lesson_keys)
    pool = WorkerGroup(args.workers, job_timeout=args.job_timeout) if args.workers > 1 else WorkerPool(job_timeout=args.job_timeout)
    pool.warm_up()

    engine = EngineServer(
        content, progress, pool, token, tuple(args.allow_origin),
        public=args.public, max_connections=args.max_connections, host=args.host,
        single_user=args.single_user, static_dir=args.static_dir,
    )
    server = await engine.start(args.port)
    port = server.sockets[0].getsockname()[1]
    print(json.dumps({"event": "ready", "port": port, "token": token}), flush=True)
    stop = asyncio.Event()
    try:
        await stop.wait()
    finally:
        server.close()
        pool.close()
        if progress is not None:
            progress.close()


def main(argv=None) -> None:
    if sys.stdout is not None:
        sys.stdout = _TolerantStream(sys.stdout)
    if sys.stderr is not None:
        sys.stderr = _TolerantStream(sys.stderr)
    args = parse_args(argv)
    try:
        asyncio.run(serve_forever(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
