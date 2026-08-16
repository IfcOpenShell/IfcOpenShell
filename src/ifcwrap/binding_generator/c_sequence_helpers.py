# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

from .abi_ir import (
    _SEQUENCE_LEAF_C_TYPE,
    _handle_destroy_name,
    _handle_list_c_type,
    _handle_list_destroy_name,
    _handle_list_list_c_type,
    _handle_list_list_destroy_name,
    _sequence_c_type,
    _sequence_destroy_name,
    _sequence_kind_parts,
    _sequence_prev_kind,
    _snake_name,
    _type_spec_sequence_kind,
)
from .authored_spec import HandleSpec, TypeSpec
from .binding_ir import BindingIR

_SEQUENCE_LEAF_CPP_TYPE: dict[str, str] = {
    "string": "std::string",
    "bool": "bool",
    "int32": "int",
    "int64": "int64_t",
    "uint8": "uint8_t",
    "uint32": "unsigned int",
    "double": "double",
}


def _is_sequence_kind(kind: str) -> bool:
    return _sequence_kind_parts(kind) is not None


def _sequence_make_name(kind: str) -> str:
    return f"make_{kind}"


def _sequence_to_cpp_name(kind: str) -> str:
    return f"to_cpp_{kind}"


def _sequence_cpp_type(kind: str) -> str:
    leaf, depth = _sequence_kind_parts(kind) or ("", 0)
    cpp_type = _SEQUENCE_LEAF_CPP_TYPE[leaf]
    for _ in range(depth):
        cpp_type = f"std::vector<{cpp_type}>"
    return cpp_type


def _sequence_items_c_type(kind: str) -> str:
    leaf, depth = _sequence_kind_parts(kind) or ("", 0)
    if depth == 1:
        return _SEQUENCE_LEAF_C_TYPE[leaf]
    return _sequence_c_type(_sequence_prev_kind(kind))


def _render_common_type_decls(sequence_kinds: tuple[str, ...]) -> str:
    typedefs = [
        """typedef struct ifcopenshell_string_t {
    char* data;
    size_t size;
    bool owned;
    void* owner;
} ifcopenshell_string_t;""",
        """typedef enum ifcopenshell_logical_t {
    IFCOPENSHELL_LOGICAL_UNKNOWN = -1,
    IFCOPENSHELL_LOGICAL_FALSE = 0,
    IFCOPENSHELL_LOGICAL_TRUE = 1
} ifcopenshell_logical_t;""",
    ]
    for kind in sequence_kinds:
        typedefs.append(
            f"""typedef struct {_sequence_c_type(kind)} {{
    {_sequence_items_c_type(kind)}* items;
    size_t size;
    void* owner;
}} {_sequence_c_type(kind)};"""
        )
    decls = [
        "void ifcopenshell_buffer_owner_destroy(void** owner);",
        "void ifcopenshell_string_destroy(ifcopenshell_string_t* value);",
    ]
    decls.extend(
        f"void {_sequence_destroy_name(kind)}({_sequence_c_type(kind)}* value);"
        for kind in sequence_kinds
    )
    return "\n\n".join((*typedefs, *decls))


def _render_sequence_destroy_impl(kind: str) -> str:
    leaf, depth = _sequence_kind_parts(kind) or ("", 0)
    if depth == 1:
        body = ""
    else:
        child_destroy = _sequence_destroy_name(_sequence_prev_kind(kind))
        body = (
            "    for (size_t i = 0; i < value->size; ++i) {\n"
            f"        {child_destroy}(&value->items[i]);\n"
            "    }"
        )
    return f"""void {_sequence_destroy_name(kind)}({_sequence_c_type(kind)}* value) {{
    if (value == nullptr) {{
        return;
    }}
    if (value->owner == nullptr) {{
        value->items = nullptr;
        value->size = 0;
        return;
    }}
{body}
    ifcopenshell_buffer_owner_destroy(&value->owner);
    value->items = nullptr;
    value->size = 0;
}}"""


def _render_common_type_impls(sequence_kinds: tuple[str, ...]) -> str:
    impls = [
        """void ifcopenshell_buffer_owner_destroy(void** owner) {
    if (owner == nullptr || *owner == nullptr) {
        return;
    }
    delete static_cast<capi_buffer_owner*>(*owner);
    *owner = nullptr;
}

void ifcopenshell_string_destroy(ifcopenshell_string_t* value) {
    if (value == nullptr) {
        return;
    }
    if (value->owner != nullptr) {
        ifcopenshell_buffer_owner_destroy(&value->owner);
    } else if (value->owned && value->data != nullptr) {
        delete[] value->data;
    }
    value->data = nullptr;
    value->size = 0;
    value->owned = false;
    value->owner = nullptr;
}"""
    ]
    impls.extend(_render_sequence_destroy_impl(kind) for kind in sequence_kinds)
    return "\n\n".join(impls)


def _render_sequence_make_impl(kind: str) -> str:
    leaf, depth = _sequence_kind_parts(kind) or ("", 0)
    cpp_type = _sequence_cpp_type(kind)
    c_type = _sequence_c_type(kind)
    if depth == 1:
        if leaf == "string":
            return f"""static {c_type} {_sequence_make_name(kind)}({cpp_type} values) {{
    struct owner_type final : capi_buffer_owner {{
        explicit owner_type({cpp_type} source) : values(std::move(source)) {{
            items.reserve(values.size());
            for (auto& value : values) {{
                items.push_back(ifcopenshell_string_t{{value.data(), value.size(), false, nullptr}});
            }}
        }}
        {cpp_type} values;
        std::vector<ifcopenshell_string_t> items;
    }};
    auto owner = std::make_unique<owner_type>(std::move(values));
    auto* items = owner->items.empty() ? nullptr : owner->items.data();
    const auto size = owner->items.size();
    return {c_type}{{items, size, owner.release()}};
}}"""
        if leaf == "bool":
            return f"""static {c_type} {_sequence_make_name(kind)}({cpp_type} values) {{
    auto owner = std::make_unique<capi_array_owner<bool>>(values.size());
    for (size_t i = 0; i < values.size(); ++i) {{
        owner->values[i] = values[i];
    }}
    auto* items = owner->values.get();
    const auto size = values.size();
    return {c_type}{{items, size, owner.release()}};
}}"""
        cast = (
            f"reinterpret_cast<{_sequence_items_c_type(kind)}*>(stored.data())"
            if leaf in {"int32", "uint32"}
            else "stored.data()"
        )
        return f"""static {c_type} {_sequence_make_name(kind)}({cpp_type} values) {{
    auto owner = std::make_unique<capi_value_owner<{cpp_type}>>(std::move(values));
    auto& stored = owner->value;
    auto* items = stored.empty() ? nullptr : {cast};
    const auto size = stored.size();
    return {c_type}{{items, size, owner.release()}};
}}"""
    prev_kind = _sequence_prev_kind(kind)
    items_type = _sequence_items_c_type(kind)
    return f"""static {c_type} {_sequence_make_name(kind)}({cpp_type} values) {{
    auto owner = std::make_unique<capi_value_owner<std::vector<{items_type}>>>(std::vector<{items_type}>{{}});
    auto& items = owner->value;
    items.reserve(values.size());
    try {{
        for (auto& value : values) {{
            items.push_back({_sequence_make_name(prev_kind)}(std::move(value)));
        }}
    }} catch (...) {{
        for (auto& item : items) {{
            {_sequence_destroy_name(prev_kind)}(&item);
        }}
        throw;
    }}
    auto* data = items.empty() ? nullptr : items.data();
    const auto size = items.size();
    return {c_type}{{data, size, owner.release()}};
}}"""


def _render_sequence_to_cpp_impl(kind: str) -> str:
    leaf, depth = _sequence_kind_parts(kind) or ("", 0)
    cpp_type = _sequence_cpp_type(kind)
    c_type = _sequence_c_type(kind)
    if depth == 1:
        if leaf == "string":
            body = (
                "    std::vector<std::string> result;\n"
                "    result.reserve(value->size);\n"
                "    for (size_t i = 0; i < value->size; ++i) {\n"
                "        const auto& item = value->items[i];\n"
                "        if (item.data == nullptr && item.size > 0) {\n"
                '            throw std::runtime_error("string_list contains a null string buffer");\n'
                "        }\n"
                '        result.emplace_back(item.data == nullptr ? "" : item.data, item.size);\n'
                "    }\n"
                "    return result;"
            )
        elif leaf == "bool":
            body = (
                "    std::vector<bool> result;\n"
                "    result.reserve(value->size);\n"
                "    for (size_t i = 0; i < value->size; ++i) {\n"
                "        result.push_back(value->items[i]);\n"
                "    }\n"
                "    return result;"
            )
        else:
            body = (
                "    if (value->size == 0) {\n"
                "        return {};\n"
                "    }\n"
                f"    return {cpp_type}(value->items, value->items + value->size);"
            )
        return f"""static {cpp_type} {_sequence_to_cpp_name(kind)}(const {c_type}* value) {{
    validate_list_items("{kind}", value->items, value->size);
{body}
}}"""
    prev_kind = _sequence_prev_kind(kind)
    return f"""static {cpp_type} {_sequence_to_cpp_name(kind)}(const {c_type}* value) {{
    validate_list_items("{kind}", value->items, value->size);
    {cpp_type} result;
    result.reserve(value->size);
    for (size_t i = 0; i < value->size; ++i) {{
        result.push_back({_sequence_to_cpp_name(prev_kind)}(&value->items[i]));
    }}
    return result;
}}"""


def _render_sequence_helpers(sequence_kinds: tuple[str, ...]) -> str:
    blocks: list[str] = []
    for kind in sequence_kinds:
        blocks.append(_render_sequence_make_impl(kind))
        blocks.append(_render_sequence_to_cpp_impl(kind))
    return "\n\n".join(blocks)


def _handle_list_helper_name(handle: HandleSpec) -> str:
    return f"make_{_snake_name(_handle_list_c_type(handle))}"


def _handle_list_list_helper_name(handle: HandleSpec) -> str:
    return f"make_{_snake_name(_handle_list_list_c_type(handle))}"


def _render_handle_list_helpers(handle: HandleSpec) -> str:
    list_c = _handle_list_c_type(handle)
    helper_name = _handle_list_helper_name(handle)
    snake = _snake_name(list_c)
    if handle.ptr_type == "value":
        return f"""template <typename Value>
static {list_c} {helper_name}(const std::vector<Value>& values) {{
    auto** items = values.empty() ? nullptr : new {handle.c_type}*[values.size()];
    size_t initialized = 0;
    try {{
        for (size_t i = 0; i < values.size(); ++i) {{
            items[i] = new {handle.c_type}{{{handle.cpp_type}(values[i])}};
            ++initialized;
        }}
    }} catch (...) {{
        for (size_t j = 0; j < initialized; ++j) {{ delete items[j]; }}
        delete[] items;
        throw;
    }}
    return {list_c}{{items, values.size()}};
}}

static std::vector<{handle.cpp_type}> to_cpp_{snake}(const {list_c}* values) {{
    validate_list_items("{snake}", values->items, values->size);
    std::vector<{handle.cpp_type}> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {{
        auto* item = values->items[i];
        if (item == nullptr) {{
            throw std::runtime_error("handle_list contains an invalid handle");
        }}
        result.push_back(item->value);
    }}
    return result;
}}"""
    if handle.ptr_type == "shared_ptr":
        return f"""static {list_c} {helper_name}(const std::vector<std::shared_ptr<{handle.cpp_type}>>& values) {{
    auto** items = values.empty() ? nullptr : new {handle.c_type}*[values.size()];
    size_t initialized = 0;
    try {{
        for (size_t i = 0; i < values.size(); ++i) {{
            items[i] = new {handle.c_type}{{values[i]}};
            ++initialized;
        }}
    }} catch (...) {{
        for (size_t j = 0; j < initialized; ++j) {{ delete items[j]; }}
        delete[] items;
        throw;
    }}
    return {list_c}{{items, values.size()}};
}}

static std::vector<std::shared_ptr<{handle.cpp_type}>> to_cpp_{snake}(const {list_c}* values) {{
    validate_list_items("{snake}", values->items, values->size);
    std::vector<std::shared_ptr<{handle.cpp_type}>> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {{
        auto* item = values->items[i];
        if (item == nullptr) {{
            throw std::runtime_error("handle_list contains an invalid handle");
        }}
        result.push_back(item->ptr);
    }}
    return result;
}}"""
    return f"""static {list_c} {helper_name}(const std::vector<{handle.cpp_type}*>& values) {{
    auto** items = values.empty() ? nullptr : new {handle.c_type}*[values.size()];
    size_t initialized = 0;
    try {{
        for (size_t i = 0; i < values.size(); ++i) {{
            items[i] = new {handle.c_type}{{values[i], false}};
            ++initialized;
        }}
    }} catch (...) {{
        for (size_t j = 0; j < initialized; ++j) {{ delete items[j]; }}
        delete[] items;
        throw;
    }}
    return {list_c}{{items, values.size()}};
}}

static {list_c} {helper_name}(const std::vector<const {handle.cpp_type}*>& values) {{
    auto** items = values.empty() ? nullptr : new {handle.c_type}*[values.size()];
    size_t initialized = 0;
    try {{
        for (size_t i = 0; i < values.size(); ++i) {{
            items[i] = new {handle.c_type}{{const_cast<{handle.cpp_type}*>(values[i]), false}};
            ++initialized;
        }}
    }} catch (...) {{
        for (size_t j = 0; j < initialized; ++j) {{ delete items[j]; }}
        delete[] items;
        throw;
    }}
    return {list_c}{{items, values.size()}};
}}

static {list_c} {helper_name}(std::vector<std::unique_ptr<{handle.cpp_type}>> values) {{
    auto** items = values.empty() ? nullptr : new {handle.c_type}*[values.size()];
    size_t initialized = 0;
    try {{
        for (size_t i = 0; i < values.size(); ++i) {{
            items[i] = new {handle.c_type}{{values[i].release(), true}};
            ++initialized;
        }}
    }} catch (...) {{
        for (size_t j = 0; j < initialized; ++j) {{ delete items[j]; }}
        delete[] items;
        throw;
    }}
    return {list_c}{{items, values.size()}};
}}

static std::vector<const {handle.cpp_type}*> to_cpp_{snake}(const {list_c}* values) {{
    validate_list_items("{snake}", values->items, values->size);
    std::vector<const {handle.cpp_type}*> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {{
        auto* item = values->items[i];
        if (item == nullptr || item->ptr == nullptr) {{
            throw std::runtime_error("handle_list contains an invalid handle");
        }}
        result.push_back(item->ptr);
    }}
    return result;
}}"""


def _render_handle_list_list_helpers(handle: HandleSpec) -> str:
    list_list_c = _handle_list_list_c_type(handle)
    list_c = _handle_list_c_type(handle)
    helper_name = _handle_list_list_helper_name(handle)
    row_helper_name = _handle_list_helper_name(handle)
    snake = _snake_name(list_list_c)
    row_snake = _snake_name(list_c)
    if handle.ptr_type == "value":
        value_vector = f"std::vector<std::vector<{handle.cpp_type}>>"
        return f"""static {list_list_c} {helper_name}(const {value_vector}& values) {{
    auto* items = values.empty() ? nullptr : new {list_c}[values.size()];
    for (size_t i = 0; i < values.size(); ++i) {{
        items[i] = {row_helper_name}(values[i]);
    }}
    return {list_list_c}{{items, values.size()}};
}}

static {value_vector} to_cpp_{snake}(const {list_list_c}* values) {{
    validate_list_items("{snake}", values->items, values->size);
    {value_vector} result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {{
        result.push_back(to_cpp_{row_snake}(&values->items[i]));
    }}
    return result;
}}"""
    if handle.ptr_type == "shared_ptr":
        shared_vector = f"std::vector<std::vector<std::shared_ptr<{handle.cpp_type}>>>"
        return f"""static {list_list_c} {helper_name}(const {shared_vector}& values) {{
    auto* items = values.empty() ? nullptr : new {list_c}[values.size()];
    for (size_t i = 0; i < values.size(); ++i) {{
        items[i] = {row_helper_name}(values[i]);
    }}
    return {list_list_c}{{items, values.size()}};
}}

static std::vector<std::vector<std::shared_ptr<{handle.cpp_type}>>> to_cpp_{snake}(const {list_list_c}* values) {{
    validate_list_items("{snake}", values->items, values->size);
    std::vector<std::vector<std::shared_ptr<{handle.cpp_type}>>> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {{
        result.push_back(to_cpp_{row_snake}(&values->items[i]));
    }}
    return result;
}}"""
    return f"""static {list_list_c} {helper_name}(const std::vector<std::vector<{handle.cpp_type}*>>& values) {{
    auto* items = values.empty() ? nullptr : new {list_c}[values.size()];
    for (size_t i = 0; i < values.size(); ++i) {{
        items[i] = {row_helper_name}(values[i]);
    }}
    return {list_list_c}{{items, values.size()}};
}}

static {list_list_c} {helper_name}(const std::vector<std::vector<const {handle.cpp_type}*>>& values) {{
    auto* items = values.empty() ? nullptr : new {list_c}[values.size()];
    for (size_t i = 0; i < values.size(); ++i) {{
        items[i] = {row_helper_name}(values[i]);
    }}
    return {list_list_c}{{items, values.size()}};
}}

static std::vector<std::vector<const {handle.cpp_type}*>> to_cpp_{snake}(const {list_list_c}* values) {{
    validate_list_items("{snake}", values->items, values->size);
    std::vector<std::vector<const {handle.cpp_type}*>> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {{
        result.push_back(to_cpp_{row_snake}(&values->items[i]));
    }}
    return result;
}}"""


def _render_handle_list_destroy_decl(handle: HandleSpec) -> str:
    list_c_type = _handle_list_c_type(handle)
    return f"void {_handle_list_destroy_name(handle)}({list_c_type}* value);"


def _render_handle_list_list_destroy_decl(handle: HandleSpec) -> str:
    list_list_c_type = _handle_list_list_c_type(handle)
    return f"void {_handle_list_list_destroy_name(handle)}({list_list_c_type}* value);"


def _render_handle_list_destroy_impl(handle: HandleSpec) -> str:
    list_c_type = _handle_list_c_type(handle)
    return f"""void {_handle_list_destroy_name(handle)}({list_c_type}* value) {{
    if (value == nullptr || value->items == nullptr) {{
        return;
    }}
    for (size_t i = 0; i < value->size; ++i) {{
        if (value->items[i] != nullptr) {{
            {_handle_destroy_name(handle)}(value->items[i]);
        }}
    }}
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}}"""


def _render_handle_list_list_destroy_impl(handle: HandleSpec) -> str:
    list_list_c_type = _handle_list_list_c_type(handle)
    return f"""void {_handle_list_list_destroy_name(handle)}({list_list_c_type}* value) {{
    if (value == nullptr || value->items == nullptr) {{
        return;
    }}
    for (size_t i = 0; i < value->size; ++i) {{
        {_handle_list_destroy_name(handle)}(&value->items[i]);
    }}
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}}"""


def _used_handle_list_handles(spec: BindingIR) -> tuple[HandleSpec, ...]:
    if spec.abi is None:
        raise ValueError("C emission requires a finalized BindingIR")
    handles_by_c_type = {handle.c_type: handle for handle in spec.handles.values()}
    return tuple(
        handles_by_c_type[value.element_type]
        for value in spec.abi.value_types.values()
        if value.kind == "handle_sequence"
        and value.sequence_depth == 1
        and value.element_type in handles_by_c_type
    )


def _used_scalar_sequence_kinds(spec: BindingIR) -> tuple[str, ...]:
    if spec.abi is None:
        raise ValueError("C emission requires a finalized BindingIR")
    return tuple(
        name for name, value in spec.abi.value_types.items() if value.kind == "sequence"
    )


def _sequence_make_helper(kind: str) -> str:
    return _sequence_make_name(kind)


def _sequence_to_cpp_helper(kind: str) -> str:
    return _sequence_to_cpp_name(kind)
