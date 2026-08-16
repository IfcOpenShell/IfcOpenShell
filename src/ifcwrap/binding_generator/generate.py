"""Generate the low-level IfcOpenShell C binding surface."""

from __future__ import annotations

import argparse
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .c_backend import render_c_abi
from .debug import debug_log
from .pipeline import build_binding_ir
from .targets.wasm.backend import render_export_list, render_wasm_bindings


@dataclass(frozen=True)
class ProductionSourceSet:
    cpp_specs: tuple[Path, ...]
    cpp_namespaces: tuple[str, ...]
    function_prefixes: tuple[str, ...]
    handle_prefixes: tuple[str, ...]

    @classmethod
    def from_spec_dir(cls, spec_dir: Path) -> ProductionSourceSet:
        return cls(
            cpp_specs=(
                spec_dir / "cpp" / "ifcparse.hpp",
                spec_dir / "cpp" / "ifcgeom.hpp",
            ),
            cpp_namespaces=(
                "ifcparse::bindings",
                "ifcgeom::bindings",
            ),
            function_prefixes=(
                "ifcopenshell_parse",
                "ifcopenshell_geom",
            ),
            handle_prefixes=("ifcopenshell", "ifcopenshell_geom"),
        )


@dataclass(frozen=True)
class GenerationConfig:
    sources: ProductionSourceSet
    c_output_dir: Path
    wasm_output_dir: Path | None = None
    discovery_include_dirs: tuple[Path, ...] = ()
    discovery_defines: tuple[str, ...] = ()
    discovery_clang_args: tuple[str, ...] = ()


@dataclass(frozen=True)
class Artifact:
    name: str
    path: Path
    content: str


def write_if_different(path: Path, content: str) -> bool:
    """Atomically write normalized UTF-8 content, preserving identical timestamps."""
    path = path.resolve()
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    data = normalized.encode("utf-8")
    try:
        if path.read_bytes() == data:
            return False
    except FileNotFoundError:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", dir=path.parent
        )
        temporary = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return True


def generate_all(config: GenerationConfig) -> tuple[Artifact, ...]:
    debug_log("pipeline.discovery.start", "full IfcOpenShell source set")
    ir = build_binding_ir(
        module="ifcopenshell",
        c_prefix="ifcopenshell",
        discovery_include_dirs=config.discovery_include_dirs,
        discovery_defines=config.discovery_defines,
        discovery_clang_args=config.discovery_clang_args,
        cpp_spec_paths=config.sources.cpp_specs,
        cpp_spec_namespace=config.sources.cpp_namespaces,
        cpp_spec_c_prefix=config.sources.function_prefixes,
        cpp_spec_handle_c_prefix=config.sources.handle_prefixes,
    )
    debug_log("pipeline.discovery.done", f"ir={id(ir)} calls={len(ir.calls)}")
    if ir.abi is None:
        raise RuntimeError("BindingIR finalization did not produce an ABI contract")
    metadata = ir.abi
    debug_log("pipeline.finalize.done", f"ir={id(ir)} abi={id(metadata)}")

    c_dir = config.c_output_dir.resolve()
    debug_log("pipeline.emit.c", f"ir={id(ir)}")
    c_artifacts = render_c_abi(ir)
    header = c_artifacts["ifcopenshell_api.h"]
    cpp = c_artifacts["ifcopenshell_api.cpp"]
    internal = c_artifacts["ifcopenshell_api_internal.hpp"]
    artifacts = [
        Artifact("c-header", c_dir / "ifcopenshell_api.h", header),
        Artifact("c-source", c_dir / "ifcopenshell_api.cpp", cpp),
        Artifact(
            "c-internal-header", c_dir / "ifcopenshell_api_internal.hpp", internal
        ),
    ]
    if config.wasm_output_dir is not None:
        wasm_dir = config.wasm_output_dir.resolve()
        debug_log("pipeline.emit.wasm", f"ir={id(ir)} abi={id(metadata)}")
        javascript, declarations = render_wasm_bindings(metadata)
        artifacts.extend(
            (
                Artifact("wasm-module", wasm_dir / "ifcopenshell_api.mjs", javascript),
                Artifact(
                    "wasm-exports",
                    wasm_dir / "ifcopenshell_exports.txt",
                    render_export_list(metadata),
                ),
                Artifact(
                    "wasm-declarations",
                    wasm_dir / "ifcopenshell_api.d.ts",
                    declarations,
                ),
            )
        )
    for artifact in artifacts:
        changed = write_if_different(artifact.path, artifact.content)
        print(
            f"{artifact.name}:{artifact.path.resolve()}:{'updated' if changed else 'unchanged'}"
        )
    return tuple(artifacts)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-dir", type=Path, required=True)
    parser.add_argument("--c-output-dir", type=Path, required=True)
    parser.add_argument("--wasm-output-dir", type=Path)
    parser.add_argument(
        "--discovery-include-dir", type=Path, action="append", default=[]
    )
    parser.add_argument("--discovery-define", action="append", default=[])
    parser.add_argument("--discovery-clang-arg", action="append", default=[])
    return parser


def main() -> int:
    args = _parser().parse_args()
    generate_all(
        GenerationConfig(
            sources=ProductionSourceSet.from_spec_dir(args.spec_dir.resolve()),
            c_output_dir=args.c_output_dir,
            wasm_output_dir=args.wasm_output_dir,
            discovery_include_dirs=tuple(args.discovery_include_dir),
            discovery_defines=tuple(args.discovery_define),
            discovery_clang_args=tuple(args.discovery_clang_arg),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
