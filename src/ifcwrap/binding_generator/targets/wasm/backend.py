from __future__ import annotations

from ...abi_ir import BindingABI
from .js_glue import render_js_glue
from .typescript import render_typescript_declarations


def render_wasm_bindings(metadata: BindingABI) -> tuple[str, str]:
    return render_js_glue(metadata, metadata.handles), render_typescript_declarations(
        metadata, metadata.handles
    )


__all__ = ["render_wasm_bindings"]
