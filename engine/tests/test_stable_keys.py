"""Stable lesson keys: the database stores keys, the protocol speaks lesson ids."""

import asyncio
import json
import re
import sqlite3

import pytest

from qlp_engine.content import ContentLibrary
from qlp_engine.progress import KEYS_VERSION, KeyMap, ProgressError, ProgressStore
from qlp_engine.server import EngineServer

MAPPING = {"1.1": "qubit", "1.2": "superposition", "3.5": "ansatz_design", "3.6": "optimizers"}
SWAPPED = {**MAPPING, "3.5": "optimizers", "3.6": "ansatz_design"}  # the two lessons trade numbers


class FakeSocket:
    def __init__(self):
        self.sent = []

    async def send(self, text):
        self.sent.append(json.loads(text))


def ask(engine, **message):
    socket = FakeSocket()
    asyncio.run(engine._handle_message(socket, json.dumps({"id": 1, **message}), {"seq": 0}))
    return socket.sent[0]


def raw_rows(path):
    db = sqlite3.connect(path / "progress.sqlite3")
    progress = {row[0] for row in db.execute("SELECT lesson_id FROM progress")}
    notes = {row[0] for row in db.execute("SELECT key FROM notes")}
    version = db.execute("PRAGMA user_version").fetchone()[0]
    db.close()
    return progress, notes, version


def old_database(path):
    """What the current (pre-keys) code writes: rows under lesson ids."""
    store = ProgressStore(path)
    store.save("1.1", code="a", completed=True)
    store.save("3.5", code="ansatz", completed=True, hints_used=2)
    store.save("3.5:challenge", code="ansatz challenge", solution_seen=True)
    store.save("3.6", code="optimizers")
    store.save("sandbox", code="free lab")
    store.save("review:3", completed=True)
    store.note_save("lesson:3.5", "note about the ansatz")
    store.note_save("lesson:3.6", "note about optimizers")
    store.note_save("general", "free note")
    store.close()


# -- the content library ----------------------------------------------------------------------------


def test_every_lesson_has_a_unique_key_that_is_not_a_lesson_id(library):
    declared = json.loads((library.root / "lesson_keys.json").read_text())
    ids = library.lesson_ids
    assert [i for i in ids if i not in declared] == [], "add the new lesson to content/lesson_keys.json"
    keys = [declared[i] for i in ids]
    assert len(set(keys)) == len(keys)
    assert all(re.fullmatch(r"[a-z][a-z0-9_]{1,40}", key) for key in keys)
    assert not set(keys) & set(declared), "a key must never look like a lesson id"
    assert not set(keys) & {"sandbox", "general", "review", "lesson"}
    assert library.lesson_keys()["1.5"] == "bell_states"


def test_a_lesson_missing_from_the_file_gets_its_folder_name(library, tmp_path):
    import shutil

    root = tmp_path / "content"
    folder = library._lessons["1.1"]
    shutil.copytree(folder, root / folder.parent.name / folder.name)
    shutil.copy(library.root / "catalog.json", root / "catalog.json")
    assert ContentLibrary(root).lesson_keys() == {"1.1": "qubit"}


# -- translation at the boundary ----------------------------------------------------------------------


def test_keymap_translates_ids_challenges_and_notes_and_leaves_the_rest():
    keys = KeyMap(MAPPING)
    assert keys.to_key("3.5") == "ansatz_design" and keys.to_key("3.5:challenge") == "ansatz_design:challenge"
    assert keys.to_id("ansatz_design:challenge") == "3.5:challenge"
    assert keys.note_to_key("lesson:3.5") == "lesson:ansatz_design" and keys.note_to_id("lesson:ansatz_design") == "lesson:3.5"
    for other in ("sandbox", "general", "review:3", "9.9", "9.9:challenge"):
        assert keys.to_key(other) == other and keys.to_id(other) == other
        assert keys.note_to_key(other) == other


def test_the_database_holds_keys_and_the_protocol_ids(tmp_path):
    store = ProgressStore(tmp_path, lesson_keys=MAPPING)
    store.save("3.5", code="x", completed=True)
    store.save("3.5:challenge", failed_attempt=True)
    store.save("review:3", completed=True)
    store.note_save("lesson:3.5", "n")
    assert set(store.all()) == {"3.5", "3.5:challenge", "review:3"}
    assert set(store.notes_all()) == {"lesson:3.5"}
    progress, notes, _ = raw_rows(tmp_path)
    assert progress == {"ansatz_design", "ansatz_design:challenge", "review:3"} and notes == {"lesson:ansatz_design"}


# -- migration ----------------------------------------------------------------------------------------


def test_a_database_made_by_the_current_code_migrates(tmp_path):
    old_database(tmp_path)
    assert raw_rows(tmp_path)[0] >= {"3.5", "3.5:challenge", "3.6", "1.1"}
    store = ProgressStore(tmp_path, lesson_keys=MAPPING)
    progress, notes, version = raw_rows(tmp_path)
    assert version == KEYS_VERSION
    assert progress == {"qubit", "ansatz_design", "ansatz_design:challenge", "optimizers", "sandbox", "review:3"}
    assert notes == {"lesson:ansatz_design", "lesson:optimizers", "general"}
    everything = store.all()
    assert everything["3.5"]["code"] == "ansatz" and everything["3.5"]["completed"] and everything["3.5"]["hints_used"] == 2
    assert everything["3.5:challenge"]["solution_seen"] and everything["3.6"]["code"] == "optimizers"
    assert store.notes_all()["lesson:3.5"]["body"] == "note about the ansatz"


def test_the_daily_backup_taken_before_the_migration_keeps_the_old_ids(tmp_path):
    old_database(tmp_path)
    ProgressStore(tmp_path, lesson_keys=MAPPING).close()
    backups = list(tmp_path.glob("progress-*.sqlite3"))
    assert backups
    db = sqlite3.connect(backups[0])
    assert "3.5" in {row[0] for row in db.execute("SELECT lesson_id FROM progress")}
    db.close()


def test_migration_is_idempotent(tmp_path):
    old_database(tmp_path)
    ProgressStore(tmp_path, lesson_keys=MAPPING).close()
    first = raw_rows(tmp_path)
    again = ProgressStore(tmp_path, lesson_keys=MAPPING)
    assert raw_rows(tmp_path) == first
    assert again.all()["3.5"]["code"] == "ansatz"


def test_migration_never_overwrites_a_row_already_under_the_key(tmp_path):
    store = ProgressStore(tmp_path)
    store.save("3.5", code="old id")
    store.save("ansatz_design", code="already keyed")
    store.close()
    kept = ProgressStore(tmp_path, lesson_keys=MAPPING)
    progress, _, _ = raw_rows(tmp_path)
    assert progress == {"3.5", "ansatz_design"}  # neither lost
    assert kept._db.execute("SELECT code FROM progress WHERE lesson_id = 'ansatz_design'").fetchone()[0] == "already keyed"


def test_a_renumbering_needs_no_migration(tmp_path):
    old_database(tmp_path)
    ProgressStore(tmp_path, lesson_keys=MAPPING).close()
    before = raw_rows(tmp_path)
    store = ProgressStore(tmp_path, lesson_keys=SWAPPED)  # 3.5 and 3.6 swapped
    assert raw_rows(tmp_path) == before
    progress, notes = store.all(), store.notes_all()
    assert progress["3.6"]["code"] == "ansatz" and progress["3.5"]["code"] == "optimizers"
    assert progress["3.6:challenge"]["code"] == "ansatz challenge" and "3.5:challenge" not in progress
    assert notes["lesson:3.6"]["body"] == "note about the ansatz" and notes["lesson:3.5"]["body"] == "note about optimizers"
    store.save("3.5", hints_used=5)  # a write after the renumbering lands on the right lesson
    assert store.all()["3.5"]["code"] == "optimizers" and store.all()["3.6"]["hints_used"] == 2


def test_a_live_provider_follows_a_renumbering_without_a_restart():
    table = dict(MAPPING)
    store = ProgressStore(None, lesson_keys=lambda: table)
    store.save("3.5", code="ansatz")
    table.update(SWAPPED)
    assert store.all()["3.6"]["code"] == "ansatz"


# -- export and import -------------------------------------------------------------------------------


def fresh(mapping):
    return EngineServer(None, ProgressStore(None, lesson_keys=mapping), pool=None, token="t")


def test_export_wipe_import_round_trips():
    source = ProgressStore(None, lesson_keys=MAPPING)
    source.save("3.5", code="ansatz", completed=True, hints_used=1)
    source.save("3.5:challenge", code="c")
    source.save("sandbox", code="lab")
    source.note_save("lesson:3.5", "note")
    source.note_save("general", "free")
    backup = source.export_backup()
    assert backup["format"] == "qlp-progress" and backup["version"] == 2
    assert set(backup["progress"]) == {"3.5", "3.5:challenge", "sandbox"}  # lesson ids, as before
    assert backup["keys"] == {"3.5": "ansatz_design"}
    target = ProgressStore(None, lesson_keys=MAPPING)
    target.import_backup(json.loads(json.dumps(backup)))
    assert target.all()["3.5"]["code"] == "ansatz" and target.all()["3.5"]["completed"]
    assert target.all()["3.5:challenge"]["code"] == "c" and target.all()["sandbox"]["code"] == "lab"
    assert target.notes_all()["lesson:3.5"]["body"] == "note" and target.notes_all()["general"]["body"] == "free"


def test_import_after_a_renumbering_lands_on_the_right_lesson():
    source = ProgressStore(None, lesson_keys=MAPPING)
    source.save("3.5", code="ansatz", completed=True)
    source.save("3.5:challenge", code="challenge")
    source.note_save("lesson:3.5", "ansatz note")
    backup = source.export_backup()  # written before the swap
    target = ProgressStore(None, lesson_keys=SWAPPED)
    target.import_backup(backup)
    assert target.all()["3.6"]["code"] == "ansatz" and "3.5" not in target.all()
    assert target.all()["3.6:challenge"]["code"] == "challenge"
    assert set(target.notes_all()) == {"lesson:3.6"}


def test_old_backups_without_keys_and_unknown_ids_are_kept_under_their_id():
    target = ProgressStore(None, lesson_keys=MAPPING)
    entry = {"code": "c", "completed": True, "hints_used": 0, "attempts": 0, "solution_seen": False, "with_solution": False}
    target.import_backup({"format": "qlp-progress", "version": 2, "progress": {"1.1": entry, "9.9": entry, "9.9:challenge": entry},
                          "notes": {"lesson:9.9": {"body": "gone lesson"}}})
    assert set(target.all()) == {"1.1", "9.9", "9.9:challenge"}
    assert target.notes_all()["lesson:9.9"]["body"] == "gone lesson"
    # a key the library does not know any more: the entry stays under the id the file gave it
    target.import_backup({"format": "qlp-progress", "version": 2, "progress": {"2.2": entry}, "keys": {"2.2": "retired_lesson"}})
    assert "2.2" in target.all()


def test_a_malformed_keys_table_is_refused():
    target = ProgressStore(None, lesson_keys=MAPPING)
    with pytest.raises(ProgressError):
        target.import_backup({"format": "qlp-progress", "progress": {}, "keys": ["x"]})


def test_the_export_request_and_hosted_mode(library):
    engine = EngineServer(library, ProgressStore(None), pool=None, token="t")
    engine.progress.save("1.1", code="hi", completed=True)
    reply = ask(engine, type="progress.export")
    assert reply["ok"] and reply["backup"]["progress"]["1.1"]["code"] == "hi" and reply["backup"]["keys"]["1.1"] == "qubit"
    hosted = EngineServer(library, None, pool=None, token="t", public=True, allowed_origins=("https://x.example",))
    assert ask(hosted, type="progress.export")["ok"] is False


def test_catalog_sections_carry_their_key(library):
    engine = EngineServer(library, ProgressStore(None), pool=None, token="t")
    sections = [s for track in ask(engine, type="catalog")["catalog"]["tracks"] for s in track["sections"]]
    assert next(s for s in sections if s["id"] == "1.5")["key"] == "bell_states"


def test_protocol_through_the_server_keeps_ids_while_the_database_has_keys(library):
    engine = EngineServer(library, ProgressStore(None), pool=None, token="t")
    ask(engine, type="progress.save", lesson_id="1.5", code="x", completed=True)
    ask(engine, type="notes.save", key="lesson:1.5", body="hello")
    assert set(ask(engine, type="catalog")["progress"]) == {"1.5"}
    assert set(ask(engine, type="notes.list")["notes"]) == {"lesson:1.5"}
    rows = {row[0] for row in engine.progress._db.execute("SELECT lesson_id FROM progress")}
    assert rows == {"bell_states"}
