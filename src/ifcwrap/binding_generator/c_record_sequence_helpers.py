"""Render owned output sequences whose elements are generated result records."""

from __future__ import annotations

from .abi_ir import (
    _result_record_list_c_type,
    _result_record_list_destroy_name,
    _result_record_list_make_name,
    _used_result_record_lists,
    _value_destroy_name,
)
from .binding_ir import BindingIR
from .c_call_rendering import _render_result_struct_field_assignments


def _render_result_record_list_helpers(spec: BindingIR) -> str:
    blocks: list[str] = []
    for struct in _used_result_record_lists(spec):
        list_type = _result_record_list_c_type(struct)
        destroy = _result_record_list_destroy_name(struct)
        assignments = "\n".join(
            _render_result_struct_field_assignments(
                struct, spec, "values[i]", "items[i]", "            "
            )
        )
        blocks.append(
            f"""static {list_type} {_result_record_list_make_name(struct)}(std::vector<{struct.cpp_type}> values) {{
    auto* items = values.empty() ? nullptr : new {struct.c_type}[values.size()]{{}};
    try {{
        for (size_t i = 0; i < values.size(); ++i) {{
{assignments}
        }}
    }} catch (...) {{
        for (size_t i = 0; i < values.size(); ++i) {{
            {_value_destroy_name(struct.c_type)}(&items[i]);
        }}
        delete[] items;
        throw;
    }}
    return {list_type}{{items, values.size()}};
}}

void {destroy}({list_type}* value) {{
    if (value == nullptr) {{
        return;
    }}
    for (size_t i = 0; i < value->size; ++i) {{
        {_value_destroy_name(struct.c_type)}(&value->items[i]);
    }}
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}}"""
        )
    return "\n\n".join(blocks)


__all__ = ["_render_result_record_list_helpers"]
