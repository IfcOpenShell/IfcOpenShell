from pathlib import Path

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--bonsaiviewer",
        type=Path,
        help="Path to the BonsaiViewer executable to test, BonsaiViewer tests are skipped without it.",
    )
