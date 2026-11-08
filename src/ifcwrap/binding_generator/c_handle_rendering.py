from __future__ import annotations

from .binding_ir import BindingIR
from .binding_model import HandleSpec, TypeSpec
from .c_type_rendering import _normalize_cpp_type, _qualify_handle_cpp_fragment


def _handle_storage_type(handle: HandleSpec) -> str:
    if handle.ptr_type == "shared_ptr":
        return f"std::shared_ptr<{handle.cpp_type}>"
    if handle.ptr_type == "value":
        return handle.cpp_type
    return f"{handle.cpp_type}*"


def _destroy_body(handle: HandleSpec) -> str:
    if handle.ptr_type == "value":
        return "delete handle;"
    if handle.destructor.startswith("function:"):
        destructor = handle.destructor[len("function:") :].strip()
        return f"if (handle->owned && handle->ptr) {{ {destructor}(handle->ptr); }}\n    delete handle;"
    if handle.destructor == "shared_ptr":
        return "handle->ptr.reset();\n    delete handle;"
    if handle.destructor == "delete":
        return "if (handle->owned && handle->ptr) { delete handle->ptr; }\n    delete handle;"
    return "delete handle;"


def _wrap_handle_expr(type_spec: TypeSpec, expr: str, spec: BindingIR) -> str:
    handle = spec.handles[type_spec.handle]
    owned = "true" if type_spec.ownership == "owned" else "false"
    if handle.ptr_type == "shared_ptr":
        normalized_cpp_type = _normalize_cpp_type(type_spec.cpp_type)
        normalized_handle_type = _normalize_cpp_type(handle.cpp_type)
        if (
            "shared_ptr" not in normalized_handle_type
            and "shared_ptr" not in normalized_cpp_type
            and "::ptr" not in normalized_cpp_type
            and normalized_cpp_type.endswith("&")
        ):
            return f"new {handle.c_type}{{std::make_shared<{handle.cpp_type}>({expr})}}"
        return f"new {handle.c_type}{{{expr}}}"
    if handle.ptr_type == "value":
        normalized_cpp_type = _normalize_cpp_type(type_spec.cpp_type)
        if handle.cpp_type.startswith("std::vector<"):
            if normalized_cpp_type == _normalize_cpp_type(handle.cpp_type):
                return f"new {handle.c_type}{{{expr}}}"
            return (
                f"new {handle.c_type}{{([&]() {{ auto tmp = {expr}; "
                f"return {handle.cpp_type}(tmp.begin(), tmp.end()); }})()}}"
            )
        return f"new {handle.c_type}{{{expr}}}"
    normalized_cpp_type = _normalize_cpp_type(type_spec.cpp_type)
    if normalized_cpp_type.startswith("std::unique_ptr<"):
        return f"new {handle.c_type}{{{expr}.release(), true}}"
    pointer_expr = expr
    if normalized_cpp_type.endswith("&"):
        pointer_expr = f"&({expr})"
    if normalized_cpp_type.startswith("const "):
        cast_target = normalized_cpp_type
        while cast_target.startswith("const "):
            cast_target = cast_target[len("const ") :].strip()
        while cast_target.endswith("&") or cast_target.endswith("*"):
            cast_target = cast_target[:-1].strip()
        cast_target = _qualify_handle_cpp_fragment(cast_target, handle.cpp_type)
        pointer_expr = f"const_cast<{cast_target}*>({pointer_expr})"
    return f"new {handle.c_type}{{{pointer_expr}, {owned}}}"
