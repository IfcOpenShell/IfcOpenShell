from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from wrappergen.clang_frontend import build_module_model
    from wrappergen.config import CompilationConfig, IgnoreConfig, WrapperConfig
    from wrappergen.emit import write_module_outputs
else:
    from .clang_frontend import build_module_model
    from .config import CompilationConfig, IgnoreConfig, WrapperConfig
    from .emit import write_module_outputs


def _existing_directories(paths: list[Path]) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []
    for path in paths:
        resolved = str(path.resolve())
        if path.is_dir() and resolved not in seen:
            seen.add(resolved)
            results.append(resolved)
    return results


def _discover_headers(src_ifcparse: Path) -> list[str]:
    return [str(path.resolve()) for path in sorted(src_ifcparse.glob("*.h")) if path.parent.name != "schemas"]


def _discover_boost_include_dirs() -> list[Path]:
    candidates: list[Path] = []
    prefix = Path(sys.prefix)
    candidates.extend(
        [
            prefix / "Library" / "include",
            prefix / "include",
        ]
    )

    executable = Path(sys.executable).resolve()
    conda_root = executable.parents[2] if len(executable.parents) >= 3 else None
    if conda_root is None:
        return candidates

    pkgs = conda_root / "pkgs"
    if not pkgs.is_dir():
        return candidates

    for pattern in ("libboost-headers-*", "boost-cpp-*"):
        for package_dir in sorted(pkgs.glob(pattern), reverse=True):
            include_dir = package_dir / "Library" / "include"
            if (include_dir / "boost" / "lexical_cast.hpp").is_file():
                candidates.append(include_dir)
    return candidates


def build_default_wrapper_config(repo_root: Path) -> WrapperConfig:
    src_ifcparse = repo_root / "src" / "ifcparse"
    include_dirs = _existing_directories([src_ifcparse, *_discover_boost_include_dirs()])
    return WrapperConfig(
        module_name="ifcopenshell_experimental",
        c_prefix="ifcopenshell",
        api_header_name="ifcopenshell_experimental_c_api.h",
        api_implementation_name="ifcopenshell_experimental_c_api.cpp",
        extension_source_name="_ifcopenshell_experimental.cpp",
        python_source_name="ifcopenshell_experimental.py",
        allowed_namespaces=["ifcopenshell", "express"],
        enum_names={"ifcopenshell::filetype": "FileType"},
        parameter_names={"type": "filetype", "read_only": "readonly"},
        class_handle_kinds={"ifcopenshell::file": "shared_ptr"},
        class_owner_types={
            "express::Base": "ifcopenshell::file",
            "express::Entity": "ifcopenshell::file",
            "express::Select": "ifcopenshell::file",
            "express::DeclaredType": "ifcopenshell::file",
        },
        type_adapters={
            "std::string": "string",
            "int": "integer",
            "size_t": "integer",
            "std::size_t": "integer",
            "unsigned int": "integer",
            "uint32_t": "integer",
            "bool": "bool",
            "void": "void",
        },
        ignore=IgnoreConfig(
            namespaces=["ifcopenshell::impl"],
            classes=[],
            enums=[],
            methods=[],
        ),
        compilation=CompilationConfig(
            headers=_discover_headers(src_ifcparse),
            include_dirs=include_dirs,
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an experimental C API, CPython module, and Python facade for ifcparse."
    )
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Repository root that contains src/ifcparse",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "generated"),
        help="Directory that will receive the generated files",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    repo_root = Path(arguments.repo_root).resolve()
    output_dir = Path(arguments.output_dir).resolve()
    model = build_module_model(build_default_wrapper_config(repo_root))
    write_module_outputs(model, output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
