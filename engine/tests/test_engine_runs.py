"""Run replies: analysis for python lessons, bounded replies, shots, stopping a Check, WorkerGroup cancel."""

import asyncio
import json
import time

import numpy as np

from ket_lab_engine import geometry, server, simulator, worker
from ket_lab_engine.pool import WorkerGroup, WorkerPool
from ket_lab_engine.server import EngineServer
from ket_lab_engine.progress import ProgressStore

# -- python lessons run analysis.py ---------------------------------------------------------------


def test_python_lesson_returns_its_analysis():
    job = {"type": "run", "framework": "python", "code": "x = [1, 2, 3]\n",
           "analysis": "def analyze(ns):\n    return {'total': sum(ns['x'])}\n"}
    reply = worker.handle(job)
    assert reply["ok"] and reply["analysis"] == {"total": 6}


def test_python_lesson_without_analysis_is_unchanged():
    reply = worker.handle({"type": "run", "framework": "python", "code": "x = 1\n"})
    assert reply["ok"] and "analysis" not in reply


def test_a_failing_analysis_does_not_break_the_run():
    job = {"type": "run", "framework": "python", "code": "x = 1\n", "analysis": "def analyze(ns):\n    raise ValueError('boom')\n"}
    reply = worker.handle(job)
    assert reply["ok"] and "boom" in reply["analysis"]["error"] and reply["variables"]


# -- bounded replies ---------------------------------------------------------------------------------

BIG = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(10)
for i in range(60):
    for q in range(10):
        qc.h(q)
    for q in range(9):
        qc.cx(q, q + 1)
    qc.rz(0.1 * i, 3)
    qc.t(5)
    qc.s(7)
    qc.ry(0.2, 9)
    qc.rx(0.3, 1)
    qc.x(2)
    qc.z(4)
"""


def test_evenly_spaced_includes_both_ends():
    picked = geometry.evenly_spaced(1001, 11)
    assert len(picked) == 11 and 0 in picked and 1000 in picked
    assert geometry.evenly_spaced(5, 9) == set(range(5))
    assert geometry.evenly_spaced(50, 1) == {49}


def test_small_run_has_no_truncation_fields():
    reply = worker.handle({"type": "run", "code": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n"})
    assert "truncated" not in reply and "full_snapshots" not in reply and "notice" not in reply
    assert all("reduced" not in snap and snap["amplitudes"] for snap in reply["snapshots"])


def test_large_run_is_bounded_and_flagged():
    reply = worker.handle({"type": "run", "code": BIG})
    assert reply["ok"] and reply["truncated"] is True
    steps, snapshots = reply["steps"], reply["snapshots"]
    assert len(snapshots) == len(steps) + 1  # shape unchanged: one snapshot per step plus the initial one
    full = reply["full_snapshots"]
    assert full[0] == 0 and full[-1] == len(steps) and len(full) <= 150_000 // 1024 + 1
    assert "evenly spaced" in reply["notice"]
    for index, snap in enumerate(snapshots):
        assert len(snap["bloch"]) == 10 and len(snap["purity"]) == 10  # light data on every step
        if index in full:
            assert len(snap["amplitudes"]) == 1024 and len(snap["probabilities"]) == 1024 and "reduced" not in snap
        else:
            assert snap["amplitudes"] is None and snap["probabilities"] == [] and snap["reduced"] is True
    assert len(json.dumps(reply)) < 8_000_000


def test_collector_matches_the_kept_trajectory_for_full_snapshots():
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(3)
    qc.h(0), qc.cx(0, 1), qc.t(2)
    kept = geometry.describe_trajectory(simulator.run_trajectory(qc))
    collector = geometry.SnapshotCollector()
    streamed = geometry.describe_trajectory(simulator.run_trajectory(qc, observer=collector), collector)
    assert kept == streamed


def test_density_run_streams_without_keeping_states_and_is_bounded():
    ops = [simulator.Op("gate", "h", (0,), matrix=np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2))] * 1
    ops += [simulator.Op("channel", "depolarizing", (0,), kraus=[np.eye(2, dtype=complex) * np.sqrt(0.9),
                                                                  np.array([[0, 1], [1, 0]], dtype=complex) * np.sqrt(0.1)])] * 400
    collector = geometry.SnapshotCollector(budget=2000)  # 2000 >> 8 qubits = 7 -> raised to the minimum of 24
    trajectory = simulator.run_ops_trajectory(ops, [1] * len(ops), 8, observer=collector)
    assert trajectory.states[0] is None and trajectory.states[-1].shape == (256, 256)
    reply = geometry.describe_trajectory(trajectory, collector)
    assert reply["truncated"] and len(reply["full_snapshots"]) == geometry.MIN_FULL_SNAPSHOTS
    assert all(snap["amplitudes"] is None for snap in reply["snapshots"])
    assert sum(1 for snap in reply["snapshots"] if snap["probabilities"]) == geometry.MIN_FULL_SNAPSHOTS


def test_large_reply_is_encoded_off_the_event_loop(monkeypatch):
    seen = []
    real = asyncio.to_thread

    async def spy(function, *args, **kwargs):
        seen.append(function)
        return await real(function, *args, **kwargs)

    monkeypatch.setattr(server.asyncio, "to_thread", spy)
    big = {"num_qubits": 10, "snapshots": [{}] * 100}
    small = {"num_qubits": 2, "snapshots": [{}] * 3}
    assert json.loads(asyncio.run(server._encode(big)))["num_qubits"] == 10
    assert len(seen) == 1
    asyncio.run(server._encode(small))
    assert len(seen) == 1


# -- shots ----------------------------------------------------------------------------------------------


def test_shots_skip_the_trajectory(monkeypatch):
    def boom(*args, **kwargs):
        raise AssertionError("the shots job must not build a trajectory")

    monkeypatch.setattr(simulator, "run_trajectory", boom)
    reply = worker.handle({"type": "shots", "shots": 100, "code": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nqc.h(0)\nqc.measure_all()\n"})
    assert reply["ok"] and reply["shots"] == 100 and sum(reply["counts"].values()) == 100


def test_shots_announce_the_sampling_phase():
    events = []
    worker.handle({"type": "shots", "code": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nqc.h(0)\n"}, events.append)
    assert events == [{"event": "phase", "name": "sampling"}]


class FakeConnection:
    def __init__(self, script):
        self.script = list(script)
        self.sent = []

    def send(self, job):
        self.sent.append(job)

    def poll(self, timeout=0):
        if self.script:
            return True
        time.sleep(min(timeout, 0.01))
        return False

    def recv(self):
        return self.script.pop(0)

    def close(self):
        pass


def fake_pool(script):
    pool = WorkerPool(job_timeout=0.3)
    pool._ensure_ready = lambda: None
    pool._connection = FakeConnection(script)
    pool._restart = lambda: setattr(pool, "restarted", True)
    return pool


def test_timeout_after_the_sampling_phase_carries_the_phase():
    pool = fake_pool([{"event": "phase", "name": "sampling"}])
    reply = asyncio.run(pool.submit({"type": "shots"}, timeout=0.2))
    assert reply["error"]["kind"] == "timeout" and reply["error"]["phase"] == "sampling"
    plain = asyncio.run(fake_pool([]).submit({"type": "run"}, timeout=0.1))
    assert "phase" not in plain["error"]


class PoolStub:
    job_timeout = 5.0

    def __init__(self, reply):
        self.reply, self.calls, self.cancelled = reply, [], []

    async def submit(self, job, timeout=None, is_stale=None, on_event=None, tag=None):
        self.calls.append({"job": job, "timeout": timeout, "tag": tag})
        return self.reply

    def cancel(self, tag):
        self.cancelled.append(tag)


class Socket:
    def __init__(self):
        self.sent = []

    async def send(self, text):
        self.sent.append(json.loads(text))


def talk(engine, socket, **message):
    asyncio.run(engine._handle_message(socket, json.dumps(message), {"seq": 0}))
    return socket.sent[-1]


def test_heavy_shots_timeout_gets_its_own_message(library):
    timeout = {"ok": False, "error": {"message": "x", "line": None, "kind": "timeout", "phase": "sampling"}}
    engine = EngineServer(library, ProgressStore(None), PoolStub(timeout), "t")
    reply = talk(engine, Socket(), id=1, type="shots", code="qc = 1", shots=10)
    assert reply["error"]["kind"] == "timeout" and "once per shot" in reply["error"]["message"]
    assert "infinite loop" not in reply["error"]["message"]


# -- Check can be stopped ------------------------------------------------------------------------------


def test_validate_is_tagged_and_cancel_uses_the_same_tag(library):
    stub = PoolStub({"ok": True, "passed": False, "code": "x", "message": "m", "fidelity": None, "line": None})
    engine = EngineServer(library, ProgressStore(None), stub, "t")
    socket = Socket()
    talk(engine, socket, id=7, type="validate", code="qc = 1", lesson_id="1.1")
    assert stub.calls[0]["tag"] == (id(socket), 7)
    asyncio.run(engine._dispatch({"type": "cancel", "target": 7}, {"seq": 0}, socket))
    assert stub.cancelled == [(id(socket), 7)]


def test_a_running_check_is_cancelled_and_saves_nothing(library):
    async def scenario():
        pool = fake_pool([])
        pool.job_timeout = 30
        engine = EngineServer(library, ProgressStore(None), pool, "t")
        socket = Socket()
        message = json.dumps({"id": 3, "type": "validate", "code": "qc = 1", "lesson_id": "1.1"})
        task = asyncio.create_task(engine._handle_message(socket, message, {"seq": 0}))
        await asyncio.sleep(0.2)
        await engine._dispatch({"type": "cancel", "target": 3}, {"seq": 0}, socket)
        await asyncio.wait_for(task, 5)
        return socket.sent[0], engine

    reply, engine = asyncio.run(scenario())
    assert reply["ok"] is False and reply["error"]["kind"] == "cancelled" and engine.progress.all() == {}


# -- WorkerGroup cancel ----------------------------------------------------------------------------------


class SlowPool:
    job_timeout = 5.0

    def __init__(self):
        self.release = None
        self.cancelled = []

    async def submit(self, job, timeout=None, is_stale=None, on_event=None, tag=None):
        if self.release is None:
            self.release = asyncio.Event()
        await self.release.wait()
        return {"ok": True, "job": job["n"]}

    def cancel(self, tag):
        self.cancelled.append(tag)


def test_group_cancel_of_a_job_still_waiting_for_a_worker():
    async def scenario():
        group = WorkerGroup(1)
        group.pools = [SlowPool()]
        first = asyncio.create_task(group.submit({"n": 1}, tag="a"))
        await asyncio.sleep(0.05)
        second = asyncio.create_task(group.submit({"n": 2}, tag="b"))  # waits: the only worker is busy
        await asyncio.sleep(0.05)
        group.cancel("b")
        group.pools[0].release.set()
        return await first, await second

    first, second = asyncio.run(scenario())
    assert first == {"ok": True, "job": 1}
    assert second["ok"] is False and second["error"]["kind"] == "cancelled"
