"""P2.8 progress.import and P2.5 notes (engine side)."""

import asyncio
import json

import pytest

from ket_lab_engine.progress import ProgressStore
from ket_lab_engine.server import EngineServer


class FakeSocket:
    def __init__(self):
        self.sent = []

    async def send(self, text):
        self.sent.append(json.loads(text))


def ask(engine, **message):
    socket = FakeSocket()
    asyncio.run(engine._handle_message(socket, json.dumps({"id": 1, **message}), {"seq": 0}))
    return socket.sent[0]


@pytest.fixture()
def engine(library):
    return EngineServer(library, ProgressStore(None), pool=None, token="t")


@pytest.fixture()
def hosted(library):
    return EngineServer(library, None, pool=None, token="t", public=True, allowed_origins=("https://x.example",))


def backup(progress=None, notes=None, version=2):
    data = {"format": "ket-lab-progress", "version": version, "progress": progress or {}}
    if notes is not None:
        data["notes"] = notes
    return data


def entry(**fields):
    return {"code": None, "completed": False, "hints_used": 0, "attempts": 0, "solution_seen": False,
            "with_solution": False, **fields}


# -- progress.import -----------------------------------------------------------------------------


def test_import_restores_into_an_empty_database_and_replies_like_catalog(engine):
    data = backup({"1.1": entry(code="qc", completed=True, hints_used=2, attempts=3),
                   "1.2:challenge": entry(solution_seen=True, with_solution=True, completed=True)})
    reply = ask(engine, type="progress.import", data=data)
    assert reply["ok"] and reply["imported"] == {"lessons": 2, "notes": 0}
    one = reply["progress"]["1.1"]
    assert one["completed"] and one["code"] == "qc" and one["hints_used"] == 2 and one["attempts"] == 3
    assert reply["progress"]["1.2:challenge"]["with_solution"] is True
    assert reply["progress"] == ask(engine, type="catalog")["progress"]
    assert set(reply["progress"]["1.1"]) == set(engine.progress.all()["1.1"])


def test_import_merge_rules(engine):
    store = engine.progress
    store.save("1.1", code="mine", completed=True, hints_used=3)
    store.save("1.2", code="draft", hints_used=1)
    store.save("1.3", code="seen", solution_seen=True)
    data = backup({
        "1.1": entry(code=None, completed=False, hints_used=1, with_solution=True),
        "1.2": entry(code="theirs", completed=True, hints_used=5, attempts=2),
        "1.3": entry(solution_seen=True, completed=True, with_solution=False),
        "1.4": entry(code="new", solution_seen=True, completed=True, with_solution=False),
    })
    progress = ask(engine, type="progress.import", data=data)["progress"]
    assert progress["1.1"]["code"] == "mine" and progress["1.1"]["hints_used"] == 3  # completed stays, larger hints
    assert progress["1.1"]["with_solution"] is False  # kept as it was here
    assert progress["1.2"]["completed"] and progress["1.2"]["code"] == "theirs" and progress["1.2"]["hints_used"] == 5
    assert progress["1.2"]["attempts"] == 2
    assert progress["1.3"]["completed"] and progress["1.3"]["solution_seen"]
    assert progress["1.4"]["solution_seen"] and progress["1.4"]["with_solution"] is False
    # importing the same file again changes nothing
    assert ask(engine, type="progress.import", data=data)["progress"] == progress


def test_import_does_not_replace_a_passing_code_with_an_unfinished_one(engine):
    engine.progress.save("1.1", code="passing", completed=True)
    reply = ask(engine, type="progress.import", data=backup({"1.1": entry(code="half done")}))
    assert reply["progress"]["1.1"]["code"] == "passing"


def test_import_keeps_newer_code_when_the_file_has_a_timestamp(engine):
    engine.progress.save("1.1", code="recent")
    old = entry(code="old")
    old["updated_at"] = 1.0
    assert ask(engine, type="progress.import", data=backup({"1.1": old}))["progress"]["1.1"]["code"] == "recent"


def test_import_old_file_renames_the_track_3_project(engine):
    data = backup({"3.5": entry(code="p", completed=True), "3.5:challenge": entry(completed=True)}, version=1)
    progress = ask(engine, type="progress.import", data=data)["progress"]
    assert set(progress) == {"3.9", "3.9:challenge"}


def test_import_accepts_the_file_as_text_too(engine):
    reply = ask(engine, type="progress.import", data=json.dumps(backup({"1.1": entry(completed=True)})))
    assert reply["ok"] and reply["progress"]["1.1"]["completed"]


@pytest.mark.parametrize(
    "data",
    [
        {"format": "other", "progress": {}},
        {"format": "ket-lab-progress", "progress": []},
        {"format": "ket-lab-progress", "progress": {"1.1": "x"}},
        {"format": "ket-lab-progress", "progress": {"1.1": {"code": 5}}},
        {"format": "ket-lab-progress", "progress": {}, "notes": {"bad key": {"body": "x"}}},
        {"format": "ket-lab-progress", "progress": {}, "notes": {"general": {"body": 5}}},
        [1],
        "not json at all",
        None,
    ],
)
def test_import_of_a_malformed_file_is_a_protocol_error_and_writes_nothing(engine, data):
    engine.progress.save("9.9", code="x")
    reply = ask(engine, type="progress.import", data=data)
    assert reply["ok"] is False and reply["error"]["kind"] == "protocol"
    assert set(engine.progress.all()) == {"9.9"} and engine.progress.notes_all() == {}


def test_a_bad_entry_after_good_ones_rolls_everything_back(engine):
    data = backup({"1.1": entry(completed=True)})
    data["notes"] = {"general": {"body": "ok"}, "lesson:1.1": {"body": 3}}
    assert ask(engine, type="progress.import", data=data)["ok"] is False
    assert engine.progress.all() == {} and engine.progress.notes_all() == {}


def test_import_is_refused_in_hosted_mode(hosted):
    reply = ask(hosted, type="progress.import", data=backup())
    assert reply["ok"] is False and reply["error"]["kind"] == "unavailable"


# -- notes ----------------------------------------------------------------------------------------


def test_notes_save_list_delete(engine):
    assert ask(engine, type="notes.list") == {"ok": True, "notes": {}, "id": 1}
    saved = ask(engine, type="notes.save", key="lesson:1.1", body="Hadamard makes |+>")
    assert saved["ok"] and saved["note"]["body"] == "Hadamard makes |+>"
    assert saved["note"]["updated_at"].endswith("Z")
    ask(engine, type="notes.save", key="general", body="free note")
    listed = ask(engine, type="notes.list")["notes"]
    assert set(listed) == {"lesson:1.1", "general"} and listed["general"]["body"] == "free note"
    assert ask(engine, type="notes.delete", key="general")["ok"]
    assert set(ask(engine, type="notes.list")["notes"]) == {"lesson:1.1"}
    assert ask(engine, type="notes.delete", key="general")["ok"]  # deleting nothing is fine


@pytest.mark.parametrize("body", ["", "   \n\t "])
def test_blank_body_deletes_the_note(engine, body):
    ask(engine, type="notes.save", key="general", body="x")
    reply = ask(engine, type="notes.save", key="general", body=body)
    assert reply["ok"] and reply["note"] is None
    assert ask(engine, type="notes.list")["notes"] == {}


@pytest.mark.parametrize("key", ["", "other", "lesson:", "lesson:a b", "lesson:../x", "General", "lesson:" + "x" * 80, 5, None])
def test_malformed_note_keys_are_rejected(engine, key):
    for kind, extra in (("notes.save", {"body": "x"}), ("notes.delete", {})):
        reply = ask(engine, type=kind, key=key, **extra)
        assert reply["ok"] is False and reply["error"]["kind"] == "protocol", (kind, key)
    assert engine.progress.notes_all() == {}


def test_note_size_cap_is_64_kb(engine):
    assert ask(engine, type="notes.save", key="general", body="a" * 65536)["ok"]
    reply = ask(engine, type="notes.save", key="general", body="a" * 65537)
    assert reply["ok"] is False and reply["error"]["kind"] == "protocol" and "64 KB" in reply["error"]["message"]
    assert len(engine.progress.notes_all()["general"]["body"]) == 65536
    assert ask(engine, type="notes.save", key="general", body=5)["ok"] is False


def test_notes_are_unavailable_in_hosted_mode(hosted):
    for kind in ("notes.list", "notes.save", "notes.delete"):
        reply = ask(hosted, type=kind, key="general", body="x")
        assert reply["ok"] is False and reply["error"]["kind"] == "unavailable"


def test_catalog_says_where_notes_live(engine, hosted):
    assert ask(engine, type="catalog")["notes_storage"] == "engine"
    reply = ask(hosted, type="catalog")
    assert reply["notes_storage"] == "client" and reply["progress_storage"] == "client"


def test_notes_survive_a_restart(tmp_path):
    store = ProgressStore(tmp_path)
    store.note_save("lesson:2.1", "kept")
    store.close()
    assert ProgressStore(tmp_path).notes_all()["lesson:2.1"]["body"] == "kept"


# -- importing notes ---------------------------------------------------------------------------------


def test_import_notes_new_same_and_different(engine):
    store = engine.progress
    store.note_save("lesson:1.1", "my text")
    store.note_save("general", "same")
    notes = {
        "lesson:1.1": {"body": "their text", "updated_at": "2026-01-01T00:00:00Z"},
        "general": {"body": "same", "updated_at": "2026-01-01T00:00:00Z"},
        "lesson:1.2": {"body": "only there", "updated_at": "2026-01-02T00:00:00Z"},
        "lesson:1.3": {"body": "   ", "updated_at": "2026-01-02T00:00:00Z"},
    }
    reply = ask(engine, type="progress.import", data=backup(notes=notes))
    assert reply["imported"]["notes"] == 2
    merged = reply["notes"]
    assert merged["lesson:1.1"]["body"] == "my text\n\n--- imported ---\ntheir text"
    assert merged["general"]["body"] == "same"
    assert merged["lesson:1.2"] == {"body": "only there", "updated_at": "2026-01-02T00:00:00Z"}
    assert "lesson:1.3" not in merged
    # the same file twice must not append the text again
    again = ask(engine, type="progress.import", data=backup(notes=notes))
    assert again["notes"]["lesson:1.1"]["body"] == merged["lesson:1.1"]["body"]
    assert again["imported"]["notes"] == 0


def test_import_notes_of_an_old_file_follow_the_renumbering(engine):
    data = backup(notes={"lesson:3.5": {"body": "project"}}, version=1)
    assert "lesson:3.9" in ask(engine, type="progress.import", data=data)["notes"]


def test_note_key_of_a_renumbered_lesson_is_renamed(tmp_path):
    store = ProgressStore(tmp_path)
    store.note_save("lesson:7.1", "x")
    store.save("7.1:challenge", code="c")
    store._rename_lesson("7.1", "7.2")
    assert list(store.notes_all()) == ["lesson:7.2"] and set(store.all()) == {"7.2:challenge"}


# -- search ------------------------------------------------------------------------------------------


def test_search_also_returns_matching_notes(engine):
    engine.progress.note_save("lesson:1.1", "Remember: the Hadamard gate is its own inverse.")
    engine.progress.note_save("general", "Ideas about entanglement for later")
    reply = ask(engine, type="search", query="hadamard")
    assert reply["results"] and "notes" in reply  # lessons unchanged
    assert [n["key"] for n in reply["notes"]] == ["lesson:1.1"]
    hit = reply["notes"][0]
    assert hit["lesson_id"] == "1.1" and hit["title"] and "Hadamard" in hit["snippet"] and hit["updated_at"]
    general = ask(engine, type="search", query="ENTANGLEMENT later")["notes"]
    assert general[0]["key"] == "general" and general[0]["lesson_id"] is None and general[0]["title"] is None
    assert ask(engine, type="search", query="zzzxxy")["notes"] == []


def test_search_notes_empty_in_hosted_mode(hosted):
    reply = ask(hosted, type="search", query="hadamard")
    assert reply["ok"] and reply["notes"] == [] and reply["results"]


def test_default_data_dir_moves_the_folder_from_before_the_rename(tmp_path, monkeypatch):
    from ket_lab_engine import progress

    monkeypatch.setattr(progress.sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    legacy = tmp_path / "quantum-learning-platform"
    legacy.mkdir()
    (legacy / "progress.sqlite3").write_text("saved")
    target = progress.default_data_dir()
    assert target == tmp_path / "ket-lab"
    assert (target / "progress.sqlite3").read_text() == "saved"
    assert not legacy.exists()
    # Once moved, a later start uses the new folder and leaves it alone.
    assert progress.default_data_dir() == target


def test_default_data_dir_without_an_old_folder(tmp_path, monkeypatch):
    from ket_lab_engine import progress

    monkeypatch.setattr(progress.sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    assert progress.default_data_dir() == tmp_path / "ket-lab"
    assert not (tmp_path / "ket-lab").exists()  # created by ProgressStore, not here
