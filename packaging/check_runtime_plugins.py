#!/usr/bin/env python3
"""Fail a packaging run when runtime plugins are missing from the produced artifact.

IfcOpenShell 0.9 splits the toolkit into shared libraries that are loaded *by
name* at runtime (``ifcopenshell::plugin``) instead of being linked against. A
dependency scanner such as ``dumpbin /dependents`` or ``ldd`` therefore cannot
see them, so a packaging step that only follows link dependencies produces an
archive that imports and then dies with ``RuntimeError: No schema named IFC4``
(#9423, #9431). Nothing verified the produced artifact, so the regression
shipped in every published Windows package.

The plugin families below are derived from the build definitions:

    ifcopenshell_parse_schema_ifc<schema>      src/ifcparse/CMakeLists.txt
    ifcopenshell_geometry_mapping_ifc<schema>  src/ifcgeom/mapping/CMakeLists.txt
    ifcopenshell_geometry_writer_ifc<schema>   src/ifcgeom/serialization/schema/CMakeLists.txt
    ifcopenshell_document_xml_ifc<schema>      src/serializers/schema_dependent/CMakeLists.txt
    ifcopenshell_document_json_ifc<schema>     src/serializers/schema_dependent/CMakeLists.txt

Each iterates ``SCHEMA_VERSIONS`` (cmake/CMakeLists.txt), whose value differs
between builds: the WASM default is a three schema subset and a caller may pass
its own list. The set of schemas is therefore never hardcoded here, it is read
back out of the artifact.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

# Plugin basenames carry no platform prefix and use underscores, see
# decorated_basename() in src/plugin/plugin.cpp. Core shared libraries instead
# keep the dotted `ifcopenshell.` names and the platform `lib` prefix.
#
# Family name -> filename prefix, one entry per per-schema plugin family.
PER_SCHEMA_FAMILIES = {
    "parse_schema": "ifcopenshell_parse_schema_ifc",
    "geometry_mapping": "ifcopenshell_geometry_mapping_ifc",
    "geometry_writer": "ifcopenshell_geometry_writer_ifc",
    "document_xml": "ifcopenshell_document_xml_ifc",
    "document_json": "ifcopenshell_document_json_ifc",
}

# Without these no IFC file can be opened at all, so their absence is always a bug.
REQUIRED_FAMILIES = ("parse_schema",)

LIBRARY_SUFFIXES = (".so", ".dll", ".dylib", ".pyd")


def _basename(name: str) -> str:
    return Path(name.replace("\\", "/")).name.lower()


def _stem(name: str) -> str:
    """Basename without the platform `lib` prefix and without any suffix chain."""
    return _basename(name).removeprefix("lib").split(".", 1)[0]


def _is_library(name: str) -> bool:
    parts = _basename(name).split(".")[1:]
    return any(f".{part}" in LIBRARY_SUFFIXES for part in parts)


def classify(names: list[str]) -> dict[str, dict[str, str]]:
    """Map each per-schema family to ``{schema: filename}`` as found in the artifact."""
    found: dict[str, dict[str, str]] = {family: {} for family in PER_SCHEMA_FAMILIES}
    for name in names:
        if not _is_library(name):
            continue
        stem = _stem(name)
        for family, prefix in PER_SCHEMA_FAMILIES.items():
            if stem.startswith(prefix):
                found[family][stem.removeprefix(prefix)] = _basename(name)
    return found


def needs_schema_plugins(names: list[str]) -> bool:
    """Whether the artifact carries an IfcOpenShell core that parses IFC files.

    Deliberately narrow: a package that only ships an unrelated plugin (the
    ``svgfill`` executable bundles ``ifcopenshell_geometry_svgfill`` and nothing
    else) never opens an IFC file and must not be failed.
    """
    triggers = ("ifcopenshell_document_rdb",) + tuple(PER_SCHEMA_FAMILIES.values())
    for name in names:
        if not _is_library(name):
            continue
        base = _basename(name).removeprefix("lib")
        stem = _stem(name)
        if stem.startswith("_ifcopenshell_wrapper"):
            return True
        if base.startswith(("ifcopenshell.parse", "ifcopenshell.geometry")):
            return True
        if stem.startswith(triggers):
            return True
    return False


def _suffix_hint(found: dict[str, dict[str, str]]) -> str:
    for filenames in found.values():
        for filename in filenames.values():
            if "." in filename:
                return filename.split(".", 1)[1]
    return "so"


def problems(names: list[str]) -> list[str]:
    """Return a list of readable problems, empty when the artifact is complete."""
    if not needs_schema_plugins(names):
        return []

    found = classify(names)
    schemas = sorted({schema for filenames in found.values() for schema in filenames})
    suffix = _suffix_hint(found)
    issues = []

    for family in REQUIRED_FAMILIES:
        if not found[family]:
            issues.append(
                f"no {PER_SCHEMA_FAMILIES[family]}* library present. These plugins are loaded by "
                "name at runtime, so a link dependency scan cannot discover them and they have to "
                "be collected explicitly."
            )

    for family, filenames in found.items():
        if not filenames:
            continue
        missing = [schema for schema in schemas if schema not in filenames]
        if missing:
            expected = ", ".join(f"{PER_SCHEMA_FAMILIES[family]}{schema}.{suffix}" for schema in missing)
            issues.append(f"{family} was built for {sorted(filenames)} but these are missing: {expected}")

    return issues


def check(names: list[str], description: str) -> None:
    """Raise ``RuntimeError`` naming the missing files if the artifact is incomplete."""
    issues = problems(names)
    if issues:
        raise RuntimeError(
            f"{description} is missing IfcOpenShell runtime plugins:\n" + "\n".join(f"  - {issue}" for issue in issues)
        )


def names_in(path: Path) -> list[str]:
    if path.is_dir():
        return [str(item.relative_to(path)) for item in path.rglob("*") if item.is_file() or item.is_symlink()]
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            return archive.namelist()
    raise RuntimeError(f"{path} is neither a directory nor a zip archive")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="+", type=Path, help="Directories or zip archives to check.")
    args = parser.parse_args()

    failed = False
    for path in args.paths:
        try:
            check(names_in(path), str(path))
        except RuntimeError as error:
            print(error, file=sys.stderr)
            failed = True
        else:
            print(f"{path}: runtime plugins OK")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
