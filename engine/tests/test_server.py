import asyncio
import json

import pytest
from websockets.asyncio.client import connect
from websockets.exceptions import InvalidStatus

from qlp_engine.pool import WorkerPool
from qlp_engine.progress import ProgressStore
from qlp_engine.server import EngineServer

TOKEN = "test-secret"
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
            track1 = next(track for track in catalog["catalog"]["tracks"] if track["id"] == 1)
            first = track1["sections"][0]
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
            assert progress.all()["1.1"]["attempts"] == 1 and not progress.all()["1.1"]["completed"]

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
            await client.call(type="run", code=GOOD)  # warm up the worker
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
            assert len(events) >= 2, "the curve must arrive in batches during training"
            streamed = [v for event in events for v in event["series"]["cost"]]
            assert streamed == series["cost"], "the summed batches give the whole series"

    with_server(test, library=library)


def test_training_can_be_cancelled(library):
    async def test(url, _):
        async with connect(f"{url}/?token={TOKEN}") as websocket:
            client = Client(websocket)
            await client.call(type="run", code=GOOD)  # warm up the worker
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
            # PennyLane: the QNode is drawn with the code's `params` variable.
            from_pl = await client.call(type="export", code=pennylane, format="qasm3")
            assert from_pl["ok"], from_pl
            assert "ry(0.5) q[0];" in from_pl["text"]
            refused = await client.call(type="export", code=noisy, format="qasm2")
            assert refused["ok"] is False and "Noise channels" in refused["error"]["message"]

    with_server(test, library=library)


def with_public_server(test, library, max_connections=0, workers=1):
    from qlp_engine.pool import WorkerGroup

    async def scenario():
        pool = WorkerGroup(workers) if workers > 1 else WorkerPool()
        engine = EngineServer(
            library, None, pool, "nao-usado", ("https://quantum.example",), public=True, max_connections=max_connections
        )
        server = await engine.start(0)
        port = server.sockets[0].getsockname()[1]
        try:
            await test(f"ws://127.0.0.1:{port}")
        finally:
            server.close()
            await server.wait_closed()
            pool.close()

    asyncio.run(scenario())


def test_public_mode_requires_the_site_origin_and_keeps_progress_in_the_browser(library):
    async def test(url):
        with pytest.raises(InvalidStatus):  # no Origin: it is not the site
            async with connect(url):
                pass
        with pytest.raises(InvalidStatus):
            async with connect(url, origin="https://outro.example"):
                pass
        async with connect(url, origin="https://quantum.example") as websocket:  # no token
            client = Client(websocket)
            catalog = await client.call(type="catalog")
            assert catalog["ok"] and catalog["progress_storage"] == "client" and catalog["progress"] == {}
            assert (await client.call(type="progress.save", lesson_id="1.1", code="x"))["ok"] is True
            assert (await client.call(type="catalog"))["progress"] == {}
            assert (await client.call(type="run", code=GOOD))["ok"] is True

    with_public_server(test, library)


def test_public_mode_refuses_to_start_without_an_origin(library):
    with pytest.raises(ValueError):
        EngineServer(library, None, WorkerPool(), "t", (), public=True)


def test_connection_limit(library):
    async def test(url):
        async with connect(url, origin="https://quantum.example"):
            with pytest.raises(InvalidStatus) as refused:
                async with connect(url, origin="https://quantum.example"):
                    pass
            assert refused.value.response.status_code == 503

    with_public_server(test, library, max_connections=1)


def test_worker_group_runs_jobs_in_parallel(library):
    import time

    # Long enough (about half a second) that timing noise on slow CI machines stays small.
    slow = "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\n" + "x = sum(range(3_000_000))\n" * 12

    async def test(url):
        async with connect(url, origin="https://quantum.example") as a, connect(url, origin="https://quantum.example") as b:
            await Client(a).call(type="run", code=GOOD)  # warm up
            await asyncio.gather(Client(a).call(type="shots", code=GOOD), Client(b).call(type="shots", code=GOOD))
            start = time.perf_counter()
            await Client(a).call(type="shots", code=slow)
            alone = time.perf_counter() - start
            start = time.perf_counter()
            results = await asyncio.gather(Client(a).call(type="shots", code=slow), Client(b).call(type="shots", code=slow))
            together = time.perf_counter() - start
            assert all(r["ok"] for r in results), results
            # In series two jobs take about twice as long as one; in parallel, well under that.
            assert together < 1.8 * alone, (alone, together)

    with_public_server(test, library, workers=2)


def test_progress_is_migrated_to_the_new_lesson_ids(tmp_path):
    import sqlite3

    db = sqlite3.connect(tmp_path / "progress.sqlite3")
    db.execute("CREATE TABLE progress (lesson_id TEXT PRIMARY KEY, code TEXT, completed_at REAL, hints_used INTEGER NOT NULL DEFAULT 0, updated_at REAL NOT NULL)")
    for lesson_id in ("2.5", "2.8", "3.5", "1.1"):
        db.execute("INSERT INTO progress VALUES (?, ?, 1.0, 0, 1.0)", (lesson_id, f"code {lesson_id}"))
    db.commit()
    db.close()

    store = ProgressStore(tmp_path)
    saved = store.all()
    assert set(saved) == {"2.6", "2.9", "4.1", "1.1"}
    assert saved["2.6"]["code"] == "code 2.5" and saved["4.1"]["code"] == "code 3.5"
    store.close()
    assert set(ProgressStore(tmp_path).all()) == {"2.6", "2.9", "4.1", "1.1"}  # runs only once


def test_solution_is_given_on_request_and_marks_the_progress(library):
    """P2.1: unsuccessful attempts count; the solution is only shown on request and is recorded."""

    async def test(url, progress):
        async with connect(f"{url}/?token={TOKEN}") as websocket:
            client = Client(websocket)
            starter = (await client.call(type="lesson", lesson_id="1.1"))["lesson"]["starter_code"]
            for _ in range(2):
                assert not (await client.call(type="validate", code=starter, lesson_id="1.1"))["passed"]
            assert progress.all()["1.1"]["attempts"] == 2
            assert not progress.all()["1.1"]["solution_seen"]

            solution = await client.call(type="solution", lesson_id="1.1")
            assert solution["ok"] and "#" in solution["code"]
            assert progress.all()["1.1"]["solution_seen"] and not progress.all()["1.1"]["completed"]

            assert (await client.call(type="validate", code=solution["code"], lesson_id="1.1"))["passed"]
            entry = (await client.call(type="catalog"))["progress"]["1.1"]
            assert entry["completed"] and entry["with_solution"]

            # Completing first and viewing the solution afterwards does not mark "with solution".
            code = library.validation_bundle("1.2")["solution"]
            assert (await client.call(type="validate", code=code, lesson_id="1.2"))["passed"]
            await client.call(type="solution", lesson_id="1.2")
            entry = progress.all()["1.2"]
            assert entry["solution_seen"] and not entry["with_solution"]

            challenge = await client.call(type="solution", lesson_id="1.1", challenge=True)
            assert challenge["ok"] and progress.all()["1.1:challenge"]["solution_seen"]
            assert not (await client.call(type="solution", lesson_id="0.1", challenge=True))["ok"]

    with_server(test, library=library)


def test_review_questions_and_catalog_flags(library):
    async def test(url, progress):
        async with connect(f"{url}/?token={TOKEN}") as websocket:
            client = Client(websocket)
            catalog = (await client.call(type="catalog"))["catalog"]
            tracks = {track["id"]: track for track in catalog["tracks"]}
            assert tracks[0]["review"] is False and tracks[1]["review"] is True
            assert tracks[1]["sections"][0]["estimated_minutes"] > 0
            review = await client.call(type="review", track=1)
            assert review["ok"] and 8 <= len(review["questions"]) <= 12
            assert not (await client.call(type="review", track=0))["ok"]
            assert not (await client.call(type="review", track="x"))["ok"]
            # The score is kept in the progress, under the key "review:<track>".
            await client.call(type="progress.save", lesson_id="review:1", code="9/12", completed=True)
            assert progress.all()["review:1"]["code"] == "9/12"

    with_server(test, library=library)


def test_project_progress_follows_the_renumbering_of_track_3(tmp_path):
    store = ProgressStore(tmp_path)
    store.save("3.5", code="curve", completed=True)
    store._db.execute("PRAGMA user_version = 1")
    store._db.commit()
    store.close()
    saved = ProgressStore(tmp_path).all()
    assert "3.5" not in saved and saved["3.9"]["code"] == "curve"


def test_single_user_mode_serves_the_interface_and_keeps_progress(library, tmp_path):
    """P2.2 (local container): interface and engine on the same port, no token, progress on the server."""
    import urllib.error
    import urllib.request

    site = tmp_path / "web"
    (site / "assets").mkdir(parents=True)
    (site / "index.html").write_text("<!doctype html><title>qlp</title>", encoding="utf-8")
    (site / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("outside the folder", encoding="utf-8")

    async def scenario():
        pool = WorkerPool()
        progress = ProgressStore(tmp_path / "data")
        engine = EngineServer(
            library, progress, pool, "nao-usado", ("http://localhost:8080",), single_user=True, static_dir=site
        )
        server = await engine.start(0)
        port = server.sockets[0].getsockname()[1]

        def get(path):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as response:
                    return response.status, response.headers, response.read()
            except urllib.error.HTTPError as error:
                return error.code, error.headers, error.read()

        try:
            status, headers, body = await asyncio.to_thread(get, "/")
            assert status == 200 and b"<title>qlp</title>" in body and headers["Content-Type"].startswith("text/html")
            status, headers, body = await asyncio.to_thread(get, "/assets/app.js")
            assert status == 200 and body == b"console.log(1)" and "immutable" in headers["Cache-Control"]
            assert (await asyncio.to_thread(get, "/assets/missing.js"))[0] == 404
            assert b"<title>qlp</title>" in (await asyncio.to_thread(get, "/some/route"))[2]  # SPA
            for escape in ("/../secret.txt", "/%2e%2e/secret.txt", "/assets/../../secret.txt"):
                assert b"outside the folder" not in (await asyncio.to_thread(get, escape))[2]

            url = f"ws://127.0.0.1:{port}/engine"
            with pytest.raises(InvalidStatus):  # another browser page does not get in
                async with connect(url, origin="https://outro.example"):
                    pass
            async with connect(url, origin="http://localhost:8080") as websocket:
                client = Client(websocket)
                assert (await client.call(type="catalog"))["progress_storage"] == "engine"
                assert (await client.call(type="validate", code=GOOD, lesson_id="1.1"))["passed"]
            assert progress.all()["1.1"]["completed"]
        finally:
            server.close()
            await server.wait_closed()
            pool.close()
            progress.close()

    asyncio.run(scenario())
    assert ProgressStore(tmp_path / "data", lesson_keys=library.lesson_keys).all()["1.1"]["completed"]  # survives a restart
