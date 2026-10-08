# /// script
# ///
"""Verify the artifacts produced by a native WASM build.

Used by `.github/workflows/build-ifcopenshell-native-wasm.yml` and by the
`docker/native-wasm.Dockerfile` mirror of it.
"""

import json
import sys
from pathlib import Path

DEFAULT_WASM_DIR = "ifcopenshell_build/Linux/wasm/build/ifcopenshell/build/ifcwrap/wasm"

EXPECTED_PLUGINS = {
    "schema": ["ifc2x3", "ifc4", "ifc4x3_add2"],
    "kernel": ["passthrough", "opencascade", "cgal", "cgalsimple", "manifold"],
    "tree": ["opencascade.brep", "opencascade.trianglebvh"],
    "mapping": ["ifc2x3", "ifc4", "ifc4x3_add2"],
    "document": [
        "xml.ifc2x3",
        "json.ifc2x3",
        "xml.ifc4",
        "json.ifc4",
        "xml.ifc4x3_add2",
        "json.ifc4x3_add2",
    ],
    "geometry_serializer": ["ttl", "obj", "glb", "stp", "igs", "svg"],
}

ARTIFACTS = [
    "ifcopenshell_wasm.wasm",
    "ifcopenshell_wasm.mjs",
    "ifcopenshell_wasm.node.mjs",
    "ifcopenshell_api.mjs",
    "ifcopenshell_api.d.ts",
    "ifcopenshell_plugins.json",
]


def main() -> int:
    wasm_dir = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_WASM_DIR)

    errors = []
    for name in ARTIFACTS:
        if not (wasm_dir / name).exists():
            errors.append(f"missing artifact: {name}")

    manifest_path = wasm_dir / "ifcopenshell_plugins.json"
    if not manifest_path.exists():
        errors.append(f"missing plugin manifest: {manifest_path}")
        report(errors)
        return 1

    manifest = json.loads(manifest_path.read_text())

    if set(manifest) != set(EXPECTED_PLUGINS):
        errors.append(f"unexpected plugin kinds: {sorted(set(manifest) ^ set(EXPECTED_PLUGINS))}")
    for kind, ids in EXPECTED_PLUGINS.items():
        expected = set(ids)
        actual = set(manifest.get(kind, {}))
        if expected - actual:
            errors.append(f"missing {kind} plugins: {sorted(expected - actual)}")
        if actual - expected:
            errors.append(f"unexpected {kind} plugins: {sorted(actual - expected)}")

    for entries in manifest.values():
        for entry in entries.values():
            if not (wasm_dir / entry["wasm"]).exists():
                errors.append(f"missing plugin artifact: {entry['wasm']}")

    if errors:
        report(errors)
        return 1

    print(f"Verified {len(ARTIFACTS)} artifacts and {sum(len(v) for v in manifest.values())} plugins.")
    return 0


def report(errors: list[str]) -> None:
    for error in errors:
        print(f"::error::{error}")
    print(f"{len(errors)} problem(s) found.", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
