from __future__ import annotations

import json

from ...abi_ir import (
    BindingABI,
    CFunctionIR,
    COptionIR,
    CParamIR,
    CTypeIR,
    ErrorCatalogEntryIR,
)
from ...binding_model import TypeSpec
from .._shared import (
    _INTERNAL_C_FUNCTIONS,
    _buffer_size_function,
    _camel_name,
    _method_name,
    _public_module_members,
    _public_name,
    _public_params,
    _snake_name,
    _type_name,
    _typed_buffer_element,
)

_POINTER_SIZE = 4

_SCALAR_LAYOUTS = {
    "bool": (1, 1),
    "int32": (4, 4),
    "uint8": (1, 1),
    "uint32": (4, 4),
    "size": (4, 4),
    "double": (8, 8),
    "int64": (8, 8),
}


def _normalize_c_type(c_type: str) -> str:
    return " ".join(c_type.replace(" *", "*").split())


def _handle_for_c_type(c_type: str, metadata: BindingABI) -> CTypeIR | None:
    normalized = _normalize_c_type(c_type)
    for handle in metadata.handles.values():
        if normalized in {f"{handle.c_type}*", f"const {handle.c_type}*"}:
            return handle
    return None


def _value_type_by_c_type(c_type: str, metadata: BindingABI) -> CTypeIR | None:
    normalized = (
        _normalize_c_type(c_type).removeprefix("const ").removesuffix("*").strip()
    )
    return next(
        (
            value
            for value in metadata.value_types.values()
            if value.c_type == normalized
        ),
        None,
    )


def _option_type_by_c_type(c_type: str, metadata: BindingABI) -> COptionIR | None:
    normalized = (
        _normalize_c_type(c_type).removeprefix("const ").removesuffix("*").strip()
    )
    return next(
        (
            option
            for option in metadata.option_structs.values()
            if option.c_type == normalized
        ),
        None,
    )


def _enum_value_map(type_spec: TypeSpec) -> dict[str, int] | None:
    if not type_spec.enum_values:
        return None
    if len(type_spec.enum_values) != len(type_spec.enum_numeric_values):
        raise ValueError("Enum names and numeric values must have equal length")
    return dict(zip(type_spec.enum_values, type_spec.enum_numeric_values))


def _enum_input_expr(name: str, type_spec: TypeSpec) -> str:
    values = _enum_value_map(type_spec)
    if values is None:
        return name
    if type_spec.sequence_depth > 0:
        return (
            f"_mapEnumInput({name}, {json.dumps(values)}, "
            f"{type_spec.sequence_depth}, {json.dumps(name)})"
        )
    return f"_enumInputValue({name}, {json.dumps(values)}, {json.dumps(name)})"


def _enum_output_expr(expression: str, type_spec: TypeSpec) -> str:
    values = _enum_value_map(type_spec)
    if values is None:
        return expression
    names = {value: name for name, value in values.items()}
    if type_spec.sequence_depth > 0:
        return (
            f"_mapEnumOutput({expression}, {json.dumps(names)}, "
            f"{type_spec.sequence_depth}, 'result')"
        )
    return f"_enumOutputValue({expression}, {json.dumps(names)}, 'result')"


def _type_layout(c_type: str, metadata: BindingABI) -> tuple[int, int]:
    normalized = _normalize_c_type(c_type)
    if normalized.endswith("*"):
        return _POINTER_SIZE, _POINTER_SIZE
    if normalized in {"bool", "uint8_t"}:
        return 1, 1
    if normalized in {"ifcopenshell_logical_t", "int32_t", "uint32_t", "size_t"}:
        return 4, 4
    if normalized in {"int64_t", "double"}:
        return 8, 8
    struct = _value_type_by_c_type(normalized, metadata)
    if struct is not None:
        return _struct_layout(struct, metadata)
    option = _option_type_by_c_type(normalized, metadata)
    if option is not None:
        return _struct_layout(option, metadata)
    return _POINTER_SIZE, _POINTER_SIZE


def _align_to(offset: int, alignment: int) -> int:
    remainder = offset % alignment
    return offset if remainder == 0 else offset + alignment - remainder


def _struct_layout(struct: CTypeIR, metadata: BindingABI) -> tuple[int, int]:
    offset = 0
    max_alignment = 1
    for field in struct.fields:
        size, alignment = _type_layout(field.c_type, metadata)
        offset = _align_to(offset, alignment)
        offset += size
        max_alignment = max(max_alignment, alignment)
    return _align_to(offset, max_alignment), max_alignment


def _sequence_kind(type_spec: TypeSpec) -> str:
    return f"{type_spec.kind}{'_list' * type_spec.sequence_depth}"


def _sequence_value_type(type_spec: TypeSpec, metadata: BindingABI) -> CTypeIR:
    if type_spec.kind == "handle" and type_spec.handle is not None:
        handle = metadata.handles[type_spec.handle]
        suffix = "_list" * type_spec.sequence_depth
        key = _snake_name(f"{handle.c_type.removesuffix('_t')}{suffix}_t")
        return metadata.value_types[key]
    if type_spec.kind == "struct" and type_spec.struct is not None:
        struct = metadata.value_types[type_spec.struct]
        return next(
            value
            for value in metadata.value_types.values()
            if value.kind == "result_record_sequence"
            and value.element_type == struct.c_type
            and value.sequence_depth == type_spec.sequence_depth
        )
    return metadata.value_types[_sequence_kind(type_spec)]


def _out_allocation(function: CFunctionIR, metadata: BindingABI) -> str | None:
    returns = function.returns
    if returns.kind == "void":
        return None
    if returns.kind == "handle":
        return "POINTER_SIZE"
    if returns.sequence_depth > 0:
        return str(_struct_layout(_sequence_value_type(returns, metadata), metadata)[0])
    if returns.kind in _SCALAR_LAYOUTS:
        return str(_SCALAR_LAYOUTS[returns.kind][0])
    if returns.kind == "string":
        return str(_struct_layout(metadata.value_types["string"], metadata)[0])
    if returns.kind == "struct" and returns.struct is not None:
        if returns.nullable:
            struct = next(
                item
                for item in metadata.value_types.values()
                if item.kind == "optional_result_struct"
                and item.element_type == returns.struct
            )
        else:
            struct = metadata.value_types[returns.struct]
        return str(_struct_layout(struct, metadata)[0])
    if returns.kind == "variant":
        struct = next(
            item
            for item in metadata.value_types.values()
            if item.kind == "variant" and item.element_type == returns.cpp_type
        )
        return str(_struct_layout(struct, metadata)[0])
    return "POINTER_SIZE"


def _read_value_type_expr(
    type_spec: TypeSpec, metadata: BindingABI, ptr_expr: str
) -> str:
    if type_spec.sequence_depth > 0:
        sequence = _sequence_value_type(type_spec, metadata)
        return f"_readValueType(module, {ptr_expr}, _VALUE_TYPES[{json.dumps(sequence.c_type)}])"
    if type_spec.kind == "string":
        return (
            f"_readValueType(module, {ptr_expr}, _VALUE_TYPES['ifcopenshell_string_t'])"
        )
    if type_spec.kind == "struct" and type_spec.struct is not None:
        if type_spec.nullable:
            struct = next(
                item
                for item in metadata.value_types.values()
                if item.kind == "optional_result_struct"
                and item.element_type == type_spec.struct
            )
        else:
            struct = metadata.value_types[type_spec.struct]
        return f"_readValueType(module, {ptr_expr}, _VALUE_TYPES[{json.dumps(struct.c_type)}])"
    if type_spec.kind == "variant":
        struct = next(
            item
            for item in metadata.value_types.values()
            if item.kind == "variant" and item.element_type == type_spec.cpp_type
        )
        return f"_readValueType(module, {ptr_expr}, _VALUE_TYPES[{json.dumps(struct.c_type)}])"
    return "module.getValue(outResultPtr, '*')"


def _return_expr(function: CFunctionIR, metadata: BindingABI) -> str:
    returns = function.returns
    if returns.kind == "void":
        return "undefined"
    if returns.kind in {"string", "struct", "variant"} or returns.sequence_depth > 0:
        result = _read_value_type_expr(returns, metadata, "outResultPtr")
    elif returns.kind == "bool":
        result = "module.getValue(outResultPtr, 'i8') !== 0"
    elif returns.kind in {"int32", "uint32", "size"}:
        result = "module.getValue(outResultPtr, 'i32')"
    elif returns.kind == "double":
        result = "module.getValue(outResultPtr, 'double')"
    elif returns.kind == "int64":
        result = "_readInt64(module, outResultPtr)"
    elif returns.kind == "handle" and returns.handle is not None:
        handle = metadata.handles[returns.handle]
        result = f"_wrap{_type_name(handle.c_type)}(module.getValue(outResultPtr, '*'), true, module)"
    else:
        result = "module.getValue(outResultPtr, '*')"
    return _enum_output_expr(result, returns)


def _out_result_destroy_function(
    function: CFunctionIR, metadata: BindingABI
) -> str | None:
    returns = function.returns
    if returns.sequence_depth > 0:
        destroy = _sequence_value_type(returns, metadata).destroy_function
    elif returns.kind == "string":
        destroy = metadata.value_types["string"].destroy_function
    elif returns.kind == "variant":
        destroy = next(
            item.destroy_function
            for item in metadata.value_types.values()
            if item.kind == "variant" and item.element_type == returns.cpp_type
        )
    elif returns.kind == "struct" and returns.struct is not None:
        if returns.nullable:
            payload = metadata.value_types[returns.struct].c_type
            destroy = next(
                item.destroy_function
                for item in metadata.value_types.values()
                if item.kind == "optional_result_struct"
                and any(field.c_type == payload for field in item.fields)
            )
        else:
            destroy = metadata.value_types[returns.struct].destroy_function
    else:
        destroy = None
    return destroy


def _destroy_out_result(function: CFunctionIR, metadata: BindingABI) -> str | None:
    destroy = _out_result_destroy_function(function, metadata)
    if destroy is None:
        return None
    return f"    if (outResultPtr) module._{destroy}(outResultPtr);"


def _js_arg_expr(
    param: CParamIR, metadata: BindingABI
) -> tuple[str, str | None, str | None]:
    name = param.name
    enum_input = _enum_input_expr(name, param.type) if param.type is not None else name
    option = _option_type_by_c_type(param.c_type, metadata)
    if option is not None:
        ptr_name = f"_{name}Ptr"
        alloc = f"    var {ptr_name} = _allocInputOption(module, {name}, {json.dumps(option.c_type)});"
        cleanup = f"    if ({ptr_name}) _freeInputOption(module, {ptr_name}, {json.dumps(option.c_type)});"
        return ptr_name, alloc, cleanup
    if param.nullable and param.type_kind in {
        "bool",
        "int32",
        "uint32",
        "size",
        "double",
        "int64",
    }:
        ptr_name = f"_{name}Ptr"
        size, value_type = {
            "bool": (1, "i8"),
            "int32": (4, "i32"),
            "uint32": (4, "i32"),
            "size": (4, "i32"),
            "double": (8, "double"),
            "int64": (8, "i64"),
        }[param.type_kind]
        value = f"({name} ? 1 : 0)" if param.type_kind == "bool" else enum_input
        alloc = (
            f"    var {ptr_name} = {name} == null ? 0 : module._malloc({size});\n"
            f"    if ({ptr_name}) module.setValue({ptr_name}, {value}, {json.dumps(value_type)});"
        )
        cleanup = f"    if ({ptr_name}) module._free({ptr_name});"
        return ptr_name, alloc, cleanup
    if param.type_kind == "bool":
        return f"{name} ? 1 : 0", None, None
    handle = _handle_for_c_type(param.c_type, metadata)
    if handle is not None:
        return f"{name} == null ? 0 : {name}.ptr", None, None
    sequence = _value_type_by_c_type(param.c_type, metadata)
    if sequence is not None and sequence.kind == "variant":
        ptr_name = f"_{name}Ptr"
        alloc = (
            f"    var {ptr_name} = {name} == null ? 0 : _allocInputVariant(module, {name}, {json.dumps(sequence.c_type)});"
            if param.nullable
            else f"    var {ptr_name} = _allocInputVariant(module, {name}, {json.dumps(sequence.c_type)});"
        )
        cleanup = f"    if ({ptr_name}) _freeInputVariant(module, {ptr_name}, {json.dumps(sequence.c_type)});"
        return ptr_name, alloc, cleanup
    if (
        sequence is not None
        and sequence.kind
        in {
            "sequence",
            "handle_sequence",
            "input_record_sequence",
            "input_variant_sequence",
        }
        and sequence.sequence_depth >= 1
    ):
        ptr_name = f"_{name}Ptr"
        if sequence.element_type == "ifcopenshell_string_t":
            alloc = (
                f"    var {ptr_name} = {name} == null ? 0 : _allocInputStringList(module, {name});"
                if param.nullable
                else f"    var {ptr_name} = _allocInputStringList(module, {name});"
            )
            cleanup = f"    if ({ptr_name}) _freeInputStringList(module, {ptr_name});"
        elif sequence.kind == "handle_sequence":
            alloc = (
                f"    var {ptr_name} = {name} == null ? 0 : _allocInputHandleSequence(module, {name}, {json.dumps(sequence.c_type)});"
                if param.nullable
                else f"    var {ptr_name} = _allocInputHandleSequence(module, {name}, {json.dumps(sequence.c_type)});"
            )
            cleanup = f"    if ({ptr_name}) _freeInputHandleSequence(module, {ptr_name}, {json.dumps(sequence.c_type)});"
        else:
            alloc = (
                f"    var {ptr_name} = {name} == null ? 0 : _allocInputSequence(module, {enum_input}, {json.dumps(sequence.c_type)});"
                if param.nullable
                else f"    var {ptr_name} = _allocInputSequence(module, {enum_input}, {json.dumps(sequence.c_type)});"
            )
            cleanup = f"    if ({ptr_name}) _freeInputSequence(module, {ptr_name}, {json.dumps(sequence.c_type)});"
        return ptr_name, alloc, cleanup
    if param.type_kind == "string":
        ptr_name = f"_{name}Ptr"
        alloc = (
            f"    var {ptr_name} = {name} == null ? 0 : _allocString(module, {name});"
            if param.nullable
            else f"    var {ptr_name} = _allocString(module, {name});"
        )
        cleanup = f"    if ({ptr_name}) module._free({ptr_name});"
        return ptr_name, alloc, cleanup
    if param.type_kind in {"int32", "uint32", "size", "double", "int64"}:
        return enum_input, None, None
    return name, None, None


def _render_handle_classes(metadata: BindingABI) -> str:
    receiver_groups: dict[str, list[CFunctionIR]] = {}
    for function in metadata.functions.values():
        if function.receiver is not None:
            receiver_groups.setdefault(function.receiver, []).append(function)

    chunks: list[str] = []
    for handle_name, handle in sorted(metadata.handles.items()):
        type_name = _type_name(handle.c_type)
        method_groups: dict[str, list[tuple[CFunctionIR, list[str]]]] = {}
        for function in sorted(
            receiver_groups.get(handle_name, []), key=lambda item: item.c_name
        ):
            if function.c_name == handle.destroy_function:
                continue
            method = _public_name(function, metadata.c_prefix)
            param_names = [param.name for param in _public_params(function)]
            if _typed_buffer_element(function, metadata) is not None:
                param_names.append("arrayType")
            method_groups.setdefault(method, []).append((function, param_names))
        methods = [
            _render_handle_method(method, overloads)
            for method, overloads in method_groups.items()
        ]
        method_block = "\n\n".join(methods)
        destroy = (
            handle.destroy_function
            or f"ifcopenshell_{_snake_name(handle.c_type)}_destroy"
        )
        chunks.append(
            f"export class {type_name} {{\n"
            "    #ptr;\n"
            "    #envelopeOwned;\n"
            "    #module;\n\n"
            "    constructor(ptr, envelopeOwned, module) {\n"
            "        this.#ptr = ptr;\n"
            "        this.#envelopeOwned = envelopeOwned;\n"
            "        this.#module = module;\n"
            "    }\n\n"
            "    get ptr() {\n"
            "        return this.#ptr;\n"
            "    }\n\n"
            "    destroy() {\n"
            f"        if (this.#ptr && this.#envelopeOwned && this.#module._{destroy}) {{\n"
            f"            this.#module._{destroy}(this.#ptr);\n"
            "            this.#ptr = 0;\n"
            "            this.#envelopeOwned = false;\n"
            "        }\n"
            "    }" + ("\n\n" + method_block if method_block else "") + "\n}\n\n"
            f"function _wrap{type_name}(ptr, envelopeOwned, module) {{\n"
            f"    return ptr ? new {type_name}(ptr, envelopeOwned, module) : null;\n"
            "}"
        )
    return "\n\n".join(chunks)


def _render_handle_method(
    method: str, overloads: list[tuple[CFunctionIR, list[str]]]
) -> str:
    if len(overloads) == 1:
        function, param_names = overloads[0]
        params = ", ".join(param_names)
        return (
            f"    {method}({params}) {{\n"
            f"        return invoke_{function.c_name}(this.#module, this{', ' if params else ''}{params});\n"
            "    }"
        )

    by_arity: dict[int, CFunctionIR] = {}
    for function, param_names in overloads:
        arity = len(param_names)
        if arity in by_arity:
            raise ValueError(
                f"Cannot render overloaded JavaScript method {method!r}: "
                f"{by_arity[arity].c_name} and {function.c_name} both take {arity} arguments"
            )
        by_arity[arity] = function

    cases = "\n".join(
        f"            case {arity}: return invoke_{function.c_name}(this.#module, this, ...args);"
        for arity, function in sorted(by_arity.items())
    )
    expected = ", ".join(str(arity) for arity in sorted(by_arity))
    return (
        f"    {method}(...args) {{\n"
        "        switch (args.length) {\n"
        f"{cases}\n"
        f"            default: throw new TypeError({method!r} + ' expects {expected} arguments');\n"
        "        }\n"
        "    }"
    )


def _render_handle_wrapper_switch(metadata: BindingABI) -> str:
    handle_types = sorted(handle.c_type for handle in metadata.handles.values())
    handle_type_set = (
        "const _HANDLE_C_TYPES = new Set(" + json.dumps(handle_types) + ");\n\n"
    )
    cases = []
    for handle in sorted(metadata.handles.values(), key=lambda item: item.c_type):
        type_name = _type_name(handle.c_type)
        cases.append(
            f"        case {json.dumps(handle.c_type)}: return _wrap{type_name}(ptr, owned, module);"
        )
    body = "\n".join(cases) or "        default: return ptr || null;"
    if cases:
        body += "\n        default: return ptr || null;"
    return handle_type_set + (
        "function _wrapHandleByType(module, handleCType, ptr, owned) {\n"
        "    switch (handleCType) {\n"
        f"{body}\n"
        "    }\n"
        "}"
    )


def _render_wrapper(function: CFunctionIR, metadata: BindingABI) -> str:
    public_params = _public_params(function)
    signature_names = ["module"]
    if function.receiver is not None:
        signature_names.append("self")
    signature_names.extend(param.name for param in public_params)
    buffer_element = _typed_buffer_element(function, metadata)
    if buffer_element is not None:
        signature_names.append("arrayType")

    marshalling_lines: list[str] = []
    cleanup_lines: list[str] = []
    arg_exprs: list[str] = []
    if function.receiver is not None:
        arg_exprs.append("self.ptr")
    for param in public_params:
        expr, alloc, cleanup = _js_arg_expr(param, metadata)
        if alloc:
            marshalling_lines.append(alloc)
        if cleanup:
            cleanup_lines.append(cleanup)
        arg_exprs.append(expr)

    allocation_size = _out_allocation(function, metadata)
    out_alloc = ""
    out_free = ""
    out_arg = ""
    if allocation_size is not None:
        out_alloc = f"    outResultPtr = module._malloc({allocation_size});\n"
        out_free = "        if (outResultPtr) module._free(outResultPtr);\n"
        out_arg = ", outResultPtr"

    call_args = ", ".join(arg_exprs)
    if call_args:
        call_args += out_arg
    else:
        call_args = out_arg.removeprefix(", ")

    error_name = function.c_name
    destroy_function = _out_result_destroy_function(function, metadata)
    destroy_line = _destroy_out_result(function, metadata)
    return_body = []
    if function.returns.kind != "void":
        if function.returns.kind in {"double_buffer", "int32_buffer"}:
            return_expr = (
                f"_copyNumericBuffer(module, module.getValue(outResultPtr, '*'), "
                f"module.getValue(outSizePtr, 'i32') >>> 0, {json.dumps(buffer_element)}, arrayType)"
            )
        elif buffer_element is not None:
            return_expr = (
                _read_value_type_expr(
                    function.returns, metadata, "outResultPtr"
                ).removesuffix(")")
                + ", true, arrayType)"
            )
        else:
            return_expr = _return_expr(function, metadata)
        return_body.append("    const result = " + return_expr + ";")
        if destroy_line:
            return_body.append(destroy_line)
            return_body.append("    outResultNeedsDestroy = false;")
        return_body.append("    return result;")
    else:
        return_body.append("    return undefined;")
    return_statement = "\n".join(return_body) + "\n"

    cleanup_block = "\n".join(cleanup_lines + ([out_free.rstrip()] if out_free else []))
    if cleanup_block:
        cleanup_block = cleanup_block + "\n"

    size_alloc = ""
    size_free = ""
    size_call = ""
    if function.returns.kind in {"double_buffer", "int32_buffer"}:
        size_function = _buffer_size_function(function, metadata)
        size_alloc = "    outSizePtr = module._malloc(4);\n"
        size_free = "        if (outSizePtr) module._free(outSizePtr);\n"
        size_args = ", ".join((*arg_exprs, "outSizePtr"))
        size_call = (
            f"    const sizeOk = module._{size_function.c_name}({size_args});\n"
            f"    if (!sizeOk) throw _lastError(module, '{size_function.c_name} failed');\n"
        )

    if function.restype == "void":
        call_block = (
            f"    module._{function.c_name}({call_args});\n"
            + f"    if (module._{metadata.error_functions['last_error_kind']}() !== 0) "
            + f"throw _lastError(module, '{error_name} failed');\n"
        )
    else:
        call_block = (
            f"    const ok = module._{function.c_name}({call_args});\n"
            + f"    if (!ok) throw _lastError(module, '{error_name} failed');\n"
        )

    return (
        f"function invoke_{function.c_name}({', '.join(signature_names)}) {{\n"
        f"    module._{metadata.error_functions['clear_error']}();\n"
        "    let outResultPtr = 0;\n"
        + ("    let outSizePtr = 0;\n" if size_alloc else "")
        + "    let outResultNeedsDestroy = false;\n"
        "    try {\n"
        + ("\n".join(marshalling_lines) + ("\n" if marshalling_lines else ""))
        + out_alloc
        + size_alloc
        + call_block
        + size_call
        + ("    outResultNeedsDestroy = true;\n" if destroy_line else "")
        + return_statement
        + "    } finally {\n"
        + (
            f"        if (outResultNeedsDestroy && outResultPtr) module._{destroy_function}(outResultPtr);\n"
            if destroy_line
            else ""
        )
        + cleanup_block
        + size_free
        + "    }\n"
        + "}"
    )


def _render_module_factory(metadata: BindingABI) -> str:
    members: list[str] = []
    module_members: dict[str, list[str]] = {}
    for handle in sorted(metadata.handles.values(), key=lambda item: item.c_type):
        type_name = _type_name(handle.c_type)
        members.append(f"        {type_name},")
    for function in sorted(metadata.functions.values(), key=lambda item: item.c_name):
        if function.receiver is not None:
            continue
        if function.c_name in _INTERNAL_C_FUNCTIONS:
            continue
        name = _public_name(function, metadata.c_prefix)
        param_names = [param.name for param in _public_params(function)]
        if _typed_buffer_element(function, metadata) is not None:
            param_names.append("arrayType")
        params = ", ".join(param_names)
        call = f"({params}) => invoke_{function.c_name}(module{', ' if params else ''}{params})"
        module_members_for_function = _public_module_members(
            function, metadata.c_prefix
        )
        if module_members_for_function:
            for module_name, member_name in module_members_for_function:
                module_members.setdefault(module_name, []).append(
                    f"            {member_name}: {call},"
                )
        else:
            members.append(f"        {name}: {call},")
    if "ifcopenshell_parse_open" in metadata.functions:
        module_members.setdefault("parse", []).append("            openBytes,")
    for module_name, nested_members in sorted(module_members.items()):
        members.append(
            f"        {module_name}: Object.freeze({{\n"
            + "\n".join(nested_members)
            + "\n        }),"
        )
    joined = "\n".join(members)
    return (
        "export async function createIfcOpenshellModule(initModule, wasmUrl, options = {}) {\n"
        "    const module = await initModule({\n"
        "        locateFile(path) {\n"
        "            if (path.endsWith('.wasm') && wasmUrl) return wasmUrl;\n"
        "            return path;\n"
        "        },\n"
        "    });\n"
        "\n"
        "    const pluginBaseUrl = options.pluginBaseUrl ?? new URL('.', import.meta.url).href;\n"
        "    const pluginManifest = options.pluginManifest ?? {};\n"
        "    const pluginLoader = options.pluginLoader ?? defaultPluginLoader;\n"
        "    const loadedPlugins = new Set();\n"
        "    const loadingPlugins = new Map();\n"
        "\n"
        "    function pluginKey(kind, id) {\n"
        "        return `${kind}:${id}`;\n"
        "    }\n"
        "\n"
        "    function pluginEntry(kind, id) {\n"
        "        return pluginManifest?.[kind]?.[id] ?? null;\n"
        "    }\n"
        "\n"
        "    function pluginDependencies(kind, id) {\n"
        "        const entry = pluginEntry(kind, id);\n"
        "        if (!entry) return [];\n"
        "        return Array.isArray(entry.depends) ? entry.depends : [];\n"
        "    }\n"
        "\n"
        "    function pluginUrl(entry) {\n"
        "        return new URL(entry.wasm, pluginBaseUrl).href;\n"
        "    }\n"
        "\n"
        "    async function defaultPluginLoader(url) {\n"
        "        const response = await fetch(url);\n"
        "        if (!response.ok) {\n"
        "            throw new Error(`Failed to fetch WASM plugin ${url}: ${response.status}`);\n"
        "        }\n"
        "        return new Uint8Array(await response.arrayBuffer());\n"
        "    }\n"
        "\n"
        "    async function loadPluginLibrary(kind, id, entry) {\n"
        "        const url = pluginUrl(entry);\n"
        "        const bytes = normalizeVirtualFileBytes(await pluginLoader(url, { kind, id, entry }));\n"
        "        const path = virtualFilePath(entry.wasm);\n"
        "        module.FS.writeFile(path, bytes);\n"
        "        try {\n"
        "            module.loadDynamicLibrary(path, { global: true, allowUndefined: true });\n"
        "        } finally {\n"
        "            module.FS.unlink(path);\n"
        "        }\n"
        "    }\n"
        "\n"
        "    async function loadPlugin(kind, id, dependencyPath = []) {\n"
        "        const key = pluginKey(kind, id);\n"
        "        if (dependencyPath.includes(key)) {\n"
        "            throw new Error(`Cyclic WASM plugin dependency: ${[...dependencyPath, key].join(' -> ')}`);\n"
        "        }\n"
        "        if (loadedPlugins.has(key)) return;\n"
        "        if (loadingPlugins.has(key)) {\n"
        "            return loadingPlugins.get(key);\n"
        "        }\n"
        "        const promise = (async () => {\n"
        "            for (const dependency of pluginDependencies(kind, id)) {\n"
        "                const separator = dependency.indexOf(':');\n"
        "                if (separator <= 0 || separator === dependency.length - 1) {\n"
        "                    throw new Error(`Invalid WASM plugin dependency ${dependency} for ${key}`);\n"
        "                }\n"
        "                await loadPlugin(dependency.slice(0, separator), dependency.slice(separator + 1), [...dependencyPath, key]);\n"
        "            }\n"
        "            if (kind === 'schema') {\n"
        "                const entry = pluginEntry('schema', id);\n"
        "                if (!entry?.wasm) {\n"
        "                    throw new Error(`Unknown WASM schema plugin ${id}`);\n"
        "                }\n"
        "                await loadPluginLibrary(kind, id, entry);\n"
        "                const schema = invoke_ifcopenshell_parse_schema_by_name(module, id.toUpperCase());\n"
        "                if (schema) schema.destroy();\n"
        "                loadedPlugins.add(key);\n"
        "                return;\n"
        "            }\n"
        "            const entry = pluginEntry(kind, id);\n"
        "            if (!entry?.wasm) {\n"
        "                throw new Error(`Unknown WASM plugin ${kind}/${id}`);\n"
        "            }\n"
        "            await loadPluginLibrary(kind, id, entry);\n"
        "            if (!invoke_ifcopenshell_geom_plugin_load(module, kind, id)) {\n"
        "                throw new Error(`Plugin ${kind}/${id} loaded but failed to register`);\n"
        "            }\n"
        "            if (!pluginIsLoaded(kind, id)) {\n"
        "                throw new Error(`Plugin ${kind}/${id} loaded but failed to register`);\n"
        "            }\n"
        "            loadedPlugins.add(key);\n"
        "        })();\n"
        "        loadingPlugins.set(key, promise);\n"
        "        try {\n"
        "            await promise;\n"
        "        } finally {\n"
        "            loadingPlugins.delete(key);\n"
        "        }\n"
        "    }\n"
        "\n"
        "    function pluginIsLoaded(kind, id) {\n"
        "        return invoke_ifcopenshell_geom_plugin_is_loaded(module, kind, id);\n"
        "    }\n"
        "\n"
        "    let nextVirtualFileId = 0;\n"
        "\n"
        "    function normalizeVirtualFileBytes(bytes) {\n"
        "        if (bytes instanceof Uint8Array) return bytes;\n"
        "        if (ArrayBuffer.isView(bytes)) {\n"
        "            return new Uint8Array(bytes.buffer, bytes.byteOffset, bytes.byteLength);\n"
        "        }\n"
        "        if (bytes instanceof ArrayBuffer) return new Uint8Array(bytes);\n"
        "        throw new TypeError('Expected IFC input as Uint8Array, ArrayBuffer, or ArrayBufferView');\n"
        "    }\n"
        "\n"
        "    function virtualFilePath(filename) {\n"
        "        const basename = String(filename || 'model.ifc').split(/[\\\\/]/).pop() || 'model.ifc';\n"
        "        const safeName = basename.replace(/[^A-Za-z0-9._-]/g, '_');\n"
        "        nextVirtualFileId += 1;\n"
        "        return `/ifcopenshell-${nextVirtualFileId}-${safeName}`;\n"
        "    }\n"
        "\n"
        "    function openBytes(bytes, filename = 'model.ifc', readonly = false) {\n"
        "        const path = virtualFilePath(filename);\n"
        "        module.FS.writeFile(path, normalizeVirtualFileBytes(bytes));\n"
        "        try {\n"
        "            return invoke_ifcopenshell_parse_open(module, path, readonly);\n"
        "        } finally {\n"
        "            module.FS.unlink(path);\n"
        "        }\n"
        "    }\n"
        "\n"
        "    return Object.freeze({\n" + joined + "\n"
        "        loadPlugin,\n"
        "        loadedPlugins: () => Array.from(loadedPlugins),\n"
        "    });\n"
        "}"
    )


def _render_value_type_metadata(metadata: BindingABI) -> str:
    payload = {
        value.c_type: {
            "cType": value.c_type,
            "kind": value.kind,
            "destroyFunction": value.destroy_function,
            "elementType": value.element_type,
            "sequenceDepth": value.sequence_depth,
            "bufferMode": (
                "snapshot" if value.kind in {"string", "sequence"} else None
            ),
            "fields": [
                {"name": field.name, "cType": field.c_type} for field in value.fields
            ],
        }
        for value in sorted(metadata.value_types.values(), key=lambda item: item.c_type)
    }
    return json.dumps(payload, indent=4, sort_keys=True)


def _render_option_type_metadata(metadata: BindingABI) -> str:
    payload = {}
    for option in sorted(
        metadata.option_structs.values(), key=lambda item: item.c_type
    ):
        fields = []
        option_fields = []
        for field in option.fields:
            field_payload = {
                "name": field.name,
                "cType": field.c_type,
                "typeKind": field.type.kind,
                "sequenceDepth": field.type.sequence_depth,
                "nullable": field.type.nullable,
            }
            if enum_values := _enum_value_map(field.type):
                field_payload["enumValues"] = enum_values
            fields.append({"name": field.name, "cType": field.c_type})
            option_fields.append(field_payload)
            if field.type.nullable:
                fields.append({"name": f"has_{field.name}", "cType": "bool"})
                field_payload["hasField"] = f"has_{field.name}"
        payload[option.c_type] = {
            "cType": option.c_type,
            "kind": "option",
            "fields": fields,
            "optionFields": option_fields,
        }
    return json.dumps(payload, indent=4, sort_keys=True)


def _render_error_object(name: str, entries: tuple[ErrorCatalogEntryIR, ...]) -> str:
    values = "\n".join(f"    {entry.name}: {entry.value}," for entry in entries)
    return f"export const {name} = Object.freeze({{\n{values}\n}});"


def render_js_glue(
    metadata: BindingABI, handles: dict[str, CTypeIR] | None = None
) -> str:
    del handles
    wrappers = "\n\n".join(
        _render_wrapper(function, metadata)
        for function in sorted(
            metadata.functions.values(), key=lambda item: item.c_name
        )
    )
    classes = _render_handle_classes(metadata)
    handle_switch = _render_handle_wrapper_switch(metadata)
    factory = _render_module_factory(metadata)
    value_types = _render_value_type_metadata(metadata)
    option_types = _render_option_type_metadata(metadata)
    error_kinds = _render_error_object(
        "IfcOpenShellErrorKind", metadata.error_catalog.kinds
    )
    error_codes = _render_error_object(
        "IfcOpenShellErrorCode", metadata.error_catalog.codes
    )
    return "\n".join(
        [
            "",
            "const _IFCOPENSHELL_ERROR_BRAND = Symbol.for('org.ifcopenshell.error');",
            "",
            error_kinds,
            "",
            error_codes,
            "",
            "/** Typed cross-target error. Inspect kind/code; never parse message. */",
            "export class IfcOpenShellError extends Error {",
            "    constructor(kindOrMessage, codeOrCause, message, cause) {",
            "        let kind;",
            "        let code;",
            "        if (typeof kindOrMessage === 'string') {",
            "            message = kindOrMessage;",
            "            cause = codeOrCause;",
            "            if (cause instanceof IfcOpenShellError) {",
            "                kind = cause.kind;",
            "                code = cause.code;",
            "            } else {",
            "                kind = IfcOpenShellErrorKind.RUNTIME;",
            "                code = IfcOpenShellErrorCode.UNSPECIFIED;",
            "            }",
            "        } else {",
            "            kind = kindOrMessage;",
            "            code = codeOrCause;",
            "        }",
            "        super(message, cause !== undefined ? { cause } : undefined);",
            "        this.name = kind === IfcOpenShellErrorKind.CANCELLED ? 'AbortError' : 'IfcOpenShellError';",
            "        this.kind = kind;",
            "        this.code = code;",
            "        Object.defineProperty(this, _IFCOPENSHELL_ERROR_BRAND, { value: true });",
            "    }",
            "    static [Symbol.hasInstance](value) {",
            "        return Boolean(value && value[_IFCOPENSHELL_ERROR_BRAND] === true);",
            "    }",
            "}",
            "",
            "export function abortError(message = 'IfcOpenShell operation was cancelled', cause) {",
            "    return new IfcOpenShellError(IfcOpenShellErrorKind.CANCELLED, IfcOpenShellErrorCode.OPERATION_CANCELLED, message, cause);",
            "}",
            "",
            "export function isIfcOpenShellAbortError(error) {",
            "    return error instanceof IfcOpenShellError && error.code === IfcOpenShellErrorCode.OPERATION_CANCELLED;",
            "}",
            "",
            "const POINTER_SIZE = 4;",
            f"const _VALUE_TYPES = {value_types};",
            f"const _OPTION_TYPES = {option_types};",
            "const _STRUCT_LAYOUT_CACHE = new Map();",
            "",
            "function _normalizeCType(cType) {",
            "    return cType.replace(/\\s+\\*/g, '*').replace(/\\s+/g, ' ').trim();",
            "}",
            "",
            "function _alignTo(offset, alignment) {",
            "    const remainder = offset % alignment;",
            "    return remainder === 0 ? offset : offset + alignment - remainder;",
            "}",
            "",
            "function _readInt64(module, ptr) {",
            "    const index = ptr >> 2;",
            "    const low = module.HEAP32[index];",
            "    const high = module.HEAP32[index + 1];",
            "    return (BigInt(high) << 32n) | BigInt(low >>> 0);",
            "}",
            "",
            "function _writeInt64(module, ptr, value) {",
            "    const normalized = BigInt(value);",
            "    const index = ptr >> 2;",
            "    module.HEAP32[index] = Number(BigInt.asIntN(32, normalized));",
            "    module.HEAP32[index + 1] = Number(BigInt.asIntN(32, normalized >> 32n));",
            "}",
            "",
            "function _enumInputValue(value, values, name) {",
            "    if (typeof value !== 'string' || !Object.prototype.hasOwnProperty.call(values, value)) {",
            "        throw new TypeError(`Invalid literal for ${name}: ${String(value)}`);",
            "    }",
            "    return values[value];",
            "}",
            "",
            "function _mapEnumInput(value, values, depth, name) {",
            "    if (depth === 0) return _enumInputValue(value, values, name);",
            "    if (!Array.isArray(value)) throw new TypeError(`Expected ${name} to be an array.`);",
            "    return value.map((item) => _mapEnumInput(item, values, depth - 1, name));",
            "}",
            "",
            "function _enumOutputValue(value, names, name) {",
            "    const key = String(value);",
            "    if (!Object.prototype.hasOwnProperty.call(names, key)) {",
            "        throw new TypeError(`Native ${name} returned unsupported enum value ${value}.`);",
            "    }",
            "    return names[key];",
            "}",
            "",
            "function _mapEnumOutput(value, names, depth, name) {",
            "    if (depth === 0) return _enumOutputValue(value, names, name);",
            "    if (!Array.isArray(value)) throw new TypeError(`Expected native ${name} to be an array.`);",
            "    return value.map((item) => _mapEnumOutput(item, names, depth - 1, name));",
            "}",
            "",
            "function _nativeTypeInfo(cType) {",
            "    const normalized = _normalizeCType(cType);",
            "    if (normalized.endsWith('*')) return { size: POINTER_SIZE, align: POINTER_SIZE, getter: '*' };",
            "    switch (normalized) {",
            "        case 'bool':",
            "        case 'uint8_t': return { size: 1, align: 1, getter: 'i8' };",
            "        case 'ifcopenshell_logical_t':",
            "        case 'int32_t':",
            "        case 'uint32_t':",
            "        case 'size_t': return { size: 4, align: 4, getter: 'i32' };",
            "        case 'double': return { size: 8, align: 8, getter: 'double' };",
            "        case 'int64_t': return { size: 8, align: 8, getter: 'i64' };",
            "        default: {",
            "            const valueType = _VALUE_TYPES[normalized];",
            "            const optionType = _OPTION_TYPES[normalized];",
            "            const structType = valueType || optionType;",
            "            if (!structType) return { size: POINTER_SIZE, align: POINTER_SIZE, getter: '*' };",
            "            const layout = _getStructLayout(structType);",
            "            return { size: layout.size, align: layout.align, getter: 'struct', valueType: structType };",
            "        }",
            "    }",
            "}",
            "",
            "function _getStructLayout(structMetadata) {",
            "    const cached = _STRUCT_LAYOUT_CACHE.get(structMetadata.cType);",
            "    if (cached) return cached;",
            "    let offset = 0;",
            "    let align = 1;",
            "    const fields = structMetadata.fields.map((field) => {",
            "        const info = _nativeTypeInfo(field.cType);",
            "        offset = _alignTo(offset, info.align);",
            "        const result = { ...field, offset, info };",
            "        offset += info.size;",
            "        align = Math.max(align, info.align);",
            "        return result;",
            "    });",
            "    const layout = { size: _alignTo(offset, align), align, fields };",
            "    _STRUCT_LAYOUT_CACHE.set(structMetadata.cType, layout);",
            "    return layout;",
            "}",
            "",
            "function _allocString(module, value) {",
            "    const size = module.lengthBytesUTF8(value) + 1;",
            "    const ptr = module._malloc(size);",
            "    module.stringToUTF8(value, ptr, size);",
            "    return ptr;",
            "}",
            "",
            "function _lastError(module, fallbackMessage) {",
            f"    const errorPtr = module._{metadata.error_functions['last_error_message']}();",
            f"    const kind = module._{metadata.error_functions['last_error_kind']}();",
            f"    const code = module._{metadata.error_functions['last_error_code']}();",
            "    const message = errorPtr ? module.UTF8ToString(errorPtr) : fallbackMessage;",
            "    return new IfcOpenShellError(kind || IfcOpenShellErrorKind.RUNTIME, code || IfcOpenShellErrorCode.UNSPECIFIED, message);",
            "}",
            "",
            "function _getValue(module, ptr, cType) {",
            "    const info = _nativeTypeInfo(cType);",
            "    if (info.getter === 'i64') return _readInt64(module, ptr);",
            "    if (info.getter === 'struct') return _readValueType(module, ptr, info.valueType);",
            "    return module.getValue(ptr, info.getter);",
            "}",
            "",
            "function _setValue(module, ptr, cType, value) {",
            "    const info = _nativeTypeInfo(cType);",
            "    if (info.getter === 'i64') {",
            "        _writeInt64(module, ptr, value);",
            "        return;",
            "    }",
            "    if (info.getter === 'i8') {",
            "        module.setValue(ptr, value ? 1 : 0, 'i8');",
            "        return;",
            "    }",
            "    module.setValue(ptr, value, info.getter);",
            "}",
            "",
            handle_switch,
            "",
            "function _readStringValue(module, ptr) {",
            "    const layout = _getStructLayout(_VALUE_TYPES['ifcopenshell_string_t']);",
            "    const dataField = layout.fields.find((field) => field.name === 'data');",
            "    const dataPtr = module.getValue(ptr + dataField.offset, '*');",
            "    return dataPtr ? module.UTF8ToString(dataPtr) : null;",
            "}",
            "",
            "function _numericArrayType(cType) {",
            "    switch (_normalizeCType(cType)) {",
            "        case 'double': return Float64Array;",
            "        case 'int32_t': return Int32Array;",
            "        case 'uint32_t': return Uint32Array;",
            "        case 'uint8_t': return Uint8Array;",
            "        default: throw new TypeError(`Unsupported numeric buffer element type ${cType}`);",
            "    }",
            "}",
            "",
            "const _NUMERIC_ARRAY_TYPES = new Set([",
            "    Int8Array, Uint8Array, Uint8ClampedArray, Int16Array, Uint16Array,",
            "    Int32Array, Uint32Array, Float32Array, Float64Array,",
            "]);",
            "",
            "function _copyNumericBuffer(module, ptr, size, cType, arrayType = null) {",
            "    if (!Number.isSafeInteger(size) || size < 0) {",
            "        throw new RangeError(`Invalid numeric buffer size ${size}`);",
            "    }",
            "    const NativeArray = _numericArrayType(cType);",
            "    const TargetArray = arrayType ?? NativeArray;",
            "    if (!_NUMERIC_ARRAY_TYPES.has(TargetArray)) {",
            "        throw new TypeError('Expected a numeric typed-array constructor');",
            "    }",
            "    if (size !== 0 && !ptr) throw new Error('Numeric buffer returned a null pointer with a non-zero size');",
            "    const memory = module.HEAPU32.buffer;",
            "    const byteLength = size * NativeArray.BYTES_PER_ELEMENT;",
            "    if (!Number.isSafeInteger(byteLength) || ptr < 0 || ptr + byteLength > memory.byteLength) {",
            "        throw new RangeError('Numeric buffer lies outside WASM memory');",
            "    }",
            "    if (ptr % NativeArray.BYTES_PER_ELEMENT !== 0) {",
            "        throw new RangeError('Numeric buffer pointer is misaligned');",
            "    }",
            "    const source = new NativeArray(memory, size === 0 ? 0 : ptr, size);",
            "    const result = new TargetArray(source);",
            "    if (module.HEAPU32.buffer !== memory) {",
            "        throw new Error('WASM memory grew during numeric buffer snapshot');",
            "    }",
            "    return result;",
            "}",
            "",
            "function _readSequenceValue(module, ptr, metadata, typedSnapshot = false, arrayType = null) {",
            "    const layout = _getStructLayout(metadata);",
            "    const itemsField = layout.fields.find((field) => field.name === 'items');",
            "    const sizeField = layout.fields.find((field) => field.name === 'size');",
            "    const itemsPtr = module.getValue(ptr + itemsField.offset, '*');",
            "    const size = module.getValue(ptr + sizeField.offset, 'i32') >>> 0;",
            "    if (typedSnapshot) return _copyNumericBuffer(module, itemsPtr, size, metadata.elementType, arrayType);",
            "    if (!itemsPtr || size === 0) return [];",
            "    const elementType = metadata.elementType;",
            "    if (!elementType) return [];",
            "    const elementInfo = _nativeTypeInfo(elementType);",
            "    const result = [];",
            "    for (let index = 0; index < size; index += 1) {",
            "        const elementPtr = itemsPtr + index * elementInfo.size;",
            "        if (elementInfo.getter === 'struct') {",
            "            result.push(_readValueType(module, elementPtr, elementInfo.valueType));",
            "        } else if (elementType in _VALUE_TYPES) {",
            "            result.push(_readValueType(module, elementPtr, _VALUE_TYPES[elementType]));",
            "        } else if (_HANDLE_C_TYPES.has(_normalizeCType(elementType))) {",
            "            const handle = _wrapHandleByType(module, elementType, module.getValue(elementPtr, '*'), true);",
            "            module.setValue(elementPtr, 0, '*');",
            "            result.push(handle);",
            "        } else {",
            "            const value = _getValue(module, elementPtr, elementType);",
            "            result.push(_normalizeCType(elementType) === 'bool' ? value !== 0 : value);",
            "        }",
            "    }",
            "    return result;",
            "}",
            "",
            "function _readStructValue(module, ptr, metadata) {",
            "    const layout = _getStructLayout(metadata);",
            "    const result = {};",
            "    for (const field of layout.fields) {",
            "        const fieldPtr = ptr + field.offset;",
            "        if (field.info.getter === 'struct') {",
            "            result[field.name] = _readValueType(module, fieldPtr, field.info.valueType);",
            "        } else if (_HANDLE_C_TYPES.has(_pointedCType(field.cType))) {",
            "            result[field.name] = _wrapHandleByType(module, _pointedCType(field.cType), module.getValue(fieldPtr, '*'), true);",
            "            module.setValue(fieldPtr, 0, '*');",
            "        } else {",
            "            const value = _getValue(module, fieldPtr, field.cType);",
            "            result[field.name] = _normalizeCType(field.cType) === 'bool' ? value !== 0 : value;",
            "        }",
            "    }",
            "    return result;",
            "}",
            "",
            "function _readOptionalResultStruct(module, ptr, metadata) {",
            "    const layout = _getStructLayout(metadata);",
            "    const hasField = layout.fields.find((field) => field.name === 'has_value');",
            "    const valueField = layout.fields.find((field) => field.name === 'value');",
            "    const hasValue = module.getValue(ptr + hasField.offset, 'i8') !== 0;",
            "    if (!hasValue) return null;",
            "    return _readValueType(module, ptr + valueField.offset, valueField.info.valueType);",
            "}",
            "",
            "function _readVariantValue(module, ptr, metadata) {",
            "    const layout = _getStructLayout(metadata);",
            "    const kindField = layout.fields.find((field) => field.name === 'kind');",
            "    const kind = module.getValue(ptr + kindField.offset, 'i32');",
            "    const valueField = layout.fields.find((field) => field.name === `value_${kind}`);",
            "    if (!valueField) throw new Error(`Unsupported variant alternative ${kind} for ${metadata.cType}`);",
            "    const fieldPtr = ptr + valueField.offset;",
            "    if (_HANDLE_C_TYPES.has(_pointedCType(valueField.cType))) {",
            "        const handlePtr = module.getValue(fieldPtr, '*');",
            "        const result = _wrapHandleByType(module, _pointedCType(valueField.cType), handlePtr, true);",
            "        module.setValue(fieldPtr, 0, '*');",
            "        return result;",
            "    }",
            "    if (valueField.info.getter === 'struct') return _readValueType(module, fieldPtr, valueField.info.valueType);",
            "    const value = _getValue(module, fieldPtr, valueField.cType);",
            "    return _normalizeCType(valueField.cType) === 'bool' ? value !== 0 : value;",
            "}",
            "",
            "function _readValueType(module, ptr, metadata, typedSnapshot = false, arrayType = null) {",
            "    switch (metadata.kind) {",
            "        case 'string': return _readStringValue(module, ptr);",
            "        case 'sequence':",
            "        case 'handle_sequence':",
            "        case 'result_record_sequence': return _readSequenceValue(module, ptr, metadata, typedSnapshot, arrayType);",
            "        case 'result_struct': return _readStructValue(module, ptr, metadata);",
            "        case 'optional_result_struct': return _readOptionalResultStruct(module, ptr, metadata);",
            "        case 'variant': return _readVariantValue(module, ptr, metadata);",
            "        default: return _readStructValue(module, ptr, metadata);",
            "    }",
            "}",
            "",
            "function _pointedCType(cType) {",
            "    return _normalizeCType(cType).replace(/^const /, '').replace(/\\*$/, '').trim();",
            "}",
            "",
            "function _valueTypeForCType(cType) {",
            "    const normalized = _pointedCType(cType);",
            "    return _VALUE_TYPES[normalized] || null;",
            "}",
            "",
            "function _optionTypeForCType(cType) {",
            "    const normalized = _pointedCType(cType);",
            "    return _OPTION_TYPES[normalized] || null;",
            "}",
            "",
            "function _hasOwnValue(value, name) {",
            "    return Object.prototype.hasOwnProperty.call(value, name) && value[name] != null;",
            "}",
            "",
            "function _allocInputStringList(module, value) {",
            "    if (!Array.isArray(value)) throw new Error('Expected a string array.');",
            "    const listMetadata = _VALUE_TYPES['ifcopenshell_string_list_t'];",
            "    const stringMetadata = _VALUE_TYPES['ifcopenshell_string_t'];",
            "    const listLayout = _getStructLayout(listMetadata);",
            "    const stringLayout = _getStructLayout(stringMetadata);",
            "    const itemsField = listLayout.fields.find((field) => field.name === 'items');",
            "    const sizeField = listLayout.fields.find((field) => field.name === 'size');",
            "    const dataField = stringLayout.fields.find((field) => field.name === 'data');",
            "    const stringSizeField = stringLayout.fields.find((field) => field.name === 'size');",
            "    const ownedField = stringLayout.fields.find((field) => field.name === 'owned');",
            "    const structPtr = module._malloc(listLayout.size);",
            "    const itemsPtr = value.length ? module._malloc(stringLayout.size * value.length) : 0;",
            "    const dataPtrs = [];",
            "    try {",
            "        _zeroMemory(module, structPtr, listLayout.size);",
            "        if (itemsPtr) _zeroMemory(module, itemsPtr, stringLayout.size * value.length);",
            "        for (let index = 0; index < value.length; index += 1) {",
            "            const itemPtr = itemsPtr + index * stringLayout.size;",
            "            const dataPtr = _allocString(module, value[index]);",
            "            dataPtrs.push(dataPtr);",
            "            module.setValue(itemPtr + dataField.offset, dataPtr, '*');",
            "            module.setValue(itemPtr + stringSizeField.offset, module.lengthBytesUTF8(value[index]), 'i32');",
            "            module.setValue(itemPtr + ownedField.offset, 1, 'i8');",
            "        }",
            "        module.setValue(structPtr + itemsField.offset, itemsPtr, '*');",
            "        module.setValue(structPtr + sizeField.offset, value.length, 'i32');",
            "        return structPtr;",
            "    } catch (error) {",
            "        for (const dataPtr of dataPtrs) module._free(dataPtr);",
            "        if (itemsPtr) module._free(itemsPtr);",
            "        module._free(structPtr);",
            "        throw error;",
            "    }",
            "}",
            "",
            "function _freeInputStringList(module, ptr) {",
            "    if (!ptr) return;",
            "    const listMetadata = _VALUE_TYPES['ifcopenshell_string_list_t'];",
            "    const stringMetadata = _VALUE_TYPES['ifcopenshell_string_t'];",
            "    const listLayout = _getStructLayout(listMetadata);",
            "    const stringLayout = _getStructLayout(stringMetadata);",
            "    const itemsField = listLayout.fields.find((field) => field.name === 'items');",
            "    const sizeField = listLayout.fields.find((field) => field.name === 'size');",
            "    const dataField = stringLayout.fields.find((field) => field.name === 'data');",
            "    const itemsPtr = module.getValue(ptr + itemsField.offset, '*');",
            "    const count = module.getValue(ptr + sizeField.offset, 'i32');",
            "    if (itemsPtr) {",
            "        for (let index = 0; index < count; index += 1) {",
            "            const itemPtr = itemsPtr + index * stringLayout.size;",
            "            const dataPtr = module.getValue(itemPtr + dataField.offset, '*');",
            "            if (dataPtr) module._free(dataPtr);",
            "        }",
            "        module._free(itemsPtr);",
            "    }",
            "    module._free(ptr);",
            "}",
            "",
            "function _allocInputHandleSequence(module, value, cType) {",
            "    if (!Array.isArray(value)) throw new Error(`Expected a handle array for ${cType}.`);",
            "    const metadata = _valueTypeForCType(cType);",
            "    if (!metadata || metadata.kind !== 'handle_sequence') {",
            "        throw new Error(`Handle sequence marshalling for ${cType} is not implemented.`);",
            "    }",
            "    const layout = _getStructLayout(metadata);",
            "    const itemsField = layout.fields.find((field) => field.name === 'items');",
            "    const sizeField = layout.fields.find((field) => field.name === 'size');",
            "    const structPtr = module._malloc(layout.size);",
            "    const itemsPtr = value.length ? module._malloc(POINTER_SIZE * value.length) : 0;",
            "    try {",
            "        for (let index = 0; index < value.length; index += 1) {",
            "            const item = value[index];",
            "            module.setValue(itemsPtr + index * POINTER_SIZE, item == null ? 0 : item.ptr, '*');",
            "        }",
            "        module.setValue(structPtr + itemsField.offset, itemsPtr, '*');",
            "        module.setValue(structPtr + sizeField.offset, value.length, 'i32');",
            "        return structPtr;",
            "    } catch (error) {",
            "        if (itemsPtr) module._free(itemsPtr);",
            "        module._free(structPtr);",
            "        throw error;",
            "    }",
            "}",
            "",
            "function _freeInputHandleSequence(module, ptr, cType) {",
            "    const metadata = _valueTypeForCType(cType);",
            "    if (!metadata) {",
            "        module._free(ptr);",
            "        return;",
            "    }",
            "    const layout = _getStructLayout(metadata);",
            "    const itemsField = layout.fields.find((field) => field.name === 'items');",
            "    const itemsPtr = module.getValue(ptr + itemsField.offset, '*');",
            "    if (itemsPtr) module._free(itemsPtr);",
            "    module._free(ptr);",
            "}",
            "",
            "function _allocInputSequence(module, value, cType) {",
            "    if (!Array.isArray(value)) throw new Error(`Expected an array for ${cType}.`);",
            "    const metadata = _valueTypeForCType(cType);",
            "    if (!metadata || !['sequence', 'input_record_sequence', 'input_variant_sequence'].includes(metadata.kind)) {",
            "        throw new Error(`Sequence marshalling for ${cType} is not implemented.`);",
            "    }",
            "    const layout = _getStructLayout(metadata);",
            "    const structPtr = module._malloc(layout.size);",
            "    try {",
            "        _zeroMemory(module, structPtr, layout.size);",
            "        _writeInputSequence(module, structPtr, value, metadata);",
            "        return structPtr;",
            "    } catch (error) {",
            "        module._free(structPtr);",
            "        throw error;",
            "    }",
            "}",
            "",
            "function _writeInputSequence(module, structPtr, value, metadata) {",
            "    if (!Array.isArray(value)) throw new Error(`Expected an array for ${metadata.cType}.`);",
            "    const elementType = _normalizeCType(metadata.elementType || '');",
            "    const elementMetadata = _valueTypeForCType(elementType) || _optionTypeForCType(elementType);",
            "    const scalarElement = ['bool', 'ifcopenshell_logical_t', 'int32_t', 'uint32_t', 'size_t', 'double', 'int64_t', 'uint8_t'].includes(elementType);",
            "    if (!scalarElement && (!elementMetadata || !['sequence', 'option', 'variant'].includes(elementMetadata.kind))) {",
            "        throw new Error(`Sequence marshalling for ${metadata.cType} is not implemented.`);",
            "    }",
            "    const layout = _getStructLayout(metadata);",
            "    const itemsField = layout.fields.find((field) => field.name === 'items');",
            "    const sizeField = layout.fields.find((field) => field.name === 'size');",
            "    const elementInfo = scalarElement ? _nativeTypeInfo(elementType) : _getStructLayout(elementMetadata);",
            "    const itemsPtr = value.length ? module._malloc(elementInfo.size * value.length) : 0;",
            "    try {",
            "        if (itemsPtr) _zeroMemory(module, itemsPtr, elementInfo.size * value.length);",
            "        for (let index = 0; index < value.length; index += 1) {",
            "            const itemPtr = itemsPtr + index * elementInfo.size;",
            "            if (scalarElement) _setValue(module, itemPtr, elementType, value[index]);",
            "            else if (elementMetadata.kind === 'option') _writeInputOption(module, itemPtr, value[index], elementMetadata);",
            "            else if (elementMetadata.kind === 'variant') _writeInputVariant(module, itemPtr, value[index], elementMetadata);",
            "            else _writeInputSequence(module, itemPtr, value[index], elementMetadata);",
            "        }",
            "        module.setValue(structPtr + itemsField.offset, itemsPtr, '*');",
            "        module.setValue(structPtr + sizeField.offset, value.length, 'i32');",
            "    } catch (error) {",
            "        if (!scalarElement && itemsPtr) {",
            "            for (let index = 0; index < value.length; index += 1) {",
            "                if (elementMetadata.kind === 'option') _freeInputOptionFields(module, itemsPtr + index * elementInfo.size, elementMetadata);",
            "                else if (elementMetadata.kind === 'variant') _freeInputVariantFields(module, itemsPtr + index * elementInfo.size, elementMetadata);",
            "                else _freeInputSequenceItems(module, itemsPtr + index * elementInfo.size, elementMetadata);",
            "            }",
            "        }",
            "        if (itemsPtr) module._free(itemsPtr);",
            "        throw error;",
            "    }",
            "}",
            "",
            "function _freeInputSequence(module, ptr, cType) {",
            "    const metadata = _valueTypeForCType(cType);",
            "    if (!metadata) {",
            "        module._free(ptr);",
            "        return;",
            "    }",
            "    _freeInputSequenceItems(module, ptr, metadata);",
            "    module._free(ptr);",
            "}",
            "",
            "function _freeInputSequenceItems(module, ptr, metadata) {",
            "    const layout = _getStructLayout(metadata);",
            "    const itemsField = layout.fields.find((field) => field.name === 'items');",
            "    const sizeField = layout.fields.find((field) => field.name === 'size');",
            "    const itemsPtr = module.getValue(ptr + itemsField.offset, '*');",
            "    const count = module.getValue(ptr + sizeField.offset, 'i32');",
            "    const elementType = _normalizeCType(metadata.elementType || '');",
            "    const elementMetadata = _valueTypeForCType(elementType) || _optionTypeForCType(elementType);",
            "    if (itemsPtr && elementMetadata && ['sequence', 'option', 'variant'].includes(elementMetadata.kind)) {",
            "        const elementLayout = _getStructLayout(elementMetadata);",
            "        for (let index = 0; index < count; index += 1) {",
            "            if (elementMetadata.kind === 'option') _freeInputOptionFields(module, itemsPtr + index * elementLayout.size, elementMetadata);",
            "            else if (elementMetadata.kind === 'variant') _freeInputVariantFields(module, itemsPtr + index * elementLayout.size, elementMetadata);",
            "            else _freeInputSequenceItems(module, itemsPtr + index * elementLayout.size, elementMetadata);",
            "        }",
            "    }",
            "    if (itemsPtr) module._free(itemsPtr);",
            "}",
            "",
            "function _zeroMemory(module, ptr, size) {",
            "    const wordCount = Math.floor(size / 4);",
            "    if (wordCount > 0 && module.HEAPU32) {",
            "        const start = ptr >>> 2;",
            "        module.HEAPU32.fill(0, start, start + wordCount);",
            "    } else {",
            "        for (let offset = 0; offset < wordCount * 4; offset += 1) {",
            "            module.setValue(ptr + offset, 0, 'i8');",
            "        }",
            "    }",
            "    for (let offset = wordCount * 4; offset < size; offset += 1) {",
            "        module.setValue(ptr + offset, 0, 'i8');",
            "    }",
            "}",
            "",
            "function _allocInputOption(module, value, cType) {",
            "    if (value == null || typeof value !== 'object') throw new TypeError(`Expected an options object for ${cType}.`);",
            "    const metadata = _optionTypeForCType(cType);",
            "    if (!metadata) throw new Error(`Unknown options type ${cType}.`);",
            "    const layout = _getStructLayout(metadata);",
            "    const ptr = module._malloc(layout.size);",
            "    _zeroMemory(module, ptr, layout.size);",
            "    try {",
            "        _writeInputOption(module, ptr, value, metadata);",
            "        return ptr;",
            "    } catch (error) {",
            "        _freeInputOption(module, ptr, cType);",
            "        throw error;",
            "    }",
            "}",
            "",
            "function _writeInputOption(module, ptr, value, metadata) {",
            "        if (value == null || typeof value !== 'object') throw new TypeError(`Expected an options object for ${metadata.cType}.`);",
            "        const layout = _getStructLayout(metadata);",
            "        for (const optionField of metadata.optionFields) {",
            "            const field = layout.fields.find((candidate) => candidate.name === optionField.name);",
            "            const hasField = optionField.hasField ? layout.fields.find((candidate) => candidate.name === optionField.hasField) : null;",
            "            const hasValue = _hasOwnValue(value, optionField.name);",
            "            if (hasField) module.setValue(ptr + hasField.offset, hasValue ? 1 : 0, 'i8');",
            "            if (!hasValue) {",
            "                if (!optionField.nullable) throw new TypeError(`Missing required options field ${optionField.name}.`);",
            "                continue;",
            "            }",
            "            _writeInputOptionField(module, ptr + field.offset, optionField, value[optionField.name]);",
            "        }",
            "}",
            "",
            "function _writeInputOptionField(module, ptr, field, value) {",
            "    if (field.enumValues) value = field.sequenceDepth > 0",
            "        ? _mapEnumInput(value, field.enumValues, field.sequenceDepth, field.name)",
            "        : _enumInputValue(value, field.enumValues, field.name);",
            "    if (field.sequenceDepth > 0) {",
            "        const sequencePtr = field.typeKind === 'string'",
            "            ? _allocInputStringList(module, value)",
            "            : _allocInputSequence(module, value, field.cType);",
            "        module.setValue(ptr, sequencePtr, '*');",
            "        return;",
            "    }",
            "    if (field.typeKind === 'string') {",
            "        module.setValue(ptr, _allocString(module, value), '*');",
            "        return;",
            "    }",
            "    if (field.typeKind === 'handle') {",
            "        module.setValue(ptr, value == null ? 0 : value.ptr, '*');",
            "        return;",
            "    }",
            "    if (field.typeKind === 'option') {",
            "        module.setValue(ptr, _allocInputOption(module, value, field.cType), '*');",
            "        return;",
            "    }",
            "    if (field.typeKind === 'variant') {",
            "        module.setValue(ptr, _allocInputVariant(module, value, field.cType), '*');",
            "        return;",
            "    }",
            "    if (field.typeKind === 'bool' || field.typeKind === 'logical') {",
            "        _setValue(module, ptr, field.cType, value ? 1 : 0);",
            "        return;",
            "    }",
            "    _setValue(module, ptr, field.cType, value);",
            "}",
            "",
            "function _allocInputVariant(module, value, cType) {",
            "    const metadata = _valueTypeForCType(cType);",
            "    if (!metadata || metadata.kind !== 'variant') throw new Error(`Unknown input variant type ${cType}.`);",
            "    const layout = _getStructLayout(metadata);",
            "    const ptr = module._malloc(layout.size);",
            "    _zeroMemory(module, ptr, layout.size);",
            "    _writeInputVariant(module, ptr, value, metadata);",
            "    return ptr;",
            "}",
            "",
            "function _writeInputVariant(module, ptr, value, metadata) {",
            "    const layout = _getStructLayout(metadata);",
            "    const kind = value?.kind;",
            "    const kindField = layout.fields.find((field) => field.name === 'kind');",
            "    const valueField = layout.fields.find((field) => field.name === `value_${kind}`);",
            "    if (!Number.isInteger(kind) || !kindField || !valueField) throw new TypeError(`Invalid variant alternative for ${metadata.cType}.`);",
            "    module.setValue(ptr + kindField.offset, kind, 'i32');",
            "    const sequence = _valueTypeForCType(valueField.cType);",
            "    if (sequence && ['sequence', 'input_record_sequence', 'input_variant_sequence'].includes(sequence.kind)) {",
            "        _writeInputSequence(module, ptr + valueField.offset, value[`value_${kind}`], sequence);",
            "        return;",
            "    }",
            "    const option = _optionTypeForCType(valueField.cType);",
            "    if (!option) throw new Error(`Input variant alternative ${kind} is not an options record.`);",
            "    module.setValue(ptr + valueField.offset, _allocInputOption(module, value[`value_${kind}`], option.cType), '*');",
            "}",
            "",
            "function _freeInputVariant(module, ptr, cType) {",
            "    if (!ptr) return;",
            "    const metadata = _valueTypeForCType(cType);",
            "    if (metadata && metadata.kind === 'variant') _freeInputVariantFields(module, ptr, metadata);",
            "    module._free(ptr);",
            "}",
            "",
            "function _freeInputVariantFields(module, ptr, metadata) {",
            "    const layout = _getStructLayout(metadata);",
            "    const kindField = layout.fields.find((field) => field.name === 'kind');",
            "    const kind = kindField ? module.getValue(ptr + kindField.offset, 'i32') : -1;",
            "    const valueField = layout.fields.find((field) => field.name === `value_${kind}`);",
            "    const sequence = valueField ? _valueTypeForCType(valueField.cType) : null;",
            "    if (valueField && sequence && ['sequence', 'input_record_sequence', 'input_variant_sequence'].includes(sequence.kind)) {",
            "        _freeInputSequenceItems(module, ptr + valueField.offset, sequence);",
            "        return;",
            "    }",
            "    const option = valueField ? _optionTypeForCType(valueField.cType) : null;",
            "    const optionPtr = valueField ? module.getValue(ptr + valueField.offset, '*') : 0;",
            "    if (option && optionPtr) _freeInputOption(module, optionPtr, option.cType);",
            "}",
            "",
            "function _freeInputOption(module, ptr, cType) {",
            "    if (!ptr) return;",
            "    const metadata = _optionTypeForCType(cType);",
            "    if (!metadata) {",
            "        module._free(ptr);",
            "        return;",
            "    }",
            "    _freeInputOptionFields(module, ptr, metadata);",
            "    module._free(ptr);",
            "}",
            "",
            "function _freeInputOptionFields(module, ptr, metadata) {",
            "    const layout = _getStructLayout(metadata);",
            "    for (const optionField of metadata.optionFields) {",
            "        const field = layout.fields.find((candidate) => candidate.name === optionField.name);",
            "        const fieldPtr = module.getValue(ptr + field.offset, '*');",
            "        if (!fieldPtr) continue;",
            "        if (optionField.sequenceDepth > 0) {",
            "            if (optionField.typeKind === 'string') _freeInputStringList(module, fieldPtr);",
            "            else _freeInputSequence(module, fieldPtr, optionField.cType);",
            "        } else if (optionField.typeKind === 'string') {",
            "            module._free(fieldPtr);",
            "        } else if (optionField.typeKind === 'option') {",
            "            _freeInputOption(module, fieldPtr, optionField.cType);",
            "        } else if (optionField.typeKind === 'variant') {",
            "            _freeInputVariant(module, fieldPtr, optionField.cType);",
            "        }",
            "    }",
            "}",
            "",
            classes,
            "",
            wrappers,
            "",
            factory,
            "",
        ]
    )


__all__ = ["render_js_glue"]
