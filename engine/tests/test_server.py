import asyncio
import json

import pytest
from websockets.asyncio.client import connect
from websockets.exceptions import InvalidStatus

from qlp_engine.pool import WorkerPool
from qlp_engine.progress import ProgressStore
from qlp_engine.server import EngineServer

TOKEN = "segredo-de-teste"
GOOD = "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nqc.x(0)\n"


class Client:
    def __init__(self, websocket):
        self.websocket = websocket
        self.next_id = 0

    async def call(self, **message):
        self.next_id += 1
        message["id"] = self.next_id
        await self.websocket.send(json.dumps(message))
        while True:
            response = json.loads(await self.websocket.recv())
            if response["id"] == message["id"]:
                return response


def with_server(test, job_timeout=5.0, library=None):
    async def scenario():
        pool = WorkerPool(job_timeout=job_timeout)
        progress = ProgressStore(None)
        engine = EngineServer(library, progress, pool, TOKEN, ("http://localhost:5173",))
        server = await engine.start(0)
        port = server.sockets[0].getsockname()[1]
        try:
            await test(f"ws://127.0.0.1:{port}", progress)
        finally:
            server.close()
            await server.wait_closed()
            pool.close()

    asyncio.run(scenario())


def test_rejects_missing_or_wrong_token(library):
    async def test(url, _):
        for target in (url, f"{url}/?token=errado"):
            with pytest.raises(InvalidStatus) as info:
                async with connect(target):
                    pass
            assert info.value.response.status_code == 401

    with_server(test, library=library)


def test_rejects_foreign_origin_even_with_token(library):
    async def test(url, _):
        with pytest.raises(InvalidStatus) as info:
            async with connect(f"{url}/?token={TOKEN}", origin="https://site-malicioso.example"):
                pass
        assert info.value.response.status_code == 403
        async with connect(f"{url}/?token={TOKEN}", origin="http://localhost:5173"):
            pass

    with_server(test, library=library)


def test_catalog_lesson_run_validate_and_progress(library):
    async def test(url, progress):
        async with connect(f"{url}/?token={TOKEN}") as websocket:
            client = Client(websocket)

            catalog = await client.call(type="catalog")
            first = catalog["catalog"]["tracks"][0]["sections"][0]
            assert first["id"] == "1.1" and first["available"] is True

            lesson = (await client.call(type="lesson", lesson_id="1.1"))["lesson"]
            assert "solution" not in lesson and lesson["starter_code"]

            run = await client.call(type="run", code=GOOD, lesson_id="1.1")
            assert run["ok"] and run["num_qubits"] == 1
            assert [step["line"] for step in run["steps"]] == [3]
            assert run["snapshots"][0]["bloch"] == [[0.0, 0.0, 1.0]]
            assert run["snapshots"][1]["bloch"] == [[0.0, 0.0, -1.0]]

            failed = await client.call(type="validate", code=lesson["starter_code"], lesson_id="1.1")
            assert failed["passed"] is False
            assert "1.1" not in progress.all()

            passed = await client.call(type="validate", code=GOOD, lesson_id="1.1")
            assert passed["passed"] is True
            assert progress.all()["1.1"]["completed"] is True

            shots = await client.call(type="shots", code=GOOD, shots=100)
            assert shots["counts"] == {"1": 100}

            broken = await client.call(type="run", code="qc = QuantumCircuit(1)\n")
            assert broken["ok"] is False and broken["error"]["line"] == 1

            unknown = await client.call(type="lesson", lesson_id="9.9")
            assert unknown["ok"] is False and unknown["error"]["kind"] == "content"

    with_server(test, library=library)


def test_infinite_loop_is_killed_and_engine_recovers(library):
    async def test(url, _):
        async with connect(f"{url}/?token={TOKEN}") as websocket:
            client = Client(websocket)
            await client.call(type="run", code=GOOD)  # aquece o worker
            stuck = await client.call(type="run", code="while True:\n    pass\n")
            assert stuck["error"]["kind"] == "timeout"
            again = await client.call(type="run", code=GOOD)
            assert again["ok"] is True

    with_server(test, job_timeout=1.0, library=library)


def test_memory_hog_does_not_take_the_engine_down(library):
    async def test(url, _):
        async with connect(f"{url}/?token={TOKEN}") as websocket:
            client = Client(websocket)
            hog = await client.call(type="run", code="import numpy as np\nx = np.ones(2**36)\n")
            assert hog["ok"] is False
            assert (await client.call(type="run", code=GOOD))["ok"] is True

    with_server(test, library=library)


def test_superseded_runs_are_dropped(library):
    async def test(url, _):
        async with connect(f"{url}/?token={TOKEN}") as websocket:
            for request_id in (1, 2, 3):
                await websocket.send(json.dumps({"id": request_id, "type": "run", "code": GOOD}))
            responses = {}
            while len(responses) < 3:
                response = json.loads(await websocket.recv())
                responses[response["id"]] = response
            assert responses[3]["ok"] is True
            assert sum(1 for r in responses.values() if r.get("stale")) >= 1

    with_server(test, library=library)
