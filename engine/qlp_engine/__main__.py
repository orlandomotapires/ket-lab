"""Ponto de entrada do motor: `python -m qlp_engine` (o `npm run dev` o inicia).

Ao ficar pronto, imprime UMA linha JSON no stdout com a porta e o token:
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
        "--public",
        action="store_true",
        help="motor hospedado: sem token, Origin obrigatório, progresso no navegador (veja deploy/)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="interface de rede (0.0.0.0 dentro de um contêiner)")
    parser.add_argument("--workers", type=int, default=1, help="processos que executam código em paralelo")
    parser.add_argument("--max-connections", type=int, default=0, help="teto de conexões simultâneas (0 = sem teto)")
    return parser.parse_args(argv)


async def serve_forever(args: argparse.Namespace) -> None:
    token = args.token or secrets.token_urlsafe(32)
    content = ContentLibrary(args.content_dir or _default_content_dir())
    progress = None if args.public else ProgressStore(args.data_dir or default_data_dir())
    pool = WorkerGroup(args.workers, job_timeout=args.job_timeout) if args.workers > 1 else WorkerPool(job_timeout=args.job_timeout)
    pool.warm_up()

    engine = EngineServer(
        content, progress, pool, token, tuple(args.allow_origin),
        public=args.public, max_connections=args.max_connections, host=args.host,
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
