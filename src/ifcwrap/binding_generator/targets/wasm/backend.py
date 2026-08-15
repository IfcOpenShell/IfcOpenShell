# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

from ...abi_ir import BindingABI
from .js_glue import render_js_glue
from .typescript import render_typescript_declarations


def render_wasm_bindings(metadata: BindingABI) -> tuple[str, str]:
    return render_js_glue(metadata, metadata.handles), render_typescript_declarations(
        metadata, metadata.handles
    )


def render_export_list(metadata: BindingABI) -> str:
    exports = {
        "_malloc",
        "_free",
        f"_{metadata.error_functions['clear_error']}",
        f"_{metadata.error_functions['last_error_message']}",
        f"_{metadata.error_functions['last_error_kind']}",
        f"_{metadata.error_functions['last_error_code']}",
    }
    exports.update(f"_{function.c_name}" for function in metadata.functions.values())
    exports.update(
        f"_{handle.destroy_function}"
        for handle in metadata.handles.values()
        if handle.destroy_function
    )
    exports.update(
        f"_{value.destroy_function}"
        for value in metadata.value_types.values()
        if value.destroy_function
    )
    return "\n".join(sorted(exports)) + "\n"


__all__ = ["render_export_list", "render_wasm_bindings"]
