"""Student progress in SQLite (standard library), stored in the data directory."""

from __future__ import annotations

import logging
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import messages

# Kept from the project's first name, so existing progress is still found after the rename to Ket Lab.
APP_DIR_NAME = "quantum-learning-platform"
BACKUPS_KEPT = 5
BUSY_TIMEOUT_MS = 5000
MAX_NOTE_BYTES = 64 * 1024
MAX_CODE_CHARS = 100_000
MAX_IMPORT_ENTRIES = 1000
# "general" for the free note; "lesson:<lesson id>" for a lesson note.
NOTE_KEY = re.compile(r"^(general|lesson:[A-Za-z0-9][A-Za-z0-9._-]{0,63})$")
BACKUP_VERSION = 2
BACKUP_FILE = re.compile(r"^progress-(\d{8})\.sqlite3$")

IMPORT_MARKER = "--- imported ---"

log = logging.getLogger("qlp_engine")


class KeyMap:
    """Translates between lesson ids ("3.5") and stable lesson keys ("ansatz_design").

    The protocol and the interface speak lesson ids; the database stores keys, so a lesson
    renumbered in the catalog keeps its progress and notes without any migration. Anything that is
    not a lesson ("sandbox", "general", "review:3", ids this library does not know) passes through
    unchanged, and so do the suffix ":challenge" and the prefix "lesson:" of note keys.
    """

    def __init__(self, ids_to_keys: dict[str, str] | None = None):
        self.by_id = dict(ids_to_keys or {})
        self.by_key = {key: lesson_id for lesson_id, key in self.by_id.items()}

    @staticmethod
    def _translate(name: str, table: dict[str, str]) -> str:
        base, suffix = (name[: -len(CHALLENGE)], CHALLENGE) if name.endswith(CHALLENGE) else (name, "")
        return table[base] + suffix if base in table else name

    def to_key(self, progress_key: str) -> str:
        return self._translate(progress_key, self.by_id)

    def to_id(self, stored_key: str) -> str:
        return self._translate(stored_key, self.by_key)

    def note_to_key(self, note_key: str) -> str:
        return "lesson:" + self.to_key(note_key[7:]) if note_key.startswith("lesson:") else note_key

    def note_to_id(self, stored_key: str) -> str:
        return "lesson:" + self.to_id(stored_key[7:]) if stored_key.startswith("lesson:") else stored_key


CHALLENGE = ":challenge"
KEYS_VERSION = 4  # PRAGMA user_version after rows were rewritten from lesson ids to stable keys


class ProgressError(ValueError):
    """A request the store refuses (bad key, note too long, malformed backup). The message is for the learner."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_data_dir() -> Path:
    home = Path.home()
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = home / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
    return base / APP_DIR_NAME


class ProgressStore:
    def __init__(self, data_dir: Path | None, lesson_keys=None):
        """`data_dir=None` uses an in-memory database (tests).

        `lesson_keys` (a dict id -> key, or a function returning one, such as
        `ContentLibrary.lesson_keys`) makes the store keep lessons under their stable keys.
        """
        self._provider = None
        self._keymap = KeyMap()
        if data_dir is None:
            target = ":memory:"
        else:
            data_dir.mkdir(parents=True, exist_ok=True)
            target = str(data_dir / "progress.sqlite3")
        self._db = sqlite3.connect(target, timeout=BUSY_TIMEOUT_MS / 1000)
        self._db.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
        if data_dir is not None:
            self._db.execute("PRAGMA journal_mode = WAL")
            self._backup(data_dir)  # before any migration touches the file
        self._migrate()
        self._db.commit()
        if lesson_keys is not None:
            self.use_keys(lesson_keys)

    # -- stable lesson keys ------------------------------------------------ #

    def use_keys(self, lesson_keys) -> None:
        """Starts keeping lessons under stable keys; rewrites older rows (ids) once, at the first use.

        The dated daily backup (taken when the store opened) still has the old ids.
        """
        self._provider = lesson_keys if callable(lesson_keys) else (lambda: lesson_keys)
        keymap = self.keys
        version = self._db.execute("PRAGMA user_version").fetchone()[0]
        if version < KEYS_VERSION:
            try:
                for lesson_id, key in keymap.by_id.items():
                    self._rename_lesson(lesson_id, key)
                self._db.execute(f"PRAGMA user_version = {KEYS_VERSION}")
                self._db.commit()
            except BaseException:
                self._db.rollback()
                raise

    @property
    def keys(self) -> KeyMap:
        """The current id <-> key table (rebuilt only when the content library hands over a new one)."""
        if self._provider is None:
            return self._keymap
        table = self._provider()
        if table is not self._keymap.by_id and table != self._keymap.by_id:
            self._keymap = KeyMap(table)
        return self._keymap

    # -- backup and schema ------------------------------------------------ #

    def _backup(self, data_dir: Path) -> None:
        """One dated copy per day (progress-YYYYMMDD.sqlite3), the last BACKUPS_KEPT kept."""
        try:
            has_data = self._db.execute("SELECT 1 FROM sqlite_master WHERE name = 'progress'").fetchone()
            if not has_data:
                return  # a new database has nothing to protect
            today = datetime.now().strftime("%Y%m%d")
            target = data_dir / f"progress-{today}.sqlite3"
            if not target.exists():
                partial = data_dir / f"progress-{today}.sqlite3.part"
                copy = sqlite3.connect(partial)
                try:
                    self._db.backup(copy)
                finally:
                    copy.close()
                partial.replace(target)
            backups = sorted(path for path in data_dir.iterdir() if BACKUP_FILE.match(path.name))
            for old in backups[:-BACKUPS_KEPT]:
                old.unlink()
        except (OSError, sqlite3.Error):
            log.exception("could not back up the progress database")  # a failed backup must not stop the engine

    def _migrate(self) -> None:
        """Schema and lesson renumberings; PRAGMA user_version stores the last step applied."""
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                lesson_id    TEXT PRIMARY KEY,
                code         TEXT,
                completed_at REAL,
                hints_used   INTEGER NOT NULL DEFAULT 0,
                updated_at   REAL NOT NULL
            )
            """
        )
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS notes (key TEXT PRIMARY KEY, body TEXT NOT NULL, updated_at TEXT NOT NULL)"
        )
        version = self._db.execute("PRAGMA user_version").fetchone()[0]
        if version < 1:
            # Roadmap phase 2: Simon enters as 2.5 and Track 3 splits (3.5 and 3.6 become 4.1 and 4.2).
            # Descending order to avoid collisions (2.8 -> 2.9 before 2.7 -> 2.8).
            for old, new in (("2.8", "2.9"), ("2.7", "2.8"), ("2.6", "2.7"), ("2.5", "2.6"), ("3.6", "4.2"), ("3.5", "4.1")):
                self._rename_lesson(old, new)
        columns = {row[1] for row in self._db.execute("PRAGMA table_info(progress)")}
        # P2.1: unsuccessful Check attempts and the moment the solution was viewed.
        if "attempts" not in columns:
            self._db.execute("ALTER TABLE progress ADD COLUMN attempts INTEGER NOT NULL DEFAULT 0")
        if "solution_seen_at" not in columns:
            self._db.execute("ALTER TABLE progress ADD COLUMN solution_seen_at REAL")
        if version < 2:
            # P3.2: Track 3 gains lessons 3.5 to 3.8; the project moves from 3.5 to 3.9.
            self._rename_lesson("3.5", "3.9")
        # Step 3 (P2.5): the notes table, created above. Every future renumbering goes through
        # _rename_lesson, which moves the challenge progress and the lesson note with the lesson.
        if version < 3:
            self._db.execute("PRAGMA user_version = 3")

    def _rename_lesson(self, old: str, new: str) -> None:
        """Renames a lesson id everywhere it is a key: progress, its challenge, and its note.

        A target that already exists is left alone (nothing is overwritten or lost).
        """
        for suffix in ("", ":challenge"):
            exists = self._db.execute("SELECT 1 FROM progress WHERE lesson_id = ?", (new + suffix,)).fetchone()
            if not exists:
                self._db.execute("UPDATE progress SET lesson_id = ? WHERE lesson_id = ?", (new + suffix, old + suffix))
        exists = self._db.execute("SELECT 1 FROM notes WHERE key = ?", (f"lesson:{new}",)).fetchone()
        if not exists:
            self._db.execute("UPDATE notes SET key = ? WHERE key = ?", (f"lesson:{new}", f"lesson:{old}"))

    # -- progress ---------------------------------------------------------- #

    def all(self) -> dict[str, dict]:
        rows = self._db.execute(
            "SELECT lesson_id, code, completed_at, hints_used, attempts, solution_seen_at FROM progress"
        ).fetchall()
        keys = self.keys
        return {
            keys.to_id(lesson_id): {
                "code": code,
                "completed": completed_at is not None,
                "completed_at": completed_at,
                "hints_used": hints_used,
                "attempts": attempts,
                "solution_seen": seen_at is not None,
                # Completed after viewing the solution: the hub shows "completed with solution".
                "with_solution": seen_at is not None and completed_at is not None and seen_at <= completed_at,
            }
            for lesson_id, code, completed_at, hints_used, attempts, seen_at in rows
        }

    def save(
        self,
        lesson_id: str,
        code: str | None = None,
        completed: bool | None = None,
        hints_used: int | None = None,
        *,
        failed_attempt: bool = False,
        solution_seen: bool = False,
    ) -> None:
        now = time.time()
        lesson_id = self.keys.to_key(lesson_id)
        self._db.execute(
            "INSERT OR IGNORE INTO progress (lesson_id, updated_at) VALUES (?, ?)",
            (lesson_id, now),
        )
        if code is not None:
            self._db.execute("UPDATE progress SET code = ? WHERE lesson_id = ?", (code, lesson_id))
        if completed:
            self._db.execute(
                "UPDATE progress SET completed_at = COALESCE(completed_at, ?) WHERE lesson_id = ?",
                (now, lesson_id),
            )
        if hints_used is not None:
            self._db.execute(
                "UPDATE progress SET hints_used = MAX(hints_used, ?) WHERE lesson_id = ?",
                (int(hints_used), lesson_id),
            )
        if failed_attempt:
            self._db.execute("UPDATE progress SET attempts = attempts + 1 WHERE lesson_id = ?", (lesson_id,))
        if solution_seen:
            self._db.execute(
                "UPDATE progress SET solution_seen_at = COALESCE(solution_seen_at, ?) WHERE lesson_id = ?",
                (now, lesson_id),
            )
        self._db.execute("UPDATE progress SET updated_at = ? WHERE lesson_id = ?", (now, lesson_id))
        self._db.commit()

    # -- restoring a backup -------------------------------------------------- #

    def import_backup(self, data: object) -> dict:
        """Merges a progress export (the file the interface writes) into the database.

        Rules, per lesson: completed wins; hints and attempts keep the larger value; the
        solution stays "seen"; "completed with the solution" is kept as it already is when the
        lesson was completed here, and taken from the file otherwise; the code in the file is
        used when it is not empty, unless this database already has a completed lesson and the
        file has none, or both sides carry an `updated_at` and ours is newer.
        Notes (optional `notes` object) are merged by `merge_notes`: nothing is overwritten.
        Raises ProgressError, writing nothing, when the file is malformed.
        """
        entries, notes, file_keys = _read_backup(data)
        entries, notes = self._land_on_current_ids(entries, notes, file_keys)
        now = time.time()
        try:
            for lesson_id, entry in entries.items():
                self._merge_lesson(self.keys.to_key(lesson_id), entry, now)
            merged_notes = self._merge_notes(notes)
            self._db.commit()
        except BaseException:
            self._db.rollback()
            raise
        return {"lessons": len(entries), "notes": merged_notes}

    def _land_on_current_ids(self, entries: dict, notes: dict, file_keys: dict[str, str]):
        """Points each lesson of a file at the lesson that carries its stable key today.

        A file written before a renumbering says "3.5 -> ansatz_design"; if ansatz_design is 3.6
        now, the entry lands on 3.6. Ids without a key in the file, or whose key this library does
        not know, stay where they are (an unknown lesson is kept under its id, never dropped).
        """
        current = self.keys.by_key

        def resolve(name: str, prefix: str = "") -> str:
            body = name[len(prefix):]
            base, suffix = (body[: -len(CHALLENGE)], CHALLENGE) if body.endswith(CHALLENGE) else (body, "")
            target = current.get(file_keys.get(base, ""))
            return prefix + target + suffix if target else name

        moved: dict[str, dict] = {}
        for lesson_id, entry in entries.items():
            moved.setdefault(resolve(lesson_id), entry)
        moved_notes: dict[str, dict] = {}
        for key, note in notes.items():
            moved_notes.setdefault(resolve(key, "lesson:") if key.startswith("lesson:") else key, note)
        return moved, moved_notes

    def export_backup(self) -> dict:
        """The progress file the interface offers to save: lesson ids as always, plus the stable keys."""
        keys = self.keys
        progress = {}
        for stored, code, completed_at, hints, attempts, seen_at, updated in self._db.execute(
            "SELECT lesson_id, code, completed_at, hints_used, attempts, solution_seen_at, updated_at FROM progress"
        ):
            progress[keys.to_id(stored)] = {
                "code": code,
                "completed": completed_at is not None,
                "completed_at": completed_at,
                "hints_used": hints,
                "attempts": attempts,
                "solution_seen": seen_at is not None,
                "with_solution": seen_at is not None and completed_at is not None and seen_at <= completed_at,
                "updated_at": updated,
            }
        notes = self.notes_all()
        named = {name for name in progress} | {name[7:] for name in notes if name.startswith("lesson:")}
        named = {name[: -len(CHALLENGE)] if name.endswith(CHALLENGE) else name for name in named}
        return {
            "format": "qlp-progress",
            "version": BACKUP_VERSION,
            "progress": progress,
            "notes": notes,
            "keys": {lesson_id: keys.by_id[lesson_id] for lesson_id in sorted(named) if lesson_id in keys.by_id},
        }

    def _merge_lesson(self, lesson_id: str, entry: dict, now: float) -> None:
        row = self._db.execute(
            "SELECT code, completed_at, hints_used, attempts, solution_seen_at, updated_at FROM progress WHERE lesson_id = ?",
            (lesson_id,),
        ).fetchone()
        code, completed_at, hints, attempts, seen_at, updated = row if row else (None, None, 0, 0, None, 0.0)
        incoming_code = entry["code"]
        if incoming_code:
            theirs = entry.get("updated_at")
            ours_is_newer = row is not None and code and theirs is not None and updated > theirs
            keeps_passing_code = completed_at is not None and not entry["completed"] and code
            if not ours_is_newer and not keeps_passing_code:
                code = incoming_code
        if entry["completed"] and completed_at is None:
            stamp = entry.get("completed_at") or now
            if entry["with_solution"]:
                completed_at, seen_at = stamp, stamp if seen_at is None else min(seen_at, stamp)
            elif entry["solution_seen"] or seen_at is not None:
                # Seen after finishing: the hub shows a plain "completed", not "with solution".
                completed_at = stamp - 1.0 if seen_at is None else min(stamp, seen_at - 1.0)
                seen_at = seen_at if seen_at is not None else stamp
            else:
                completed_at = stamp
        if entry["solution_seen"] and seen_at is None:
            seen_at = now
        self._db.execute(
            "INSERT INTO progress (lesson_id, code, completed_at, hints_used, attempts, solution_seen_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(lesson_id) DO UPDATE SET code = excluded.code, "
            "completed_at = excluded.completed_at, hints_used = excluded.hints_used, attempts = excluded.attempts, "
            "solution_seen_at = excluded.solution_seen_at, updated_at = excluded.updated_at",
            (lesson_id, code, completed_at, max(hints, entry["hints_used"]), max(attempts, entry["attempts"]), seen_at, now),
        )

    # -- notes ----------------------------------------------------------------- #

    def notes_all(self) -> dict[str, dict]:
        keys = self.keys
        return {keys.note_to_id(key): note for key, note in self._notes_stored().items()}

    def _notes_stored(self) -> dict[str, dict]:
        rows = self._db.execute("SELECT key, body, updated_at FROM notes").fetchall()
        return {key: {"body": body, "updated_at": updated_at} for key, body, updated_at in rows}

    def note_save(self, key: object, body: object) -> dict | None:
        """Saves a note; an empty (or blank) body deletes it. Returns the stored note or None."""
        key = self.keys.note_to_key(check_note_key(key))
        if not isinstance(body, str):
            raise ProgressError(messages.t("notes.bad_body"))
        if len(body.encode("utf-8")) > MAX_NOTE_BYTES:
            raise ProgressError(messages.t("notes.too_long", limit=MAX_NOTE_BYTES // 1024))
        if not body.strip():
            self.note_delete(key)
            return None
        note = {"body": body, "updated_at": _now_iso()}
        self._db.execute(
            "INSERT INTO notes (key, body, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET body = excluded.body, updated_at = excluded.updated_at",
            (key, body, note["updated_at"]),
        )
        self._db.commit()
        return note

    def note_delete(self, key: object) -> None:
        self._db.execute("DELETE FROM notes WHERE key = ?", (self.keys.note_to_key(check_note_key(key)),))
        self._db.commit()

    def _merge_notes(self, incoming: dict[str, dict]) -> int:
        """Never overwrites: a different text on both sides keeps both, the imported one after a marker."""
        changed = 0
        current = self._notes_stored()
        for key, note in incoming.items():
            key = self.keys.note_to_key(key)
            body = note["body"]
            if not body.strip():
                continue
            ours = current.get(key)
            if ours is None:
                merged, stamp = body, note.get("updated_at") or _now_iso()
            elif body.strip() in ours["body"]:
                continue  # already here (importing the same file twice must not duplicate it)
            else:
                merged = f"{ours['body'].rstrip()}\n\n{IMPORT_MARKER}\n{body}"
                stamp = _now_iso()
            self._db.execute(
                "INSERT INTO notes (key, body, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET body = excluded.body, updated_at = excluded.updated_at",
                (key, merged, stamp),
            )
            changed += 1
        return changed

    def close(self) -> None:
        self._db.close()


def check_note_key(key: object) -> str:
    if not isinstance(key, str) or not NOTE_KEY.match(key):
        raise ProgressError(messages.t("notes.bad_key"))
    return key


def _number(value: object, default: float | None = None) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return default
    return float(value)


def _count(value: object) -> int:
    number = _number(value, 0)
    return int(min(max(number, 0), 10_000))


def _rename_old_keys(entries: dict, pairs: list[tuple[str, str]], prefix: str = "") -> None:
    for old, new in pairs:
        for suffix in ("", ":challenge"):
            source, target = prefix + old + suffix, prefix + new + suffix
            if source in entries and target not in entries:
                entries[target] = entries[source]
            entries.pop(source, None)


def _read_backup(data: object) -> tuple[dict[str, dict], dict[str, dict], dict[str, str]]:
    """Validates a progress export and returns (lessons, notes, keys) in a normal form.

    `keys` is the optional id -> stable key table that newer files carry; old files have none.
    """
    bad = ProgressError(messages.t("import.bad_file"))
    if not isinstance(data, dict) or data.get("format") != "qlp-progress":
        raise bad
    raw, raw_notes = data.get("progress"), data.get("notes", {})
    if not isinstance(raw, dict) or not isinstance(raw_notes, dict):
        raise bad
    if len(raw) > MAX_IMPORT_ENTRIES or len(raw_notes) > MAX_IMPORT_ENTRIES:
        raise ProgressError(messages.t("import.too_big"))
    raw, raw_notes = dict(raw), dict(raw_notes)
    raw_keys = data.get("keys", {})
    if not isinstance(raw_keys, dict) or len(raw_keys) > MAX_IMPORT_ENTRIES * 2:
        raise bad
    file_keys = {
        lesson_id: key for lesson_id, key in raw_keys.items()
        if isinstance(lesson_id, str) and isinstance(key, str) and 0 < len(key) <= 80  # anything else is ignored
    }
    version = _number(data.get("version"), 1)
    if version < 2:  # same rule as the interface: Track 3 project 3.5 became 3.9
        _rename_old_keys(raw, [("3.5", "3.9")])
        _rename_old_keys(raw_notes, [("3.5", "3.9")], prefix="lesson:")
    entries: dict[str, dict] = {}
    for lesson_id, entry in raw.items():
        if not isinstance(lesson_id, str) or not 0 < len(lesson_id) <= 80 or not isinstance(entry, dict):
            raise bad
        code = entry.get("code")
        if code is not None and (not isinstance(code, str) or len(code) > MAX_CODE_CHARS):
            raise bad
        entries[lesson_id] = {
            "code": code,
            "completed": bool(entry.get("completed")),
            "completed_at": _number(entry.get("completed_at")),
            "hints_used": _count(entry.get("hints_used")),
            "attempts": _count(entry.get("attempts")),
            "solution_seen": bool(entry.get("solution_seen")),
            "with_solution": bool(entry.get("with_solution")),
            "updated_at": _number(entry.get("updated_at")),
        }
    notes: dict[str, dict] = {}
    for key, note in raw_notes.items():
        check_note_key(key)
        if not isinstance(note, dict) or not isinstance(note.get("body"), str):
            raise bad
        if len(note["body"].encode("utf-8")) > MAX_NOTE_BYTES * 4:
            raise ProgressError(messages.t("import.too_big"))
        stamp = note.get("updated_at")
        notes[key] = {"body": note["body"], "updated_at": stamp if isinstance(stamp, str) and len(stamp) <= 40 else None}
    return entries, notes, file_keys
