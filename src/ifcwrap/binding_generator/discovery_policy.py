from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .binding_model import (
    CallSpec,
    DiscoveryDiagnostic,
    HandleSpec,
    OptionStructSpec,
    ParamSpec,
    ResultStructSpec,
    TypeSpec,
)
from .clang_discovery import (
    DiscoveredConstructor,
    DiscoveredCppType,
    DiscoveredField,
    DiscoveredFunction,
    DiscoveredMethod,
    DiscoveredParam,
    DiscoveryEnvironment,
    discover_base_types,
    discover_public_constructors,
    discover_public_fields,
    discover_public_methods,
)
from .debug import debug_log, debug_path
from .policy_ir import (
    ArrayElementFieldPolicyOp,
    AsItemCastPolicyOp,
    BoolOutParamPolicyOp,
    CcomponentsAccessorPolicyOp,
    ChildrenAddPolicyOp,
    ChildrenAtPolicyOp,
    ChildrenCountPolicyOp,
    ConstructorPolicyOp,
    DirectFieldPolicyOp,
    DirectMethodPolicyOp,
    FieldSetterPolicyOp,
    ListAtPolicyOp,
    ListCountPolicyOp,
    MethodAtPolicyOp,
    MethodSizePolicyOp,
    OptionalGetPolicyOp,
    OptionalHasPolicyOp,
    PointerPresencePolicyOp,
    PolicyCallSpec,
    ValueHandleFieldPolicyOp,
    VariantGetPolicyOp,
    VariantSetPolicyOp,
)
from .semantic_types import (
    EnumSemanticType,
    OptionalSemanticType,
    RecordSemanticType,
    ScalarSemanticType,
    SequenceSemanticType,
    StringSemanticType,
    UnsupportedSemanticType,
    VariantSemanticType,
    VoidSemanticType,
    analyze_cpp_type,
    semantic_leaf_type,
    semantic_record_match_names,
    semantic_sequence_alias,
    semantic_sequence_depth,
    semantic_sequence_lengths,
)

_SCALAR_SEQUENCE_FAMILIES = frozenset(
    {"bool", "string", "int32", "int64", "uint8", "uint32", "double"}
)


class AmbiguousHandleMatchError(ValueError):
    """Raised when a C++ type maps to more than one registered handle."""


@dataclass(frozen=True)
class DiscoveryChildrenSpec:
    element_handle: str | None
    count_as: str | None
    at_as: str | None
    cpp_field: str = "children"
    add_as: str | None = None
    add_cast_cpp_type: str | None = None


@dataclass(frozen=True)
class CcomponentsAccessorSpec:
    expose_as: str
    dimensions: int | None  # 3 for vector, 16 for matrix (4x4)
    access_via: str  # e.g. "ccomponents" or "data()->ccomponents"


@dataclass(frozen=True)
class VariantAccessorTypeSpec:
    cpp_type: str
    getter_types: tuple[str, ...]


@dataclass(frozen=True)
class VariantAccessorsSpec:
    get_method: str  # C++ method name for getter (e.g. "get")
    set_method: str  # C++ method name for setter (e.g. "set")
    variant_type: str  # full C++ variant type for constructing set values
    types: dict[
        str, VariantAccessorTypeSpec
    ]  # expose_suffix -> getter/setter type policy


@dataclass(frozen=True)
class MethodAtAccessorSpec:
    method_name: str
    expose_as: str
    item_handle: str
    ownership: str | None
    out_of_range_message: str
    exception_type: str


@dataclass(frozen=True)
class HandleListAccessorsSpec:
    receiver: str
    list_param: str
    item_handle: str
    count_as: str
    at_as: str
    out_of_range_message: str


@dataclass(frozen=True)
class DiscoveryClassSpec:
    handle: str
    translation_unit: str
    exclude: tuple[str, ...]
    rename: dict[str, str]
    discover_fields: bool
    include_inherited_fields: bool
    discover_has_fields: bool
    discover_children: DiscoveryChildrenSpec | None
    discover_as_item: bool
    extra_fields: dict[str, str]  # field_name -> cpp_type (for template classes)
    field_setters: tuple[str, ...]  # field names to generate setters for
    method_sizes: dict[str, str]  # method_name -> expose_as (generates X().size())
    method_at_accessors: tuple[MethodAtAccessorSpec, ...]
    array_pair_fields: dict[
        str, str | None
    ]  # field_name -> optional return_kind for std::array<T,2> split accessors
    ccomponents_accessor: (
        CcomponentsAccessorSpec | None
    )  # generates Eigen ccomponents data extraction
    variant_accessors: (
        VariantAccessorsSpec | None
    )  # generates typed get/set for variant methods
    compile_guard: str | None = None


@dataclass(frozen=True)
class DiscoverySpec:
    include_dir: Path
    classes: tuple[DiscoveryClassSpec, ...]
    constructors: tuple[DiscoveryConstructorSpec, ...]


@dataclass(frozen=True)
class DiscoveryConstructorSpec:
    handle: str
    cpp_class: str
    translation_unit: str
    expose_as: str
    params: tuple[str, ...] | None
    param_names: tuple[str, ...]
    param_renames: dict[str, str]
    compile_guard: str | None
    compile_guard_message: str | None


@dataclass(frozen=True)
class DiscoveryOverloadSpec:
    cpp_name: str
    expose_as: str
    params: tuple[str, ...]


@dataclass(frozen=True)
class MergedBindingSpec:
    """A merged binding spec containing multiple modules."""

    module: str  # Common module name (e.g., "ifcopenshell")
    c_prefix: str  # Common C prefix (e.g., "ifcopenshell")
    public_headers: tuple[str, ...]  # Merged public headers
    handles: dict[str, HandleSpec]  # All handles from all modules
    result_structs: dict[str, ResultStructSpec]
    functions: tuple[CallSpec, ...]  # All functions from all modules
    methods: tuple[CallSpec, ...]  # All methods from all modules
    option_structs: dict[str, OptionStructSpec] = field(default_factory=dict)


def _handle_list_accessor_calls(
    *,
    list_handle_name: str,
    accessors: HandleListAccessorsSpec,
    handles: dict[str, HandleSpec],
) -> tuple[CallSpec, CallSpec]:
    if accessors.receiver not in handles:
        msg = f"list accessors for '{list_handle_name}' refer to unknown receiver handle '{accessors.receiver}'"
        raise ValueError(msg)
    if accessors.item_handle not in handles:
        msg = f"list accessors for '{list_handle_name}' refer to unknown item handle '{accessors.item_handle}'"
        raise ValueError(msg)

    list_type = TypeSpec(kind="handle", handle=list_handle_name, ownership="borrowed")
    item_handle = handles[accessors.item_handle]
    item_type = TypeSpec(
        kind="handle",
        handle=accessors.item_handle,
        ownership="owned",
        cpp_type=f"{item_handle.cpp_type}*",
    )
    list_param = ParamSpec(name=accessors.list_param, type=list_type)
    index_param = ParamSpec(name="index", type=TypeSpec(kind="size"))
    receiver = handles[accessors.receiver]

    count_call = PolicyCallSpec(
        expose_as=accessors.count_as,
        receiver=accessors.receiver,
        returns=TypeSpec(kind="size"),
        params=(list_param,),
        operation=ListCountPolicyOp(list_param=accessors.list_param),
    )
    at_call = PolicyCallSpec(
        expose_as=accessors.at_as,
        receiver=accessors.receiver,
        returns=item_type,
        params=(list_param, index_param),
        operation=ListAtPolicyOp(
            list_param=accessors.list_param,
            item_cpp_type=item_handle.cpp_type,
            out_of_range_message=accessors.out_of_range_message,
        ),
    )
    return (
        _materialize_policy_call(
            count_call, c_name=_make_c_name(receiver, count_call.expose_as)
        ),
        _materialize_policy_call(
            at_call, c_name=_make_c_name(receiver, at_call.expose_as)
        ),
    )


def _normalize_cpp_type(cpp_type: str) -> str:
    cpp_type = re.sub(r"/\*.*?\*/", "", cpp_type)
    cpp_type = " ".join(cpp_type.replace(" &", "&").replace(" *", "*").split())
    cpp_type = (
        cpp_type.replace("< ", "<")
        .replace(" >", ">")
        .replace(", ", ", ")
        .replace(" ,", ",")
    )
    cpp_type = cpp_type.replace("const ", "").strip()
    return cpp_type


def _cpp_type_contains_handle_item(cpp_type: str, handle_cpp_type: str) -> bool:
    normalized = _normalize_cpp_type(cpp_type)
    normalized_handle = _normalize_cpp_type(handle_cpp_type)
    if normalized_handle in normalized:
        return True
    simple = normalized_handle
    shared_ptr_match = re.fullmatch(r"std::shared_ptr<\s*(.+?)\s*>", simple)
    if shared_ptr_match:
        simple = shared_ptr_match.group(1)
    simple = simple.removesuffix("::ptr").removesuffix("*").removesuffix("&").strip()
    simple = simple.split("::")[-1]
    return bool(
        simple
        and re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(simple)}(?![A-Za-z0-9_])", normalized
        )
    )


def _cpp_type_variants(cpp_type: str | DiscoveredCppType) -> tuple[str, ...]:
    if isinstance(cpp_type, DiscoveredCppType):
        ordered = [
            cpp_type.canonical_spelling,
            cpp_type.normalized_desugared_spelling,
            cpp_type.normalized_spelling,
            cpp_type.desugared_spelling,
            cpp_type.spelling,
        ]
    else:
        normalized = _normalize_cpp_type(cpp_type)
        ordered = [normalized, cpp_type]
    variants: list[str] = []
    seen: set[str] = set()
    for value in ordered:
        if not value:
            continue
        normalized_value = _normalize_cpp_type(value)
        if normalized_value in seen:
            continue
        seen.add(normalized_value)
        variants.append(normalized_value)
    return tuple(variants)


def _cpp_type_debug(cpp_type: str | DiscoveredCppType) -> str:
    if isinstance(cpp_type, DiscoveredCppType):
        if cpp_type.desugared_spelling and _normalize_cpp_type(
            cpp_type.desugared_spelling
        ) != _normalize_cpp_type(cpp_type.spelling):
            return f"{cpp_type.spelling} -> {cpp_type.desugared_spelling}"
        return cpp_type.spelling
    return cpp_type


def _cpp_type_storage(cpp_type: str | DiscoveredCppType) -> str:
    if isinstance(cpp_type, DiscoveredCppType):
        return (
            cpp_type.storage_spelling
            or cpp_type.canonical_spelling
            or cpp_type.normalized_spelling
            or cpp_type.spelling
        )
    return _normalize_cpp_type(cpp_type)


def _qualified_name_suffixes(name: str) -> tuple[str, ...]:
    normalized = _normalize_cpp_type(name)
    parts = [part for part in normalized.split("::") if part]
    if not parts:
        return tuple()
    return tuple("::".join(parts[index:]) for index in range(len(parts)))


def _cpp_type_names_match(candidate: str, target: str) -> bool:
    candidate_suffixes = set(_qualified_name_suffixes(candidate))
    target_suffixes = set(_qualified_name_suffixes(target))
    return bool(
        candidate_suffixes
        and target_suffixes
        and candidate_suffixes.intersection(target_suffixes)
    )


def _find_handle_for_cpp_type(
    cpp_type: str | DiscoveredCppType, handles: dict[str, HandleSpec]
) -> str | None:
    bases = [
        variant.removesuffix("&").removesuffix("*").strip().removeprefix("const ")
        for variant in _cpp_type_variants(cpp_type)
    ]
    seen_bases: set[str] = set()
    ordered_bases: list[str] = []
    for base in bases:
        if base and base not in seen_bases:
            seen_bases.add(base)
            ordered_bases.append(base)
    fallback_bases: tuple[str, ...] = ()
    if isinstance(cpp_type, DiscoveredCppType):
        fallback_bases = tuple(
            base
            for base in cpp_type.base_record_names
            if base and base not in seen_bases
        )

    matches: set[str] = set()
    for base in (*ordered_bases, *fallback_bases):
        for handle_name, handle in handles.items():
            if _cpp_type_names_match(handle.cpp_type, base):
                matches.add(handle_name)
        if base.endswith("::ptr"):
            sp_base = base.removesuffix("::ptr")
            for handle_name, handle in handles.items():
                if _cpp_type_names_match(handle.cpp_type, sp_base):
                    matches.add(handle_name)
        m = re.match(r"(?:const\s+)?(?:(?:std|boost)::)?shared_ptr<\s*(.+?)\s*>", base)
        if m:
            inner = m.group(1).removeprefix("const ").strip()
            for handle_name, handle in handles.items():
                if _cpp_type_names_match(handle.cpp_type, inner):
                    matches.add(handle_name)
    if len(matches) > 1:
        msg = (
            f"C++ type '{_cpp_type_debug(cpp_type)}' matches multiple registered handles: "
            f"{', '.join(sorted(matches))}"
        )
        raise AmbiguousHandleMatchError(msg)
    return next(iter(matches), None)


def _type_spec_from_record_semantic(
    semantic: RecordSemanticType,
    *,
    handles: dict[str, HandleSpec],
    ownership: str,
    nullable: bool,
    own_shared_ptr: bool = False,
) -> TypeSpec | None:
    match_names = list(semantic_record_match_names(semantic))
    if semantic.pointer_wrapper is not None and semantic.pointee is not None:
        match_names.insert(0, semantic.pointee.cpp_type)
    for match_name in match_names:
        handle_name = _find_handle_for_cpp_type(match_name, handles)
        if handle_name is not None:
            is_shared_ptr = (
                semantic.pointer_wrapper == "shared_ptr"
                or _normalize_cpp_type(semantic.cpp_type).endswith("::ptr")
            )
            normalized = _normalize_cpp_type(semantic.cpp_type)
            is_reference = normalized.endswith("&") or normalized.endswith("&&")
            is_raw_pointer = semantic.pointer_wrapper is None and normalized.endswith(
                "*"
            )
            is_nullable_pointer = semantic.pointer_wrapper == "unique_ptr"
            resolved_ownership = (
                "owned"
                if semantic.pointer_wrapper == "unique_ptr"
                or (own_shared_ptr and is_shared_ptr)
                or (not is_reference and not is_raw_pointer)
                else ownership
            )
            return TypeSpec(
                kind="handle",
                handle=handle_name,
                ownership=resolved_ownership,
                nullable=nullable or is_nullable_pointer,
                cpp_type=semantic.cpp_type,
            )
    return None


def _type_spec_from_result_struct_semantic(
    semantic: RecordSemanticType,
    result_structs: dict[str, ResultStructSpec],
) -> TypeSpec | None:
    for match_name in semantic_record_match_names(semantic):
        for struct_name, struct in result_structs.items():
            if _cpp_type_names_match(struct.cpp_type, match_name):
                return TypeSpec(
                    kind="struct", struct=struct_name, cpp_type=semantic.cpp_type
                )
    return None


def _sequence_leaf_kind(semantic: ScalarSemanticType | StringSemanticType) -> str:
    if isinstance(semantic, StringSemanticType):
        return "string"
    return semantic.family


def _lower_generic_sequence_type(
    semantic: SequenceSemanticType,
    *,
    handles: dict[str, HandleSpec],
    ownership: str,
    result_structs: dict[str, ResultStructSpec] | None = None,
) -> TypeSpec | None:
    leaf = semantic_leaf_type(semantic)
    depth = semantic_sequence_depth(semantic)
    sequence_metadata = {
        "alias": semantic_sequence_alias(semantic),
        "fixed_lengths": semantic_sequence_lengths(semantic),
    }

    if isinstance(leaf, RecordSemanticType):
        result_spec = _type_spec_from_result_struct_semantic(leaf, result_structs or {})
        if result_spec is not None:
            return TypeSpec(
                kind="struct",
                struct=result_spec.struct,
                ownership="copy",
                cpp_type=semantic.cpp_type,
                sequence_depth=depth,
                **sequence_metadata,
            )
        record_spec = _type_spec_from_record_semantic(
            leaf, handles=handles, ownership=ownership, nullable=False
        )
        if record_spec is None:
            reparsed_leaf = analyze_cpp_type(leaf.cpp_type)
            if isinstance(reparsed_leaf, RecordSemanticType):
                record_spec = _type_spec_from_record_semantic(
                    reparsed_leaf, handles=handles, ownership=ownership, nullable=False
                )
        if record_spec is None:
            return None
        return TypeSpec(
            kind="handle",
            handle=record_spec.handle,
            ownership=record_spec.ownership,
            cpp_type=semantic.cpp_type,
            sequence_depth=depth,
            **sequence_metadata,
        )

    if isinstance(leaf, StringSemanticType):
        return TypeSpec(
            kind="string",
            ownership="copy",
            cpp_type=semantic.cpp_type,
            sequence_depth=depth,
            **sequence_metadata,
        )

    if isinstance(leaf, ScalarSemanticType):
        if leaf.family in _SCALAR_SEQUENCE_FAMILIES:
            return TypeSpec(
                kind=_sequence_leaf_kind(leaf),
                ownership="copy",
                cpp_type=semantic.cpp_type,
                sequence_depth=depth,
                **sequence_metadata,
            )
    return None


def _infer_type(
    cpp_type: str | DiscoveredCppType,
    handles: dict[str, HandleSpec],
    *,
    ownership: str,
    nullable_pointers: bool,
    own_shared_ptr: bool = False,
    nullable_string_pointers: bool = False,
    result_structs: dict[str, ResultStructSpec] | None = None,
) -> TypeSpec:
    result_structs = result_structs or {}
    semantic = analyze_cpp_type(cpp_type)
    if isinstance(semantic, VoidSemanticType):
        return TypeSpec(kind="void", cpp_type=_cpp_type_storage(cpp_type))
    if isinstance(semantic, EnumSemanticType):
        return TypeSpec(
            kind="int32",
            cpp_type=_cpp_type_storage(cpp_type),
            alias=(semantic.enum_qualified_name or semantic.cpp_type).rsplit("::", 1)[
                -1
            ],
            enum_values=tuple(name for name, _ in semantic.values),
            enum_numeric_values=tuple(value for _, value in semantic.values),
        )
    if isinstance(semantic, StringSemanticType):
        nullable = nullable_string_pointers and _normalize_cpp_type(
            semantic.cpp_type
        ).endswith("*")
        return TypeSpec(
            kind="string",
            ownership="copy",
            nullable=nullable,
            cpp_type=_cpp_type_storage(cpp_type),
        )
    if isinstance(semantic, OptionalSemanticType):
        inner_cpp_type = (
            cpp_type.template_args[0]
            if isinstance(cpp_type, DiscoveredCppType) and cpp_type.template_args
            else semantic.element.cpp_type
        )
        inner = _infer_type(
            inner_cpp_type,
            handles,
            ownership=ownership,
            nullable_pointers=True,
            own_shared_ptr=own_shared_ptr,
            result_structs=result_structs,
        )
        return TypeSpec(
            kind=inner.kind,
            handle=inner.handle,
            struct=inner.struct,
            variants=inner.variants,
            ownership=inner.ownership,
            nullable=True,
            cpp_type=_cpp_type_storage(cpp_type),
            sequence_depth=inner.sequence_depth,
            alias=inner.alias,
            fixed_lengths=inner.fixed_lengths,
            enum_values=inner.enum_values,
            enum_numeric_values=inner.enum_numeric_values,
            literal_value=inner.literal_value,
        )
    if isinstance(semantic, VariantSemanticType):
        alternatives = tuple(
            _infer_type(
                alternative.cpp_type,
                handles,
                ownership=ownership,
                nullable_pointers=False,
                own_shared_ptr=own_shared_ptr,
                result_structs=result_structs,
            )
            for alternative in semantic.alternatives
        )
        return TypeSpec(
            kind="variant",
            variants=alternatives,
            ownership="copy",
            cpp_type=_cpp_type_storage(cpp_type),
        )
    if isinstance(semantic, ScalarSemanticType):
        scalar_kind = {
            "bool": "bool",
            "int32": "int32",
            "int64": "int64",
            "uint32": "uint32",
            "size": "size",
            "double": "double",
        }.get(semantic.family)
        if scalar_kind is not None:
            return TypeSpec(kind=scalar_kind, cpp_type=_cpp_type_storage(cpp_type))
    if isinstance(semantic, RecordSemanticType):
        struct_spec = _type_spec_from_result_struct_semantic(semantic, result_structs)
        if struct_spec is not None:
            return struct_spec
        record_spec = _type_spec_from_record_semantic(
            semantic,
            handles=handles,
            ownership=ownership,
            nullable=nullable_pointers
            and _normalize_cpp_type(semantic.cpp_type).endswith("*"),
            own_shared_ptr=own_shared_ptr,
        )
        if record_spec is not None:
            return record_spec
    if isinstance(semantic, SequenceSemanticType):
        for handle_name, handle in handles.items():
            if _cpp_type_names_match(handle.cpp_type, semantic.cpp_type):
                normalized = _normalize_cpp_type(semantic.cpp_type)
                return TypeSpec(
                    kind="handle",
                    handle=handle_name,
                    ownership="owned"
                    if not normalized.endswith("&") and not normalized.endswith("*")
                    else ownership,
                    cpp_type=_cpp_type_storage(cpp_type),
                )
        sequence_spec = _lower_generic_sequence_type(
            semantic,
            handles=handles,
            ownership=ownership,
            result_structs=result_structs,
        )
        if sequence_spec is None:
            reparsed_sequence = analyze_cpp_type(semantic.cpp_type)
            if (
                isinstance(reparsed_sequence, SequenceSemanticType)
                and reparsed_sequence != semantic
            ):
                sequence_spec = _lower_generic_sequence_type(
                    reparsed_sequence,
                    handles=handles,
                    ownership=ownership,
                    result_structs=result_structs,
                )
        if sequence_spec is not None:
            return sequence_spec
    if (
        isinstance(semantic, UnsupportedSemanticType)
        and semantic.reason == "opaque void pointer/reference"
        and semantic.cpp_type.strip().startswith("const void")
    ):
        return TypeSpec(
            kind="opaque_ptr",
            cpp_type=_cpp_type_storage(cpp_type),
            nullable=nullable_pointers
            and _normalize_cpp_type(semantic.cpp_type).endswith("*"),
        )
    msg = f"Unsupported discovered type '{_cpp_type_debug(cpp_type)}'"
    raise ValueError(msg)


def _infer_return_type(
    cpp_type: str | DiscoveredCppType,
    handles: dict[str, HandleSpec],
    result_structs: dict[str, ResultStructSpec] | None = None,
) -> TypeSpec:
    try:
        return _infer_type(
            cpp_type,
            handles,
            ownership="borrowed",
            nullable_pointers=True,
            own_shared_ptr=True,
            result_structs=result_structs,
        )
    except ValueError as exc:
        msg = str(exc).replace(
            "Unsupported discovered type", "Unsupported discovered return type"
        )
        raise ValueError(msg) from exc


def _infer_param_type(
    cpp_type: str | DiscoveredCppType, handles: dict[str, HandleSpec]
) -> TypeSpec:
    try:
        return _infer_type(
            cpp_type,
            handles,
            ownership="borrowed",
            nullable_pointers=False,
            nullable_string_pointers=True,
        )
    except ValueError as exc:
        msg = str(exc).replace(
            "Unsupported discovered type", "Unsupported discovered parameter type"
        )
        raise ValueError(msg) from exc


def _is_nonconst_lvalue_ref(cpp_type: DiscoveredCppType) -> bool:
    return cpp_type.is_lvalue_reference and not cpp_type.is_const


def _bool_out_param_signature(
    discovered: DiscoveredMethod | DiscoveredFunction,
    handles: dict[str, HandleSpec],
) -> tuple[TypeSpec, tuple[ParamSpec, ...], BoolOutParamPolicyOp] | None:
    if (
        _normalize_cpp_type(discovered.return_cpp_type) != "bool"
        or len(discovered.params) != 1
    ):
        return None
    out_param = discovered.params[0]
    if not _is_nonconst_lvalue_ref(out_param.cpp_type_ref):
        return None
    returns = _infer_param_type(out_param.cpp_type_ref, handles)
    if (
        returns.kind not in {"bool", "int32", "int64", "uint32", "size", "double"}
        or returns.sequence_depth
    ):
        return None
    return (
        TypeSpec(kind=returns.kind, cpp_type=returns.cpp_type),
        tuple(),
        BoolOutParamPolicyOp(
            cpp_name=discovered.cpp_name, out_param_cpp_type=out_param.cpp_type
        ),
    )


def _direct_method_policy_operation(
    discovered: DiscoveredMethod,
    handles: dict[str, HandleSpec],
) -> object:
    bool_out_param = _bool_out_param_signature(discovered, handles)
    if bool_out_param is not None:
        return bool_out_param[2]
    return DirectMethodPolicyOp(cpp_name=discovered.cpp_name)


def _infer_method_signature(
    discovered: DiscoveredMethod,
    *,
    handles: dict[str, HandleSpec],
) -> tuple[TypeSpec, tuple[ParamSpec, ...]]:
    bool_out_param = _bool_out_param_signature(discovered, handles)
    if bool_out_param is not None:
        return bool_out_param[0], bool_out_param[1]
    return (
        _infer_return_type(discovered.return_type_ref, handles),
        tuple(
            ParamSpec(
                name=param.name,
                type=_infer_param_type(param.cpp_type_ref, handles),
            )
            for param in discovered.params
        ),
    )


def _make_c_name(handle: HandleSpec, expose_as: str) -> str:
    receiver = handle.c_type.removeprefix("ifcopenshell_").removesuffix("_t")
    return f"ifcopenshell_{receiver}_{expose_as}"


def _simple_type_spec(kind_str: str) -> TypeSpec:
    """Create a TypeSpec from a simple kind string (e.g. 'int32', 'double_list')."""
    match = re.fullmatch(r"([a-z0-9]+)((?:_list)+)", kind_str)
    if match is not None and match.group(1) in _SCALAR_SEQUENCE_FAMILIES:
        return TypeSpec(
            kind=match.group(1),
            ownership="copy",
            sequence_depth=match.group(2).count("_list"),
        )
    return TypeSpec(kind=kind_str)


def _infer_array_pair_element_type(
    field: DiscoveredField, handles: dict[str, HandleSpec]
) -> TypeSpec:
    type_ref = field.cpp_type_ref
    if type_ref.template_name != "std::array" or len(type_ref.template_args) != 2:
        msg = f"array_pair_fields entry '{field.cpp_name}' must refer to std::array<T, 2>, got '{field.cpp_type}'"
        raise ValueError(msg)
    size_arg = (
        type_ref.template_args[1].storage_spelling or type_ref.template_args[1].spelling
    )
    if size_arg.strip() != "2":
        msg = f"array_pair_fields entry '{field.cpp_name}' must refer to std::array<T, 2>, got '{field.cpp_type}'"
        raise ValueError(msg)
    return _infer_return_type(type_ref.template_args[0], handles)


def _variant_accessor_type_spec(
    cpp_type: str, handles: dict[str, HandleSpec]
) -> TypeSpec | None:
    try:
        inferred = _infer_type(
            cpp_type, handles, ownership="copy", nullable_pointers=False
        )
    except ValueError:
        return None
    if inferred.sequence_depth == 0:
        if inferred.kind in {"bool", "int32", "int64", "double", "string"}:
            return TypeSpec(kind=inferred.kind)
        return None
    if inferred.sequence_depth == 1 and inferred.kind in {"int32", "double", "string"}:
        return TypeSpec(
            kind=inferred.kind, ownership="copy", cpp_type=cpp_type, sequence_depth=1
        )
    return None


def _make_function_c_name(prefix: str, expose_as: str) -> str:
    return f"{prefix}_{expose_as}"


def _append_discovery_diagnostic(
    diagnostics: list[DiscoveryDiagnostic],
    *,
    owner: str,
    member: str,
    code: str,
    message: str,
) -> None:
    diagnostics.append(
        DiscoveryDiagnostic(owner=owner, member=member, code=code, message=message)
    )


def _register_generated_call(
    call: CallSpec,
    *,
    calls: list[CallSpec],
    calls_by_c_name: dict[str, CallSpec],
    diagnostics: list[DiscoveryDiagnostic],
    owner: str,
    member: str,
) -> bool:
    existing = calls_by_c_name.get(call.c_name)
    if existing is not None:
        if existing != call:
            _append_discovery_diagnostic(
                diagnostics,
                owner=owner,
                member=member,
                code="generated_name_collision",
                message=f"Skipped generated call '{call.c_name}' because another generated call already uses that name",
            )
        return False
    calls_by_c_name[call.c_name] = call
    calls.append(call)
    return True


def _register_policy_call(
    policy_call: PolicyCallSpec,
    *,
    handle: HandleSpec | None,
    c_prefix: str = "ifcopenshell",
    calls: list[CallSpec],
    calls_by_c_name: dict[str, CallSpec],
    diagnostics: list[DiscoveryDiagnostic],
    owner: str,
    member: str,
) -> bool:
    if handle is None:
        c_name = _make_function_c_name(c_prefix, policy_call.expose_as)
    else:
        c_name = _make_c_name(handle, policy_call.expose_as)
    call = _materialize_policy_call(policy_call, c_name=c_name)
    return _register_generated_call(
        call,
        calls=calls,
        calls_by_c_name=calls_by_c_name,
        diagnostics=diagnostics,
        owner=owner,
        member=member,
    )


def _materialize_policy_call(
    call: PolicyCallSpec,
    *,
    c_name: str,
) -> CallSpec:
    return CallSpec(
        expose_as=call.expose_as,
        c_name=c_name,
        receiver=call.receiver,
        returns=call.returns,
        params=call.params,
        policy_operation=call.operation,
    )


def _snake_case_identifier(name: str) -> str:
    chars: list[str] = []
    previous_is_lower_or_digit = False
    for index, char in enumerate(name):
        if char == ":":
            continue
        if char == "_":
            chars.append(char)
            previous_is_lower_or_digit = False
            continue
        is_upper = char.isalpha() and char.upper() == char and char.lower() != char
        next_is_lower = index + 1 < len(name) and name[index + 1].islower()
        if chars and is_upper and (previous_is_lower_or_digit or next_is_lower):
            chars.append("_")
        chars.append(char.lower())
        previous_is_lower_or_digit = char.islower() or char.isdigit()
    return "".join(chars)


def _select_overload(
    overloads: tuple[DiscoveredMethod, ...] | tuple[DiscoveredFunction, ...],
    spec: DiscoveryOverloadSpec,
):
    target_params = tuple(_normalize_cpp_type(param) for param in spec.params)
    for overload in overloads:
        overload_params = tuple(
            _normalize_cpp_type(param.cpp_type) for param in overload.params
        )
        if overload.cpp_name == spec.cpp_name and overload_params == target_params:
            return overload
    candidates = ", ".join(
        f"{overload.cpp_name}({', '.join(param.cpp_type for param in overload.params)})"
        for overload in overloads
        if overload.cpp_name == spec.cpp_name
    )
    msg = f"Unable to resolve overload '{spec.cpp_name}({', '.join(spec.params)})'"
    if candidates:
        msg += f"; discovered: {candidates}"
    raise ValueError(msg)


def _extract_optional_inner_type(
    cpp_type: str | DiscoveredCppType,
) -> str | DiscoveredCppType | None:
    """Extract T from std::optional<T>. Returns None if not optional."""
    if isinstance(cpp_type, DiscoveredCppType):
        if (
            cpp_type.template_name == "std::optional"
            and len(cpp_type.template_args) == 1
        ):
            return cpp_type.template_args[0]
        normalized = cpp_type.canonical_spelling
    else:
        normalized = _normalize_cpp_type(cpp_type)
    prefix = "std::optional<"
    if normalized.startswith(prefix) and normalized.endswith(">"):
        return normalized[len(prefix) : -1].strip()
    return None


def _constructor_signature_debug(constructor: DiscoveredConstructor) -> str:
    params = ", ".join(
        _cpp_type_debug(param.cpp_type_ref) for param in constructor.params
    )
    return f"{constructor.cpp_name}({params})"


def _simple_cpp_name(name: str) -> str:
    return name.rsplit("::", 1)[-1]


def _children_stem(cpp_field: str, element_handle: str) -> str:
    if cpp_field != "children":
        stem = _snake_case_identifier(cpp_field)
        if stem.endswith("ies"):
            return f"{stem[:-3]}y"
        if stem.endswith("s"):
            return stem[:-1]
        return stem
    stem = element_handle
    if stem.startswith("taxonomy_"):
        stem = stem[len("taxonomy_") :]
    return stem


def _handle_from_child_type(
    cpp_type: str | DiscoveredCppType, handles: dict[str, HandleSpec]
) -> str | None:
    try:
        inferred = _infer_return_type(cpp_type, handles)
    except AmbiguousHandleMatchError:
        raise
    except ValueError:
        return None
    if inferred.kind == "handle":
        return inferred.handle
    return None


def _collection_base_child_handle(
    item: DiscoveryClassSpec,
    handle: HandleSpec,
    *,
    handles: dict[str, HandleSpec],
    discovery_environment: DiscoveryEnvironment,
    include_dir: Path,
) -> str | None:
    translation_unit = (include_dir / item.translation_unit).resolve()
    for base in discover_base_types(
        discovery_environment, translation_unit, handle.cpp_type
    ):
        if _simple_cpp_name(base.cpp_type_ref.template_name or "") != "collection_base":
            continue
        if not base.cpp_type_ref.template_args:
            continue
        child_handle = _handle_from_child_type(
            base.cpp_type_ref.template_args[0], handles
        )
        if child_handle is not None:
            return child_handle
    return None


def _infer_children_element_handle(
    item: DiscoveryClassSpec,
    handle: HandleSpec,
    dc: DiscoveryChildrenSpec,
    *,
    handles: dict[str, HandleSpec],
    class_cache: dict[object, object],
    discovery_environment: DiscoveryEnvironment,
    include_dir: Path,
) -> str:
    field_cache_key = ("fields", handle.cpp_type, item.translation_unit, True)
    fields_by_name = class_cache.get(field_cache_key)
    if fields_by_name is None:
        translation_unit = (include_dir / item.translation_unit).resolve()
        fields_by_name = discover_public_fields(
            discovery_environment,
            translation_unit,
            handle.cpp_type,
            include_inherited=True,
        )
        class_cache[field_cache_key] = fields_by_name
    field = fields_by_name.get(dc.cpp_field)
    if field is None:
        msg = f"discover_children field '{dc.cpp_field}' was not discovered on {item.handle}"
        raise ValueError(msg)
    type_ref = field.cpp_type_ref
    if (
        _simple_cpp_name(type_ref.template_name or "") != "vector"
        or len(type_ref.template_args) != 1
    ):
        msg = (
            f"discover_children field '{dc.cpp_field}' must be a vector-like child field, "
            f"got '{field.cpp_type}' (desugared '{type_ref.desugared_spelling}', "
            f"template arguments {len(type_ref.template_args)})"
        )
        raise ValueError(msg)
    element_type = type_ref.template_args[0]
    if _simple_cpp_name(element_type.template_name or "") == "vector":
        msg = f"discover_children field '{dc.cpp_field}' is nested and cannot be inferred safely"
        raise ValueError(msg)
    child_handle = _handle_from_child_type(element_type, handles)
    if child_handle is not None:
        return child_handle
    if element_type.storage_spelling.endswith(
        "T::ptr"
    ) or element_type.spelling.endswith("T::ptr"):
        child_handle = _collection_base_child_handle(
            item,
            handle,
            handles=handles,
            discovery_environment=discovery_environment,
            include_dir=include_dir,
        )
        if child_handle is not None:
            return child_handle
    msg = f"Unable to infer discover_children element handle for field '{dc.cpp_field}' on {item.handle}"
    raise ValueError(msg)


def _eigen_matrix_dimensions(cpp_type: str | DiscoveredCppType) -> int | None:
    if isinstance(cpp_type, DiscoveredCppType):
        if (
            _simple_cpp_name(cpp_type.template_name or "") == "Matrix"
            and len(cpp_type.template_args) == 3
        ):
            rows = cpp_type.template_args[1].storage_spelling
            cols = cpp_type.template_args[2].storage_spelling
            if rows.isdigit() and cols.isdigit():
                return int(rows) * int(cols)
        candidates = (
            cpp_type.storage_spelling,
            cpp_type.normalized_desugared_spelling,
            cpp_type.desugared_spelling,
            cpp_type.normalized_spelling,
            cpp_type.spelling,
        )
    else:
        candidates = (cpp_type,)
    for candidate in candidates:
        if not candidate:
            continue
        match = re.fullmatch(
            r"Eigen::Matrix<\s*double\s*,\s*(\d+)\s*,\s*(\d+)\s*>", candidate
        )
        if match is not None:
            return int(match.group(1)) * int(match.group(2))
    return None


def _access_path_method_names(access_via: str) -> tuple[str, ...]:
    parts = re.split(r"(?:->|\.)", access_via.replace(" ", ""))
    if not parts or any(
        not re.fullmatch(r"[A-Za-z_]\w*(?:\(\))?", part) for part in parts
    ):
        msg = f"Unable to infer ccomponents dimensions from access path '{access_via}'"
        raise ValueError(msg)
    return tuple(part.removesuffix("()") for part in parts)


def _infer_ccomponents_dimensions(
    item: DiscoveryClassSpec,
    handle: HandleSpec,
    *,
    handles: dict[str, HandleSpec],
    discovery_environment: DiscoveryEnvironment,
    include_dir: Path,
) -> int:
    if item.ccomponents_accessor is None:
        raise ValueError("ccomponents_accessor is not configured")
    translation_unit = (include_dir / item.translation_unit).resolve()
    current_cpp_type = handle.cpp_type
    access_parts = _access_path_method_names(item.ccomponents_accessor.access_via)
    for member_name in access_parts[:-1]:
        methods = discover_public_methods(
            discovery_environment,
            translation_unit,
            current_cpp_type,
            include_inherited=True,
            selected_names=(member_name,),
        )
        candidates = tuple(
            method for method in methods.get(member_name, ()) if not method.params
        )
        if len(candidates) != 1:
            msg = (
                f"Unable to infer ccomponents dimensions for {item.handle}: access path member "
                f"'{member_name}' is not an unambiguous zero-argument method"
            )
            raise ValueError(msg)
        next_handle = _find_handle_for_cpp_type(candidates[0].return_type_ref, handles)
        if next_handle is None:
            msg = (
                f"Unable to infer ccomponents dimensions for {item.handle}: access path member "
                f"'{member_name}' returns an unregistered handle type"
            )
            raise ValueError(msg)
        current_cpp_type = handles[next_handle].cpp_type

    visited: set[str] = set()
    queue = [current_cpp_type]
    while queue:
        class_name = queue.pop(0)
        if class_name in visited:
            continue
        visited.add(class_name)
        for base in discover_base_types(
            discovery_environment, translation_unit, class_name
        ):
            if (
                _simple_cpp_name(base.cpp_type_ref.template_name or "") == "eigen_base"
                and base.cpp_type_ref.template_args
            ):
                dimensions = _eigen_matrix_dimensions(
                    base.cpp_type_ref.template_args[0]
                )
                if dimensions is not None:
                    return dimensions
            if (
                base.cpp_type_ref.base_name
                and base.cpp_type_ref.base_name not in visited
            ):
                queue.append(base.cpp_type_ref.base_name)
    msg = f"Unable to infer ccomponents dimensions for {item.handle}"
    raise ValueError(msg)


def _emit_optional_field_calls(
    item: DiscoveryClassSpec,
    handle: HandleSpec,
    field_name: str,
    cpp_name: str,
    inner_cpp_type: str,
    handles: dict[str, HandleSpec],
    calls: list[CallSpec],
    calls_by_c_name: dict[str, CallSpec],
    diagnostics: list[DiscoveryDiagnostic],
) -> None:
    """Generate has_X / X pair for a std::optional<T> field."""
    try:
        returns = _infer_return_type(inner_cpp_type, handles)
    except ValueError:
        _append_discovery_diagnostic(
            diagnostics,
            owner=item.handle,
            member=field_name,
            code="unsupported_optional_inner_type",
            message=f"Skipped optional field '{field_name}' because inner type '{inner_cpp_type}' is not supported",
        )
        return

    expose_as = item.rename.get(field_name, _snake_case_identifier(field_name))

    # has_X
    has_expose = f"has_{expose_as}"
    has_call = PolicyCallSpec(
        expose_as=has_expose,
        receiver=item.handle,
        returns=TypeSpec(kind="bool", cpp_type=None),
        params=(),
        operation=OptionalHasPolicyOp(field_name=cpp_name),
    )
    _register_policy_call(
        has_call,
        handle=handle,
        calls=calls,
        calls_by_c_name=calls_by_c_name,
        diagnostics=diagnostics,
        owner=item.handle,
        member=field_name,
    )

    # X (the getter)
    get_call = PolicyCallSpec(
        expose_as=expose_as,
        receiver=item.handle,
        returns=returns,
        params=(),
        operation=OptionalGetPolicyOp(field_name=cpp_name),
    )
    _register_policy_call(
        get_call,
        handle=handle,
        calls=calls,
        calls_by_c_name=calls_by_c_name,
        diagnostics=diagnostics,
        owner=item.handle,
        member=field_name,
    )


def _emit_children_calls(
    item: DiscoveryClassSpec,
    handle: HandleSpec,
    handles: dict[str, HandleSpec],
    class_cache: dict[object, object],
    discovery_environment: DiscoveryEnvironment,
    include_dir: Path,
    calls: list[CallSpec],
    calls_by_c_name: dict[str, CallSpec],
    diagnostics: list[DiscoveryDiagnostic],
) -> None:
    dc = item.discover_children
    if dc is None:
        return

    element_handle = dc.element_handle or _infer_children_element_handle(
        item,
        handle,
        dc,
        handles=handles,
        class_cache=class_cache,
        discovery_environment=discovery_environment,
        include_dir=include_dir,
    )
    stem = _children_stem(dc.cpp_field, element_handle)
    count_as = dc.count_as or f"{stem}_count"
    at_as = dc.at_as or f"{stem}_at"

    count_call = PolicyCallSpec(
        expose_as=count_as,
        receiver=item.handle,
        returns=TypeSpec(
            kind="size", handle=None, ownership=None, nullable=False, cpp_type=None
        ),
        params=(),
        operation=ChildrenCountPolicyOp(field_name=dc.cpp_field),
    )
    _register_policy_call(
        count_call,
        handle=handle,
        calls=calls,
        calls_by_c_name=calls_by_c_name,
        diagnostics=diagnostics,
        owner=item.handle,
        member=dc.cpp_field,
    )

    at_call = PolicyCallSpec(
        expose_as=at_as,
        receiver=item.handle,
        returns=TypeSpec(
            kind="handle",
            handle=element_handle,
            ownership="borrowed",
            nullable=False,
            cpp_type=None,
        ),
        params=(
            ParamSpec(
                name="index",
                type=TypeSpec(
                    kind="size",
                    handle=None,
                    ownership=None,
                    nullable=False,
                    cpp_type=None,
                ),
            ),
        ),
        operation=ChildrenAtPolicyOp(field_name=dc.cpp_field),
    )
    _register_policy_call(
        at_call,
        handle=handle,
        calls=calls,
        calls_by_c_name=calls_by_c_name,
        diagnostics=diagnostics,
        owner=item.handle,
        member=dc.cpp_field,
    )

    if dc.add_as is None:
        return

    add_call = PolicyCallSpec(
        expose_as=dc.add_as,
        receiver=item.handle,
        returns=TypeSpec(kind="void"),
        params=(
            ParamSpec(
                name="item",
                type=TypeSpec(
                    kind="handle", handle=element_handle, ownership="borrowed"
                ),
            ),
        ),
        operation=ChildrenAddPolicyOp(
            field_name=dc.cpp_field, cast_cpp_type=dc.add_cast_cpp_type
        ),
    )
    _register_policy_call(
        add_call,
        handle=handle,
        calls=calls,
        calls_by_c_name=calls_by_c_name,
        diagnostics=diagnostics,
        owner=item.handle,
        member=dc.cpp_field,
    )


def _emit_ccomponents_call(
    item: DiscoveryClassSpec,
    handle: HandleSpec,
    handles: dict[str, HandleSpec],
    discovery_environment: DiscoveryEnvironment,
    include_dir: Path,
    calls: list[CallSpec],
    calls_by_c_name: dict[str, CallSpec],
    diagnostics: list[DiscoveryDiagnostic],
) -> None:
    cc = item.ccomponents_accessor
    if cc is None:
        return
    dimensions = cc.dimensions
    if dimensions is None:
        dimensions = _infer_ccomponents_dimensions(
            item,
            handle,
            handles=handles,
            discovery_environment=discovery_environment,
            include_dir=include_dir,
        )
    cc_call = PolicyCallSpec(
        expose_as=cc.expose_as,
        receiver=item.handle,
        returns=TypeSpec(kind="double", ownership="copy", sequence_depth=1),
        params=(),
        operation=CcomponentsAccessorPolicyOp(
            access_via=cc.access_via, dimensions=dimensions
        ),
    )
    _register_policy_call(
        cc_call,
        handle=handle,
        calls=calls,
        calls_by_c_name=calls_by_c_name,
        diagnostics=diagnostics,
        owner=item.handle,
        member=cc.access_via,
    )


def _emit_variant_accessor_calls(
    item: DiscoveryClassSpec,
    handle: HandleSpec,
    handles: dict[str, HandleSpec],
    calls: list[CallSpec],
    calls_by_c_name: dict[str, CallSpec],
    diagnostics: list[DiscoveryDiagnostic],
) -> None:
    va = item.variant_accessors
    if va is None:
        return

    for suffix, type_spec in va.types.items():
        cpp_type = type_spec.cpp_type
        return_type = _variant_accessor_type_spec(cpp_type, handles)
        if return_type is None:
            _append_discovery_diagnostic(
                diagnostics,
                owner=item.handle,
                member=suffix,
                code="unsupported_variant_accessor_type",
                message=f"Skipped variant accessor '{suffix}' because type '{cpp_type}' is not supported",
            )
            continue

        get_expose = f"get_{suffix}"
        get_call = PolicyCallSpec(
            expose_as=get_expose,
            receiver=item.handle,
            returns=return_type,
            params=(ParamSpec(name="name", type=TypeSpec(kind="string")),),
            operation=VariantGetPolicyOp(
                method_name=va.get_method,
                cpp_type=cpp_type,
                getter_types=type_spec.getter_types,
            ),
        )
        _register_policy_call(
            get_call,
            handle=handle,
            calls=calls,
            calls_by_c_name=calls_by_c_name,
            diagnostics=diagnostics,
            owner=item.handle,
            member=suffix,
        )

        set_expose = f"set_{suffix}"
        set_call = PolicyCallSpec(
            expose_as=set_expose,
            receiver=item.handle,
            returns=TypeSpec(kind="void"),
            params=(
                ParamSpec(name="name", type=TypeSpec(kind="string")),
                ParamSpec(name="value", type=return_type),
            ),
            operation=VariantSetPolicyOp(
                method_name=va.set_method,
                variant_type=va.variant_type,
                cpp_type=cpp_type,
            ),
        )
        _register_policy_call(
            set_call,
            handle=handle,
            calls=calls,
            calls_by_c_name=calls_by_c_name,
            diagnostics=diagnostics,
            owner=item.handle,
            member=suffix,
        )


def _discover_method_calls(
    spec_path: Path,
    discovery: DiscoverySpec,
    handles: dict[str, HandleSpec],
    discovery_environment: DiscoveryEnvironment,
) -> tuple[tuple[CallSpec, ...], tuple[DiscoveryDiagnostic, ...]]:
    include_dir = (spec_path.parent / discovery.include_dir).resolve()
    class_cache: dict[object, object] = {}
    calls: list[CallSpec] = []
    calls_by_c_name: dict[str, CallSpec] = {}
    diagnostics: list[DiscoveryDiagnostic] = []

    debug_log(
        "spec.discover_methods.start",
        f"spec={debug_path(spec_path)} classes={len(discovery.classes)} include_dir={debug_path(include_dir)}",
    )

    for item_index, item in enumerate(discovery.classes, start=1):
        if not _compile_guard_active(
            item.compile_guard, discovery_environment.compilation.defines
        ):
            continue
        handle = handles[item.handle]
        excluded = set(item.exclude)
        debug_log(
            "spec.discover_methods.class",
            f"{item_index}/{len(discovery.classes)} handle={item.handle} cpp={handle.cpp_type} tu={item.translation_unit}",
        )

        method_names = frozenset(
            accessor.method_name for accessor in item.method_at_accessors
        )
        methods_by_name: dict[str, tuple[DiscoveredMethod, ...]] = {}
        if method_names:
            method_cache_key = (
                "methods",
                handle.cpp_type,
                item.translation_unit,
                method_names,
            )
            cached_methods = class_cache.get(method_cache_key)
            if cached_methods is None:
                translation_unit = (include_dir / item.translation_unit).resolve()
                cached_methods = discover_public_methods(
                    discovery_environment,
                    translation_unit,
                    handle.cpp_type,
                    include_inherited=False,
                    selected_names=method_names,
                )
                class_cache[method_cache_key] = cached_methods
            methods_by_name = cached_methods

        # Discover public fields if requested
        if item.discover_fields:
            field_cache_key = (
                "fields",
                handle.cpp_type,
                item.translation_unit,
                item.include_inherited_fields,
            )
            fields_by_name = class_cache.get(field_cache_key)
            if fields_by_name is None:
                translation_unit = (include_dir / item.translation_unit).resolve()
                fields_by_name = discover_public_fields(
                    discovery_environment,
                    translation_unit,
                    handle.cpp_type,
                    include_inherited=item.include_inherited_fields,
                )
                class_cache[field_cache_key] = fields_by_name

            for field_name in sorted(fields_by_name):
                if field_name in excluded:
                    continue
                field = fields_by_name[field_name]

                # Handle std::optional<T> fields
                optional_inner = _extract_optional_inner_type(field.cpp_type_ref)
                if optional_inner is not None:
                    _emit_optional_field_calls(
                        item,
                        handle,
                        field_name,
                        field.cpp_name,
                        optional_inner,
                        handles,
                        calls,
                        calls_by_c_name,
                        diagnostics,
                    )
                    continue

                try:
                    returns = _infer_return_type(field.cpp_type_ref, handles)
                except ValueError as exc:
                    _append_discovery_diagnostic(
                        diagnostics,
                        owner=item.handle,
                        member=field_name,
                        code="unsupported_field_type",
                        message=(
                            f"Skipped auto-discovered field '{field_name}' because type "
                            f"'{_cpp_type_debug(field.cpp_type_ref)}' is not supported: {exc}"
                        ),
                    )
                    continue

                # Determine if this is a value-typed handle field (not a pointer/shared_ptr).
                # Value handle fields need make_shared wrapping; pointer fields use direct access.
                field_kind = "field"
                if returns.kind == "handle":
                    normalized_field_type = _normalize_cpp_type(field.cpp_type)
                    is_pointer_field = (
                        normalized_field_type.endswith("*")
                        or normalized_field_type.endswith("::ptr")
                        or "shared_ptr" in normalized_field_type
                    )
                    if not is_pointer_field:
                        field_kind = "value_handle_field"
                        returns = TypeSpec(
                            kind="handle",
                            handle=returns.handle,
                            ownership="owned",
                            nullable=False,
                            cpp_type=returns.cpp_type,
                        )

                expose_as = item.rename.get(
                    field_name, _snake_case_identifier(field_name)
                )
                call = CallSpec(
                    expose_as=expose_as,
                    c_name=_make_c_name(handle, expose_as),
                    receiver=item.handle,
                    returns=returns,
                    params=(),
                    policy_operation=(
                        DirectFieldPolicyOp(field_name=field.cpp_name)
                        if field_kind == "field"
                        else ValueHandleFieldPolicyOp(field_name=field.cpp_name)
                    ),
                )
                existing = calls_by_c_name.get(call.c_name)
                if existing is not None:
                    _append_discovery_diagnostic(
                        diagnostics,
                        owner=item.handle,
                        member=field_name,
                        code="field_name_collision",
                        message=f"Skipped generated field accessor '{call.c_name}' because another call already uses that name",
                    )
                    continue
                calls_by_c_name[call.c_name] = call
                calls.append(call)

                # For nullable handle fields, optionally generate has_X
                if (
                    item.discover_has_fields
                    and field_kind == "field"
                    and returns.kind == "handle"
                ):
                    has_expose = f"has_{expose_as}"
                    has_call = PolicyCallSpec(
                        expose_as=has_expose,
                        receiver=item.handle,
                        returns=TypeSpec(kind="bool", cpp_type=None),
                        params=(),
                        operation=PointerPresencePolicyOp(field_name=field.cpp_name),
                    )
                    _register_policy_call(
                        has_call,
                        handle=handle,
                        calls=calls,
                        calls_by_c_name=calls_by_c_name,
                        diagnostics=diagnostics,
                        owner=item.handle,
                        member=field_name,
                    )

        _emit_children_calls(
            item,
            handle,
            handles,
            class_cache,
            discovery_environment,
            include_dir,
            calls,
            calls_by_c_name,
            diagnostics,
        )

        # Generate extra fields (manually specified for template classes)
        for field_name, cpp_type in item.extra_fields.items():
            if field_name in excluded:
                continue
            try:
                returns = _infer_return_type(cpp_type, handles)
            except ValueError:
                msg = f"Cannot infer return type for extra_field '{field_name}' with cpp_type '{cpp_type}' on {item.handle}"
                raise ValueError(msg)

            normalized = _normalize_cpp_type(cpp_type)
            is_pointer = (
                normalized.endswith("*")
                or normalized.endswith("::ptr")
                or "shared_ptr" in normalized
            )
            field_kind = "field" if is_pointer else "value_handle_field"
            if field_kind == "value_handle_field" and returns.kind == "handle":
                returns = TypeSpec(
                    kind="handle",
                    handle=returns.handle,
                    ownership="owned",
                    nullable=False,
                    cpp_type=returns.cpp_type,
                )

            expose_as = item.rename.get(field_name, _snake_case_identifier(field_name))
            call = CallSpec(
                expose_as=expose_as,
                c_name=_make_c_name(handle, expose_as),
                receiver=item.handle,
                returns=returns,
                params=(),
                policy_operation=(
                    DirectFieldPolicyOp(field_name=field_name)
                    if field_kind == "field"
                    else ValueHandleFieldPolicyOp(field_name=field_name)
                ),
            )
            _register_generated_call(
                call,
                calls=calls,
                calls_by_c_name=calls_by_c_name,
                diagnostics=diagnostics,
                owner=item.handle,
                member=field_name,
            )

            # Also generate has_X for nullable handle extra fields
            if (
                item.discover_has_fields
                and field_kind == "field"
                and returns.kind == "handle"
            ):
                has_expose = f"has_{expose_as}"
                has_call = PolicyCallSpec(
                    expose_as=has_expose,
                    receiver=item.handle,
                    returns=TypeSpec(kind="bool", cpp_type=None),
                    params=(),
                    operation=PointerPresencePolicyOp(field_name=field_name),
                )
                _register_policy_call(
                    has_call,
                    handle=handle,
                    calls=calls,
                    calls_by_c_name=calls_by_c_name,
                    diagnostics=diagnostics,
                    owner=item.handle,
                    member=field_name,
                )

        # Generate field setters
        for setter_field in item.field_setters:
            param_type: TypeSpec | None = None
            if setter_field in item.extra_fields:
                cpp_type_str = item.extra_fields[setter_field]
                try:
                    param_type = _infer_return_type(cpp_type_str, handles)
                except ValueError:
                    pass
            elif item.discover_fields:
                field_cache_key = (
                    "fields",
                    handle.cpp_type,
                    item.translation_unit,
                    item.include_inherited_fields,
                )
                cached = class_cache.get(field_cache_key)
                if cached and setter_field in cached:
                    try:
                        param_type = _infer_return_type(
                            cached[setter_field].cpp_type, handles
                        )
                    except ValueError:
                        pass
            if param_type is None:
                msg = f"Cannot determine type for field_setter '{setter_field}' on {item.handle}"
                raise ValueError(msg)

            set_expose = f"set_{_snake_case_identifier(setter_field)}"
            set_call = PolicyCallSpec(
                expose_as=set_expose,
                receiver=item.handle,
                returns=TypeSpec(kind="void"),
                params=(ParamSpec(name="value", type=param_type),),
                operation=FieldSetterPolicyOp(field_name=setter_field),
            )
            _register_policy_call(
                set_call,
                handle=handle,
                calls=calls,
                calls_by_c_name=calls_by_c_name,
                diagnostics=diagnostics,
                owner=item.handle,
                member=setter_field,
            )

        # Generate method_size calls (method().size())
        for method_name, expose_as in item.method_sizes.items():
            ms_call = PolicyCallSpec(
                expose_as=expose_as,
                receiver=item.handle,
                returns=TypeSpec(kind="size"),
                params=(),
                operation=MethodSizePolicyOp(method_name=method_name),
            )
            _register_policy_call(
                ms_call,
                handle=handle,
                calls=calls,
                calls_by_c_name=calls_by_c_name,
                diagnostics=diagnostics,
                owner=item.handle,
                member=method_name,
            )

        for accessor in item.method_at_accessors:
            item_handle = handles.get(accessor.item_handle)
            if item_handle is None:
                msg = f"method_at_accessors entry '{accessor.expose_as}' refers to unknown handle '{accessor.item_handle}'"
                raise ValueError(msg)
            overloads = methods_by_name.get(accessor.method_name)
            if overloads is None:
                msg = f"method_at_accessors entry '{accessor.method_name}' was not discovered on {item.handle}"
                raise ValueError(msg)
            if len(overloads) != 1:
                msg = f"method_at_accessors entry '{accessor.method_name}' on {item.handle} is overloaded"
                raise ValueError(msg)
            discovered = overloads[0]
            if discovered.params:
                msg = f"method_at_accessors entry '{accessor.method_name}' on {item.handle} must refer to a no-argument method"
                raise ValueError(msg)
            if not _cpp_type_contains_handle_item(
                discovered.return_cpp_type, item_handle.cpp_type
            ):
                msg = (
                    f"method_at_accessors entry '{accessor.method_name}' returns '{discovered.return_cpp_type}', "
                    f"which does not contain item handle type '{item_handle.cpp_type}'"
                )
                raise ValueError(msg)
            inferred_container = _infer_return_type(discovered.return_type_ref, handles)
            if (
                inferred_container.kind != "handle"
                or inferred_container.handle != accessor.item_handle
                or inferred_container.sequence_depth == 0
            ):
                msg = (
                    f"method_at_accessors entry '{accessor.method_name}' returns "
                    f"'{discovered.return_cpp_type}', which does not infer a sequence "
                    f"of '{accessor.item_handle}' handles"
                )
                raise ValueError(msg)
            at_call = PolicyCallSpec(
                expose_as=accessor.expose_as,
                receiver=item.handle,
                returns=TypeSpec(
                    kind="handle",
                    handle=accessor.item_handle,
                    ownership=accessor.ownership or inferred_container.ownership,
                ),
                params=(ParamSpec(name="index", type=TypeSpec(kind="size")),),
                operation=MethodAtPolicyOp(
                    method_name=accessor.method_name,
                    item_cpp_type=item_handle.cpp_type,
                    out_of_range_message=accessor.out_of_range_message,
                    exception_type=accessor.exception_type,
                ),
            )
            _register_policy_call(
                at_call,
                handle=handle,
                calls=calls,
                calls_by_c_name=calls_by_c_name,
                diagnostics=diagnostics,
                owner=item.handle,
                member=accessor.method_name,
            )

        # Generate array_pair_field calls (field[0] as _u, field[1] as _v)
        for field_name, return_kind in item.array_pair_fields.items():
            if return_kind is not None:
                ret_type = _simple_type_spec(return_kind)
            else:
                field_cache_key = (
                    "fields",
                    handle.cpp_type,
                    item.translation_unit,
                    item.include_inherited_fields,
                )
                fields_by_name = class_cache.get(field_cache_key)
                if fields_by_name is None:
                    translation_unit = (include_dir / item.translation_unit).resolve()
                    fields_by_name = discover_public_fields(
                        discovery_environment,
                        translation_unit,
                        handle.cpp_type,
                        include_inherited=item.include_inherited_fields,
                    )
                    class_cache[field_cache_key] = fields_by_name
                field = fields_by_name.get(field_name)
                if field is None:
                    msg = f"array_pair_fields entry '{field_name}' was not discovered on {item.handle}"
                    raise ValueError(msg)
                ret_type = _infer_array_pair_element_type(field, handles)
            for suffix, index in [("_u", 0), ("_v", 1)]:
                expose = f"{field_name}{suffix}"
                ap_call = PolicyCallSpec(
                    expose_as=expose,
                    receiver=item.handle,
                    returns=ret_type,
                    params=(),
                    operation=ArrayElementFieldPolicyOp(
                        expression=f"{field_name}[{index}]"
                    ),
                )
                _register_policy_call(
                    ap_call,
                    handle=handle,
                    calls=calls,
                    calls_by_c_name=calls_by_c_name,
                    diagnostics=diagnostics,
                    owner=item.handle,
                    member=field_name,
                )

        # Generate as_item cast if requested
        if item.discover_as_item:
            as_item_call = PolicyCallSpec(
                expose_as="as_item",
                receiver=item.handle,
                returns=TypeSpec(
                    kind="handle",
                    handle="taxonomy_item",
                    ownership="owned",
                    nullable=False,
                    cpp_type=None,
                ),
                params=(),
                operation=AsItemCastPolicyOp(),
            )
            _register_policy_call(
                as_item_call,
                handle=handle,
                calls=calls,
                calls_by_c_name=calls_by_c_name,
                diagnostics=diagnostics,
                owner=item.handle,
                member="as_item",
            )

        _emit_ccomponents_call(
            item,
            handle,
            handles,
            discovery_environment,
            include_dir,
            calls,
            calls_by_c_name,
            diagnostics,
        )
        _emit_variant_accessor_calls(
            item,
            handle,
            handles,
            calls,
            calls_by_c_name,
            diagnostics,
        )

    debug_log(
        "spec.discover_methods.done",
        f"spec={debug_path(spec_path)} calls={len(calls)} diagnostics={len(diagnostics)}",
    )
    return tuple(calls), tuple(diagnostics)


def _compile_guard_active(compile_guard: str | None, defines: tuple[str, ...]) -> bool:
    if compile_guard is None:
        return True
    normalized = {define.removeprefix("-D") for define in defines}
    return compile_guard in normalized


def _select_constructor(
    constructors: tuple[DiscoveredConstructor, ...],
    params: tuple[str, ...] | None,
    *,
    context: str,
) -> DiscoveredConstructor:
    def param_matches(discovered: DiscoveredParam, target: str) -> bool:
        discovered_type = _normalize_cpp_type(
            discovered.cpp_type_ref.canonical_spelling
        )
        target_type = _normalize_cpp_type(target)
        if discovered_type == target_type:
            return True
        discovered_suffix = "".join(ch for ch in discovered_type if ch in "*&")
        target_suffix = "".join(ch for ch in target_type if ch in "*&")
        if discovered_suffix != target_suffix:
            return False
        discovered_base = discovered_type.replace("*", "").replace("&", "").strip()
        target_base = target_type.replace("*", "").replace("&", "").strip()
        return _cpp_type_names_match(discovered_base, target_base)

    if params is None:
        if not constructors:
            msg = (
                f"{context}: no public constructors are available for source inference"
            )
            raise ValueError(msg)
        if len(constructors) == 1:
            return constructors[0]
        available = ", ".join(
            _constructor_signature_debug(constructor) for constructor in constructors
        )
        msg = f"{context}: constructor params are required when overloads are present; available: {available}"
        raise ValueError(msg)

    matches = [
        constructor
        for constructor in constructors
        if len(constructor.params) == len(params)
        and all(
            param_matches(discovered_param, target_param)
            for discovered_param, target_param in zip(constructor.params, params)
        )
    ]
    if len(matches) == 1:
        return matches[0]
    available = ", ".join(
        _constructor_signature_debug(constructor) for constructor in constructors
    )
    if not matches:
        msg = f"{context}: unable to resolve constructor with params ({', '.join(params)}); available: {available}"
        raise ValueError(msg)
    msg = f"{context}: constructor params ({', '.join(params)}) are ambiguous; available: {available}"
    raise ValueError(msg)


def _constructor_fallback_params(
    item: DiscoveryConstructorSpec, handles: dict[str, HandleSpec]
) -> tuple[ParamSpec, ...]:
    if item.params is None or item.param_names is None:
        msg = f"Guarded constructor '{item.expose_as}' requires params and param_names for fallback generation"
        raise ValueError(msg)
    if len(item.params) != len(item.param_names):
        msg = (
            f"Guarded constructor '{item.expose_as}' has mismatched params and param_names "
            f"({len(item.params)} vs {len(item.param_names)})"
        )
        raise ValueError(msg)
    params: list[ParamSpec] = []
    for source_type, param_name in zip(item.params, item.param_names):
        params.append(
            ParamSpec(name=param_name, type=_infer_param_type(source_type, handles))
        )
    return tuple(params)


def _discover_constructor_calls(
    spec_path: Path,
    discovery: DiscoverySpec,
    handles: dict[str, HandleSpec],
    c_prefix: str,
    discovery_environment: DiscoveryEnvironment,
) -> tuple[tuple[CallSpec, ...], tuple[DiscoveryDiagnostic, ...]]:
    include_dir = (spec_path.parent / discovery.include_dir).resolve()
    constructor_cache: dict[tuple[str, str], tuple[DiscoveredConstructor, ...]] = {}
    calls: list[CallSpec] = []
    calls_by_c_name: dict[str, CallSpec] = {}
    diagnostics: list[DiscoveryDiagnostic] = []

    debug_log(
        "spec.discover_constructors.start",
        f"spec={debug_path(spec_path)} constructors={len(discovery.constructors)} include_dir={debug_path(include_dir)}",
    )

    for item_index, item in enumerate(discovery.constructors, start=1):
        handle = handles[item.handle]
        cache_key = (item.cpp_class, item.translation_unit)
        constructors = constructor_cache.get(cache_key)
        if constructors is None:
            if item.compile_guard is not None and not _compile_guard_active(
                item.compile_guard, discovery_environment.compilation.defines
            ):
                constructors = tuple()
            else:
                translation_unit = (include_dir / item.translation_unit).resolve()
                try:
                    constructors = discover_public_constructors(
                        discovery_environment,
                        translation_unit,
                        item.cpp_class,
                    )
                except (ValueError, RuntimeError):
                    if item.compile_guard is None:
                        raise
                    constructors = tuple()
            constructor_cache[cache_key] = constructors

        fallback_params: tuple[ParamSpec, ...] | None = None
        if item.compile_guard is not None:
            fallback_params = _constructor_fallback_params(item, handles)

        try:
            constructor = _select_constructor(
                constructors,
                item.params,
                context=f"Constructor discovery for '{item.cpp_class}' item {item_index}",
            )
        except ValueError:
            if fallback_params is not None:
                _append_discovery_diagnostic(
                    diagnostics,
                    owner=item.cpp_class,
                    member=item.expose_as,
                    code="guarded_constructor_unavailable",
                    message=f"Using guarded fallback signature for '{item.expose_as}' because the constructor was unavailable in the AST",
                )
                constructor = None
                params = list(fallback_params)
            else:
                raise
        else:
            params = []
            if fallback_params is not None:
                params = list(fallback_params)
            else:
                for param in constructor.params:
                    param_name = item.param_renames.get(param.name, param.name)
                    params.append(
                        ParamSpec(
                            name=param_name,
                            type=_infer_param_type(param.cpp_type_ref, handles),
                        )
                    )
        call = CallSpec(
            expose_as=item.expose_as,
            c_name=_make_function_c_name(c_prefix, item.expose_as),
            receiver=None,
            returns=TypeSpec(kind="handle", handle=item.handle, ownership="owned"),
            params=tuple(params),
            policy_operation=ConstructorPolicyOp(
                cpp_class=item.cpp_class if item.cpp_class != handle.cpp_type else None,
                compile_guard=item.compile_guard,
                compile_guard_message=item.compile_guard_message,
            ),
        )
        existing = calls_by_c_name.get(call.c_name)
        if existing is not None:
            if existing == call:
                continue
            msg = f"Discovered constructor collision for generated name '{call.c_name}'"
            raise ValueError(msg)
        calls_by_c_name[call.c_name] = call
        calls.append(call)

    return tuple(calls), tuple(diagnostics)
