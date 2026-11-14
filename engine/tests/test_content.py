"""Suíte de conteúdo: toda lição precisa ser válida, resolvível e existir nos três idiomas."""

import json

import jsonschema
import pytest

from qlp_engine import i18n, validation

from .conftest import CONTENT_DIR

MANIFEST_SCHEMA = json.loads((CONTENT_DIR / "schema" / "manifest.schema.json").read_text(encoding="utf-8"))
TEXT_SCHEMA = json.loads((CONTENT_DIR / "schema" / "text.schema.json").read_text(encoding="utf-8"))
MANIFESTS = sorted(CONTENT_DIR.glob("track_*/*/manifest.json"))
LESSON_IDS = [json.loads(p.read_text(encoding="utf-8"))["id"] for p in MANIFESTS]


def test_there_is_content():
    assert MANIFESTS


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.parent.name)
def test_manifest_matches_schema(path):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.validate(manifest, MANIFEST_SCHEMA)
    assert manifest["default_visualizer"] in manifest["available_visualizers"]


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
@pytest.mark.parametrize("lang", i18n.LANGS)
def test_every_lesson_exists_in_every_language(library, lesson_id, lang):
    folder = CONTENT_DIR / next(p for p in MANIFESTS if json.loads(p.read_text())["id"] == lesson_id).parent
    locale = folder / "locales" / lang
    for name in ("text.json", "theory.md", "starter_code.py"):
        assert (locale / name).is_file(), f"{lesson_id}: falta locales/{lang}/{name}"

    text = json.loads((locale / "text.json").read_text(encoding="utf-8"))
    jsonschema.validate(text, TEXT_SCHEMA)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if "prediction_answer" in manifest:
        assert manifest["prediction_answer"] < len(text["prediction"]["options"])
    if "comparison" in manifest:
        assert "comparison" in text

    lesson = library.lesson(lesson_id, lang)
    assert lesson["lang"] == lang
    assert lesson["theory"].strip()
    section = next(s for t in library.catalog(lang)["tracks"] for s in t["sections"] if s["id"] == lesson_id)
    assert lesson["title"] == section["title"], "o título da lição precisa ser igual ao do catálogo"


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_every_language_has_the_same_number_of_hints_and_options(library, lesson_id):
    shapes = set()
    for lang in i18n.LANGS:
        lesson = library.lesson(lesson_id, lang)
        shapes.add((len(lesson["hints"]), len(lesson.get("prediction", {}).get("options", []))))
    assert len(shapes) == 1, shapes


def test_every_lesson_is_in_the_catalog(library):
    catalog_ids = {s["id"] for t in library.catalog()["tracks"] for s in t["sections"]}
    assert set(library.lesson_ids) <= catalog_ids


def test_catalog_is_translated(library):
    titles = {lang: library.catalog(lang)["tracks"][0]["title"] for lang in i18n.LANGS}
    assert len(set(titles.values())) == 3, titles


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_reference_solution_passes(library, lesson_id):
    bundle = library.validation_bundle(lesson_id)
    result = validation.validate(bundle["solution"], bundle)
    assert result["passed"], (lesson_id, result)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
@pytest.mark.parametrize("lang", i18n.LANGS)
def test_starter_code_runs_but_does_not_pass(library, lesson_id, lang):
    bundle = library.validation_bundle(lesson_id)
    result = validation.validate(library.starter_code(lesson_id, lang), bundle)
    assert not result["passed"], (lesson_id, lang)
    assert result["code"] != "error", (lesson_id, lang, result)


def test_lesson_payload_does_not_leak_the_solution(library):
    for lesson_id in library.lesson_ids:
        payload = library.lesson(lesson_id)
        assert "solution" not in payload and "validation" not in payload
        assert "prediction_answer" not in payload
        assert payload["hints"]


def test_engine_messages_exist_in_every_language():
    for key, entry in i18n.MESSAGES.items():
        assert set(entry) == set(i18n.LANGS), key
        fields = {lang: sorted(_fields(text)) for lang, text in entry.items()}
        assert len({tuple(v) for v in fields.values()}) == 1, (key, fields)


def _fields(template: str) -> set[str]:
    import string

    return {name for _, name, _, _ in string.Formatter().parse(template) if name}


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_every_lesson_has_theoretical_and_practical_references(library, lesson_id):
    references = library.lesson(lesson_id).get("references") or []
    kinds = {ref["kind"] for ref in references}
    assert len(references) >= 2, f"{lesson_id}: pelo menos 2 referências"
    assert kinds & {"book", "paper"}, f"{lesson_id}: falta uma referência teórica (livro ou artigo)"
    assert kinds & {"course", "tutorial"}, f"{lesson_id}: falta uma referência prática (curso ou tutorial)"
    urls = [ref["url"] for ref in references]
    assert len(set(urls)) == len(urls), f"{lesson_id}: links repetidos"
    assert all(url.startswith("https://") for url in urls)
