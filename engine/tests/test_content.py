"""Suíte de conteúdo: toda lição precisa ser válida, completa e resolvível."""

import json

import jsonschema
import pytest

from qlp_engine import messages, validation

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
def test_every_lesson_has_its_text(library, lesson_id):
    folder = next(p for p in MANIFESTS if json.loads(p.read_text())["id"] == lesson_id).parent
    for name in ("text.json", "theory.md", "starter_code.py"):
        assert (folder / name).is_file(), f"{lesson_id}: falta {name}"

    text = json.loads((folder / "text.json").read_text(encoding="utf-8"))
    jsonschema.validate(text, TEXT_SCHEMA)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if "prediction_answer" in manifest:
        assert manifest["prediction_answer"] < len(text["prediction"]["options"])
    if "comparison" in manifest:
        assert "comparison" in text

    lesson = library.lesson(lesson_id)
    assert lesson["theory"].strip()
    section = next(s for t in library.catalog()["tracks"] for s in t["sections"] if s["id"] == lesson_id)
    assert lesson["title"] == section["title"], "o título da lição precisa ser igual ao do catálogo"


def test_every_lesson_is_in_the_catalog(library):
    catalog_ids = {s["id"] for t in library.catalog()["tracks"] for s in t["sections"]}
    assert set(library.lesson_ids) <= catalog_ids


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_reference_solution_passes(library, lesson_id):
    bundle = library.validation_bundle(lesson_id)
    result = validation.validate(bundle["solution"], bundle)
    assert result["passed"], (lesson_id, result)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_starter_code_runs_but_does_not_pass(library, lesson_id):
    bundle = library.validation_bundle(lesson_id)
    result = validation.validate(library.starter_code(lesson_id), bundle)
    assert not result["passed"], lesson_id
    assert result["code"] != "error", (lesson_id, result)


def test_lesson_payload_does_not_leak_the_solution(library):
    for lesson_id in library.lesson_ids:
        payload = library.lesson(lesson_id)
        assert "solution" not in payload and "validation" not in payload
        assert "prediction_answer" not in payload
        assert payload["hints"]


def test_engine_messages_format_without_errors():
    import string

    for key, template in messages.MESSAGES.items():
        names = {name for _, name, _, _ in string.Formatter().parse(template) if name}
        assert messages.t(key, **{name: "x" for name in names}), key


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_every_lesson_has_theoretical_and_practical_references(library, lesson_id):
    references = library.lesson(lesson_id).get("references") or []
    kinds = {ref["kind"] for ref in references}
    assert len(references) >= 2, f"{lesson_id}: pelo menos 2 referências"
    assert kinds & {"book", "paper"}, f"{lesson_id}: falta uma referência teórica (livro ou artigo)"
    assert kinds & {"course", "tutorial"}, f"{lesson_id}: falta uma referência prática (curso ou tutorial)"
    assert all(ref["location"].strip() and "TODO" not in ref["location"] for ref in references), (
        f"{lesson_id}: local de leitura ausente ou não verificado"
    )
    urls = [ref["url"] for ref in references]
    assert len(set(urls)) == len(urls), f"{lesson_id}: links repetidos"
    assert all(url.startswith("https://") for url in urls)


@pytest.mark.parametrize(
    "query, expected",
    [
        ("grover", "2.6"),
        ("Kraus", "4.1"),
        ("entanglement", "1.5"),
        ("ENTANGLEMENT", "1.5"),
        ("quantum fourier", "2.7"),  # duas palavras
        ("teleportation", "1.6"),
        ("max-cut", "3.3"),
        ("deutsch-jozsa", "2.3"),  # hífen do teclado acha o título com traço (–)
    ],
)
def test_search_finds_the_right_lesson_first(library, query, expected):
    results = library.search(query)
    assert results and results[0]["id"] == expected, [(r["id"], r["title"]) for r in results[:3]]
    assert results[0]["snippet"]


def test_search_requires_every_word_and_ignores_empty_queries(library):
    assert library.search("") == []
    assert library.search("grover xyzzy") == []
    snippet = library.search("Kraus")[0]["snippet"]
    assert "$" not in snippet and "Kraus" in snippet


CHALLENGE_IDS = [
    json.loads(p.read_text(encoding="utf-8"))["id"]
    for p in MANIFESTS
    if "challenge" in json.loads(p.read_text(encoding="utf-8"))
]


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_challenge_text_and_rules_come_together(library, lesson_id):
    folder = next(p for p in MANIFESTS if json.loads(p.read_text())["id"] == lesson_id).parent
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    text = json.loads((folder / "text.json").read_text(encoding="utf-8"))
    assert ("challenge" in manifest) == ("challenge" in text), lesson_id
    if "challenge" in manifest:
        assert (folder / "challenge_solution.py").is_file()
        if manifest["challenge"]["validation"]["type"] == "custom":
            assert (folder / "challenge_check.py").is_file()


@pytest.mark.parametrize("lesson_id", CHALLENGE_IDS or ["-"])
def test_challenge_is_solvable_and_harder_than_the_mission(library, lesson_id):
    if lesson_id == "-":
        pytest.skip("nenhuma lição com desafio ainda")
    bundle = library.validation_bundle(lesson_id, challenge=True)
    solved = validation.validate(bundle["solution"], bundle)
    assert solved["passed"], (lesson_id, solved)
    starter = validation.validate(library.starter_code(lesson_id), bundle)
    assert not starter["passed"], lesson_id
    mission_solution = library.validation_bundle(lesson_id)["solution"]
    assert not validation.validate(mission_solution, bundle)["passed"], f"{lesson_id}: a solução da missão já resolve o desafio"
