# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

import re

from .abi_ir import (
    _optional_struct_c_type,
    _variant_c_type,
)
from .authored_spec import ParamSpec, TypeSpec
from .binding_ir import BindingIR, CallIR
from .binding_model import OptionStructSpec


def _ordered_result_structs(spec: BindingIR) -> tuple[object, ...]:
    ordered: list[object] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(struct: object) -> None:
        if struct.name in visited:
            return
        if struct.name in visiting:
            raise ValueError(f"Cyclic result struct dependency at {struct.name}")
        visiting.add(struct.name)
        for field in struct.fields:
            if field.type.kind == "struct" and field.type.struct is not None:
                visit(spec.result_structs[field.type.struct])
        visiting.remove(struct.name)
        visited.add(struct.name)
        ordered.append(struct)

    for struct in spec.result_structs.values():
        visit(struct)
    return tuple(ordered)


def _normalize_cpp_type(cpp_type: str | None) -> str:
    if not cpp_type:
        return ""
    cpp_type = re.sub(r"/\*.*?\*/", "", cpp_type)
    return " ".join(
        cpp_type.replace(" &", "&")
        .replace(" *", "*")
        .replace("< ", "<")
        .replace(" >", ">")
        .split()
    )


def _qualify_handle_cpp_fragment(cpp_fragment: str, handle_cpp_type: str) -> str:
    qualified = _normalize_cpp_type(handle_cpp_type)
    simple = qualified.rsplit("::", 1)[-1]
    if not simple or "::" in cpp_fragment:
        return cpp_fragment
    return re.sub(rf"\b{re.escape(simple)}\b", qualified, cpp_fragment)


def _render_result_struct_decl(struct: object, spec: BindingIR) -> str:
    if spec.abi is None:
        raise ValueError("C emission requires a finalized BindingIR")
    finalized = spec.abi.value_types[struct.name]
    fields = "\n".join(
        f"    {field.c_type} {field.name};" for field in finalized.fields
    )
    return f"typedef struct {finalized.c_type} {{\n{fields}\n}} {finalized.c_type};"


def _render_optional_result_struct_decl(type_spec: TypeSpec, spec: BindingIR) -> str:
    if spec.abi is None:
        raise ValueError("C emission requires a finalized BindingIR")
    c_type = _optional_struct_c_type(type_spec, spec)
    finalized = next(
        value for value in spec.abi.value_types.values() if value.c_type == c_type
    )
    fields = "\n".join(
        f"    {field.c_type} {field.name};" for field in finalized.fields
    )
    return f"typedef struct {c_type} {{\n{fields}\n}} {c_type};"


def _render_variant_decl(type_spec: TypeSpec, spec: BindingIR) -> str:
    if spec.abi is None:
        raise ValueError("C emission requires a finalized BindingIR")
    c_type = _variant_c_type(type_spec, spec)
    finalized = next(
        value for value in spec.abi.value_types.values() if value.c_type == c_type
    )
    fields = "\n".join(
        f"    {field.c_type} {field.name};" for field in finalized.fields
    )
    return f"typedef struct {c_type} {{\n{fields}\n}} {c_type};"


def _render_option_struct_decl(struct: OptionStructSpec, spec: BindingIR) -> str:
    if spec.abi is None:
        raise ValueError("C emission requires a finalized BindingIR")
    lines: list[str] = []
    for field in spec.abi.option_structs[struct.name].fields:
        lines.append(f"    {field.c_type} {field.name};")
        if field.presence_field is not None:
            lines.append(f"    bool {field.presence_field};")
    fields = "\n".join(lines)
    return f"typedef struct {struct.c_type} {{\n{fields}\n}} {struct.c_type};"


def _render_call_decl(call: CallIR, spec: BindingIR) -> str:
    if spec.abi is None:
        raise ValueError("C emission requires a finalized BindingIR")
    function = spec.abi.functions[call.c_name]
    parts = [f"{param.c_type} {param.name}" for param in function.params]
    params = ", ".join(parts) if parts else "void"
    declaration = f"{function.restype} {call.c_name}({params});"
    if not call.doc:
        return declaration
    return _render_doc_comment(call.doc) + "\n" + declaration


def _render_doc_comment(doc: str) -> str:
    escaped = doc.replace("*/", "* /").strip()
    lines = escaped.splitlines()
    if len(lines) == 1:
        return f"/** {lines[0]} */"
    body = "\n".join(f" * {line}" if line else " *" for line in lines)
    return f"/**\n{body}\n */"
