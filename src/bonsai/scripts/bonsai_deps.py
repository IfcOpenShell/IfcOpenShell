"""Clone or update Bonsai external dependencies.

Must be run from the repository root.
"""

import shlex
import subprocess
from pathlib import Path

DEPS = [
    ("https://projects.blender.org/pioverfour/sun_position.git", "sun_position"),
    ("https://github.com/kevancress/MeasureIt_ARCH", "MeasureIt_ARCH"),
    ("https://github.com/nortikin/sverchok.git", "sverchok"),
]


def run(command: list[str]) -> None:
    print("$", shlex.join(command))
    subprocess.check_call(command)


base = Path("src/bonsai/external_dependencies")
base.mkdir(parents=True, exist_ok=True)

for url, name in DEPS:
    path = base / name
    if not path.exists():
        run(["git", "clone", url, str(path)])
    else:
        run(["git", "-C", str(path), "pull", "--rebase"])
