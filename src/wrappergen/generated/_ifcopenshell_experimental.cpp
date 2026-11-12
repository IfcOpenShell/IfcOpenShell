#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "ifcopenshell_experimental_c_api.h"

static const char* IFCOPENSHELL_EXCEPTION_CAPSULE_NAME = "ifcopenshell_experimental.exception";
static const char* IFCOPENSHELL_ATTRIBUTE_OUT_OF_RANGE_EXCEPTION_CAPSULE_NAME = "ifcopenshell_experimental.attribute_out_of_range_exception";
static const char* IFCOPENSHELL_INVALID_TOKEN_EXCEPTION_CAPSULE_NAME = "ifcopenshell_experimental.invalid_token_exception";
static const char* IFCOPENSHELL_PARAMETER_TYPE_CAPSULE_NAME = "ifcopenshell_experimental.parameter_type";
static const char* IFCOPENSHELL_NAMED_TYPE_CAPSULE_NAME = "ifcopenshell_experimental.named_type";
static const char* IFCOPENSHELL_SIMPLE_TYPE_CAPSULE_NAME = "ifcopenshell_experimental.simple_type";
static const char* IFCOPENSHELL_AGGREGATION_TYPE_CAPSULE_NAME = "ifcopenshell_experimental.aggregation_type";
static const char* IFCOPENSHELL_DECLARATION_CAPSULE_NAME = "ifcopenshell_experimental.declaration";
static const char* IFCOPENSHELL_TYPE_DECLARATION_CAPSULE_NAME = "ifcopenshell_experimental.type_declaration";
static const char* IFCOPENSHELL_SELECT_TYPE_CAPSULE_NAME = "ifcopenshell_experimental.select_type";
static const char* IFCOPENSHELL_ENUMERATION_TYPE_CAPSULE_NAME = "ifcopenshell_experimental.enumeration_type";
static const char* IFCOPENSHELL_ATTRIBUTE_CAPSULE_NAME = "ifcopenshell_experimental.attribute";
static const char* IFCOPENSHELL_INVERSE_ATTRIBUTE_CAPSULE_NAME = "ifcopenshell_experimental.inverse_attribute";
static const char* IFCOPENSHELL_ENTITY_CAPSULE_NAME = "ifcopenshell_experimental.entity";
static const char* IFCOPENSHELL_SCHEMA_DEFINITION_CAPSULE_NAME = "ifcopenshell_experimental.schema_definition";
static const char* EXPRESS_BASE_CAPSULE_NAME = "ifcopenshell_experimental.express_base";
static const char* EXPRESS_ENTITY_CAPSULE_NAME = "ifcopenshell_experimental.express_entity";
static const char* EXPRESS_SELECT_CAPSULE_NAME = "ifcopenshell_experimental.express_select";
static const char* EXPRESS_DECLARED_TYPE_CAPSULE_NAME = "ifcopenshell_experimental.express_declared_type";
static const char* IFCOPENSHELL_FULL_BUFFER_IMPL_CAPSULE_NAME = "ifcopenshell_experimental.full_buffer_impl";
static const char* IFCOPENSHELL_PAGED_FILE_IMPL_CAPSULE_NAME = "ifcopenshell_experimental.paged_file_impl";
static const char* IFCOPENSHELL_PUSHED_SEQUENTIAL_IMPL_CAPSULE_NAME = "ifcopenshell_experimental.pushed_sequential_impl";
static const char* IFCOPENSHELL_CHARACTER_ENCODER_CAPSULE_NAME = "ifcopenshell_experimental.character_encoder";
static const char* IFCOPENSHELL_FILE_OPEN_STATUS_CAPSULE_NAME = "ifcopenshell_experimental.file_open_status";
static const char* IFCOPENSHELL_SPF_HEADER_CAPSULE_NAME = "ifcopenshell_experimental.spf_header";
static const char* IFCOPENSHELL_FILE_CAPSULE_NAME = "ifcopenshell_experimental.file";
static const char* IFCOPENSHELL_GLOBAL_ID_CAPSULE_NAME = "ifcopenshell_experimental.global_id";

static PyObject* raise_last_error(const char* fallback_message) {
    const char* message = ifcopenshell_last_error_message();
    PyErr_SetString(PyExc_RuntimeError, message ? message : fallback_message);
    return nullptr;
}

static void ifcopenshell_exception_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_exception_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_EXCEPTION_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_exception_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_attribute_out_of_range_exception_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_attribute_out_of_range_exception_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_ATTRIBUTE_OUT_OF_RANGE_EXCEPTION_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_attribute_out_of_range_exception_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_invalid_token_exception_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_invalid_token_exception_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_INVALID_TOKEN_EXCEPTION_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_invalid_token_exception_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_parameter_type_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_parameter_type_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_PARAMETER_TYPE_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_parameter_type_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_named_type_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_named_type_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_NAMED_TYPE_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_named_type_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_simple_type_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_simple_type_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_SIMPLE_TYPE_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_simple_type_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_aggregation_type_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_aggregation_type_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_AGGREGATION_TYPE_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_aggregation_type_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_declaration_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_declaration_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_DECLARATION_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_declaration_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_type_declaration_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_type_declaration_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_TYPE_DECLARATION_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_type_declaration_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_select_type_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_select_type_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_SELECT_TYPE_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_select_type_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_enumeration_type_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_enumeration_type_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_ENUMERATION_TYPE_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_enumeration_type_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_attribute_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_attribute_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_ATTRIBUTE_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_attribute_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_inverse_attribute_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_inverse_attribute_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_INVERSE_ATTRIBUTE_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_inverse_attribute_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_entity_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_entity_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_ENTITY_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_entity_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_schema_definition_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_schema_definition_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_SCHEMA_DEFINITION_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_schema_definition_free(handle);
    }
    PyErr_Clear();
}

static void express_base_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_express_base_t*>(PyCapsule_GetPointer(capsule, EXPRESS_BASE_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_express_base_free(handle);
    }
    PyErr_Clear();
}

static void express_entity_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_express_entity_t*>(PyCapsule_GetPointer(capsule, EXPRESS_ENTITY_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_express_entity_free(handle);
    }
    PyErr_Clear();
}

static void express_select_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_express_select_t*>(PyCapsule_GetPointer(capsule, EXPRESS_SELECT_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_express_select_free(handle);
    }
    PyErr_Clear();
}

static void express_declared_type_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_express_declared_type_t*>(PyCapsule_GetPointer(capsule, EXPRESS_DECLARED_TYPE_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_express_declared_type_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_full_buffer_impl_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_full_buffer_impl_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_FULL_BUFFER_IMPL_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_full_buffer_impl_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_paged_file_impl_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_paged_file_impl_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_PAGED_FILE_IMPL_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_paged_file_impl_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_pushed_sequential_impl_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_pushed_sequential_impl_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_PUSHED_SEQUENTIAL_IMPL_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_pushed_sequential_impl_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_character_encoder_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_character_encoder_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_CHARACTER_ENCODER_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_character_encoder_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_file_open_status_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_file_open_status_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_FILE_OPEN_STATUS_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_file_open_status_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_spf_header_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_spf_header_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_SPF_HEADER_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_spf_header_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_file_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_file_free(handle);
    }
    PyErr_Clear();
}

static void ifcopenshell_global_id_capsule_destructor(PyObject* capsule) {
    auto* handle = static_cast<ifcopenshell_global_id_t*>(PyCapsule_GetPointer(capsule, IFCOPENSHELL_GLOBAL_ID_CAPSULE_NAME));
    if (handle != nullptr) {
        ifcopenshell_global_id_free(handle);
    }
    PyErr_Clear();
}

static PyObject* py_exception_new_with_message(PyObject*, PyObject* args) {
    const char* message = nullptr;
    if (!PyArg_ParseTuple(args, "s", &message)) {
        return nullptr;
    }
    auto* result = ifcopenshell_exception_new_with_message(message);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_EXCEPTION_CAPSULE_NAME, ifcopenshell_exception_capsule_destructor);
}

static PyObject* py_attribute_out_of_range_exception_new_with_message(PyObject*, PyObject* args) {
    const char* message = nullptr;
    if (!PyArg_ParseTuple(args, "s", &message)) {
        return nullptr;
    }
    auto* result = ifcopenshell_attribute_out_of_range_exception_new_with_message(message);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_ATTRIBUTE_OUT_OF_RANGE_EXCEPTION_CAPSULE_NAME, ifcopenshell_attribute_out_of_range_exception_capsule_destructor);
}

static PyObject* py_invalid_token_exception_new_with_token_start_token_string_expected_type(PyObject*, PyObject* args) {
    int token_start = 0;
    const char* token_string = nullptr;
    const char* expected_type = nullptr;
    if (!PyArg_ParseTuple(args, "iss", &token_start, &token_string, &expected_type)) {
        return nullptr;
    }
    auto* result = ifcopenshell_invalid_token_exception_new_with_token_start_token_string_expected_type(token_start, token_string, expected_type);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_INVALID_TOKEN_EXCEPTION_CAPSULE_NAME, ifcopenshell_invalid_token_exception_capsule_destructor);
}

static PyObject* py_parameter_type_as_named_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_parameter_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_parameter_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_PARAMETER_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_parameter_type_as_named_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_NAMED_TYPE_CAPSULE_NAME, ifcopenshell_named_type_capsule_destructor);
}

static PyObject* py_parameter_type_as_simple_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_parameter_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_parameter_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_PARAMETER_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_parameter_type_as_simple_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_SIMPLE_TYPE_CAPSULE_NAME, ifcopenshell_simple_type_capsule_destructor);
}

static PyObject* py_parameter_type_as_aggregation_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_parameter_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_parameter_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_PARAMETER_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_parameter_type_as_aggregation_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_AGGREGATION_TYPE_CAPSULE_NAME, ifcopenshell_aggregation_type_capsule_destructor);
}

static PyObject* py_parameter_type_is(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_parameter_type_t*>(nullptr);
    const char* arg0 = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &arg0)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_parameter_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_PARAMETER_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    bool result = ifcopenshell_parameter_type_is(handle, arg0);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyBool_FromLong(result ? 1 : 0);
}

static PyObject* py_named_type_declared_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_named_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_named_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_NAMED_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_named_type_declared_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_DECLARATION_CAPSULE_NAME, ifcopenshell_declaration_capsule_destructor);
}

static PyObject* py_named_type_as_named_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_named_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_named_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_NAMED_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_named_type_as_named_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_NAMED_TYPE_CAPSULE_NAME, ifcopenshell_named_type_capsule_destructor);
}

static PyObject* py_named_type_is(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_named_type_t*>(nullptr);
    const char* name = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &name)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_named_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_NAMED_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    bool result = ifcopenshell_named_type_is(handle, name);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyBool_FromLong(result ? 1 : 0);
}

static PyObject* py_simple_type_as_simple_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_simple_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_simple_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_SIMPLE_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_simple_type_as_simple_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_SIMPLE_TYPE_CAPSULE_NAME, ifcopenshell_simple_type_capsule_destructor);
}

static PyObject* py_aggregation_type_bound1(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_aggregation_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_aggregation_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_AGGREGATION_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_aggregation_type_bound1(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_aggregation_type_bound2(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_aggregation_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_aggregation_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_AGGREGATION_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_aggregation_type_bound2(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_aggregation_type_type_of_element(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_aggregation_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_aggregation_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_AGGREGATION_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_aggregation_type_type_of_element(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_PARAMETER_TYPE_CAPSULE_NAME, ifcopenshell_parameter_type_capsule_destructor);
}

static PyObject* py_aggregation_type_as_aggregation_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_aggregation_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_aggregation_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_AGGREGATION_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_aggregation_type_as_aggregation_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_AGGREGATION_TYPE_CAPSULE_NAME, ifcopenshell_aggregation_type_capsule_destructor);
}

static PyObject* py_declaration_new_with_name_index_in_schema(PyObject*, PyObject* args) {
    const char* name = nullptr;
    int index_in_schema = 0;
    if (!PyArg_ParseTuple(args, "si", &name, &index_in_schema)) {
        return nullptr;
    }
    auto* result = ifcopenshell_declaration_new_with_name_index_in_schema(name, index_in_schema);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_DECLARATION_CAPSULE_NAME, ifcopenshell_declaration_capsule_destructor);
}

static PyObject* py_declaration_name(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_declaration_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_declaration_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_DECLARATION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    char* result = ifcopenshell_declaration_name(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    PyObject* value = PyUnicode_FromString(result);
    ifcopenshell_string_free(result);
    return value;
}

static PyObject* py_declaration_name_uc(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_declaration_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_declaration_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_DECLARATION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    char* result = ifcopenshell_declaration_name_uc(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    PyObject* value = PyUnicode_FromString(result);
    ifcopenshell_string_free(result);
    return value;
}

static PyObject* py_declaration_as_type_declaration(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_declaration_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_declaration_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_DECLARATION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_declaration_as_type_declaration(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_TYPE_DECLARATION_CAPSULE_NAME, ifcopenshell_type_declaration_capsule_destructor);
}

static PyObject* py_declaration_as_select_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_declaration_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_declaration_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_DECLARATION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_declaration_as_select_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_SELECT_TYPE_CAPSULE_NAME, ifcopenshell_select_type_capsule_destructor);
}

static PyObject* py_declaration_as_enumeration_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_declaration_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_declaration_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_DECLARATION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_declaration_as_enumeration_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_ENUMERATION_TYPE_CAPSULE_NAME, ifcopenshell_enumeration_type_capsule_destructor);
}

static PyObject* py_declaration_as_entity(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_declaration_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_declaration_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_DECLARATION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_declaration_as_entity(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_ENTITY_CAPSULE_NAME, ifcopenshell_entity_capsule_destructor);
}

static PyObject* py_declaration_is(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_declaration_t*>(nullptr);
    const char* name = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &name)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_declaration_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_DECLARATION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    bool result = ifcopenshell_declaration_is(handle, name);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyBool_FromLong(result ? 1 : 0);
}

static PyObject* py_declaration_index_in_schema(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_declaration_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_declaration_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_DECLARATION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_declaration_index_in_schema(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_declaration_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_declaration_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_declaration_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_DECLARATION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_declaration_type(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_declaration_schema(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_declaration_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_declaration_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_DECLARATION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_declaration_schema(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_SCHEMA_DEFINITION_CAPSULE_NAME, ifcopenshell_schema_definition_capsule_destructor);
}

static PyObject* py_type_declaration_declared_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_type_declaration_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_type_declaration_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_TYPE_DECLARATION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_type_declaration_declared_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_PARAMETER_TYPE_CAPSULE_NAME, ifcopenshell_parameter_type_capsule_destructor);
}

static PyObject* py_type_declaration_as_type_declaration(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_type_declaration_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_type_declaration_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_TYPE_DECLARATION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_type_declaration_as_type_declaration(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_TYPE_DECLARATION_CAPSULE_NAME, ifcopenshell_type_declaration_capsule_destructor);
}

static PyObject* py_select_type_select_list(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_select_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_select_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_SELECT_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_select_type_select_list(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_declaration_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_declaration_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_declaration_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_declaration_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_declaration_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, IFCOPENSHELL_DECLARATION_CAPSULE_NAME, ifcopenshell_declaration_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_declaration_free(item);
            Py_DECREF(values);
            ifcopenshell_declaration_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_declaration_list_free(result);
    return values;
}

static PyObject* py_select_type_as_select_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_select_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_select_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_SELECT_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_select_type_as_select_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_SELECT_TYPE_CAPSULE_NAME, ifcopenshell_select_type_capsule_destructor);
}

static PyObject* py_enumeration_type_lookup_enum_offset(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_enumeration_type_t*>(nullptr);
    const char* value_name = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &value_name)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_enumeration_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ENUMERATION_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_enumeration_type_lookup_enum_offset(handle, value_name);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_enumeration_type_as_enumeration_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_enumeration_type_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_enumeration_type_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ENUMERATION_TYPE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_enumeration_type_as_enumeration_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_ENUMERATION_TYPE_CAPSULE_NAME, ifcopenshell_enumeration_type_capsule_destructor);
}

static PyObject* py_attribute_name(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_attribute_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_attribute_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ATTRIBUTE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    char* result = ifcopenshell_attribute_name(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    PyObject* value = PyUnicode_FromString(result);
    ifcopenshell_string_free(result);
    return value;
}

static PyObject* py_attribute_type_of_attribute(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_attribute_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_attribute_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ATTRIBUTE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_attribute_type_of_attribute(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_PARAMETER_TYPE_CAPSULE_NAME, ifcopenshell_parameter_type_capsule_destructor);
}

static PyObject* py_attribute_optional(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_attribute_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_attribute_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ATTRIBUTE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    bool result = ifcopenshell_attribute_optional(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyBool_FromLong(result ? 1 : 0);
}

static PyObject* py_inverse_attribute_name(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_inverse_attribute_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_inverse_attribute_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_INVERSE_ATTRIBUTE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    char* result = ifcopenshell_inverse_attribute_name(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    PyObject* value = PyUnicode_FromString(result);
    ifcopenshell_string_free(result);
    return value;
}

static PyObject* py_inverse_attribute_bound1(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_inverse_attribute_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_inverse_attribute_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_INVERSE_ATTRIBUTE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_inverse_attribute_bound1(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_inverse_attribute_bound2(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_inverse_attribute_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_inverse_attribute_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_INVERSE_ATTRIBUTE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_inverse_attribute_bound2(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_inverse_attribute_entity_reference(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_inverse_attribute_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_inverse_attribute_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_INVERSE_ATTRIBUTE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_inverse_attribute_entity_reference(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_ENTITY_CAPSULE_NAME, ifcopenshell_entity_capsule_destructor);
}

static PyObject* py_inverse_attribute_attribute_reference(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_inverse_attribute_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_inverse_attribute_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_INVERSE_ATTRIBUTE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_inverse_attribute_attribute_reference(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_ATTRIBUTE_CAPSULE_NAME, ifcopenshell_attribute_capsule_destructor);
}

static PyObject* py_entity_is_abstract(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_entity_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_entity_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ENTITY_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    bool result = ifcopenshell_entity_is_abstract(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyBool_FromLong(result ? 1 : 0);
}

static PyObject* py_entity_subtypes(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_entity_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_entity_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ENTITY_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_entity_subtypes(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_entity_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_entity_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_entity_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_entity_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_entity_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, IFCOPENSHELL_ENTITY_CAPSULE_NAME, ifcopenshell_entity_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_entity_free(item);
            Py_DECREF(values);
            ifcopenshell_entity_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_entity_list_free(result);
    return values;
}

static PyObject* py_entity_attributes(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_entity_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_entity_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ENTITY_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_entity_attributes(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_attribute_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_attribute_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_attribute_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_attribute_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_attribute_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, IFCOPENSHELL_ATTRIBUTE_CAPSULE_NAME, ifcopenshell_attribute_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_attribute_free(item);
            Py_DECREF(values);
            ifcopenshell_attribute_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_attribute_list_free(result);
    return values;
}

static PyObject* py_entity_all_attributes(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_entity_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_entity_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ENTITY_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_entity_all_attributes(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_attribute_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_attribute_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_attribute_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_attribute_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_attribute_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, IFCOPENSHELL_ATTRIBUTE_CAPSULE_NAME, ifcopenshell_attribute_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_attribute_free(item);
            Py_DECREF(values);
            ifcopenshell_attribute_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_attribute_list_free(result);
    return values;
}

static PyObject* py_entity_all_inverse_attributes(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_entity_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_entity_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ENTITY_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_entity_all_inverse_attributes(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_inverse_attribute_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_inverse_attribute_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_inverse_attribute_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_inverse_attribute_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_inverse_attribute_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, IFCOPENSHELL_INVERSE_ATTRIBUTE_CAPSULE_NAME, ifcopenshell_inverse_attribute_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_inverse_attribute_free(item);
            Py_DECREF(values);
            ifcopenshell_inverse_attribute_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_inverse_attribute_list_free(result);
    return values;
}

static PyObject* py_entity_attribute_by_index(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_entity_t*>(nullptr);
    int index = 0;
    if (!PyArg_ParseTuple(args, "Oi", &self_capsule, &index)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_entity_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ENTITY_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_entity_attribute_by_index(handle, index);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_ATTRIBUTE_CAPSULE_NAME, ifcopenshell_attribute_capsule_destructor);
}

static PyObject* py_entity_attribute_count(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_entity_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_entity_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ENTITY_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_entity_attribute_count(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_entity_supertype(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_entity_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_entity_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ENTITY_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_entity_supertype(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_ENTITY_CAPSULE_NAME, ifcopenshell_entity_capsule_destructor);
}

static PyObject* py_entity_as_entity(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_entity_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_entity_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_ENTITY_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_entity_as_entity(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_ENTITY_CAPSULE_NAME, ifcopenshell_entity_capsule_destructor);
}

static PyObject* py_schema_definition_declaration_by_name_with_name(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_schema_definition_t*>(nullptr);
    const char* name = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &name)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_schema_definition_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_SCHEMA_DEFINITION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_schema_definition_declaration_by_name_with_name(handle, name);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_DECLARATION_CAPSULE_NAME, ifcopenshell_declaration_capsule_destructor);
}

static PyObject* py_schema_definition_declaration_by_name_with_declaration_index(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_schema_definition_t*>(nullptr);
    int declaration_index = 0;
    if (!PyArg_ParseTuple(args, "Oi", &self_capsule, &declaration_index)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_schema_definition_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_SCHEMA_DEFINITION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_schema_definition_declaration_by_name_with_declaration_index(handle, declaration_index);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_DECLARATION_CAPSULE_NAME, ifcopenshell_declaration_capsule_destructor);
}

static PyObject* py_schema_definition_declarations(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_schema_definition_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_schema_definition_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_SCHEMA_DEFINITION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_schema_definition_declarations(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_declaration_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_declaration_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_declaration_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_declaration_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_declaration_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, IFCOPENSHELL_DECLARATION_CAPSULE_NAME, ifcopenshell_declaration_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_declaration_free(item);
            Py_DECREF(values);
            ifcopenshell_declaration_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_declaration_list_free(result);
    return values;
}

static PyObject* py_schema_definition_type_declarations(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_schema_definition_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_schema_definition_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_SCHEMA_DEFINITION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_schema_definition_type_declarations(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_type_declaration_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_type_declaration_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_type_declaration_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_type_declaration_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_type_declaration_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, IFCOPENSHELL_TYPE_DECLARATION_CAPSULE_NAME, ifcopenshell_type_declaration_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_type_declaration_free(item);
            Py_DECREF(values);
            ifcopenshell_type_declaration_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_type_declaration_list_free(result);
    return values;
}

static PyObject* py_schema_definition_select_types(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_schema_definition_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_schema_definition_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_SCHEMA_DEFINITION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_schema_definition_select_types(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_select_type_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_select_type_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_select_type_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_select_type_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_select_type_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, IFCOPENSHELL_SELECT_TYPE_CAPSULE_NAME, ifcopenshell_select_type_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_select_type_free(item);
            Py_DECREF(values);
            ifcopenshell_select_type_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_select_type_list_free(result);
    return values;
}

static PyObject* py_schema_definition_enumeration_types(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_schema_definition_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_schema_definition_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_SCHEMA_DEFINITION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_schema_definition_enumeration_types(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_enumeration_type_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_enumeration_type_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_enumeration_type_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_enumeration_type_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_enumeration_type_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, IFCOPENSHELL_ENUMERATION_TYPE_CAPSULE_NAME, ifcopenshell_enumeration_type_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_enumeration_type_free(item);
            Py_DECREF(values);
            ifcopenshell_enumeration_type_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_enumeration_type_list_free(result);
    return values;
}

static PyObject* py_schema_definition_entities(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_schema_definition_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_schema_definition_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_SCHEMA_DEFINITION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_schema_definition_entities(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_entity_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_entity_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_entity_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_entity_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_entity_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, IFCOPENSHELL_ENTITY_CAPSULE_NAME, ifcopenshell_entity_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_entity_free(item);
            Py_DECREF(values);
            ifcopenshell_entity_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_entity_list_free(result);
    return values;
}

static PyObject* py_schema_definition_name(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_schema_definition_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_schema_definition_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_SCHEMA_DEFINITION_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    char* result = ifcopenshell_schema_definition_name(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    PyObject* value = PyUnicode_FromString(result);
    ifcopenshell_string_free(result);
    return value;
}

static PyObject* py_base_new(PyObject*, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return nullptr;
    }
    auto* result = ifcopenshell_base_new();
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, EXPRESS_BASE_CAPSULE_NAME, express_base_capsule_destructor);
}

static PyObject* py_base_declaration(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_express_base_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_express_base_t*>(PyCapsule_GetPointer(self_capsule, EXPRESS_BASE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_base_declaration(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_DECLARATION_CAPSULE_NAME, ifcopenshell_declaration_capsule_destructor);
}

static PyObject* py_base_unset_attribute_value(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_express_base_t*>(nullptr);
    int attribute_index = 0;
    if (!PyArg_ParseTuple(args, "Oi", &self_capsule, &attribute_index)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_express_base_t*>(PyCapsule_GetPointer(self_capsule, EXPRESS_BASE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_base_unset_attribute_value(handle, attribute_index);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_base_identity(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_express_base_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_express_base_t*>(PyCapsule_GetPointer(self_capsule, EXPRESS_BASE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_base_identity(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_base_id(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_express_base_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_express_base_t*>(PyCapsule_GetPointer(self_capsule, EXPRESS_BASE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_base_id(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_entity_new(PyObject*, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return nullptr;
    }
    auto* result = ifcopenshell_entity_new();
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, EXPRESS_ENTITY_CAPSULE_NAME, express_entity_capsule_destructor);
}

static PyObject* py_entity_get_inverse(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_express_entity_t*>(nullptr);
    const char* attribute_name = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &attribute_name)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_express_entity_t*>(PyCapsule_GetPointer(self_capsule, EXPRESS_ENTITY_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_entity_get_inverse(handle, attribute_name);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_express_entity_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_express_entity_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_express_entity_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_express_entity_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_express_entity_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, EXPRESS_ENTITY_CAPSULE_NAME, express_entity_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_express_entity_free(item);
            Py_DECREF(values);
            ifcopenshell_express_entity_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_express_entity_list_free(result);
    return values;
}

static PyObject* py_select_new(PyObject*, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return nullptr;
    }
    auto* result = ifcopenshell_select_new();
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, EXPRESS_SELECT_CAPSULE_NAME, express_select_capsule_destructor);
}

static PyObject* py_select_concrete(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_express_select_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_express_select_t*>(PyCapsule_GetPointer(self_capsule, EXPRESS_SELECT_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_select_concrete(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, EXPRESS_BASE_CAPSULE_NAME, express_base_capsule_destructor);
}

static PyObject* py_declared_type_new(PyObject*, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return nullptr;
    }
    auto* result = ifcopenshell_declared_type_new();
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, EXPRESS_DECLARED_TYPE_CAPSULE_NAME, express_declared_type_capsule_destructor);
}

static PyObject* py_full_buffer_impl_new(PyObject*, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return nullptr;
    }
    auto* result = ifcopenshell_full_buffer_impl_new();
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_FULL_BUFFER_IMPL_CAPSULE_NAME, ifcopenshell_full_buffer_impl_capsule_destructor);
}

static PyObject* py_full_buffer_impl_new_with_path(PyObject*, PyObject* args) {
    const char* path = nullptr;
    if (!PyArg_ParseTuple(args, "s", &path)) {
        return nullptr;
    }
    auto* result = ifcopenshell_full_buffer_impl_new_with_path(path);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_FULL_BUFFER_IMPL_CAPSULE_NAME, ifcopenshell_full_buffer_impl_capsule_destructor);
}

static PyObject* py_full_buffer_impl_size(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_full_buffer_impl_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_full_buffer_impl_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FULL_BUFFER_IMPL_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_full_buffer_impl_size(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_full_buffer_impl_get_u32(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_full_buffer_impl_t*>(nullptr);
    int position = 0;
    if (!PyArg_ParseTuple(args, "Oi", &self_capsule, &position)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_full_buffer_impl_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FULL_BUFFER_IMPL_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_full_buffer_impl_get_u32(handle, position);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_full_buffer_impl_push_next_page(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_full_buffer_impl_t*>(nullptr);
    const char* page_data = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &page_data)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_full_buffer_impl_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FULL_BUFFER_IMPL_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_full_buffer_impl_push_next_page(handle, page_data);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_full_buffer_impl_drop_pages(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_full_buffer_impl_t*>(nullptr);
    int up_to_position = 0;
    if (!PyArg_ParseTuple(args, "Oi", &self_capsule, &up_to_position)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_full_buffer_impl_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FULL_BUFFER_IMPL_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_full_buffer_impl_drop_pages(handle, up_to_position);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_paged_file_impl_new_with_path_page_size_page_capacity(PyObject*, PyObject* args) {
    const char* path = nullptr;
    int page_size = 0;
    int page_capacity = 0;
    if (!PyArg_ParseTuple(args, "sii", &path, &page_size, &page_capacity)) {
        return nullptr;
    }
    auto* result = ifcopenshell_paged_file_impl_new_with_path_page_size_page_capacity(path, page_size, page_capacity);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_PAGED_FILE_IMPL_CAPSULE_NAME, ifcopenshell_paged_file_impl_capsule_destructor);
}

static PyObject* py_paged_file_impl_size(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_paged_file_impl_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_paged_file_impl_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_PAGED_FILE_IMPL_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_paged_file_impl_size(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_paged_file_impl_get_u32(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_paged_file_impl_t*>(nullptr);
    int position = 0;
    if (!PyArg_ParseTuple(args, "Oi", &self_capsule, &position)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_paged_file_impl_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_PAGED_FILE_IMPL_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_paged_file_impl_get_u32(handle, position);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_paged_file_impl_push_next_page(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_paged_file_impl_t*>(nullptr);
    const char* page_data = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &page_data)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_paged_file_impl_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_PAGED_FILE_IMPL_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_paged_file_impl_push_next_page(handle, page_data);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_paged_file_impl_drop_pages(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_paged_file_impl_t*>(nullptr);
    int up_to_position = 0;
    if (!PyArg_ParseTuple(args, "Oi", &self_capsule, &up_to_position)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_paged_file_impl_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_PAGED_FILE_IMPL_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_paged_file_impl_drop_pages(handle, up_to_position);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_pushed_sequential_impl_size(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_pushed_sequential_impl_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_pushed_sequential_impl_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_PUSHED_SEQUENTIAL_IMPL_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_pushed_sequential_impl_size(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_pushed_sequential_impl_get_u32(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_pushed_sequential_impl_t*>(nullptr);
    int position = 0;
    if (!PyArg_ParseTuple(args, "Oi", &self_capsule, &position)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_pushed_sequential_impl_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_PUSHED_SEQUENTIAL_IMPL_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_pushed_sequential_impl_get_u32(handle, position);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_pushed_sequential_impl_push_next_page(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_pushed_sequential_impl_t*>(nullptr);
    const char* page_data = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &page_data)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_pushed_sequential_impl_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_PUSHED_SEQUENTIAL_IMPL_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_pushed_sequential_impl_push_next_page(handle, page_data);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_pushed_sequential_impl_drop_pages(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_pushed_sequential_impl_t*>(nullptr);
    int up_to_position = 0;
    if (!PyArg_ParseTuple(args, "Oi", &self_capsule, &up_to_position)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_pushed_sequential_impl_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_PUSHED_SEQUENTIAL_IMPL_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_pushed_sequential_impl_drop_pages(handle, up_to_position);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_character_encoder_new_with_input(PyObject*, PyObject* args) {
    const char* input = nullptr;
    if (!PyArg_ParseTuple(args, "s", &input)) {
        return nullptr;
    }
    auto* result = ifcopenshell_character_encoder_new_with_input(input);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_CHARACTER_ENCODER_CAPSULE_NAME, ifcopenshell_character_encoder_capsule_destructor);
}

static PyObject* py_file_new_with_path(PyObject*, PyObject* args) {
    const char* path = nullptr;
    if (!PyArg_ParseTuple(args, "s", &path)) {
        return nullptr;
    }
    auto* result = ifcopenshell_file_new_with_path(path);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_FILE_CAPSULE_NAME, ifcopenshell_file_capsule_destructor);
}

static PyObject* py_file_new_with_path_with_filetype(PyObject*, PyObject* args) {
    const char* path = nullptr;
    int filetype = 0;
    if (!PyArg_ParseTuple(args, "si", &path, &filetype)) {
        return nullptr;
    }
    auto* result = ifcopenshell_file_new_with_path_with_filetype(path, static_cast<ifcopenshell_file_type_t>(filetype));
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_FILE_CAPSULE_NAME, ifcopenshell_file_capsule_destructor);
}

static PyObject* py_file_new_with_path_with_filetype_readonly(PyObject*, PyObject* args) {
    const char* path = nullptr;
    int filetype = 0;
    int readonly = 0;
    if (!PyArg_ParseTuple(args, "sip", &path, &filetype, &readonly)) {
        return nullptr;
    }
    auto* result = ifcopenshell_file_new_with_path_with_filetype_readonly(path, static_cast<ifcopenshell_file_type_t>(filetype), readonly);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_FILE_CAPSULE_NAME, ifcopenshell_file_capsule_destructor);
}

static PyObject* py_file_initialize(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    const char* path = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &path)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    bool result = ifcopenshell_file_initialize(handle, path);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyBool_FromLong(result ? 1 : 0);
}

static PyObject* py_file_initialize_with_filetype(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    const char* path = nullptr;
    int filetype = 0;
    if (!PyArg_ParseTuple(args, "Osi", &self_capsule, &path, &filetype)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    bool result = ifcopenshell_file_initialize_with_filetype(handle, path, static_cast<ifcopenshell_file_type_t>(filetype));
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyBool_FromLong(result ? 1 : 0);
}

static PyObject* py_file_initialize_with_filetype_readonly(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    const char* path = nullptr;
    int filetype = 0;
    int readonly = 0;
    if (!PyArg_ParseTuple(args, "Osip", &self_capsule, &path, &filetype, &readonly)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    bool result = ifcopenshell_file_initialize_with_filetype_readonly(handle, path, static_cast<ifcopenshell_file_type_t>(filetype), readonly);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyBool_FromLong(result ? 1 : 0);
}

static PyObject* py_file_bypass_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    const char* type_name = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &type_name)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_file_bypass_type(handle, type_name);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_file_good(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_file_good(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_FILE_OPEN_STATUS_CAPSULE_NAME, ifcopenshell_file_open_status_capsule_destructor);
}

static PyObject* py_file_instances_by_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    const char* type_name = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &type_name)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_file_instances_by_type(handle, type_name);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_express_base_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_express_base_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_express_base_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_express_base_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_express_base_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, EXPRESS_BASE_CAPSULE_NAME, express_base_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_express_base_free(item);
            Py_DECREF(values);
            ifcopenshell_express_base_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_express_base_list_free(result);
    return values;
}

static PyObject* py_file_instances_by_type_excl_subtypes(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    const char* type_name = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &type_name)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_file_instances_by_type_excl_subtypes(handle, type_name);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_express_base_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_express_base_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_express_base_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_express_base_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_express_base_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, EXPRESS_BASE_CAPSULE_NAME, express_base_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_express_base_free(item);
            Py_DECREF(values);
            ifcopenshell_express_base_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_express_base_list_free(result);
    return values;
}

static PyObject* py_file_instances_by_reference(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    int reference_id = 0;
    if (!PyArg_ParseTuple(args, "Oi", &self_capsule, &reference_id)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_file_instances_by_reference(handle, reference_id);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    int size = ifcopenshell_express_base_list_size(result);
    if (ifcopenshell_last_error_message() != nullptr) {
        ifcopenshell_express_base_list_free(result);
        return raise_last_error("Native call failed");
    }
    PyObject* values = PyList_New(size);
    if (values == nullptr) {
        ifcopenshell_express_base_list_free(result);
        return nullptr;
    }
    for (int index = 0; index < size; ++index) {
        auto* item = ifcopenshell_express_base_list_get(result, index);
        if (item == nullptr) {
            Py_DECREF(values);
            ifcopenshell_express_base_list_free(result);
            return raise_last_error("Native call failed");
        }
        PyObject* capsule = PyCapsule_New(item, EXPRESS_BASE_CAPSULE_NAME, express_base_capsule_destructor);
        if (capsule == nullptr) {
            ifcopenshell_express_base_free(item);
            Py_DECREF(values);
            ifcopenshell_express_base_list_free(result);
            return nullptr;
        }
        PyList_SET_ITEM(values, index, capsule);
    }
    ifcopenshell_express_base_list_free(result);
    return values;
}

static PyObject* py_file_instance_by_id(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    int instance_id = 0;
    if (!PyArg_ParseTuple(args, "Oi", &self_capsule, &instance_id)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_file_instance_by_id(handle, instance_id);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, EXPRESS_BASE_CAPSULE_NAME, express_base_capsule_destructor);
}

static PyObject* py_file_instance_by_guid(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    const char* global_id = nullptr;
    if (!PyArg_ParseTuple(args, "Os", &self_capsule, &global_id)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_file_instance_by_guid(handle, global_id);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, EXPRESS_BASE_CAPSULE_NAME, express_base_capsule_destructor);
}

static PyObject* py_file_get_total_inverses(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    int instance_id = 0;
    if (!PyArg_ParseTuple(args, "Oi", &self_capsule, &instance_id)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_file_get_total_inverses(handle, instance_id);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_file_fresh_id(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_file_fresh_id(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_file_get_max_id(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    int result = ifcopenshell_file_get_max_id(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyLong_FromLong(result);
}

static PyObject* py_file_ifcroot_type(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_file_ifcroot_type(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_DECLARATION_CAPSULE_NAME, ifcopenshell_declaration_capsule_destructor);
}

static PyObject* py_file_recalculate_id_counter(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_file_recalculate_id_counter(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_file_header(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_file_header(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_SPF_HEADER_CAPSULE_NAME, ifcopenshell_spf_header_capsule_destructor);
}

static PyObject* py_file_schema(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    auto* result = ifcopenshell_file_schema(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_SCHEMA_DEFINITION_CAPSULE_NAME, ifcopenshell_schema_definition_capsule_destructor);
}

static PyObject* py_file_build_inverses(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_file_build_inverses(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_file_batch(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_file_batch(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_file_unbatch(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_file_unbatch(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_file_reset_identity_cache(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_file_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_file_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_FILE_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    ifcopenshell_file_reset_identity_cache(handle);
    if (ifcopenshell_last_error_message() != nullptr) {
        return raise_last_error("Native call failed");
    }
    Py_RETURN_NONE;
}

static PyObject* py_global_id_new(PyObject*, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return nullptr;
    }
    auto* result = ifcopenshell_global_id_new();
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_GLOBAL_ID_CAPSULE_NAME, ifcopenshell_global_id_capsule_destructor);
}

static PyObject* py_global_id_new_with_value(PyObject*, PyObject* args) {
    const char* value = nullptr;
    if (!PyArg_ParseTuple(args, "s", &value)) {
        return nullptr;
    }
    auto* result = ifcopenshell_global_id_new_with_value(value);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    return PyCapsule_New(result, IFCOPENSHELL_GLOBAL_ID_CAPSULE_NAME, ifcopenshell_global_id_capsule_destructor);
}

static PyObject* py_global_id_formatted(PyObject*, PyObject* args) {
    PyObject* self_capsule = nullptr;
    auto* handle = static_cast<ifcopenshell_global_id_t*>(nullptr);
    if (!PyArg_ParseTuple(args, "O", &self_capsule)) {
        return nullptr;
    }
    handle = static_cast<ifcopenshell_global_id_t*>(PyCapsule_GetPointer(self_capsule, IFCOPENSHELL_GLOBAL_ID_CAPSULE_NAME));
    if (handle == nullptr) {
        return nullptr;
    }
    char* result = ifcopenshell_global_id_formatted(handle);
    if (result == nullptr) {
        return raise_last_error("Native call failed");
    }
    PyObject* value = PyUnicode_FromString(result);
    ifcopenshell_string_free(result);
    return value;
}

static PyMethodDef MODULE_METHODS[] = {
    {"exception_new_with_message", py_exception_new_with_message, METH_VARARGS, nullptr},
    {"attribute_out_of_range_exception_new_with_message", py_attribute_out_of_range_exception_new_with_message, METH_VARARGS, nullptr},
    {"invalid_token_exception_new_with_token_start_token_string_expected_type", py_invalid_token_exception_new_with_token_start_token_string_expected_type, METH_VARARGS, nullptr},
    {"parameter_type_as_named_type", py_parameter_type_as_named_type, METH_VARARGS, nullptr},
    {"parameter_type_as_simple_type", py_parameter_type_as_simple_type, METH_VARARGS, nullptr},
    {"parameter_type_as_aggregation_type", py_parameter_type_as_aggregation_type, METH_VARARGS, nullptr},
    {"parameter_type_is", py_parameter_type_is, METH_VARARGS, nullptr},
    {"named_type_declared_type", py_named_type_declared_type, METH_VARARGS, nullptr},
    {"named_type_as_named_type", py_named_type_as_named_type, METH_VARARGS, nullptr},
    {"named_type_is", py_named_type_is, METH_VARARGS, nullptr},
    {"simple_type_as_simple_type", py_simple_type_as_simple_type, METH_VARARGS, nullptr},
    {"aggregation_type_bound1", py_aggregation_type_bound1, METH_VARARGS, nullptr},
    {"aggregation_type_bound2", py_aggregation_type_bound2, METH_VARARGS, nullptr},
    {"aggregation_type_type_of_element", py_aggregation_type_type_of_element, METH_VARARGS, nullptr},
    {"aggregation_type_as_aggregation_type", py_aggregation_type_as_aggregation_type, METH_VARARGS, nullptr},
    {"declaration_new_with_name_index_in_schema", py_declaration_new_with_name_index_in_schema, METH_VARARGS, nullptr},
    {"declaration_name", py_declaration_name, METH_VARARGS, nullptr},
    {"declaration_name_uc", py_declaration_name_uc, METH_VARARGS, nullptr},
    {"declaration_as_type_declaration", py_declaration_as_type_declaration, METH_VARARGS, nullptr},
    {"declaration_as_select_type", py_declaration_as_select_type, METH_VARARGS, nullptr},
    {"declaration_as_enumeration_type", py_declaration_as_enumeration_type, METH_VARARGS, nullptr},
    {"declaration_as_entity", py_declaration_as_entity, METH_VARARGS, nullptr},
    {"declaration_is", py_declaration_is, METH_VARARGS, nullptr},
    {"declaration_index_in_schema", py_declaration_index_in_schema, METH_VARARGS, nullptr},
    {"declaration_type", py_declaration_type, METH_VARARGS, nullptr},
    {"declaration_schema", py_declaration_schema, METH_VARARGS, nullptr},
    {"type_declaration_declared_type", py_type_declaration_declared_type, METH_VARARGS, nullptr},
    {"type_declaration_as_type_declaration", py_type_declaration_as_type_declaration, METH_VARARGS, nullptr},
    {"select_type_select_list", py_select_type_select_list, METH_VARARGS, nullptr},
    {"select_type_as_select_type", py_select_type_as_select_type, METH_VARARGS, nullptr},
    {"enumeration_type_lookup_enum_offset", py_enumeration_type_lookup_enum_offset, METH_VARARGS, nullptr},
    {"enumeration_type_as_enumeration_type", py_enumeration_type_as_enumeration_type, METH_VARARGS, nullptr},
    {"attribute_name", py_attribute_name, METH_VARARGS, nullptr},
    {"attribute_type_of_attribute", py_attribute_type_of_attribute, METH_VARARGS, nullptr},
    {"attribute_optional", py_attribute_optional, METH_VARARGS, nullptr},
    {"inverse_attribute_name", py_inverse_attribute_name, METH_VARARGS, nullptr},
    {"inverse_attribute_bound1", py_inverse_attribute_bound1, METH_VARARGS, nullptr},
    {"inverse_attribute_bound2", py_inverse_attribute_bound2, METH_VARARGS, nullptr},
    {"inverse_attribute_entity_reference", py_inverse_attribute_entity_reference, METH_VARARGS, nullptr},
    {"inverse_attribute_attribute_reference", py_inverse_attribute_attribute_reference, METH_VARARGS, nullptr},
    {"entity_is_abstract", py_entity_is_abstract, METH_VARARGS, nullptr},
    {"entity_subtypes", py_entity_subtypes, METH_VARARGS, nullptr},
    {"entity_attributes", py_entity_attributes, METH_VARARGS, nullptr},
    {"entity_all_attributes", py_entity_all_attributes, METH_VARARGS, nullptr},
    {"entity_all_inverse_attributes", py_entity_all_inverse_attributes, METH_VARARGS, nullptr},
    {"entity_attribute_by_index", py_entity_attribute_by_index, METH_VARARGS, nullptr},
    {"entity_attribute_count", py_entity_attribute_count, METH_VARARGS, nullptr},
    {"entity_supertype", py_entity_supertype, METH_VARARGS, nullptr},
    {"entity_as_entity", py_entity_as_entity, METH_VARARGS, nullptr},
    {"schema_definition_declaration_by_name_with_name", py_schema_definition_declaration_by_name_with_name, METH_VARARGS, nullptr},
    {"schema_definition_declaration_by_name_with_declaration_index", py_schema_definition_declaration_by_name_with_declaration_index, METH_VARARGS, nullptr},
    {"schema_definition_declarations", py_schema_definition_declarations, METH_VARARGS, nullptr},
    {"schema_definition_type_declarations", py_schema_definition_type_declarations, METH_VARARGS, nullptr},
    {"schema_definition_select_types", py_schema_definition_select_types, METH_VARARGS, nullptr},
    {"schema_definition_enumeration_types", py_schema_definition_enumeration_types, METH_VARARGS, nullptr},
    {"schema_definition_entities", py_schema_definition_entities, METH_VARARGS, nullptr},
    {"schema_definition_name", py_schema_definition_name, METH_VARARGS, nullptr},
    {"base_new", py_base_new, METH_VARARGS, nullptr},
    {"base_declaration", py_base_declaration, METH_VARARGS, nullptr},
    {"base_unset_attribute_value", py_base_unset_attribute_value, METH_VARARGS, nullptr},
    {"base_identity", py_base_identity, METH_VARARGS, nullptr},
    {"base_id", py_base_id, METH_VARARGS, nullptr},
    {"entity_new", py_entity_new, METH_VARARGS, nullptr},
    {"entity_get_inverse", py_entity_get_inverse, METH_VARARGS, nullptr},
    {"select_new", py_select_new, METH_VARARGS, nullptr},
    {"select_concrete", py_select_concrete, METH_VARARGS, nullptr},
    {"declared_type_new", py_declared_type_new, METH_VARARGS, nullptr},
    {"full_buffer_impl_new", py_full_buffer_impl_new, METH_VARARGS, nullptr},
    {"full_buffer_impl_new_with_path", py_full_buffer_impl_new_with_path, METH_VARARGS, nullptr},
    {"full_buffer_impl_size", py_full_buffer_impl_size, METH_VARARGS, nullptr},
    {"full_buffer_impl_get_u32", py_full_buffer_impl_get_u32, METH_VARARGS, nullptr},
    {"full_buffer_impl_push_next_page", py_full_buffer_impl_push_next_page, METH_VARARGS, nullptr},
    {"full_buffer_impl_drop_pages", py_full_buffer_impl_drop_pages, METH_VARARGS, nullptr},
    {"paged_file_impl_new_with_path_page_size_page_capacity", py_paged_file_impl_new_with_path_page_size_page_capacity, METH_VARARGS, nullptr},
    {"paged_file_impl_size", py_paged_file_impl_size, METH_VARARGS, nullptr},
    {"paged_file_impl_get_u32", py_paged_file_impl_get_u32, METH_VARARGS, nullptr},
    {"paged_file_impl_push_next_page", py_paged_file_impl_push_next_page, METH_VARARGS, nullptr},
    {"paged_file_impl_drop_pages", py_paged_file_impl_drop_pages, METH_VARARGS, nullptr},
    {"pushed_sequential_impl_size", py_pushed_sequential_impl_size, METH_VARARGS, nullptr},
    {"pushed_sequential_impl_get_u32", py_pushed_sequential_impl_get_u32, METH_VARARGS, nullptr},
    {"pushed_sequential_impl_push_next_page", py_pushed_sequential_impl_push_next_page, METH_VARARGS, nullptr},
    {"pushed_sequential_impl_drop_pages", py_pushed_sequential_impl_drop_pages, METH_VARARGS, nullptr},
    {"character_encoder_new_with_input", py_character_encoder_new_with_input, METH_VARARGS, nullptr},
    {"file_new_with_path", py_file_new_with_path, METH_VARARGS, nullptr},
    {"file_new_with_path_with_filetype", py_file_new_with_path_with_filetype, METH_VARARGS, nullptr},
    {"file_new_with_path_with_filetype_readonly", py_file_new_with_path_with_filetype_readonly, METH_VARARGS, nullptr},
    {"file_initialize", py_file_initialize, METH_VARARGS, nullptr},
    {"file_initialize_with_filetype", py_file_initialize_with_filetype, METH_VARARGS, nullptr},
    {"file_initialize_with_filetype_readonly", py_file_initialize_with_filetype_readonly, METH_VARARGS, nullptr},
    {"file_bypass_type", py_file_bypass_type, METH_VARARGS, nullptr},
    {"file_good", py_file_good, METH_VARARGS, nullptr},
    {"file_instances_by_type", py_file_instances_by_type, METH_VARARGS, nullptr},
    {"file_instances_by_type_excl_subtypes", py_file_instances_by_type_excl_subtypes, METH_VARARGS, nullptr},
    {"file_instances_by_reference", py_file_instances_by_reference, METH_VARARGS, nullptr},
    {"file_instance_by_id", py_file_instance_by_id, METH_VARARGS, nullptr},
    {"file_instance_by_guid", py_file_instance_by_guid, METH_VARARGS, nullptr},
    {"file_get_total_inverses", py_file_get_total_inverses, METH_VARARGS, nullptr},
    {"file_fresh_id", py_file_fresh_id, METH_VARARGS, nullptr},
    {"file_get_max_id", py_file_get_max_id, METH_VARARGS, nullptr},
    {"file_ifcroot_type", py_file_ifcroot_type, METH_VARARGS, nullptr},
    {"file_recalculate_id_counter", py_file_recalculate_id_counter, METH_VARARGS, nullptr},
    {"file_header", py_file_header, METH_VARARGS, nullptr},
    {"file_schema", py_file_schema, METH_VARARGS, nullptr},
    {"file_build_inverses", py_file_build_inverses, METH_VARARGS, nullptr},
    {"file_batch", py_file_batch, METH_VARARGS, nullptr},
    {"file_unbatch", py_file_unbatch, METH_VARARGS, nullptr},
    {"file_reset_identity_cache", py_file_reset_identity_cache, METH_VARARGS, nullptr},
    {"global_id_new", py_global_id_new, METH_VARARGS, nullptr},
    {"global_id_new_with_value", py_global_id_new_with_value, METH_VARARGS, nullptr},
    {"global_id_formatted", py_global_id_formatted, METH_VARARGS, nullptr},
    {nullptr, nullptr, 0, nullptr},
};

static PyModuleDef MODULE_DEF = {
    PyModuleDef_HEAD_INIT,
    "_ifcopenshell_experimental",
    nullptr,
    -1,
    MODULE_METHODS,
};

PyMODINIT_FUNC PyInit__ifcopenshell_experimental(void) {
    PyObject* module = PyModule_Create(&MODULE_DEF);
    if (module == nullptr) {
        return nullptr;
    }
    if (PyModule_AddIntConstant(module, "FT_IFCSPF", IFCOPENSHELL_FILE_TYPE_T_FT_IFCSPF) < 0) {
        Py_DECREF(module);
        return nullptr;
    }
    if (PyModule_AddIntConstant(module, "FT_IFCXML", IFCOPENSHELL_FILE_TYPE_T_FT_IFCXML) < 0) {
        Py_DECREF(module);
        return nullptr;
    }
    if (PyModule_AddIntConstant(module, "FT_IFCZIP", IFCOPENSHELL_FILE_TYPE_T_FT_IFCZIP) < 0) {
        Py_DECREF(module);
        return nullptr;
    }
    if (PyModule_AddIntConstant(module, "FT_ROCKSDB", IFCOPENSHELL_FILE_TYPE_T_FT_ROCKSDB) < 0) {
        Py_DECREF(module);
        return nullptr;
    }
    if (PyModule_AddIntConstant(module, "FT_UNKNOWN", IFCOPENSHELL_FILE_TYPE_T_FT_UNKNOWN) < 0) {
        Py_DECREF(module);
        return nullptr;
    }
    if (PyModule_AddIntConstant(module, "FT_AUTODETECT", IFCOPENSHELL_FILE_TYPE_T_FT_AUTODETECT) < 0) {
        Py_DECREF(module);
        return nullptr;
    }
    return module;
}
