from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python print_walls.py path/to/model.ifc")
        return 1

    generated_dir = Path(__file__).resolve().parents[1] / "generated"
    if str(generated_dir) not in sys.path:
        sys.path.insert(0, str(generated_dir))

    import ifcopenshell_experimental as ifx

    model = ifx.file.with_path(sys.argv[1])
    for wall in model.instances_by_type("IfcWall"):
        print(f"#{wall.id()} {wall.declaration.name()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
