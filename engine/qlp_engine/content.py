"""Loads the catalog and the lessons from the /content folder.

Structure of a lesson:
    manifest.json        structure (visualizations, validation); no text
    text.json            title, summary, mission, prediction, hints
    theory.md            theory text
    starter_code.py      starter code
    solution.py          reference solution (defines the target)
    hidden_setup.py      optional: hidden setup, oracles

This module does not import Qiskit: it runs in the server process, which must
start fast. Everything that needs simulation happens in the worker.
"""

from __future__ import annotations

import json
import os
import re
import time
import unicodedata
from pathlib import Path

from .messages import t

REQUIRED_MANIFEST_KEYS = ("id", "track", "num_qubits", "validation")


class ContentError(Exception):
    pass


KEYS_FILE = "lesson_keys.json"
_FOLDER_SLUG = re.compile(r"^section_\d+_\d+_(.+)$")


class _FileCache:
    """Parsed files by modification time: an edit by a lesson author shows up on the next request."""

    def __init__(self):
        self._entries: dict[Path, tuple[tuple[int, int], object]] = {}

    def get(self, path: Path, load):
        try:
            info = os.stat(path)
        except FileNotFoundError:
            self._entries.pop(path, None)
            return load(path)  # raises the same friendly error as before
        stamp = (info.st_mtime_ns, info.st_size)
        hit = self._entries.get(path)
        if hit is not None and hit[0] == stamp:
            return hit[1]
        value = load(path)
        self._entries[path] = (stamp, value)
        return value

    @staticmethod
    def dir_stamp(path: Path) -> int | None:
        try:
            return path.stat().st_mtime_ns
        except FileNotFoundError:
            return None

    def stamp(self, path: Path) -> tuple[int, int] | None:
        try:
            info = path.stat()
        except FileNotFoundError:
            return None
        return (info.st_mtime_ns, info.st_size)


class ContentLibrary:
    # Seconds between looks at the folder layout (new, removed or renumbered lessons). File contents are
    # checked on every read, so an edited text shows up at once; tests that rename a lesson set this to 0.
    rescan_interval = 0.5

    def __init__(self, root: Path):
        self.root = Path(root)
        if not self.root.is_dir():
            raise ContentError(f"Content folder not found: {self.root}")
        self._files = _FileCache()
        self._lessons: dict[str, Path] = {}
        self._tracks: dict[int, Path] = {}
        self._scan_signature: tuple | None = None
        self._watched: list[str] = []
        self._scanned_at = 0.0
        self._search_index: dict[str, tuple[tuple, dict]] = {}
        self._keys_table: dict[str, str] = {}
        self._keys_signature: tuple | None = None
        self._scan(strict=True)

    # -- reading with a cache ------------------------------------------------ #

    def _json(self, path: Path) -> dict:
        return self._files.get(path, _read_json)

    def _text(self, path: Path) -> str:
        return self._files.get(path, _read_text)

    def _scan(self, strict: bool = False) -> None:
        """(Re)builds the lesson index when a manifest was added, removed or edited.

        One directory listing and one stat per manifest: cheaper than a request needs to notice.
        A manifest that is broken half-way through an edit keeps the previous index (only the
        first scan, at startup, is strict).
        """
        now = time.monotonic()
        if not strict and now - self._scanned_at < self.rescan_interval:
            return
        self._scanned_at = now
        if self._quick_signature() == self._scan_signature:
            return
        manifests = sorted(self.root.glob("track_*/*/manifest.json"))
        lessons: dict[str, Path] = {}
        tracks: dict[int, Path] = {}
        try:
            for manifest_path in manifests:
                manifest = self._json(manifest_path)
                missing = [key for key in REQUIRED_MANIFEST_KEYS if key not in manifest]
                if missing:
                    raise ContentError(f"{manifest_path}: missing fields {missing}")
                if manifest["id"] in lessons:
                    raise ContentError(f"Duplicate lesson id: {manifest['id']}")
                lessons[manifest["id"]] = manifest_path.parent
                tracks[int(manifest["track"])] = manifest_path.parent.parent
        except ContentError:
            if strict:
                raise
            return  # keep serving the last good index until the author finishes the edit
        self._lessons, self._tracks = lessons, tracks
        folders = {self.root, *tracks.values()}
        self._watched = [str(f / "manifest.json") for f in lessons.values()] + [str(f) for f in sorted(folders)]
        self._scan_signature = self._quick_signature()

    def _quick_signature(self) -> tuple:
        """Cheap fingerprint of the lesson layout: the known manifests and the folders that list them.

        A section folder added or removed changes its track folder's modification time; a track folder
        changes the content root's; an edited manifest changes its own stamp. About 60 stat calls.
        """
        stat = os.stat
        stamps = []
        for path in self._watched:
            try:
                info = stat(path)
                stamps.append((info.st_mtime_ns, info.st_size))
            except OSError:
                stamps.append(None)
        return tuple(stamps)

    @property
    def lesson_ids(self) -> list[str]:
        self._scan()
        return list(self._lessons)

    def lesson_keys(self) -> dict[str, str]:
        """Stable key of every lesson, by lesson id (content/lesson_keys.json).

        The database stores progress under these keys, so renumbering a lesson only means editing
        the catalog, the manifest's id and this file. A lesson missing from the file gets the name
        of its folder without the numbers (what the file was first generated from). The same
        dict object is returned until something changes.
        """
        self._scan()
        path = self.root / KEYS_FILE
        signature = (self._files.stamp(path), self._scan_signature, len(self._lessons))
        if signature != self._keys_signature:
            declared = self._json(path) if path.exists() else {}
            table = dict(declared) if isinstance(declared, dict) else {}
            for lesson_id, folder in self._lessons.items():
                if lesson_id not in table:
                    found = _FOLDER_SLUG.match(folder.name)
                    table[lesson_id] = found.group(1) if found else folder.name
            self._keys_table, self._keys_signature = table, signature
        return self._keys_table

    def catalog(self) -> dict:
        """Full curriculum; each section indicates whether it already has content."""
        self._scan()
        raw = self._json(self.root / "catalog.json")
        keys = self.lesson_keys()
        return {
            "tracks": [
                {
                    "id": track["id"],
                    "title": track["title"],
                    "level": track["level"],
                    "review": self._review_path(track["id"]) is not None,
                    "sections": [
                        {
                            "id": section["id"],
                            "title": section["title"],
                            "summary": section["summary"],
                            "available": section["id"] in self._lessons,
                            **({"key": keys[section["id"]]} if section["id"] in keys else {}),
                            **self._section_flags(section["id"]),
                        }
                        for section in track["sections"]
                    ],
                }
                for track in raw["tracks"]
            ]
        }

    def bibliography(self) -> dict:
        """All lesson references (without repetition, with the lessons that cite them),
        plus the course material and software used in development (content/sources.json).

        Books become a reading guide: each cited passage (section, title, pages), in
        book order, with the lessons that cite it. Papers are sorted by the first author's
        surname; course pages, in the order the curriculum uses them.
        """
        self._scan()
        entries: dict[str, dict] = {}
        for lesson_id, folder in self._lessons.items():
            for ref in self._json(folder / "manifest.json").get("references", []):
                key = ref["url"] if ref["kind"] != "book" else ref["title"]  # one book, several sections
                entry = entries.setdefault(key, {k: ref[k] for k in ("kind", "title", "authors", "url")} | {"year": ref.get("year"), "lessons": []})
                if lesson_id not in entry["lessons"]:
                    entry["lessons"].append(lesson_id)
                if ref["kind"] == "book":
                    sections = entry.setdefault("sections", {})
                    for part in _split_location(ref["location"]):
                        cited = sections.setdefault(part, [])
                        if lesson_id not in cited:
                            cited.append(lesson_id)
        for entry in entries.values():
            entry["lessons"].sort(key=_lesson_key)
            if "sections" in entry:
                entry["sections"] = sorted(
                    ({"location": part, "lessons": sorted(ids, key=_lesson_key)} for part, ids in entry["sections"].items()),
                    key=lambda section: _location_key(section["location"]),
                )
        works = list(entries.values())
        books = sorted((w for w in works if w["kind"] == "book"), key=lambda w: _surname(w["authors"]))
        papers = sorted((w for w in works if w["kind"] == "paper"), key=lambda w: (_surname(w["authors"]), w.get("year") or 0))
        # Courses and tutorials: in curriculum order (the first lesson that cites them, outside
        # Track 0, which is optional and would cite the pages out of course order).
        def by_use(work: dict) -> tuple:
            main = [lesson for lesson in work["lessons"] if not lesson.startswith("0.")] or work["lessons"]
            return (_lesson_key(main[0]), work["title"])
        courses = sorted((w for w in works if w["kind"] == "course"), key=by_use)
        tutorials = sorted((w for w in works if w["kind"] == "tutorial"), key=by_use)
        sources = self._json(self.root / "sources.json") if (self.root / "sources.json").exists() else {}
        return {
            "works": books + papers + courses + tutorials,
            "lectures": sources.get("lectures", []),
            "software": sources.get("software", []),
        }

    def glossary(self) -> list[dict]:
        """Glossary terms (content/glossary.json), if it exists."""
        path = self.root / "glossary.json"
        return self._json(path)["terms"] if path.exists() else []

    def review(self, track_id: int) -> list[dict]:
        """End-of-track review questions (track_N_*/review.json)."""
        self._scan()
        path = self._review_path(track_id)
        if path is None:
            raise ContentError(t("content.no_review", track=track_id))
        return self._json(path)["questions"]

    def solution(self, lesson_id: str, challenge: bool = False) -> str:
        """Commented solution, shown on request from someone who is stuck (never sent along with the lesson)."""
        folder = self._folder(lesson_id)
        if challenge and "challenge" not in self._json(folder / "manifest.json"):
            raise ContentError(t("content.no_challenge", lesson_id=lesson_id))
        return self._text(folder / ("challenge_solution.py" if challenge else "solution.py"))

    def lesson(self, lesson_id: str) -> dict:
        """Everything the frontend needs to open the lesson (without the solution)."""
        folder = self._folder(lesson_id)
        manifest = self._json(folder / "manifest.json")
        text = self._json(folder / "text.json")

        lesson = {k: v for k, v in manifest.items() if k not in ("validation", "prediction_answer")}
        lesson.update({k: text[k] for k in ("title", "summary", "mission", "hints")})
        lesson["objectives"] = text.get("objectives", [])
        if "challenge" in manifest and "challenge" in text:
            # Optional challenge, unlocked after the mission: only the text goes to the interface.
            lesson["challenge"] = {k: text["challenge"][k] for k in ("mission", "hints")}
        if "prediction" in text:
            lesson["prediction"] = {**text["prediction"], "answer": manifest["prediction_answer"]}
        if "comparison" in manifest:
            lesson["comparison"] = {**manifest["comparison"], **text.get("comparison", {})}
        if "views" in text:
            lesson["view_labels"] = text["views"]
        if "controls" in manifest:
            labels = text.get("controls", {})
            lesson["controls"] = [
                {**control, "label": labels.get(control["id"], {}).get("label", control["id"]),
                 "option_labels": labels.get(control["id"], {}).get("options", {})}
                for control in manifest["controls"]
            ]
        lesson["theory"] = self._text(folder / "theory.md")
        lesson["starter_code"] = self._text(folder / "starter_code.py")
        return lesson

    def search(self, query: str, limit: int = 8) -> list[dict]:
        """Search across lessons: title, summary, mission, hints and theory.

        Ignores accents and case; all the search words must appear.
        Sorts by relevance (title weighs more than the theory body) and returns a
        snippet of text around the first occurrence.
        """
        terms = [t for t in _fold(query).split() if t]
        if not terms:
            return []
        weights = {"title": 8, "summary": 4, "mission": 3, "hints": 2, "theory": 1}
        results = []
        for lesson_id, entry in self._index().items():
            fields, folded = entry["fields"], entry["folded"]
            if not all(any(term in text for text in folded.values()) for term in terms):
                continue
            score = sum(weights[name] * text.count(term) for name, text in folded.items() for term in terms)
            score += 20 * sum(term in folded["title"] for term in terms) + (5 if lesson_id.startswith(query.strip()) else 0)
            if entry["project"]:  # someone searching for a concept wants the lesson that teaches it, not the project
                score *= 0.5
            source = next((name for name in ("summary", "mission", "theory", "hints") if terms[0] in folded[name]), "summary")
            results.append({
                "id": lesson_id,
                "track": entry["track"],
                "title": fields["title"],
                "snippet": _snippet(fields[source], folded[source], terms[0]),
                "score": score,
            })
        results.sort(key=lambda r: (-r["score"], r["id"]))
        return results[:limit]

    def _index(self) -> dict[str, dict]:
        """Searchable text of every lesson, folded once; a lesson is re-read only when its files change."""
        self._scan()
        index: dict[str, dict] = {}
        for lesson_id, folder in self._lessons.items():
            files = [folder / name for name in ("manifest.json", "text.json", "theory.md")]
            stamp = tuple(self._files.stamp(path) for path in files)
            cached = self._search_index.get(lesson_id)
            if cached is not None and cached[0] == (folder, stamp):
                index[lesson_id] = cached[1]
                continue
            try:
                lesson = self.lesson(lesson_id)
            except (ContentError, KeyError):  # an incomplete lesson does not break the search over the others
                continue
            fields = {
                "title": lesson["title"],
                "summary": lesson["summary"],
                "mission": lesson["mission"],
                "hints": " ".join(lesson["hints"]),
                "theory": _plain(lesson["theory"]),
            }
            entry = {
                "fields": fields,
                "folded": {name: _fold(text) for name, text in fields.items()},
                "track": lesson["track"],
                "project": bool(lesson.get("project")),
            }
            self._search_index[lesson_id] = ((folder, stamp), entry)
            index[lesson_id] = entry
        return index

    def starter_code(self, lesson_id: str) -> str:
        return self._text(self._folder(lesson_id) / "starter_code.py")

    def validation_bundle(self, lesson_id: str, challenge: bool = False) -> dict:
        """Data the worker needs to validate (includes the reference solution).

        With `challenge`, validates the lesson's challenge: rules in manifest["challenge"],
        challenge_solution.py and, if they exist, challenge_check.py and
        challenge_hidden_setup.py (otherwise, the lesson's hidden setup).
        """
        folder = self._folder(lesson_id)
        manifest = self._json(folder / "manifest.json")
        if challenge and "challenge" not in manifest:
            raise ContentError(t("content.no_challenge", lesson_id=lesson_id))
        prefix = "challenge_" if challenge else ""
        validation = manifest["challenge"]["validation"] if challenge else manifest["validation"]
        bundle = {
            "id": manifest["id"],
            "validation": validation,
            "max_qubits": manifest.get("max_qubits"),
            "framework": manifest.get("framework", "qiskit"),
            "solution": self._text(folder / f"{prefix}solution.py"),
            "hidden_setup": self._hidden_setup(folder, challenge),
        }
        if validation["type"] == "custom":
            bundle["check"] = self._text(folder / f"{prefix}check.py")
            text = self._json(folder / "text.json")
            source = text.get("challenge", {}) if challenge else text
            bundle["messages"] = source.get("messages", {})
        return bundle

    def timeout(self, lesson_id: str | None) -> float | None:
        if not lesson_id:
            return None
        value = self._json(self._folder(lesson_id) / "manifest.json").get("timeout")
        return float(value) if value else None

    def control_inputs(self, lesson_id: str | None, chosen: dict | None) -> dict | None:
        """Values of the lesson's controls (e.g. injected error), validated against the manifest."""
        if not lesson_id:
            return None
        controls = self._json(self._folder(lesson_id) / "manifest.json").get("controls")
        if not controls:
            return None
        chosen = chosen if isinstance(chosen, dict) else {}
        values = {}
        for control in controls:
            value = chosen.get(control["id"], control["default"])
            values[control["id"]] = value if value in control["options"] else control["default"]
        return {"_QLP_INPUT": values}

    def run_context(self, lesson_id: str | None, challenge: bool = False) -> dict:
        """Optional execution context of a lesson (hidden setup, qubit cap)."""
        if not lesson_id:
            return {}
        folder = self._folder(lesson_id)
        manifest = self._json(folder / "manifest.json")
        analysis = folder / "analysis.py"
        return {
            "max_qubits": manifest.get("max_qubits"),
            "hidden_setup": self._hidden_setup(folder, challenge and "challenge" in manifest),
            "framework": manifest.get("framework", "qiskit"),
            "qnode": manifest.get("qnode"),
            "analysis": self._text(analysis) if analysis.exists() else None,
        }

    def _section_flags(self, lesson_id: str) -> dict:
        """End-of-track project, whether a challenge exists and the objectives, for the track map."""
        if lesson_id not in self._lessons:
            return {}
        folder = self._lessons[lesson_id]
        manifest = self._json(folder / "manifest.json")
        text = self._json(folder / "text.json")
        return {
            "project": bool(manifest.get("project")),
            "has_challenge": "challenge" in manifest,
            "estimated_minutes": manifest.get("estimated_minutes"),
            # Shown on the home page, where the learner chooses what to study next.
            "objectives": text.get("objectives", []),
        }

    def _review_path(self, track_id) -> Path | None:
        folder = self._tracks.get(int(track_id)) if str(track_id).lstrip("-").isdigit() else None
        path = folder / "review.json" if folder else None
        return path if path and path.exists() else None

    def _hidden_setup(self, folder: Path, challenge: bool = False) -> str | None:
        if challenge and (folder / "challenge_hidden_setup.py").exists():
            return self._text(folder / "challenge_hidden_setup.py")
        path = folder / "hidden_setup.py"
        return self._text(path) if path.exists() else None

    def _folder(self, lesson_id: str) -> Path:
        self._scan()
        try:
            return self._lessons[lesson_id]
        except KeyError:
            raise ContentError(t("content.unknown_lesson", lesson_id=lesson_id)) from None


_DASHES = str.maketrans({"\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-", "\u2212": "-"})


def _lesson_key(lesson_id: str) -> tuple[int, ...]:
    return tuple(int(part) for part in lesson_id.split("."))


def _surname(authors: str) -> str:
    """Surname of the first author ("A. Yu. Kitaev" -> "kitaev"), without accents."""
    first = authors.split(",")[0].strip()
    return _fold(first.split()[-1] if first else "")


def _split_location(location: str) -> list[str]:
    """Splits "Section 1.3.6, …, pp. 25–26; Section 2.2.8, …" into passages, without breaking
    the parentheses (which sometimes contain semicolons)."""
    parts, depth, current = [], 0, ""
    for char in location:
        depth += char == "("
        depth -= char == ")"
        if char == ";" and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += char
    parts.append(current.strip())
    pieces = []
    for part in parts:
        # "…, pp. 447–449, and Section 12.2, …": each section is its own passage.
        pieces += re.split(r",? and (?=(?:Sections? |Figure |Exercise |Box ))", part)
    # The notes in parentheses belong to each lesson; the book passage is the same.
    # (Numbers like "(1.50)" stay: only what contains text, with spaces, is removed.)
    cleaned = (re.sub(r"\s*\((?=[^)]*\s)[^)]*\)", "", piece).strip(" ,") for piece in pieces)
    return [piece[0].upper() + piece[1:] for piece in cleaned if piece]


def _location_key(location: str) -> tuple:
    """Book order: by first cited page; with no page, by section number."""
    page = re.search(r"\bpp?\. (\d+)", location)
    if page:
        return (0, int(page.group(1)))
    number = re.search(r"(\d+(?:\.\d+)*)", location)
    return (1, tuple(int(n) for n in number.group(1).split("."))) if number else (2, location)


def _fold(text: str) -> str:
    """Lowercase and without accents: 'Entanglement' and 'entanglement', 'Quântica' and 'quantica'."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    folded = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    # Hyphen, en dash and em dash count as the same character: "Deutsch-Jozsa" finds "Deutsch–Jozsa".
    # The replacement is one character for one, so the snippet positions remain valid.
    return folded.translate(_DASHES)


def _plain(markdown: str) -> str:
    """Running text of the theory: without LaTeX formulas, code and Markdown markup."""
    text = re.sub(r"\$\$.*?\$\$", " ", markdown, flags=re.S)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\$[^$]*\$", "…", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _snippet(text: str, folded: str, term: str, width: int = 120) -> str:
    """Snippet of up to `width` characters around the first occurrence of the term.

    Removing accents does not change the text length (composed letters become a
    single letter), so the positions match the original.
    """
    position = folded.find(term)
    if position < 0 or len(folded) != len(text):
        return text[:width].rstrip() + ("…" if len(text) > width else "")
    start = max(0, position - width // 3)
    end = min(len(text), start + width)
    snippet = text[start:end].strip()
    return ("…" if start > 0 else "") + snippet + ("…" if end < len(text) else "")


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ContentError(f"Missing file: {path}") from None
    except json.JSONDecodeError as exc:
        raise ContentError(f"{path}: invalid JSON ({exc})") from None


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ContentError(f"Missing file: {path}") from None
