from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Union

from .authored_spec import (
    AuthoredBindingSpec,
    MergedBindingSpec,
    load_authored_spec,
    load_merged_specs,
)
from .binding_ir import BindingIR, lower_binding_spec
from .binding_model import HandleSpec
from .c_backend import _render_cpp
from .c_header_rendering import _render_header
from .c_internal_header import _render_internal_header
from .clang_discovery import CompilationConfig, DiscoveryEnvironment
from .cpp_spec_frontend import (
    discover_cpp_spec_contract_headers,
    discover_cpp_spec_functions,
    discover_cpp_spec_handles,
    discover_cpp_spec_option_structs,
    discover_cpp_spec_result_structs,
    lower_cpp_spec_functions_to_calls,
    lower_cpp_spec_handles_to_specs,
    lower_cpp_spec_result_structs_to_specs,
)
from .debug import debug_log, debug_path

# Type alias for spec types
SourceBindingSpec = Union[AuthoredBindingSpec, MergedBindingSpec]


@dataclass(frozen=True)
class CppSpecConfig:
    path: Path
    namespace: str
    c_prefix: str | None = None
    handle_c_prefix: str | None = None


def _normalize_repeated_cpp_option(
    values: str | Sequence[str] | None,
    count: int,
    *,
    option_name: str,
    required: bool,
) -> tuple[str | None, ...]:
    if isinstance(values, str):
        normalized: tuple[str, ...] = (values,)
    else:
        normalized = tuple(values or ())
    if not normalized:
        if required:
            msg = f"{option_name} is required when cpp_spec_paths are provided"
            raise ValueError(msg)
        return (None,) * count
    if len(normalized) == 1:
        return normalized * count
    if len(normalized) != count:
        msg = f"{option_name} must be provided once or exactly once per C++ spec"
        raise ValueError(msg)
    return normalized


_EMPTY_ARG = "__IFCOPENSHELL_EMPTY__"


def _cpp_spec_configs(
    spec_paths: Sequence[Path],
    namespaces: str | Sequence[str] | None,
    c_prefixes: str | Sequence[str] | None,
    handle_c_prefixes: str | Sequence[str] | None = None,
) -> tuple[CppSpecConfig, ...]:
    namespace_values = _normalize_repeated_cpp_option(
        namespaces,
        len(spec_paths),
        option_name="cpp_spec_namespace",
        required=True,
    )
    c_prefix_values = _normalize_repeated_cpp_option(
        c_prefixes,
        len(spec_paths),
        option_name="cpp_spec_c_prefix",
        required=False,
    )
    handle_c_prefix_values = _normalize_repeated_cpp_option(
        handle_c_prefixes,
        len(spec_paths),
        option_name="cpp_spec_handle_c_prefix",
        required=False,
    )
    return tuple(
        CppSpecConfig(
            path=path,
            namespace=namespace,
            c_prefix=c_prefix,
            handle_c_prefix=("" if handle_c_prefix == _EMPTY_ARG else handle_c_prefix)
            or c_prefix,
        )
        for path, namespace, c_prefix, handle_c_prefix in zip(
            spec_paths, namespace_values, c_prefix_values, handle_c_prefix_values
        )
        if namespace is not None
    )


def _cpp_spec_public_header(spec_path: Path, include_dirs: tuple[Path, ...]) -> str:
    resolved = spec_path.resolve()
    for include_dir in include_dirs:
        try:
            return resolved.relative_to(include_dir.resolve()).as_posix()
        except ValueError:
            continue
    return spec_path.name


def _merge_cpp_specs(
    base: MergedBindingSpec,
    configs: Sequence[CppSpecConfig],
    *,
    discovery_include_dirs: tuple[Path, ...] = (),
    discovery_defines: tuple[str, ...] = (),
    discovery_clang_args: tuple[str, ...] = (),
) -> MergedBindingSpec:
    environment = _cpp_spec_environment(
        discovery_include_dirs=discovery_include_dirs,
        discovery_defines=discovery_defines,
        discovery_clang_args=discovery_clang_args,
    )
    handles = dict(base.handles)
    result_structs = dict(base.result_structs)
    option_structs = dict(getattr(base, "option_structs", {}))
    calls = list(base.functions)
    methods = list(base.methods)
    existing_c_names = {call.c_name for call in (*base.functions, *base.methods)}
    public_headers = list(base.public_headers)
    for config in configs:
        public_header = _cpp_spec_public_header(config.path, discovery_include_dirs)
        if public_header not in public_headers:
            public_headers.append(public_header)

        for handle_name, handle in lower_cpp_spec_handles_to_specs(
            discover_cpp_spec_handles(config.path, c_prefix=config.handle_c_prefix)
        ).items():
            if handle_name in handles and handles[handle_name] != handle:
                msg = f"C++ spec handle '{handle_name}' is declared with conflicting metadata"
                raise ValueError(msg)
            handles[handle_name] = handle
        for struct_name, struct in lower_cpp_spec_result_structs_to_specs(
            discover_cpp_spec_result_structs(config.path, config.namespace),
            handles,
            environment=environment,
            translation_unit=config.path,
        ).items():
            if struct_name in result_structs and result_structs[struct_name] != struct:
                msg = f"C++ spec result struct '{struct_name}' is declared with conflicting metadata"
                raise ValueError(msg)
            result_structs[struct_name] = struct
        functions = discover_cpp_spec_functions(
            environment,
            config.path,
            config.namespace,
            contract_headers=discover_cpp_spec_contract_headers(
                config.path, discovery_include_dirs
            ),
        )
        for struct_name, struct in discover_cpp_spec_option_structs(
            environment,
            config.path,
            functions,
            handles,
            result_structs,
            c_prefix=config.c_prefix,
        ).items():
            if struct_name in option_structs and option_structs[struct_name] != struct:
                msg = f"C++ spec option struct '{struct_name}' is declared with conflicting metadata"
                raise ValueError(msg)
            option_structs[struct_name] = struct
        for call in lower_cpp_spec_functions_to_calls(
            functions,
            handles,
            result_structs,
            option_structs,
            c_prefix=config.c_prefix,
        ):
            if call.c_name in existing_c_names:
                calls = [
                    existing for existing in calls if existing.c_name != call.c_name
                ]
                methods = [
                    existing for existing in methods if existing.c_name != call.c_name
                ]
            else:
                existing_c_names.add(call.c_name)
            if call.receiver is None:
                calls.append(call)
            else:
                methods.append(call)

    return MergedBindingSpec(
        module=base.module,
        c_prefix=base.c_prefix,
        public_headers=tuple(public_headers),
        handles=handles,
        result_structs=result_structs,
        option_structs=option_structs,
        functions=tuple(calls),
        methods=tuple(methods),
        discovery_diagnostics=base.discovery_diagnostics,
    )


def write_c_abi(
    spec: BindingIR,
    header_out: Path,
    cpp_out: Path,
    internal_header_out: Path | None = None,
) -> tuple[Path, Path, Path]:
    header_out.parent.mkdir(parents=True, exist_ok=True)
    cpp_out.parent.mkdir(parents=True, exist_ok=True)
    header_out.write_text(_render_header(spec), encoding="utf-8")
    cpp_out.write_text(_render_cpp(spec, header_out.name), encoding="utf-8")
    if internal_header_out is None:
        internal_header_out = cpp_out.with_name(header_out.stem + "_internal.hpp")
    internal_header_out.parent.mkdir(parents=True, exist_ok=True)
    internal_header_out.write_text(
        _render_internal_header(spec, header_out.name), encoding="utf-8"
    )
    return header_out.resolve(), cpp_out.resolve(), internal_header_out.resolve()


def build_binding_ir(
    spec_paths: Sequence[Path],
    *,
    module: str = "ifcopenshell",
    c_prefix: str = "ifcopenshell",
    discovery_include_dirs: tuple[Path, ...] = (),
    discovery_defines: tuple[str, ...] = (),
    discovery_clang_args: tuple[str, ...] = (),
    cpp_spec_paths: Sequence[Path] = (),
    cpp_spec_namespace: str | Sequence[str] | None = None,
    cpp_spec_c_prefix: str | Sequence[str] | None = None,
    cpp_spec_handle_c_prefix: str | Sequence[str] | None = None,
) -> BindingIR:
    if cpp_spec_paths and not spec_paths:
        if not cpp_spec_namespace:
            msg = "cpp_spec_namespace is required when only cpp_spec_paths are provided"
            raise ValueError(msg)
        configs = _cpp_spec_configs(
            cpp_spec_paths,
            cpp_spec_namespace,
            cpp_spec_c_prefix or c_prefix,
            cpp_spec_handle_c_prefix,
        )
        environment = _cpp_spec_environment(
            discovery_include_dirs=discovery_include_dirs,
            discovery_defines=discovery_defines,
            discovery_clang_args=discovery_clang_args,
        )
        handles = {}
        result_structs = {}
        option_structs = {}
        calls = []
        existing_c_names: set[str] = set()
        for config in configs:
            for handle_name, handle in lower_cpp_spec_handles_to_specs(
                discover_cpp_spec_handles(config.path, c_prefix=config.handle_c_prefix)
            ).items():
                if handle_name in handles and handles[handle_name] != handle:
                    msg = f"C++ spec handle '{handle_name}' is declared with conflicting metadata"
                    raise ValueError(msg)
                handles[handle_name] = handle
            for struct_name, struct in lower_cpp_spec_result_structs_to_specs(
                discover_cpp_spec_result_structs(config.path, config.namespace),
                handles,
                environment=environment,
                translation_unit=config.path,
            ).items():
                if (
                    struct_name in result_structs
                    and result_structs[struct_name] != struct
                ):
                    msg = f"C++ spec result struct '{struct_name}' is declared with conflicting metadata"
                    raise ValueError(msg)
                result_structs[struct_name] = struct
            functions = discover_cpp_spec_functions(
                environment,
                config.path,
                config.namespace,
                contract_headers=discover_cpp_spec_contract_headers(
                    config.path, discovery_include_dirs
                ),
            )
            for struct_name, struct in discover_cpp_spec_option_structs(
                environment,
                config.path,
                functions,
                handles,
                result_structs,
                c_prefix=config.c_prefix,
            ).items():
                if (
                    struct_name in option_structs
                    and option_structs[struct_name] != struct
                ):
                    msg = f"C++ spec option struct '{struct_name}' is declared with conflicting metadata"
                    raise ValueError(msg)
                option_structs[struct_name] = struct
            for call in lower_cpp_spec_functions_to_calls(
                functions,
                handles,
                result_structs,
                option_structs,
                c_prefix=config.c_prefix,
            ):
                if call.c_name in existing_c_names:
                    msg = f"C++ spec export '{call.c_name}' duplicates an existing generated C symbol"
                    raise ValueError(msg)
                existing_c_names.add(call.c_name)
                calls.append(call)

        return lower_binding_spec(
            MergedBindingSpec(
                module=module,
                c_prefix=c_prefix,
                public_headers=tuple(
                    _cpp_spec_public_header(config.path, discovery_include_dirs)
                    for config in configs
                ),
                handles=handles,
                result_structs=result_structs,
                option_structs=option_structs,
                functions=tuple(calls),
                methods=(),
                discovery_diagnostics=(),
            )
        )

    if not spec_paths:
        msg = "At least one spec path is required"
        raise ValueError(msg)
    if len(spec_paths) == 1 and not cpp_spec_paths:
        return lower_binding_spec(
            load_authored_spec(
                spec_paths[0],
                discovery_include_dirs=discovery_include_dirs,
                discovery_defines=discovery_defines,
                discovery_clang_args=discovery_clang_args,
            )
        )

    cpp_spec_configs = (
        _cpp_spec_configs(
            cpp_spec_paths,
            cpp_spec_namespace,
            cpp_spec_c_prefix,
            cpp_spec_handle_c_prefix,
        )
        if cpp_spec_paths
        else ()
    )
    cpp_spec_handles: dict[str, HandleSpec] = {}
    for config in cpp_spec_configs:
        for handle_name, handle in lower_cpp_spec_handles_to_specs(
            discover_cpp_spec_handles(config.path, c_prefix=config.handle_c_prefix)
        ).items():
            if (
                handle_name in cpp_spec_handles
                and cpp_spec_handles[handle_name] != handle
            ):
                msg = f"C++ spec handle '{handle_name}' is declared with conflicting metadata"
                raise ValueError(msg)
            cpp_spec_handles[handle_name] = handle
    merged_spec = load_merged_specs(
        list(spec_paths),
        module,
        c_prefix,
        discovery_include_dirs=discovery_include_dirs,
        discovery_defines=discovery_defines,
        discovery_clang_args=discovery_clang_args,
        existing_handles=cpp_spec_handles,
    )
    if cpp_spec_configs:
        merged_spec = _merge_cpp_specs(
            merged_spec,
            cpp_spec_configs,
            discovery_include_dirs=discovery_include_dirs,
            discovery_defines=discovery_defines,
            discovery_clang_args=discovery_clang_args,
        )
    return lower_binding_spec(merged_spec)


def generate(
    spec_path: Path,
    header_out: Path,
    cpp_out: Path,
    internal_header_out: Path | None = None,
    discovery_include_dirs: tuple[Path, ...] = (),
    discovery_defines: tuple[str, ...] = (),
    discovery_clang_args: tuple[str, ...] = (),
) -> tuple[Path, Path, Path]:
    debug_log(
        "c_backend.generate.start",
        f"spec={debug_path(spec_path)} header_out={debug_path(header_out)} cpp_out={debug_path(cpp_out)} internal_header_out={debug_path(internal_header_out)}",
    )
    result = write_c_abi(
        build_binding_ir(
            [spec_path],
            discovery_include_dirs=discovery_include_dirs,
            discovery_defines=discovery_defines,
            discovery_clang_args=discovery_clang_args,
        ),
        header_out,
        cpp_out,
        internal_header_out,
    )
    debug_log("c_backend.generate.done", f"spec={debug_path(spec_path)}")
    return result


def generate_merged(
    spec_paths: list[Path],
    module: str,
    c_prefix: str,
    header_out: Path,
    cpp_out: Path,
    internal_header_out: Path | None = None,
    discovery_include_dirs: tuple[Path, ...] = (),
    discovery_defines: tuple[str, ...] = (),
    discovery_clang_args: tuple[str, ...] = (),
    cpp_spec_paths: list[Path] | None = None,
    cpp_spec_namespace: str | Sequence[str] | None = None,
    cpp_spec_c_prefix: str | Sequence[str] | None = None,
    cpp_spec_handle_c_prefix: str | Sequence[str] | None = None,
) -> tuple[Path, Path, Path]:
    """Generate bindings from multiple specs merged together."""
    debug_log(
        "c_backend.generate_merged.start",
        f"specs={len(spec_paths)} header_out={debug_path(header_out)} cpp_out={debug_path(cpp_out)} internal_header_out={debug_path(internal_header_out)}",
    )
    result = write_c_abi(
        build_binding_ir(
            spec_paths,
            module=module,
            c_prefix=c_prefix,
            discovery_include_dirs=discovery_include_dirs,
            discovery_defines=discovery_defines,
            discovery_clang_args=discovery_clang_args,
            cpp_spec_paths=tuple(cpp_spec_paths or ()),
            cpp_spec_namespace=cpp_spec_namespace,
            cpp_spec_c_prefix=cpp_spec_c_prefix,
            cpp_spec_handle_c_prefix=cpp_spec_handle_c_prefix,
        ),
        header_out,
        cpp_out,
        internal_header_out,
    )
    debug_log("c_backend.generate_merged.done", f"module={module}")
    return result


def _cpp_spec_environment(
    *,
    discovery_include_dirs: tuple[Path, ...] = (),
    discovery_defines: tuple[str, ...] = (),
    discovery_clang_args: tuple[str, ...] = (),
) -> DiscoveryEnvironment:
    return DiscoveryEnvironment(
        compilation=CompilationConfig(
            include_dirs=discovery_include_dirs,
            defines=discovery_defines,
            clang_args=("-x", "c++", "-std=c++17", *discovery_clang_args),
        ),
    )


def generate_cpp_specs(
    spec_paths: list[Path],
    namespace: str | Sequence[str],
    module: str,
    c_prefix: str,
    header_out: Path,
    cpp_out: Path,
    internal_header_out: Path | None = None,
    discovery_include_dirs: tuple[Path, ...] = (),
    discovery_defines: tuple[str, ...] = (),
    discovery_clang_args: tuple[str, ...] = (),
    function_c_prefix: str | Sequence[str] | None = None,
    handle_c_prefix: str | Sequence[str] | None = None,
) -> tuple[Path, Path, Path]:
    """Generate bindings from explicit C++ spec translation units."""
    result = write_c_abi(
        build_binding_ir(
            (),
            module=module,
            c_prefix=c_prefix,
            discovery_include_dirs=discovery_include_dirs,
            discovery_defines=discovery_defines,
            discovery_clang_args=discovery_clang_args,
            cpp_spec_paths=spec_paths,
            cpp_spec_namespace=namespace,
            cpp_spec_c_prefix=function_c_prefix,
            cpp_spec_handle_c_prefix=handle_c_prefix,
        ),
        header_out,
        cpp_out,
        internal_header_out,
    )
    debug_log(
        "c_backend.generate_cpp_specs.done", f"specs={len(spec_paths)} module={module}"
    )
    return result
