# This file was generated with the assistance of an AI coding tool.
#
# Runs every Python program that the documentation includes snippets from.
#
#   cd docs/ifcopenshell/examples
#   python -m pytest

import functools
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
MODELS = ROOT / "models"

# The model each directory's programs are run against, as in CMakeLists.txt.
GROUPS = {
    "hello_world": MODELS / "hello_world.ifc",
    "code_examples": MODELS / "AC20-FZK-Haus.ifc",
    "geometry_processing": MODELS / "AC20-FZK-Haus.ifc",
    "geometry_creation": MODELS / "AC20-FZK-Haus.ifc",
    "geometry_tree": MODELS / "AC20-FZK-Haus.ifc",
    "schema_querying": MODELS / "AC20-FZK-Haus.ifc",
}

EXAMPLES = sorted(
    (program, model)
    for directory, model in GROUPS.items()
    if (ROOT / directory).is_dir()
    for program in (ROOT / directory).glob("*.py")
    if not program.name.startswith("_")
)


@functools.cache
def installed_version() -> str:
    command = [sys.executable, "-c", "import ifcopenshell; print(ifcopenshell.version)"]
    return subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip()


def version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", version)[:3])


@pytest.mark.parametrize(
    ("program", "model"),
    EXAMPLES,
    ids=[program.relative_to(ROOT).as_posix() for program, _ in EXAMPLES],
)
def test_example(program: Path, model: Path, tmp_path: Path):
    required = re.search(r"^# Requires IfcOpenShell ([\d.]+)", program.read_text(encoding="utf-8"), re.MULTILINE)
    if required and version_tuple(installed_version()) < version_tuple(required[1]):
        pytest.skip(f"needs IfcOpenShell {required[1]}, {installed_version()} is installed")
    result = subprocess.run(
        [sys.executable, str(program), str(model)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, result.stdout + result.stderr
