// This file was generated with the assistance of an AI coding tool.
// SPDX-License-Identifier: LGPL-3.0-or-later
#include "ifcopenshell_api_internal.hpp"

#include <emscripten/bind.h>
#include <type_traits>

namespace {
using emscripten::val;
template <typename T>
struct is_vector : std::false_type {};
template <typename T>
struct is_vector<std::vector<T>> : std::true_type {};

template <typename T>
val to_js(const T& value, const val& wrap_instance) {
    if constexpr (is_vector<T>::value) {
        auto result = val::array();
        for (const auto& item : value) {
            result.call<void>("push", to_js(item, wrap_instance));
        }
        return result;
    } else if constexpr (std::is_same_v<T, ifcopenshell::blank> || std::is_same_v<T, ifcopenshell::derived> ||
                         std::is_same_v<T, ifcopenshell::empty_aggregate> ||
                         std::is_same_v<T, ifcopenshell::empty_aggregate_of_aggregate>) {
        return val::null();
    } else if constexpr (std::is_same_v<T, express::base>) {
        if (!value) {
            return val::null();
        }
        return wrap_instance(reinterpret_cast<uintptr_t>(new ifcopenshell_instance_t{value}));
    } else if constexpr (std::is_same_v<T, ifcopenshell::enumeration_reference>) {
        return val(std::string(value.value()));
    } else if constexpr (std::is_same_v<T, boost::logic::tribool>) {
        return boost::logic::indeterminate(value) ? val("UNKNOWN") : val(static_cast<bool>(value));
    } else if constexpr (std::is_same_v<T, boost::dynamic_bitset<>>) {
        std::string bits;
        boost::to_string(value, bits);
        return val(bits);
    } else if constexpr (std::is_same_v<T, int64_t>) {
        // Preserve the usual JS number API without rounding large IFC integers.
        if (value >= -9007199254740991LL && value <= 9007199254740991LL) {
            return val(static_cast<double>(value));
        }
        return val(value);
    } else {
        return val(value);
    }
}

val attribute_value_to_js(const ifcopenshell::attribute_value& value, const val& wrap_instance) {
    return value.apply_visitor([&](const auto& v) -> val { return to_js(v, wrap_instance); });
}

template <typename T>
T from_js(const val& value, const val& unwrap_instance, ifcopenshell::file* file) {
    if constexpr (is_vector<T>::value) {
        if (!val::global("Array").call<bool>("isArray", value)) {
            throw std::runtime_error("Expected an array");
        }
        T result;
        const auto count = value["length"].as<unsigned>();
        result.reserve(count);
        for (unsigned i = 0; i < count; ++i) {
            result.push_back(from_js<typename T::value_type>(value[i], unwrap_instance, file));
        }
        return result;
    } else if constexpr (std::is_same_v<T, express::base>) {
        auto* handle = reinterpret_cast<ifcopenshell_instance_t*>(unwrap_instance(value).as<uintptr_t>());
        if (!handle) {
            throw std::runtime_error("Expected a live entity_instance");
        }
        if (handle->value.file() != file) {
            throw std::runtime_error("Cannot reference an entity_instance from a different IFC file");
        }
        return handle->value;
    } else if constexpr (std::is_same_v<T, int64_t>) {
        if (value.typeOf().as<std::string>() == "bigint") {
            if (!val::global("BigInt").call<val>("asIntN", 64, value).strictlyEquals(value)) {
                throw std::runtime_error("Integer exceeds signed 64-bit range");
            }
            return value.as<int64_t>();
        }
        if (!val::global("Number").call<bool>("isSafeInteger", value)) {
            throw std::runtime_error("Expected a safe integer number or signed 64-bit bigint");
        }
        return static_cast<int64_t>(value.as<double>());
    } else if constexpr (std::is_same_v<T, double>) {
        if (value.typeOf().as<std::string>() != "number") {
            throw std::runtime_error("Expected a number");
        }
        return value.as<double>();
    } else if constexpr (std::is_same_v<T, bool>) {
        if (value.typeOf().as<std::string>() != "boolean") {
            throw std::runtime_error("Expected a boolean");
        }
        return value.as<bool>();
    } else if constexpr (std::is_same_v<T, std::string>) {
        if (value.typeOf().as<std::string>() != "string") {
            throw std::runtime_error("Expected a string");
        }
        return value.as<std::string>();
    } else if constexpr (std::is_same_v<T, boost::dynamic_bitset<>>) {
        const auto bits = from_js<std::string>(value, unwrap_instance, file);
        if (!ifcopenshell::valid_binary_string(bits)) {
            throw std::runtime_error("Invalid binary string");
        }
        return boost::dynamic_bitset<>(bits);
    }
}

void set_attribute_value_js(express::base& instance, unsigned index, const val& value, const val& unwrap_instance) {
    using namespace ifcopenshell;
    // Resolve the index before accessing the storage, including for null assignments.
    const auto type = capi::instance_attribute_type(instance, index);
    if (value.isNull()) {
        auto* entity = instance.declaration().as_entity();
        if (entity && index < entity->derived().size() && entity->derived()[index]) {
            instance.set_attribute_value(index, derived{});
        } else {
            instance.set_attribute_value(index, blank{});
        }
        return;
    }
    auto* file = instance.file();
    switch (type) {
#define SET_VALUE(kind, ...)                                                                     \
    case kind:                                                                                   \
        instance.set_attribute_value(index, from_js<__VA_ARGS__>(value, unwrap_instance, file)); \
        return
        SET_VALUE(Argument_INT, int64_t);
        SET_VALUE(Argument_DOUBLE, double);
        SET_VALUE(Argument_BOOL, bool);
        SET_VALUE(Argument_STRING, std::string);
        SET_VALUE(Argument_BINARY, boost::dynamic_bitset<>);
        SET_VALUE(Argument_ENTITY_INSTANCE, express::base);
        SET_VALUE(Argument_AGGREGATE_OF_INT, std::vector<int64_t>);
        SET_VALUE(Argument_AGGREGATE_OF_DOUBLE, std::vector<double>);
        SET_VALUE(Argument_AGGREGATE_OF_STRING, std::vector<std::string>);
        SET_VALUE(Argument_AGGREGATE_OF_BINARY, std::vector<boost::dynamic_bitset<>>);
        SET_VALUE(Argument_AGGREGATE_OF_ENTITY_INSTANCE, std::vector<express::base>);
        SET_VALUE(Argument_AGGREGATE_OF_AGGREGATE_OF_INT, std::vector<std::vector<int64_t>>);
        SET_VALUE(Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE, std::vector<std::vector<double>>);
        SET_VALUE(Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE, std::vector<std::vector<express::base>>);
#undef SET_VALUE
    case Argument_LOGICAL: {
        boost::logic::tribool logical(boost::logic::indeterminate);
        if (value.typeOf().as<std::string>() == "boolean") {
            logical = value.as<bool>();
        } else if (!value.strictlyEquals(val("UNKNOWN"))) {
            throw std::runtime_error("Expected boolean or UNKNOWN");
        }
        instance.set_attribute_value(index, logical);
        return;
    }
    case Argument_ENUMERATION:
        if (!capi::set_instance_argument_enumeration_by_name(instance, index, from_js<std::string>(value, unwrap_instance, file))) {
            throw std::runtime_error("Invalid enumeration value");
        }
        return;
    default:
        throw std::runtime_error("Unsupported attribute type");
    }
}

val read_attribute(uintptr_t ptr, const val& wrap_instance) {
    try {
        return attribute_value_to_js(reinterpret_cast<ifcopenshell_parse_attribute_value_t*>(ptr)->value, wrap_instance);
    } catch (const std::exception& error) {
        val::global("Error").new_(std::string(error.what())).throw_();
        return val::undefined();
    }
}

void write_attribute(uintptr_t ptr, unsigned index, const val& value, const val& unwrap_instance) {
    try {
        set_attribute_value_js(reinterpret_cast<ifcopenshell_instance_t*>(ptr)->value, index, value, unwrap_instance);
    } catch (const std::exception& error) {
        val::global("TypeError").new_(std::string(error.what())).throw_();
    }
}
} // namespace

EMSCRIPTEN_BINDINGS(ifcopenshell_attribute_values) {
    emscripten::function("attributeValueToJs", &read_attribute);
    emscripten::function("setAttributeValueFromJs", &write_attribute);
}
