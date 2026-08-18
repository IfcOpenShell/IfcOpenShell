"""Pure C/C++ emitter over a finalized BindingIR."""

from __future__ import annotations

from .binding_ir import BindingIR
from .c_call_rendering import _render_call_impl
from .c_handle_rendering import _destroy_body, _handle_storage_type
from .c_header_rendering import _render_header
from .c_internal_header import _render_internal_header
from .c_record_sequence_helpers import _render_result_record_list_helpers
from .c_runtime_support import _render_cpp_support_runtime
from .c_sequence_helpers import (
    _render_common_type_impls,
    _render_handle_list_destroy_impl,
    _render_handle_list_helpers,
    _render_handle_list_list_destroy_impl,
    _render_handle_list_list_helpers,
    _render_sequence_helpers,
    _snake_name,
    _used_handle_list_handles,
    _used_handle_list_list_handles,
    _used_scalar_sequence_kinds,
)
from .c_value_rendering import _render_result_struct_destroy_impls
from .c_variant_helpers import _render_variant_destroy_impls
from .debug import debug_log


def _render_cpp(ir: BindingIR, header_name: str) -> str:
    debug_log(
        "c_backend.render_cpp.start",
        f"module={ir.module} handles={len(ir.handles)} functions={len(ir.functions)} methods={len(ir.methods)}",
    )
    handle_structs = []
    for handle in ir.handles.values():
        storage_type = _handle_storage_type(handle)
        if handle.name in {"attribute_value", "instance_list"}:
            handle_structs.append(
                f"struct {handle.c_type} {{\n    {storage_type} value;\n}};"
            )
        elif handle.ptr_type == "shared_ptr":
            handle_structs.append(
                f"struct {handle.c_type} {{\n    {storage_type} ptr;\n}};"
            )
        elif handle.ptr_type == "value":
            handle_structs.append(
                f"struct {handle.c_type} {{\n    {storage_type} value;\n}};"
            )
        else:
            handle_structs.append(
                f"struct {handle.c_type} {{\n    {storage_type} ptr;\n    bool owned;\n}};"
            )

    destroy_impls = [
        f"""void ifcopenshell_{_snake_name(handle.c_type)}_destroy({handle.c_type}* handle) {{
    if (handle == nullptr) {{
        return;
    }}
    {_destroy_body(handle)}
}}"""
        for handle in ir.handles.values()
    ]

    rendered_calls: list[str] = []
    total_calls = len(ir.calls)
    for index, call in enumerate(ir.calls, start=1):
        if index == 1 or index % 100 == 0 or index == total_calls:
            debug_log(
                "c_backend.render_cpp.calls",
                f"{index}/{total_calls} current={call.c_name}",
            )
        rendered_calls.append(_render_call_impl(call, ir))
    call_impls = "\n\n".join(rendered_calls)
    destroy_impls_block = "\n\n".join(destroy_impls)
    handle_list_types = _used_handle_list_handles(ir)
    handle_list_list_types = _used_handle_list_list_handles(ir)
    sequence_kinds = _used_scalar_sequence_kinds(ir)
    handle_list_helpers = "\n\n".join(
        _render_handle_list_helpers(handle) for handle in handle_list_types
    )
    handle_list_list_helpers = "\n\n".join(
        _render_handle_list_list_helpers(handle) for handle in handle_list_list_types
    )
    handle_list_destroy_impls = "\n\n".join(
        _render_handle_list_destroy_impl(handle) for handle in handle_list_types
    )
    handle_list_list_destroy_impls = "\n\n".join(
        _render_handle_list_list_destroy_impl(handle)
        for handle in handle_list_list_types
    )
    variant_destroy_impls = _render_variant_destroy_impls(ir)
    common_type_impls = _render_common_type_impls(sequence_kinds)
    sequence_helpers = _render_sequence_helpers(sequence_kinds)
    runtime_support = _render_cpp_support_runtime()
    internal_header_name = header_name.removesuffix(".h") + "_internal.hpp"
    rendered = f"""#include "{header_name}"
#include "{internal_header_name}"

#include <algorithm>
#include <array>
#include <cstring>
#include <exception>
#include <fstream>
#include <iterator>
#include <limits>
#include <memory>
#include <new>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <typeinfo>
#include <utility>
#include <variant>
#include <vector>

// Note: project-specific headers (geometry, serializers, schema, etc.) are
// pulled in transitively via {internal_header_name}; do not re-include them
// here to avoid header-guard-less redefinitions in third-party headers.
#include "utils.h"

{runtime_support}

{handle_list_helpers}
{handle_list_list_helpers}

{common_type_impls}

{sequence_helpers}

{_render_result_record_list_helpers(ir)}

void {ir.c_prefix}_clear_error(void) {{
    ifcopenshell::capi::g_last_error_kind = IFCOPENSHELL_ERROR_NONE;
    ifcopenshell::capi::g_last_error_code = IFCOPENSHELL_ERROR_CODE_NONE;
    ifcopenshell::capi::g_last_error.clear();
}}

const char* {ir.c_prefix}_last_error_message(void) {{
    return ifcopenshell::capi::g_last_error.c_str();
}}

int {ir.c_prefix}_last_error_kind(void) {{
    return ifcopenshell::capi::g_last_error_kind;
}}

int {ir.c_prefix}_last_error_code(void) {{
    return ifcopenshell::capi::g_last_error_code;
}}

{destroy_impls_block}
{handle_list_destroy_impls}
{handle_list_list_destroy_impls}
{_render_result_struct_destroy_impls(ir)}
{variant_destroy_impls}

{call_impls}
"""
    debug_log("c_backend.render_cpp.done", f"module={ir.module} bytes={len(rendered)}")
    return rendered


def render_c_abi(
    ir: BindingIR, header_name: str = "ifcopenshell_api.h"
) -> dict[str, str]:
    if ir.abi is None:
        raise ValueError("C emission requires a finalized BindingIR")
    return {
        header_name: _render_header(ir),
        header_name.removesuffix(".h") + ".cpp": _render_cpp(ir, header_name),
        header_name.removesuffix(".h") + "_internal.hpp": _render_internal_header(
            ir, header_name
        ),
    }
