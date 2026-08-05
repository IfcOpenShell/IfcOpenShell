#!/usr/bin/env python3
# /// script
# ///
# This file was generated with the assistance of an AI coding tool.
"""Order Pyodide wheel shared objects so wasm side modules load safely."""

from __future__ import annotations

import argparse
import os
import re
import tempfile
import zipfile
from pathlib import Path

SCHEMA_ORDER = {
    "ifc2x3": 0,
    "ifc4": 1,
    "ifc4x1": 2,
    "ifc4x2": 3,
    "ifc4x3": 4,
    "ifc4x3_add1": 5,
    "ifc4x3_add2": 6,
}

MAIN_SHARED_OBJECT_RE = re.compile(r"^_ifcopenshell_wrapper(?:\.|$)")
SCHEMA_PLUGIN_RE = re.compile(r"^ifcopenshell\.parse\.schema\.([^.]+)\.so$")
MAPPING_PLUGIN_RE = re.compile(r"^ifcopenshell\.geometry\.mapping\.([^.]+)\.so$")
DOCUMENT_PLUGIN_RE = re.compile(r"^ifcopenshell\.document\.[^.]+\.([^.]+)\.so$")
GEOMETRY_SERIALIZATION_PLUGIN_RE = re.compile(r"^ifcopenshell\.geometry\.serialization\.([^.]+)\.so$")


def schema_key(schema: str) -> tuple[int, str]:
    schema = schema.lower()
    return SCHEMA_ORDER.get(schema, len(SCHEMA_ORDER)), schema


def shared_object_sort_key(filename: str, index: int) -> tuple[int, tuple[int, str], str, int]:
    basename = Path(filename).name
    if MAIN_SHARED_OBJECT_RE.match(basename):
        return 0, schema_key(""), basename, index

    if match := SCHEMA_PLUGIN_RE.match(basename):
        return 1, schema_key(match.group(1)), basename, index

    if match := MAPPING_PLUGIN_RE.match(basename):
        return 2, schema_key(match.group(1)), basename, index

    if match := DOCUMENT_PLUGIN_RE.match(basename):
        return 3, schema_key(match.group(1)), basename, index

    if match := GEOMETRY_SERIALIZATION_PLUGIN_RE.match(basename):
        return 4, schema_key(match.group(1)), basename, index

    return 5, schema_key(""), basename, index


def ordered_infos(infos: list[zipfile.ZipInfo]) -> list[zipfile.ZipInfo]:
    shared_infos = [(index, info) for index, info in enumerate(infos) if info.filename.endswith(".so")]
    ordered_shared_infos = [
        info for index, info in sorted(shared_infos, key=lambda item: shared_object_sort_key(item[1].filename, item[0]))
    ]
    ordered_shared_iter = iter(ordered_shared_infos)
    return [next(ordered_shared_iter) if info.filename.endswith(".so") else info for info in infos]


def zip_info_for_write(source: zipfile.ZipInfo) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(source.filename)
    info.date_time = source.date_time
    info.compress_type = source.compress_type
    info.comment = source.comment
    info.create_system = source.create_system
    info.external_attr = source.external_attr
    info.extra = source.extra
    return info


def shared_object_names(infos: list[zipfile.ZipInfo]) -> list[str]:
    return [info.filename for info in infos if info.filename.endswith(".so")]


def rewrite_wheel(wheel: Path, ordered: list[zipfile.ZipInfo]) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{wheel.name}.", suffix=".tmp", dir=wheel.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        with zipfile.ZipFile(wheel) as zin, zipfile.ZipFile(
            temp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as zout:
            for info in ordered:
                zout.writestr(zip_info_for_write(info), zin.read(info))
        os.replace(temp_path, wheel)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def order_wheel(wheel: Path, check: bool) -> bool:
    wheel = wheel.resolve()
    if wheel.suffix != ".whl":
        raise ValueError(f"not a wheel: {wheel}")

    with zipfile.ZipFile(wheel) as zf:
        infos = zf.infolist()

    ordered = ordered_infos(infos)
    changed = shared_object_names(infos) != shared_object_names(ordered)
    if check:
        if changed:
            print(f"{wheel}: shared object order needs updating")
            return False
        print(f"{wheel}: shared object order is already valid")
        return True

    if changed:
        rewrite_wheel(wheel, ordered)
        print(f"{wheel}: reordered shared objects")
    else:
        print(f"{wheel}: shared object order is already valid")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path, help="Wheel to rewrite in place")
    parser.add_argument("--check", action="store_true", help="Only validate the current shared object order")
    args = parser.parse_args()

    return 0 if order_wheel(args.wheel, args.check) else 1


if __name__ == "__main__":
    raise SystemExit(main())
