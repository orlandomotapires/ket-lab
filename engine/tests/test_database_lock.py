"""Two connections to the same progress file: a lock must become an error reply, never a freeze."""

import asyncio
import json
import sqlite3
import time

import pytest

from ket_lab_engine.progress import ProgressStore
from ket_lab_engine.server import EngineServer


class Socket:
    def __init__(self):
        self.sent = []

    async def send(self, text):
        self.sent.append(json.loads(text))


def test_a_locked_database_fails_fast_then_recovers(tmp_path):
    first = ProgressStore(tmp_path)
    second = ProgressStore(tmp_path)
    second._db.execute("PRAGMA busy_timeout = 150")
    first._db.execute("BEGIN IMMEDIATE")  # the other connection holds the write lock
    start = time.monotonic()
    with pytest.raises(sqlite3.OperationalError, match="locked"):
        second.save("1.1", code="x")
    assert time.monotonic() - start < 3
    first._db.rollback()
    second.save("1.1", code="x")  # the lock is gone: the next write works
    assert first.all()["1.1"]["code"] == "x"


def test_a_lock_inside_a_request_gets_a_reply(tmp_path, library):
    holder = ProgressStore(tmp_path)
    store = ProgressStore(tmp_path)
    store._db.execute("PRAGMA busy_timeout = 100")
    engine = EngineServer(library, store, pool=None, token="t")
    holder._db.execute("BEGIN IMMEDIATE")
    socket = Socket()
    asyncio.run(engine._handle_message(socket, json.dumps({"id": 4, "type": "progress.save", "lesson_id": "1.1", "code": "x"}), {"seq": 0}))
    reply = socket.sent[0]
    assert reply["id"] == 4 and reply["ok"] is False and reply["error"]["kind"] == "internal"
    holder._db.rollback()
