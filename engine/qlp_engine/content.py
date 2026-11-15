"""Carrega o catálogo e as lições da pasta /content.

Estrutura de uma lição:
    manifest.json        estrutura (visualizações, validação); sem texto
    text.json            título, resumo, missão, previsão, dicas
    theory.md            teoria
    starter_code.py      código inicial
    solution.py          solução de referência (define o alvo)
    hidden_setup.py      opcional: preparação oculta, oráculos

Este módulo não importa o Qiskit: roda no processo do servidor, que precisa
iniciar rápido. Tudo que exige simulação acontece no worker.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from .messages import t

REQUIRED_MANIFEST_KEYS = ("id", "track", "num_qubits", "validation")


class ContentError(Exception):
    pass


class ContentLibrary:
    def __init__(self, root: Path):
        self.root = Path(root)
        if not self.root.is_dir():
            raise ContentError(f"Pasta de conteúdo não encontrada: {self.root}")
        self._lessons: dict[str, Path] = {}
        for manifest_path in sorted(self.root.glob("track_*/*/manifest.json")):
            manifest = _read_json(manifest_path)
            missing = [key for key in REQUIRED_MANIFEST_KEYS if key not in manifest]
            if missing:
                raise ContentError(f"{manifest_path}: faltam os campos {missing}")
            if manifest["id"] in self._lessons:
                raise ContentError(f"Id de lição duplicado: {manifest['id']}")
            self._lessons[manifest["id"]] = manifest_path.parent

    @property
    def lesson_ids(self) -> list[str]:
        return list(self._lessons)

    def catalog(self) -> dict:
        """Currículo completo; cada seção indica se já tem conteúdo."""
        raw = _read_json(self.root / "catalog.json")
        return {
            "tracks": [
                {
                    "id": track["id"],
                    "title": track["title"],
                    "level": track["level"],
                    "sections": [
                        {
                            "id": section["id"],
                            "title": section["title"],
                            "summary": section["summary"],
                            "available": section["id"] in self._lessons,
                            **self._section_flags(section["id"]),
                        }
                        for section in track["sections"]
                    ],
                }
                for track in raw["tracks"]
            ]
        }

    def bibliography(self) -> dict:
        """Todas as referências das lições (sem repetição, com as lições que as citam),
        mais o material de aula e o software usados no desenvolvimento (content/sources.json).

        Livros viram um guia de leitura: cada trecho citado (seção, título, páginas), na
        ordem do livro, com as lições que o citam. Artigos ficam em ordem de sobrenome do
        primeiro autor; páginas de curso, na ordem em que o currículo as usa.
        """
        entries: dict[str, dict] = {}
        for lesson_id, folder in self._lessons.items():
            for ref in _read_json(folder / "manifest.json").get("references", []):
                key = ref["url"] if ref["kind"] != "book" else ref["title"]  # um livro, várias seções
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
        # Cursos e tutoriais: na ordem do currículo (a primeira lição que os cita, fora da
        # Trilha 0, que é opcional e citaria as páginas fora da ordem do curso).
        def by_use(work: dict) -> tuple:
            main = [lesson for lesson in work["lessons"] if not lesson.startswith("0.")] or work["lessons"]
            return (_lesson_key(main[0]), work["title"])
        courses = sorted((w for w in works if w["kind"] == "course"), key=by_use)
        tutorials = sorted((w for w in works if w["kind"] == "tutorial"), key=by_use)
        sources = _read_json(self.root / "sources.json") if (self.root / "sources.json").exists() else {}
        return {
            "works": books + papers + courses + tutorials,
            "lectures": sources.get("lectures", []),
            "software": sources.get("software", []),
        }

    def glossary(self) -> list[dict]:
        """Termos do glossário (content/glossary.json), se existir."""
        path = self.root / "glossary.json"
        return _read_json(path)["terms"] if path.exists() else []

    def lesson(self, lesson_id: str) -> dict:
        """Tudo que o frontend precisa para abrir a lição (sem a solução)."""
        folder = self._folder(lesson_id)
        manifest = _read_json(folder / "manifest.json")
        text = _read_json(folder / "text.json")

        lesson = {k: v for k, v in manifest.items() if k not in ("validation", "prediction_answer")}
        lesson.update({k: text[k] for k in ("title", "summary", "mission", "hints")})
        lesson["objectives"] = text.get("objectives", [])
        if "challenge" in manifest and "challenge" in text:
            # Desafio opcional, liberado depois da missão: só o texto vai para a interface.
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
        lesson["theory"] = _read_text(folder / "theory.md")
        lesson["starter_code"] = _read_text(folder / "starter_code.py")
        return lesson

    def search(self, query: str, limit: int = 8) -> list[dict]:
        """Busca nas lições: título, resumo, missão, dicas e teoria.

        Ignora acentos e maiúsculas; todas as palavras da busca precisam aparecer.
        Ordena por relevância (título pesa mais que o corpo da teoria) e devolve um
        trecho de texto em volta da primeira ocorrência.
        """
        terms = [t for t in _fold(query).split() if t]
        if not terms:
            return []
        weights = {"title": 8, "summary": 4, "mission": 3, "hints": 2, "theory": 1}
        results = []
        for lesson_id in self._lessons:
            try:
                lesson = self.lesson(lesson_id)
            except (ContentError, KeyError):  # lição incompleta não derruba a busca das outras
                continue
            fields = {
                "title": lesson["title"],
                "summary": lesson["summary"],
                "mission": lesson["mission"],
                "hints": " ".join(lesson["hints"]),
                "theory": _plain(lesson["theory"]),
            }
            folded = {name: _fold(text) for name, text in fields.items()}
            if not all(any(term in text for text in folded.values()) for term in terms):
                continue
            score = sum(weights[name] * text.count(term) for name, text in folded.items() for term in terms)
            score += 20 * sum(term in folded["title"] for term in terms) + (5 if lesson_id.startswith(query.strip()) else 0)
            if lesson.get("project"):  # quem busca um conceito quer a lição que o ensina, não o projeto
                score *= 0.5
            source = next((name for name in ("summary", "mission", "theory", "hints") if terms[0] in folded[name]), "summary")
            results.append({
                "id": lesson_id,
                "track": lesson["track"],
                "title": lesson["title"],
                "snippet": _snippet(fields[source], folded[source], terms[0]),
                "score": score,
            })
        results.sort(key=lambda r: (-r["score"], r["id"]))
        return results[:limit]

    def starter_code(self, lesson_id: str) -> str:
        return _read_text(self._folder(lesson_id) / "starter_code.py")

    def validation_bundle(self, lesson_id: str, challenge: bool = False) -> dict:
        """Dados que o worker precisa para validar (inclui a solução de referência).

        Com `challenge`, valida o desafio da lição: regras em manifest["challenge"],
        challenge_solution.py e, se existirem, challenge_check.py e
        challenge_hidden_setup.py (senão, o setup oculto da lição).
        """
        folder = self._folder(lesson_id)
        manifest = _read_json(folder / "manifest.json")
        if challenge and "challenge" not in manifest:
            raise ContentError(t("content.no_challenge", lesson_id=lesson_id))
        prefix = "challenge_" if challenge else ""
        validation = manifest["challenge"]["validation"] if challenge else manifest["validation"]
        bundle = {
            "id": manifest["id"],
            "validation": validation,
            "max_qubits": manifest.get("max_qubits"),
            "framework": manifest.get("framework", "qiskit"),
            "solution": _read_text(folder / f"{prefix}solution.py"),
            "hidden_setup": self._hidden_setup(folder, challenge),
        }
        if validation["type"] == "custom":
            bundle["check"] = _read_text(folder / f"{prefix}check.py")
            text = _read_json(folder / "text.json")
            source = text.get("challenge", {}) if challenge else text
            bundle["messages"] = source.get("messages", {})
        return bundle

    def timeout(self, lesson_id: str | None) -> float | None:
        if not lesson_id:
            return None
        value = _read_json(self._folder(lesson_id) / "manifest.json").get("timeout")
        return float(value) if value else None

    def control_inputs(self, lesson_id: str | None, chosen: dict | None) -> dict | None:
        """Valores dos controles da lição (ex.: erro injetado), validados contra o manifest."""
        if not lesson_id:
            return None
        controls = _read_json(self._folder(lesson_id) / "manifest.json").get("controls")
        if not controls:
            return None
        chosen = chosen if isinstance(chosen, dict) else {}
        values = {}
        for control in controls:
            value = chosen.get(control["id"], control["default"])
            values[control["id"]] = value if value in control["options"] else control["default"]
        return {"_QLP_INPUT": values}

    def run_context(self, lesson_id: str | None, challenge: bool = False) -> dict:
        """Contexto opcional de execução de uma lição (setup oculto, teto de qubits)."""
        if not lesson_id:
            return {}
        folder = self._folder(lesson_id)
        manifest = _read_json(folder / "manifest.json")
        analysis = folder / "analysis.py"
        return {
            "max_qubits": manifest.get("max_qubits"),
            "hidden_setup": self._hidden_setup(folder, challenge and "challenge" in manifest),
            "framework": manifest.get("framework", "qiskit"),
            "qnode": manifest.get("qnode"),
            "analysis": _read_text(analysis) if analysis.exists() else None,
        }

    def _section_flags(self, lesson_id: str) -> dict:
        """Projeto de fim de trilha e existência de desafio, para o mapa de trilhas."""
        if lesson_id not in self._lessons:
            return {}
        manifest = _read_json(self._lessons[lesson_id] / "manifest.json")
        return {"project": bool(manifest.get("project")), "has_challenge": "challenge" in manifest}

    def _hidden_setup(self, folder: Path, challenge: bool = False) -> str | None:
        if challenge and (folder / "challenge_hidden_setup.py").exists():
            return _read_text(folder / "challenge_hidden_setup.py")
        path = folder / "hidden_setup.py"
        return _read_text(path) if path.exists() else None

    def _folder(self, lesson_id: str) -> Path:
        try:
            return self._lessons[lesson_id]
        except KeyError:
            raise ContentError(t("content.unknown_lesson", lesson_id=lesson_id)) from None


_DASHES = str.maketrans({"\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-", "\u2212": "-"})


def _lesson_key(lesson_id: str) -> tuple[int, ...]:
    return tuple(int(part) for part in lesson_id.split("."))


def _surname(authors: str) -> str:
    """Sobrenome do primeiro autor ("A. Yu. Kitaev" -> "kitaev"), sem acentos."""
    first = authors.split(",")[0].strip()
    return _fold(first.split()[-1] if first else "")


def _split_location(location: str) -> list[str]:
    """Separa "Section 1.3.6, …, pp. 25–26; Section 2.2.8, …" nos trechos, sem quebrar
    os parênteses (que às vezes têm ponto e vírgula dentro)."""
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
        # "…, pp. 447–449, and Section 12.2, …": cada seção é um trecho próprio.
        pieces += re.split(r",? and (?=(?:Sections? |Figure |Exercise |Box ))", part)
    # As notas entre parênteses são de cada lição; o trecho do livro é o mesmo.
    # (Números como "(1.50)" ficam: só sai o que tem texto, com espaços.)
    cleaned = (re.sub(r"\s*\((?=[^)]*\s)[^)]*\)", "", piece).strip(" ,") for piece in pieces)
    return [piece[0].upper() + piece[1:] for piece in cleaned if piece]


def _location_key(location: str) -> tuple:
    """Ordem do livro: pela primeira página citada; sem página, pelo número da seção."""
    page = re.search(r"\bpp?\. (\d+)", location)
    if page:
        return (0, int(page.group(1)))
    number = re.search(r"(\d+(?:\.\d+)*)", location)
    return (1, tuple(int(n) for n in number.group(1).split("."))) if number else (2, location)


def _fold(text: str) -> str:
    """Minúsculas e sem acentos: 'Emaranhamento' e 'emaranhamento', 'Quântica' e 'quantica'."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    folded = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    # Hífen, traço e travessão contam como o mesmo caractere: "Deutsch-Jozsa" acha "Deutsch–Jozsa".
    # A troca é de um caractere por um, então as posições do trecho continuam valendo.
    return folded.translate(_DASHES)


def _plain(markdown: str) -> str:
    """Texto corrido da teoria: sem fórmulas LaTeX, código e marcação Markdown."""
    text = re.sub(r"\$\$.*?\$\$", " ", markdown, flags=re.S)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\$[^$]*\$", "…", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _snippet(text: str, folded: str, term: str, width: int = 120) -> str:
    """Trecho de até `width` caracteres em volta da primeira ocorrência do termo.

    Remover acentos não muda o comprimento do texto (letras compostas viram uma
    letra), então as posições batem com o original.
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
        raise ContentError(f"Arquivo ausente: {path}") from None
    except json.JSONDecodeError as exc:
        raise ContentError(f"{path}: JSON inválido ({exc})") from None


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ContentError(f"Arquivo ausente: {path}") from None
