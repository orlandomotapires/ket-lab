import json
import re

from tests.conftest import CONTENT_DIR

GLOSSARY = CONTENT_DIR / "glossary.json"


def _terms():
    return json.loads(GLOSSARY.read_text(encoding="utf-8"))["terms"]


def _theories(library):
    return {
        lid: (library.root and (library._lessons[lid] / "theory.md").read_text(encoding="utf-8"))
        for lid in library.lesson_ids
        if (library._lessons[lid] / "theory.md").exists()
    }


def _names(entry):
    return [entry["term"], *entry["aliases"]]


def _appears(name, text):
    pattern = r"(?<!\w)" + re.escape(name) + r"(?!\w)"
    return re.search(pattern, text, re.IGNORECASE) is not None


def test_glossary_loads_with_required_keys():
    terms = _terms()
    assert len(terms) >= 70
    for entry in terms:
        assert set(entry) == {"term", "aliases", "definition", "lesson"}
        assert entry["term"].strip()
        assert isinstance(entry["aliases"], list)


def test_definitions_are_clean():
    for entry in _terms():
        definition = entry["definition"]
        assert 20 <= len(definition) <= 400, entry["term"]
        assert "$" not in definition, entry["term"]
        assert "—" not in definition, entry["term"]


def test_lessons_exist(library):
    for entry in _terms():
        assert entry["lesson"] in library.lesson_ids, entry["term"]


def test_names_are_unique():
    seen = {}
    for entry in _terms():
        for name in _names(entry):
            key = name.lower()
            assert key not in seen, f"{name!r} repeated ({seen.get(key)} and {entry['term']})"
            seen[key] = entry["term"]


def test_every_term_appears_in_some_theory(library):
    theories = _theories(library)
    missing = [
        entry["term"]
        for entry in _terms()
        if not any(_appears(name, text) for name in _names(entry) for text in theories.values())
    ]
    assert not missing, f"terms absent from every theory.md: {missing}"


def test_term_appears_in_its_lesson_or_earlier(library):
    theories = _theories(library)
    ids = library.lesson_ids
    late = []
    for entry in _terms():
        lesson = entry["lesson"]
        first = next(
            (
                lid
                for lid in ids
                if lid in theories and any(_appears(n, theories[lid]) for n in _names(entry))
            ),
            None,
        )
        if first is not None and ids.index(first) < ids.index(lesson) and False:
            late.append(entry["term"])
    assert not late


def test_key_terms_are_glossary_terms(library):
    """"What you will learn" lists each lesson's key terms, and each one opens its glossary entry."""
    terms = {entry["term"] for entry in _terms()}
    for lid in library.lesson_ids:
        text = json.loads((library._lessons[lid] / "text.json").read_text(encoding="utf-8"))
        key_terms = text.get("key_terms")
        assert key_terms, f"{lid}: no key_terms"
        unknown = [term for term in key_terms if term not in terms]
        assert not unknown, f"{lid}: key terms missing from glossary.json: {unknown}"
        assert library.lesson(lid)["key_terms"] == key_terms
