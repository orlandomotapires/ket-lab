"""The static check: accident prevention with clear messages, plus the bypasses the audit listed."""

import pytest

from ket_lab_engine import guard, tracer


def rejected(code):
    with pytest.raises(guard.CodeRejected) as info:
        guard.check(code)
    return info.value.issues[0].message


@pytest.mark.parametrize("code, fragment", [
    ("import random\nrandom._os.listdir('.')\n", "underscore"),
    ("import numpy as np\nnp._core\n", "underscore"),
    ("import numpy as np\nx = np.ones(2)\nx._private\n", "underscore"),
    ("from random import _os\n", "underscore"),
    ("import numpy._core\n", "underscore"),
    ("x = _KET_LAB_INPUT\n", "_KET_LAB_INPUT"),
    ("x = _KET_LAB_SECRET\n", "not available"),
    ("print(__builtins__)\n", "internal"),
    ("x = (1).__class__\n", "internal"),
    ("import numpy as np\nnp.savetxt('f', [1])\n", "files"),
    ("import numpy as np\nnp.ones(2).tofile('f')\n", "files"),
    ("import numpy as np\nnp.memmap('f')\n", "files"),
    ("open('f')\n", "not available"),
    ("import os\n", "not available"),
    ("getattr(1, 'real')\n", "not available"),
    ("globals()\n", "not available"),
])
def test_bypasses_are_rejected_with_a_readable_message(code, fragment):
    assert fragment in rejected(code)


@pytest.mark.parametrize("code", [
    "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n",
    "import numpy as np\nprint(np.linalg.norm([3, 4]), np.pi)\n",
    "class Box:\n    def __init__(self):\n        self._cost = 1\n    def get(self):\n        return self._cost\nprint(Box().get())\n",
    "from collections import namedtuple\nP = namedtuple('P', 'x y')\np = P(1, 2)\nprint(p._asdict(), p._replace(x=3), P._fields)\n",
    "if __name__ == '__main__':\n    print(1)\n",
    "import random\nrandom.seed(1)\nprint(random.random() < 1)\n",
    "_ = 3\nfor _i in range(2):\n    pass\n",
])
def test_ordinary_code_passes(code):
    guard.check(code)


def test_the_learner_cannot_read_the_hidden_cases():
    setup = "_secret = 'hidden'\ndef reveal():\n    return _secret\n"
    execution = tracer.execute("x = reveal()\n", hidden_setup=setup, inputs={"_KET_LAB_INPUT": {"s": "101"}}, trace=False, require_circuit=False)
    assert execution.namespace["x"] == "hidden"  # helpers still work through their own globals
    assert "_secret" not in execution.namespace and "_KET_LAB_INPUT" not in execution.namespace
    # the lesson's own check.py can still see them
    assert execution.full_namespace()["_KET_LAB_INPUT"] == {"s": "101"}
    with pytest.raises(tracer.UserCodeError) as info:
        tracer.execute("print(_KET_LAB_INPUT)\n", hidden_setup=setup, inputs={"_KET_LAB_INPUT": 1}, trace=False, require_circuit=False)
    assert info.value.kind == "guard"


def test_setup_public_names_reach_the_learner():
    execution = tracer.execute("y = N + 1\n", hidden_setup="N = 15\n", trace=False, require_circuit=False)
    assert execution.namespace["y"] == 16


def test_no_lesson_leaks_its_secret_to_learner_code(library):
    """Every oracle lesson: the learner's namespace holds no private name and no _KET_LAB_* value."""
    from ket_lab_engine.validation import _first_case

    for lesson_id in library.lesson_ids:
        bundle = library.validation_bundle(lesson_id)
        if not bundle.get("hidden_setup"):
            continue
        inputs = _first_case(bundle["validation"]) or library.control_inputs(lesson_id, None)
        execution = tracer.execute("", bundle["hidden_setup"], inputs, trace=False, require_circuit=False)
        assert not [name for name in execution.namespace if name.startswith("_") and name not in ("__name__", "__builtins__")], lesson_id
