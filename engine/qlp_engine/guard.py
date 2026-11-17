"""Static check of the student's code.

IMPORTANT: this is NOT a security sandbox. AST filters can be
bypassed. The goal here is to give friendly error messages and avoid
accidents (deleting a file by mistake, hanging while waiting for `input()`).
Real isolation comes from: a separate worker process, timeout with kill,
a memory limit, a qubit cap and WebSocket authentication.
"""

from __future__ import annotations

import ast
import builtins
from dataclasses import dataclass

from .messages import t

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
        "scipy",
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


# Attributes that start with an underscore are a library's internals (`random._os` is the `os` module).
# These are the public ones that happen to start with one (namedtuple's API).
ALLOWED_PRIVATE_ATTRIBUTES = frozenset({"_asdict", "_replace", "_fields", "_make"})
# Names the platform's own setup uses to hand cases to the lesson (the learner has no reason to look).
RESERVED_PREFIX = "_QLP"
# Reading and writing files through NumPy: not an accident the `open` ban would catch.
FILE_ATTRIBUTES = frozenset(
    {"fromfile", "tofile", "savetxt", "loadtxt", "genfromtxt", "memmap", "open_memmap", "savez", "savez_compressed"}
)
# Names starting with `self` or `cls` may use their own underscore attributes (`self._cost`).
OWN_OBJECT_NAMES = frozenset({"self", "cls"})


@dataclass(frozen=True)
class GuardIssue:
    line: int
    message: str


class CodeRejected(Exception):
    """The code did not pass the static check."""

    def __init__(self, issues: list[GuardIssue]):
        super().__init__(issues[0].message if issues else "code rejected")
        self.issues = issues


def check(code: str) -> ast.Module:
    """Parses the code and returns the AST, or raises CodeRejected/SyntaxError."""
    tree = ast.parse(code, filename="<student>")
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
                for alias in node.names:
                    if alias.name.startswith("_"):
                        issues.append(GuardIssue(node.lineno, t("guard.private", name=alias.name)))
        elif isinstance(node, ast.Name):
            if node.id in FORBIDDEN_NAMES or node.id.startswith(RESERVED_PREFIX):
                issues.append(GuardIssue(node.lineno, t("guard.forbidden_name", name=node.id)))
            elif _is_dunder(node.id) and node.id != "__name__":
                issues.append(GuardIssue(node.lineno, t("guard.dunder", name=node.id)))
        elif isinstance(node, ast.Attribute):
            if _is_dunder(node.attr):
                issues.append(GuardIssue(node.lineno, t("guard.dunder", name=node.attr)))
            elif node.attr.startswith("_") and not _may_use_private(node):
                issues.append(GuardIssue(node.lineno, t("guard.private", name=node.attr)))
            elif node.attr in FILE_ATTRIBUTES:
                issues.append(GuardIssue(node.lineno, t("guard.files", name=node.attr)))

    if issues:
        issues.sort(key=lambda issue: issue.line)
        raise CodeRejected(issues)
    return tree


def _may_use_private(node: ast.Attribute) -> bool:
    if node.attr in ALLOWED_PRIVATE_ATTRIBUTES:
        return True
    return isinstance(node.value, ast.Name) and node.value.id in OWN_OBJECT_NAMES


def _check_module(name: str, line: int, issues: list[GuardIssue]) -> None:
    if any(part.startswith("_") for part in name.split(".")):
        issues.append(GuardIssue(line, t("guard.private", name=name)))
    root = name.split(".")[0]
    if root not in ALLOWED_IMPORTS:
        allowed = ", ".join(sorted(ALLOWED_IMPORTS))
        issues.append(GuardIssue(line, t("guard.module", name=root, allowed=allowed)))


def _is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def restricted_builtins() -> dict:
    """Builtins handed to the student's code (import limited to the allowed list)."""
    safe = {k: v for k, v in vars(builtins).items() if k not in FORBIDDEN_NAMES}
    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level or name.split(".")[0] not in ALLOWED_IMPORTS:
            raise ImportError(t("guard.module_short", name=name))
        return real_import(name, globals, locals, fromlist, level)

    safe["__import__"] = guarded_import
    return safe
