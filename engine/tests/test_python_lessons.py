"""Lições sem circuito (framework "python"): execução e tabela de variáveis."""

from qlp_engine import worker


def test_python_run_returns_the_learner_variables():
    code = (
        "import numpy as np\n"
        "z = 1 + 2j\n"
        "v = np.array([3, 4]) / 5\n"
        "M = np.eye(2)\n"
        "n = 3\n"
        "def helper():\n"
        "    return 1\n"
        "_hidden = 7\n"
        "big = np.zeros(1000)\n"
        "print('ok')\n"
    )
    result = worker.handle({"type": "run", "code": code, "framework": "python"})
    assert result["ok"], result
    assert result["steps"] == [] and result["snapshots"] == [] and result["stdout"] == "ok\n"
    rows = {row["name"]: row for row in result["variables"]}
    assert list(rows) == ["z", "v", "M", "n"]  # sem módulos, funções, privadas ou arrays grandes
    assert rows["z"]["value"] == "1.+2.j" and rows["z"]["type"] == "complex"
    assert rows["v"]["type"] == "array 2" and "0.6" in rows["v"]["value"]
    assert rows["M"]["type"] == "array 2×2"


def test_python_run_reports_errors_with_the_line():
    result = worker.handle({"type": "run", "code": "x = 1\ny = x / 0\n", "framework": "python"})
    assert result["ok"] is False and result["error"]["line"] == 2
