"""Commented solutions ("Show a solution" button) and end-of-track reviews."""

import io
import json
import tokenize

import jsonschema
import pytest

from .conftest import CONTENT_DIR

MANIFESTS = sorted(CONTENT_DIR.glob("track_*/*/manifest.json"))
SOLUTIONS = sorted(
    path for manifest in MANIFESTS for path in manifest.parent.glob("*solution.py")
)
REVIEW_SCHEMA = json.loads((CONTENT_DIR / "schema" / "review.schema.json").read_text(encoding="utf-8"))
TRACK_FOLDERS = sorted(p for p in CONTENT_DIR.glob("track_*") if p.is_dir())
# Track 0 is optional and has no review.
REVIEWED_TRACKS = [p for p in TRACK_FOLDERS if not p.name.startswith("track_0_")]


def _comments_and_code(source: str) -> tuple[list[str], int]:
    comments, code_lines = [], set()
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            comments.append(token.string.lstrip("# ").strip())
        elif token.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER):
            code_lines.add(token.start[0])
    return comments, len(code_lines)


@pytest.mark.parametrize("path", SOLUTIONS, ids=lambda p: f"{p.parent.name}/{p.name}")
def test_solution_is_explained(path):
    """The solution is shown to a student who is stuck: each step carries the idea, not just the code."""
    source = path.read_text(encoding="utf-8")
    comments, code_lines = _comments_and_code(source)
    explained = [c for c in comments if len(c.split()) >= 4]
    assert len(explained) >= 3, f"{path}: at least 3 comments that explain the idea"
    assert len(explained) * 6 >= code_lines, f"{path}: {len(explained)} comments for {code_lines} lines of code"
    first_code = next(
        (i for i, line in enumerate(source.splitlines()) if line.strip() and not line.lstrip().startswith(("#", "import ", "from "))),
        0,
    )
    head = "\n".join(source.splitlines()[:first_code])
    assert "#" in head, f"{path}: start with a comment that sums up the idea of the solution"
    assert "—" not in source, f"{path}: no em dashes (writing guide)"


def _track_lessons(folder) -> dict[str, dict]:
    return {
        (manifest := json.loads(path.read_text(encoding="utf-8")))["id"]: manifest
        for path in folder.glob("*/manifest.json")
    }


@pytest.mark.parametrize("folder", REVIEWED_TRACKS, ids=lambda p: p.name)
def test_track_review(folder):
    path = folder / "review.json"
    assert path.is_file(), f"{folder.name}: falta review.json"
    review = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.validate(review, REVIEW_SCHEMA)
    lessons = _track_lessons(folder)
    questions = review["questions"]
    for q in questions:
        assert q["answer"] < len(q["options"]), q["question"]
        assert q["lesson"] in lessons, f"{folder.name}: lesson {q['lesson']} is not in this track"
        assert len(q["explanation"].split()) >= 8, f"explanation too short: {q['question']}"
        assert "—" not in json.dumps(q, ensure_ascii=False)
    assert len({q["question"] for q in questions}) == len(questions)
    # The review covers the track: at least 60% of the lessons (excluding the project) appear.
    taught = [i for i, m in lessons.items() if not m.get("project")]
    covered = {q["lesson"] for q in questions}
    assert len(covered & set(taught)) >= 0.6 * len(taught) or len(covered) >= 8, (folder.name, sorted(covered))
    # The right answer is not always in the same position.
    assert len({q["answer"] for q in questions}) >= 3, f"{folder.name}: vary the position of the right answer"
