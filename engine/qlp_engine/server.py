"""Servidor WebSocket local do motor.

Modo local (padrão): um WebSocket em localhost NÃO é protegido pela same-origin
policy, e qualquer página aberta no navegador do aluno pode tentar conectar. Por isso:
  * escuta apenas em 127.0.0.1, em porta aleatória por padrão;
  * exige um token por sessão (query string `?token=`);
  * recusa conexões cujo cabeçalho Origin não esteja na lista permitida.

Modo público (`--public`, motor hospedado atrás do site): não há token, mas o
Origin é obrigatório e precisa ser o do site; há um teto de conexões; e o
progresso não é guardado no servidor (fica no navegador de cada aluno). O
isolamento do código do aluno é responsabilidade do contêiner (deploy/).
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

from . import messages
from .content import ContentError, ContentLibrary
from .pool import WorkerPool
from .progress import ProgressStore

HOST = "127.0.0.1"
MAX_MESSAGE_BYTES = 512 * 1024
MAX_CODE_CHARS = 100_000
# Treinos (botão Executar no laboratório livre) podem levar bem mais que uma edição ao vivo.
TRAIN_TIMEOUT_S = 120.0

# QLP_LOG=1 registra no stderr o tipo de cada requisição (diagnóstico).
LOG_REQUESTS = os.environ.get("QLP_LOG") == "1"



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
    ):
        self.content = content
        self.progress = None if public else progress
        self.pool = pool
        self.token = token
        self.public = public
        self.max_connections = max_connections
        self.host = host
        self.connections = 0
        # Local: None permite clientes sem Origin (não são navegadores), e o token continua exigido.
        # Público: sem token, o Origin do site é a única credencial, então ele é obrigatório.
        if public and not allowed_origins:
            raise ValueError("o modo público exige ao menos um --allow-origin")
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
        if self.max_connections and self.connections >= self.max_connections:
            return connection.respond(http.HTTPStatus.SERVICE_UNAVAILABLE, "muitas conexões\n")
        if self.public:
            return None
        query = parse_qs(urlparse(request.path).query)
        supplied = (query.get("token") or [""])[0]
        if not hmac.compare_digest(supplied.encode(), self.token.encode()):
            return connection.respond(http.HTTPStatus.UNAUTHORIZED, "token inválido\n")
        return None

    async def _handle_connection(self, websocket) -> None:
        _log(f"conexão aberta ({websocket.request.headers.get('Origin')})")
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
            _log(f"conexão encerrada (código {websocket.close_code}, motivo {websocket.close_reason!r})")
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
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, AttributeError) as exc:
            response = _error(messages.t("server.bad_request", detail=exc), "protocol")
        response["id"] = request_id
        try:
            await websocket.send(json.dumps(response, ensure_ascii=False))
        except ConnectionClosed:
            pass

    async def _dispatch(self, message: dict, latest_run: dict, websocket=None) -> dict:
        kind = message["type"]
        _log(f"{kind} {message.get('lesson_id') or ''}".rstrip())

        if kind == "catalog":
            catalog = self.content.catalog()
            if self.progress is None:
                return {"ok": True, "catalog": catalog, "progress": {}, "progress_storage": "client"}
            return {"ok": True, "catalog": catalog, "progress": self.progress.all(), "progress_storage": "engine"}

        if kind == "lesson":
            return {"ok": True, "lesson": self.content.lesson(message["lesson_id"])}

        if kind == "search":
            query = str(message.get("query", ""))[:100]
            return {"ok": True, "results": self.content.search(query)}

        if kind == "progress.save":
            if self.progress is None:  # modo público: o navegador guarda o progresso
                return {"ok": True}
            self.progress.save(
                message["lesson_id"],
                code=message.get("code"),
                completed=message.get("completed"),
                hints_used=message.get("hints_used"),
            )
            return {"ok": True}

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
            if kind == "validate":
                job["lesson"] = self.content.validation_bundle(lesson_id)
                # Validar pode reexecutar o código várias vezes (casos secretos, treinos).
                result = await self.pool.submit(job, timeout=timeout * 3 if timeout else None)
                if result.get("passed") and self.progress is not None:
                    self.progress.save(lesson_id, code=code, completed=True)
                return result

            job.update(self.content.run_context(lesson_id))
            job["inputs"] = self.content.control_inputs(lesson_id, message.get("controls"))
            if kind == "export":
                # Exportar reexecuta o código; um treino do laboratório precisa do tempo de treino.
                job["format"] = message.get("format")
                return await self.pool.submit(job, timeout=max(timeout or 0, TRAIN_TIMEOUT_S))
            if kind == "run" and message.get("train"):
                return await self._train(job, message, websocket, timeout)
            if kind == "shots":
                job["shots"] = message.get("shots", 1024)
                return await self.pool.submit(job, timeout=timeout)

            # run: só a edição mais recente interessa; execuções ultrapassadas são descartadas.
            latest_run["seq"] += 1
            seq = latest_run["seq"]
            return await self.pool.submit(job, timeout=timeout, is_stale=lambda: seq != latest_run["seq"])

        return _error(messages.t("server.unknown_type", kind=kind), "protocol")

    async def _train(self, job: dict, message: dict, websocket, timeout: float | None) -> dict:
        """Execução longa pelo botão: envia as métricas de `report(...)` enquanto roda."""
        loop = asyncio.get_running_loop()
        request_id = message.get("id")
        job["stream"] = True

        def on_event(event: dict) -> None:  # thread do pool
            payload = json.dumps({"id": request_id, "event": "progress", "series": event.get("series", {})})
            loop.call_soon_threadsafe(lambda: asyncio.ensure_future(_send(websocket, payload)))

        return await self.pool.submit(
            job, timeout=max(timeout or 0, TRAIN_TIMEOUT_S), on_event=on_event, tag=(id(websocket), request_id)
        )


async def _send(websocket, payload: str) -> None:
    try:
        await websocket.send(payload)
    except ConnectionClosed:
        pass


def _log(text: str) -> None:
    if not LOG_REQUESTS:
        return
    try:
        print(f"[qlp-engine] {text}", file=sys.stderr, flush=True)
    except (OSError, ValueError):
        pass  # sem terminal para escrever (ex.: processo pai encerrado); o log é opcional


def _error(message: str, kind: str) -> dict:
    return {"ok": False, "error": {"message": message, "line": None, "kind": kind}}
