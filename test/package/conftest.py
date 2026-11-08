from pathlib import Path

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--bonsaiviewer",
        type=Path,
        help="Path to the BonsaiViewer executable to test, BonsaiViewer tests are skipped without it.",
    )
    parser.addoption(
        "--not-bundled",
        action="store_true",
        help=(
            "Package was built without CREATE_BUNDLE, which installs plug-ins to the lib dir, "
            "not to `site-packages/ifcopenshell`."
        ),
    )
