"""Verificação estática do código do aluno.

IMPORTANTE: isto NÃO é uma sandbox de segurança. Filtros por AST são
contornáveis. O objetivo aqui é dar mensagens de erro amigáveis e evitar
acidentes (apagar um arquivo sem querer, travar esperando `input()`).
O isolamento real vem de: processo worker separado, timeout com kill,
limite de memória, teto de qubits e autenticação do WebSocket.
"""

from __future__ import annotations

import ast
import builtins
from dataclasses import dataclass

from .i18n import t

ALLOWED_IMPORTS = frozenset(
    {
        "qiskit",
        "pennylane",
        "numpy",
        "math",
        "cmath",
        "random",
        "itertools",
        "functools",
        "collections",
        "fractions",
    }
)

FORBIDDEN_NAMES = frozenset(
    {
        "__import__",
        "eval",
        "exec",
        "compile",
        "open",
        "input",
        "breakpoint",
        "globals",
        "locals",
        "vars",
        "getattr",
        "setattr",
        "delattr",
        "exit",
        "quit",
    }
)


@dataclass(frozen=True)
class GuardIssue:
    line: int
    message: str


class CodeRejected(Exception):
    """O código não passou na verificação estática."""

    def __init__(self, issues: list[GuardIssue]):
        super().__init__(issues[0].message if issues else "código rejeitado")
        self.issues = issues


def check(code: str) -> ast.Module:
    """Analisa o código e devolve a AST, ou levanta CodeRejected/SyntaxError."""
    tree = ast.parse(code, filename="<aluno>")
    issues: list[GuardIssue] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                _check_module(alias.name, node.lineno, issues)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                issues.append(GuardIssue(node.lineno, t("guard.relative_import")))
            else:
                _check_module(node.module or "", node.lineno, issues)
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            issues.append(GuardIssue(node.lineno, t("guard.forbidden_name", name=node.id)))
        elif isinstance(node, ast.Attribute) and _is_dunder(node.attr):
            issues.append(GuardIssue(node.lineno, t("guard.dunder", name=node.attr)))

    if issues:
        issues.sort(key=lambda issue: issue.line)
        raise CodeRejected(issues)
    return tree


def _check_module(name: str, line: int, issues: list[GuardIssue]) -> None:
    root = name.split(".")[0]
    if root not in ALLOWED_IMPORTS:
        allowed = ", ".join(sorted(ALLOWED_IMPORTS))
        issues.append(GuardIssue(line, t("guard.module", name=root, allowed=allowed)))


def _is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def restricted_builtins() -> dict:
    """Builtins entregues ao código do aluno (import limitado à lista permitida)."""
    safe = {k: v for k, v in vars(builtins).items() if k not in FORBIDDEN_NAMES}
    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level or name.split(".")[0] not in ALLOWED_IMPORTS:
            raise ImportError(t("guard.module_short", name=name))
        return real_import(name, globals, locals, fromlist, level)

    safe["__import__"] = guarded_import
    return safe
