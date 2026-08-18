from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .binding_ir import BindingIR, lower_binding_spec
from .binding_model import HandleSpec
from .clang_discovery import CompilationConfig, DiscoveryEnvironment
from .cpp_spec_frontend import (
    discover_cpp_spec_functions,
    discover_cpp_spec_handles,
    discover_cpp_spec_methods,
    discover_cpp_spec_policy,
    discover_cpp_spec_result_structs,
    discover_cpp_spec_selected_functions,
    lower_cpp_spec_functions_to_calls,
    lower_cpp_spec_handles_to_specs,
    lower_cpp_spec_methods_to_calls,
    lower_cpp_spec_policy_to_calls,
    lower_cpp_spec_result_structs_to_specs,
)
from .discovery_policy import MergedBindingSpec


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
    calls = list(base.functions)
    methods = list(base.methods)
    existing_c_names = {call.c_name for call in (*base.functions, *base.methods)}
    public_headers = list(base.public_headers)
    selected_calls = []
    adapter_calls = []
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
        )
        functions += discover_cpp_spec_selected_functions(
            environment,
            config.path,
        )
        selected_calls.extend(
            lower_cpp_spec_methods_to_calls(
                environment,
                config.path,
                discover_cpp_spec_methods(config.path),
                handles,
            )
        )
        selected_calls.extend(
            lower_cpp_spec_policy_to_calls(
                environment,
                config.path,
                discover_cpp_spec_policy(config.path, handles),
                handles,
                config.c_prefix or base.c_prefix,
            )
        )
        adapter_calls.extend(
            lower_cpp_spec_functions_to_calls(
                functions,
                handles,
                result_structs,
                c_prefix=config.c_prefix,
            )
        )

    for call in (*selected_calls, *adapter_calls):
        if call.c_name in existing_c_names:
            calls = [existing for existing in calls if existing.c_name != call.c_name]
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
        functions=tuple(calls),
        methods=tuple(methods),
    )


def build_binding_ir(
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
    if not cpp_spec_paths:
        msg = "At least one C++ spec path is required"
        raise ValueError(msg)

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
    merged_spec = MergedBindingSpec(
        module=module,
        c_prefix=c_prefix,
        public_headers=(),
        handles=cpp_spec_handles,
        result_structs={},
        functions=(),
        methods=(),
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
