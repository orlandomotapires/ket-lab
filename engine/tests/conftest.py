from pathlib import Path

import pytest

from qlp_engine.content import ContentLibrary

CONTENT_DIR = Path(__file__).resolve().parents[2] / "content"


@pytest.fixture(scope="session")
def library() -> ContentLibrary:
    return ContentLibrary(CONTENT_DIR)
