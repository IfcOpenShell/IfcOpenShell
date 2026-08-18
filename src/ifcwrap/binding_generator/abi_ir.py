"""Authoritative finalized C ABI contract embedded in BindingIR."""

from __future__ import annotations

import re
from dataclasses import dataclass, field as dataclass_field
from types import MappingProxyType

from .binding_ir import BindingIR, CallIR
from .binding_model import HandleSpec, TypeSpec


@dataclass(frozen=True)
class CFieldIR:
    name: str
    c_type: str
    doc: str | None = None


@dataclass(frozen=True)
class CTypeIR:
    c_type: str
    kind: str
    fields: tuple[CFieldIR, ...]
    destroy_function: str | None
    element_type: str | None = None
    sequence_depth: int = 0
    layout: str = "transparent"
    variants: tuple[TypeSpec, ...] = ()


@dataclass(frozen=True)
class COptionFieldIR:
    name: str
    type: TypeSpec
    c_type: str
    doc: str | None = None
    presence_field: str | None = None
    has_default: bool = False


@dataclass(frozen=True)
class COptionIR:
    name: str
    c_type: str
    fields: tuple[COptionFieldIR, ...]


@dataclass(frozen=True)
class CParamIR:
    name: str
    c_type: str
    role: str
    type_kind: str
    nullable: bool = False
    has_default: bool = False
    type: TypeSpec | None = None


@dataclass(frozen=True)
class CFunctionIR:
    c_name: str
    restype: str
    params: tuple[CParamIR, ...]
    error_policy: str
    returns: TypeSpec
    receiver: str | None
    doc: str | None = None
    public_module: str | None = None


@dataclass(frozen=True)
class ErrorCatalogEntryIR:
    name: str
    value: int


@dataclass(frozen=True)
class ErrorCatalogIR:
    kinds: tuple[ErrorCatalogEntryIR, ...]
    codes: tuple[ErrorCatalogEntryIR, ...]

    def __post_init__(self) -> None:
        for label, entries in (("kind", self.kinds), ("code", self.codes)):
            names = [entry.name for entry in entries]
            values = [entry.value for entry in entries]
            if len(names) != len(set(names)):
                raise ValueError(f"Duplicate error {label} name")
            if len(values) != len(set(values)):
                raise ValueError(f"Duplicate error {label} value")


ERROR_CATALOG = ErrorCatalogIR(
    kinds=tuple(
        ErrorCatalogEntryIR(name, value)
        for name, value in (
            ("NONE", 0),
            ("RUNTIME", 1),
            ("VALUE", 2),
            ("TYPE", 3),
            ("CANCELLED", 4),
        )
    ),
    codes=tuple(
        ErrorCatalogEntryIR(name, value)
        for name, value in (
            ("NONE", 0),
            ("UNSPECIFIED", 1),
            ("INVALID_ARGUMENT", 2),
            ("DOMAIN_ERROR", 3),
            ("OPERATION_CANCELLED", 4),
        )
    ),
)


@dataclass(frozen=True)
class BindingABI:
    module: str
    c_prefix: str
    handles: dict[str, CTypeIR]
    value_types: dict[str, CTypeIR]
    functions: dict[str, CFunctionIR]
    error_functions: dict[str, str]
    error_catalog: ErrorCatalogIR = ERROR_CATALOG
    option_structs: dict[str, COptionIR] = dataclass_field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "handles", MappingProxyType(dict(self.handles)))
        object.__setattr__(
            self, "value_types", MappingProxyType(dict(self.value_types))
        )
        object.__setattr__(self, "functions", MappingProxyType(dict(self.functions)))
        object.__setattr__(
            self, "error_functions", MappingProxyType(dict(self.error_functions))
        )
        object.__setattr__(
            self, "option_structs", MappingProxyType(dict(self.option_structs))
        )


_SCALAR_PARAM_TYPES = {
    "bool": "bool",
    "int32": "int32_t",
    "int64": "int64_t",
    "double": "double",
    "uint32": "uint32_t",
    "size": "size_t",
}

_SCALAR_OUT_TYPES = {
    "bool": "bool*",
    "int32": "int32_t*",
    "int64": "int64_t*",
    "double": "double*",
    "uint32": "uint32_t*",
    "size": "size_t*",
}

_BUFFER_TYPES = {
    "double_buffer": ("const double*", "const double**"),
    "int32_buffer": ("const int32_t*", "const int32_t**"),
}

_SEQUENCE_LEAF_C_TYPE = {
    "string": "ifcopenshell_string_t",
    "bool": "bool",
    "int32": "int32_t",
    "int64": "int64_t",
    "uint8": "uint8_t",
    "uint32": "uint32_t",
    "double": "double",
}


def _sequence_kind_parts(kind: str) -> tuple[str, int] | None:
    match = re.fullmatch(r"([a-z0-9]+)((?:_list)+)", kind)
    if match is None:
        return None
    leaf = match.group(1)
    depth = match.group(2).count("_list")
    if leaf not in _SEQUENCE_LEAF_C_TYPE:
        return None
    return leaf, depth


def _sequence_c_type(kind: str) -> str:
    return f"ifcopenshell_{kind}_t"


def _sequence_prev_kind(kind: str) -> str:
    leaf, depth = _sequence_kind_parts(kind) or ("", 0)
    if depth <= 1:
        raise ValueError(f"{kind} has no previous sequence kind")
    return f"{leaf}{'_list' * (depth - 1)}"


def _sequence_items_c_type(kind: str) -> str:
    leaf, depth = _sequence_kind_parts(kind) or ("", 0)
    if depth == 1:
        return _SEQUENCE_LEAF_C_TYPE[leaf]
    return _sequence_c_type(_sequence_prev_kind(kind))


def _snake_name(c_type: str) -> str:
    return c_type.removeprefix("ifcopenshell_").removesuffix("_t")


def _handle_list_c_type(handle: HandleSpec) -> str:
    return f"{handle.c_type.removesuffix('_t')}_list_t"


def _handle_list_list_c_type(handle: HandleSpec) -> str:
    return f"{handle.c_type.removesuffix('_t')}_list_list_t"


def _option_list_c_type(option: object) -> str:
    return f"{option.c_type.removesuffix('_t')}_list_t"


def _variant_list_c_type(type_spec: TypeSpec, ir: BindingIR) -> str:
    return f"{_variant_c_type(type_spec, ir).removesuffix('_t')}_list_t"


def _handle_destroy_name(handle: HandleSpec) -> str:
    return f"ifcopenshell_{_snake_name(handle.c_type)}_destroy"


def _handle_list_destroy_name(handle: HandleSpec) -> str:
    return f"ifcopenshell_{_snake_name(_handle_list_c_type(handle))}_destroy"


def _handle_list_list_destroy_name(handle: HandleSpec) -> str:
    return f"ifcopenshell_{_snake_name(_handle_list_list_c_type(handle))}_destroy"


def _sequence_destroy_name(kind: str) -> str:
    return f"ifcopenshell_{kind}_destroy"


def _value_destroy_name(c_type: str) -> str:
    return f"ifcopenshell_{_snake_name(c_type)}_destroy"


def _result_record_list_c_type(struct: object) -> str:
    return f"{struct.c_type.removesuffix('_t')}_list_t"


def _result_record_list_destroy_name(struct: object) -> str:
    return f"ifcopenshell_{_snake_name(_result_record_list_c_type(struct))}_destroy"


def _result_record_list_make_name(struct: object) -> str:
    return f"make_{_snake_name(_result_record_list_c_type(struct))}"


def _type_spec_sequence_kind(type_spec: TypeSpec) -> str | None:
    if type_spec.sequence_depth <= 0 or type_spec.kind in {
        "handle",
        "option",
        "struct",
        "variant",
    }:
        return None
    return f"{type_spec.kind}{'_list' * type_spec.sequence_depth}"


def _used_scalar_sequence_kinds(ir: BindingIR) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []

    def add_type(type_spec: TypeSpec) -> None:
        kind = _type_spec_sequence_kind(type_spec)
        if kind is None:
            return
        parts = _sequence_kind_parts(kind)
        if parts is None:
            return
        leaf, depth = parts
        for current_depth in range(1, depth + 1):
            current = f"{leaf}{'_list' * current_depth}"
            if current not in seen:
                seen.add(current)
                ordered.append(current)

    for call in ir.calls:
        add_type(call.returns)
        for param in call.params:
            add_type(param.type)
    for struct in ir.result_structs.values():
        for field in struct.fields:
            add_type(field.type)
    for struct in ir.option_structs.values():
        for field in struct.fields:
            add_type(field.type)
    return tuple(ordered)


def _used_handle_sequence_depths(ir: BindingIR) -> dict[str, set[int]]:
    depths: dict[str, set[int]] = {}

    def add(type_spec: TypeSpec) -> None:
        if (
            type_spec.kind != "handle"
            or type_spec.sequence_depth == 0
            or type_spec.handle is None
        ):
            return
        depths.setdefault(type_spec.handle, set()).add(type_spec.sequence_depth)

    for call in ir.calls:
        add(call.returns)
        for param in call.params:
            add(param.type)
    for struct in ir.result_structs.values():
        for field in struct.fields:
            add(field.type)
    for struct in ir.option_structs.values():
        for field in struct.fields:
            add(field.type)
    return depths


def _used_handle_list_handles(ir: BindingIR) -> tuple[HandleSpec, ...]:
    return tuple(ir.handles[name] for name in _used_handle_sequence_depths(ir))


def _used_result_record_lists(ir: BindingIR) -> tuple[object, ...]:
    seen: set[str] = set()
    structs: list[object] = []

    def add(type_spec: TypeSpec) -> None:
        if (
            type_spec.kind != "struct"
            or type_spec.sequence_depth != 1
            or type_spec.struct is None
            or type_spec.struct in seen
        ):
            return
        seen.add(type_spec.struct)
        structs.append(ir.result_structs[type_spec.struct])

    for call in ir.calls:
        add(call.returns)
    for struct in ir.result_structs.values():
        for field in struct.fields:
            add(field.type)
    return tuple(structs)


def _param_c_type(type_spec: TypeSpec, ir: BindingIR) -> str:
    sequence_kind = _type_spec_sequence_kind(type_spec)
    if sequence_kind is not None:
        return f"const {_sequence_c_type(sequence_kind)}*"
    if type_spec.kind in _SCALAR_PARAM_TYPES:
        c_type = _SCALAR_PARAM_TYPES[type_spec.kind]
        return f"const {c_type}*" if type_spec.nullable else c_type
    if type_spec.kind == "string":
        return "const char*"
    if type_spec.kind in _BUFFER_TYPES:
        return _BUFFER_TYPES[type_spec.kind][0]
    if type_spec.kind == "handle":
        if type_spec.handle is None:
            raise ValueError("handle type is missing handle name")
        handle = ir.handles[type_spec.handle]
        if type_spec.sequence_depth == 1:
            return f"const {_handle_list_c_type(handle)}*"
        if type_spec.sequence_depth == 2:
            return f"const {_handle_list_list_c_type(handle)}*"
        return f"{handle.c_type}*"
    if type_spec.kind == "opaque_ptr":
        return "void*"
    if type_spec.kind == "struct":
        if type_spec.struct is None:
            raise ValueError("struct type is missing struct name")
        return ir.result_structs[type_spec.struct].c_type
    if type_spec.kind == "option":
        if type_spec.struct is None:
            raise ValueError("option type is missing option struct name")
        if type_spec.sequence_depth == 1:
            return f"const {_option_list_c_type(ir.option_structs[type_spec.struct])}*"
        return f"const {ir.option_structs[type_spec.struct].c_type}*"
    if type_spec.kind == "variant":
        if type_spec.sequence_depth == 1:
            return f"const {_variant_list_c_type(type_spec, ir)}*"
        return f"const {_variant_c_type(type_spec, ir)}*"
    raise ValueError(f"Unsupported parameter kind: {type_spec.kind}")


def _option_field_c_type(type_spec: TypeSpec, ir: BindingIR) -> str:
    if type_spec.kind in _SCALAR_PARAM_TYPES and type_spec.sequence_depth == 0:
        return _SCALAR_PARAM_TYPES[type_spec.kind]
    return _param_c_type(type_spec, ir)


def _variant_alt_name(type_spec: TypeSpec, ir: BindingIR) -> str:
    sequence_kind = _type_spec_sequence_kind(type_spec)
    if sequence_kind is not None:
        fixed_suffix = "_".join(
            "any" if length is None else str(length)
            for length in type_spec.fixed_lengths
        )
        return f"{sequence_kind}_{fixed_suffix}" if fixed_suffix else sequence_kind
    if type_spec.kind == "handle" and type_spec.handle is not None:
        return type_spec.handle
    if type_spec.kind == "struct" and type_spec.struct is not None:
        return type_spec.struct
    if type_spec.kind == "option" and type_spec.struct is not None:
        return type_spec.struct
    return type_spec.kind


def _variant_c_type(type_spec: TypeSpec, ir: BindingIR) -> str:
    parts = "_".join(_variant_alt_name(alt, ir) for alt in type_spec.variants)
    return f"{ir.c_prefix}_{parts}_variant_t"


def _variant_destroy_name(type_spec: TypeSpec, ir: BindingIR) -> str:
    return f"ifcopenshell_{_snake_name(_variant_c_type(type_spec, ir))}_destroy"


def _optional_struct_c_type(type_spec: TypeSpec, ir: BindingIR) -> str:
    if type_spec.struct is None:
        raise ValueError("nullable struct return is missing struct name")
    base = ir.result_structs[type_spec.struct].c_type.removeprefix(f"{ir.c_prefix}_")
    return f"{ir.c_prefix}_optional_{base}"


def _out_c_type(type_spec: TypeSpec, ir: BindingIR) -> str:
    sequence_kind = _type_spec_sequence_kind(type_spec)
    if sequence_kind is not None:
        return f"{_sequence_c_type(sequence_kind)}*"
    if type_spec.kind in _SCALAR_OUT_TYPES:
        return _SCALAR_OUT_TYPES[type_spec.kind]
    if type_spec.kind == "string":
        return "ifcopenshell_string_t*"
    if type_spec.kind in _BUFFER_TYPES:
        return _BUFFER_TYPES[type_spec.kind][1]
    if type_spec.kind == "handle":
        if type_spec.handle is None:
            raise ValueError("handle type is missing handle name")
        handle = ir.handles[type_spec.handle]
        if type_spec.sequence_depth == 1:
            return f"{_handle_list_c_type(handle)}*"
        if type_spec.sequence_depth == 2:
            return f"{_handle_list_list_c_type(handle)}*"
        return f"{handle.c_type}**"
    if type_spec.kind == "struct":
        if type_spec.struct is None:
            raise ValueError("struct type is missing struct name")
        if type_spec.sequence_depth == 1:
            return f"{_result_record_list_c_type(ir.result_structs[type_spec.struct])}*"
        if type_spec.nullable:
            return f"{_optional_struct_c_type(type_spec, ir)}*"
        return f"{ir.result_structs[type_spec.struct].c_type}*"
    if type_spec.kind == "variant":
        return f"{_variant_c_type(type_spec, ir)}*"
    raise ValueError(f"Unsupported return kind: {type_spec.kind}")


def _field_c_type(type_spec: TypeSpec, ir: BindingIR) -> str:
    sequence_kind = _type_spec_sequence_kind(type_spec)
    if sequence_kind is not None:
        return _sequence_c_type(sequence_kind)
    if type_spec.kind in _SCALAR_PARAM_TYPES:
        return _SCALAR_PARAM_TYPES[type_spec.kind]
    if type_spec.kind == "string":
        return "ifcopenshell_string_t"
    if type_spec.kind == "handle":
        if type_spec.handle is None:
            raise ValueError("handle type is missing handle name")
        handle = ir.handles[type_spec.handle]
        if type_spec.sequence_depth == 1:
            return _handle_list_c_type(handle)
        if type_spec.sequence_depth == 2:
            return _handle_list_list_c_type(handle)
        return f"{handle.c_type}*"
    if type_spec.kind == "struct":
        if type_spec.struct is None:
            raise ValueError("struct type is missing struct name")
        if type_spec.sequence_depth == 1:
            return _result_record_list_c_type(ir.result_structs[type_spec.struct])
        return ir.result_structs[type_spec.struct].c_type
    if type_spec.kind == "option":
        if type_spec.struct is None:
            raise ValueError("option type is missing struct name")
        return f"const {ir.option_structs[type_spec.struct].c_type}*"
    if type_spec.kind == "variant":
        return _variant_c_type(type_spec, ir)
    raise ValueError(f"Unsupported result struct field kind: {type_spec.kind}")


def _finalize_handles(ir: BindingIR) -> dict[str, CTypeIR]:
    result: dict[str, CTypeIR] = {}
    for name, handle in sorted(ir.handles.items()):
        if handle.ptr_type == "shared_ptr":
            fields: tuple[CFieldIR, ...] = ()
            layout = "opaque"
        elif handle.ptr_type == "value":
            fields = ()
            layout = "opaque"
        else:
            fields = (CFieldIR("ptr", "void*"), CFieldIR("owned", "bool"))
            layout = "ptr_owned"
        result[name] = CTypeIR(
            c_type=handle.c_type,
            kind="handle",
            fields=fields,
            destroy_function=_handle_destroy_name(handle),
            element_type=handle.cpp_type,
            layout=layout,
        )
    return result


def _finalize_value_types(ir: BindingIR) -> dict[str, CTypeIR]:
    result: dict[str, CTypeIR] = {
        "string": CTypeIR(
            c_type="ifcopenshell_string_t",
            kind="string",
            fields=(
                CFieldIR("data", "char*"),
                CFieldIR("size", "size_t"),
                CFieldIR("owned", "bool"),
                CFieldIR("owner", "void*"),
            ),
            destroy_function="ifcopenshell_string_destroy",
        )
    }
    for kind in _used_scalar_sequence_kinds(ir):
        result[kind] = CTypeIR(
            c_type=_sequence_c_type(kind),
            kind="sequence",
            fields=(
                CFieldIR("items", f"{_sequence_items_c_type(kind)}*"),
                CFieldIR("size", "size_t"),
                CFieldIR("owner", "void*"),
            ),
            destroy_function=_sequence_destroy_name(kind),
            element_type=_sequence_items_c_type(kind),
            sequence_depth=(_sequence_kind_parts(kind) or ("", 0))[1],
        )
    handle_sequence_depths = _used_handle_sequence_depths(ir)
    for handle_name, depths in handle_sequence_depths.items():
        handle = ir.handles[handle_name]
        list_type = _handle_list_c_type(handle)
        result[_snake_name(list_type)] = CTypeIR(
            c_type=list_type,
            kind="handle_sequence",
            fields=(
                CFieldIR("items", f"{handle.c_type}**"),
                CFieldIR("size", "size_t"),
            ),
            destroy_function=_handle_list_destroy_name(handle),
            element_type=handle.c_type,
            sequence_depth=1,
        )
        if 2 in depths:
            list_list_type = _handle_list_list_c_type(handle)
            result[_snake_name(list_list_type)] = CTypeIR(
                c_type=list_list_type,
                kind="handle_sequence",
                fields=(
                    CFieldIR("items", f"{list_type}*"),
                    CFieldIR("size", "size_t"),
                ),
                destroy_function=_handle_list_list_destroy_name(handle),
                element_type=list_type,
                sequence_depth=2,
            )
    for struct in _used_result_record_lists(ir):
        list_type = _result_record_list_c_type(struct)
        result[_snake_name(list_type)] = CTypeIR(
            c_type=list_type,
            kind="result_record_sequence",
            fields=(
                CFieldIR("items", f"{struct.c_type}*"),
                CFieldIR("size", "size_t"),
            ),
            destroy_function=_result_record_list_destroy_name(struct),
            element_type=struct.c_type,
            sequence_depth=1,
        )
    for struct in ir.result_structs.values():
        result[struct.name] = CTypeIR(
            c_type=struct.c_type,
            kind="result_struct",
            fields=tuple(
                CFieldIR(field.name, _field_c_type(field.type, ir), field.doc)
                for field in struct.fields
            ),
            destroy_function=_value_destroy_name(struct.c_type),
            element_type=struct.cpp_type,
        )
    for option in ir.option_structs.values():
        used = any(
            param.type.kind == "option"
            and param.type.struct == option.name
            and param.type.sequence_depth == 1
            for call in ir.calls
            for param in call.params
        ) or any(
            field.type.kind == "option"
            and field.type.struct == option.name
            and field.type.sequence_depth == 1
            for parent in ir.option_structs.values()
            for field in parent.fields
        )
        if used:
            list_type = _option_list_c_type(option)
            result[_snake_name(list_type)] = CTypeIR(
                c_type=list_type,
                kind="input_record_sequence",
                fields=(
                    CFieldIR("items", f"{option.c_type}*"),
                    CFieldIR("size", "size_t"),
                ),
                destroy_function=None,
                element_type=option.c_type,
                sequence_depth=1,
            )
    for call in ir.calls:
        returns = call.returns
        if returns.kind == "struct" and returns.nullable and returns.struct is not None:
            c_type = _optional_struct_c_type(returns, ir)
            result[_snake_name(c_type)] = CTypeIR(
                c_type=c_type,
                kind="optional_result_struct",
                fields=(
                    CFieldIR("has_value", "bool"),
                    CFieldIR("value", ir.result_structs[returns.struct].c_type),
                ),
                destroy_function=_value_destroy_name(c_type),
                element_type=returns.struct,
            )
    for variant in _used_variant_types(ir):
        c_type = _variant_c_type(variant, ir)
        result[_snake_name(c_type)] = CTypeIR(
            c_type=c_type,
            kind="variant",
            fields=tuple(
                [CFieldIR("kind", "int32_t")]
                + [
                    CFieldIR(f"value_{index}", _field_c_type(alt, ir))
                    for index, alt in enumerate(variant.variants)
                ]
            ),
            destroy_function=_variant_destroy_name(variant, ir),
            element_type=variant.cpp_type,
            variants=variant.variants,
        )
        if variant.sequence_depth == 1:
            list_type = _variant_list_c_type(variant, ir)
            result[_snake_name(list_type)] = CTypeIR(
                c_type=list_type,
                kind="input_variant_sequence",
                fields=(
                    CFieldIR("items", f"{c_type}*"),
                    CFieldIR("size", "size_t"),
                ),
                destroy_function=None,
                element_type=c_type,
                sequence_depth=1,
            )
    return result


def _used_variant_types(ir: BindingIR) -> tuple[TypeSpec, ...]:
    variants: dict[str, TypeSpec] = {}

    def visit(type_spec: TypeSpec) -> None:
        if type_spec.kind != "variant":
            return
        c_type = _variant_c_type(type_spec, ir)
        previous = variants.get(c_type)
        if previous is None or type_spec.sequence_depth > previous.sequence_depth:
            variants[c_type] = type_spec
        for alternative in type_spec.variants:
            visit(alternative)

    for call in ir.calls:
        visit(call.returns)
        for param in call.params:
            visit(param.type)
    for option in ir.option_structs.values():
        for field in option.fields:
            visit(field.type)
    for struct in ir.result_structs.values():
        for field in struct.fields:
            visit(field.type)
    return tuple(variants.values())


def _finalize_function(call: CallIR, ir: BindingIR) -> CFunctionIR:
    params: list[CParamIR] = []
    if call.receiver is not None:
        receiver = ir.handles[call.receiver]
        params.append(
            CParamIR(
                name="self",
                c_type=f"{receiver.c_type}*",
                role="receiver",
                type_kind="handle",
                nullable=False,
            )
        )
    for param in call.params:
        params.append(
            CParamIR(
                name=param.name,
                c_type=_param_c_type(param.type, ir),
                role="param",
                type_kind=param.type.kind,
                nullable=param.type.nullable,
                has_default=param.has_default,
                type=param.type,
            )
        )
    if call.returns.kind != "void":
        params.append(
            CParamIR(
                name="out_result",
                c_type=_out_c_type(call.returns, ir),
                role="out_result",
                type_kind=call.returns.kind,
                nullable=False,
            )
        )
    return CFunctionIR(
        c_name=call.c_name,
        restype="bool",
        params=tuple(params),
        error_policy="bool_return_last_error",
        returns=call.returns,
        receiver=call.receiver,
        doc=call.doc,
        public_module=call.public_module,
    )


def _validate_type_reference(type_spec: TypeSpec, ir: BindingIR, context: str) -> None:
    if type_spec.kind == "handle":
        if type_spec.handle is None:
            raise ValueError(f"{context}: handle type is missing its logical name")
        if type_spec.handle not in ir.handles:
            raise ValueError(f"{context}: unknown handle '{type_spec.handle}'")
    elif type_spec.kind == "struct":
        if type_spec.struct is None:
            raise ValueError(f"{context}: result struct type is missing its name")
        if type_spec.struct not in ir.result_structs:
            raise ValueError(f"{context}: unknown result struct '{type_spec.struct}'")
    elif type_spec.kind == "option":
        if type_spec.struct is None:
            raise ValueError(f"{context}: option type is missing its struct name")
        if type_spec.struct not in ir.option_structs:
            raise ValueError(f"{context}: unknown option struct '{type_spec.struct}'")
    elif type_spec.kind == "variant":
        if not type_spec.variants:
            raise ValueError(f"{context}: variant has no alternatives")
        for index, alternative in enumerate(type_spec.variants):
            _validate_type_reference(
                alternative, ir, f"{context} variant alternative {index}"
            )


def _validate_semantic_references(ir: BindingIR) -> None:
    for call in ir.calls:
        if call.receiver is not None and call.receiver not in ir.handles:
            raise ValueError(
                f"call {call.c_name}: unknown receiver handle '{call.receiver}'"
            )
        for param in call.params:
            _validate_type_reference(
                param.type, ir, f"call {call.c_name} parameter '{param.name}'"
            )
        _validate_type_reference(call.returns, ir, f"call {call.c_name} return")
    for struct in ir.result_structs.values():
        for field in struct.fields:
            _validate_type_reference(
                field.type, ir, f"result struct {struct.name} field '{field.name}'"
            )
    for option in ir.option_structs.values():
        for field in option.fields:
            _validate_type_reference(
                field.type, ir, f"option struct {option.name} field '{field.name}'"
            )


def finalize_abi(ir: BindingIR) -> BindingABI:
    _validate_semantic_references(ir)
    functions: dict[str, CFunctionIR] = {}
    for call in sorted(ir.calls, key=lambda item: item.c_name):
        try:
            functions[call.c_name] = _finalize_function(call, ir)
        except ValueError as error:
            raise ValueError(f"call {call.c_name}: {error}") from error
    metadata = BindingABI(
        module=ir.module,
        c_prefix=ir.c_prefix,
        handles=_finalize_handles(ir),
        value_types=_finalize_value_types(ir),
        option_structs={
            name: COptionIR(
                name=option.name,
                c_type=option.c_type,
                fields=tuple(
                    COptionFieldIR(
                        field.name,
                        field.type,
                        _option_field_c_type(field.type, ir),
                        field.doc,
                        f"has_{field.name}" if field.type.nullable else None,
                        field.has_default,
                    )
                    for field in option.fields
                ),
            )
            for name, option in ir.option_structs.items()
        },
        functions=functions,
        error_functions={
            "clear_error": f"{ir.c_prefix}_clear_error",
            "last_error_message": f"{ir.c_prefix}_last_error_message",
            "last_error_kind": f"{ir.c_prefix}_last_error_kind",
            "last_error_code": f"{ir.c_prefix}_last_error_code",
        },
    )
    _validate_finalized_contract(ir, metadata)
    return metadata


def _validate_finalized_contract(ir: BindingIR, metadata: BindingABI) -> None:
    calls = ir.calls
    symbols = [call.c_name for call in calls]
    duplicates = sorted({symbol for symbol in symbols if symbols.count(symbol) > 1})
    if duplicates:
        raise ValueError(
            f"Duplicate C symbols in finalized BindingIR: {', '.join(duplicates)}"
        )
    for call in calls:
        if call.receiver is not None and call.receiver not in ir.handles:
            raise ValueError(
                f"Unknown receiver '{call.receiver}' in call {call.c_name}"
            )
        function = metadata.functions.get(call.c_name)
        if function is None:
            raise ValueError(f"Missing finalized ABI function for {call.c_name}")
        out_params = [param for param in function.params if param.role == "out_result"]
        expected = 0 if call.returns.kind == "void" else 1
        if len(out_params) != expected:
            raise ValueError(
                f"Call {call.c_name} has {len(out_params)} out-result parameters; expected {expected}"
            )
    c_types = [value.c_type for value in metadata.value_types.values()]
    duplicate_types = sorted(
        {c_type for c_type in c_types if c_types.count(c_type) > 1}
    )
    if duplicate_types:
        raise ValueError(
            f"Duplicate generated C type definitions: {', '.join(duplicate_types)}"
        )
    missing_destroy = [
        value.c_type
        for value in (*metadata.handles.values(), *metadata.value_types.values())
        if value.kind in {"handle", "string", "sequence", "handle_sequence", "variant"}
        and not value.destroy_function
    ]
    if missing_destroy:
        raise ValueError(
            f"Missing destructor symbols for: {', '.join(missing_destroy)}"
        )
