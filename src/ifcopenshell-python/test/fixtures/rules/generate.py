import subprocess
import sys
from pathlib import Path

directory = Path(__file__).parent

if __name__ == "__main__":
    for path in directory.glob("*.ifc"):
        path.unlink()

    for path in sorted(directory.glob("generate_*.py")):
        print(f"=== {path.name} ===")
        subprocess.run([sys.executable, str(path)], cwd=directory, check=True)
