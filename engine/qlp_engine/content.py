"""Carrega o catálogo e as lições da pasta /content, no idioma pedido.

Estrutura de uma lição:
    manifest.json            estrutura (visualizações, validação); sem texto
    solution.py              solução de referência (define o alvo)
    hidden_setup.py          opcional: preparação oculta, oráculos
    locales/<idioma>/
        text.json            título, resumo, missão, previsão, dicas
        theory.md            teoria
        starter_code.py      código inicial (com comentários no idioma)

Este módulo não importa o Qiskit: roda no processo do servidor, que precisa
iniciar rápido. Tudo que exige simulação acontece no worker.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import i18n

REQUIRED_MANIFEST_KEYS = ("id", "track", "num_qubits", "validation")
LOCALIZED_FILES = ("text.json", "theory.md", "starter_code.py")


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

    def catalog(self, lang: str | None = None) -> dict:
        """Currículo completo no idioma pedido; cada seção indica se já tem conteúdo."""
        lang = i18n.normalize(lang)
        raw = _read_json(self.root / "catalog.json")
        return {
            "tracks": [
                {
                    "id": track["id"],
                    "title": _pick(track["title"], lang),
                    "level": _pick(track["level"], lang),
                    "sections": [
                        {
                            "id": section["id"],
                            "title": _pick(section["title"], lang),
                            "summary": _pick(section["summary"], lang),
                            "available": section["id"] in self._lessons,
                        }
                        for section in track["sections"]
                    ],
                }
                for track in raw["tracks"]
            ]
        }

    def lesson(self, lesson_id: str, lang: str | None = None) -> dict:
        """Tudo que o frontend precisa para abrir a lição (sem a solução)."""
        folder = self._folder(lesson_id)
        manifest = _read_json(folder / "manifest.json")
        locale = self._locale_dir(folder, i18n.normalize(lang))
        text = _read_json(locale / "text.json")

        lesson = {k: v for k, v in manifest.items() if k not in ("validation", "prediction_answer")}
        lesson.update({k: text[k] for k in ("title", "summary", "mission", "hints")})
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
        lesson["theory"] = _read_text(locale / "theory.md")
        lesson["starter_code"] = _read_text(locale / "starter_code.py")
        lesson["lang"] = locale.name
        return lesson

    def starter_code(self, lesson_id: str, lang: str) -> str:
        return _read_text(self._locale_dir(self._folder(lesson_id), lang) / "starter_code.py")

    def locales(self, lesson_id: str) -> list[str]:
        folder = self._folder(lesson_id) / "locales"
        return sorted(p.name for p in folder.iterdir() if p.is_dir()) if folder.is_dir() else []

    def validation_bundle(self, lesson_id: str, lang: str | None = None) -> dict:
        """Dados que o worker precisa para validar (inclui a solução de referência)."""
        folder = self._folder(lesson_id)
        manifest = _read_json(folder / "manifest.json")
        bundle = {
            "id": manifest["id"],
            "validation": manifest["validation"],
            "max_qubits": manifest.get("max_qubits"),
            "framework": manifest.get("framework", "qiskit"),
            "solution": _read_text(folder / "solution.py"),
            "hidden_setup": self._hidden_setup(folder),
        }
        if manifest["validation"]["type"] == "custom":
            bundle["check"] = _read_text(folder / "check.py")
            text = _read_json(self._locale_dir(folder, i18n.normalize(lang)) / "text.json")
            bundle["messages"] = text.get("messages", {})
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

    def run_context(self, lesson_id: str | None) -> dict:
        """Contexto opcional de execução de uma lição (setup oculto, teto de qubits)."""
        if not lesson_id:
            return {}
        folder = self._folder(lesson_id)
        manifest = _read_json(folder / "manifest.json")
        analysis = folder / "analysis.py"
        return {
            "max_qubits": manifest.get("max_qubits"),
            "hidden_setup": self._hidden_setup(folder),
            "framework": manifest.get("framework", "qiskit"),
            "qnode": manifest.get("qnode"),
            "analysis": _read_text(analysis) if analysis.exists() else None,
        }

    def _hidden_setup(self, folder: Path) -> str | None:
        path = folder / "hidden_setup.py"
        return _read_text(path) if path.exists() else None

    def _locale_dir(self, folder: Path, lang: str) -> Path:
        """O idioma pedido; na falta dele, inglês e depois português."""
        for candidate in (lang, i18n.DEFAULT_LANG, "pt"):
            path = folder / "locales" / candidate
            if path.is_dir():
                return path
        raise ContentError(f"{folder}: nenhuma pasta de idioma encontrada")

    def _folder(self, lesson_id: str) -> Path:
        try:
            return self._lessons[lesson_id]
        except KeyError:
            raise ContentError(i18n.t("content.unknown_lesson", lesson_id=lesson_id)) from None


def _pick(value, lang: str) -> str:
    """Texto do catálogo no idioma pedido (com a mesma ordem de fallback das lições)."""
    if isinstance(value, str):
        return value
    return value.get(lang) or value.get(i18n.DEFAULT_LANG) or value.get("pt") or next(iter(value.values()))


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
