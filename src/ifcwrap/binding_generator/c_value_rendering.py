"""Render recursive cleanup for generated compound C ABI values."""

from __future__ import annotations

from .abi_ir import BindingABI
from .binding_ir import BindingIR


def _normalized_pointer(c_type: str) -> tuple[str, int]:
    normalized = " ".join(c_type.replace(" *", "*").split())
    depth = 0
    while normalized.endswith("*"):
        depth += 1
        normalized = normalized[:-1].strip()
    return normalized.removeprefix("const ").strip(), depth


def _value_type_by_c_type(metadata: BindingABI, c_type: str):
    return next(
        (value for value in metadata.value_types.values() if value.c_type == c_type),
        None,
    )


def _render_field_destroy(
    field_c_type: str, field_expr: str, metadata: BindingABI
) -> str | None:
    base, pointer_depth = _normalized_pointer(field_c_type)
    if pointer_depth == 1:
        handle = next(
            (value for value in metadata.handles.values() if value.c_type == base),
            None,
        )
        if handle is None:
            return None
        return (
            f"    if ({field_expr} != nullptr) {{\n"
            f"        {handle.destroy_function}({field_expr});\n"
            f"        {field_expr} = nullptr;\n"
            "    }"
        )
    value = _value_type_by_c_type(metadata, base)
    if value is None or value.destroy_function is None:
        return None
    return f"    {value.destroy_function}(&{field_expr});"


def _render_result_struct_destroy(value, metadata: BindingABI) -> str:
    if value.kind == "optional_result_struct":
        nested = _value_type_by_c_type(metadata, value.fields[1].c_type)
        nested_destroy = nested.destroy_function if nested is not None else None
        body = (
            f"    if (value->has_value) {{\n"
            f"        {nested_destroy}(&value->value);\n"
            "    }\n"
            "    value->has_value = false;"
            if nested_destroy
            else "    value->has_value = false;"
        )
    else:
        fields = [
            _render_field_destroy(field.c_type, f"value->{field.name}", metadata)
            for field in value.fields
        ]
        body = "\n".join(field for field in fields if field is not None)
        if not body:
            body = "    (void)value;"
    return f"""void {value.destroy_function}({value.c_type}* value) {{
    if (value == nullptr) {{
        return;
    }}
{body}
}}"""


def _compound_value_types(metadata: BindingABI):
    return tuple(
        value
        for value in metadata.value_types.values()
        if value.kind in {"result_struct", "optional_result_struct"}
        and value.destroy_function
    )


def _render_result_struct_destroy_decls(metadata: BindingABI) -> str:
    return "\n".join(
        f"void {value.destroy_function}({value.c_type}* value);"
        for value in _compound_value_types(metadata)
    )


def _render_result_struct_destroy_impls(ir: BindingIR) -> str:
    if ir.abi is None:
        raise ValueError("C emission requires a finalized BindingIR")
    return "\n\n".join(
        _render_result_struct_destroy(value, ir.abi)
        for value in _compound_value_types(ir.abi)
    )


__all__ = [
    "_render_result_struct_destroy_decls",
    "_render_result_struct_destroy_impls",
]
