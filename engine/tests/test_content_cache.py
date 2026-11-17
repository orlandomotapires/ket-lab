"""Lesson files are cached by modification time; a lesson author's edit shows up without a restart."""

import json
import os
import shutil

import pytest

from qlp_engine.content import ContentLibrary


@pytest.fixture()
def copy(tmp_path, library):
    root = tmp_path / "content"
    root.mkdir()
    for name in ("catalog.json", "glossary.json", "sources.json", "lesson_keys.json"):
        if (library.root / name).exists():
            shutil.copy(library.root / name, root / name)
    for lesson_id in ("1.1", "1.2"):
        folder = library._lessons[lesson_id]
        target = root / folder.parent.name / folder.name
        shutil.copytree(folder, target)
    lib = ContentLibrary(root)
    lib.rescan_interval = 0
    return lib, root


def bump(path):
    stat = path.stat()
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 5_000_000))


def test_second_read_is_served_from_the_cache(copy, monkeypatch):
    lib, _ = copy
    lib.timeout("1.1"), lib.run_context("1.1"), lib.control_inputs("1.1", None), lib.catalog()
    calls = []
    from qlp_engine import content

    real = content._read_json
    monkeypatch.setattr(content, "_read_json", lambda path: calls.append(path) or real(path))
    lib.timeout("1.1"), lib.run_context("1.1"), lib.control_inputs("1.1", None), lib.catalog()
    assert calls == []


def test_an_edited_text_shows_up_at_once(copy):
    lib, root = copy
    folder = lib._lessons["1.1"]
    assert lib.lesson("1.1")["title"] != "Edited"
    text = json.loads((folder / "text.json").read_text(encoding="utf-8"))
    text["title"] = "Edited"
    (folder / "text.json").write_text(json.dumps(text), encoding="utf-8")
    bump(folder / "text.json")
    assert lib.lesson("1.1")["title"] == "Edited"


def test_manifest_edit_changes_timeout(copy):
    lib, _ = copy
    folder = lib._lessons["1.1"]
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    manifest["timeout"] = 17
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    bump(folder / "manifest.json")
    assert lib.timeout("1.1") == 17.0


def test_search_index_follows_edits(copy):
    lib, _ = copy
    folder = lib._lessons["1.1"]
    assert lib.search("zzyzxword") == []
    (folder / "theory.md").write_text(
        (folder / "theory.md").read_text(encoding="utf-8") + "\nThe zzyzxword appears here.\n", encoding="utf-8"
    )
    bump(folder / "theory.md")
    assert [hit["id"] for hit in lib.search("zzyzxword")] == ["1.1"]
    assert lib.search("zzyzxword")[0]["snippet"]


def test_new_removed_and_renumbered_lessons(copy):
    lib, root = copy
    first = lib._lessons["1.2"]
    manifest = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
    manifest["id"] = "1.9"
    (first / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    bump(first / "manifest.json")
    assert "1.9" in lib.lesson_ids and "1.2" not in lib.lesson_ids
    shutil.rmtree(first)
    assert lib.lesson_ids == ["1.1"]


def test_a_broken_manifest_keeps_the_last_good_index(copy):
    lib, _ = copy
    folder = lib._lessons["1.2"]
    (folder / "manifest.json").write_text("{ not json", encoding="utf-8")
    bump(folder / "manifest.json")
    assert set(lib.lesson_ids) == {"1.1", "1.2"}  # still served while the author finishes the edit
