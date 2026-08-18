from __future__ import annotations

from .abi_ir import (
    ErrorCatalogEntryIR,
    _handle_destroy_name,
    _option_list_c_type,
    _result_record_list_c_type,
    _result_record_list_destroy_name,
    _used_result_record_lists,
    _used_variant_types,
    _variant_c_type,
    _variant_list_c_type,
)
from .binding_ir import BindingIR
from .binding_model import HandleSpec
from .c_sequence_helpers import (
    _handle_list_c_type,
    _handle_list_list_c_type,
    _render_common_type_decls,
    _render_handle_list_destroy_decl,
    _render_handle_list_list_destroy_decl,
    _used_handle_list_handles,
    _used_handle_list_list_handles,
    _used_scalar_sequence_kinds,
)
from .c_type_rendering import (
    _ordered_result_structs,
    _render_call_decl,
    _render_option_struct_decl,
    _render_optional_result_struct_decl,
    _render_result_struct_decl,
    _render_variant_decl,
)
from .c_value_rendering import _render_result_struct_destroy_decls
from .c_variant_helpers import _render_variant_destroy_decls
from .debug import debug_log


def _render_handle_destroy_decl(handle: HandleSpec) -> str:
    return f"void {_handle_destroy_name(handle)}({handle.c_type}* handle);"


def _render_error_enum(
    entries: tuple[ErrorCatalogEntryIR, ...], prefix: str, c_type: str
) -> str:
    values = ",\n".join(
        f"    {prefix}{entry.name} = {entry.value}" for entry in entries
    )
    return f"typedef enum {{\n{values}\n}} {c_type};"


def _render_header(spec: BindingIR) -> str:
    debug_log(
        "c_backend.render_header.start",
        f"module={spec.module} handles={len(spec.handles)} functions={len(spec.functions)} methods={len(spec.methods)}",
    )
    guard = f"{spec.c_prefix.upper()}_API_H"
    handle_forwards = "\n".join(
        f"typedef struct {handle.c_type} {handle.c_type};"
        for handle in spec.handles.values()
    )
    handle_list_types = _used_handle_list_handles(spec)
    handle_list_list_types = _used_handle_list_list_handles(spec)
    handle_list_forwards = "\n".join(
        f"typedef struct {_handle_list_c_type(handle)} {{\n"
        f"    {handle.c_type}** items;\n"
        f"    size_t size;\n"
        f"}} {_handle_list_c_type(handle)};"
        for handle in handle_list_types
    )
    handle_list_list_forwards = "\n".join(
        f"typedef struct {_handle_list_list_c_type(handle)} {{\n"
        f"    {_handle_list_c_type(handle)}* items;\n"
        f"    size_t size;\n"
        f"}} {_handle_list_list_c_type(handle)};"
        for handle in handle_list_list_types
    )
    result_record_lists = {
        struct.name: struct for struct in _used_result_record_lists(spec)
    }
    result_decl_blocks = []
    for struct in _ordered_result_structs(spec):
        result_decl_blocks.append(_render_result_struct_decl(struct, spec))
        if struct.name in result_record_lists:
            list_type = _result_record_list_c_type(struct)
            result_decl_blocks.append(
                f"typedef struct {list_type} {{\n    {struct.c_type}* items;\n    size_t size;\n}} {list_type};"
            )
    result_struct_decls = "\n\n".join(result_decl_blocks)
    optional_result_struct_decls = "\n\n".join(
        _render_optional_result_struct_decl(call.returns, spec)
        for call in spec.calls
        if call.returns.kind == "struct" and call.returns.nullable
    )
    variant_decls = "\n\n".join(
        _render_variant_decl(variant, spec) for variant in _used_variant_types(spec)
    )
    variant_list_decls = "\n\n".join(
        f"typedef struct {_variant_list_c_type(variant, spec)} {{\n"
        f"    {_variant_c_type(variant, spec)}* items;\n"
        f"    size_t size;\n"
        f"}} {_variant_list_c_type(variant, spec)};"
        for variant in _used_variant_types(spec)
        if variant.sequence_depth == 1
    )
    option_struct_forwards = "\n".join(
        f"typedef struct {spec.option_structs[name].c_type} {spec.option_structs[name].c_type};"
        for name in sorted(spec.option_structs)
    )
    option_list_names = {
        param.type.struct
        for call in spec.calls
        for param in call.params
        if param.type.kind == "option"
        and param.type.struct is not None
        and param.type.sequence_depth == 1
    } | {
        field.type.struct
        for option in spec.option_structs.values()
        for field in option.fields
        if field.type.kind == "option"
        and field.type.struct is not None
        and field.type.sequence_depth == 1
    }
    option_list_forwards = "\n".join(
        f"typedef struct {_option_list_c_type(spec.option_structs[name])} "
        f"{_option_list_c_type(spec.option_structs[name])};"
        for name in sorted(option_list_names)
    )
    option_struct_decls = "\n\n".join(
        _render_option_struct_decl(struct, spec)
        for struct in spec.option_structs.values()
    )
    option_list_decls = "\n\n".join(
        f"typedef struct {_option_list_c_type(option)} {{\n"
        f"    {option.c_type}* items;\n"
        f"    size_t size;\n"
        f"}} {_option_list_c_type(option)};"
        for option in spec.option_structs.values()
        if option.name in option_list_names
    )
    destroy_decls = "\n".join(
        _render_handle_destroy_decl(handle) for handle in spec.handles.values()
    )
    handle_list_destroy_decls = "\n".join(
        _render_handle_list_destroy_decl(handle) for handle in handle_list_types
    )
    handle_list_list_destroy_decls = "\n".join(
        _render_handle_list_list_destroy_decl(handle)
        for handle in handle_list_list_types
    )
    variant_destroy_decls = _render_variant_destroy_decls(spec)
    result_struct_destroy_decls = _render_result_struct_destroy_decls(spec.abi)
    result_record_list_destroy_decls = "\n".join(
        f"void {_result_record_list_destroy_name(struct)}({_result_record_list_c_type(struct)}* value);"
        for struct in _used_result_record_lists(spec)
    )
    call_decls = "\n".join(_render_call_decl(call, spec) for call in spec.calls)
    sequence_kinds = _used_scalar_sequence_kinds(spec)
    common_type_decls = _render_common_type_decls(sequence_kinds)
    error_kind_decl = _render_error_enum(
        spec.abi.error_catalog.kinds,
        "IFCOPENSHELL_ERROR_",
        "ifcopenshell_error_kind_t",
    )
    error_code_decl = _render_error_enum(
        spec.abi.error_catalog.codes,
        "IFCOPENSHELL_ERROR_CODE_",
        "ifcopenshell_error_code_t",
    )

    rendered = f"""#ifndef {guard}
#define {guard}

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {{
#endif

/* Common types - guarded to allow multiple API headers to be included */
#ifndef IFCOPENSHELL_COMMON_TYPES_DEFINED
#define IFCOPENSHELL_COMMON_TYPES_DEFINED

{common_type_decls}

#endif /* IFCOPENSHELL_COMMON_TYPES_DEFINED */

{handle_forwards}

{handle_list_forwards}
{handle_list_list_forwards}

{option_struct_forwards}
{option_list_forwards}

{variant_decls}
{variant_list_decls}

{option_struct_decls}

{option_list_decls}

{result_struct_decls}

{optional_result_struct_decls}

{error_kind_decl}

{error_code_decl}

/*
 * Error state is thread-local. Kinds and codes are stable programmatic
 * identifiers; messages are diagnostics and must not be parsed. Every
 * generated call clears the state before execution. A nullable result is a
 * successful absence only when the kind remains IFCOPENSHELL_ERROR_NONE.
 * Returned message storage remains valid until the next error or clear on
 * the calling thread.
 */
void {spec.c_prefix}_clear_error(void);
const char* {spec.c_prefix}_last_error_message(void);
int {spec.c_prefix}_last_error_kind(void);
int {spec.c_prefix}_last_error_code(void);

{destroy_decls}
{handle_list_destroy_decls}
{handle_list_list_destroy_decls}
{result_struct_destroy_decls}
{result_record_list_destroy_decls}
{variant_destroy_decls}

{call_decls}

#ifdef __cplusplus
}}
#endif

#endif
"""
    debug_log(
        "c_backend.render_header.done", f"module={spec.module} bytes={len(rendered)}"
    )
    return rendered
