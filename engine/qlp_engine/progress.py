"""Progresso do aluno em SQLite (biblioteca padrão), guardado no diretório de dados."""

from __future__ import annotations

import os
import sqlite3
import sys
import time
from pathlib import Path

APP_DIR_NAME = "quantum-learning-platform"


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
    def __init__(self, data_dir: Path | None):
        """`data_dir=None` usa um banco em memória (testes)."""
        if data_dir is None:
            target = ":memory:"
        else:
            data_dir.mkdir(parents=True, exist_ok=True)
            target = str(data_dir / "progress.sqlite3")
        self._db = sqlite3.connect(target)
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
        self._db.commit()

    def all(self) -> dict[str, dict]:
        rows = self._db.execute(
            "SELECT lesson_id, code, completed_at, hints_used FROM progress"
        ).fetchall()
        return {
            lesson_id: {
                "code": code,
                "completed": completed_at is not None,
                "completed_at": completed_at,
                "hints_used": hints_used,
            }
            for lesson_id, code, completed_at, hints_used in rows
        }

    def save(
        self,
        lesson_id: str,
        code: str | None = None,
        completed: bool | None = None,
        hints_used: int | None = None,
    ) -> None:
        now = time.time()
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
        self._db.execute("UPDATE progress SET updated_at = ? WHERE lesson_id = ?", (now, lesson_id))
        self._db.commit()

    def close(self) -> None:
        self._db.close()
