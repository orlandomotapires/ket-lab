"""Servidor WebSocket local do motor.

Segurança: um WebSocket em localhost NÃO é protegido pela same-origin policy —
qualquer página aberta no navegador do aluno pode tentar conectar. Por isso:
  * escuta apenas em 127.0.0.1, em porta aleatória por padrão;
  * exige um token por sessão (query string `?token=`);
  * recusa conexões cujo cabeçalho Origin não esteja na lista permitida.
"""

from __future__ import annotations

import asyncio
import hmac
import http
import json
import os
import sys
from urllib.parse import parse_qs, urlparse

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

from . import i18n
from .content import ContentError, ContentLibrary
from .pool import WorkerPool
from .progress import ProgressStore

HOST = "127.0.0.1"
MAX_MESSAGE_BYTES = 512 * 1024
MAX_CODE_CHARS = 100_000

# QLP_LOG=1 registra no stderr o tipo de cada requisição (diagnóstico).
LOG_REQUESTS = os.environ.get("QLP_LOG") == "1"

# Origens da janela Tauri (varia por plataforma).
TAURI_ORIGINS = ("tauri://localhost", "http://tauri.localhost", "https://tauri.localhost")


class EngineServer:
    def __init__(
        self,
        content: ContentLibrary,
        progress: ProgressStore,
        pool: WorkerPool,
        token: str,
        allowed_origins: tuple[str, ...] = (),
    ):
        self.content = content
        self.progress = progress
        self.pool = pool
        self.token = token
        # None permite clientes sem cabeçalho Origin (não são navegadores); o token continua exigido.
        self.origins = [*TAURI_ORIGINS, *allowed_origins, None]

    async def start(self, port: int = 0):
        return await serve(
            self._handle_connection,
            HOST,
            port,
            origins=self.origins,
            process_request=self._check_token,
            max_size=MAX_MESSAGE_BYTES,
        )

    def _check_token(self, connection, request):
        query = parse_qs(urlparse(request.path).query)
        supplied = (query.get("token") or [""])[0]
        if not hmac.compare_digest(supplied.encode(), self.token.encode()):
            return connection.respond(http.HTTPStatus.UNAUTHORIZED, "token inválido\n")
        return None

    async def _handle_connection(self, websocket) -> None:
        _log(f"conexão aberta ({websocket.request.headers.get('Origin')})")
        latest_run = {"seq": 0}
        tasks: set[asyncio.Task] = set()
        try:
            async for raw in websocket:
                task = asyncio.create_task(self._handle_message(websocket, raw, latest_run))
                tasks.add(task)
                task.add_done_callback(tasks.discard)
        except ConnectionClosed:
            pass
        finally:
            _log(f"conexão encerrada (código {websocket.close_code}, motivo {websocket.close_reason!r})")
            for task in tasks:
                task.cancel()

    async def _handle_message(self, websocket, raw, latest_run: dict) -> None:
        request_id = None
        try:
            message = json.loads(raw)
            request_id = message.get("id")
            # Vale para esta tarefa e para a thread do pool que ela usar.
            i18n.set_lang(message.get("lang"))
            response = await self._dispatch(message, latest_run)
        except ContentError as exc:
            response = _error(str(exc), "content")
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, AttributeError) as exc:
            response = _error(i18n.t("server.bad_request", detail=exc), "protocol")
        response["id"] = request_id
        try:
            await websocket.send(json.dumps(response, ensure_ascii=False))
        except ConnectionClosed:
            pass

    async def _dispatch(self, message: dict, latest_run: dict) -> dict:
        kind = message["type"]
        _log(f"{kind} {message.get('lesson_id') or ''}".rstrip())

        if kind == "catalog":
            catalog = self.content.catalog(i18n.current())
            return {"ok": True, "catalog": catalog, "progress": self.progress.all()}

        if kind == "lesson":
            return {"ok": True, "lesson": self.content.lesson(message["lesson_id"], i18n.current())}

        if kind == "progress.save":
            self.progress.save(
                message["lesson_id"],
                code=message.get("code"),
                completed=message.get("completed"),
                hints_used=message.get("hints_used"),
            )
            return {"ok": True}

        if kind in ("run", "shots", "validate"):
            code = message["code"]
            if not isinstance(code, str) or len(code) > MAX_CODE_CHARS:
                return _error(i18n.t("server.bad_code"), "protocol")
            lesson_id = message.get("lesson_id")
            job = {"type": kind, "code": code, "seed": message.get("seed", 0), "lang": i18n.current()}

            timeout = self.content.timeout(lesson_id)
            if kind == "validate":
                job["lesson"] = self.content.validation_bundle(lesson_id, i18n.current())
                # Validar pode reexecutar o código várias vezes (casos secretos, treinos).
                result = await self.pool.submit(job, timeout=timeout * 3 if timeout else None)
                if result.get("passed"):
                    self.progress.save(lesson_id, code=code, completed=True)
                return result

            job.update(self.content.run_context(lesson_id))
            job["inputs"] = self.content.control_inputs(lesson_id, message.get("controls"))
            if kind == "shots":
                job["shots"] = message.get("shots", 1024)
                return await self.pool.submit(job, timeout=timeout)

            # run: só a edição mais recente interessa; execuções ultrapassadas são descartadas.
            latest_run["seq"] += 1
            seq = latest_run["seq"]
            return await self.pool.submit(job, timeout=timeout, is_stale=lambda: seq != latest_run["seq"])

        return _error(i18n.t("server.unknown_type", kind=kind), "protocol")


def _log(text: str) -> None:
    if not LOG_REQUESTS:
        return
    try:
        print(f"[qlp-engine] {text}", file=sys.stderr, flush=True)
    except (OSError, ValueError):
        pass  # sem terminal para escrever (ex.: processo pai encerrado); o log é opcional


def _error(message: str, kind: str) -> dict:
    return {"ok": False, "error": {"message": message, "line": None, "kind": kind}}
