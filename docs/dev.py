# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell Contributors
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

"""Rebuild the documentation page you are editing and reload the browser.

The C++, Python, and TypeScript API references stay as they were from the last
full build. Run ``python -m sphinx -M html . _build`` when those need to be
regenerated.
"""

import os
import subprocess
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent


def main() -> int:
    os.environ["DOCS_DEV"] = "1"
    port = "8080"
    if "--port" in sys.argv:
        port = sys.argv[sys.argv.index("--port") + 1]
    os.environ["DOCS_DEV_BASE"] = f"http://127.0.0.1:{port}"
    os.chdir(DOCS)
    if not (DOCS / "_build" / "html" / "index.html").is_file():
        print(
            "No HTML build yet. From this directory, run:\n"
            "    python -m sphinx -M html . _build",
            file=sys.stderr,
        )
        return 1
    command = [
        sys.executable,
        "-m",
        "sphinx_autobuild",
        ".",
        "_build/html",
        "-d",
        "_build/doctrees",
        "--host",
        "127.0.0.1",
        "--port",
        "8080",
        "--open-browser",
        "--ignore",
        str(DOCS / "output" / "api"),
        "--ignore",
        str(DOCS / "output" / "doxygen"),
        "--ignore",
        str(DOCS / "autoapi"),
        *sys.argv[1:],
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
