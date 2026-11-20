"""P1.3: the engine always replies, survives exit(), returns what was printed, migrates keys, uses WAL."""

import asyncio
import json
import sqlite3

import pytest

from ket_lab_engine import worker
from ket_lab_engine.progress import ProgressStore
from ket_lab_engine.server import EngineServer


class FakeSocket:
    def __init__(self):
        self.sent = []

    async def send(self, text):
        self.sent.append(json.loads(text))


class BoomProgress:
    def all(self):
        raise sqlite3.OperationalError("database is locked")


def ask(engine, raw):
    socket = FakeSocket()
    asyncio.run(engine._handle_message(socket, raw, {"seq": 0}))
    assert len(socket.sent) == 1, "every request must get exactly one reply"
    return socket.sent[0]


@pytest.fixture()
def engine(library):
    return EngineServer(library, ProgressStore(None), pool=None, token="t")


def test_unexpected_exception_still_gets_an_internal_error_reply(library):
    engine = EngineServer(library, BoomProgress(), pool=None, token="t")
    reply = ask(engine, json.dumps({"id": 7, "type": "catalog"}))
    assert reply["id"] == 7 and reply["ok"] is False
    assert reply["error"]["kind"] == "internal"
    assert "locked" not in reply["error"]["message"]  # no raw detail for the learner


@pytest.mark.parametrize(
    "message",
    [
        {"type": "progress.save", "lesson_id": ["1.1"], "code": "x"},
        {"type": "progress.save", "lesson_id": 11},
        {"type": "progress.save", "lesson_id": "1.1", "code": 5},
        {"type": "progress.save", "lesson_id": "x" * 500},
        {"type": "progress.save", "lesson_id": "1.1", "hints_used": "many"},
        {"type": "search", "query": {"a": 1}},
        {"type": "lesson", "lesson_id": {"a": 1}},
        {"type": "run", "code": 12},
        {"type": "run", "code": "x" * 200_000},
        {"type": ["run"]},
        {"type": "shots", "code": "x", "shots": "lots"},
        {"type": "validate", "code": "x", "lesson_id": "1.1", "controls": [1]},
        [1, 2, 3],
        "text",
        None,
    ],
)
def test_malformed_messages_get_a_protocol_error(engine, message):
    reply = ask(engine, json.dumps(message))
    assert reply["ok"] is False and reply["error"]["kind"] == "protocol", reply
    assert not engine.progress.all()  # nothing was saved


def test_invalid_json_gets_a_protocol_error(engine):
    reply = ask(engine, "{not json")
    assert reply["error"]["kind"] == "protocol"


def test_exit_in_learner_code_is_reported_and_does_not_end_the_worker():
    for body in ("raise SystemExit", "raise SystemExit(3)", "raise GeneratorExit"):
        code = "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nprint('before')\n" + body + "\n"
        reply = worker.handle({"type": "run", "code": code})
        assert reply["ok"] is False and reply["error"]["kind"] == "runtime", (body, reply)
        assert "tried to exit" in reply["error"]["message"]
        assert reply["error"]["line"] == 4
        assert reply["stdout"] == "before\n"
    # exit() and quit() are refused earlier, by the static check
    assert worker.handle({"type": "run", "code": "exit()\n"})["error"]["kind"] == "guard"
    assert worker.handle({"type": "ping"}) == {"ok": True}


def test_exit_inside_validation_is_a_normal_failed_check():
    lesson = {"id": "t", "solution": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nqc.x(0)\n",
              "validation": {"type": "state_fidelity"}}
    reply = worker.handle({"type": "validate", "code": "print('hi')\nraise SystemExit\n", "lesson": lesson})
    assert reply["ok"] is True and reply["passed"] is False and reply["code"] == "error"
    assert "tried to exit" in reply["message"] and reply["stdout"] == "hi\n"


def test_output_printed_before_an_error_comes_back_with_it():
    code = "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nprint('step 1')\nprint(1 / 0)\n"
    reply = worker.handle({"type": "run", "code": code})
    assert reply == {
        "ok": False,
        "error": {"message": "ZeroDivisionError: division by zero", "line": 4, "kind": "runtime"},
        "stdout": "step 1\n",
    }
    # python lessons use the same path
    reply = worker.handle({"type": "run", "framework": "python", "code": "print('a')\nraise ValueError('b')\n"})
    assert reply["ok"] is False and reply["stdout"] == "a\n"


def test_no_stdout_field_when_nothing_was_printed():
    reply = worker.handle({"type": "run", "code": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\n1/0\n"})
    assert reply["ok"] is False and "stdout" not in reply


def test_output_survives_a_circuit_the_simulator_refuses():
    code = "from qiskit import QuantumCircuit\nprint('built')\nqc = QuantumCircuit(40)\nqc.h(0)\n"
    reply = worker.handle({"type": "run", "code": code})
    assert reply["ok"] is False and reply["error"]["kind"] == "simulation" and reply["stdout"] == "built\n"


# -- progress store ------------------------------------------------------------------------------


def _legacy_db(path, version, rows, notes=()):
    db = sqlite3.connect(path / "progress.sqlite3")
    db.execute("CREATE TABLE progress (lesson_id TEXT PRIMARY KEY, code TEXT, completed_at REAL, hints_used INTEGER NOT NULL DEFAULT 0, updated_at REAL NOT NULL)")
    for lesson_id in rows:
        db.execute("INSERT INTO progress VALUES (?, ?, 1.0, 0, 1.0)", (lesson_id, f"code {lesson_id}"))
    if notes:
        db.execute("CREATE TABLE notes (key TEXT PRIMARY KEY, body TEXT NOT NULL, updated_at TEXT NOT NULL)")
        for key in notes:
            db.execute("INSERT INTO notes VALUES (?, ?, 'x')", (key, f"note {key}"))
    db.execute(f"PRAGMA user_version = {version}")
    db.commit()
    db.close()


def test_challenge_keys_and_notes_move_with_their_lesson(tmp_path):
    _legacy_db(
        tmp_path, 0,
        ["2.5", "2.5:challenge", "2.8:challenge", "3.5", "3.5:challenge", "3.6:challenge", "1.1:challenge"],
        notes=["lesson:2.5", "lesson:3.5", "general"],
    )
    store = ProgressStore(tmp_path)
    saved = store.all()
    assert set(saved) == {"2.6", "2.6:challenge", "2.9:challenge", "4.1", "4.1:challenge", "4.2:challenge", "1.1:challenge"}
    assert saved["2.6:challenge"]["code"] == "code 2.5:challenge"
    notes = store.notes_all()
    assert set(notes) == {"lesson:2.6", "lesson:4.1", "general"}
    assert notes["lesson:2.6"]["body"] == "note lesson:2.5"


def test_challenge_key_of_the_track_3_project_follows_it_to_3_9(tmp_path):
    _legacy_db(tmp_path, 1, ["3.5", "3.5:challenge"], notes=["lesson:3.5"])
    store = ProgressStore(tmp_path)
    assert set(store.all()) == {"3.9", "3.9:challenge"}
    assert set(store.notes_all()) == {"lesson:3.9"}


def test_a_rename_never_overwrites_an_existing_target(tmp_path):
    store = ProgressStore(tmp_path)
    store.save("5.1", code="old")
    store.save("5.2", code="new")
    store._rename_lesson("5.1", "5.2")
    assert store.all()["5.2"]["code"] == "new" and store.all()["5.1"]["code"] == "old"


def test_database_uses_wal_and_a_busy_timeout(tmp_path):
    store = ProgressStore(tmp_path)
    assert store._db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert store._db.execute("PRAGMA busy_timeout").fetchone()[0] >= 1000
    assert store._db.execute("PRAGMA user_version").fetchone()[0] == 3


def test_startup_backup_one_per_day_last_five_kept(tmp_path, monkeypatch):
    first = ProgressStore(tmp_path)  # new database: nothing to protect yet
    first.save("1.1", code="mine", completed=True)
    first.close()
    assert not list(tmp_path.glob("progress-*.sqlite3"))
    for day in ("20260101", "20260102", "20260103", "20260104", "20260105", "20260106"):
        (tmp_path / f"progress-{day}.sqlite3").write_bytes(b"old")
    ProgressStore(tmp_path).close()
    ProgressStore(tmp_path).close()  # a second start the same day adds nothing
    backups = sorted(path.name for path in tmp_path.glob("progress-*.sqlite3"))
    assert len(backups) == 5 and "progress-20260101.sqlite3" not in backups and "progress-20260102.sqlite3" not in backups
    today = backups[-1]
    assert today > "progress-20260106.sqlite3"
    copy = sqlite3.connect(tmp_path / today)
    assert copy.execute("SELECT code FROM progress WHERE lesson_id = '1.1'").fetchone() == ("mine",)
    copy.close()
    assert not list(tmp_path.glob("*.part"))
