from __future__ import annotations

import re
from dataclasses import dataclass, field as dataclass_field, replace
from pathlib import Path

from .binding_model import (
    CallSpec,
    HandleSpec,
    OptionStructFieldSpec,
    OptionStructSpec,
    ParamSpec,
    ResultStructFieldSpec,
    ResultStructSpec,
    TypeSpec,
)
from .clang_discovery import (
    DiscoveredCppType,
    DiscoveredFunction,
    DiscoveredMethod,
    DiscoveryEnvironment,
    discover_namespace_functions,
    discover_public_fields,
    discover_public_methods,
)
from .contract_discovery import (
    _clean_doc_comment,
    _has_default,
    _leading_annotations,
    _param_name,
    _split_params,
    _strip_comments,
    discover_marked_functions_in_headers,
)
from .debug import debug_log
from .discovery_policy import (
    CcomponentsAccessorSpec,
    DiscoveryChildrenSpec,
    DiscoveryClassSpec,
    DiscoveryConstructorSpec,
    DiscoveryOverloadSpec,
    DiscoverySpec,
    HandleListAccessorsSpec,
    MethodAtAccessorSpec,
    VariantAccessorsSpec,
    VariantAccessorTypeSpec,
    _cpp_type_names_match,
    _direct_method_policy_operation,
    _discover_constructor_calls,
    _discover_method_calls,
    _handle_list_accessor_calls,
    _infer_method_signature,
    _infer_param_type,
    _infer_return_type,
    _normalize_cpp_type,
    _select_overload,
)
from .policy_ir import (
    BoolOutParamPolicyOp,
    DirectFunctionPolicyOp,
    SpecMethodFunctionPolicyOp,
)
from .semantic_types import (
    OptionalSemanticType,
    RecordSemanticType,
    SequenceSemanticType,
    VariantSemanticType,
    analyze_cpp_type,
    semantic_leaf_type,
    semantic_sequence_alias,
    semantic_sequence_depth,
    semantic_sequence_lengths,
)


@dataclass(frozen=True)
class CppSpecFunction:
    name: str
    namespace: str
    discovered: DiscoveredFunction
    return_annotations: frozenset[str]
    param_annotations: dict[str, frozenset[str]]
    param_defaults: dict[str, bool]
    receiver: str | None = None
    doc: str | None = None
    public_module: str | None = None


@dataclass(frozen=True)
class CppSpecHandle:
    name: str
    cpp_type: str
    c_type: str
    destructor: str
    ptr_type: str = "raw"
    empty_check: str | None = None


@dataclass(frozen=True)
class CppSpecResultStruct:
    name: str
    cpp_type: str
    c_type: str
    fields: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CppSpecMethod:
    handle: str
    cpp_name: str
    expose_as: str
    params: tuple[str, ...]


@dataclass
class _CppClassPolicy:
    handle: str
    translation_unit: str
    discover_fields: bool = False
    include_inherited_fields: bool = False
    exclude: list[str] = dataclass_field(default_factory=list)
    rename: dict[str, str] = dataclass_field(default_factory=dict)
    discover_has_fields: bool = False
    discover_as_item: bool = False
    extra_fields: dict[str, str] = dataclass_field(default_factory=dict)
    field_setters: list[str] = dataclass_field(default_factory=list)
    method_sizes: dict[str, str] = dataclass_field(default_factory=dict)
    method_at_accessors: list[MethodAtAccessorSpec] = dataclass_field(default_factory=list)
    discover_children: DiscoveryChildrenSpec | None = None
    array_pair_fields: dict[str, str | None] = dataclass_field(default_factory=dict)
    ccomponents_accessor: CcomponentsAccessorSpec | None = None
    variant_accessors: VariantAccessorsSpec | None = None
    compile_guard: str | None = None

    def freeze(self) -> DiscoveryClassSpec:
        return DiscoveryClassSpec(
            handle=self.handle,
            translation_unit=self.translation_unit,
            exclude=tuple(self.exclude),
            rename=self.rename,
            discover_fields=self.discover_fields,
            include_inherited_fields=self.include_inherited_fields,
            discover_has_fields=self.discover_has_fields,
            discover_children=self.discover_children,
            discover_as_item=self.discover_as_item,
            extra_fields=self.extra_fields,
            field_setters=tuple(self.field_setters),
            method_sizes=self.method_sizes,
            method_at_accessors=tuple(self.method_at_accessors),
            array_pair_fields=self.array_pair_fields,
            ccomponents_accessor=self.ccomponents_accessor,
            variant_accessors=self.variant_accessors,
            compile_guard=self.compile_guard,
        )


@dataclass
class _CppConstructorPolicy:
    handle: str
    cpp_class: str
    translation_unit: str
    expose_as: str
    params: list[str] | None
    param_names: list[str] = dataclass_field(default_factory=list)
    param_renames: dict[str, str] = dataclass_field(default_factory=dict)
    compile_guard: str | None = None
    compile_guard_message: str | None = None

    def freeze(self) -> DiscoveryConstructorSpec:
        return DiscoveryConstructorSpec(
            handle=self.handle,
            cpp_class=self.cpp_class,
            translation_unit=self.translation_unit,
            expose_as=self.expose_as,
            params=tuple(self.params) if self.params is not None else None,
            param_names=tuple(self.param_names),
            param_renames=self.param_renames,
            compile_guard=self.compile_guard,
            compile_guard_message=self.compile_guard_message,
        )


@dataclass(frozen=True)
class CppSpecPolicy:
    discovery: DiscoverySpec | None
    list_accessors: tuple[tuple[str, HandleListAccessorsSpec], ...]


def _option_struct_name(cpp_type: object) -> tuple[str, str] | None:
    semantic = analyze_cpp_type(cpp_type)
    if isinstance(semantic, OptionalSemanticType) and isinstance(
        semantic.element, RecordSemanticType
    ):
        qualified = semantic.element.base_name
        simple = qualified.rsplit("::", 1)[-1]
        return (simple, qualified) if simple.endswith("Options") else None
    spelling = (
        getattr(cpp_type, "normalized_spelling", None)
        or getattr(cpp_type, "spelling", None)
        or str(cpp_type)
    )
    normalized = " ".join(spelling.replace(" &", "&").replace(" *", "*").split())
    while normalized.startswith("const "):
        normalized = normalized[len("const ") :].strip()
    normalized = normalized.rstrip("&*").strip()
    simple = normalized.rsplit("::", 1)[-1]
    if not simple.endswith("Options"):
        return None
    qualified = (
        getattr(cpp_type, "canonical_spelling", None)
        or getattr(cpp_type, "normalized_desugared_spelling", None)
        or normalized
    )
    qualified = " ".join(qualified.replace(" &", "&").replace(" *", "*").split())
    while qualified.startswith("const "):
        qualified = qualified[len("const ") :].strip()
    qualified = qualified.rstrip("&*").strip()
    return simple, qualified


def _option_sequence_struct_name(cpp_type: object) -> tuple[str, str] | None:
    spelling = (
        getattr(cpp_type, "normalized_spelling", None)
        or getattr(cpp_type, "spelling", None)
        or str(cpp_type)
    )
    semantic = analyze_cpp_type(spelling)
    if not isinstance(semantic, SequenceSemanticType):
        return None
    leaf = semantic_leaf_type(semantic)
    if not isinstance(leaf, RecordSemanticType):
        return None
    simple = leaf.base_name.rsplit("::", 1)[-1]
    if not simple.endswith("Options"):
        return None
    return simple, leaf.base_name


def _option_c_type(name: str, c_prefix: str | None) -> str:
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    return f"{c_prefix}_{snake}_t" if c_prefix else f"ifcopenshell_{snake}_t"


def _split_macro_args(args: str) -> tuple[str, ...]:
    result: list[str] = []
    start = 0
    angle_depth = paren_depth = bracket_depth = 0
    for index, char in enumerate(args):
        if char == "<":
            angle_depth += 1
        elif char == ">" and angle_depth:
            angle_depth -= 1
        elif char == "(":
            paren_depth += 1
        elif char == ")" and paren_depth:
            paren_depth -= 1
        elif char == "[":
            bracket_depth += 1
        elif char == "]" and bracket_depth:
            bracket_depth -= 1
        elif char == "," and not angle_depth and not paren_depth and not bracket_depth:
            result.append(args[start:index].strip())
            start = index + 1
    result.append(args[start:].strip())
    return tuple(item for item in result if item)


def _handle_name_from_c_type(c_type: str) -> str:
    return c_type.removeprefix("ifcopenshell_").removesuffix("_t")


def _strip_string_literal(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _find_macro_invocations(text: str, marker: str) -> tuple[tuple[str, int], ...]:
    pattern = re.compile(rf"\b{re.escape(marker)}\s*\(")
    invocations: list[tuple[str, int]] = []
    for match in pattern.finditer(text):
        line_start = text.rfind("\n", 0, match.start()) + 1
        if text[line_start : match.start()].lstrip().startswith("#"):
            continue
        start = match.end()
        depth = 1
        quote: str | None = None
        escaped = False
        index = start
        while index < len(text):
            char = text[index]
            if quote is not None:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
            elif char in {'"', "'"}:
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    invocations.append((text[start:index], index + 1))
                    break
            index += 1
    return tuple(invocations)


def discover_cpp_spec_handles(
    translation_unit: Path,
    *,
    marker: str = "IFCAPI_HANDLE",
    c_prefix: str | None = None,
) -> tuple[CppSpecHandle, ...]:
    """Discover explicitly declared C ABI handles from a C++ binding spec translation unit."""
    text = translation_unit.read_text(encoding="utf-8")
    handles: list[CppSpecHandle] = []
    seen_c_types: set[str] = set()
    for raw_args, end in _find_macro_invocations(text, marker):
        args = _split_macro_args(raw_args)
        if len(args) not in {2, 3, 4, 5}:
            msg = f"{marker} expects cpp_type/destructor, optional handle name, optional ptr_type, and optional empty_check"
            raise ValueError(msg)
        if len(args) >= 3 and re.fullmatch(r"[A-Za-z_]\w*", args[0]):
            handle_name = args[0]
            cpp_type = args[1]
            destructor = args[2]
            ptr_type = args[3] if len(args) >= 4 else "raw"
            empty_check = _strip_string_literal(args[4]) if len(args) == 5 else None
            c_type_match = re.match(
                r"\s*(?:struct|class)\s+(?P<c_type>ifcopenshell_[A-Za-z0-9_]+_t)\s*;",
                text[end:],
                re.DOTALL,
            )
            if c_prefix is not None:
                c_type = (
                    c_type_match.group("c_type")
                    if c_type_match is not None
                    else f"{c_prefix}_{handle_name}_t"
                )
            elif c_type_match is not None:
                c_type = c_type_match.group("c_type")
            else:
                msg = f"{marker} must be followed by an ifcopenshell_*_t struct/class declaration"
                raise ValueError(msg)
        else:
            c_type_match = re.match(
                r"\s*(?:struct|class)\s+(?P<c_type>ifcopenshell_[A-Za-z0-9_]+_t)\s*;",
                text[end:],
                re.DOTALL,
            )
            if c_type_match is None:
                msg = f"{marker} must be followed by an ifcopenshell_*_t struct/class declaration"
                raise ValueError(msg)
            c_type = c_type_match.group("c_type")
            handle_name = _handle_name_from_c_type(c_type)
            cpp_type = args[0]
            destructor = args[1]
            ptr_type = args[2] if len(args) >= 3 else "raw"
            empty_check = _strip_string_literal(args[3]) if len(args) == 4 else None
        if c_type in seen_c_types:
            msg = f"C++ spec handle '{c_type}' is declared more than once"
            raise ValueError(msg)
        seen_c_types.add(c_type)
        handles.append(
            CppSpecHandle(
                name=handle_name,
                cpp_type=cpp_type,
                c_type=c_type,
                destructor=destructor,
                ptr_type=ptr_type,
                empty_check=empty_check,
            )
        )
    return tuple(handles)


def discover_cpp_spec_methods(
    translation_unit: Path,
    *,
    marker: str = "IFCAPI_DISCOVER_METHOD",
) -> tuple[CppSpecMethod, ...]:
    """Read the explicitly selected native methods from a C++ binding spec."""
    text = translation_unit.read_text(encoding="utf-8")
    methods: list[CppSpecMethod] = []
    seen: set[tuple[str, str, tuple[str, ...]]] = set()
    for raw_args, _ in _find_macro_invocations(text, marker):
        args = _split_macro_args(raw_args)
        if len(args) < 3:
            msg = f"{marker} expects handle, C++ name, exposed name, and optional parameter types"
            raise ValueError(msg)
        method = CppSpecMethod(
            handle=args[0],
            cpp_name=args[1],
            expose_as=args[2],
            params=args[3:],
        )
        key = (method.handle, method.expose_as, method.params)
        if key in seen:
            msg = (
                f"C++ spec method '{method.handle}.{method.expose_as}' "
                "is declared more than once"
            )
            raise ValueError(msg)
        seen.add(key)
        methods.append(method)
    return tuple(methods)


def discover_cpp_spec_selected_functions(
    environment: DiscoveryEnvironment,
    translation_unit: Path,
    *,
    marker: str = "IFCAPI_DISCOVER_FUNCTION",
) -> tuple[CppSpecFunction, ...]:
    """Discover explicitly selected functions outside the spec namespace."""
    text = translation_unit.read_text(encoding="utf-8")
    selections: list[tuple[str, str]] = []
    names_by_namespace: dict[str, set[str]] = {}
    seen: set[tuple[str, str]] = set()
    for raw_args, _ in _find_macro_invocations(text, marker):
        args = _split_macro_args(raw_args)
        if len(args) != 2:
            msg = f"{marker} expects a C++ namespace and function name"
            raise ValueError(msg)
        namespace, name = args
        key = (namespace, name)
        if key in seen:
            msg = f"C++ spec function '{namespace}::{name}' is declared more than once"
            raise ValueError(msg)
        seen.add(key)
        selections.append(key)
        names_by_namespace.setdefault(namespace, set()).add(name)

    discovered_namespaces = {
        namespace: discover_namespace_functions(
            environment,
            translation_unit,
            namespace,
            selected_names=frozenset(names),
        )
        for namespace, names in names_by_namespace.items()
    }
    functions: list[CppSpecFunction] = []
    for namespace, name in selections:
        discovered = discovered_namespaces[namespace]
        overloads = discovered.get(name, ())
        if len(overloads) != 1:
            msg = (
                f"C++ spec function '{namespace}::{name}' has {len(overloads)} "
                "overloads; selected functions must be unique"
            )
            raise ValueError(msg)
        functions.append(
            CppSpecFunction(
                name=name,
                namespace=namespace,
                discovered=overloads[0],
                return_annotations=frozenset(),
                param_annotations={},
                param_defaults={},
            )
        )
    return tuple(functions)


def _cpp_policy_type_matches(discovered_type: str, requested_type: str) -> bool:
    discovered_type = _normalize_cpp_type(discovered_type)
    requested_type = _normalize_cpp_type(requested_type)
    unqualified_discovered = re.sub(
        r"\b(?:[A-Za-z_]\w*::)+", "", discovered_type
    ).replace(" ", "")
    unqualified_requested = re.sub(
        r"\b(?:[A-Za-z_]\w*::)+", "", requested_type
    ).replace(" ", "")
    if unqualified_discovered == unqualified_requested:
        return True
    discovered_suffix = "".join(char for char in discovered_type if char in "*&")
    requested_suffix = "".join(char for char in requested_type if char in "*&")
    if discovered_suffix != requested_suffix:
        return False
    discovered_base = discovered_type.replace("*", "").replace("&", "")
    requested_base = requested_type.replace("*", "").replace("&", "")
    return _cpp_type_names_match(discovered_base, requested_base)


def lower_cpp_spec_methods_to_calls(
    environment: DiscoveryEnvironment,
    translation_unit: Path,
    methods: tuple[CppSpecMethod, ...],
    handles: dict[str, HandleSpec],
) -> tuple[CallSpec, ...]:
    """Discover selected native methods with Clang and lower their signatures."""
    method_cache: dict[str, dict[str, tuple[DiscoveredMethod, ...]]] = {}
    selected_names = {
        handle: frozenset(
            method.cpp_name for method in methods if method.handle == handle
        )
        for handle in {method.handle for method in methods}
    }
    calls: list[CallSpec] = []
    for method in methods:
        handle = handles.get(method.handle)
        if handle is None:
            msg = f"C++ spec method refers to unknown handle '{method.handle}'"
            raise ValueError(msg)
        discovered_by_name = method_cache.get(method.handle)
        if discovered_by_name is None:
            discovered_by_name = discover_public_methods(
                environment,
                translation_unit,
                handle.cpp_type,
                include_inherited=True,
                selected_names=selected_names[method.handle],
            )
            method_cache[method.handle] = discovered_by_name
        overloads = discovered_by_name.get(method.cpp_name)
        if overloads is None:
            msg = (
                f"Unable to discover method '{method.cpp_name}' "
                f"for handle '{method.handle}'"
            )
            raise ValueError(msg)
        requested_params = tuple(
            param.removeprefix("IFCAPI_INT32(").removesuffix(")")
            if param.startswith("IFCAPI_INT32(")
            else param
            for param in method.params
        )
        overload_policy = DiscoveryOverloadSpec(
            cpp_name=method.cpp_name,
            expose_as=method.expose_as,
            params=requested_params,
        )
        try:
            selected = _select_overload(overloads, overload_policy)
        except ValueError:
            candidates = tuple(
                overload
                for overload in overloads
                if len(overload.params) == len(requested_params)
                and all(
                    any(
                        candidate and _cpp_policy_type_matches(candidate, requested)
                        for candidate in (
                            param.cpp_type,
                            param.cpp_type_ref.normalized_spelling,
                            param.cpp_type_ref.normalized_desugared_spelling,
                            param.cpp_type_ref.canonical_spelling,
                        )
                    )
                    for param, requested in zip(
                        overload.params, requested_params, strict=True
                    )
                )
            )
            if len(candidates) != 1:
                raise
            selected = candidates[0]
        returns, params = _infer_method_signature(
            selected,
            handles=handles,
        )
        policy_operation = _direct_method_policy_operation(selected, handles)
        if len(params) == len(method.params):
            params = tuple(
                replace(param, type=replace(param.type, kind="int32"))
                if requested.startswith("IFCAPI_INT32(")
                else param
                for param, requested in zip(params, method.params, strict=True)
            )
        elif params or not isinstance(policy_operation, BoolOutParamPolicyOp):
            msg = f"Unable to apply parameter policy for '{method.handle}.{method.cpp_name}'"
            raise ValueError(msg)
        calls.append(
            CallSpec(
                expose_as=method.expose_as,
                c_name=_receiver_c_name(handle, method.expose_as),
                receiver=method.handle,
                returns=returns,
                params=params,
                policy_operation=policy_operation,
            )
        )
    return tuple(calls)


def _policy_value(value: str) -> str | None:
    value = _strip_string_literal(value)
    return None if value == "_" else value


def discover_cpp_spec_policy(
    translation_unit: Path,
    handles: dict[str, HandleSpec],
    *,
    marker: str = "IFCAPI_DISCOVER_POLICY",
) -> CppSpecPolicy:
    """Read structured policy that cannot be inferred from C++ declarations."""
    text = translation_unit.read_text(encoding="utf-8")
    classes: dict[str, _CppClassPolicy] = {}
    list_accessors: list[tuple[str, HandleListAccessorsSpec]] = []

    def class_policy(handle: str) -> _CppClassPolicy:
        if handle not in handles:
            msg = f"{marker} refers to unknown handle '{handle}'"
            raise ValueError(msg)
        return classes.setdefault(
            handle,
            _CppClassPolicy(
                handle=handle,
                translation_unit=translation_unit.name,
            ),
        )

    for raw_args, _ in _find_macro_invocations(text, marker):
        args = _split_macro_args(raw_args)
        if len(args) < 2:
            msg = f"{marker} expects a handle, operation, and operation arguments"
            raise ValueError(msg)
        handle, operation, *values = args
        if operation == "list_accessor":
            if len(values) != 6:
                msg = (
                    f"{marker} list_accessor expects receiver, list parameter, "
                    "item handle, count name, at name, and message"
                )
                raise ValueError(msg)
            if handle not in handles:
                msg = f"{marker} refers to unknown list handle '{handle}'"
                raise ValueError(msg)
            receiver, list_param, item_handle, count_as, at_as, message = values
            list_accessors.append(
                (
                    handle,
                    HandleListAccessorsSpec(
                        receiver=receiver,
                        list_param=list_param,
                        item_handle=item_handle,
                        count_as=count_as,
                        at_as=at_as,
                        out_of_range_message=_strip_string_literal(message),
                    ),
                )
            )
            continue
        policy = class_policy(handle)
        if operation == "fields":
            if any(value != "inherited" for value in values):
                msg = f"{marker} fields only accepts the optional 'inherited' flag"
                raise ValueError(msg)
            policy.discover_fields = True
            policy.include_inherited_fields = "inherited" in values
        elif operation == "exclude":
            policy.exclude.extend(values)
        elif operation == "rename":
            if len(values) != 2:
                msg = f"{marker} rename expects source and exposed names"
                raise ValueError(msg)
            policy.rename[values[0]] = values[1]
        elif operation == "has_fields":
            if values:
                msg = f"{marker} has_fields does not accept arguments"
                raise ValueError(msg)
            policy.discover_has_fields = True
        elif operation == "as_item":
            if values:
                msg = f"{marker} as_item does not accept arguments"
                raise ValueError(msg)
            policy.discover_as_item = True
        elif operation == "extra_field":
            if len(values) != 2:
                msg = f"{marker} extra_field expects name and C++ type"
                raise ValueError(msg)
            policy.extra_fields[values[0]] = values[1]
        elif operation == "field_setter":
            policy.field_setters.extend(values)
        elif operation == "method_size":
            if len(values) != 2:
                msg = f"{marker} method_size expects method and exposed names"
                raise ValueError(msg)
            policy.method_sizes[values[0]] = values[1]
        elif operation == "method_at":
            if len(values) not in {5, 6}:
                msg = (
                    f"{marker} method_at expects method, exposed name, item handle, "
                    "message, exception, and optional ownership"
                )
                raise ValueError(msg)
            exception_type = values[4]
            if exception_type not in {"std::out_of_range", "std::runtime_error"}:
                msg = f"{marker} method_at received unsupported exception '{exception_type}'"
                raise ValueError(msg)
            ownership = values[5] if len(values) == 6 else None
            if ownership not in {None, "owned", "borrowed", "static"}:
                msg = f"{marker} method_at received unsupported ownership '{ownership}'"
                raise ValueError(msg)
            policy.method_at_accessors.append(
                MethodAtAccessorSpec(
                    method_name=values[0],
                    expose_as=values[1],
                    item_handle=values[2],
                    ownership=ownership,
                    out_of_range_message=_strip_string_literal(values[3]),
                    exception_type=exception_type,
                )
            )
        elif operation == "children":
            names = [*values, "_", "_", "_", "_", "_"][:6]
            policy.discover_children = DiscoveryChildrenSpec(
                cpp_field=_policy_value(names[0]) or "children",
                element_handle=_policy_value(names[1]),
                count_as=_policy_value(names[2]),
                at_as=_policy_value(names[3]),
                add_as=_policy_value(names[4]),
                add_cast_cpp_type=_policy_value(names[5]),
            )
        elif operation == "array_pair":
            policy.array_pair_fields.update((value, None) for value in values)
        elif operation == "ccomponents":
            if not 1 <= len(values) <= 3:
                msg = (
                    f"{marker} ccomponents expects an exposed name and optional "
                    "access path and dimensions"
                )
                raise ValueError(msg)
            access_via = (
                _strip_string_literal(access)
                if len(values) > 1 and (access := _policy_value(values[1]))
                else "ccomponents"
            )
            dimensions = (
                int(value)
                if len(values) > 2 and (value := _policy_value(values[2]))
                else None
            )
            policy.ccomponents_accessor = CcomponentsAccessorSpec(
                expose_as=values[0],
                dimensions=dimensions,
                access_via=access_via,
            )
        elif operation == "compile_guard":
            if len(values) != 1:
                msg = f"{marker} compile_guard expects one macro name"
                raise ValueError(msg)
            policy.compile_guard = values[0]
        elif operation == "variant":
            if len(values) < 5:
                msg = (
                    f"{marker} variant expects get method, set method, variant "
                    "type, suffix, and C++ type"
                )
                raise ValueError(msg)
            get_method, set_method, variant_type, suffix, cpp_type, *getter_types = (
                values
            )
            if policy.variant_accessors is None:
                policy.variant_accessors = VariantAccessorsSpec(
                    get_method=get_method,
                    set_method=set_method,
                    variant_type=variant_type,
                    types={},
                )
            variant = policy.variant_accessors
            if (
                variant.get_method != get_method
                or variant.set_method != set_method
                or variant.variant_type != variant_type
            ):
                msg = f"{marker} variant entries for '{handle}' disagree"
                raise ValueError(msg)
            variant.types[suffix] = VariantAccessorTypeSpec(
                cpp_type=cpp_type,
                getter_types=tuple(getter_types) or (cpp_type,),
            )
        else:
            msg = f"Unknown {marker} operation '{operation}'"
            raise ValueError(msg)

    constructors: dict[str, _CppConstructorPolicy] = {}
    constructor_marker = "IFCAPI_DISCOVER_CONSTRUCTOR"
    for raw_args, _ in _find_macro_invocations(text, constructor_marker):
        args = _split_macro_args(raw_args)
        if len(args) != 6:
            msg = (
                f"{constructor_marker} expects handle, class, exposed name, "
                "mode, guard, and message"
            )
            raise ValueError(msg)
        handle, cpp_class, expose_as, mode, guard, message = args
        if handle not in handles:
            msg = f"{constructor_marker} refers to unknown handle '{handle}'"
            raise ValueError(msg)
        if expose_as in constructors:
            msg = f"Constructor '{expose_as}' is declared more than once"
            raise ValueError(msg)
        if mode not in {"auto", "explicit"}:
            msg = f"{constructor_marker} mode must be 'auto' or 'explicit'"
            raise ValueError(msg)
        constructors[expose_as] = _CppConstructorPolicy(
            handle=handle,
            cpp_class=cpp_class,
            translation_unit=translation_unit.name,
            expose_as=expose_as,
            params=[] if mode == "explicit" else None,
            compile_guard=_policy_value(guard),
            compile_guard_message=_policy_value(message),
        )

    param_marker = "IFCAPI_CONSTRUCTOR_PARAM"
    for raw_args, _ in _find_macro_invocations(text, param_marker):
        args = _split_macro_args(raw_args)
        if len(args) != 4:
            msg = (
                f"{param_marker} expects exposed name, source name, public name, "
                "and C++ type"
            )
            raise ValueError(msg)
        expose_as, source_name, public_name, cpp_type = args
        constructor = constructors.get(expose_as)
        if constructor is None:
            msg = f"{param_marker} refers to unknown constructor '{expose_as}'"
            raise ValueError(msg)
        if constructor.params is None:
            msg = f"{param_marker} cannot extend auto constructor '{expose_as}'"
            raise ValueError(msg)
        constructor.params.append(cpp_type)
        constructor.param_names.append(public_name)
        if source_name != public_name:
            constructor.param_renames[source_name] = public_name

    discovery = (
        DiscoverySpec(
            include_dir=Path("."),
            classes=tuple(policy.freeze() for policy in classes.values()),
            constructors=tuple(
                constructor.freeze() for constructor in constructors.values()
            ),
        )
        if classes or constructors
        else None
    )
    return CppSpecPolicy(
        discovery=discovery,
        list_accessors=tuple(list_accessors),
    )


def lower_cpp_spec_policy_to_calls(
    environment: DiscoveryEnvironment,
    translation_unit: Path,
    policy: CppSpecPolicy,
    handles: dict[str, HandleSpec],
    c_prefix: str,
) -> tuple[CallSpec, ...]:
    calls: list[CallSpec] = []
    if policy.discovery is not None:
        constructor_calls, constructor_diagnostics = _discover_constructor_calls(
            translation_unit,
            policy.discovery,
            handles,
            c_prefix,
            environment,
        )
        method_calls, method_diagnostics = _discover_method_calls(
            translation_unit,
            policy.discovery,
            handles,
            environment,
        )
        calls.extend((*constructor_calls, *method_calls))
        for diagnostic in (*constructor_diagnostics, *method_diagnostics):
            debug_log(
                "spec.discovery.diagnostic",
                f"{diagnostic.owner}.{diagnostic.member}: {diagnostic.message}",
            )
    for handle, accessors in policy.list_accessors:
        calls.extend(
            _handle_list_accessor_calls(
                list_handle_name=handle,
                accessors=accessors,
                handles=handles,
            )
        )
    return tuple(calls)


def discover_cpp_spec_result_structs(
    translation_unit: Path,
    namespace: str,
    *,
    marker: str = "IFCAPI_RESULT_STRUCT",
) -> tuple[CppSpecResultStruct, ...]:
    """Discover explicitly declared generated result structs from a C++ spec translation unit."""
    text = _strip_comments(translation_unit.read_text(encoding="utf-8"))
    marker_re = re.escape(marker)
    struct_re = re.compile(
        rf"\b{marker_re}\s*\((?P<args>[^)]*)\)\s*"
        r"struct\s+(?P<name>[A-Za-z_]\w*)\s*\{(?P<body>.*?)\}\s*;",
        re.DOTALL,
    )
    result_structs: list[CppSpecResultStruct] = []
    seen_c_types: set[str] = set()
    for match in struct_re.finditer(text):
        args = _split_macro_args(match.group("args"))
        if len(args) not in {1, 2}:
            msg = f"{marker} expects c_type/cpp_type and optional cpp_type"
            raise ValueError(msg)
        name = match.group("name")
        if re.fullmatch(r"ifcopenshell_[A-Za-z0-9_]+_t", name):
            c_type = name
            cpp_type = args[0]
            if len(args) == 2:
                msg = f"{marker} with an ifcopenshell_*_t struct name expects only cpp_type"
                raise ValueError(msg)
        else:
            c_type = args[0]
            cpp_type = args[1] if len(args) == 2 else f"{namespace}::{name}"
        if not re.fullmatch(r"ifcopenshell_[A-Za-z0-9_]+_t", c_type):
            msg = f"{marker} c_type must be an ifcopenshell_*_t type"
            raise ValueError(msg)
        if c_type in seen_c_types:
            msg = f"C++ spec result struct '{c_type}' is declared more than once"
            raise ValueError(msg)
        seen_c_types.add(c_type)
        fields: list[tuple[str, str]] = []
        for raw_field in match.group("body").split(";"):
            field = raw_field.strip()
            if not field:
                continue
            field_match = re.match(
                r"(?P<type>.+?)\s+(?P<name>[A-Za-z_]\w*)$", field, re.DOTALL
            )
            if field_match is None:
                msg = f"Unable to parse result struct field declaration: {field!r}"
                raise ValueError(msg)
            fields.append(
                (" ".join(field_match.group("type").split()), field_match.group("name"))
            )
        result_structs.append(
            CppSpecResultStruct(
                name=name,
                cpp_type=cpp_type,
                c_type=c_type,
                fields=tuple(fields),
            )
        )
    return tuple(result_structs)


CppSpecSignature = tuple[
    frozenset[str],
    dict[str, frozenset[str]],
    dict[str, bool],
    str | None,
    str | None,
    str | None,
    str | None,
]


def _param_type_decl(param: str) -> str:
    name = _param_name(param)
    return param[: param.rfind(name)].strip() if name else param.strip()


_PRIVATE_NAMES = frozenset({"to_base_vector"})


def _discover_spec_signatures(
    source: Path,
    selected_names: set[str],
) -> dict[str, tuple[CppSpecSignature, ...]]:
    text = source.read_text(encoding="utf-8")
    signatures: dict[str, list[CppSpecSignature]] = {}
    selected_names = selected_names - _PRIVATE_NAMES
    if not selected_names:
        return {}
    signature_re = re.compile(
        r"(?P<doc>(?:(?:[ \t]*(?://[/!].*?)\n)|(?:[ \t]*/\*[*!].*?\*/\s*))*?)"
        r"(?P<annotations>(?:IFCAPI_\w+(?:\([^)]*\))?\s+)*)"
        r"(?P<return_decl>[\w:<>~,\s*&()]+?)\s+"
        r"(?P<name>[A-Za-z_]\w*)\s*\("
        r"(?P<params>[^;{}]*)\)\s*\{",
        re.DOTALL,
    )
    for match in signature_re.finditer(text):
        name = match.group("name")
        if name not in selected_names:
            continue
        return_decl = f"{match.group('annotations')}{match.group('return_decl')}"
        return_decl = re.sub(r"^\s*inline\s+", "", return_decl.strip())
        return_annotations, _ = _leading_annotations(return_decl)
        param_annotations: dict[str, frozenset[str]] = {}
        param_defaults: dict[str, bool] = {}
        first_param_type = None
        first_param_name = None
        for param in _split_params(match.group("params")):
            annotations, rest = _leading_annotations(param)
            if first_param_type is None:
                first_param_type = _param_type_decl(rest)
                first_param_name = _param_name(rest)
            if annotations:
                param_annotations[_param_name(rest)] = annotations
            if _has_default(param):
                param_defaults[_param_name(rest)] = True
        if first_param_name == "self":
            if name in signatures and any(
                item[3] == first_param_type for item in signatures[name]
            ):
                msg = f"C++ spec export '{name}' is declared more than once; exported spec functions must be unique"
                raise ValueError(msg)
        else:
            if name in signatures:
                msg = f"C++ spec export '{name}' is declared more than once; exported spec functions must be unique"
                raise ValueError(msg)
        signatures.setdefault(name, []).append(
            (
                return_annotations,
                param_annotations,
                param_defaults,
                None,
                first_param_type,
                _clean_doc_comment(match.group("doc")),
                None,
            )
        )
    return {name: tuple(entries) for name, entries in signatures.items()}


def discover_cpp_spec_contract_headers(
    translation_unit: Path,
    include_dirs: tuple[Path, ...],
) -> tuple[Path, ...]:
    text = _strip_comments(translation_unit.read_text(encoding="utf-8"))
    headers: list[Path] = []
    seen: set[Path] = set()
    for match in re.finditer(
        r'^\s*#\s*include\s+"(?P<header>[^"]+)"', text, re.MULTILINE
    ):
        header = match.group("header")
        candidates = (
            translation_unit.parent / header,
            *(include_dir / header for include_dir in include_dirs),
        )
        for candidate in candidates:
            if not candidate.exists():
                continue
            resolved = candidate.resolve()
            if resolved in seen:
                break
            if discover_marked_functions_in_headers([resolved]):
                headers.append(resolved)
                seen.add(resolved)
            break
    return tuple(headers)


def discover_cpp_spec_functions(
    environment: DiscoveryEnvironment,
    translation_unit: Path,
    namespace: str,
    *,
    contract_headers: tuple[Path, ...] = (),
) -> tuple[CppSpecFunction, ...]:
    discovered = discover_namespace_functions(
        environment,
        translation_unit,
        namespace,
    )

    spec_sigs = _discover_spec_signatures(translation_unit, set(discovered.keys()))

    combined = dict(spec_sigs)
    for function in discover_marked_functions_in_headers(contract_headers):
        if function.name in combined:
            msg = f"C++ spec export '{function.name}' is declared more than once; exported spec functions must be unique"
            raise ValueError(msg)
        combined[function.name] = (
            (
                function.return_annotations,
                function.param_annotations,
                function.param_defaults,
                None,
                None,
                function.doc,
                function.header.stem,
            ),
        )
    if not combined:
        msg = f"No exported functions were found in C++ spec '{translation_unit}'"
        raise ValueError(msg)

    result: list[CppSpecFunction] = []
    for name in sorted(combined):
        overloads = discovered.get(name, ())
        if not overloads:
            msg = f"C++ spec export '{name}' was found in spec but not discovered by Clang"
            raise ValueError(msg)
        for (
            return_annotations,
            param_annotations,
            param_defaults,
            receiver,
            first_param_type,
            doc,
            public_module,
        ) in combined[name]:
            selected_overloads = overloads
            if len(overloads) != 1 and first_param_type is not None:
                selected_overloads = tuple(
                    overload
                    for overload in overloads
                    if overload.params
                    and _canonical_cpp_type(overload.params[0].cpp_type_ref)
                    == _canonical_cpp_type(first_param_type)
                )
            if len(selected_overloads) != 1:
                msg = f"C++ spec export '{name}' has {len(overloads)} overloads; exported spec functions must be unique"
                raise ValueError(msg)
            result.append(
                CppSpecFunction(
                    name=name,
                    namespace=namespace,
                    discovered=selected_overloads[0],
                    return_annotations=return_annotations,
                    param_annotations=param_annotations,
                    param_defaults=param_defaults,
                    receiver=receiver,
                    doc=doc,
                    public_module=public_module,
                )
            )
    return tuple(result)


def _receiver_c_name(handle: HandleSpec, expose_as: str) -> str:
    receiver = handle.c_type.removeprefix("ifcopenshell_").removesuffix("_t")
    return f"ifcopenshell_{receiver}_{expose_as}"


def _prefixed_c_name(name: str, c_prefix: str | None) -> str:
    if not c_prefix or name.startswith(f"{c_prefix}_"):
        return name
    return f"{c_prefix}_{name}"


def _canonical_cpp_type(cpp_type: object) -> str:
    if not isinstance(cpp_type, str):
        cpp_type = (
            getattr(cpp_type, "normalized_spelling", None)
            or getattr(cpp_type, "spelling", None)
            or str(cpp_type)
        )
    normalized = " ".join(cpp_type.replace(" *", "*").replace(" &", "&").split())
    while normalized.startswith("const "):
        normalized = normalized[len("const ") :].strip()
    normalized = normalized.removesuffix("&").removesuffix("*").strip()
    return normalized.split("::")[-1]


def _apply_type_annotations(
    type_spec: TypeSpec, annotations: frozenset[str]
) -> TypeSpec:
    ownership = type_spec.ownership
    if "IFCAPI_OWNED" in annotations:
        ownership = "owned"
    elif "IFCAPI_COPY" in annotations:
        ownership = "copy"
    elif "IFCAPI_STATIC" in annotations:
        ownership = "static"
    if ownership == type_spec.ownership:
        return type_spec
    return TypeSpec(
        kind=type_spec.kind,
        handle=type_spec.handle,
        struct=type_spec.struct,
        variants=type_spec.variants,
        ownership=ownership,
        nullable=type_spec.nullable,
        cpp_type=type_spec.cpp_type,
        sequence_depth=type_spec.sequence_depth,
    )


def _apply_param_annotations(
    type_spec: TypeSpec,
    annotations: frozenset[str],
    handles: dict[str, HandleSpec],
) -> TypeSpec:
    return _apply_type_annotations(type_spec, annotations)


def _apply_return_annotations(
    type_spec: TypeSpec,
    annotations: frozenset[str],
    handles: dict[str, HandleSpec],
) -> TypeSpec:
    return _apply_type_annotations(type_spec, annotations)


def lower_cpp_spec_functions_to_calls(
    functions: tuple[CppSpecFunction, ...],
    handles: dict[str, HandleSpec],
    result_structs: dict[str, ResultStructSpec] | None = None,
    option_structs: dict[str, OptionStructSpec] | None = None,
    c_prefix: str | None = None,
) -> tuple[CallSpec, ...]:
    """Lower discovered C++ spec functions to the binding call model."""
    result_structs = result_structs or {}
    option_structs = option_structs or {}
    calls: list[CallSpec] = []
    for function in functions:
        discovered = function.discovered
        returns = _apply_return_annotations(
            _infer_return_type(discovered.return_type_ref, handles, result_structs),
            function.return_annotations,
            handles,
        )

        if "IFCAPI_DOUBLE_BUFFER" not in function.return_annotations:
            return_type_ref = discovered.return_type_ref
            is_const_ref = (
                hasattr(return_type_ref, "is_const")
                and return_type_ref.is_const
                and hasattr(return_type_ref, "is_lvalue_reference")
                and return_type_ref.is_lvalue_reference
            )
            is_const_ptr = (
                hasattr(return_type_ref, "is_const")
                and return_type_ref.is_const
                and hasattr(return_type_ref, "is_lvalue_reference")
                and not return_type_ref.is_lvalue_reference
                and hasattr(return_type_ref, "pointer_depth")
                and return_type_ref.pointer_depth > 0
            )
            if (
                returns.kind == "double"
                and returns.sequence_depth == 1
                and is_const_ref
            ):
                returns = TypeSpec(
                    kind="double_buffer",
                    ownership=returns.ownership,
                    nullable=returns.nullable,
                    cpp_type=returns.cpp_type,
                )
            elif (
                returns.kind == "int32" and returns.sequence_depth == 1 and is_const_ref
            ):
                returns = TypeSpec(
                    kind="int32_buffer",
                    ownership=returns.ownership,
                    nullable=returns.nullable,
                    cpp_type=returns.cpp_type,
                )
            elif is_const_ptr:
                normalized = " ".join(
                    returns.cpp_type.replace(" *", "*").replace(" &", "&").split()
                )
                normalized = normalized.replace("const ", "").strip()
                if normalized == "double*":
                    returns = TypeSpec(
                        kind="double_buffer",
                        ownership=returns.ownership,
                        nullable=returns.nullable,
                        cpp_type=returns.cpp_type,
                    )
                elif normalized == "int32_t*":
                    returns = TypeSpec(
                        kind="int32_buffer",
                        ownership=returns.ownership,
                        nullable=returns.nullable,
                        cpp_type=returns.cpp_type,
                    )
        if (
            "IFCAPI_HANDLE_RESULT" not in function.return_annotations
            and returns.kind == "handle"
        ):
            return_type_raw = discovered.return_type_ref
            cpp_norm = return_type_raw.normalized_spelling or return_type_raw.spelling
            cpp_norm = " ".join(cpp_norm.replace(" *", "*").replace(" &", "&").split())
            cpp_norm = re.sub(r"\bconst\b\s*", "", cpp_norm).strip()
            if "*" in cpp_norm:
                stripped = cpp_norm.removesuffix("*").removesuffix("&").strip()
                if stripped and stripped != cpp_norm:
                    for handle_name, handle in handles.items():
                        handle_norm = " ".join(
                            handle.cpp_type.replace(" *", "*")
                            .replace(" &", "&")
                            .split()
                        )
                        handle_norm = re.sub(r"\bconst\b\s*", "", handle_norm).strip()
                        if handle_norm == stripped:
                            returns = TypeSpec(
                                kind="handle",
                                handle=handle_name,
                                ownership=returns.ownership,
                                nullable=returns.nullable,
                                cpp_type=returns.cpp_type,
                            )
                            break
        discovered_params = discovered.params
        receiver_cpp_type = None
        receiver = function.receiver
        if receiver is None:
            if discovered_params and discovered_params[0].name == "self":
                first_param = discovered_params[0]
                first_type = first_param.cpp_type_ref
                first_canonical = _canonical_cpp_type(first_type)
                for handle_name, handle in handles.items():
                    if _canonical_cpp_type(handle.cpp_type) == first_canonical:
                        receiver = handle_name
                        break
                if receiver is None:
                    msg = (
                        f"C++ spec method export '{function.name}' has first parameter 'self' "
                        f"with type '{first_type.normalized_spelling or first_type.spelling}' "
                        f"that does not match any known handle"
                    )
                    raise ValueError(msg)
                receiver_cpp_type = (
                    first_type.normalized_spelling or first_type.spelling
                )
                discovered_params = discovered_params[1:]
        elif function.receiver is not None:
            if function.receiver not in handles:
                msg = f"C++ spec export '{function.name}' declares unknown receiver handle '{function.receiver}'"
                raise ValueError(msg)
            if not discovered_params:
                msg = f"C++ spec method export '{function.name}' must declare an explicit receiver parameter"
                raise ValueError(msg)
            receiver_param = discovered_params[0]
            receiver_cpp_type = (
                receiver_param.cpp_type_ref.normalized_spelling
                or receiver_param.cpp_type_ref.spelling
            )
            handle_cpp_type = handles[function.receiver].cpp_type
            if _canonical_cpp_type(receiver_cpp_type) != _canonical_cpp_type(
                handle_cpp_type
            ):
                msg = (
                    f"C++ spec method export '{function.name}' receiver parameter type "
                    f"'{receiver_cpp_type}' does not match handle '{function.receiver}' type '{handle_cpp_type}'"
                )
                raise ValueError(msg)
            discovered_params = discovered_params[1:]
        params = []
        for param in discovered_params:
            param_ann = function.param_annotations.get(param.name, frozenset())
            option_name = _option_struct_name(param.cpp_type_ref)
            if option_name is not None and option_name[0] in option_structs:
                option = option_structs[option_name[0]]
                nullable = isinstance(
                    analyze_cpp_type(param.cpp_type_ref), OptionalSemanticType
                )
                param_type = TypeSpec(
                    kind="option",
                    struct=option.name,
                    nullable=nullable,
                    cpp_type=param.cpp_type_ref.normalized_spelling
                    or param.cpp_type_ref.spelling,
                )
            elif (
                sequence_option := _option_sequence_struct_name(param.cpp_type_ref)
            ) is not None and sequence_option[0] in option_structs:
                option = option_structs[sequence_option[0]]
                param_type = TypeSpec(
                    kind="option",
                    struct=option.name,
                    cpp_type=param.cpp_type_ref.normalized_spelling
                    or param.cpp_type_ref.spelling,
                    sequence_depth=1,
                )
            else:
                param_type = _apply_param_annotations(
                    _infer_param_type(param.cpp_type_ref, handles),
                    param_ann,
                    handles,
                )
            if param_type.kind == "handle" and "IFCAPI_HANDLE_PARAM" not in param_ann:
                cpp_type_raw = (
                    param.cpp_type_ref.normalized_spelling
                    or param.cpp_type_ref.spelling
                )
                cpp_norm = " ".join(
                    cpp_type_raw.replace(" *", "*").replace(" &", "&").split()
                )
                cpp_norm = re.sub(r"\bconst\b\s*", "", cpp_norm).strip()
                if "*" in cpp_norm:
                    stripped = cpp_norm.removesuffix("*").removesuffix("&").strip()
                    if stripped and stripped != cpp_norm:
                        for handle_name, handle in handles.items():
                            handle_norm = " ".join(
                                handle.cpp_type.replace(" *", "*")
                                .replace(" &", "&")
                                .split()
                            )
                            handle_norm = re.sub(
                                r"\bconst\b\s*", "", handle_norm
                            ).strip()
                            if handle_norm == stripped:
                                param_type = TypeSpec(
                                    kind="handle",
                                    handle=handle_name,
                                    ownership=param_type.ownership,
                                    nullable=param_type.nullable,
                                    cpp_type=param_type.cpp_type,
                                )
                                break
            params.append(
                ParamSpec(
                    name=param.name,
                    type=param_type,
                    has_default=function.param_defaults.get(param.name, False),
                )
            )
        cpp_name = f"{function.namespace}::{discovered.cpp_name}"
        calls.append(
            CallSpec(
                expose_as=function.name,
                c_name=(
                    _receiver_c_name(handles[receiver], function.name)
                    if receiver is not None
                    else _prefixed_c_name(function.name, c_prefix)
                ),
                receiver=receiver,
                returns=returns,
                params=tuple(params),
                policy_operation=(
                    SpecMethodFunctionPolicyOp(
                        cpp_name=cpp_name, receiver_cpp_type=receiver_cpp_type
                    )
                    if receiver_cpp_type is not None
                    else DirectFunctionPolicyOp(cpp_name=cpp_name)
                ),
                doc=function.doc,
                public_module=function.public_module,
            )
        )
    return tuple(calls)


def lower_cpp_spec_handles_to_specs(
    handles: tuple[CppSpecHandle, ...],
) -> dict[str, HandleSpec]:
    return {
        handle.name: HandleSpec(
            name=handle.name,
            cpp_type=handle.cpp_type,
            c_type=handle.c_type,
            destructor=handle.destructor,
            ptr_type=handle.ptr_type,
            empty_check=handle.empty_check,
        )
        for handle in handles
    }


def lower_cpp_spec_result_structs_to_specs(
    structs: tuple[CppSpecResultStruct, ...],
    handles: dict[str, HandleSpec],
    *,
    environment: DiscoveryEnvironment | None = None,
    translation_unit: Path | None = None,
) -> dict[str, ResultStructSpec]:
    result: dict[str, ResultStructSpec] = {
        struct.name: ResultStructSpec(
            name=struct.name,
            cpp_type=struct.cpp_type,
            c_type=struct.c_type,
            fields=(),
        )
        for struct in structs
    }
    for struct in structs:
        semantic_fields = (
            discover_public_fields(environment, translation_unit, struct.cpp_type)
            if environment is not None and translation_unit is not None
            else {}
        )
        fields = tuple(
            ResultStructFieldSpec(
                name=field_name,
                type=_infer_return_type(field_cpp_type, handles, result),
                cpp_field=field_name,
                doc=(
                    semantic_fields[field_name].doc
                    if field_name in semantic_fields
                    else None
                ),
            )
            for field_cpp_type, field_name in struct.fields
        )
        result[struct.name] = ResultStructSpec(
            name=struct.name,
            cpp_type=struct.cpp_type,
            c_type=struct.c_type,
            fields=fields,
        )
    return result


def discover_cpp_spec_option_structs(
    environment: DiscoveryEnvironment,
    translation_unit: Path,
    functions: tuple[CppSpecFunction, ...],
    handles: dict[str, HandleSpec],
    result_structs: dict[str, ResultStructSpec] | None = None,
    *,
    c_prefix: str | None = None,
) -> dict[str, OptionStructSpec]:
    """Discover semantic input option structs from C++ spec function parameters.

    A parameter whose canonical type name ends in `Options` is treated as a
    source-authored options object. The public fields of that struct become the
    binding contract for high-level generated language facades. Lowering to the
    C ABI is intentionally separate so the C-compatible surface can remain
    explicit and stable.
    """
    result_structs = result_structs or {}
    option_structs: dict[str, OptionStructSpec] = {}
    pending: list[tuple[str, str]] = []
    for function in functions:
        for param in function.discovered.params:
            option_name = _option_struct_name(
                param.cpp_type_ref
            ) or _option_sequence_struct_name(param.cpp_type_ref)
            if option_name is None:
                continue
            simple_name, cpp_type = option_name
            if "::" not in cpp_type and function.namespace:
                cpp_type = f"{function.namespace}::{cpp_type}"
            if simple_name in option_structs:
                continue
            option_structs[simple_name] = OptionStructSpec(
                name=simple_name,
                cpp_type=cpp_type,
                c_type=_option_c_type(simple_name, c_prefix),
                fields=(),
            )
            pending.append((simple_name, cpp_type))

    def record_ref(semantic: object) -> tuple[str, str] | None:
        if not isinstance(semantic, RecordSemanticType):
            return None
        normalized_cpp_type = " ".join(semantic.cpp_type.replace(" *", "*").split())
        if normalized_cpp_type.rstrip("&").endswith("*"):
            return None
        qualified = semantic.base_name
        simple = qualified.rsplit("::", 1)[-1]
        if any(
            _canonical_cpp_type(handle.cpp_type) == _canonical_cpp_type(qualified)
            for handle in handles.values()
        ):
            return None
        if any(
            _canonical_cpp_type(struct.cpp_type) == _canonical_cpp_type(qualified)
            for struct in result_structs.values()
        ):
            return None
        return simple, qualified

    def referenced_records(semantic: object) -> tuple[tuple[str, str], ...]:
        if isinstance(semantic, OptionalSemanticType):
            return referenced_records(semantic.element)
        if isinstance(semantic, SequenceSemanticType):
            return referenced_records(semantic.element)
        if isinstance(semantic, VariantSemanticType):
            return tuple(
                item
                for alternative in semantic.alternatives
                for item in referenced_records(alternative)
            )
        ref = record_ref(semantic)
        return (ref,) if ref is not None else ()

    def infer_input_type(cpp_type: object) -> TypeSpec:
        semantic = analyze_cpp_type(cpp_type)
        if isinstance(semantic, OptionalSemanticType):
            inner_cpp_type = (
                cpp_type.template_args[0]
                if isinstance(cpp_type, DiscoveredCppType) and cpp_type.template_args
                else semantic.element.cpp_type
            )
            inner = infer_input_type(inner_cpp_type)
            return TypeSpec(
                **{
                    **inner.__dict__,
                    "nullable": True,
                    "cpp_type": getattr(cpp_type, "storage_spelling", None)
                    or semantic.cpp_type,
                }
            )
        if isinstance(semantic, VariantSemanticType):
            return TypeSpec(
                kind="variant",
                variants=tuple(
                    infer_input_type(alternative.cpp_type)
                    for alternative in semantic.alternatives
                ),
                ownership="copy",
                cpp_type=getattr(cpp_type, "storage_spelling", None)
                or semantic.cpp_type,
            )
        if isinstance(semantic, SequenceSemanticType):
            leaf = semantic_leaf_type(semantic)
            leaf_type = infer_input_type(leaf.cpp_type)
            if leaf_type.kind in {"option", "variant"}:
                return TypeSpec(
                    **{
                        **leaf_type.__dict__,
                        "cpp_type": getattr(cpp_type, "storage_spelling", None)
                        or semantic.cpp_type,
                        "sequence_depth": semantic_sequence_depth(semantic),
                        "alias": semantic_sequence_alias(semantic),
                        "fixed_lengths": semantic_sequence_lengths(semantic),
                    }
                )
        ref = record_ref(semantic)
        if ref is not None and ref[0] in option_structs:
            return TypeSpec(
                kind="option",
                struct=ref[0],
                cpp_type=getattr(cpp_type, "storage_spelling", None)
                or semantic.cpp_type,
            )
        return _infer_param_type(cpp_type, handles)

    processed: set[str] = set()
    while pending:
        simple_name, cpp_type = pending.pop(0)
        if simple_name in processed:
            continue
        discovered_fields = discover_public_fields(
            environment, translation_unit, cpp_type
        ).values()
        discovered_fields = tuple(discovered_fields)
        for field in discovered_fields:
            for child_name, child_cpp_type in referenced_records(
                analyze_cpp_type(field.cpp_type_ref)
            ):
                if child_name not in option_structs:
                    option_structs[child_name] = OptionStructSpec(
                        name=child_name,
                        cpp_type=child_cpp_type,
                        c_type=_option_c_type(child_name, c_prefix),
                        fields=(),
                    )
                    pending.append((child_name, child_cpp_type))
        option_structs[simple_name] = OptionStructSpec(
            name=simple_name,
            cpp_type=cpp_type,
            c_type=option_structs[simple_name].c_type,
            fields=tuple(
                OptionStructFieldSpec(
                    name=field.cpp_name,
                    type=infer_input_type(field.cpp_type_ref),
                    cpp_field=field.cpp_name,
                    doc=field.doc,
                    has_default=(
                        field.cpp_type_ref.template_name == "std::optional"
                        and field.has_initializer
                    ),
                )
                for field in discovered_fields
            ),
        )
        processed.add(simple_name)
    return option_structs
