"""Ponto de entrada do sidecar: `python -m qlp_engine`.

Ao ficar pronto, imprime UMA linha JSON no stdout com a porta e o token:
    {"event": "ready", "port": 51234, "token": "..."}
O shell desktop lê essa linha para saber onde conectar.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import multiprocessing
import secrets
import sys
import threading
from pathlib import Path

from .content import ContentLibrary
from .pool import WorkerPool
from .progress import ProgressStore, default_data_dir
from .server import EngineServer


def _default_content_dir() -> Path:
    if getattr(sys, "frozen", False):  # executável PyInstaller: conteúdo ao lado do binário
        return Path(sys.executable).resolve().parent / "content"
    return Path(__file__).resolve().parents[2] / "content"


class _TolerantStream:
    """Envolve stdout/stderr para que escrever num pipe fechado não derrube o motor.

    Se o processo que lê a saída do motor morrer, qualquer aviso impresso (do
    próprio motor ou de uma biblioteca) levantaria BrokenPipeError no meio de
    uma requisição.
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
    parser = argparse.ArgumentParser(prog="qlp-engine", description="Motor da Quantum Learning Platform")
    parser.add_argument("--port", type=int, default=0, help="porta local (0 = aleatória)")
    parser.add_argument("--token", default=None, help="token de sessão (padrão: aleatório)")
    parser.add_argument(
        "--allow-origin",
        action="append",
        default=[],
        help="origem adicional permitida (ex.: http://localhost:5173 em desenvolvimento)",
    )
    parser.add_argument("--content-dir", type=Path, default=None)
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--job-timeout", type=float, default=5.0, help="segundos por execução")
    parser.add_argument(
        "--exit-on-stdin-close",
        action="store_true",
        help="encerra quando o stdin fechar (o shell desktop mantém o pipe aberto enquanto vive)",
    )
    return parser.parse_args(argv)


async def serve_forever(args: argparse.Namespace) -> None:
    token = args.token or secrets.token_urlsafe(32)
    content = ContentLibrary(args.content_dir or _default_content_dir())
    progress = ProgressStore(args.data_dir or default_data_dir())
    pool = WorkerPool(job_timeout=args.job_timeout)
    pool.warm_up()

    engine = EngineServer(content, progress, pool, token, tuple(args.allow_origin))
    server = await engine.start(args.port)
    port = server.sockets[0].getsockname()[1]
    print(json.dumps({"event": "ready", "port": port, "token": token}), flush=True)
    stop = asyncio.Event()
    if args.exit_on_stdin_close:
        _watch_stdin(asyncio.get_running_loop(), stop)
    try:
        await stop.wait()
    finally:
        server.close()
        pool.close()
        progress.close()


def _watch_stdin(loop: asyncio.AbstractEventLoop, stop: asyncio.Event) -> None:
    """Se o processo pai morrer (mesmo sem avisar), o pipe fecha e o motor sai junto."""

    def wait_for_eof() -> None:
        try:
            while sys.stdin.buffer.read(4096):
                pass
        except (OSError, ValueError):
            pass
        loop.call_soon_threadsafe(stop.set)

    threading.Thread(target=wait_for_eof, daemon=True).start()


def main(argv=None) -> None:
    multiprocessing.freeze_support()
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
