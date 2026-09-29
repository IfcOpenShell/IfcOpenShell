from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .conventions import (
    c_identifier_from_cpp_name,
    enum_adapter_target,
    handle_adapter_target,
    is_enum_adapter,
    is_handle_adapter,
    is_sequence_adapter,
    normalize_cpp_type,
    normalize_identifier,
    sequence_adapter_target,
)
from .model import CallableModel, ClassModel, EnumModel, ModuleModel, ParameterModel


def _class_index(model: ModuleModel) -> dict[str, ClassModel]:
    return {normalize_cpp_type(class_model.cpp_name): class_model for class_model in model.classes}


def _enum_index(model: ModuleModel) -> dict[str, EnumModel]:
    return {normalize_cpp_type(enum_model.cpp_name): enum_model for enum_model in model.enums}


def _class_c_type(class_model: ClassModel, model: ModuleModel) -> str:
    return f"{model.c_prefix}_{_class_c_identifier(class_model, model)}_t"


def _list_c_type(class_model: ClassModel, model: ModuleModel) -> str:
    return f"{model.c_prefix}_{_class_c_identifier(class_model, model)}_list_t"


def _class_c_identifier(class_model: ClassModel, model: ModuleModel) -> str:
    return c_identifier_from_cpp_name(class_model.cpp_name, model.c_prefix)


def _capsule_name_symbol(class_model: ClassModel) -> str:
    return f"{normalize_identifier(class_model.cpp_name).upper()}_CAPSULE_NAME"


def _capsule_destructor_name(class_model: ClassModel) -> str:
    return f"{normalize_identifier(class_model.cpp_name)}_capsule_destructor"


def _parameter_names(parameters: list[ParameterModel]) -> str:
    return "_".join(normalize_identifier(parameter.name) for parameter in parameters)


def _api_owner_identifier(owner: ClassModel) -> str:
    root_namespace = owner.cpp_name.split("::", 1)[0] if "::" in owner.cpp_name else None
    return c_identifier_from_cpp_name(owner.cpp_name, root_namespace)


@dataclass(slots=True)
class CallableVariant:
    owner: ClassModel
    callable: CallableModel
    api_name: str
    parameters: list[ParameterModel]


def _expand_variants(owner: ClassModel, callable_model: CallableModel) -> list[CallableVariant]:
    required = callable_model.minimum_arity
    variants: list[CallableVariant] = []
    for arity in range(required, len(callable_model.parameters) + 1):
        included = callable_model.parameters[:arity]
        api_name = f"{_api_owner_identifier(owner)}_{callable_model.c_name}"
        if callable_model.kind == "constructor":
            required_parameters = callable_model.parameters[:required]
            optional_parameters = callable_model.parameters[required:arity]
            if required_parameters:
                api_name += f"_with_{_parameter_names(required_parameters)}"
            if optional_parameters:
                api_name += f"_with_{_parameter_names(optional_parameters)}"
        elif required < len(callable_model.parameters):
            optional_parameters = callable_model.parameters[required:arity]
            if optional_parameters:
                api_name += f"_with_{_parameter_names(optional_parameters)}"
        variants.append(
            CallableVariant(
                owner=owner,
                callable=callable_model,
                api_name=api_name,
                parameters=included,
            )
        )
    return variants or [
        CallableVariant(
            owner=owner,
            callable=callable_model,
            api_name=f"{_api_owner_identifier(owner)}_{callable_model.c_name}",
            parameters=callable_model.parameters,
        )
    ]


def _all_variants(model: ModuleModel) -> list[CallableVariant]:
    variants: list[CallableVariant] = []
    for owner in model.classes:
        for callable_model in owner.callables:
            variants.extend(_expand_variants(owner, callable_model))
    return variants


def _full_variant(owner: ClassModel, callable_model: CallableModel) -> CallableVariant:
    return _expand_variants(owner, callable_model)[-1]


def _sequence_targets(model: ModuleModel) -> list[ClassModel]:
    class_models = _class_index(model)
    seen: set[str] = set()
    results: list[ClassModel] = []
    for owner in model.classes:
        for callable_model in owner.callables:
            if is_sequence_adapter(callable_model.return_adapter):
                target = sequence_adapter_target(callable_model.return_adapter)
                if target not in seen:
                    seen.add(target)
                    results.append(class_models[target])
    return results


def _enum_c_type(adapter: str, model: ModuleModel) -> str:
    enum_model = _enum_index(model).get(enum_adapter_target(adapter))
    if enum_model is None:
        raise RuntimeError(f"Unable to resolve enum adapter '{adapter}'")
    return enum_model.c_name


def _return_c_type(adapter: str, model: ModuleModel) -> str:
    if adapter == "string":
        return "char*"
    if adapter == "integer":
        return "int"
    if adapter == "bool":
        return "bool"
    if adapter == "void":
        return "void"
    if is_enum_adapter(adapter):
        return _enum_c_type(adapter, model)
    if is_handle_adapter(adapter):
        return f"{_class_c_type(_class_index(model)[handle_adapter_target(adapter)], model)}*"
    if is_sequence_adapter(adapter):
        return f"{_list_c_type(_class_index(model)[sequence_adapter_target(adapter)], model)}*"
    raise RuntimeError(f"Unsupported return adapter: {adapter}")


def _parameter_c_type(parameter: ParameterModel, model: ModuleModel) -> str:
    if parameter.adapter == "string":
        return "const char*"
    if parameter.adapter == "integer":
        return "int"
    if parameter.adapter == "bool":
        return "bool"
    if is_enum_adapter(parameter.adapter):
        return _enum_c_type(parameter.adapter, model)
    if is_handle_adapter(parameter.adapter):
        target = _class_index(model)[handle_adapter_target(parameter.adapter)]
        return f"{_class_c_type(target, model)}*"
    raise RuntimeError(f"Unsupported parameter adapter: {parameter.adapter}")


def _class_or_enum_cpp_name(adapter: str, model: ModuleModel) -> str:
    if is_handle_adapter(adapter):
        return _class_index(model)[handle_adapter_target(adapter)].cpp_name
    if is_enum_adapter(adapter):
        return _enum_index(model)[enum_adapter_target(adapter)].cpp_name
    raise RuntimeError(f"Adapter '{adapter}' does not resolve to a named C++ type")


def _cpp_argument(parameter: ParameterModel, model: ModuleModel) -> str:
    if parameter.adapter == "string":
        return f'std::string({parameter.name} ? {parameter.name} : "")'
    if is_enum_adapter(parameter.adapter):
        return f"static_cast<{_class_or_enum_cpp_name(parameter.adapter, model)}>({parameter.name})"
    if is_handle_adapter(parameter.adapter):
        target = _class_index(model)[handle_adapter_target(parameter.adapter)]
        actual_type = normalize_cpp_type(parameter.cpp_type)
        if actual_type.endswith("*"):
            if target.handle_kind == "shared_ptr":
                return f"{parameter.name}->value.get()"
            return f"&{parameter.name}->value"
        if target.handle_kind == "shared_ptr":
            return f"*{parameter.name}->value"
        return f"{parameter.name}->value"
    return parameter.name


def _call_expression(variant: CallableVariant, model: ModuleModel) -> str:
    arguments = ", ".join(_cpp_argument(parameter, model) for parameter in variant.parameters)
    if variant.callable.kind == "constructor":
        if variant.owner.handle_kind == "shared_ptr":
            return f"std::make_shared<{variant.owner.cpp_name}>({arguments})"
        return f"{variant.owner.cpp_name}({arguments})"
    access = "handle->value->" if variant.owner.handle_kind == "shared_ptr" else "handle->value."
    return f"{access}{variant.callable.cpp_name}({arguments})"


def _vector_inner_type(cpp_type: str) -> str | None:
    canonical = normalize_cpp_type(cpp_type)
    prefix = "std::vector<"
    if not canonical.startswith(prefix) or not canonical.endswith(">"):
        return None
    return canonical[len(prefix) : -1]


def _owner_expression(source: ClassModel, target: ClassModel) -> str:
    if target.owner_cpp_name is None:
        raise RuntimeError(f"Class '{target.cpp_name}' does not declare an owner relationship")
    if normalize_cpp_type(source.cpp_name) == normalize_cpp_type(target.owner_cpp_name):
        if source.handle_kind != "shared_ptr":
            raise RuntimeError(f"Owner class '{source.cpp_name}' must use shared_ptr handle storage")
        return "handle->value"
    if source.owner_cpp_name and normalize_cpp_type(source.owner_cpp_name) == normalize_cpp_type(target.owner_cpp_name):
        return "handle->owner"
    raise RuntimeError(
        f"Unable to propagate owner '{target.owner_cpp_name}' from '{source.cpp_name}' to '{target.cpp_name}'"
    )


def _emit_handle_return_lines(
    lines: list[str],
    source_owner: ClassModel,
    target: ClassModel,
    callable_model: CallableModel,
    call_expression: str,
    model: ModuleModel,
) -> None:
    normalized_return = normalize_cpp_type(callable_model.return_cpp_type)
    if normalized_return.endswith("*"):
        lines.append(f"        auto result_ptr = {call_expression};")
        lines.append("        if (result_ptr == nullptr) {")
        lines.append("            return nullptr;")
        lines.append("        }")
        lines.append("        auto result = *result_ptr;")
    else:
        lines.append(f"        auto result = {call_expression};")
    if target.handle_kind == "shared_ptr":
        lines.append(f"        auto wrapped_value = std::make_shared<{target.cpp_name}>(std::move(result));")
        lines.append(f"        return new {_class_c_type(target, model)}{{ std::move(wrapped_value) }};")
        return
    if target.owner_cpp_name is not None:
        owner_expression = "{}" if callable_model.kind == "constructor" else _owner_expression(source_owner, target)
        lines.append(f"        return new {_class_c_type(target, model)}{{ {owner_expression}, std::move(result) }};")
        return
    lines.append(f"        return new {_class_c_type(target, model)}{{ std::move(result) }};")


def _emit_sequence_return_lines(
    lines: list[str],
    source_owner: ClassModel,
    target: ClassModel,
    callable_model: CallableModel,
    call_expression: str,
    model: ModuleModel,
) -> None:
    vector_inner = _vector_inner_type(callable_model.return_cpp_type)
    if vector_inner is not None and vector_inner.endswith("*"):
        lines.append(f"        auto source_result = {call_expression};")
        lines.append(f"        std::vector<{target.cpp_name}> result;")
        lines.append("        result.reserve(source_result.size());")
        lines.append("        for (const auto* item : source_result) {")
        lines.append("            if (item != nullptr) {")
        lines.append("                result.push_back(*item);")
        lines.append("            }")
        lines.append("        }")
    else:
        lines.append(f"        auto result = {call_expression};")
    if target.owner_cpp_name is not None:
        owner_expression = _owner_expression(source_owner, target)
        lines.append(f"        return new {_list_c_type(target, model)}{{ {owner_expression}, std::move(result) }};")
        return
    lines.append(f"        return new {_list_c_type(target, model)}{{ std::move(result) }};")


def emit_c_api_header(model: ModuleModel) -> str:
    sequence_targets = _sequence_targets(model)
    lines = [
        "#ifndef IFCOPENSHELL_EXPERIMENTAL_C_API_H",
        "#define IFCOPENSHELL_EXPERIMENTAL_C_API_H",
        "",
        "#include <stdbool.h>",
        "#include <stddef.h>",
        "",
        "#ifdef __cplusplus",
        'extern "C" {',
        "#endif",
        "",
    ]
    for class_model in model.classes:
        lines.append(f"typedef struct {_class_c_type(class_model, model)} {_class_c_type(class_model, model)};")
    if model.classes:
        lines.append("")
    for class_model in sequence_targets:
        lines.append(f"typedef struct {_list_c_type(class_model, model)} {_list_c_type(class_model, model)};")
    if sequence_targets:
        lines.append("")
    for enum_model in model.enums:
        lines.append(f"typedef enum {enum_model.c_name} {{")
        for value in enum_model.values:
            lines.append(f"    {value.c_name} = {value.value},")
        lines.append(f"}} {enum_model.c_name};")
        lines.append("")
    lines.extend(
        [
            "const char* ifcopenshell_last_error_message(void);",
            "void ifcopenshell_last_error_clear(void);",
            "void ifcopenshell_string_free(char* value);",
            "",
        ]
    )
    for variant in _all_variants(model):
        return_type = _return_c_type(variant.callable.return_adapter, model)
        parameters = ", ".join(
            f"{_parameter_c_type(parameter, model)} {parameter.name}" for parameter in variant.parameters
        )
        if variant.callable.kind == "method":
            self_type = f"{_class_c_type(variant.owner, model)}* handle"
            parameters = f"{self_type}, {parameters}" if parameters else self_type
        lines.append(f"{return_type} {model.c_prefix}_{variant.api_name}({parameters});")
    if _all_variants(model):
        lines.append("")
    for class_model in sequence_targets:
        list_prefix = f"{model.c_prefix}_{_class_c_identifier(class_model, model)}_list"
        lines.append(f"int {list_prefix}_size(const {_list_c_type(class_model, model)}* handle);")
        lines.append(
            f"{_class_c_type(class_model, model)}* {list_prefix}_get(const {_list_c_type(class_model, model)}* handle, int index);"
        )
        lines.append(f"void {list_prefix}_free({_list_c_type(class_model, model)}* handle);")
        lines.append("")
    for class_model in model.classes:
        lines.append(
            f"void {model.c_prefix}_{_class_c_identifier(class_model, model)}_free({_class_c_type(class_model, model)}* handle);"
        )
    lines.extend(
        [
            "",
            "#ifdef __cplusplus",
            "}",
            "#endif",
            "",
            "#endif",
            "",
        ]
    )
    return "\n".join(lines)


def emit_c_api_implementation(model: ModuleModel) -> str:
    sequence_targets = _sequence_targets(model)
    lines = [
        f'#include "{model.api_header_name}"',
        "",
    ]
    for header in sorted(dict.fromkeys(model.source_headers)):
        lines.append(f'#include "{header}"')
    lines.extend(
        [
            "",
            "#include <algorithm>",
            "#include <memory>",
            "#include <stdexcept>",
            "#include <string>",
            "#include <utility>",
            "#include <vector>",
            "",
            "namespace {",
            "thread_local std::string g_last_error;",
            "",
            "char* duplicate_string(const std::string& value) {",
            "    auto* buffer = new char[value.size() + 1];",
            "    std::copy(value.begin(), value.end(), buffer);",
            "    buffer[value.size()] = '\\0';",
            "    return buffer;",
            "}",
            "",
            "void set_last_error(const std::exception& exception) {",
            "    g_last_error = exception.what();",
            "}",
            "}",
            "",
        ]
    )
    for class_model in model.classes:
        lines.append(f"struct {_class_c_type(class_model, model)} {{")
        if class_model.owner_cpp_name is not None:
            lines.append(f"    std::shared_ptr<{class_model.owner_cpp_name}> owner;")
        if class_model.handle_kind == "shared_ptr":
            lines.append(f"    std::shared_ptr<{class_model.cpp_name}> value;")
        else:
            lines.append(f"    {class_model.cpp_name} value;")
        lines.append("};")
        lines.append("")
    for class_model in sequence_targets:
        lines.append(f"struct {_list_c_type(class_model, model)} {{")
        if class_model.owner_cpp_name is not None:
            lines.append(f"    std::shared_ptr<{class_model.owner_cpp_name}> owner;")
        lines.append(f"    std::vector<{class_model.cpp_name}> value;")
        lines.append("};")
        lines.append("")
    lines.extend(
        [
            'extern "C" {',
            "",
            "const char* ifcopenshell_last_error_message(void) {",
            "    return g_last_error.empty() ? nullptr : g_last_error.c_str();",
            "}",
            "",
            "void ifcopenshell_last_error_clear(void) {",
            "    g_last_error.clear();",
            "}",
            "",
            "void ifcopenshell_string_free(char* value) {",
            "    delete[] value;",
            "}",
            "",
        ]
    )
    for variant in _all_variants(model):
        return_type = _return_c_type(variant.callable.return_adapter, model)
        parameter_list = ", ".join(
            f"{_parameter_c_type(parameter, model)} {parameter.name}" for parameter in variant.parameters
        )
        if variant.callable.kind == "method":
            self_type = f"{_class_c_type(variant.owner, model)}* handle"
            parameter_list = f"{self_type}, {parameter_list}" if parameter_list else self_type
        lines.append(f"{return_type} {model.c_prefix}_{variant.api_name}({parameter_list}) {{")
        lines.append("    ifcopenshell_last_error_clear();")
        lines.append("    try {")
        if variant.callable.kind == "method":
            lines.append("        if (handle == nullptr) {")
            lines.append('            throw std::runtime_error("Null handle received");')
            lines.append("        }")
        for parameter in variant.parameters:
            if is_handle_adapter(parameter.adapter):
                lines.append(f"        if ({parameter.name} == nullptr) {{")
                lines.append(
                    f'            throw std::runtime_error("Null handle parameter received for {parameter.name}");'
                )
                lines.append("        }")
        call_expression = _call_expression(variant, model)
        if variant.callable.kind == "constructor":
            lines.append(f"        auto constructed_value = {call_expression};")
            if variant.owner.handle_kind == "shared_ptr":
                lines.append(
                    f"        return new {_class_c_type(variant.owner, model)}{{ std::move(constructed_value) }};"
                )
            elif variant.owner.owner_cpp_name is not None:
                lines.append(
                    f"        return new {_class_c_type(variant.owner, model)}{{ {{}}, std::move(constructed_value) }};"
                )
            else:
                lines.append(
                    f"        return new {_class_c_type(variant.owner, model)}{{ std::move(constructed_value) }};"
                )
        elif variant.callable.return_adapter == "string":
            lines.append(f"        auto result = {call_expression};")
            lines.append("        return duplicate_string(result);")
        elif variant.callable.return_adapter in {"integer", "bool", "void"} or is_enum_adapter(
            variant.callable.return_adapter
        ):
            if variant.callable.return_adapter == "void":
                lines.append(f"        {call_expression};")
                lines.append("        return;")
            else:
                lines.append(f"        return {call_expression};")
        elif is_handle_adapter(variant.callable.return_adapter):
            target = _class_index(model)[handle_adapter_target(variant.callable.return_adapter)]
            _emit_handle_return_lines(lines, variant.owner, target, variant.callable, call_expression, model)
        elif is_sequence_adapter(variant.callable.return_adapter):
            target = _class_index(model)[sequence_adapter_target(variant.callable.return_adapter)]
            _emit_sequence_return_lines(lines, variant.owner, target, variant.callable, call_expression, model)
        else:
            raise RuntimeError(f"Unsupported return adapter in C API emitter: {variant.callable.return_adapter}")
        lines.append("    } catch (const std::exception& exception) {")
        lines.append("        set_last_error(exception);")
        if return_type == "void":
            lines.append("        return;")
        elif return_type in {"int", "bool"} or is_enum_adapter(variant.callable.return_adapter):
            lines.append("        return 0;")
        else:
            lines.append("        return nullptr;")
        lines.append("    }")
        lines.append("}")
        lines.append("")
    for class_model in sequence_targets:
        list_prefix = f"{model.c_prefix}_{_class_c_identifier(class_model, model)}_list"
        lines.extend(
            [
                f"int {list_prefix}_size(const {_list_c_type(class_model, model)}* handle) {{",
                "    ifcopenshell_last_error_clear();",
                "    try {",
                "        if (handle == nullptr) {",
                '            throw std::runtime_error("Null list handle received");',
                "        }",
                "        return static_cast<int>(handle->value.size());",
                "    } catch (const std::exception& exception) {",
                "        set_last_error(exception);",
                "        return 0;",
                "    }",
                "}",
                "",
                f"{_class_c_type(class_model, model)}* {list_prefix}_get(const {_list_c_type(class_model, model)}* handle, int index) {{",
                "    ifcopenshell_last_error_clear();",
                "    try {",
                "        if (handle == nullptr) {",
                '            throw std::runtime_error("Null list handle received");',
                "        }",
                "        if (index < 0 || static_cast<size_t>(index) >= handle->value.size()) {",
                '            throw std::out_of_range("List index out of range");',
                "        }",
            ]
        )
        if class_model.handle_kind == "shared_ptr":
            lines.append(
                f"        auto item_value = std::make_shared<{class_model.cpp_name}>(handle->value.at(static_cast<size_t>(index)));"
            )
            lines.append(f"        return new {_class_c_type(class_model, model)}{{ std::move(item_value) }};")
        elif class_model.owner_cpp_name is not None:
            lines.append(f"        auto item_value = handle->value.at(static_cast<size_t>(index));")
            lines.append(
                f"        return new {_class_c_type(class_model, model)}{{ handle->owner, std::move(item_value) }};"
            )
        else:
            lines.append(f"        auto item_value = handle->value.at(static_cast<size_t>(index));")
            lines.append(f"        return new {_class_c_type(class_model, model)}{{ std::move(item_value) }};")
        lines.extend(
            [
                "    } catch (const std::exception& exception) {",
                "        set_last_error(exception);",
                "        return nullptr;",
                "    }",
                "}",
                "",
                f"void {list_prefix}_free({_list_c_type(class_model, model)}* handle) {{",
                "    delete handle;",
                "}",
                "",
            ]
        )
    for class_model in model.classes:
        lines.append(
            f"void {model.c_prefix}_{_class_c_identifier(class_model, model)}_free({_class_c_type(class_model, model)}* handle) {{"
        )
        lines.append("    delete handle;")
        lines.append("}")
        lines.append("")
    lines.extend(["}", ""])
    return "\n".join(lines)


def emit_python_extension(model: ModuleModel) -> str:
    class_models = _class_index(model)
    lines = [
        "#define PY_SSIZE_T_CLEAN",
        "#include <Python.h>",
        "",
        f'#include "{model.api_header_name}"',
        "",
    ]
    for class_model in model.classes:
        lines.append(
            f'static const char* {_capsule_name_symbol(class_model)} = "{model.module_name}.{_class_c_identifier(class_model, model)}";'
        )
    lines.extend(
        [
            "",
            "static PyObject* raise_last_error(const char* fallback_message) {",
            "    const char* message = ifcopenshell_last_error_message();",
            "    PyErr_SetString(PyExc_RuntimeError, message ? message : fallback_message);",
            "    return nullptr;",
            "}",
            "",
        ]
    )
    for class_model in model.classes:
        lines.extend(
            [
                f"static void {_capsule_destructor_name(class_model)}(PyObject* capsule) {{",
                f"    auto* handle = static_cast<{_class_c_type(class_model, model)}*>(PyCapsule_GetPointer(capsule, {_capsule_name_symbol(class_model)}));",
                "    if (handle != nullptr) {",
                f"        {model.c_prefix}_{_class_c_identifier(class_model, model)}_free(handle);",
                "    }",
                "    PyErr_Clear();",
                "}",
                "",
            ]
        )
    for variant in _all_variants(model):
        lines.append(f"static PyObject* py_{variant.api_name}(PyObject*, PyObject* args) {{")
        parse_format: list[str] = []
        parse_targets: list[str] = []
        call_arguments: list[str] = []
        if variant.callable.kind == "method":
            lines.append("    PyObject* self_capsule = nullptr;")
            lines.append(f"    auto* handle = static_cast<{_class_c_type(variant.owner, model)}*>(nullptr);")
            parse_format.append("O")
            parse_targets.append("&self_capsule")
        for parameter in variant.parameters:
            if parameter.adapter == "string":
                lines.append(f"    const char* {parameter.name} = nullptr;")
                parse_format.append("s")
                parse_targets.append(f"&{parameter.name}")
            elif parameter.adapter == "bool":
                lines.append(f"    int {parameter.name} = 0;")
                parse_format.append("p")
                parse_targets.append(f"&{parameter.name}")
            elif parameter.adapter == "integer" or is_enum_adapter(parameter.adapter):
                lines.append(f"    int {parameter.name} = 0;")
                parse_format.append("i")
                parse_targets.append(f"&{parameter.name}")
            elif is_handle_adapter(parameter.adapter):
                target = class_models[handle_adapter_target(parameter.adapter)]
                lines.append(f"    PyObject* {parameter.name}_capsule = nullptr;")
                lines.append(f"    auto* {parameter.name} = static_cast<{_class_c_type(target, model)}*>(nullptr);")
                parse_format.append("O")
                parse_targets.append(f"&{parameter.name}_capsule")
            else:
                raise RuntimeError(f"Unsupported parameter adapter in Python extension emitter: {parameter.adapter}")
        if parse_targets:
            lines.append(f'    if (!PyArg_ParseTuple(args, "{"".join(parse_format)}", {", ".join(parse_targets)})) {{')
        else:
            lines.append('    if (!PyArg_ParseTuple(args, "")) {')
        lines.append("        return nullptr;")
        lines.append("    }")
        if variant.callable.kind == "method":
            lines.append(
                f"    handle = static_cast<{_class_c_type(variant.owner, model)}*>(PyCapsule_GetPointer(self_capsule, {_capsule_name_symbol(variant.owner)}));"
            )
            lines.append("    if (handle == nullptr) {")
            lines.append("        return nullptr;")
            lines.append("    }")
            call_arguments.append("handle")
        for parameter in variant.parameters:
            if is_handle_adapter(parameter.adapter):
                target = class_models[handle_adapter_target(parameter.adapter)]
                lines.append(
                    f"    {parameter.name} = static_cast<{_class_c_type(target, model)}*>(PyCapsule_GetPointer({parameter.name}_capsule, {_capsule_name_symbol(target)}));"
                )
                lines.append(f"    if ({parameter.name} == nullptr) {{")
                lines.append("        return nullptr;")
                lines.append("    }")
            call_arguments.append(_extension_native_argument(parameter, model))
        native_call = f"{model.c_prefix}_{variant.api_name}({', '.join(call_arguments)})"
        if variant.callable.return_adapter == "string":
            lines.append(f"    char* result = {native_call};")
            lines.append("    if (result == nullptr) {")
            lines.append('        return raise_last_error("Native call failed");')
            lines.append("    }")
            lines.append("    PyObject* value = PyUnicode_FromString(result);")
            lines.append("    ifcopenshell_string_free(result);")
            lines.append("    return value;")
        elif variant.callable.return_adapter == "integer":
            lines.append(f"    int result = {native_call};")
            lines.append("    if (ifcopenshell_last_error_message() != nullptr) {")
            lines.append('        return raise_last_error("Native call failed");')
            lines.append("    }")
            lines.append("    return PyLong_FromLong(result);")
        elif variant.callable.return_adapter == "bool":
            lines.append(f"    bool result = {native_call};")
            lines.append("    if (ifcopenshell_last_error_message() != nullptr) {")
            lines.append('        return raise_last_error("Native call failed");')
            lines.append("    }")
            lines.append("    return PyBool_FromLong(result ? 1 : 0);")
        elif variant.callable.return_adapter == "void":
            lines.append(f"    {native_call};")
            lines.append("    if (ifcopenshell_last_error_message() != nullptr) {")
            lines.append('        return raise_last_error("Native call failed");')
            lines.append("    }")
            lines.append("    Py_RETURN_NONE;")
        elif is_enum_adapter(variant.callable.return_adapter):
            lines.append(f"    int result = {native_call};")
            lines.append("    if (ifcopenshell_last_error_message() != nullptr) {")
            lines.append('        return raise_last_error("Native call failed");')
            lines.append("    }")
            lines.append("    return PyLong_FromLong(result);")
        elif is_handle_adapter(variant.callable.return_adapter):
            target = class_models[handle_adapter_target(variant.callable.return_adapter)]
            lines.append(f"    auto* result = {native_call};")
            lines.append("    if (result == nullptr) {")
            lines.append('        return raise_last_error("Native call failed");')
            lines.append("    }")
            lines.append(
                f"    return PyCapsule_New(result, {_capsule_name_symbol(target)}, {_capsule_destructor_name(target)});"
            )
        elif is_sequence_adapter(variant.callable.return_adapter):
            target = class_models[sequence_adapter_target(variant.callable.return_adapter)]
            list_prefix = f"{model.c_prefix}_{_class_c_identifier(target, model)}_list"
            lines.append(f"    auto* result = {native_call};")
            lines.append("    if (result == nullptr) {")
            lines.append('        return raise_last_error("Native call failed");')
            lines.append("    }")
            lines.append(f"    int size = {list_prefix}_size(result);")
            lines.append("    if (ifcopenshell_last_error_message() != nullptr) {")
            lines.append(f"        {list_prefix}_free(result);")
            lines.append('        return raise_last_error("Native call failed");')
            lines.append("    }")
            lines.append("    PyObject* values = PyList_New(size);")
            lines.append("    if (values == nullptr) {")
            lines.append(f"        {list_prefix}_free(result);")
            lines.append("        return nullptr;")
            lines.append("    }")
            lines.append("    for (int index = 0; index < size; ++index) {")
            lines.append(f"        auto* item = {list_prefix}_get(result, index);")
            lines.append("        if (item == nullptr) {")
            lines.append("            Py_DECREF(values);")
            lines.append(f"            {list_prefix}_free(result);")
            lines.append('            return raise_last_error("Native call failed");')
            lines.append("        }")
            lines.append(
                f"        PyObject* capsule = PyCapsule_New(item, {_capsule_name_symbol(target)}, {_capsule_destructor_name(target)});"
            )
            lines.append("        if (capsule == nullptr) {")
            lines.append(f"            {model.c_prefix}_{_class_c_identifier(target, model)}_free(item);")
            lines.append("            Py_DECREF(values);")
            lines.append(f"            {list_prefix}_free(result);")
            lines.append("            return nullptr;")
            lines.append("        }")
            lines.append("        PyList_SET_ITEM(values, index, capsule);")
            lines.append("    }")
            lines.append(f"    {list_prefix}_free(result);")
            lines.append("    return values;")
        else:
            raise RuntimeError(
                f"Unsupported return adapter in Python extension emitter: {variant.callable.return_adapter}"
            )
        lines.append("}")
        lines.append("")
    lines.extend(["static PyMethodDef MODULE_METHODS[] = {"])
    for variant in _all_variants(model):
        lines.append(f'    {{"{variant.api_name}", py_{variant.api_name}, METH_VARARGS, nullptr}},')
    lines.extend(
        [
            "    {nullptr, nullptr, 0, nullptr},",
            "};",
            "",
            "static PyModuleDef MODULE_DEF = {",
            "    PyModuleDef_HEAD_INIT,",
            f'    "_{model.module_name}",',
            "    nullptr,",
            "    -1,",
            "    MODULE_METHODS,",
            "};",
            "",
            f"PyMODINIT_FUNC PyInit__{model.module_name}(void) {{",
            "    PyObject* module = PyModule_Create(&MODULE_DEF);",
            "    if (module == nullptr) {",
            "        return nullptr;",
            "    }",
        ]
    )
    for enum_model in model.enums:
        for value in enum_model.values:
            lines.append(f'    if (PyModule_AddIntConstant(module, "{value.name}", {value.c_name}) < 0) {{')
            lines.append("        Py_DECREF(module);")
            lines.append("        return nullptr;")
            lines.append("    }")
    lines.extend(["    return module;", "}", ""])
    return "\n".join(lines)


def _python_type_for_parameter(parameter: ParameterModel, model: ModuleModel) -> str:
    if parameter.adapter == "string":
        return "str"
    if parameter.adapter == "integer":
        return "int"
    if parameter.adapter == "bool":
        return "bool"
    if is_enum_adapter(parameter.adapter):
        return _enum_index(model)[enum_adapter_target(parameter.adapter)].py_name
    if is_handle_adapter(parameter.adapter):
        return _class_index(model)[handle_adapter_target(parameter.adapter)].py_name
    return "object"


def _python_type_for_return(adapter: str, model: ModuleModel) -> str:
    if adapter == "string":
        return "str"
    if adapter == "integer":
        return "int"
    if adapter == "bool":
        return "bool"
    if adapter == "void":
        return "None"
    if is_enum_adapter(adapter):
        return _enum_index(model)[enum_adapter_target(adapter)].py_name
    if is_handle_adapter(adapter):
        return _class_index(model)[handle_adapter_target(adapter)].py_name
    if is_sequence_adapter(adapter):
        target = _class_index(model)[sequence_adapter_target(adapter)]
        return f"list[{target.py_name}]"
    return "object"


def _python_parameter_signature(parameter: ParameterModel, model: ModuleModel) -> str:
    signature = f"{parameter.name}: {_python_type_for_parameter(parameter, model)}"
    if parameter.default_python_value is not None:
        signature += f" = {parameter.default_python_value}"
    return signature


def _python_native_argument(parameter: ParameterModel) -> str:
    if is_enum_adapter(parameter.adapter):
        return f"int({parameter.name})"
    if is_handle_adapter(parameter.adapter):
        return f"{parameter.name}._handle"
    return parameter.name


def _extension_native_argument(parameter: ParameterModel, model: ModuleModel) -> str:
    if is_enum_adapter(parameter.adapter):
        return f"static_cast<{_enum_c_type(parameter.adapter, model)}>({parameter.name})"
    return parameter.name


def _emit_python_return(
    lines: list[str],
    call_expression: str,
    adapter: str,
    model: ModuleModel,
    indent: str,
) -> None:
    if adapter in {"string", "integer", "bool"}:
        lines.append(f"{indent}return {call_expression}")
        return
    if adapter == "void":
        lines.append(f"{indent}{call_expression}")
        lines.append(f"{indent}return None")
        return
    if is_enum_adapter(adapter):
        enum_model = _enum_index(model)[enum_adapter_target(adapter)]
        lines.append(f"{indent}return {enum_model.py_name}({call_expression})")
        return
    if is_handle_adapter(adapter):
        target = _class_index(model)[handle_adapter_target(adapter)]
        lines.append(f"{indent}return {target.py_name}({call_expression})")
        return
    if is_sequence_adapter(adapter):
        target = _class_index(model)[sequence_adapter_target(adapter)]
        lines.append(f"{indent}return [{target.py_name}(item) for item in {call_expression}]")
        return
    raise RuntimeError(f"Unsupported return adapter in Python facade emitter: {adapter}")


def emit_python_facade(model: ModuleModel) -> str:
    lines = [
        "from __future__ import annotations",
        "",
        "from enum import IntEnum",
        "",
        f"import _{model.module_name} as _native",
        "",
    ]
    for enum_model in model.enums:
        lines.append(f"class {enum_model.py_name}(IntEnum):")
        for value in enum_model.values:
            lines.append(f"    {value.name} = _native.{value.name}")
        lines.append("")
    for class_model in model.classes:
        lines.append(f"class {class_model.py_name}:")
        lines.append('    __slots__ = ("_handle",)')
        lines.append("")
        lines.append("    def __init__(self, handle) -> None:")
        lines.append("        self._handle = handle")
        lines.append("")
        for callable_model in class_model.callables:
            parameters = ", ".join(
                _python_parameter_signature(parameter, model) for parameter in callable_model.parameters
            )
            full_variant = _full_variant(class_model, callable_model)
            call_arguments = ", ".join(_python_native_argument(parameter) for parameter in callable_model.parameters)
            return_annotation = _python_type_for_return(callable_model.return_adapter, model)
            if callable_model.kind == "constructor":
                lines.append("    @staticmethod")
                lines.append(f"    def {callable_model.py_name}({parameters}) -> {class_model.py_name}:")
                native_call = f"_native.{full_variant.api_name}({call_arguments})"
                _emit_python_return(lines, native_call, callable_model.return_adapter, model, "        ")
            else:
                signature = f"self, {parameters}" if parameters else "self"
                separator = ", " if call_arguments else ""
                native_call = f"_native.{full_variant.api_name}(self._handle{separator}{call_arguments})"
                lines.append(f"    def {callable_model.py_name}({signature}) -> {return_annotation}:")
                _emit_python_return(lines, native_call, callable_model.return_adapter, model, "        ")
            lines.append("")
        if not class_model.callables:
            lines.append("    pass")
            lines.append("")
    return "\n".join(lines)


def write_module_outputs(model: ModuleModel, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / model.api_header_name).write_text(emit_c_api_header(model), encoding="utf-8")
    (output_dir / model.api_implementation_name).write_text(emit_c_api_implementation(model), encoding="utf-8")
    (output_dir / model.extension_source_name).write_text(emit_python_extension(model), encoding="utf-8")
    (output_dir / model.python_source_name).write_text(emit_python_facade(model), encoding="utf-8")
