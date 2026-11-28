# This file was generated with the assistance of an AI coding tool.

import re
import shutil
import subprocess
from pathlib import Path

import pytest

PACKAGE_DIR = Path(__file__).parent.parent


@pytest.mark.skipif(shutil.which("make") is None, reason="make is not installed")
def test_dist_target_copies_every_declared_module():
    pyproject = (PACKAGE_DIR / "pyproject.toml").read_text()
    declared = re.search(r"^py-modules\s*=\s*\[(.*?)\]", pyproject, re.MULTILINE).group(1)
    modules = {f"{name}.py" for name in re.findall(r'"([^"]+)"', declared)}
    assert len(modules) > 1

    dry_run = subprocess.run(
        ["make", "-n", "dist", "IS_STABLE=TRUE"], cwd=PACKAGE_DIR, capture_output=True, text=True, check=True
    )
    copied = {name for line in dry_run.stdout.splitlines() if line.startswith("cp -r ") for name in line.split()[2:-1]}
    assert modules <= copied
