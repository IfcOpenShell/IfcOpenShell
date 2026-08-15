# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ..binding_model import TypeSpec

if TYPE_CHECKING:
    from ..abi_ir import BindingABI, CFunctionIR, CParamIR

_DOMAIN_PREFIXES = ("ifcopenshell_parse_", "ifcopenshell_geom_")


def _sequence_leaf_type(type_spec: TypeSpec) -> TypeSpec:
    """Remove sequence shape while retaining the element's semantic metadata."""
    if type_spec.sequence_depth <= 0:
        raise ValueError("Expected a sequence type")
    return replace(
        type_spec,
        sequence_depth=0,
        fixed_lengths=(),
        nullable=False,
    )


def _snake_name(c_type: str) -> str:
    return c_type.removeprefix("ifcopenshell_").removesuffix("_t")


def _type_name(c_type: str) -> str:
    return "IfcOpenshell" + "".join(
        part.capitalize() for part in _snake_name(c_type).split("_") if part
    )


def _method_name(c_name: str, c_prefix: str) -> str:
    for prefix in _DOMAIN_PREFIXES:
        if c_name.startswith(prefix):
            return c_name[len(prefix) :]
    exact_prefix = f"{c_prefix}_"
    if c_name.startswith(exact_prefix):
        return c_name[len(exact_prefix) :]
    return c_name.removeprefix("ifcopenshell_")


def _camel_name(name: str) -> str:
    parts = [part for part in name.split("_") if part]
    if not parts:
        return name
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def _module_public_name(name: str) -> str:
    return _camel_name(name)


def _module_type_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_") if part) + "Api"


def _public_name(function: CFunctionIR, c_prefix: str) -> str:
    name = _method_name(function.c_name, c_prefix)
    if function.receiver is not None:
        name = name.removeprefix(f"{function.receiver}_")
    return _camel_name(name)


def _public_module_member(
    function: CFunctionIR, c_prefix: str
) -> tuple[str, str] | None:
    if function.receiver is not None:
        return None
    if function.c_name.startswith("ifcopenshell_parse_"):
        return "parse", _camel_name(function.c_name.removeprefix("ifcopenshell_parse_"))
    if function.c_name.startswith("ifcopenshell_geom_"):
        return "geom", _camel_name(function.c_name.removeprefix("ifcopenshell_geom_"))
    if c_prefix == "ifcopenshell" and function.c_name.startswith("ifcopenshell_"):
        rest = function.c_name.removeprefix("ifcopenshell_")
        public_module = function.public_module
        if public_module and rest.startswith(f"{public_module}_"):
            return public_module, _camel_name(rest.removeprefix(f"{public_module}_"))
        module, sep, member = rest.partition("_")
        if sep and module and member:
            return module, _camel_name(member)
    return None


def _public_module_members(
    function: CFunctionIR, c_prefix: str
) -> tuple[tuple[str, str], ...]:
    """Return the canonical module member and retained compatibility aliases."""
    member = _public_module_member(function, c_prefix)
    if member is None:
        return ()
    result = [member]
    if c_prefix == "ifcopenshell" and function.c_name.startswith("ifcopenshell_"):
        rest = function.c_name.removeprefix("ifcopenshell_")
        legacy_module, separator, legacy_member = rest.partition("_")
        legacy = (
            (legacy_module, _camel_name(legacy_member))
            if separator and legacy_module and legacy_member
            else None
        )
        if legacy is not None and legacy != member:
            result.append(legacy)
    return tuple(result)


def _public_params(function: CFunctionIR) -> tuple[CParamIR, ...]:
    return tuple(param for param in function.params if param.role == "param")


def _typed_buffer_element(function: CFunctionIR, metadata: BindingABI) -> str | None:
    if not function.c_name.endswith("_buffer"):
        return None
    returns = function.returns
    if returns.kind == "double_buffer":
        return "double"
    if returns.kind == "int32_buffer":
        return "int32_t"
    if returns.sequence_depth != 1:
        return None
    sequence = metadata.value_types.get(f"{returns.kind}_list")
    if sequence is None:
        return None
    element_type = " ".join(
        (sequence.element_type or "").replace(" *", "*").split()
    ).removeprefix("const ")
    return (
        element_type
        if element_type in {"double", "int32_t", "uint32_t", "uint8_t"}
        else None
    )


def _buffer_size_function(function: CFunctionIR, metadata: BindingABI) -> CFunctionIR:
    size_name = f"{function.c_name}_size"
    try:
        size_function = metadata.functions[size_name]
    except KeyError as exc:
        raise ValueError(
            f"Typed buffer {function.c_name} requires companion {size_name}"
        ) from exc
    if size_function.receiver != function.receiver:
        raise ValueError(
            f"Typed buffer {function.c_name} and {size_name} must use the same receiver"
        )
    if tuple(param.c_type for param in _public_params(size_function)) != tuple(
        param.c_type for param in _public_params(function)
    ) or size_function.returns.kind not in {"size", "uint32"}:
        raise ValueError(
            f"Typed buffer {size_name} must mirror the buffer parameters and return size"
        )
    return size_function


_INTERNAL_C_FUNCTIONS = frozenset(
    {
        "ifcopenshell_parse_set_plugin_search_paths",
        "ifcopenshell_parse_clear_plugin_search_paths",
        "ifcopenshell_geom_plugin_is_loaded",
        "ifcopenshell_geom_plugin_load",
    }
)


__all__ = [
    "_INTERNAL_C_FUNCTIONS",
    "_buffer_size_function",
    "_camel_name",
    "_method_name",
    "_module_public_name",
    "_module_type_name",
    "_public_module_member",
    "_public_module_members",
    "_public_name",
    "_public_params",
    "_sequence_leaf_type",
    "_snake_name",
    "_type_name",
    "_typed_buffer_element",
]
