#!/usr/bin/env python3
"""Split optional IfcOpenShell Pyodide payloads into separate wheels."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import os
import re
import sys
import time
import zipfile
from email.parser import Parser
from pathlib import Path


MAIN_SHARED_OBJECT_RE = re.compile(r"(^|/)_ifcopenshell_wrapper(?:\.|$)")
PURE_PYTHON_PACKAGE_NAME = "ifcopenshell-pure-python"
PURE_PYTHON_PREFIXES = (
    "ifcopenshell/api/",
    "ifcopenshell/express/",
    "ifcopenshell/mvd/",
    "ifcopenshell/simple_spf/",
)


def wheel_parts(path: Path) -> tuple[str, str, str, str, str]:
    if path.suffix != ".whl":
        raise ValueError(f"not a wheel: {path}")
    stem = path.name[:-4]
    left, py_tag, abi_tag, platform_tag = stem.rsplit("-", 3)
    dist, version = left.rsplit("-", 1)
    return dist, version, py_tag, abi_tag, platform_tag


def safe_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower().strip("-")


def wheel_escape(value: str) -> str:
    return re.sub(r"[^\w\d.]+", "_", value, flags=re.UNICODE)


def wheel_version_escape(value: str) -> str:
    return re.sub(r"[^\w\d.+]+", "_", value, flags=re.UNICODE)


def dist_info_dir(name: str, version: str) -> str:
    return f"{wheel_escape(name)}-{wheel_version_escape(version)}.dist-info"


def sha256_record_value(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return "sha256=" + base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def make_info(name: str, *, source: zipfile.ZipInfo | None = None, mode: int | None = None) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name)
    if source is not None:
        info.date_time = source.date_time
        info.external_attr = source.external_attr
        info.comment = source.comment
        info.create_system = source.create_system
    else:
        info.date_time = time.localtime(time.time())[:6]
        info.external_attr = ((mode if mode is not None else 0o644) & 0xFFFF) << 16
        info.create_system = 3
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def write_record(zf: zipfile.ZipFile, entries: dict[str, bytes | None], record_name: str) -> None:
    rows: list[list[str]] = []
    for name in sorted(entries):
        data = entries[name]
        if name == record_name:
            rows.append([name, "", ""])
        elif data is None:
            raise ValueError(f"missing bytes for RECORD entry {name}")
        else:
            rows.append([name, sha256_record_value(data), str(len(data))])

    buf = io.StringIO(newline="")
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerows(rows)
    zf.writestr(make_info(record_name), buf.getvalue().encode("utf-8"))


def read_original_metadata(zf: zipfile.ZipFile) -> tuple[str, str, str]:
    metadata_names = [n for n in zf.namelist() if n.endswith(".dist-info/METADATA")]
    wheel_names = [n for n in zf.namelist() if n.endswith(".dist-info/WHEEL")]
    record_names = [n for n in zf.namelist() if n.endswith(".dist-info/RECORD")]
    if len(metadata_names) != 1 or len(wheel_names) != 1 or len(record_names) != 1:
        raise ValueError("expected exactly one METADATA, WHEEL, and RECORD in the source wheel")
    return metadata_names[0], wheel_names[0], record_names[0]


def shared_package_name(so_path: str) -> str:
    stem = Path(so_path).name.removesuffix(".so")
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-")
    return safe_name(stem)


def is_pure_python_split_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in PURE_PYTHON_PREFIXES)


def build_wheel(
    output_dir: Path,
    package_name: str,
    version: str,
    tag: str,
    root_is_purelib: bool,
    summary: str,
    payloads: list[tuple[zipfile.ZipInfo, bytes]],
    license_files: dict[str, bytes],
) -> Path:
    di = dist_info_dir(package_name, version)
    wheel_name = f"{wheel_escape(package_name)}-{wheel_version_escape(version)}-{tag}.whl"
    out = output_dir / wheel_name
    record_name = f"{di}/RECORD"
    entries: dict[str, bytes | None] = {}

    metadata = (
        "Metadata-Version: 2.4\n"
        f"Name: {package_name}\n"
        f"Version: {version}\n"
        f"Summary: {summary}\n"
        "License-File: COPYING\n"
        "License-File: COPYING.LESSER\n"
        "\n"
    ).encode("utf-8")
    wheel = (
        "Wheel-Version: 1.0\n"
        "Generator: split_pyodide_ifcopenshell_wheel.py\n"
        f"Root-Is-Purelib: {str(root_is_purelib).lower()}\n"
        f"Tag: {tag}\n"
        "\n"
    ).encode("utf-8")

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for info, data in payloads:
            zf.writestr(make_info(info.filename, source=info), data)
            entries[info.filename] = data

        metadata_name = f"{di}/METADATA"
        wheel_meta_name = f"{di}/WHEEL"
        zf.writestr(make_info(metadata_name), metadata)
        zf.writestr(make_info(wheel_meta_name), wheel)
        entries[metadata_name] = metadata
        entries[wheel_meta_name] = wheel

        for basename, data in license_files.items():
            name = f"{di}/licenses/{basename}"
            zf.writestr(make_info(name), data)
            entries[name] = data

        entries[record_name] = None
        write_record(zf, entries, record_name)
    return out


def rewrite_main_wheel(source: Path, target: Path, split_paths: set[str]) -> None:
    with zipfile.ZipFile(source) as zin, zipfile.ZipFile(
        target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zout:
        _, _, record_name = read_original_metadata(zin)
        entries: dict[str, bytes | None] = {}
        for info in zin.infolist():
            if info.filename in split_paths or info.filename == record_name:
                continue
            data = zin.read(info.filename)
            zout.writestr(make_info(info.filename, source=info), data)
            entries[info.filename] = data
        entries[record_name] = None
        write_record(zout, entries, record_name)


def verify_wheel(path: Path) -> None:
    with zipfile.ZipFile(path) as zf:
        zf.testzip()
        metadata_name, wheel_name, record_name = read_original_metadata(zf)
        Parser().parsestr(zf.read(metadata_name).decode("utf-8"))
        wheel_text = zf.read(wheel_name).decode("utf-8")
        if "Wheel-Version:" not in wheel_text or "Tag:" not in wheel_text:
            raise ValueError(f"invalid WHEEL metadata in {path}")

        record_rows = list(csv.reader(io.StringIO(zf.read(record_name).decode("utf-8"))))
        names = {row[0] for row in record_rows}
        missing = set(zf.namelist()) - names
        if missing:
            raise ValueError(f"{path} RECORD is missing entries: {sorted(missing)[:5]}")
        for name, digest, size in record_rows:
            if name == record_name:
                continue
            data = zf.read(name)
            if digest != sha256_record_value(data) or size != str(len(data)):
                raise ValueError(f"{path} RECORD mismatch for {name}")


def split_wheel(wheel_path: Path, output_dir: Path) -> None:
    wheel_path = wheel_path.expanduser().resolve()
    if not wheel_path.exists():
        raise FileNotFoundError(wheel_path)

    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    main_wheel_path = output_dir / wheel_path.name
    if main_wheel_path.resolve(strict=False) == wheel_path:
        raise ValueError("output directory must not point to the input wheel location")

    _, version, py_tag, abi_tag, platform_tag = wheel_parts(wheel_path)
    binary_tag = f"{py_tag}-{abi_tag}-{platform_tag}"
    pure_tag = "py3-none-any"

    with zipfile.ZipFile(wheel_path) as zf:
        file_infos = [info for info in zf.infolist() if not info.is_dir()]
        so_infos = [info for info in file_infos if info.filename.endswith(".so")]
        split_so_infos = [info for info in so_infos if not MAIN_SHARED_OBJECT_RE.search(Path(info.filename).name)]
        pure_python_infos = [info for info in file_infos if is_pure_python_split_path(info.filename)]
        if not split_so_infos and not pure_python_infos:
            raise RuntimeError("no secondary .so files or pure Python subpackages found to split")

        license_files = {
            Path(info.filename).name: zf.read(info.filename)
            for info in file_infos
            if ".dist-info/licenses/" in info.filename
        }
        split_so_payloads = [(info, zf.read(info.filename)) for info in split_so_infos]
        pure_python_payloads = [(info, zf.read(info.filename)) for info in pure_python_infos]

    created_wheels: list[Path] = []
    for info, data in split_so_payloads:
        package_name = shared_package_name(info.filename)
        created_wheels.append(
            build_wheel(
                output_dir,
                package_name,
                version,
                binary_tag,
                False,
                f"Pyodide shared library split from IfcOpenShell ({Path(info.filename).name}).",
                [(info, data)],
                license_files,
            )
        )

    if pure_python_payloads:
        created_wheels.append(
            build_wheel(
                output_dir,
                PURE_PYTHON_PACKAGE_NAME,
                version,
                pure_tag,
                True,
                "Pure Python subpackages split from IfcOpenShell.",
                pure_python_payloads,
                license_files,
            )
        )

    temp_main_wheel = output_dir / f".{wheel_path.name}.tmp"
    try:
        rewrite_main_wheel(
            wheel_path,
            temp_main_wheel,
            {info.filename for info, _ in split_so_payloads + pure_python_payloads},
        )
        verify_wheel(temp_main_wheel)
        for created in created_wheels:
            verify_wheel(created)
        os.replace(temp_main_wheel, main_wheel_path)
    finally:
        if temp_main_wheel.exists():
            temp_main_wheel.unlink()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract optional IfcOpenShell Pyodide payloads into separate wheel artifacts."
    )
    parser.add_argument("wheel", help="IfcOpenShell Pyodide wheel to split")
    parser.add_argument("output_dir", help="Directory for generated wheels")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    split_wheel(Path(args.wheel), Path(args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
