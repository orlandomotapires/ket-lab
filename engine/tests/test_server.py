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
            if response["id"] == message["id"] and "event" not in response:
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


TRAINING = """from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
qc.h(0)
for epoch in range(150):
    work = sum(range(100_000))
    report(1 / (epoch + 1), accuracy=epoch / 150)
"""


def test_training_streams_progress_before_the_result(library):
    async def test(url, _):
        async with connect(f"{url}/?token={TOKEN}") as websocket:
            await websocket.send(json.dumps({"id": 1, "type": "run", "code": TRAINING, "train": True}))
            events, result = [], None
            while result is None:
                message = json.loads(await websocket.recv())
                if message.get("event") == "progress":
                    events.append(message)
                else:
                    result = message
            assert result["ok"] is True, result
            series = result["training"]["series"]
            assert len(series["cost"]) == 150 and len(series["accuracy"]) == 150
            assert len(events) >= 2, "a curva precisa chegar em lotes durante o treino"
            streamed = [v for event in events for v in event["series"]["cost"]]
            assert streamed == series["cost"], "os lotes somados dão a série inteira"

    with_server(test, library=library)


def test_training_can_be_cancelled(library):
    async def test(url, _):
        async with connect(f"{url}/?token={TOKEN}") as websocket:
            client = Client(websocket)
            await client.call(type="run", code=GOOD)  # aquece o worker
            endless = "i = 0\nwhile True:\n    i += 1\n    if i % 100000 == 0:\n        report(i)\n"
            await websocket.send(json.dumps({"id": 50, "type": "run", "code": endless, "train": True}))
            first = json.loads(await websocket.recv())
            assert first.get("event") == "progress"
            await websocket.send(json.dumps({"id": 51, "type": "cancel", "target": 50}))
            responses = {}
            while 50 not in responses:
                message = json.loads(await websocket.recv())
                if "event" not in message:
                    responses[message["id"]] = message
            assert responses[50]["error"]["kind"] == "cancelled"
            assert (await client.call(type="run", code=GOOD))["ok"] is True

    with_server(test, library=library)


def test_export_to_openqasm(library):
    bell = "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n"
    pennylane = (
        "import pennylane as qml\n"
        "from pennylane import numpy as np\n"
        "dev = qml.device('default.qubit', wires=2)\n"
        "@qml.qnode(dev)\n"
        "def circuit(params):\n"
        "    qml.RY(params[0], wires=0)\n"
        "    qml.CNOT(wires=[0, 1])\n"
        "    return qml.expval(qml.PauliZ(1))\n"
        "params = np.array([0.5])\n"
    )
    noisy = pennylane.replace("default.qubit", "default.mixed").replace(
        "    return", "    qml.BitFlip(0.1, wires=0)\n    return"
    )

    async def test(url, _):
        async with connect(f"{url}/?token={TOKEN}") as websocket:
            client = Client(websocket)
            qasm2 = await client.call(type="export", code=bell, format="qasm2")
            assert qasm2["ok"] and qasm2["text"].startswith("OPENQASM 2.0;") and "cx q[0],q[1];" in qasm2["text"]
            qasm3 = await client.call(type="export", code=bell, format="qasm3")
            assert qasm3["text"].startswith("OPENQASM 3.0;") and "cx q[0], q[1];" in qasm3["text"]
            # PennyLane: o QNode é desenhado com a variável `params` do código.
            from_pl = await client.call(type="export", code=pennylane, format="qasm3")
            assert from_pl["ok"], from_pl
            assert "ry(0.5) q[0];" in from_pl["text"]
            refused = await client.call(type="export", code=noisy, format="qasm2")
            assert refused["ok"] is False and "Noise channels" in refused["error"]["message"]

    with_server(test, library=library)
