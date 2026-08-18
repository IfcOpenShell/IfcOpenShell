# SPDX-License-Identifier: LGPL-3.0-or-later

from __future__ import annotations

from src.ifcwrap.binding_generator.abi_ir import (
    BindingABI,
    CFieldIR,
    CFunctionIR,
    CParamIR,
    CTypeIR,
)
from src.ifcwrap.binding_generator.binding_model import TypeSpec
from src.ifcwrap.binding_generator.targets.wasm.backend import render_wasm_bindings


def make_metadata() -> BindingABI:
    file_handle = CTypeIR(
        c_type="ifcopenshell_file_t",
        kind="handle",
        fields=(CFieldIR("ptr", "void*"), CFieldIR("owned", "bool")),
        destroy_function="ifcopenshell_file_destroy",
        layout="ptr_owned",
    )
    open_function = CFunctionIR(
        c_name="ifcopenshell_parse_open",
        restype="bool",
        params=(
            CParamIR("path", "const char*", "param", "string"),
            CParamIR("streaming", "bool", "param", "bool"),
            CParamIR(
                "out_result",
                "ifcopenshell_file_t**",
                "out_result",
                "handle",
            ),
        ),
        error_policy="bool_return_last_error",
        returns=TypeSpec(kind="handle", handle="file"),
        receiver=None,
    )
    return BindingABI(
        module="ifcopenshell",
        c_prefix="ifcopenshell",
        handles={"file": file_handle},
        value_types={},
        option_structs={},
        functions={
            open_function.c_name: open_function,
        },
        error_functions={
            "clear_error": "ifcopenshell_clear_error",
            "last_error_message": "ifcopenshell_last_error_message",
            "last_error_kind": "ifcopenshell_last_error_kind",
            "last_error_code": "ifcopenshell_last_error_code",
        },
    )


def test_wasm_glue_wraps_handles() -> None:
    javascript, _ = render_wasm_bindings(make_metadata())

    assert "ifcopenshell_parse_open" in javascript
    assert "ifcopenshell_file_destroy" in javascript
    assert "class IfcOpenshellFile" in javascript
    assert "UTF8ToString" in javascript
    assert (
        "module.loadDynamicLibrary(path, { global: true, allowUndefined: true });"
        in javascript
    )
    assert "loadAsync" not in javascript
    assert "IfcOpenShellErrorKind.CANCELLED" in javascript
    assert "IfcOpenShellErrorCode.OPERATION_CANCELLED" in javascript
    assert "Cyclic WASM plugin dependency" in javascript


def test_typescript_declares_low_level_contract() -> None:
    _, declarations = render_wasm_bindings(make_metadata())

    assert "export class IfcOpenshellFile" in declarations
    assert "open(path: string, streaming: boolean)" in declarations
    assert "CANCELLED: 4" in declarations
    assert "OPERATION_CANCELLED: 4" in declarations
