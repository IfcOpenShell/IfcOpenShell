import subprocess
import sys
from pathlib import Path

import ifcopenshell

directory = Path(__file__).parent


def normalize_header(f: ifcopenshell.file) -> None:
    f.header.file_name.time_stamp = "1970-01-01T00:00:00"
    f.header.file_name.preprocessor_version = "IfcOpenShell"
    f.header.file_name.originating_system = "IfcOpenShell"


if __name__ == "__main__":
    for path in directory.glob("*.ifc"):
        path.unlink()

    for path in sorted(directory.glob("generate_*.py")):
        print(f"=== {path.name} ===")
        subprocess.run([sys.executable, str(path)], cwd=directory, check=True)
