from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .config import WrapperConfig
from .conventions import (
    cpp_leaf_name,
    enum_adapter_name,
    handle_adapter_name,
    is_enum_adapter,
    normalize_cpp_type,
    normalize_identifier,
    pascal_case,
    resolve_cpp_type_key,
    safe_python_identifier,
    sequence_adapter_name,
    strip_pointer,
)
from .model import CallableModel, ClassModel, EnumModel, EnumValueModel, ModuleModel, ParameterModel


def _require_clang():
    try:
        from clang import cindex
    except ImportError as exc:
        raise RuntimeError(
            "clang.cindex is required for wrapper generation. Install the Clang Python bindings "
            "and ensure libclang is discoverable before rerunning the generator."
        ) from exc
    return cindex


@dataclass(slots=True)
class _ParameterSpec:
    has_default: bool
    default_cpp_value: str | None


def _iter_children(cursor):
    for child in cursor.get_children():
        yield child
        yield from _iter_children(child)


def _qualified_name(cursor) -> str:
    cindex = _require_clang()
    accepted = {
        cindex.CursorKind.NAMESPACE,
        cindex.CursorKind.CLASS_DECL,
        cindex.CursorKind.STRUCT_DECL,
        cindex.CursorKind.ENUM_DECL,
    }
    names: list[str] = []
    current = cursor
    while current is not None and current.kind != cindex.CursorKind.TRANSLATION_UNIT:
        if current.kind in accepted and current.spelling:
            names.append(current.spelling)
        current = current.semantic_parent
    return "::".join(reversed(names))


def _join_cpp_tokens(tokens: list[str]) -> str:
    return "".join(tokens).strip()


def _parse_parameter_specs(cursor) -> list[_ParameterSpec]:
    parameters = list(cursor.get_arguments())
    if not parameters:
        return []

    tokens = [token.spelling for token in cursor.get_tokens()]
    try:
        start = tokens.index("(") + 1
    except ValueError:
        return [_ParameterSpec(False, None) for _ in parameters]

    depth = 0
    current: list[str] = []
    groups: list[list[str]] = []
    for token in tokens[start:]:
        if token in {"(", "<", "["}:
            depth += 1
        elif token in {")", ">", "]"}:
            if token == ")" and depth == 0:
                if current:
                    groups.append(current[:])
                break
            depth = max(depth - 1, 0)
        elif token == "," and depth == 0:
            groups.append(current[:])
            current = []
            continue
        current.append(token)
    if current:
        groups.append(current)

    specs: list[_ParameterSpec] = []
    for index, _ in enumerate(parameters):
        group = groups[index] if index < len(groups) else []
        if "=" not in group:
            specs.append(_ParameterSpec(False, None))
            continue
        equals = group.index("=")
        default_tokens = group[equals + 1 :]
        specs.append(_ParameterSpec(True, _join_cpp_tokens(default_tokens) or None))
    return specs


def _build_translation_unit(config: WrapperConfig, header: Path):
    cindex = _require_clang()
    index = cindex.Index.create()
    arguments: list[str] = []
    if config.compilation.compile_commands:
        database = cindex.CompilationDatabase.fromDirectory(str(Path(config.compilation.compile_commands).resolve()))
        candidates = [header.with_suffix(".cpp"), header.with_suffix(".cc"), header.with_suffix(".cxx")]
        for candidate in candidates:
            commands = database.getCompileCommands(str(candidate.resolve()))
            if not commands:
                continue
            command = list(commands[0].arguments)
            filtered: list[str] = []
            skip_next = False
            for argument in command[1:]:
                if skip_next:
                    skip_next = False
                    continue
                if argument in {"-c", "/c"}:
                    continue
                if argument in {"-o", "/Fo", "/Fd"}:
                    skip_next = True
                    continue
                if argument.endswith((".cpp", ".cc", ".cxx", ".c")):
                    continue
                filtered.append(argument)
            arguments.extend(filtered)
            break
    if not arguments:
        arguments.extend(config.compilation.clang_args)
        arguments.extend(f"-I{Path(include_dir).resolve()}" for include_dir in config.compilation.include_dirs)
        arguments.extend(f"-D{define}" for define in config.compilation.defines)
    return index.parse(str(header.resolve()), args=arguments)


def _cursor_file_path(cursor) -> Path | None:
    file = cursor.location.file
    if file is None:
        return None
    try:
        return Path(file.name).resolve()
    except OSError:
        return None


def _is_in_allowed_headers(cursor, allowed_headers: set[Path]) -> bool:
    path = _cursor_file_path(cursor)
    return path in allowed_headers if path is not None else False


def _is_in_allowed_namespace(cpp_name: str, config: WrapperConfig) -> bool:
    if not config.allowed_namespaces:
        return True
    return any(cpp_name == namespace or cpp_name.startswith(f"{namespace}::") for namespace in config.allowed_namespaces)


def _matches_ignore(cpp_name: str, ignored: list[str]) -> bool:
    return cpp_name in ignored


def _matches_ignored_namespace(cpp_name: str, ignored_namespaces: list[str]) -> bool:
    return any(cpp_name == namespace or cpp_name.startswith(f"{namespace}::") for namespace in ignored_namespaces)


def _has_export_macro(cursor, macro_name: str) -> bool:
    return any(token.spelling == macro_name for token in cursor.get_tokens())


def _is_top_level_type(cursor) -> bool:
    cindex = _require_clang()
    parent = cursor.semantic_parent
    return parent is not None and parent.kind in {cindex.CursorKind.TRANSLATION_UNIT, cindex.CursorKind.NAMESPACE}


def _collect_enum_cursors(translation_units, config: WrapperConfig, allowed_headers: set[Path]) -> dict[str, object]:
    cindex = _require_clang()
    enums: dict[str, object] = {}
    for translation_unit in translation_units:
        for cursor in _iter_children(translation_unit.cursor):
            if cursor.kind != cindex.CursorKind.ENUM_DECL:
                continue
            if not cursor.is_definition():
                continue
            if not _is_top_level_type(cursor):
                continue
            if not _is_in_allowed_headers(cursor, allowed_headers):
                continue
            cpp_name = _qualified_name(cursor)
            if not cpp_name or not _is_in_allowed_namespace(cpp_name, config):
                continue
            if _matches_ignored_namespace(cpp_name, config.ignore.namespaces):
                continue
            if _matches_ignore(cpp_name, config.ignore.enums):
                continue
            enums[normalize_cpp_type(cpp_name)] = cursor
    return enums


def _collect_class_cursors(translation_units, config: WrapperConfig, allowed_headers: set[Path]) -> dict[str, object]:
    cindex = _require_clang()
    classes: dict[str, object] = {}
    for translation_unit in translation_units:
        for cursor in _iter_children(translation_unit.cursor):
            if cursor.kind not in {cindex.CursorKind.CLASS_DECL, cindex.CursorKind.STRUCT_DECL}:
                continue
            if not cursor.is_definition():
                continue
            if not _is_top_level_type(cursor):
                continue
            if not _is_in_allowed_headers(cursor, allowed_headers):
                continue
            cpp_name = _qualified_name(cursor)
            if not cpp_name or not _is_in_allowed_namespace(cpp_name, config):
                continue
            if _matches_ignored_namespace(cpp_name, config.ignore.namespaces):
                continue
            if _matches_ignore(cpp_name, config.ignore.classes):
                continue
            if config.require_exported_classes and not _has_export_macro(cursor, config.export_macro):
                continue
            classes[normalize_cpp_type(cpp_name)] = cursor
    return classes


def _normalized_type_adapters(config: WrapperConfig) -> dict[str, str]:
    return {normalize_cpp_type(cpp_type): adapter for cpp_type, adapter in config.type_adapters.items()}


def _python_class_name(cpp_name: str, config: WrapperConfig) -> str:
    return config.class_names.get(cpp_name, cpp_leaf_name(cpp_name))


def _python_enum_name(cpp_name: str, config: WrapperConfig) -> str:
    return config.enum_names.get(cpp_name, pascal_case(cpp_leaf_name(cpp_name)))


def _parameter_python_name(raw_name: str, index: int, config: WrapperConfig) -> str:
    source = raw_name or f"arg{index}"
    return safe_python_identifier(normalize_identifier(config.parameter_names.get(source, source)))


def _owner_cpp_name(cpp_name: str, config: WrapperConfig) -> str | None:
    return config.class_owner_types.get(cpp_name)


def _handle_kind(cpp_name: str, config: WrapperConfig) -> str:
    return config.class_handle_kinds.get(cpp_name, config.default_class_handle_kind)


def _resolve_parameter_adapter(
    cpp_type: str,
    scalar_adapters: dict[str, str],
    enum_cursors: dict[str, object],
) -> str | None:
    canonical = normalize_cpp_type(cpp_type)
    if canonical in scalar_adapters:
        return scalar_adapters[canonical]
    enum_key = resolve_cpp_type_key(cpp_type, set(enum_cursors))
    if enum_key is not None:
        return enum_adapter_name(enum_key)
    return None


def _vector_inner_type(cpp_type: str) -> str | None:
    canonical = normalize_cpp_type(cpp_type)
    prefix = "std::vector<"
    if not canonical.startswith(prefix) or not canonical.endswith(">"):
        return None
    return canonical[len(prefix) : -1]


def _resolve_return_adapter(
    cpp_type: str,
    scalar_adapters: dict[str, str],
    enum_cursors: dict[str, object],
    class_models_by_cpp: dict[str, ClassModel],
) -> str | None:
    canonical = normalize_cpp_type(cpp_type)
    if canonical in scalar_adapters:
        return scalar_adapters[canonical]
    enum_key = resolve_cpp_type_key(cpp_type, set(enum_cursors))
    if enum_key is not None:
        return enum_adapter_name(enum_key)
    vector_inner = _vector_inner_type(cpp_type)
    if vector_inner:
        sequence_key = resolve_cpp_type_key(vector_inner, set(class_models_by_cpp))
        if sequence_key is not None:
            return sequence_adapter_name(sequence_key)
    pointee = resolve_cpp_type_key(strip_pointer(cpp_type), set(class_models_by_cpp))
    if pointee is not None:
        target = class_models_by_cpp[pointee]
        if canonical.endswith("*") and target.handle_kind == "shared_ptr":
            return None
        return handle_adapter_name(pointee)
    return None


def _python_default_value(
    cpp_value: str | None,
    adapter: str,
    enum_py_names: dict[str, str],
) -> str | None:
    if cpp_value is None:
        return None
    if adapter == "bool":
        if cpp_value == "true":
            return "True"
        if cpp_value == "false":
            return "False"
        return None
    if adapter == "integer":
        return cpp_value if cpp_value.lstrip("-").isdigit() else None
    if adapter == "string":
        return cpp_value if cpp_value.startswith(("\"", "'")) else None
    if is_enum_adapter(adapter):
        enum_name = enum_py_names.get(adapter.split(":", 1)[1])
        if enum_name is None:
            return None
        return f"{enum_name}.{cpp_value.rsplit('::', 1)[-1]}"
    return None


def _build_parameter_models(
    cursor,
    config: WrapperConfig,
    scalar_adapters: dict[str, str],
    enum_cursors: dict[str, object],
) -> list[ParameterModel] | None:
    parameter_specs = _parse_parameter_specs(cursor)
    parameter_models: list[ParameterModel] = []
    for index, parameter in enumerate(cursor.get_arguments()):
        adapter = _resolve_parameter_adapter(parameter.type.spelling, scalar_adapters, enum_cursors)
        if adapter is None:
            return None
        spec = parameter_specs[index] if index < len(parameter_specs) else _ParameterSpec(False, None)
        parameter_models.append(
            ParameterModel(
                name=_parameter_python_name(parameter.spelling, index, config),
                cpp_name=parameter.spelling or f"arg{index}",
                cpp_type=parameter.type.spelling,
                adapter=adapter,
                has_default=spec.has_default,
                default_cpp_value=spec.default_cpp_value,
            )
        )
    return parameter_models


def _is_deleted(cursor) -> bool:
    tokens = [token.spelling for token in cursor.get_tokens()]
    return "=" in tokens and "delete" in tokens


def _is_copy_or_move_constructor(cursor, owner_cpp_name: str) -> bool:
    parameters = list(cursor.get_arguments())
    if len(parameters) != 1:
        return False
    return strip_pointer(parameters[0].type.spelling) == normalize_cpp_type(owner_cpp_name)


def _constructor_py_name(parameters: list[ParameterModel], minimum_arity: int) -> str:
    if minimum_arity == 0:
        return "create"
    required = parameters[:minimum_arity]
    suffix = "_".join(parameter.name for parameter in required)
    return safe_python_identifier(f"with_{suffix}")


def _finalize_overload_names(callables: list[CallableModel]) -> None:
    groups: dict[str, list[CallableModel]] = defaultdict(list)
    for callable_model in callables:
        groups[callable_model.py_name].append(callable_model)
    for group in groups.values():
        if len(group) == 1:
            continue
        for index, callable_model in enumerate(group, start=1):
            parameter_suffix = "_".join(parameter.name for parameter in callable_model.parameters)
            if callable_model.kind == "constructor":
                callable_model.py_name = f"{callable_model.py_name}_{parameter_suffix}" if parameter_suffix else f"{callable_model.py_name}_overload_{index}"
            else:
                callable_model.py_name = f"{callable_model.py_name}_with_{parameter_suffix}" if parameter_suffix else f"{callable_model.py_name}_overload_{index}"
                callable_model.c_name = normalize_identifier(callable_model.py_name)


def _deduplicate_callables(callables: list[CallableModel]) -> list[CallableModel]:
    unique: list[CallableModel] = []
    seen: set[tuple[str, str, str, tuple[str, ...]]] = set()
    for callable_model in callables:
        key = (
            callable_model.kind,
            callable_model.cpp_name,
            callable_model.return_adapter,
            tuple(normalize_cpp_type(parameter.cpp_type) for parameter in callable_model.parameters),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(callable_model)
    return unique


def _discover_constructors(
    class_cursor,
    owner: ClassModel,
    config: WrapperConfig,
    scalar_adapters: dict[str, str],
    enum_cursors: dict[str, object],
) -> list[CallableModel]:
    cindex = _require_clang()
    constructors: list[CallableModel] = []
    for child in class_cursor.get_children():
        if child.kind != cindex.CursorKind.CONSTRUCTOR:
            continue
        if child.access_specifier != cindex.AccessSpecifier.PUBLIC:
            continue
        if _is_deleted(child) or _is_copy_or_move_constructor(child, owner.cpp_name):
            continue
        parameters = _build_parameter_models(child, config, scalar_adapters, enum_cursors)
        if parameters is None:
            continue
        callable_model = CallableModel(
            kind="constructor",
            owner_cpp_name=owner.cpp_name,
            owner_py_name=owner.py_name,
            cpp_name=cpp_leaf_name(owner.cpp_name),
            py_name="create",
            c_name="new",
            return_cpp_type=owner.cpp_name,
            return_adapter=handle_adapter_name(owner.cpp_name),
            parameters=parameters,
        )
        callable_model.py_name = _constructor_py_name(parameters, callable_model.minimum_arity)
        constructors.append(callable_model)
    return constructors


def _discover_methods(
    class_cursor,
    owner: ClassModel,
    config: WrapperConfig,
    scalar_adapters: dict[str, str],
    enum_cursors: dict[str, object],
    class_models_by_cpp: dict[str, ClassModel],
) -> list[CallableModel]:
    cindex = _require_clang()
    methods: list[CallableModel] = []
    for child in class_cursor.get_children():
        if child.kind != cindex.CursorKind.CXX_METHOD:
            continue
        if child.access_specifier != cindex.AccessSpecifier.PUBLIC:
            continue
        if child.spelling.startswith("operator") or _is_deleted(child):
            continue
        if child.is_static_method():
            continue
        qualified_name = f"{owner.cpp_name}::{child.spelling}"
        if _matches_ignore(qualified_name, config.ignore.methods):
            continue
        return_adapter = _resolve_return_adapter(child.result_type.spelling, scalar_adapters, enum_cursors, class_models_by_cpp)
        if return_adapter is None:
            continue
        parameters = _build_parameter_models(child, config, scalar_adapters, enum_cursors)
        if parameters is None:
            continue
        methods.append(
            CallableModel(
                kind="method",
                owner_cpp_name=owner.cpp_name,
                owner_py_name=owner.py_name,
                cpp_name=child.spelling,
                py_name=safe_python_identifier(normalize_identifier(child.spelling)),
                c_name=normalize_identifier(child.spelling),
                return_cpp_type=child.result_type.spelling,
                return_adapter=return_adapter,
                parameters=parameters,
            )
        )
    return methods


def _build_enum_model(cpp_name: str, cursor, config: WrapperConfig) -> EnumModel:
    py_name = _python_enum_name(cpp_name, config)
    c_name = default_c_name = f"{config.c_prefix}_{normalize_identifier(py_name)}_t"
    values: list[EnumValueModel] = []
    for child in cursor.get_children():
        if child.spelling:
            values.append(
                EnumValueModel(
                    name=child.spelling,
                    c_name=f"{default_c_name.upper()}_{child.spelling}",
                    value=child.enum_value,
                )
            )
    return EnumModel(cpp_name=cpp_name, py_name=py_name, c_name=c_name, values=values)


def build_module_model(config: WrapperConfig) -> ModuleModel:
    translation_units = [_build_translation_unit(config, Path(header)) for header in config.compilation.headers]
    allowed_headers = {Path(header).resolve() for header in config.compilation.headers}

    enum_cursors = _collect_enum_cursors(translation_units, config, allowed_headers)
    class_cursors = _collect_class_cursors(translation_units, config, allowed_headers)
    scalar_adapters = _normalized_type_adapters(config)

    class_models_by_cpp: dict[str, ClassModel] = {}
    for normalized_cpp_name, cursor in class_cursors.items():
        cpp_name = _qualified_name(cursor)
        owner_cpp_name = _owner_cpp_name(cpp_name, config)
        owner_py_name = _python_class_name(owner_cpp_name, config) if owner_cpp_name else None
        class_models_by_cpp[normalized_cpp_name] = ClassModel(
            cpp_name=cpp_name,
            py_name=_python_class_name(cpp_name, config),
            handle_kind=_handle_kind(cpp_name, config),
            owner_cpp_name=owner_cpp_name,
            owner_py_name=owner_py_name,
        )

    for normalized_cpp_name, cursor in class_cursors.items():
        owner = class_models_by_cpp[normalized_cpp_name]
        owner.callables.extend(_discover_constructors(cursor, owner, config, scalar_adapters, enum_cursors))
        owner.callables.extend(_discover_methods(cursor, owner, config, scalar_adapters, enum_cursors, class_models_by_cpp))
        owner.callables = _deduplicate_callables(owner.callables)
        _finalize_overload_names(owner.callables)

    used_class_names: set[str] = set()
    used_enum_names: set[str] = set()
    for class_model in class_models_by_cpp.values():
        if class_model.callables:
            used_class_names.add(normalize_cpp_type(class_model.cpp_name))
        if class_model.owner_cpp_name:
            used_class_names.add(normalize_cpp_type(class_model.owner_cpp_name))
        for callable_model in class_model.callables:
            if is_enum_adapter(callable_model.return_adapter):
                used_enum_names.add(callable_model.return_adapter.split(":", 1)[1])
            if callable_model.return_adapter.startswith("handle:"):
                used_class_names.add(callable_model.return_adapter.split(":", 1)[1])
            if callable_model.return_adapter.startswith("sequence:"):
                used_class_names.add(callable_model.return_adapter.split(":", 1)[1])
            for parameter in callable_model.parameters:
                if is_enum_adapter(parameter.adapter):
                    used_enum_names.add(parameter.adapter.split(":", 1)[1])

    selected_classes: list[ClassModel] = []
    for normalized_cpp_name, class_model in class_models_by_cpp.items():
        if normalized_cpp_name in used_class_names:
            selected_classes.append(class_model)

    enum_models_by_cpp: dict[str, EnumModel] = {}
    for normalized_cpp_name in sorted(used_enum_names):
        cursor = enum_cursors.get(normalized_cpp_name)
        if cursor is None:
            continue
        cpp_name = _qualified_name(cursor)
        enum_models_by_cpp[normalized_cpp_name] = _build_enum_model(cpp_name, cursor, config)

    enum_py_names = {normalized_cpp_name: model.py_name for normalized_cpp_name, model in enum_models_by_cpp.items()}
    for class_model in selected_classes:
        for callable_model in class_model.callables:
            for parameter in callable_model.parameters:
                if parameter.has_default:
                    parameter.default_python_value = _python_default_value(
                        parameter.default_cpp_value,
                        parameter.adapter,
                        enum_py_names,
                    )

    if not any(class_model.callables for class_model in selected_classes):
        raise RuntimeError("No supported public classes or methods were discovered in the configured headers")

    source_headers: list[str] = []
    seen_headers: set[str] = set()
    for class_model in selected_classes:
        cursor = class_cursors.get(normalize_cpp_type(class_model.cpp_name))
        header = _cursor_file_path(cursor) if cursor is not None else None
        if header is not None and header.name not in seen_headers:
            seen_headers.add(header.name)
            source_headers.append(header.name)
    for normalized_cpp_name in enum_models_by_cpp:
        cursor = enum_cursors.get(normalized_cpp_name)
        header = _cursor_file_path(cursor) if cursor is not None else None
        if header is not None and header.name not in seen_headers:
            seen_headers.add(header.name)
            source_headers.append(header.name)

    return ModuleModel(
        module_name=config.module_name,
        c_prefix=config.c_prefix,
        api_header_name=config.api_header_name,
        api_implementation_name=config.api_implementation_name,
        extension_source_name=config.extension_source_name,
        python_source_name=config.python_source_name,
        source_headers=source_headers,
        classes=selected_classes,
        enums=list(enum_models_by_cpp.values()),
    )
