#include "ifcopenshell_api.h"
#include "ifcopenshell_api_internal.hpp"

#include <algorithm>
#include <array>
#include <cstring>
#include <exception>
#include <fstream>
#include <iterator>
#include <limits>
#include <memory>
#include <new>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <typeinfo>
#include <utility>
#include <variant>
#include <vector>

// Note: project-specific headers (geometry, serializers, schema, etc.) are
// pulled in transitively via ifcopenshell_api_internal.hpp; do not re-include them
// here to avoid header-guard-less redefinitions in third-party headers.
#include "utils.h"

// Error reporting state. Defined in the named ifcopenshell::capi namespace so
// that external translation units can participate via the internal header.
namespace ifcopenshell {
namespace capi {
thread_local std::string g_last_error;
thread_local int g_last_error_kind = IFCOPENSHELL_ERROR_NONE;
thread_local int g_last_error_code = IFCOPENSHELL_ERROR_CODE_NONE;

void set_last_error(const std::string& message) {
    g_last_error_kind = IFCOPENSHELL_ERROR_RUNTIME;
    g_last_error_code = IFCOPENSHELL_ERROR_CODE_UNSPECIFIED;
    g_last_error = message;
}

void set_last_error(int kind, const std::string& message) {
    g_last_error_kind = kind;
    g_last_error_code = kind == IFCOPENSHELL_ERROR_NONE
        ? IFCOPENSHELL_ERROR_CODE_NONE
        : IFCOPENSHELL_ERROR_CODE_UNSPECIFIED;
    g_last_error = message;
}

void set_last_error(int kind, int code, const std::string& message) {
    g_last_error_kind = kind;
    g_last_error_code = code;
    g_last_error = message;
}

int last_error_kind() {
    return g_last_error_kind;
}

void set_error_from_current_exception() {
    if (last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
        return;
    }
    try {
        throw;
    } catch (const std::invalid_argument& error) {
        set_last_error(IFCOPENSHELL_ERROR_VALUE, IFCOPENSHELL_ERROR_CODE_INVALID_ARGUMENT, error.what());
    } catch (const std::domain_error& error) {
        set_last_error(IFCOPENSHELL_ERROR_VALUE, IFCOPENSHELL_ERROR_CODE_DOMAIN_ERROR, error.what());
    } catch (const std::bad_cast& error) {
        set_last_error(IFCOPENSHELL_ERROR_TYPE, IFCOPENSHELL_ERROR_CODE_UNSPECIFIED, error.what());
    } catch (const std::bad_typeid& error) {
        set_last_error(IFCOPENSHELL_ERROR_TYPE, IFCOPENSHELL_ERROR_CODE_UNSPECIFIED, error.what());
    } catch (const std::exception& error) {
        set_last_error(IFCOPENSHELL_ERROR_RUNTIME, IFCOPENSHELL_ERROR_CODE_UNSPECIFIED, error.what());
    } catch (...) {
        set_last_error(IFCOPENSHELL_ERROR_RUNTIME, IFCOPENSHELL_ERROR_CODE_UNSPECIFIED, "Unknown C++ exception");
    }
}
} // namespace capi
} // namespace ifcopenshell

namespace {
using ifcopenshell::capi::g_last_error;
using ifcopenshell::capi::set_last_error;

struct capi_buffer_owner {
    virtual ~capi_buffer_owner() = default;
};

template <typename T>
struct capi_value_owner final : capi_buffer_owner {
    explicit capi_value_owner(T value) : value(std::move(value)) {}
    T value;
};

template <typename T>
struct capi_array_owner final : capi_buffer_owner {
    explicit capi_array_owner(size_t size)
        : values(size == 0 ? nullptr : std::make_unique<T[]>(size)) {}
    std::unique_ptr<T[]> values;
};

template <size_t N, typename Sequence>
auto to_fixed_array(Sequence&& values) {
    if (values.size() != N) {
        throw std::invalid_argument("Fixed-size sequence has invalid cardinality");
    }
    using item_type = std::decay_t<decltype(values[0])>;
    std::array<item_type, N> result{};
    std::move(values.begin(), values.end(), result.begin());
    return result;
}

template <typename Sequence, typename Transform>
auto transform_sequence(Sequence&& values, Transform transform) {
    using item_type = decltype(transform(std::move(values[0])));
    std::vector<item_type> result;
    result.reserve(values.size());
    for (auto& value : values) {
        result.push_back(transform(std::move(value)));
    }
    return result;
}

template <size_t N, typename Sequence, typename Transform>
auto transform_fixed_sequence(Sequence&& values, Transform transform) {
    if (values.size() != N) {
        throw std::invalid_argument("Fixed-size sequence has invalid cardinality");
    }
    using item_type = decltype(transform(std::move(values[0])));
    std::array<item_type, N> result{};
    for (size_t index = 0; index < N; ++index) {
        result[index] = transform(std::move(values[index]));
    }
    return result;
}

bool feature_use_attribute_value_derived = false;
std::stringstream ifcopenshell_log_stream;
bool g_log_stream_initialized = false;

void ensure_log_stream_initialized() {
    if (!g_log_stream_initialized) {
        logger::set_output(nullptr, &ifcopenshell_log_stream);
        g_log_stream_initialized = true;
    }
}

ifcopenshell::argument_type helper_fn_attribute_type(const express::Base* inst, unsigned index) {
    const ifcopenshell::parameter_type* parameter_type = nullptr;
    if (inst->declaration().as_entity()) {
        parameter_type = inst->declaration().as_entity()->attribute_by_index(index)->type_of_attribute();
        if (inst->declaration().as_entity()->derived()[index]) {
            return ifcopenshell::Argument_DERIVED;
        }
    } else if (inst->declaration().as_type_declaration() && index == 0) {
        parameter_type = inst->declaration().as_type_declaration()->declared_type();
    } else if (inst->declaration().as_enumeration_type() && index == 0) {
        return ifcopenshell::Argument_STRING;
    }

    if (parameter_type == nullptr) {
        return ifcopenshell::Argument_UNKNOWN;
    }
    return ifcopenshell::from_parameter_type(parameter_type);
}

void validate_list_items(const char* name, const void* items, size_t size) {
    if (size > 0 && items == nullptr) {
        throw std::runtime_error(std::string("Parameter '") + name + "' has a null items pointer");
    }
}

template <typename T>
struct capi_is_std_vector : std::false_type {};

template <typename T, typename Alloc>
struct capi_is_std_vector<std::vector<T, Alloc>> : std::true_type {};

template <typename T>
inline constexpr bool capi_is_std_vector_v = capi_is_std_vector<T>::value;

std::string json_escape_string(const std::string& value) {
    std::ostringstream out;
    for (unsigned char ch : value) {
        switch (ch) {
        case '\\': out << "\\\\"; break;
        case '"': out << "\\\""; break;
        case '\b': out << "\\b"; break;
        case '\f': out << "\\f"; break;
        case '\n': out << "\\n"; break;
        case '\r': out << "\\r"; break;
        case '\t': out << "\\t"; break;
        default:
            if (ch < 0x20) {
                out << "\\u"
                    << "00"
                    << "0123456789abcdef"[ch >> 4]
                    << "0123456789abcdef"[ch & 0x0f];
            } else {
                out << static_cast<char>(ch);
            }
        }
    }
    return out.str();
}

std::string json_quote(const std::string& value) {
    return std::string(1, '"') + json_escape_string(value) + '"';
}

std::string instance_to_info_json_string(const express::Base& instance, bool include_identifier);

template <typename T>
std::string value_to_json_string(const T& value, bool include_identifier);

template <typename T>
std::string vector_to_json_string(const std::vector<T>& values, bool include_identifier) {
    std::ostringstream out;
    out << "[";
    for (size_t i = 0; i < values.size(); ++i) {
        if (i != 0) {
            out << ",";
        }
        out << value_to_json_string(values[i], include_identifier);
    }
    out << "]";
    return out.str();
}

std::string reference_or_simple_type_to_json_string(const ifcopenshell::reference_or_simple_type& value, bool include_identifier) {
    if (auto* instance = std::get_if<express::Base>(&value)) {
        return *instance ? instance_to_info_json_string(*instance, include_identifier) : "null";
    }
    auto reference = std::get<ifcopenshell::instance_reference>(value);
    return std::string(R"({"ref":)") + std::to_string(reference.v) + "}";
}

template <typename T>
std::string value_to_json_string(const T& value, bool include_identifier) {
    if constexpr (capi_is_std_vector_v<T>) {
        return vector_to_json_string(value, include_identifier);
    } else if constexpr (std::is_same_v<T, std::string>) {
        return json_quote(value);
    } else if constexpr (std::is_same_v<T, const char*>) {
        return value ? json_quote(value) : "null";
    } else if constexpr (std::is_same_v<T, bool>) {
        return value ? "true" : "false";
    } else if constexpr (std::is_same_v<T, boost::logic::tribool>) {
        if (boost::logic::indeterminate(value)) {
            return json_quote("UNKNOWN");
        }
        return value ? "true" : "false";
    } else if constexpr (std::is_same_v<T, boost::dynamic_bitset<>>) {
        std::string bits;
        boost::to_string(value, bits);
        return json_quote(bits);
    } else if constexpr (std::is_integral_v<T> || std::is_floating_point_v<T>) {
        std::ostringstream out;
        out << value;
        return out.str();
    } else if constexpr (std::is_same_v<T, enumeration_reference>) {
        return json_quote(std::string(value.value()));
    } else if constexpr (std::is_same_v<T, ifcopenshell::reference_or_simple_type>) {
        return reference_or_simple_type_to_json_string(value, include_identifier);
    } else if constexpr (std::is_same_v<T, express::Base>) {
        return value ? instance_to_info_json_string(value, include_identifier) : "null";
    } else if constexpr (
        std::is_same_v<T, empty_aggregate_t> ||
        std::is_same_v<T, empty_aggregate_of_aggregate_t> ||
        std::is_same_v<T, blank> ||
        std::is_same_v<T, derived>) {
        return "null";
    } else {
        throw std::runtime_error("Unsupported IFC value type in JSON serialization");
    }
}

std::string attribute_value_to_json_string(const attribute_value& value, bool include_identifier) {
    return value.apply_visitor([include_identifier](const auto& inner) -> std::string {
        return value_to_json_string(inner, include_identifier);
    });
}

std::string instance_to_info_json_string(const express::Base& instance, bool include_identifier) {
    if (!instance) {
        return "null";
    }
    std::ostringstream out;
    out << "{";
    bool first = true;
    auto emit_field = [&](const std::string& key, const std::string& json_value) {
        if (!first) {
            out << ",";
        }
        first = false;
        out << json_quote(key) << ":" << json_value;
    };

    if (instance.declaration().as_entity()) {
        const auto attributes = instance.declaration().as_entity()->all_attributes();
        for (size_t i = 0; i < attributes.size(); ++i) {
            emit_field(attributes[i]->name(), attribute_value_to_json_string(instance.get_attribute_value(i), include_identifier));
        }
        if (include_identifier) {
            emit_field("id", std::to_string(instance.id()));
        }
    } else {
        emit_field("wrappedValue", attribute_value_to_json_string(instance.get_attribute_value(0), include_identifier));
    }

    emit_field("type", json_quote(instance.declaration().name()));
    out << "}";
    return out.str();
}

std::string unresolved_reference_variant_to_json_string(
    const std::variant<
        ifcopenshell::reference_or_simple_type,
        std::vector<ifcopenshell::reference_or_simple_type>,
        std::vector<std::vector<ifcopenshell::reference_or_simple_type>>>& value,
    bool include_identifier) {
    return std::visit(
        [include_identifier](const auto& inner) -> std::string {
            return value_to_json_string(inner, include_identifier);
        },
        value);
}

std::string unresolved_references_to_json_string(
    const ifcopenshell::unresolved_references& references,
    const ifcopenshell::declaration* declaration) {
    std::ostringstream out;
    out << "[";
    bool first = true;
    for (const auto& entry : references) {
        if (!first) {
            out << ",";
        }
        first = false;
        const auto& mutable_value = entry.first;
        out << "{"
            << R"("entity_name":)" << mutable_value.name_
            << R"(,"attribute_index":)" << static_cast<int>(mutable_value.index_);
        if (declaration && declaration->as_entity() && mutable_value.index_ < declaration->as_entity()->attribute_count()) {
            out << R"(,"attribute_name":)" << json_quote(declaration->as_entity()->attribute_by_index(mutable_value.index_)->name());
        }
        out << R"(,"value":)" << unresolved_reference_variant_to_json_string(entry.second, true) << "}";
    }
    out << "]";
    return out.str();
}

std::string inverses_to_json_string(const ifcopenshell::impl::in_memory_file_storage::entities_by_ref_t& inverses) {
    std::ostringstream out;
    out << "[";
    bool first = true;
    for (const auto& entry : inverses) {
        for (const auto& inverse : entry.second) {
            if (!first) {
                out << ",";
            }
            first = false;
            out << "{"
                << R"("instance_id":)" << entry.first
                << R"(,"instance_type":)" << std::get<0>(inverse.first)
                << R"(,"attribute_index":)" << std::get<1>(inverse.first)
                << R"(,"referencing_ids":)" << vector_to_json_string(inverse.second, true)
                << "}";
        }
    }
    out << "]";
    return out.str();
}

std::string instance_stream_read_instance_json(ifcopenshell::instance_streamer<>* streamer) {
    if (!(*streamer)) {
        return "null";
    }
    auto inst = streamer->read_instance();
    if (!inst) {
        return "null";
    }

    std::ostringstream out;
    out << "{";
    bool first = true;
    auto emit_field = [&](const std::string& key, const std::string& json_value) {
        if (!first) {
            out << ",";
        }
        first = false;
        out << json_quote(key) << ":" << json_value;
    };

    emit_field("id", std::to_string(std::get<0>(*inst)));
    emit_field("type", json_quote(std::get<1>(*inst)->name()));

    const auto* declaration = std::get<1>(*inst);
    const auto& data = std::get<2>(*inst);
    if (declaration->as_entity()) {
        for (size_t i = 0; i < declaration->as_entity()->attribute_count(); ++i) {
            emit_field(
                declaration->as_entity()->attribute_by_index(i)->name(),
                attribute_value_to_json_string(data->get_attribute_value(i), true));
        }
    }

    for (const auto& reference : streamer->references()) {
        std::string key = std::to_string(reference.first.index_);
        if (declaration->as_entity() && reference.first.index_ < declaration->as_entity()->attribute_count()) {
            key = declaration->as_entity()->attribute_by_index(reference.first.index_)->name();
        }
        emit_field(key, unresolved_reference_variant_to_json_string(reference.second, true));
    }

    streamer->references().clear();
    streamer->inverses().clear();
    out << "}";
    return out.str();
}

ifcopenshell_string_t make_string(std::string value) {
    auto owner = std::make_unique<capi_value_owner<std::string>>(std::move(value));
    auto& stored = owner->value;
    return ifcopenshell_string_t{stored.data(), stored.size(), false, owner.release()};
}

ifcopenshell_string_t make_static_string(const char* value) {
    if (value == nullptr) {
        return ifcopenshell_string_t{nullptr, 0, false, nullptr};
    }
    return ifcopenshell_string_t{const_cast<char*>(value), std::strlen(value), false, nullptr};
}

template <typename T>
void set_instance_argument(express::Base* instance, size_t index, const T& value) {
    instance->set_attribute_value(index, value);
}

void set_instance_argument(express::Base* instance, size_t index, express::Base* value) {
    if (value == nullptr) {
        instance->unset_attribute_value(index);
    } else {
        instance->set_attribute_value(index, *value);
    }
}

void set_instance_argument(express::Base* instance, size_t index, std::vector<express::Base>* value) {
    if (value == nullptr) {
        instance->unset_attribute_value(index);
    } else {
        instance->set_attribute_value(index, *value);
    }
}

void unset_instance_argument(express::Base* instance, size_t index) {
    instance->unset_attribute_value(index);
}

void set_instance_attribute_from_attribute_value(express::Base* instance, size_t index, const attribute_value& value) {
    value.apply_visitor([&](const auto& inner) -> void {
        using T = std::decay_t<decltype(inner)>;
        if constexpr (std::is_same_v<T, derived>) {
            throw std::runtime_error("Cannot assign a derived attribute sentinel.");
        } else if constexpr (std::is_same_v<T, empty_aggregate_t> ||
                              std::is_same_v<T, empty_aggregate_of_aggregate_t>) {
            // Empty-aggregate sentinels arise when reading absent aggregate
            // values; assigning them is equivalent to unsetting the attribute.
            unset_instance_argument(instance, index);
        } else {
            set_instance_argument(instance, index, inner);
        }
    });
}
} // namespace

namespace ifcopenshell {
namespace capi {

void set_feature(const std::string& name, bool value) {
    if (name == "use_attribute_value_derived") {
        feature_use_attribute_value_derived = value;
        return;
    }
    throw std::runtime_error("Invalid feature specification");
}

bool get_feature(const std::string& name) {
    if (name == "use_attribute_value_derived") {
        return feature_use_attribute_value_derived;
    }
    throw std::runtime_error("Invalid feature specification");
}

std::string get_log() {
    ensure_log_stream_initialized();
    std::string log = ifcopenshell_log_stream.str();
    ifcopenshell_log_stream.str("");
    ifcopenshell_log_stream.clear();
    return log;
}

void turn_on_detailed_logging() {
    logger::set_output(&std::cout, &std::cout);
    logger::verbosity(logger::LOG_DEBUG);
}

void turn_off_detailed_logging() {
    ensure_log_stream_initialized();
    logger::set_output(nullptr, &ifcopenshell_log_stream);
    logger::verbosity(logger::LOG_WARNING);
}

void set_log_format_json() {
    ensure_log_stream_initialized();
    ifcopenshell_log_stream.str("");
    ifcopenshell_log_stream.clear();
    logger::output_format(logger::FMT_JSON);
}

void set_log_format_text() {
    ensure_log_stream_initialized();
    ifcopenshell_log_stream.str("");
    ifcopenshell_log_stream.clear();
    logger::output_format(logger::FMT_PLAIN);
}

std::string get_info_json(const express::Base& instance, bool include_identifier) {
    return instance_to_info_json_string(instance, include_identifier);
}

std::string streamer_references(ifcopenshell::instance_streamer<>* streamer) {
    return unresolved_references_to_json_string(streamer->references(), nullptr);
}

std::string streamer_inverses(ifcopenshell::instance_streamer<>* streamer) {
    return inverses_to_json_string(streamer->inverses());
}

std::string streamer_read_instance_json(ifcopenshell::instance_streamer<>* streamer) {
    return instance_stream_read_instance_json(streamer);
}

void unset_instance_argument_value(express::Base& instance, size_t index) {
    instance.set_attribute_value(index, blank{});
}

void unset_instance_argument(express::Base& instance, size_t index) {
    instance.set_attribute_value(index, blank{});
}

ifcopenshell::argument_type instance_attribute_type(const express::Base& instance, unsigned index) {
    return ::helper_fn_attribute_type(&instance, index);
}

void set_instance_attribute_from_attribute_value(express::Base& instance, size_t index, const attribute_value& value) {
    ::set_instance_attribute_from_attribute_value(&instance, index, value);
}

void set_instance_argument_bool(express::Base& instance, size_t index, bool value) {
    set_instance_argument(&instance, index, value);
}

void set_instance_argument_int32(express::Base& instance, size_t index, int value) {
    set_instance_argument(&instance, index, value);
}

void set_instance_argument_double(express::Base& instance, size_t index, double value) {
    set_instance_argument(&instance, index, value);
}

void set_instance_argument_string(express::Base& instance, size_t index, const std::string& value) {
    set_instance_argument(&instance, index, value);
}

void set_instance_argument_instance(express::Base& instance, size_t index, express::Base* value) {
    set_instance_argument(&instance, index, value);
}

void set_instance_argument_instance_list(express::Base& instance, size_t index, std::vector<express::Base>* value) {
    set_instance_argument(&instance, index, value);
}

void set_instance_argument_int32_list(express::Base& instance, size_t index, const std::vector<int>& value) {
    set_instance_argument(&instance, index, value);
}

void set_instance_argument_double_list(express::Base& instance, size_t index, const std::vector<double>& value) {
    set_instance_argument(&instance, index, value);
}

void set_instance_argument_string_list(express::Base& instance, size_t index, const std::vector<std::string>& value) {
    set_instance_argument(&instance, index, value);
}

void set_instance_argument_int32_list_list(express::Base& instance, size_t index, const std::vector<std::vector<int>>& value) {
    set_instance_argument(&instance, index, value);
}

void set_instance_argument_double_list_list(express::Base& instance, size_t index, const std::vector<std::vector<double>>& value) {
    set_instance_argument(&instance, index, value);
}

void set_instance_argument_logical(express::Base& instance, size_t index, int value) {
    ifcopenshell::argument_type arg_type = helper_fn_attribute_type(&instance, static_cast<unsigned>(index));
    if (arg_type != ifcopenshell::Argument_LOGICAL) {
        throw ifcopenshell::exception("Attribute not set");
    }
    boost::logic::tribool logical_value;
    if (value == 0) {
        logical_value = false;
    } else if (value == 1) {
        logical_value = true;
    } else if (value == -1) {
        logical_value = boost::logic::indeterminate;
    } else {
        throw ifcopenshell::exception("Logical value must be -1, 0, or 1");
    }
    set_instance_argument(&instance, index, logical_value);
}

void set_instance_argument_aggregate_of_aggregate_of_entity_instance(
    express::Base& instance,
    size_t index,
    const std::vector<std::vector<int>>& value
) {
    ifcopenshell::argument_type arg_type = helper_fn_attribute_type(&instance, static_cast<unsigned>(index));
    if (arg_type != ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
        throw ifcopenshell::exception("Attribute not set");
    }
    if (instance.file() == nullptr) {
        throw ifcopenshell::exception("Instance is not attached to a file.");
    }
    std::vector<std::vector<express::Base>> aggregate;
    for (const auto& group : value) {
        std::vector<express::Base> instances;
        instances.reserve(group.size());
        for (int identifier : group) {
            auto resolved = instance.file()->instance_by_id(identifier);
            if (!resolved) {
                throw ifcopenshell::exception("Unable to resolve instance id " + std::to_string(identifier));
            }
            instances.push_back(resolved);
        }
        aggregate.push_back(std::move(instances));
    }
    set_instance_argument(&instance, index, aggregate);
}

void set_instance_argument_enumeration(
    express::Base& instance,
    size_t index,
    const ifcopenshell::enumeration_type* enumeration,
    size_t enumeration_index
) {
    set_instance_argument(&instance, index, enumeration_reference(enumeration, enumeration_index));
}

bool set_instance_argument_enumeration_by_name(express::Base& instance, size_t index, const std::string& value) {
    auto* entity_decl = instance.declaration().as_entity();
    if (entity_decl == nullptr) {
        return false;
    }
    const auto attrs = entity_decl->all_attributes();
    if (index >= attrs.size()) {
        return false;
    }
    const ifcopenshell::parameter_type* parameter_type = attrs[index]->type_of_attribute();
    const ifcopenshell::enumeration_type* enumeration = nullptr;
    while (parameter_type != nullptr) {
        auto* named = parameter_type->as_named_type();
        if (named == nullptr) {
            break;
        }
        auto* declaration = named->declared_type();
        if ((enumeration = declaration->as_enumeration_type()) != nullptr) {
            break;
        }
        auto* type_declaration = declaration->as_type_declaration();
        if (type_declaration == nullptr) {
            break;
        }
        parameter_type = type_declaration->declared_type();
    }
    if (enumeration == nullptr) {
        return false;
    }
    const auto& items = enumeration->enumeration_items();
    auto it = std::find(items.begin(), items.end(), value);
    if (it == items.end()) {
        throw ifcopenshell::exception("'" + value + "' is not a valid value for enumeration " + enumeration->name());
    }
    set_instance_argument(&instance, index, enumeration_reference(enumeration, static_cast<size_t>(std::distance(items.begin(), it))));
    return true;
}

} // namespace capi
} // namespace ifcopenshell

template <typename Value>
static ifcopenshell_instance_list_t make_instance_list(const std::vector<Value>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_instance_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_instance_t{express::Base(values[i])};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_instance_list_t{items, values.size()};
}

template <typename = void>
static std::vector<express::Base> to_cpp_instance_list(const ifcopenshell_instance_list_t* values) {
    validate_list_items("instance_list", values->items, values->size);
    std::vector<express::Base> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->value);
    }
    return result;
}

template <typename Item>
static ifcopenshell_geom_svgfill_polygon_list_t make_geom_svgfill_polygon_list(const std::vector<Item*>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_geom_svgfill_polygon_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_geom_svgfill_polygon_t{const_cast<svgfill::polygon_2*>(values[i]), false};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_geom_svgfill_polygon_list_t{items, values.size()};
}

template <typename Item>
static ifcopenshell_geom_svgfill_polygon_list_t make_geom_svgfill_polygon_list(std::vector<std::unique_ptr<Item>> values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_geom_svgfill_polygon_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_geom_svgfill_polygon_t{values[i].release(), true};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_geom_svgfill_polygon_list_t{items, values.size()};
}

template <typename = void>
static std::vector<const svgfill::polygon_2*> to_cpp_geom_svgfill_polygon_list(const ifcopenshell_geom_svgfill_polygon_list_t* values) {
    validate_list_items("geom_svgfill_polygon_list", values->items, values->size);
    std::vector<const svgfill::polygon_2*> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr || item->ptr == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->ptr);
    }
    return result;
}

template <typename Item>
static ifcopenshell_geom_conversion_result_shape_list_t make_geom_conversion_result_shape_list(const std::vector<Item*>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_geom_conversion_result_shape_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_geom_conversion_result_shape_t{const_cast<IfcGeom::ConversionResultShape*>(values[i]), false};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_geom_conversion_result_shape_list_t{items, values.size()};
}

template <typename Item>
static ifcopenshell_geom_conversion_result_shape_list_t make_geom_conversion_result_shape_list(std::vector<std::unique_ptr<Item>> values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_geom_conversion_result_shape_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_geom_conversion_result_shape_t{values[i].release(), true};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_geom_conversion_result_shape_list_t{items, values.size()};
}

template <typename = void>
static std::vector<const IfcGeom::ConversionResultShape*> to_cpp_geom_conversion_result_shape_list(const ifcopenshell_geom_conversion_result_shape_list_t* values) {
    validate_list_items("geom_conversion_result_shape_list", values->items, values->size);
    std::vector<const IfcGeom::ConversionResultShape*> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr || item->ptr == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->ptr);
    }
    return result;
}

template <typename Item>
static ifcopenshell_declaration_list_t make_declaration_list(const std::vector<Item*>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_declaration_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_declaration_t{const_cast<ifcopenshell::declaration*>(values[i]), false};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_declaration_list_t{items, values.size()};
}

template <typename Item>
static ifcopenshell_declaration_list_t make_declaration_list(std::vector<std::unique_ptr<Item>> values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_declaration_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_declaration_t{values[i].release(), true};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_declaration_list_t{items, values.size()};
}

template <typename = void>
static std::vector<const ifcopenshell::declaration*> to_cpp_declaration_list(const ifcopenshell_declaration_list_t* values) {
    validate_list_items("declaration_list", values->items, values->size);
    std::vector<const ifcopenshell::declaration*> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr || item->ptr == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->ptr);
    }
    return result;
}

template <typename Item>
static ifcopenshell_entity_list_t make_entity_list(const std::vector<Item*>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_entity_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_entity_t{const_cast<ifcopenshell::entity*>(values[i]), false};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_entity_list_t{items, values.size()};
}

template <typename Item>
static ifcopenshell_entity_list_t make_entity_list(std::vector<std::unique_ptr<Item>> values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_entity_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_entity_t{values[i].release(), true};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_entity_list_t{items, values.size()};
}

template <typename = void>
static std::vector<const ifcopenshell::entity*> to_cpp_entity_list(const ifcopenshell_entity_list_t* values) {
    validate_list_items("entity_list", values->items, values->size);
    std::vector<const ifcopenshell::entity*> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr || item->ptr == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->ptr);
    }
    return result;
}

template <typename Item>
static ifcopenshell_enumeration_list_t make_enumeration_list(const std::vector<Item*>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_enumeration_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_enumeration_t{const_cast<ifcopenshell::enumeration_type*>(values[i]), false};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_enumeration_list_t{items, values.size()};
}

template <typename Item>
static ifcopenshell_enumeration_list_t make_enumeration_list(std::vector<std::unique_ptr<Item>> values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_enumeration_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_enumeration_t{values[i].release(), true};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_enumeration_list_t{items, values.size()};
}

template <typename = void>
static std::vector<const ifcopenshell::enumeration_type*> to_cpp_enumeration_list(const ifcopenshell_enumeration_list_t* values) {
    validate_list_items("enumeration_list", values->items, values->size);
    std::vector<const ifcopenshell::enumeration_type*> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr || item->ptr == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->ptr);
    }
    return result;
}

template <typename Item>
static ifcopenshell_select_type_list_t make_select_type_list(const std::vector<Item*>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_select_type_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_select_type_t{const_cast<ifcopenshell::select_type*>(values[i]), false};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_select_type_list_t{items, values.size()};
}

template <typename Item>
static ifcopenshell_select_type_list_t make_select_type_list(std::vector<std::unique_ptr<Item>> values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_select_type_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_select_type_t{values[i].release(), true};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_select_type_list_t{items, values.size()};
}

template <typename = void>
static std::vector<const ifcopenshell::select_type*> to_cpp_select_type_list(const ifcopenshell_select_type_list_t* values) {
    validate_list_items("select_type_list", values->items, values->size);
    std::vector<const ifcopenshell::select_type*> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr || item->ptr == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->ptr);
    }
    return result;
}

template <typename Item>
static ifcopenshell_type_declaration_list_t make_type_declaration_list(const std::vector<Item*>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_type_declaration_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_type_declaration_t{const_cast<ifcopenshell::type_declaration*>(values[i]), false};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_type_declaration_list_t{items, values.size()};
}

template <typename Item>
static ifcopenshell_type_declaration_list_t make_type_declaration_list(std::vector<std::unique_ptr<Item>> values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_type_declaration_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_type_declaration_t{values[i].release(), true};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_type_declaration_list_t{items, values.size()};
}

template <typename = void>
static std::vector<const ifcopenshell::type_declaration*> to_cpp_type_declaration_list(const ifcopenshell_type_declaration_list_t* values) {
    validate_list_items("type_declaration_list", values->items, values->size);
    std::vector<const ifcopenshell::type_declaration*> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr || item->ptr == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->ptr);
    }
    return result;
}

template <typename Item>
static ifcopenshell_attribute_list_t make_attribute_list(const std::vector<Item*>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_attribute_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_attribute_t{const_cast<ifcopenshell::attribute*>(values[i]), false};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_attribute_list_t{items, values.size()};
}

template <typename Item>
static ifcopenshell_attribute_list_t make_attribute_list(std::vector<std::unique_ptr<Item>> values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_attribute_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_attribute_t{values[i].release(), true};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_attribute_list_t{items, values.size()};
}

template <typename = void>
static std::vector<const ifcopenshell::attribute*> to_cpp_attribute_list(const ifcopenshell_attribute_list_t* values) {
    validate_list_items("attribute_list", values->items, values->size);
    std::vector<const ifcopenshell::attribute*> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr || item->ptr == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->ptr);
    }
    return result;
}

template <typename Item>
static ifcopenshell_inverse_attribute_list_t make_inverse_attribute_list(const std::vector<Item*>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_inverse_attribute_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_inverse_attribute_t{const_cast<ifcopenshell::inverse_attribute*>(values[i]), false};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_inverse_attribute_list_t{items, values.size()};
}

template <typename Item>
static ifcopenshell_inverse_attribute_list_t make_inverse_attribute_list(std::vector<std::unique_ptr<Item>> values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_inverse_attribute_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_inverse_attribute_t{values[i].release(), true};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_inverse_attribute_list_t{items, values.size()};
}

template <typename = void>
static std::vector<const ifcopenshell::inverse_attribute*> to_cpp_inverse_attribute_list(const ifcopenshell_inverse_attribute_list_t* values) {
    validate_list_items("inverse_attribute_list", values->items, values->size);
    std::vector<const ifcopenshell::inverse_attribute*> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr || item->ptr == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->ptr);
    }
    return result;
}

template <typename Item>
static ifcopenshell_geom_taxonomy_style_list_t make_geom_taxonomy_style_list(const std::vector<std::shared_ptr<Item>>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_geom_taxonomy_style_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_geom_taxonomy_style_t{values[i]};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_geom_taxonomy_style_list_t{items, values.size()};
}

template <typename = void>
static std::vector<std::shared_ptr<ifcopenshell::geometry::taxonomy::style>> to_cpp_geom_taxonomy_style_list(const ifcopenshell_geom_taxonomy_style_list_t* values) {
    validate_list_items("geom_taxonomy_style_list", values->items, values->size);
    std::vector<std::shared_ptr<ifcopenshell::geometry::taxonomy::style>> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->ptr);
    }
    return result;
}

template <typename Item>
static ifcopenshell_geom_taxonomy_item_list_t make_geom_taxonomy_item_list(const std::vector<std::shared_ptr<Item>>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_geom_taxonomy_item_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_geom_taxonomy_item_t{values[i]};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_geom_taxonomy_item_list_t{items, values.size()};
}

template <typename = void>
static std::vector<std::shared_ptr<ifcopenshell::geometry::taxonomy::item>> to_cpp_geom_taxonomy_item_list(const ifcopenshell_geom_taxonomy_item_list_t* values) {
    validate_list_items("geom_taxonomy_item_list", values->items, values->size);
    std::vector<std::shared_ptr<ifcopenshell::geometry::taxonomy::item>> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->ptr);
    }
    return result;
}

template <typename Item>
static ifcopenshell_geom_element_list_t make_geom_element_list(const std::vector<Item*>& values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_geom_element_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_geom_element_t{const_cast<IfcGeom::Element*>(values[i]), false};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_geom_element_list_t{items, values.size()};
}

template <typename Item>
static ifcopenshell_geom_element_list_t make_geom_element_list(std::vector<std::unique_ptr<Item>> values) {
    auto** items = values.empty() ? nullptr : new ifcopenshell_geom_element_t*[values.size()];
    size_t initialized = 0;
    try {
        for (size_t i = 0; i < values.size(); ++i) {
            items[i] = new ifcopenshell_geom_element_t{values[i].release(), true};
            ++initialized;
        }
    } catch (...) {
        for (size_t j = 0; j < initialized; ++j) { delete items[j]; }
        delete[] items;
        throw;
    }
    return ifcopenshell_geom_element_list_t{items, values.size()};
}

template <typename = void>
static std::vector<const IfcGeom::Element*> to_cpp_geom_element_list(const ifcopenshell_geom_element_list_t* values) {
    validate_list_items("geom_element_list", values->items, values->size);
    std::vector<const IfcGeom::Element*> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        auto* item = values->items[i];
        if (item == nullptr || item->ptr == nullptr) {
            throw std::runtime_error("handle_list contains an invalid handle");
        }
        result.push_back(item->ptr);
    }
    return result;
}
template <typename = void>
static ifcopenshell_instance_list_list_t make_instance_list_list(const std::vector<std::vector<express::Base>>& values) {
    auto* items = values.empty() ? nullptr : new ifcopenshell_instance_list_t[values.size()];
    for (size_t i = 0; i < values.size(); ++i) {
        items[i] = make_instance_list(values[i]);
    }
    return ifcopenshell_instance_list_list_t{items, values.size()};
}

template <typename = void>
static std::vector<std::vector<express::Base>> to_cpp_instance_list_list(const ifcopenshell_instance_list_list_t* values) {
    validate_list_items("instance_list_list", values->items, values->size);
    std::vector<std::vector<express::Base>> result;
    result.reserve(values->size);
    for (size_t i = 0; i < values->size; ++i) {
        result.push_back(to_cpp_instance_list(&values->items[i]));
    }
    return result;
}

void ifcopenshell_buffer_owner_destroy(void** owner) {
    if (owner == nullptr || *owner == nullptr) {
        return;
    }
    delete static_cast<capi_buffer_owner*>(*owner);
    *owner = nullptr;
}

void ifcopenshell_string_destroy(ifcopenshell_string_t* value) {
    if (value == nullptr) {
        return;
    }
    if (value->owner != nullptr) {
        ifcopenshell_buffer_owner_destroy(&value->owner);
    } else if (value->owned && value->data != nullptr) {
        delete[] value->data;
    }
    value->data = nullptr;
    value->size = 0;
    value->owned = false;
    value->owner = nullptr;
}

void ifcopenshell_string_list_destroy(ifcopenshell_string_list_t* value) {
    if (value == nullptr) {
        return;
    }
    if (value->owner == nullptr) {
        value->items = nullptr;
        value->size = 0;
        return;
    }

    ifcopenshell_buffer_owner_destroy(&value->owner);
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_int32_list_destroy(ifcopenshell_int32_list_t* value) {
    if (value == nullptr) {
        return;
    }
    if (value->owner == nullptr) {
        value->items = nullptr;
        value->size = 0;
        return;
    }

    ifcopenshell_buffer_owner_destroy(&value->owner);
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_double_list_destroy(ifcopenshell_double_list_t* value) {
    if (value == nullptr) {
        return;
    }
    if (value->owner == nullptr) {
        value->items = nullptr;
        value->size = 0;
        return;
    }

    ifcopenshell_buffer_owner_destroy(&value->owner);
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_bool_list_destroy(ifcopenshell_bool_list_t* value) {
    if (value == nullptr) {
        return;
    }
    if (value->owner == nullptr) {
        value->items = nullptr;
        value->size = 0;
        return;
    }

    ifcopenshell_buffer_owner_destroy(&value->owner);
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_uint32_list_destroy(ifcopenshell_uint32_list_t* value) {
    if (value == nullptr) {
        return;
    }
    if (value->owner == nullptr) {
        value->items = nullptr;
        value->size = 0;
        return;
    }

    ifcopenshell_buffer_owner_destroy(&value->owner);
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_int32_list_list_destroy(ifcopenshell_int32_list_list_t* value) {
    if (value == nullptr) {
        return;
    }
    if (value->owner == nullptr) {
        value->items = nullptr;
        value->size = 0;
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        ifcopenshell_int32_list_destroy(&value->items[i]);
    }
    ifcopenshell_buffer_owner_destroy(&value->owner);
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_int32_list_list_list_destroy(ifcopenshell_int32_list_list_list_t* value) {
    if (value == nullptr) {
        return;
    }
    if (value->owner == nullptr) {
        value->items = nullptr;
        value->size = 0;
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        ifcopenshell_int32_list_list_destroy(&value->items[i]);
    }
    ifcopenshell_buffer_owner_destroy(&value->owner);
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_uint8_list_destroy(ifcopenshell_uint8_list_t* value) {
    if (value == nullptr) {
        return;
    }
    if (value->owner == nullptr) {
        value->items = nullptr;
        value->size = 0;
        return;
    }

    ifcopenshell_buffer_owner_destroy(&value->owner);
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_double_list_list_destroy(ifcopenshell_double_list_list_t* value) {
    if (value == nullptr) {
        return;
    }
    if (value->owner == nullptr) {
        value->items = nullptr;
        value->size = 0;
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        ifcopenshell_double_list_destroy(&value->items[i]);
    }
    ifcopenshell_buffer_owner_destroy(&value->owner);
    value->items = nullptr;
    value->size = 0;
}

template <typename = void>
static ifcopenshell_string_list_t make_string_list(std::vector<std::string> values) {
    struct owner_type final : capi_buffer_owner {
        explicit owner_type(std::vector<std::string> source) : values(std::move(source)) {
            items.reserve(values.size());
            for (auto& value : values) {
                items.push_back(ifcopenshell_string_t{value.data(), value.size(), false, nullptr});
            }
        }
        std::vector<std::string> values;
        std::vector<ifcopenshell_string_t> items;
    };
    auto owner = std::make_unique<owner_type>(std::move(values));
    auto* items = owner->items.empty() ? nullptr : owner->items.data();
    const auto size = owner->items.size();
    return ifcopenshell_string_list_t{items, size, owner.release()};
}

template <typename = void>
static std::vector<std::string> to_cpp_string_list(const ifcopenshell_string_list_t* value) {
    validate_list_items("string_list", value->items, value->size);
    std::vector<std::string> result;
    result.reserve(value->size);
    for (size_t i = 0; i < value->size; ++i) {
        const auto& item = value->items[i];
        if (item.data == nullptr && item.size > 0) {
            throw std::runtime_error("string_list contains a null string buffer");
        }
        result.emplace_back(item.data == nullptr ? "" : item.data, item.size);
    }
    return result;
}

template <typename = void>
static ifcopenshell_int32_list_t make_int32_list(std::vector<int> values) {
    auto owner = std::make_unique<capi_value_owner<std::vector<int>>>(std::move(values));
    auto& stored = owner->value;
    auto* items = stored.empty() ? nullptr : reinterpret_cast<int32_t*>(stored.data());
    const auto size = stored.size();
    return ifcopenshell_int32_list_t{items, size, owner.release()};
}

template <typename = void>
static std::vector<int> to_cpp_int32_list(const ifcopenshell_int32_list_t* value) {
    validate_list_items("int32_list", value->items, value->size);
    if (value->size == 0) {
        return {};
    }
    return std::vector<int>(value->items, value->items + value->size);
}

template <typename = void>
static ifcopenshell_double_list_t make_double_list(std::vector<double> values) {
    auto owner = std::make_unique<capi_value_owner<std::vector<double>>>(std::move(values));
    auto& stored = owner->value;
    auto* items = stored.empty() ? nullptr : stored.data();
    const auto size = stored.size();
    return ifcopenshell_double_list_t{items, size, owner.release()};
}

template <typename = void>
static std::vector<double> to_cpp_double_list(const ifcopenshell_double_list_t* value) {
    validate_list_items("double_list", value->items, value->size);
    if (value->size == 0) {
        return {};
    }
    return std::vector<double>(value->items, value->items + value->size);
}

template <typename = void>
static ifcopenshell_bool_list_t make_bool_list(std::vector<bool> values) {
    auto owner = std::make_unique<capi_array_owner<bool>>(values.size());
    for (size_t i = 0; i < values.size(); ++i) {
        owner->values[i] = values[i];
    }
    auto* items = owner->values.get();
    const auto size = values.size();
    return ifcopenshell_bool_list_t{items, size, owner.release()};
}

template <typename = void>
static std::vector<bool> to_cpp_bool_list(const ifcopenshell_bool_list_t* value) {
    validate_list_items("bool_list", value->items, value->size);
    std::vector<bool> result;
    result.reserve(value->size);
    for (size_t i = 0; i < value->size; ++i) {
        result.push_back(value->items[i]);
    }
    return result;
}

template <typename = void>
static ifcopenshell_uint32_list_t make_uint32_list(std::vector<unsigned int> values) {
    auto owner = std::make_unique<capi_value_owner<std::vector<unsigned int>>>(std::move(values));
    auto& stored = owner->value;
    auto* items = stored.empty() ? nullptr : reinterpret_cast<uint32_t*>(stored.data());
    const auto size = stored.size();
    return ifcopenshell_uint32_list_t{items, size, owner.release()};
}

template <typename = void>
static std::vector<unsigned int> to_cpp_uint32_list(const ifcopenshell_uint32_list_t* value) {
    validate_list_items("uint32_list", value->items, value->size);
    if (value->size == 0) {
        return {};
    }
    return std::vector<unsigned int>(value->items, value->items + value->size);
}

template <typename = void>
static ifcopenshell_int32_list_list_t make_int32_list_list(std::vector<std::vector<int>> values) {
    auto owner = std::make_unique<capi_value_owner<std::vector<ifcopenshell_int32_list_t>>>(std::vector<ifcopenshell_int32_list_t>{});
    auto& items = owner->value;
    items.reserve(values.size());
    try {
        for (auto& value : values) {
            items.push_back(make_int32_list(std::move(value)));
        }
    } catch (...) {
        for (auto& item : items) {
            ifcopenshell_int32_list_destroy(&item);
        }
        throw;
    }
    auto* data = items.empty() ? nullptr : items.data();
    const auto size = items.size();
    return ifcopenshell_int32_list_list_t{data, size, owner.release()};
}

template <typename = void>
static std::vector<std::vector<int>> to_cpp_int32_list_list(const ifcopenshell_int32_list_list_t* value) {
    validate_list_items("int32_list_list", value->items, value->size);
    std::vector<std::vector<int>> result;
    result.reserve(value->size);
    for (size_t i = 0; i < value->size; ++i) {
        result.push_back(to_cpp_int32_list(&value->items[i]));
    }
    return result;
}

template <typename = void>
static ifcopenshell_int32_list_list_list_t make_int32_list_list_list(std::vector<std::vector<std::vector<int>>> values) {
    auto owner = std::make_unique<capi_value_owner<std::vector<ifcopenshell_int32_list_list_t>>>(std::vector<ifcopenshell_int32_list_list_t>{});
    auto& items = owner->value;
    items.reserve(values.size());
    try {
        for (auto& value : values) {
            items.push_back(make_int32_list_list(std::move(value)));
        }
    } catch (...) {
        for (auto& item : items) {
            ifcopenshell_int32_list_list_destroy(&item);
        }
        throw;
    }
    auto* data = items.empty() ? nullptr : items.data();
    const auto size = items.size();
    return ifcopenshell_int32_list_list_list_t{data, size, owner.release()};
}

template <typename = void>
static std::vector<std::vector<std::vector<int>>> to_cpp_int32_list_list_list(const ifcopenshell_int32_list_list_list_t* value) {
    validate_list_items("int32_list_list_list", value->items, value->size);
    std::vector<std::vector<std::vector<int>>> result;
    result.reserve(value->size);
    for (size_t i = 0; i < value->size; ++i) {
        result.push_back(to_cpp_int32_list_list(&value->items[i]));
    }
    return result;
}

template <typename = void>
static ifcopenshell_uint8_list_t make_uint8_list(std::vector<uint8_t> values) {
    auto owner = std::make_unique<capi_value_owner<std::vector<uint8_t>>>(std::move(values));
    auto& stored = owner->value;
    auto* items = stored.empty() ? nullptr : stored.data();
    const auto size = stored.size();
    return ifcopenshell_uint8_list_t{items, size, owner.release()};
}

template <typename = void>
static std::vector<uint8_t> to_cpp_uint8_list(const ifcopenshell_uint8_list_t* value) {
    validate_list_items("uint8_list", value->items, value->size);
    if (value->size == 0) {
        return {};
    }
    return std::vector<uint8_t>(value->items, value->items + value->size);
}

template <typename = void>
static ifcopenshell_double_list_list_t make_double_list_list(std::vector<std::vector<double>> values) {
    auto owner = std::make_unique<capi_value_owner<std::vector<ifcopenshell_double_list_t>>>(std::vector<ifcopenshell_double_list_t>{});
    auto& items = owner->value;
    items.reserve(values.size());
    try {
        for (auto& value : values) {
            items.push_back(make_double_list(std::move(value)));
        }
    } catch (...) {
        for (auto& item : items) {
            ifcopenshell_double_list_destroy(&item);
        }
        throw;
    }
    auto* data = items.empty() ? nullptr : items.data();
    const auto size = items.size();
    return ifcopenshell_double_list_list_t{data, size, owner.release()};
}

template <typename = void>
static std::vector<std::vector<double>> to_cpp_double_list_list(const ifcopenshell_double_list_list_t* value) {
    validate_list_items("double_list_list", value->items, value->size);
    std::vector<std::vector<double>> result;
    result.reserve(value->size);
    for (size_t i = 0; i < value->size; ++i) {
        result.push_back(to_cpp_double_list(&value->items[i]));
    }
    return result;
}



void ifcopenshell_clear_error(void) {
    ifcopenshell::capi::g_last_error_kind = IFCOPENSHELL_ERROR_NONE;
    ifcopenshell::capi::g_last_error_code = IFCOPENSHELL_ERROR_CODE_NONE;
    ifcopenshell::capi::g_last_error.clear();
}

const char* ifcopenshell_last_error_message(void) {
    return ifcopenshell::capi::g_last_error.c_str();
}

int ifcopenshell_last_error_kind(void) {
    return ifcopenshell::capi::g_last_error_kind;
}

int ifcopenshell_last_error_code(void) {
    return ifcopenshell::capi::g_last_error_code;
}

void ifcopenshell_file_destroy(ifcopenshell_file_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_instance_streamer_destroy(ifcopenshell_instance_streamer_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_instance_destroy(ifcopenshell_instance_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_header_destroy(ifcopenshell_header_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_file_description_destroy(ifcopenshell_file_description_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_file_name_destroy(ifcopenshell_file_name_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_file_schema_destroy(ifcopenshell_file_schema_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_declaration_destroy(ifcopenshell_declaration_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_type_declaration_destroy(ifcopenshell_type_declaration_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_select_type_destroy(ifcopenshell_select_type_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_schema_destroy(ifcopenshell_schema_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_enumeration_destroy(ifcopenshell_enumeration_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_parameter_type_destroy(ifcopenshell_parameter_type_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_named_type_destroy(ifcopenshell_named_type_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_simple_type_destroy(ifcopenshell_simple_type_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_aggregation_type_destroy(ifcopenshell_aggregation_type_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_entity_destroy(ifcopenshell_entity_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_attribute_destroy(ifcopenshell_attribute_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_inverse_attribute_destroy(ifcopenshell_inverse_attribute_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_parse_attribute_value_destroy(ifcopenshell_parse_attribute_value_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_parse_instance_list_destroy(ifcopenshell_parse_instance_list_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_geom_iterator_destroy(ifcopenshell_geom_iterator_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_settings_destroy(ifcopenshell_geom_settings_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_serializer_settings_destroy(ifcopenshell_geom_serializer_settings_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_geometry_serializer_destroy(ifcopenshell_geom_geometry_serializer_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_serializer_destroy(ifcopenshell_geom_serializer_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_buffer_destroy(ifcopenshell_geom_buffer_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_tree_destroy(ifcopenshell_geom_tree_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_tree_clash_list_destroy(ifcopenshell_geom_tree_clash_list_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_tree_clash_destroy(ifcopenshell_geom_tree_clash_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_tree_ray_intersection_list_destroy(ifcopenshell_geom_tree_ray_intersection_list_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_tree_ray_intersection_destroy(ifcopenshell_geom_tree_ray_intersection_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_transformation_destroy(ifcopenshell_geom_transformation_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_element_destroy(ifcopenshell_geom_element_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_brep_element_destroy(ifcopenshell_geom_brep_element_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_triangulation_element_destroy(ifcopenshell_geom_triangulation_element_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_serialized_element_destroy(ifcopenshell_geom_serialized_element_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_triangulation_destroy(ifcopenshell_geom_triangulation_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_geom_brep_representation_destroy(ifcopenshell_geom_brep_representation_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_geom_serialization_destroy(ifcopenshell_geom_serialization_t* handle) {
    if (handle == nullptr) {
        return;
    }
    delete handle;
}

void ifcopenshell_geom_conversion_result_shape_destroy(ifcopenshell_geom_conversion_result_shape_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_opaque_number_destroy(ifcopenshell_geom_opaque_number_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_svgfill_polygon_destroy(ifcopenshell_geom_svgfill_polygon_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_function_item_evaluator_destroy(ifcopenshell_geom_function_item_evaluator_t* handle) {
    if (handle == nullptr) {
        return;
    }
    if (handle->owned && handle->ptr) { delete handle->ptr; }
    delete handle;
}

void ifcopenshell_geom_taxonomy_item_destroy(ifcopenshell_geom_taxonomy_item_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_matrix4_destroy(ifcopenshell_geom_taxonomy_matrix4_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_point3_destroy(ifcopenshell_geom_taxonomy_point3_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_direction3_destroy(ifcopenshell_geom_taxonomy_direction3_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_style_destroy(ifcopenshell_geom_taxonomy_style_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_colour_destroy(ifcopenshell_geom_taxonomy_colour_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_line_destroy(ifcopenshell_geom_taxonomy_line_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_circle_destroy(ifcopenshell_geom_taxonomy_circle_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_ellipse_destroy(ifcopenshell_geom_taxonomy_ellipse_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_bspline_curve_destroy(ifcopenshell_geom_taxonomy_bspline_curve_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_offset_curve_destroy(ifcopenshell_geom_taxonomy_offset_curve_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_edge_destroy(ifcopenshell_geom_taxonomy_edge_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_loop_destroy(ifcopenshell_geom_taxonomy_loop_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_face_destroy(ifcopenshell_geom_taxonomy_face_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_shell_destroy(ifcopenshell_geom_taxonomy_shell_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_solid_destroy(ifcopenshell_geom_taxonomy_solid_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_plane_destroy(ifcopenshell_geom_taxonomy_plane_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_cylinder_destroy(ifcopenshell_geom_taxonomy_cylinder_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_sphere_destroy(ifcopenshell_geom_taxonomy_sphere_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_torus_destroy(ifcopenshell_geom_taxonomy_torus_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_bspline_surface_destroy(ifcopenshell_geom_taxonomy_bspline_surface_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_collection_destroy(ifcopenshell_geom_taxonomy_collection_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_loft_destroy(ifcopenshell_geom_taxonomy_loft_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_extrusion_destroy(ifcopenshell_geom_taxonomy_extrusion_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_revolve_destroy(ifcopenshell_geom_taxonomy_revolve_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_sweep_along_curve_destroy(ifcopenshell_geom_taxonomy_sweep_along_curve_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_node_destroy(ifcopenshell_geom_taxonomy_node_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}

void ifcopenshell_geom_taxonomy_boolean_result_destroy(ifcopenshell_geom_taxonomy_boolean_result_t* handle) {
    if (handle == nullptr) {
        return;
    }
    handle->ptr.reset();
    delete handle;
}
void ifcopenshell_instance_list_destroy(ifcopenshell_instance_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_instance_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_geom_svgfill_polygon_list_destroy(ifcopenshell_geom_svgfill_polygon_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_geom_svgfill_polygon_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_geom_conversion_result_shape_list_destroy(ifcopenshell_geom_conversion_result_shape_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_geom_conversion_result_shape_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_declaration_list_destroy(ifcopenshell_declaration_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_declaration_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_entity_list_destroy(ifcopenshell_entity_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_entity_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_enumeration_list_destroy(ifcopenshell_enumeration_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_enumeration_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_select_type_list_destroy(ifcopenshell_select_type_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_select_type_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_type_declaration_list_destroy(ifcopenshell_type_declaration_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_type_declaration_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_attribute_list_destroy(ifcopenshell_attribute_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_attribute_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_inverse_attribute_list_destroy(ifcopenshell_inverse_attribute_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_inverse_attribute_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_geom_taxonomy_style_list_destroy(ifcopenshell_geom_taxonomy_style_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_geom_taxonomy_style_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_geom_taxonomy_item_list_destroy(ifcopenshell_geom_taxonomy_item_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_geom_taxonomy_item_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}

void ifcopenshell_geom_element_list_destroy(ifcopenshell_geom_element_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        if (value->items[i] != nullptr) {
            ifcopenshell_geom_element_destroy(value->items[i]);
        }
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}
void ifcopenshell_instance_list_list_destroy(ifcopenshell_instance_list_list_t* value) {
    if (value == nullptr || value->items == nullptr) {
        return;
    }
    for (size_t i = 0; i < value->size; ++i) {
        ifcopenshell_instance_list_destroy(&value->items[i]);
    }
    delete[] value->items;
    value->items = nullptr;
    value->size = 0;
}



bool ifcopenshell_geom_create_xml_serializer(ifcopenshell_file_t* file, const char* filename, ifcopenshell_geom_serializer_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (file == nullptr || file->ptr == nullptr) { throw std::runtime_error("Handle parameter \"file\" is invalid"); }
    auto file_cpp = file->ptr;
    if (filename == nullptr) { throw std::runtime_error("Parameter \"filename\" must not be null"); }
    std::string filename_cpp(filename);
        auto result_value = std::unique_ptr<Serializer>(static_cast<Serializer*>(new XmlSerializer(file_cpp, filename_cpp)));
        *out_result = new ifcopenshell_geom_serializer_t{result_value.release(), true};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_tree(ifcopenshell_geom_tree_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        #if defined(IFOPSH_WITH_OPENCASCADE)
        auto result_value = std::unique_ptr<IfcGeom::tree>(new IfcGeom::tree());
        *out_result = new ifcopenshell_geom_tree_t{result_value.release(), true};
#else
        throw std::runtime_error("ifcopenshell_geom_create_tree requires IFOPSH_WITH_OPENCASCADE");
#endif
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_tree_from_file(ifcopenshell_file_t* file, ifcopenshell_geom_tree_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (file == nullptr || file->ptr == nullptr) { throw std::runtime_error("Handle parameter \"file\" is invalid"); }
    auto& file_cpp = *file->ptr;
        #if defined(IFOPSH_WITH_OPENCASCADE)
        auto result_value = std::unique_ptr<IfcGeom::tree>(new IfcGeom::tree(file_cpp));
        *out_result = new ifcopenshell_geom_tree_t{result_value.release(), true};
#else
        throw std::runtime_error("ifcopenshell_geom_create_tree_from_file requires IFOPSH_WITH_OPENCASCADE");
#endif
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_tree_from_file_with_settings(ifcopenshell_file_t* file, ifcopenshell_geom_settings_t* settings, ifcopenshell_geom_tree_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (file == nullptr || file->ptr == nullptr) { throw std::runtime_error("Handle parameter \"file\" is invalid"); }
    auto& file_cpp = *file->ptr;
    if (settings == nullptr || settings->ptr == nullptr) { throw std::runtime_error("Handle parameter \"settings\" is invalid"); }
    auto& settings_cpp = *settings->ptr;
        #if defined(IFOPSH_WITH_OPENCASCADE)
        auto result_value = std::unique_ptr<IfcGeom::tree>(new IfcGeom::tree(file_cpp, settings_cpp));
        *out_result = new ifcopenshell_geom_tree_t{result_value.release(), true};
#else
        throw std::runtime_error("ifcopenshell_geom_create_tree_from_file_with_settings requires IFOPSH_WITH_OPENCASCADE");
#endif
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_tree_from_iterator(ifcopenshell_geom_iterator_t* iterator, ifcopenshell_geom_tree_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (iterator == nullptr || iterator->ptr == nullptr) { throw std::runtime_error("Handle parameter \"iterator\" is invalid"); }
    auto& iterator_cpp = *iterator->ptr;
        #if defined(IFOPSH_WITH_OPENCASCADE)
        auto result_value = std::unique_ptr<IfcGeom::tree>(new IfcGeom::tree(iterator_cpp));
        *out_result = new ifcopenshell_geom_tree_t{result_value.release(), true};
#else
        throw std::runtime_error("ifcopenshell_geom_create_tree_from_iterator requires IFOPSH_WITH_OPENCASCADE");
#endif
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_json_serializer(ifcopenshell_file_t* file, const char* filename, ifcopenshell_geom_serializer_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (file == nullptr || file->ptr == nullptr) { throw std::runtime_error("Handle parameter \"file\" is invalid"); }
    auto file_cpp = file->ptr;
    if (filename == nullptr) { throw std::runtime_error("Parameter \"filename\" must not be null"); }
    std::string filename_cpp(filename);
        #if defined(WITH_GLTF)
        auto result_value = std::unique_ptr<Serializer>(static_cast<Serializer*>(new JsonSerializer(file_cpp, filename_cpp)));
        *out_result = new ifcopenshell_geom_serializer_t{result_value.release(), true};
#else
        throw std::runtime_error("JSON serializer requires GLTF support (nlohmann_json)");
#endif
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_rocksdb_serializer_streaming(const char* input_filename, const char* rocksdb_filename, ifcopenshell_geom_serializer_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (input_filename == nullptr) { throw std::runtime_error("Parameter \"input_filename\" must not be null"); }
    std::string input_filename_cpp(input_filename);
    if (rocksdb_filename == nullptr) { throw std::runtime_error("Parameter \"rocksdb_filename\" must not be null"); }
    std::string rocksdb_filename_cpp(rocksdb_filename);
        #if defined(IFOPSH_WITH_ROCKSDB)
        auto result_value = std::unique_ptr<Serializer>(static_cast<Serializer*>(new RocksDbSerializer(input_filename_cpp, rocksdb_filename_cpp)));
        *out_result = new ifcopenshell_geom_serializer_t{result_value.release(), true};
#else
        throw std::runtime_error("ifcopenshell_geom_create_rocksdb_serializer_streaming requires IFOPSH_WITH_ROCKSDB");
#endif
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_buffer(ifcopenshell_geom_buffer_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        auto result_value = std::unique_ptr<stream_or_filename>(new stream_or_filename());
        *out_result = new ifcopenshell_geom_buffer_t{result_value.release(), true};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_buffer_from_filename(const char* filename, ifcopenshell_geom_buffer_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (filename == nullptr) { throw std::runtime_error("Parameter \"filename\" must not be null"); }
    std::string filename_cpp(filename);
        auto result_value = std::unique_ptr<stream_or_filename>(new stream_or_filename(filename_cpp));
        *out_result = new ifcopenshell_geom_buffer_t{result_value.release(), true};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_settings(ifcopenshell_geom_settings_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        auto result_value = std::unique_ptr<ifcopenshell::geometry::Settings>(new ifcopenshell::geometry::Settings());
        *out_result = new ifcopenshell_geom_settings_t{result_value.release(), true};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_serializer_settings(ifcopenshell_geom_serializer_settings_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        auto result_value = std::unique_ptr<ifcopenshell::geometry::SerializerSettings>(new ifcopenshell::geometry::SerializerSettings());
        *out_result = new ifcopenshell_geom_serializer_settings_t{result_value.release(), true};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_argument_type_to_string(int32_t type, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto type_cpp = static_cast<int>(type);
        *out_result = make_string(ifcparse::bindings::argument_type_to_string(type_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_clear_plugin_search_paths(void) {
    try {
        ifcopenshell_clear_error();
        ifcparse::bindings::clear_plugin_search_paths();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_clear_schemas(void) {
    try {
        ifcopenshell_clear_error();
        ifcparse::bindings::clear_schemas();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_escape_xml(const char* text) {
    try {
        ifcopenshell_clear_error();
    if (text == nullptr) { throw std::runtime_error("Parameter \"text\" must not be null"); }
    std::string text_cpp(text);
        ifcparse::bindings::escape_xml(text_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_from_parameter_type(ifcopenshell_parameter_type_t* parameter_type, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (parameter_type == nullptr || parameter_type->ptr == nullptr) { throw std::runtime_error("Handle parameter \"parameter_type\" is invalid"); }
    auto parameter_type_cpp = parameter_type->ptr;
        *out_result = static_cast<int32_t>(ifcparse::bindings::from_parameter_type(parameter_type_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_general_token_ptr(size_t start, const char* token, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto start_cpp = static_cast<size_t>(start);
    if (token == nullptr) { throw std::runtime_error("Parameter \"token\" must not be null"); }
    std::string token_cpp(token);
        *out_result = static_cast<int32_t>(ifcparse::bindings::general_token_ptr(start_cpp, token_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_get_feature(const char* name, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        *out_result = ifcparse::bindings::get_feature(name_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_get_info_json(ifcopenshell_instance_t* instance, bool include_identifier, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (instance == nullptr) { throw std::runtime_error("Handle parameter \"instance\" must not be null"); }
    const auto& instance_cpp = instance->value;
    auto include_identifier_cpp = static_cast<bool>(include_identifier);
        *out_result = make_string(ifcparse::bindings::get_info_json(instance_cpp, include_identifier_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_get_log(ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        *out_result = make_string(ifcparse::bindings::get_log());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_get_plugin_search_paths(ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        *out_result = make_string_list(ifcparse::bindings::get_plugin_search_paths());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_get_si_equivalent(ifcopenshell_instance_t* named_unit, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (named_unit == nullptr) { throw std::runtime_error("Handle parameter \"named_unit\" must not be null"); }
    const auto& named_unit_cpp = named_unit->value;
        *out_result = static_cast<double>(ifcparse::bindings::get_si_equivalent(named_unit_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_guess_file_type(const char* path, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (path == nullptr) { throw std::runtime_error("Parameter \"path\" must not be null"); }
    std::string path_cpp(path);
        *out_result = static_cast<int32_t>(ifcparse::bindings::guess_file_type(path_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_instance_list_create_from_handles(const ifcopenshell_instance_list_t* instances, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (instances == nullptr) { throw std::runtime_error("Parameter \"instances\" must not be null"); }
    auto instances_cpp = to_cpp_instance_list(instances);
        *out_result = new ifcopenshell_parse_instance_list_t{ifcparse::bindings::instance_list_create_from_handles(instances_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_make_aggregate(int32_t element_type, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto element_type_cpp = static_cast<int>(element_type);
        *out_result = static_cast<int32_t>(ifcparse::bindings::make_aggregate(element_type_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_new_file(const char* schema_identifier, int32_t file_type, const char* path, ifcopenshell_file_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (schema_identifier == nullptr) { throw std::runtime_error("Parameter \"schema_identifier\" must not be null"); }
    std::string schema_identifier_cpp(schema_identifier);
    auto file_type_cpp = static_cast<int>(file_type);
    if (path == nullptr) { throw std::runtime_error("Parameter \"path\" must not be null"); }
    std::string path_cpp(path);
        auto result_value = ifcparse::bindings::new_file(schema_identifier_cpp, file_type_cpp, path_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_open(const char* path, bool readonly, ifcopenshell_file_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (path == nullptr) { throw std::runtime_error("Parameter \"path\" must not be null"); }
    std::string path_cpp(path);
    auto readonly_cpp = static_cast<bool>(readonly);
        auto result_value = ifcparse::bindings::open(path_cpp, readonly_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_open_bypass(const char* path, const ifcopenshell_string_list_t* type_names, ifcopenshell_file_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (path == nullptr) { throw std::runtime_error("Parameter \"path\" must not be null"); }
    std::string path_cpp(path);
    if (type_names == nullptr) { throw std::runtime_error("Parameter \"type_names\" must not be null"); }
    auto type_names_cpp = to_cpp_string_list(type_names);
        auto result_value = ifcparse::bindings::open_bypass(path_cpp, type_names_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_operator_token_ptr(size_t start, const char* data, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto start_cpp = static_cast<size_t>(start);
    if (data == nullptr) { throw std::runtime_error("Parameter \"data\" must not be null"); }
    std::string data_cpp(data);
        *out_result = static_cast<int32_t>(ifcparse::bindings::operator_token_ptr(start_cpp, data_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_read_memory(void* data, int32_t length, ifcopenshell_file_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (data == nullptr) { throw std::runtime_error("Parameter \"data\" must not be null"); }
    auto data_cpp = static_cast<const void*>(data);
    auto length_cpp = static_cast<int>(length);
        auto result_value = ifcparse::bindings::read_memory(data_cpp, length_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_register_schema(ifcopenshell_schema_t* schema) {
    try {
        ifcopenshell_clear_error();
    if (schema == nullptr || schema->ptr == nullptr) { throw std::runtime_error("Handle parameter \"schema\" is invalid"); }
    auto schema_cpp = schema->ptr;
        ifcparse::bindings::register_schema(schema_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_sanitate_material_name(const char* material_name) {
    try {
        ifcopenshell_clear_error();
    if (material_name == nullptr) { throw std::runtime_error("Parameter \"material_name\" must not be null"); }
    std::string material_name_cpp(material_name);
        ifcparse::bindings::sanitate_material_name(material_name_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_schema_by_name(const char* schema_name, ifcopenshell_schema_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (schema_name == nullptr) { throw std::runtime_error("Parameter \"schema_name\" must not be null"); }
    std::string schema_name_cpp(schema_name);
        auto result_value = ifcparse::bindings::schema_by_name(schema_name_cpp);
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_schema_t{const_cast<ifcopenshell::schema_definition*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_schema_names(ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        *out_result = make_string_list(ifcparse::bindings::schema_names());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_schema_plugin_registration_symbol(ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        *out_result = make_string(ifcparse::bindings::schema_plugin_registration_symbol());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_set_feature(const char* name, bool value) {
    try {
        ifcopenshell_clear_error();
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
    auto value_cpp = static_cast<bool>(value);
        ifcparse::bindings::set_feature(name_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_set_log_format_json(void) {
    try {
        ifcopenshell_clear_error();
        ifcparse::bindings::set_log_format_json();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_set_log_format_text(void) {
    try {
        ifcopenshell_clear_error();
        ifcparse::bindings::set_log_format_text();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_set_plugin_search_paths(const ifcopenshell_string_list_t* paths) {
    try {
        ifcopenshell_clear_error();
    if (paths == nullptr) { throw std::runtime_error("Parameter \"paths\" must not be null"); }
    auto paths_cpp = to_cpp_string_list(paths);
        ifcparse::bindings::set_plugin_search_paths(paths_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_si_prefix_to_value(const char* prefix, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (prefix == nullptr) { throw std::runtime_error("Parameter \"prefix\" must not be null"); }
    std::string prefix_cpp(prefix);
        *out_result = static_cast<double>(ifcparse::bindings::si_prefix_to_value(prefix_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_stream(ifcopenshell_instance_streamer_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        auto result_value = ifcparse::bindings::stream();
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_streamer_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_stream_from_path(const char* path, bool mmap, ifcopenshell_instance_streamer_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (path == nullptr) { throw std::runtime_error("Parameter \"path\" must not be null"); }
    std::string path_cpp(path);
    auto mmap_cpp = static_cast<bool>(mmap);
        auto result_value = ifcparse::bindings::stream_from_path(path_cpp, mmap_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_streamer_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_stream_from_string(const char* data, ifcopenshell_instance_streamer_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (data == nullptr) { throw std::runtime_error("Parameter \"data\" must not be null"); }
    std::string data_cpp(data);
        auto result_value = ifcparse::bindings::stream_from_string(data_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_streamer_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_traverse(ifcopenshell_instance_t* instance, int32_t max_depth, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (instance == nullptr) { throw std::runtime_error("Handle parameter \"instance\" must not be null"); }
    const auto& instance_cpp = instance->value;
    auto max_depth_cpp = static_cast<int>(max_depth);
        *out_result = new ifcopenshell_parse_instance_list_t{ifcparse::bindings::traverse(instance_cpp, max_depth_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_traverse_breadth_first(ifcopenshell_instance_t* instance, int32_t max_depth, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (instance == nullptr) { throw std::runtime_error("Handle parameter \"instance\" must not be null"); }
    const auto& instance_cpp = instance->value;
    auto max_depth_cpp = static_cast<int>(max_depth);
        *out_result = new ifcopenshell_parse_instance_list_t{ifcparse::bindings::traverse_breadth_first(instance_cpp, max_depth_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_turn_off_detailed_logging(void) {
    try {
        ifcopenshell_clear_error();
        ifcparse::bindings::turn_off_detailed_logging();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_turn_on_detailed_logging(void) {
    try {
        ifcopenshell_clear_error();
        ifcparse::bindings::turn_on_detailed_logging();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_unescape_xml(const char* text) {
    try {
        ifcopenshell_clear_error();
    if (text == nullptr) { throw std::runtime_error("Parameter \"text\" must not be null"); }
    std::string text_cpp(text);
        ifcparse::bindings::unescape_xml(text_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_valid_binary_string(const char* binary_string, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (binary_string == nullptr) { throw std::runtime_error("Parameter \"binary_string\" must not be null"); }
    std::string binary_string_cpp(binary_string);
        *out_result = ifcparse::bindings::valid_binary_string(binary_string_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_version(ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        *out_result = make_static_string(ifcparse::bindings::version());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_arrange_polygons(const ifcopenshell_geom_svgfill_polygon_list_t* polygons_cpp, ifcopenshell_geom_svgfill_polygon_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (polygons_cpp == nullptr) { throw std::runtime_error("Parameter \"polygons_cpp\" must not be null"); }
    auto polygons_cpp_cpp = to_cpp_geom_svgfill_polygon_list(polygons_cpp);
        *out_result = make_geom_svgfill_polygon_list(ifcgeom::bindings::arrange_polygons(polygons_cpp_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_convert_loop_to_function_item(ifcopenshell_geom_taxonomy_item_t* loop_item_cpp, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (loop_item_cpp == nullptr || loop_item_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"loop_item_cpp\" is invalid"); }
    const auto& loop_item_cpp_cpp = loop_item_cpp->ptr;
        *out_result = new ifcopenshell_geom_taxonomy_item_t{ifcgeom::bindings::convert_loop_to_function_item(loop_item_cpp_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_epeck_from_double(double value, ifcopenshell_geom_opaque_number_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto value_cpp = static_cast<double>(value);
        auto result_value = ifcgeom::bindings::create_epeck_from_double(value_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_opaque_number_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_epeck_from_int(int32_t value, ifcopenshell_geom_opaque_number_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto value_cpp = static_cast<int>(value);
        auto result_value = ifcgeom::bindings::create_epeck_from_int(value_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_opaque_number_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_epeck_from_string(const char* value_cpp, ifcopenshell_geom_opaque_number_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (value_cpp == nullptr) { throw std::runtime_error("Parameter \"value_cpp\" must not be null"); }
    std::string value_cpp_cpp(value_cpp);
        auto result_value = ifcgeom::bindings::create_epeck_from_string(value_cpp_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_opaque_number_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_function_item_evaluator(ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_geom_taxonomy_item_t* fn_item_cpp, ifcopenshell_geom_function_item_evaluator_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (settings_cpp == nullptr || settings_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"settings_cpp\" is invalid"); }
    auto settings_cpp_cpp = settings_cpp->ptr;
    if (fn_item_cpp == nullptr || fn_item_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"fn_item_cpp\" is invalid"); }
    const auto& fn_item_cpp_cpp = fn_item_cpp->ptr;
        auto result_value = ifcgeom::bindings::create_function_item_evaluator(settings_cpp_cpp, fn_item_cpp_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_function_item_evaluator_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_geometry_serializer_by_path(const char* format, const char* output_filename, const char* output_temp_filename, ifcopenshell_geom_settings_t* geometry_settings, ifcopenshell_geom_serializer_settings_t* serializer_settings, ifcopenshell_geom_geometry_serializer_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (format == nullptr) { throw std::runtime_error("Parameter \"format\" must not be null"); }
    std::string format_cpp(format);
    if (output_filename == nullptr) { throw std::runtime_error("Parameter \"output_filename\" must not be null"); }
    std::string output_filename_cpp(output_filename);
    if (output_temp_filename == nullptr) { throw std::runtime_error("Parameter \"output_temp_filename\" must not be null"); }
    std::string output_temp_filename_cpp(output_temp_filename);
    if (geometry_settings == nullptr || geometry_settings->ptr == nullptr) { throw std::runtime_error("Handle parameter \"geometry_settings\" is invalid"); }
    auto geometry_settings_cpp = geometry_settings->ptr;
    if (serializer_settings == nullptr || serializer_settings->ptr == nullptr) { throw std::runtime_error("Handle parameter \"serializer_settings\" is invalid"); }
    auto serializer_settings_cpp = serializer_settings->ptr;
        auto result_value = ifcgeom::bindings::create_geometry_serializer_by_path(format_cpp, output_filename_cpp, output_temp_filename_cpp, geometry_settings_cpp, serializer_settings_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_geometry_serializer_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_geometry_serializer_by_stream(const char* format, ifcopenshell_geom_buffer_t* output, ifcopenshell_geom_buffer_t* output_temp, ifcopenshell_geom_settings_t* geometry_settings, ifcopenshell_geom_serializer_settings_t* serializer_settings, ifcopenshell_geom_geometry_serializer_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (format == nullptr) { throw std::runtime_error("Parameter \"format\" must not be null"); }
    std::string format_cpp(format);
    if (output == nullptr || output->ptr == nullptr) { throw std::runtime_error("Handle parameter \"output\" is invalid"); }
    auto output_cpp = output->ptr;
    if (output_temp == nullptr || output_temp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"output_temp\" is invalid"); }
    auto output_temp_cpp = output_temp->ptr;
    if (geometry_settings == nullptr || geometry_settings->ptr == nullptr) { throw std::runtime_error("Handle parameter \"geometry_settings\" is invalid"); }
    auto geometry_settings_cpp = geometry_settings->ptr;
    if (serializer_settings == nullptr || serializer_settings->ptr == nullptr) { throw std::runtime_error("Handle parameter \"serializer_settings\" is invalid"); }
    auto serializer_settings_cpp = serializer_settings->ptr;
        auto result_value = ifcgeom::bindings::create_geometry_serializer_by_stream(format_cpp, output_cpp, output_temp_cpp, geometry_settings_cpp, serializer_settings_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_geometry_serializer_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_iterator(const char* geometry_library_cpp, ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_file_t* file_cpp, int32_t num_threads, ifcopenshell_geom_iterator_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (geometry_library_cpp == nullptr) { throw std::runtime_error("Parameter \"geometry_library_cpp\" must not be null"); }
    std::string geometry_library_cpp_cpp(geometry_library_cpp);
    if (settings_cpp == nullptr || settings_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"settings_cpp\" is invalid"); }
    auto settings_cpp_cpp = settings_cpp->ptr;
    if (file_cpp == nullptr || file_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"file_cpp\" is invalid"); }
    auto file_cpp_cpp = file_cpp->ptr;
    auto num_threads_cpp = static_cast<int>(num_threads);
        auto result_value = ifcgeom::bindings::create_iterator(geometry_library_cpp_cpp, settings_cpp_cpp, file_cpp_cpp, num_threads_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_iterator_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_iterator_with_include_exclude(const char* geometry_library_cpp, ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_file_t* file_cpp, const ifcopenshell_string_list_t* elems_cpp, bool include, int32_t num_threads, ifcopenshell_geom_iterator_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (geometry_library_cpp == nullptr) { throw std::runtime_error("Parameter \"geometry_library_cpp\" must not be null"); }
    std::string geometry_library_cpp_cpp(geometry_library_cpp);
    if (settings_cpp == nullptr || settings_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"settings_cpp\" is invalid"); }
    auto settings_cpp_cpp = settings_cpp->ptr;
    if (file_cpp == nullptr || file_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"file_cpp\" is invalid"); }
    auto file_cpp_cpp = file_cpp->ptr;
    if (elems_cpp == nullptr) { throw std::runtime_error("Parameter \"elems_cpp\" must not be null"); }
    auto elems_cpp_cpp = to_cpp_string_list(elems_cpp);
    auto include_cpp = static_cast<bool>(include);
    auto num_threads_cpp = static_cast<int>(num_threads);
        auto result_value = ifcgeom::bindings::create_iterator_with_include_exclude(geometry_library_cpp_cpp, settings_cpp_cpp, file_cpp_cpp, elems_cpp_cpp, include_cpp, num_threads_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_iterator_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_iterator_with_include_exclude_globalid(const char* geometry_library_cpp, ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_file_t* file_cpp, const ifcopenshell_string_list_t* elems_cpp, bool include, int32_t num_threads, ifcopenshell_geom_iterator_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (geometry_library_cpp == nullptr) { throw std::runtime_error("Parameter \"geometry_library_cpp\" must not be null"); }
    std::string geometry_library_cpp_cpp(geometry_library_cpp);
    if (settings_cpp == nullptr || settings_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"settings_cpp\" is invalid"); }
    auto settings_cpp_cpp = settings_cpp->ptr;
    if (file_cpp == nullptr || file_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"file_cpp\" is invalid"); }
    auto file_cpp_cpp = file_cpp->ptr;
    if (elems_cpp == nullptr) { throw std::runtime_error("Parameter \"elems_cpp\" must not be null"); }
    auto elems_cpp_cpp = to_cpp_string_list(elems_cpp);
    auto include_cpp = static_cast<bool>(include);
    auto num_threads_cpp = static_cast<int>(num_threads);
        auto result_value = ifcgeom::bindings::create_iterator_with_include_exclude_globalid(geometry_library_cpp_cpp, settings_cpp_cpp, file_cpp_cpp, elems_cpp_cpp, include_cpp, num_threads_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_iterator_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_iterator_with_include_exclude_id(const char* geometry_library_cpp, ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_file_t* file_cpp, const ifcopenshell_int32_list_t* elems_cpp, bool include, int32_t num_threads, ifcopenshell_geom_iterator_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (geometry_library_cpp == nullptr) { throw std::runtime_error("Parameter \"geometry_library_cpp\" must not be null"); }
    std::string geometry_library_cpp_cpp(geometry_library_cpp);
    if (settings_cpp == nullptr || settings_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"settings_cpp\" is invalid"); }
    auto settings_cpp_cpp = settings_cpp->ptr;
    if (file_cpp == nullptr || file_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"file_cpp\" is invalid"); }
    auto file_cpp_cpp = file_cpp->ptr;
    if (elems_cpp == nullptr) { throw std::runtime_error("Parameter \"elems_cpp\" must not be null"); }
    auto elems_cpp_cpp = to_cpp_int32_list(elems_cpp);
    auto include_cpp = static_cast<bool>(include);
    auto num_threads_cpp = static_cast<int>(num_threads);
        auto result_value = ifcgeom::bindings::create_iterator_with_include_exclude_id(geometry_library_cpp_cpp, settings_cpp_cpp, file_cpp_cpp, elems_cpp_cpp, include_cpp, num_threads_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_iterator_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_create_shape(ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_instance_t* instance_cpp, ifcopenshell_instance_t* representation, const char* geometry_library, ifcopenshell_geom_element_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (settings_cpp == nullptr || settings_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"settings_cpp\" is invalid"); }
    auto settings_cpp_cpp = settings_cpp->ptr;
    if (instance_cpp == nullptr) { throw std::runtime_error("Handle parameter \"instance_cpp\" must not be null"); }
    auto instance_cpp_cpp = &instance_cpp->value;
    std::optional<express::Base> representation_cpp;
    if (representation != nullptr) { representation_cpp = representation->value; }
    std::optional<std::string> geometry_library_cpp;
    if (geometry_library != nullptr) { geometry_library_cpp = std::string(geometry_library); }
        auto result_value = ifcgeom::bindings::create_shape(settings_cpp_cpp, instance_cpp_cpp, representation_cpp, geometry_library_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_element_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_line_segments_to_polygons(int32_t solver, double eps, const char* segments_json_cpp, ifcopenshell_geom_svgfill_polygon_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto solver_cpp = static_cast<int>(solver);
    auto eps_cpp = static_cast<double>(eps);
    if (segments_json_cpp == nullptr) { throw std::runtime_error("Parameter \"segments_json_cpp\" must not be null"); }
    std::string segments_json_cpp_cpp(segments_json_cpp);
        *out_result = make_geom_svgfill_polygon_list(ifcgeom::bindings::line_segments_to_polygons(solver_cpp, eps_cpp, segments_json_cpp_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_map_shape(ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_instance_t* instance_cpp, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (settings_cpp == nullptr || settings_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"settings_cpp\" is invalid"); }
    auto settings_cpp_cpp = settings_cpp->ptr;
    if (instance_cpp == nullptr) { throw std::runtime_error("Handle parameter \"instance_cpp\" must not be null"); }
    auto instance_cpp_cpp = &instance_cpp->value;
        *out_result = new ifcopenshell_geom_taxonomy_item_t{ifcgeom::bindings::map_shape(settings_cpp_cpp, instance_cpp_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_nary_union(const ifcopenshell_geom_conversion_result_shape_list_t* shapes_cpp, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (shapes_cpp == nullptr) { throw std::runtime_error("Parameter \"shapes_cpp\" must not be null"); }
    auto shapes_cpp_cpp = to_cpp_geom_conversion_result_shape_list(shapes_cpp);
        auto result_value = ifcgeom::bindings::nary_union(shapes_cpp_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_plugin_is_loaded(const char* kind, const char* id, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (kind == nullptr) { throw std::runtime_error("Parameter \"kind\" must not be null"); }
    std::string kind_cpp(kind);
    if (id == nullptr) { throw std::runtime_error("Parameter \"id\" must not be null"); }
    std::string id_cpp(id);
        *out_result = ifcgeom::bindings::plugin_is_loaded(kind_cpp, id_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_plugin_load(const char* kind, const char* id, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (kind == nullptr) { throw std::runtime_error("Parameter \"kind\" must not be null"); }
    std::string kind_cpp(kind);
    if (id == nullptr) { throw std::runtime_error("Parameter \"id\" must not be null"); }
    std::string id_cpp(id);
        *out_result = ifcgeom::bindings::plugin_load(kind_cpp, id_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_svg_to_line_segments(const char* svg_data_cpp, const char* class_name, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (svg_data_cpp == nullptr) { throw std::runtime_error("Parameter \"svg_data_cpp\" must not be null"); }
    std::string svg_data_cpp_cpp(svg_data_cpp);
    std::optional<std::string> class_name_cpp;
    if (class_name != nullptr) { class_name_cpp = std::string(class_name); }
        *out_result = make_string(ifcgeom::bindings::svg_to_line_segments(svg_data_cpp_cpp, class_name_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_svg_to_polygons(const char* svg_data_cpp, const char* class_name, ifcopenshell_geom_svgfill_polygon_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (svg_data_cpp == nullptr) { throw std::runtime_error("Parameter \"svg_data_cpp\" must not be null"); }
    std::string svg_data_cpp_cpp(svg_data_cpp);
    std::optional<std::string> class_name_cpp;
    if (class_name != nullptr) { class_name_cpp = std::string(class_name); }
        *out_result = make_geom_svgfill_polygon_list(ifcgeom::bindings::svg_to_polygons(svg_data_cpp_cpp, class_name_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_boolean_result(int32_t operation, ifcopenshell_geom_taxonomy_boolean_result_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto operation_cpp = static_cast<int>(operation);
        *out_result = new ifcopenshell_geom_taxonomy_boolean_result_t{ifcgeom::bindings::taxonomy_create_boolean_result(operation_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_box(double dx, double dy, double dz, ifcopenshell_geom_taxonomy_solid_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto dx_cpp = static_cast<double>(dx);
    auto dy_cpp = static_cast<double>(dy);
    auto dz_cpp = static_cast<double>(dz);
        *out_result = new ifcopenshell_geom_taxonomy_solid_t{ifcgeom::bindings::taxonomy_create_box(dx_cpp, dy_cpp, dz_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_bspline_curve(int32_t degree, ifcopenshell_geom_taxonomy_bspline_curve_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto degree_cpp = static_cast<int>(degree);
        *out_result = new ifcopenshell_geom_taxonomy_bspline_curve_t{ifcgeom::bindings::taxonomy_create_bspline_curve(degree_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_bspline_surface(int32_t degree_u, int32_t degree_v, ifcopenshell_geom_taxonomy_bspline_surface_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto degree_u_cpp = static_cast<int>(degree_u);
    auto degree_v_cpp = static_cast<int>(degree_v);
        *out_result = new ifcopenshell_geom_taxonomy_bspline_surface_t{ifcgeom::bindings::taxonomy_create_bspline_surface(degree_u_cpp, degree_v_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_circle(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, double radius, ifcopenshell_geom_taxonomy_circle_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto origin_x_cpp = static_cast<double>(origin_x);
    auto origin_y_cpp = static_cast<double>(origin_y);
    auto origin_z_cpp = static_cast<double>(origin_z);
    auto dir_x_cpp = static_cast<double>(dir_x);
    auto dir_y_cpp = static_cast<double>(dir_y);
    auto dir_z_cpp = static_cast<double>(dir_z);
    auto radius_cpp = static_cast<double>(radius);
        *out_result = new ifcopenshell_geom_taxonomy_circle_t{ifcgeom::bindings::taxonomy_create_circle(origin_x_cpp, origin_y_cpp, origin_z_cpp, dir_x_cpp, dir_y_cpp, dir_z_cpp, radius_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_collection(ifcopenshell_geom_taxonomy_collection_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        *out_result = new ifcopenshell_geom_taxonomy_collection_t{ifcgeom::bindings::taxonomy_create_collection()};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_cylinder(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, double radius, ifcopenshell_geom_taxonomy_cylinder_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto origin_x_cpp = static_cast<double>(origin_x);
    auto origin_y_cpp = static_cast<double>(origin_y);
    auto origin_z_cpp = static_cast<double>(origin_z);
    auto dir_x_cpp = static_cast<double>(dir_x);
    auto dir_y_cpp = static_cast<double>(dir_y);
    auto dir_z_cpp = static_cast<double>(dir_z);
    auto radius_cpp = static_cast<double>(radius);
        *out_result = new ifcopenshell_geom_taxonomy_cylinder_t{ifcgeom::bindings::taxonomy_create_cylinder(origin_x_cpp, origin_y_cpp, origin_z_cpp, dir_x_cpp, dir_y_cpp, dir_z_cpp, radius_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_direction3(double x, double y, double z, ifcopenshell_geom_taxonomy_direction3_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto x_cpp = static_cast<double>(x);
    auto y_cpp = static_cast<double>(y);
    auto z_cpp = static_cast<double>(z);
        *out_result = new ifcopenshell_geom_taxonomy_direction3_t{ifcgeom::bindings::taxonomy_create_direction3(x_cpp, y_cpp, z_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_ellipse(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, double radius1, double radius2, ifcopenshell_geom_taxonomy_ellipse_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto origin_x_cpp = static_cast<double>(origin_x);
    auto origin_y_cpp = static_cast<double>(origin_y);
    auto origin_z_cpp = static_cast<double>(origin_z);
    auto dir_x_cpp = static_cast<double>(dir_x);
    auto dir_y_cpp = static_cast<double>(dir_y);
    auto dir_z_cpp = static_cast<double>(dir_z);
    auto radius1_cpp = static_cast<double>(radius1);
    auto radius2_cpp = static_cast<double>(radius2);
        *out_result = new ifcopenshell_geom_taxonomy_ellipse_t{ifcgeom::bindings::taxonomy_create_ellipse(origin_x_cpp, origin_y_cpp, origin_z_cpp, dir_x_cpp, dir_y_cpp, dir_z_cpp, radius1_cpp, radius2_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_extrusion(ifcopenshell_geom_taxonomy_item_t* basis_cpp, ifcopenshell_geom_taxonomy_direction3_t* direction_cpp, double depth, ifcopenshell_geom_taxonomy_extrusion_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (basis_cpp == nullptr || basis_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"basis_cpp\" is invalid"); }
    const auto& basis_cpp_cpp = basis_cpp->ptr;
    if (direction_cpp == nullptr || direction_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"direction_cpp\" is invalid"); }
    const auto& direction_cpp_cpp = direction_cpp->ptr;
    auto depth_cpp = static_cast<double>(depth);
        *out_result = new ifcopenshell_geom_taxonomy_extrusion_t{ifcgeom::bindings::taxonomy_create_extrusion(basis_cpp_cpp, direction_cpp_cpp, depth_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_line(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, ifcopenshell_geom_taxonomy_line_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto origin_x_cpp = static_cast<double>(origin_x);
    auto origin_y_cpp = static_cast<double>(origin_y);
    auto origin_z_cpp = static_cast<double>(origin_z);
    auto dir_x_cpp = static_cast<double>(dir_x);
    auto dir_y_cpp = static_cast<double>(dir_y);
    auto dir_z_cpp = static_cast<double>(dir_z);
        *out_result = new ifcopenshell_geom_taxonomy_line_t{ifcgeom::bindings::taxonomy_create_line(origin_x_cpp, origin_y_cpp, origin_z_cpp, dir_x_cpp, dir_y_cpp, dir_z_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_loft(ifcopenshell_geom_taxonomy_loft_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        *out_result = new ifcopenshell_geom_taxonomy_loft_t{ifcgeom::bindings::taxonomy_create_loft()};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_node(ifcopenshell_geom_taxonomy_node_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
        *out_result = new ifcopenshell_geom_taxonomy_node_t{ifcgeom::bindings::taxonomy_create_node()};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_offset_curve(ifcopenshell_geom_taxonomy_item_t* basis, ifcopenshell_geom_taxonomy_direction3_t* reference, double offset, ifcopenshell_geom_taxonomy_offset_curve_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (basis == nullptr || basis->ptr == nullptr) { throw std::runtime_error("Handle parameter \"basis\" is invalid"); }
    const auto& basis_cpp = basis->ptr;
    if (reference == nullptr || reference->ptr == nullptr) { throw std::runtime_error("Handle parameter \"reference\" is invalid"); }
    const auto& reference_cpp = reference->ptr;
    auto offset_cpp = static_cast<double>(offset);
        *out_result = new ifcopenshell_geom_taxonomy_offset_curve_t{ifcgeom::bindings::taxonomy_create_offset_curve(basis_cpp, reference_cpp, offset_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_plane(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, ifcopenshell_geom_taxonomy_plane_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto origin_x_cpp = static_cast<double>(origin_x);
    auto origin_y_cpp = static_cast<double>(origin_y);
    auto origin_z_cpp = static_cast<double>(origin_z);
    auto dir_x_cpp = static_cast<double>(dir_x);
    auto dir_y_cpp = static_cast<double>(dir_y);
    auto dir_z_cpp = static_cast<double>(dir_z);
        *out_result = new ifcopenshell_geom_taxonomy_plane_t{ifcgeom::bindings::taxonomy_create_plane(origin_x_cpp, origin_y_cpp, origin_z_cpp, dir_x_cpp, dir_y_cpp, dir_z_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_point3(double x, double y, double z, ifcopenshell_geom_taxonomy_point3_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto x_cpp = static_cast<double>(x);
    auto y_cpp = static_cast<double>(y);
    auto z_cpp = static_cast<double>(z);
        *out_result = new ifcopenshell_geom_taxonomy_point3_t{ifcgeom::bindings::taxonomy_create_point3(x_cpp, y_cpp, z_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_revolve(ifcopenshell_geom_taxonomy_item_t* basis_cpp, ifcopenshell_geom_taxonomy_point3_t* axis_origin_cpp, ifcopenshell_geom_taxonomy_direction3_t* direction_cpp, double angle, ifcopenshell_geom_taxonomy_revolve_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (basis_cpp == nullptr || basis_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"basis_cpp\" is invalid"); }
    const auto& basis_cpp_cpp = basis_cpp->ptr;
    if (axis_origin_cpp == nullptr || axis_origin_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"axis_origin_cpp\" is invalid"); }
    const auto& axis_origin_cpp_cpp = axis_origin_cpp->ptr;
    if (direction_cpp == nullptr || direction_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"direction_cpp\" is invalid"); }
    const auto& direction_cpp_cpp = direction_cpp->ptr;
    auto angle_cpp = static_cast<double>(angle);
        *out_result = new ifcopenshell_geom_taxonomy_revolve_t{ifcgeom::bindings::taxonomy_create_revolve(basis_cpp_cpp, axis_origin_cpp_cpp, direction_cpp_cpp, angle_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_sphere(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, double radius, ifcopenshell_geom_taxonomy_sphere_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto origin_x_cpp = static_cast<double>(origin_x);
    auto origin_y_cpp = static_cast<double>(origin_y);
    auto origin_z_cpp = static_cast<double>(origin_z);
    auto dir_x_cpp = static_cast<double>(dir_x);
    auto dir_y_cpp = static_cast<double>(dir_y);
    auto dir_z_cpp = static_cast<double>(dir_z);
    auto radius_cpp = static_cast<double>(radius);
        *out_result = new ifcopenshell_geom_taxonomy_sphere_t{ifcgeom::bindings::taxonomy_create_sphere(origin_x_cpp, origin_y_cpp, origin_z_cpp, dir_x_cpp, dir_y_cpp, dir_z_cpp, radius_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_sweep_along_curve(ifcopenshell_geom_taxonomy_face_t* basis_face_cpp, ifcopenshell_geom_taxonomy_item_t* directrix_cpp, ifcopenshell_geom_taxonomy_direction3_t* reference_direction_cpp, ifcopenshell_geom_taxonomy_sweep_along_curve_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (basis_face_cpp == nullptr || basis_face_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"basis_face_cpp\" is invalid"); }
    const auto& basis_face_cpp_cpp = basis_face_cpp->ptr;
    if (directrix_cpp == nullptr || directrix_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"directrix_cpp\" is invalid"); }
    const auto& directrix_cpp_cpp = directrix_cpp->ptr;
    if (reference_direction_cpp == nullptr || reference_direction_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"reference_direction_cpp\" is invalid"); }
    const auto& reference_direction_cpp_cpp = reference_direction_cpp->ptr;
        *out_result = new ifcopenshell_geom_taxonomy_sweep_along_curve_t{ifcgeom::bindings::taxonomy_create_sweep_along_curve(basis_face_cpp_cpp, directrix_cpp_cpp, reference_direction_cpp_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_create_torus(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, double radius1, double radius2, ifcopenshell_geom_taxonomy_torus_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto origin_x_cpp = static_cast<double>(origin_x);
    auto origin_y_cpp = static_cast<double>(origin_y);
    auto origin_z_cpp = static_cast<double>(origin_z);
    auto dir_x_cpp = static_cast<double>(dir_x);
    auto dir_y_cpp = static_cast<double>(dir_y);
    auto dir_z_cpp = static_cast<double>(dir_z);
    auto radius1_cpp = static_cast<double>(radius1);
    auto radius2_cpp = static_cast<double>(radius2);
        *out_result = new ifcopenshell_geom_taxonomy_torus_t{ifcgeom::bindings::taxonomy_create_torus(origin_x_cpp, origin_y_cpp, origin_z_cpp, dir_x_cpp, dir_y_cpp, dir_z_cpp, radius1_cpp, radius2_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_function_item_end(ifcopenshell_geom_taxonomy_item_t* item_cpp, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (item_cpp == nullptr || item_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"item_cpp\" is invalid"); }
    const auto& item_cpp_cpp = item_cpp->ptr;
        *out_result = static_cast<double>(ifcgeom::bindings::taxonomy_function_item_end(item_cpp_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_function_item_start(ifcopenshell_geom_taxonomy_item_t* item_cpp, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (item_cpp == nullptr || item_cpp->ptr == nullptr) { throw std::runtime_error("Handle parameter \"item_cpp\" is invalid"); }
    const auto& item_cpp_cpp = item_cpp->ptr;
        *out_result = static_cast<double>(ifcgeom::bindings::taxonomy_function_item_start(item_cpp_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_helmert_curve_point(double A0, double A1, double A2, double s, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    auto A0_cpp = static_cast<double>(A0);
    auto A1_cpp = static_cast<double>(A1);
    auto A2_cpp = static_cast<double>(A2);
    auto s_cpp = static_cast<double>(s);
        *out_result = make_double_list(ifcopenshell::geometry::helmert_curve_point(A0_cpp, A1_cpp, A2_cpp, s_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_create(ifcopenshell_file_t* self, ifcopenshell_declaration_t* declaration, int32_t instance_id, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (declaration == nullptr || declaration->ptr == nullptr) { throw std::runtime_error("Handle parameter \"declaration\" is invalid"); }
    auto declaration_cpp = declaration->ptr;
    auto instance_id_cpp = static_cast<int>(instance_id);
        auto result_value = self_cpp->create(declaration_cpp, instance_id_cpp);
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_get_inverses_by_declaration(ifcopenshell_file_t* self, int32_t instance_id, ifcopenshell_declaration_t* declaration, int32_t attribute_index, ifcopenshell_instance_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto instance_id_cpp = static_cast<int>(instance_id);
    if (declaration == nullptr || declaration->ptr == nullptr) { throw std::runtime_error("Handle parameter \"declaration\" is invalid"); }
    auto declaration_cpp = declaration->ptr;
    auto attribute_index_cpp = static_cast<int>(attribute_index);
        *out_result = make_instance_list(self_cpp->get_inverse(instance_id_cpp, declaration_cpp, attribute_index_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_by_type(ifcopenshell_file_t* self, const char* type_name, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (type_name == nullptr) { throw std::runtime_error("Parameter \"type_name\" must not be null"); }
    std::string type_name_cpp(type_name);
        *out_result = new ifcopenshell_parse_instance_list_t{self_cpp->instances_by_type(type_name_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_by_type_excl_subtypes(ifcopenshell_file_t* self, const char* type_name, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (type_name == nullptr) { throw std::runtime_error("Parameter \"type_name\" must not be null"); }
    std::string type_name_cpp(type_name);
        *out_result = new ifcopenshell_parse_instance_list_t{self_cpp->instances_by_type_excl_subtypes(type_name_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_add(ifcopenshell_file_t* self, ifcopenshell_instance_t* entity, int32_t instance_id, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (entity == nullptr) { throw std::runtime_error("Handle parameter \"entity\" must not be null"); }
    const auto& entity_cpp = entity->value;
    auto instance_id_cpp = static_cast<int>(instance_id);
        auto result_value = self_cpp->add_entity(entity_cpp, instance_id_cpp);
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_add_type_ref(ifcopenshell_file_t* self, ifcopenshell_instance_t* new_entity) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (new_entity == nullptr) { throw std::runtime_error("Handle parameter \"new_entity\" must not be null"); }
    const auto& new_entity_cpp = new_entity->value;
        self_cpp->add_type_ref(new_entity_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_batch(ifcopenshell_file_t* self) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        self_cpp->batch();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_build_inverses(ifcopenshell_file_t* self) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        self_cpp->build_inverses();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_build_inverses_(ifcopenshell_file_t* self, ifcopenshell_instance_t* entity) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (entity == nullptr) { throw std::runtime_error("Handle parameter \"entity\" must not be null"); }
    const auto& entity_cpp = entity->value;
        self_cpp->build_inverses_(entity_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_bypass_type(ifcopenshell_file_t* self, const char* type_name) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (type_name == nullptr) { throw std::runtime_error("Parameter \"type_name\" must not be null"); }
    std::string type_name_cpp(type_name);
        self_cpp->bypass_type(type_name_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_create_timestamp(ifcopenshell_file_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->create_timestamp());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_fresh_id(ifcopenshell_file_t* self, uint32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<uint32_t>(self_cpp->fresh_id());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_get_inverse_indices_by_id(ifcopenshell_file_t* self, int32_t instance_id, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto instance_id_cpp = static_cast<int>(instance_id);
        *out_result = make_int32_list(self_cpp->get_inverse_indices_by_id(instance_id_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_get_max_id(ifcopenshell_file_t* self, uint32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<uint32_t>(self_cpp->get_max_id());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_get_total_inverses_by_id(ifcopenshell_file_t* self, int32_t instance_id, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto instance_id_cpp = static_cast<int>(instance_id);
        *out_result = static_cast<size_t>(self_cpp->get_total_inverses(instance_id_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_ifcroot_type(ifcopenshell_file_t* self, ifcopenshell_declaration_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->ifcroot_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_declaration_t{const_cast<ifcopenshell::declaration*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_initialize(ifcopenshell_file_t* self, const char* path, int32_t type, bool read_only, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (path == nullptr) { throw std::runtime_error("Parameter \"path\" must not be null"); }
    std::string path_cpp(path);
    auto type_cpp = static_cast<ifcopenshell::filetype>(type);
    auto read_only_cpp = static_cast<bool>(read_only);
        *out_result = self_cpp->initialize(path_cpp, type_cpp, read_only_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_by_guid(ifcopenshell_file_t* self, const char* global_id, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (global_id == nullptr) { throw std::runtime_error("Parameter \"global_id\" must not be null"); }
    std::string global_id_cpp(global_id);
        auto result_value = self_cpp->instance_by_guid(global_id_cpp);
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_by_id(ifcopenshell_file_t* self, int32_t instance_id, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto instance_id_cpp = static_cast<int>(instance_id);
        auto result_value = self_cpp->instance_by_id(instance_id_cpp);
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_instances_by_reference(ifcopenshell_file_t* self, int32_t reference_id, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto reference_id_cpp = static_cast<int>(reference_id);
        *out_result = new ifcopenshell_parse_instance_list_t{self_cpp->instances_by_reference(reference_id_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_process_deletion_inverse(ifcopenshell_file_t* self, ifcopenshell_instance_t* entity) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (entity == nullptr) { throw std::runtime_error("Handle parameter \"entity\" must not be null"); }
    const auto& entity_cpp = entity->value;
        self_cpp->process_deletion_inverse(entity_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_recalculate_id_counter(ifcopenshell_file_t* self) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        self_cpp->recalculate_id_counter();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_remove(ifcopenshell_file_t* self, ifcopenshell_instance_t* entity) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (entity == nullptr) { throw std::runtime_error("Handle parameter \"entity\" must not be null"); }
    const auto& entity_cpp = entity->value;
        self_cpp->remove_entity(entity_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_remove_type_ref(ifcopenshell_file_t* self, ifcopenshell_instance_t* new_entity) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (new_entity == nullptr) { throw std::runtime_error("Handle parameter \"new_entity\" must not be null"); }
    const auto& new_entity_cpp = new_entity->value;
        self_cpp->remove_type_ref(new_entity_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_reset_identity_cache(ifcopenshell_file_t* self) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        self_cpp->reset_identity_cache();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_schema(ifcopenshell_file_t* self, ifcopenshell_schema_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->schema();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_schema_t{const_cast<ifcopenshell::schema_definition*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_traverse(ifcopenshell_file_t* self, ifcopenshell_instance_t* instance, int32_t max_depth, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (instance == nullptr) { throw std::runtime_error("Handle parameter \"instance\" must not be null"); }
    const auto& instance_cpp = instance->value;
    auto max_depth_cpp = static_cast<int>(max_depth);
        *out_result = new ifcopenshell_parse_instance_list_t{self_cpp->traverse(instance_cpp, max_depth_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_traverse_breadth_first(ifcopenshell_file_t* self, ifcopenshell_instance_t* instance, int32_t max_depth, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (instance == nullptr) { throw std::runtime_error("Handle parameter \"instance\" must not be null"); }
    const auto& instance_cpp = instance->value;
    auto max_depth_cpp = static_cast<int>(max_depth);
        *out_result = new ifcopenshell_parse_instance_list_t{self_cpp->traverse_breadth_first(instance_cpp, max_depth_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_unbatch(ifcopenshell_file_t* self) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        self_cpp->unbatch();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_declaration(ifcopenshell_instance_t* self, ifcopenshell_declaration_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = new ifcopenshell_declaration_t{const_cast<ifcopenshell::declaration*>(&(self_cpp->declaration())), false};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_file(ifcopenshell_instance_t* self, ifcopenshell_file_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        auto result_value = self_cpp->file();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_t{result_value, false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_get_argument(ifcopenshell_instance_t* self, size_t attribute_index, ifcopenshell_parse_attribute_value_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto attribute_index_cpp = static_cast<size_t>(attribute_index);
        *out_result = new ifcopenshell_parse_attribute_value_t{self_cpp->get_attribute_value(attribute_index_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_id(ifcopenshell_instance_t* self, uint32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) {
        *out_result = false;
        return true;
    }
    auto* self_cpp = &self->value;
        *out_result = static_cast<uint32_t>(self_cpp->id());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_identity(ifcopenshell_instance_t* self, uint32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) {
        *out_result = false;
        return true;
    }
    auto* self_cpp = &self->value;
        *out_result = static_cast<uint32_t>(self_cpp->identity());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_schema_declaration_by_name(ifcopenshell_schema_t* self, const char* name, ifcopenshell_declaration_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto result_value = self_cpp->declaration_by_name(name_cpp);
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_declaration_t{const_cast<ifcopenshell::declaration*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_schema_declaration_by_index(ifcopenshell_schema_t* self, size_t declaration_index, ifcopenshell_declaration_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto declaration_index_cpp = static_cast<size_t>(declaration_index);
        auto result_value = self_cpp->declaration_by_name(declaration_index_cpp);
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_declaration_t{const_cast<ifcopenshell::declaration*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_schema_declarations(ifcopenshell_schema_t* self, ifcopenshell_declaration_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_declaration_list(self_cpp->declarations());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_schema_entities(ifcopenshell_schema_t* self, ifcopenshell_entity_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_entity_list(self_cpp->entities());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_schema_enumeration_types(ifcopenshell_schema_t* self, ifcopenshell_enumeration_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_enumeration_list(self_cpp->enumeration_types());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_schema_name(ifcopenshell_schema_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->name());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_schema_select_types(ifcopenshell_schema_t* self, ifcopenshell_select_type_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_select_type_list(self_cpp->select_types());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_schema_type_declarations(ifcopenshell_schema_t* self, ifcopenshell_type_declaration_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_type_declaration_list(self_cpp->type_declarations());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_declaration_is_a(ifcopenshell_declaration_t* self, const char* name, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        *out_result = self_cpp->is(name_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_declaration_as_entity(ifcopenshell_declaration_t* self, ifcopenshell_entity_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_entity();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_entity_t{const_cast<ifcopenshell::entity*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_declaration_as_enumeration_type(ifcopenshell_declaration_t* self, ifcopenshell_enumeration_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_enumeration_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_enumeration_t{const_cast<ifcopenshell::enumeration_type*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_declaration_as_select_type(ifcopenshell_declaration_t* self, ifcopenshell_select_type_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_select_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_select_type_t{const_cast<ifcopenshell::select_type*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_declaration_as_type_declaration(ifcopenshell_declaration_t* self, ifcopenshell_type_declaration_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_type_declaration();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_type_declaration_t{const_cast<ifcopenshell::type_declaration*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_declaration_index_in_schema(ifcopenshell_declaration_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->index_in_schema());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_declaration_name(ifcopenshell_declaration_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->name());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_declaration_name_uc(ifcopenshell_declaration_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->name_uc());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_declaration_schema(ifcopenshell_declaration_t* self, ifcopenshell_schema_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->schema();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_schema_t{const_cast<ifcopenshell::schema_definition*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_declaration_type(ifcopenshell_declaration_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->type());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_type_declaration_as_type_declaration(ifcopenshell_type_declaration_t* self, ifcopenshell_type_declaration_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_type_declaration();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_type_declaration_t{const_cast<ifcopenshell::type_declaration*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_type_declaration_declared_type(ifcopenshell_type_declaration_t* self, ifcopenshell_parameter_type_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->declared_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_parameter_type_t{const_cast<ifcopenshell::parameter_type*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_select_type_as_select_type(ifcopenshell_select_type_t* self, ifcopenshell_select_type_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_select_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_select_type_t{const_cast<ifcopenshell::select_type*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_select_type_select_list(ifcopenshell_select_type_t* self, ifcopenshell_declaration_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_declaration_list(self_cpp->select_list());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_enumeration_as_enumeration_type(ifcopenshell_enumeration_t* self, ifcopenshell_enumeration_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_enumeration_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_enumeration_t{const_cast<ifcopenshell::enumeration_type*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_enumeration_enumeration_items(ifcopenshell_enumeration_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string_list(self_cpp->enumeration_items());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_enumeration_lookup_enum_offset(ifcopenshell_enumeration_t* self, const char* value_name, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (value_name == nullptr) { throw std::runtime_error("Parameter \"value_name\" must not be null"); }
    std::string value_name_cpp(value_name);
        *out_result = static_cast<size_t>(self_cpp->lookup_enum_offset(value_name_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_enumeration_lookup_enum_value(ifcopenshell_enumeration_t* self, size_t i, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto i_cpp = static_cast<size_t>(i);
        *out_result = make_string(self_cpp->lookup_enum_value(i_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parameter_type_as_aggregation_type(ifcopenshell_parameter_type_t* self, ifcopenshell_aggregation_type_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_aggregation_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_aggregation_type_t{const_cast<ifcopenshell::aggregation_type*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parameter_type_as_named_type(ifcopenshell_parameter_type_t* self, ifcopenshell_named_type_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_named_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_named_type_t{const_cast<ifcopenshell::named_type*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parameter_type_as_simple_type(ifcopenshell_parameter_type_t* self, ifcopenshell_simple_type_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_simple_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_simple_type_t{const_cast<ifcopenshell::simple_type*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_named_type_is_a(ifcopenshell_named_type_t* self, const char* name, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        *out_result = self_cpp->is(name_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_named_type_as_named_type(ifcopenshell_named_type_t* self, ifcopenshell_named_type_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_named_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_named_type_t{const_cast<ifcopenshell::named_type*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_named_type_declared_type(ifcopenshell_named_type_t* self, ifcopenshell_declaration_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->declared_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_declaration_t{result_value, false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_simple_type_as_simple_type(ifcopenshell_simple_type_t* self, ifcopenshell_simple_type_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_simple_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_simple_type_t{const_cast<ifcopenshell::simple_type*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_simple_type_declared_type(ifcopenshell_simple_type_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->declared_type());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_aggregation_type_as_aggregation_type(ifcopenshell_aggregation_type_t* self, ifcopenshell_aggregation_type_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_aggregation_type();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_aggregation_type_t{const_cast<ifcopenshell::aggregation_type*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_aggregation_type_bound1(ifcopenshell_aggregation_type_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->bound1());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_aggregation_type_bound2(ifcopenshell_aggregation_type_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->bound2());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_aggregation_type_type_of_element(ifcopenshell_aggregation_type_t* self, ifcopenshell_parameter_type_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->type_of_element();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_parameter_type_t{result_value, false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_header_file(ifcopenshell_header_t* self, ifcopenshell_file_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->owner_file();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_t{result_value, false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_header_file_description(ifcopenshell_header_t* self, ifcopenshell_file_description_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->file_description();
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_description_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_header_file_name(ifcopenshell_header_t* self, ifcopenshell_file_name_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->file_name();
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_name_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_header_file_schema(ifcopenshell_header_t* self, ifcopenshell_file_schema_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->file_schema();
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_schema_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_description_class(ifcopenshell_file_description_t* self, ifcopenshell_entity_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = new ifcopenshell_entity_t{const_cast<ifcopenshell::entity*>(&(self_cpp->Class())), false};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_description_description(ifcopenshell_file_description_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = make_string_list(self_cpp->description());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_description_implementation_level(ifcopenshell_file_description_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = make_string(self_cpp->implementation_level());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_description_initialize(ifcopenshell_file_description_t* self, const ifcopenshell_string_list_t* v1_description, const char* v2_implementation_level, ifcopenshell_file_description_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v1_description == nullptr) { throw std::runtime_error("Parameter \"v1_description\" must not be null"); }
    auto v1_description_cpp = to_cpp_string_list(v1_description);
    if (v2_implementation_level == nullptr) { throw std::runtime_error("Parameter \"v2_implementation_level\" must not be null"); }
    std::string v2_implementation_level_cpp(v2_implementation_level);
        auto result_value = self_cpp->initialize(v1_description_cpp, v2_implementation_level_cpp);
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_description_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_description_setdescription(ifcopenshell_file_description_t* self, const ifcopenshell_string_list_t* v) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v == nullptr) { throw std::runtime_error("Parameter \"v\" must not be null"); }
    auto v_cpp = to_cpp_string_list(v);
        self_cpp->setdescription(v_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_description_setimplementation_level(ifcopenshell_file_description_t* self, const char* v) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v == nullptr) { throw std::runtime_error("Parameter \"v\" must not be null"); }
    std::string v_cpp(v);
        self_cpp->setimplementation_level(v_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_class(ifcopenshell_file_name_t* self, ifcopenshell_entity_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = new ifcopenshell_entity_t{const_cast<ifcopenshell::entity*>(&(self_cpp->Class())), false};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_author(ifcopenshell_file_name_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = make_string_list(self_cpp->author());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_authorization(ifcopenshell_file_name_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = make_string(self_cpp->authorization());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_initialize(ifcopenshell_file_name_t* self, const char* v1_name, const char* v2_time_stamp, const ifcopenshell_string_list_t* v3_author, const ifcopenshell_string_list_t* v4_organization, const char* v5_preprocessor_version, const char* v6_originating_system, const char* v7_authorization, ifcopenshell_file_name_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v1_name == nullptr) { throw std::runtime_error("Parameter \"v1_name\" must not be null"); }
    std::string v1_name_cpp(v1_name);
    if (v2_time_stamp == nullptr) { throw std::runtime_error("Parameter \"v2_time_stamp\" must not be null"); }
    std::string v2_time_stamp_cpp(v2_time_stamp);
    if (v3_author == nullptr) { throw std::runtime_error("Parameter \"v3_author\" must not be null"); }
    auto v3_author_cpp = to_cpp_string_list(v3_author);
    if (v4_organization == nullptr) { throw std::runtime_error("Parameter \"v4_organization\" must not be null"); }
    auto v4_organization_cpp = to_cpp_string_list(v4_organization);
    if (v5_preprocessor_version == nullptr) { throw std::runtime_error("Parameter \"v5_preprocessor_version\" must not be null"); }
    std::string v5_preprocessor_version_cpp(v5_preprocessor_version);
    if (v6_originating_system == nullptr) { throw std::runtime_error("Parameter \"v6_originating_system\" must not be null"); }
    std::string v6_originating_system_cpp(v6_originating_system);
    if (v7_authorization == nullptr) { throw std::runtime_error("Parameter \"v7_authorization\" must not be null"); }
    std::string v7_authorization_cpp(v7_authorization);
        auto result_value = self_cpp->initialize(v1_name_cpp, v2_time_stamp_cpp, v3_author_cpp, v4_organization_cpp, v5_preprocessor_version_cpp, v6_originating_system_cpp, v7_authorization_cpp);
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_name_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_name(ifcopenshell_file_name_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = make_string(self_cpp->name());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_organization(ifcopenshell_file_name_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = make_string_list(self_cpp->organization());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_originating_system(ifcopenshell_file_name_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = make_string(self_cpp->originating_system());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_preprocessor_version(ifcopenshell_file_name_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = make_string(self_cpp->preprocessor_version());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_setauthor(ifcopenshell_file_name_t* self, const ifcopenshell_string_list_t* v) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v == nullptr) { throw std::runtime_error("Parameter \"v\" must not be null"); }
    auto v_cpp = to_cpp_string_list(v);
        self_cpp->setauthor(v_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_setauthorization(ifcopenshell_file_name_t* self, const char* v) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v == nullptr) { throw std::runtime_error("Parameter \"v\" must not be null"); }
    std::string v_cpp(v);
        self_cpp->setauthorization(v_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_setname(ifcopenshell_file_name_t* self, const char* v) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v == nullptr) { throw std::runtime_error("Parameter \"v\" must not be null"); }
    std::string v_cpp(v);
        self_cpp->setname(v_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_setorganization(ifcopenshell_file_name_t* self, const ifcopenshell_string_list_t* v) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v == nullptr) { throw std::runtime_error("Parameter \"v\" must not be null"); }
    auto v_cpp = to_cpp_string_list(v);
        self_cpp->setorganization(v_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_setoriginating_system(ifcopenshell_file_name_t* self, const char* v) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v == nullptr) { throw std::runtime_error("Parameter \"v\" must not be null"); }
    std::string v_cpp(v);
        self_cpp->setoriginating_system(v_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_setpreprocessor_version(ifcopenshell_file_name_t* self, const char* v) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v == nullptr) { throw std::runtime_error("Parameter \"v\" must not be null"); }
    std::string v_cpp(v);
        self_cpp->setpreprocessor_version(v_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_settime_stamp(ifcopenshell_file_name_t* self, const char* v) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v == nullptr) { throw std::runtime_error("Parameter \"v\" must not be null"); }
    std::string v_cpp(v);
        self_cpp->settime_stamp(v_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_name_time_stamp(ifcopenshell_file_name_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = make_string(self_cpp->time_stamp());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_schema_class(ifcopenshell_file_schema_t* self, ifcopenshell_entity_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = new ifcopenshell_entity_t{const_cast<ifcopenshell::entity*>(&(self_cpp->Class())), false};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_schema_initialize(ifcopenshell_file_schema_t* self, const ifcopenshell_string_list_t* v1_schema_identifiers, ifcopenshell_file_schema_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v1_schema_identifiers == nullptr) { throw std::runtime_error("Parameter \"v1_schema_identifiers\" must not be null"); }
    auto v1_schema_identifiers_cpp = to_cpp_string_list(v1_schema_identifiers);
        auto result_value = self_cpp->initialize(v1_schema_identifiers_cpp);
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_schema_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_schema_schema_identifiers(ifcopenshell_file_schema_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = make_string_list(self_cpp->schema_identifiers());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_schema_setschema_identifiers(ifcopenshell_file_schema_t* self, const ifcopenshell_string_list_t* v) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (v == nullptr) { throw std::runtime_error("Parameter \"v\" must not be null"); }
    auto v_cpp = to_cpp_string_list(v);
        self_cpp->setschema_identifiers(v_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_attribute_index(ifcopenshell_entity_t* self, const char* attr_name, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (attr_name == nullptr) { throw std::runtime_error("Parameter \"attr_name\" must not be null"); }
    std::string attr_name_cpp(attr_name);
        *out_result = static_cast<int32_t>(self_cpp->attribute_index(attr_name_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_all_attributes(ifcopenshell_entity_t* self, ifcopenshell_attribute_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_attribute_list(self_cpp->all_attributes());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_all_inverse_attributes(ifcopenshell_entity_t* self, ifcopenshell_inverse_attribute_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_inverse_attribute_list(self_cpp->all_inverse_attributes());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_as_entity(ifcopenshell_entity_t* self, ifcopenshell_entity_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->as_entity();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_entity_t{const_cast<ifcopenshell::entity*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_attribute_by_index(ifcopenshell_entity_t* self, size_t index, ifcopenshell_attribute_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto index_cpp = static_cast<size_t>(index);
        auto result_value = self_cpp->attribute_by_index(index_cpp);
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_attribute_t{const_cast<ifcopenshell::attribute*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_attribute_count(ifcopenshell_entity_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<size_t>(self_cpp->attribute_count());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_attributes(ifcopenshell_entity_t* self, ifcopenshell_attribute_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_attribute_list(self_cpp->attributes());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_derived(ifcopenshell_entity_t* self, ifcopenshell_bool_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_bool_list(self_cpp->derived());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_inverse_attributes(ifcopenshell_entity_t* self, ifcopenshell_inverse_attribute_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_inverse_attribute_list(self_cpp->inverse_attributes());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_is_abstract(ifcopenshell_entity_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->is_abstract();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_set_attributes(ifcopenshell_entity_t* self, const ifcopenshell_attribute_list_t* attributes, const ifcopenshell_bool_list_t* derived) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (attributes == nullptr) { throw std::runtime_error("Parameter \"attributes\" must not be null"); }
    auto attributes_cpp = to_cpp_attribute_list(attributes);
    if (derived == nullptr) { throw std::runtime_error("Parameter \"derived\" must not be null"); }
    auto derived_cpp = to_cpp_bool_list(derived);
        self_cpp->set_attributes(attributes_cpp, derived_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_set_inverse_attributes(ifcopenshell_entity_t* self, const ifcopenshell_inverse_attribute_list_t* inverse_attributes) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (inverse_attributes == nullptr) { throw std::runtime_error("Parameter \"inverse_attributes\" must not be null"); }
    auto inverse_attributes_cpp = to_cpp_inverse_attribute_list(inverse_attributes);
        self_cpp->set_inverse_attributes(inverse_attributes_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_set_subtypes(ifcopenshell_entity_t* self, const ifcopenshell_entity_list_t* subtypes) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (subtypes == nullptr) { throw std::runtime_error("Parameter \"subtypes\" must not be null"); }
    auto subtypes_cpp = to_cpp_entity_list(subtypes);
        self_cpp->set_subtypes(subtypes_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_subtypes(ifcopenshell_entity_t* self, ifcopenshell_entity_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_entity_list(self_cpp->subtypes());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_supertype(ifcopenshell_entity_t* self, ifcopenshell_entity_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->supertype();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_entity_t{const_cast<ifcopenshell::entity*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_attribute_name(ifcopenshell_attribute_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->name());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_attribute_optional(ifcopenshell_attribute_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->optional();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_attribute_type_of_attribute(ifcopenshell_attribute_t* self, ifcopenshell_parameter_type_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->type_of_attribute();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_parameter_type_t{const_cast<ifcopenshell::parameter_type*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_inverse_attribute_attribute_reference(ifcopenshell_inverse_attribute_t* self, ifcopenshell_attribute_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->attribute_reference();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_attribute_t{const_cast<ifcopenshell::attribute*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_inverse_attribute_bound1(ifcopenshell_inverse_attribute_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->bound1());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_inverse_attribute_bound2(ifcopenshell_inverse_attribute_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->bound2());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_inverse_attribute_entity_reference(ifcopenshell_inverse_attribute_t* self, ifcopenshell_entity_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->entity_reference();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_entity_t{const_cast<ifcopenshell::entity*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_inverse_attribute_name(ifcopenshell_inverse_attribute_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->name());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_streamer_bypassed_instances(ifcopenshell_instance_streamer_t* self, ifcopenshell_uint32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_uint32_list(self_cpp->bypassed_instances());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_streamer_has_semicolon(ifcopenshell_instance_streamer_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->has_semicolon();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_streamer_push_page(ifcopenshell_instance_streamer_t* self, const char* page_data) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (page_data == nullptr) { throw std::runtime_error("Parameter \"page_data\" must not be null"); }
    std::string page_data_cpp(page_data);
        self_cpp->push_page(page_data_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_streamer_semicolon_count(ifcopenshell_instance_streamer_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<size_t>(self_cpp->semicolon_count());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_edges(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_int32_list(self_cpp->edges());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_edges_item_ids(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_int32_list(self_cpp->edges_item_ids());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_faces(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_int32_list(self_cpp->faces());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_item_ids(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_int32_list(self_cpp->item_ids());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_material_ids(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_int32_list(self_cpp->material_ids());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_materials(ifcopenshell_geom_triangulation_t* self, ifcopenshell_geom_taxonomy_style_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_geom_taxonomy_style_list(self_cpp->materials());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_normals(ifcopenshell_geom_triangulation_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(self_cpp->normals());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_polyhedral_faces_with_holes(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_list_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_int32_list_list_list(self_cpp->polyhedral_faces_with_holes());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_polyhedral_faces_without_holes(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_int32_list_list(self_cpp->polyhedral_faces_without_holes());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_uvs(ifcopenshell_geom_triangulation_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(self_cpp->uvs());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_verts(ifcopenshell_geom_triangulation_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(self_cpp->verts());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_bounds_max(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_taxonomy_point3_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = new ifcopenshell_geom_taxonomy_point3_t{std::make_shared<ifcopenshell::geometry::taxonomy::point3>(self_cpp->bounds_max())};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_bounds_min(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_taxonomy_point3_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = new ifcopenshell_geom_taxonomy_point3_t{std::make_shared<ifcopenshell::geometry::taxonomy::point3>(self_cpp->bounds_min())};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_compute_bounds(ifcopenshell_geom_iterator_t* self, bool with_geometry) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto with_geometry_cpp = static_cast<bool>(with_geometry);
        self_cpp->compute_bounds(with_geometry_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_create(ifcopenshell_geom_iterator_t* self, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->create();
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_file(ifcopenshell_geom_iterator_t* self, ifcopenshell_file_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->file();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_file_t{result_value, false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_get(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_element_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->get();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_element_t{result_value, false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_get_log(ifcopenshell_geom_iterator_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->getLog());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_get_native(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_brep_element_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->get_native();
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_brep_element_t{result_value, false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_get_object(ifcopenshell_geom_iterator_t* self, int32_t id, ifcopenshell_geom_element_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto id_cpp = static_cast<int>(id);
        auto result_value = self_cpp->get_object(id_cpp);
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_element_t{const_cast<IfcGeom::Element*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_get_task_items(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_taxonomy_item_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_geom_taxonomy_item_list(self_cpp->get_task_items());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_get_task_products(ifcopenshell_geom_iterator_t* self, ifcopenshell_instance_list_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_instance_list_list(self_cpp->get_task_products());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_had_error_processing_elements(ifcopenshell_geom_iterator_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->had_error_processing_elements();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_initialize(ifcopenshell_geom_iterator_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->initialize();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_progress(ifcopenshell_geom_iterator_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->progress());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_unit_magnitude(ifcopenshell_geom_iterator_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<double>(self_cpp->unit_magnitude());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_unit_name(ifcopenshell_geom_iterator_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->unit_name());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_representation_calculate_projected_surface_area(ifcopenshell_geom_brep_representation_t* self, ifcopenshell_geom_taxonomy_matrix4_t* ax, double along_x, double along_y, double along_z, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (ax == nullptr || ax->ptr == nullptr) { throw std::runtime_error("Handle parameter \"ax\" is invalid"); }
    const auto& ax_cpp = ax->ptr;
    auto along_x_cpp = static_cast<double&>(along_x);
    auto along_y_cpp = static_cast<double&>(along_y);
    auto along_z_cpp = static_cast<double&>(along_z);
        *out_result = self_cpp->calculate_projected_surface_area(ax_cpp, along_x_cpp, along_y_cpp, along_z_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_representation_entity(ifcopenshell_geom_brep_representation_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->entity());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_representation_id(ifcopenshell_geom_brep_representation_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->id());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_representation_item(ifcopenshell_geom_brep_representation_t* self, int32_t i, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto i_cpp = static_cast<int>(i);
        auto result_value = self_cpp->item(i_cpp);
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{const_cast<IfcGeom::ConversionResultShape*>(result_value), false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_representation_item_id(ifcopenshell_geom_brep_representation_t* self, int32_t i, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto i_cpp = static_cast<int>(i);
        *out_result = static_cast<int32_t>(self_cpp->item_id(i_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_representation_settings(ifcopenshell_geom_brep_representation_t* self, ifcopenshell_geom_settings_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = new ifcopenshell_geom_settings_t{const_cast<ifcopenshell::geometry::Settings*>(&(self_cpp->settings())), false};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_representation_calculate_surface_area(ifcopenshell_geom_brep_representation_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        double result_value{};
        if (self_cpp->calculate_surface_area(result_value)) {
            *out_result = static_cast<double>(result_value);
        } else {
            *out_result = std::numeric_limits<double>::quiet_NaN();
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_representation_calculate_volume(ifcopenshell_geom_brep_representation_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        double result_value{};
        if (self_cpp->calculate_volume(result_value)) {
            *out_result = static_cast<double>(result_value);
        } else {
            *out_result = std::numeric_limits<double>::quiet_NaN();
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_representation_size(ifcopenshell_geom_brep_representation_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->size());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_element_context(ifcopenshell_geom_element_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->context());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_element_guid(ifcopenshell_geom_element_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->guid());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_element_id(ifcopenshell_geom_element_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->id());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_element_name(ifcopenshell_geom_element_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->name());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_element_parent_id(ifcopenshell_geom_element_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->parent_id());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_element_parents(ifcopenshell_geom_element_t* self, ifcopenshell_geom_element_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_geom_element_list(self_cpp->parents());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_element_product(ifcopenshell_geom_element_t* self, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->product();
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_element_transformation(ifcopenshell_geom_element_t* self, ifcopenshell_geom_transformation_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = new ifcopenshell_geom_transformation_t{const_cast<IfcGeom::Transformation*>(&(self_cpp->transformation())), false};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_element_type(ifcopenshell_geom_element_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->type());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_element_unique_id(ifcopenshell_geom_element_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->unique_id());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_element_calculate_projected_surface_area(ifcopenshell_geom_brep_element_t* self, double along_x, double along_y, double along_z, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto along_x_cpp = static_cast<double&>(along_x);
    auto along_y_cpp = static_cast<double&>(along_y);
    auto along_z_cpp = static_cast<double&>(along_z);
        *out_result = self_cpp->calculate_projected_surface_area(along_x_cpp, along_y_cpp, along_z_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_element_geometry(ifcopenshell_geom_brep_element_t* self, ifcopenshell_geom_brep_representation_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = new ifcopenshell_geom_brep_representation_t{const_cast<IfcGeom::Representation::BRep*>(&(self_cpp->geometry())), false};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_element_geometry(ifcopenshell_geom_triangulation_element_t* self, ifcopenshell_geom_triangulation_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = new ifcopenshell_geom_triangulation_t{const_cast<IfcGeom::Representation::Triangulation*>(&(self_cpp->geometry())), false};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serialized_element_geometry(ifcopenshell_geom_serialized_element_t* self, ifcopenshell_geom_serialization_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = new ifcopenshell_geom_serialization_t{const_cast<IfcGeom::Representation::Serialization*>(&(self_cpp->geometry())), false};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_is_manifold(ifcopenshell_geom_conversion_result_shape_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->is_manifold();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_num_edges(ifcopenshell_geom_conversion_result_shape_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->num_edges());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_num_faces(ifcopenshell_geom_conversion_result_shape_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->num_faces());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_num_vertices(ifcopenshell_geom_conversion_result_shape_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->num_vertices());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_surface_area_along_direction(ifcopenshell_geom_conversion_result_shape_t* self, double tol, ifcopenshell_geom_taxonomy_matrix4_t* arg_1, double along_x, double along_y, double along_z, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto tol_cpp = static_cast<double>(tol);
    if (arg_1 == nullptr || arg_1->ptr == nullptr) { throw std::runtime_error("Handle parameter \"arg_1\" is invalid"); }
    const auto& arg_1_cpp = arg_1->ptr;
    auto along_x_cpp = static_cast<double&>(along_x);
    auto along_y_cpp = static_cast<double&>(along_y);
    auto along_z_cpp = static_cast<double&>(along_z);
        *out_result = self_cpp->surface_area_along_direction(tol_cpp, arg_1_cpp, along_x_cpp, along_y_cpp, along_z_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_surface_genus(ifcopenshell_geom_conversion_result_shape_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->surface_genus());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_function_item_evaluator_evaluation_points(ifcopenshell_geom_function_item_evaluator_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(self_cpp->evaluation_points());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_function_item_evaluator_evaluation_points_range(ifcopenshell_geom_function_item_evaluator_t* self, double ustart, double uend, int32_t nsteps, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto ustart_cpp = static_cast<double>(ustart);
    auto uend_cpp = static_cast<double>(uend);
    auto nsteps_cpp = static_cast<unsigned int>(nsteps);
        *out_result = make_double_list(self_cpp->evaluation_points(ustart_cpp, uend_cpp, nsteps_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_function_item_evaluator_evaluate(ifcopenshell_geom_function_item_evaluator_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->evaluate()};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_function_item_evaluator_evaluate_range(ifcopenshell_geom_function_item_evaluator_t* self, double ustart, double uend, int32_t nsteps, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto ustart_cpp = static_cast<double>(ustart);
    auto uend_cpp = static_cast<double>(uend);
    auto nsteps_cpp = static_cast<unsigned int>(nsteps);
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->evaluate(ustart_cpp, uend_cpp, nsteps_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serialization_brep_data(ifcopenshell_geom_serialization_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->brep_data());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serialization_surface_style_ids(ifcopenshell_geom_serialization_t* self, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_int32_list(self_cpp->surface_style_ids());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serialization_surface_styles(ifcopenshell_geom_serialization_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(self_cpp->surface_styles());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_geometry_serializer_geometry_settings(ifcopenshell_geom_geometry_serializer_t* self, ifcopenshell_geom_settings_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = new ifcopenshell_geom_settings_t{const_cast<ifcopenshell::geometry::Settings*>(&(self_cpp->geometry_settings())), false};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_geometry_serializer_settings(ifcopenshell_geom_geometry_serializer_t* self, ifcopenshell_geom_serializer_settings_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = new ifcopenshell_geom_serializer_settings_t{const_cast<ifcopenshell::geometry::SerializerSettings*>(&(self_cpp->settings())), false};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_geometry_serializer_write_triangulation_element(ifcopenshell_geom_geometry_serializer_t* self, ifcopenshell_geom_triangulation_element_t* o) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (o == nullptr || o->ptr == nullptr) { throw std::runtime_error("Handle parameter \"o\" is invalid"); }
    auto o_cpp = o->ptr;
        self_cpp->write(o_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_geometry_serializer_write_brep_element(ifcopenshell_geom_geometry_serializer_t* self, ifcopenshell_geom_brep_element_t* o) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (o == nullptr || o->ptr == nullptr) { throw std::runtime_error("Handle parameter \"o\" is invalid"); }
    auto o_cpp = o->ptr;
        self_cpp->write(o_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_geometry_serializer_finalize(ifcopenshell_geom_geometry_serializer_t* self) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        self_cpp->finalize();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_geometry_serializer_is_tesselated(ifcopenshell_geom_geometry_serializer_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->isTesselated();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_geometry_serializer_is_streaming(ifcopenshell_geom_geometry_serializer_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->is_streaming();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_geometry_serializer_read(ifcopenshell_geom_geometry_serializer_t* self, ifcopenshell_file_t* f, const char* guid, const char* representation_id, int32_t rt, ifcopenshell_geom_element_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (f == nullptr || f->ptr == nullptr) { throw std::runtime_error("Handle parameter \"f\" is invalid"); }
    auto& f_cpp = *f->ptr;
    if (guid == nullptr) { throw std::runtime_error("Parameter \"guid\" must not be null"); }
    std::string guid_cpp(guid);
    if (representation_id == nullptr) { throw std::runtime_error("Parameter \"representation_id\" must not be null"); }
    std::string representation_id_cpp(representation_id);
    auto rt_cpp = static_cast<GeometrySerializer::read_type>(rt);
        auto result_value = self_cpp->read(f_cpp, guid_cpp, representation_id_cpp, rt_cpp);
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_element_t{result_value, false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_geometry_serializer_ready(ifcopenshell_geom_geometry_serializer_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->ready();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_geometry_serializer_set_file(ifcopenshell_geom_geometry_serializer_t* self, ifcopenshell_file_t* arg_0) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (arg_0 == nullptr || arg_0->ptr == nullptr) { throw std::runtime_error("Handle parameter \"arg_0\" is invalid"); }
    auto arg_0_cpp = arg_0->ptr;
        self_cpp->setFile(arg_0_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_geometry_serializer_set_unit_name_and_magnitude(ifcopenshell_geom_geometry_serializer_t* self, const char* name, double magnitude) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
    auto magnitude_cpp = static_cast<float>(magnitude);
        self_cpp->setUnitNameAndMagnitude(name_cpp, magnitude_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_geometry_serializer_write_header(ifcopenshell_geom_geometry_serializer_t* self) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        self_cpp->writeHeader();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_style_has_specularity(ifcopenshell_geom_taxonomy_style_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = self_cpp->has_specularity();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_style_has_transparency(ifcopenshell_geom_taxonomy_style_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = self_cpp->has_transparency();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_opaque_number_to_double(ifcopenshell_geom_opaque_number_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<double>(self_cpp->to_double());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_opaque_number_to_string(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->to_string());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_finalize(ifcopenshell_geom_serializer_t* self) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        self_cpp->finalize();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_is_streaming(ifcopenshell_geom_serializer_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->is_streaming();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_ready(ifcopenshell_geom_serializer_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->ready();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_set_file(ifcopenshell_geom_serializer_t* self, ifcopenshell_file_t* arg_0) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (arg_0 == nullptr || arg_0->ptr == nullptr) { throw std::runtime_error("Handle parameter \"arg_0\" is invalid"); }
    auto arg_0_cpp = arg_0->ptr;
        self_cpp->setFile(arg_0_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_write_header(ifcopenshell_geom_serializer_t* self) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        self_cpp->writeHeader();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_get_type(ifcopenshell_geom_settings_t* self, const char* name, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        *out_result = make_string(self_cpp->get_type(name_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_setting_names(ifcopenshell_geom_settings_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string_list(self_cpp->setting_names());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_settings_get_type(ifcopenshell_geom_serializer_settings_t* self, const char* name, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        *out_result = make_string(self_cpp->get_type(name_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_settings_setting_names(ifcopenshell_geom_serializer_settings_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string_list(self_cpp->setting_names());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_buffer_get_value(ifcopenshell_geom_buffer_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(self_cpp->get_value());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_buffer_is_ready(ifcopenshell_geom_buffer_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->is_ready();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_item_hash(ifcopenshell_geom_taxonomy_item_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<size_t>(self_cpp->hash());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_item_identity(ifcopenshell_geom_taxonomy_item_t* self, uint32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<uint32_t>(self_cpp->identity());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_item_kind(ifcopenshell_geom_taxonomy_item_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<int32_t>(self_cpp->kind());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_enable_face_styles(ifcopenshell_geom_tree_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->enable_face_styles();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_set_enable_face_styles(ifcopenshell_geom_tree_t* self, bool enable) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto enable_cpp = static_cast<bool>(enable);
        self_cpp->enable_face_styles(enable_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_add_file(ifcopenshell_geom_tree_t* self, ifcopenshell_file_t* file, ifcopenshell_geom_settings_t* settings) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (file == nullptr || file->ptr == nullptr) { throw std::runtime_error("Handle parameter \"file\" is invalid"); }
    auto& file_cpp = *file->ptr;
    if (settings == nullptr || settings->ptr == nullptr) { throw std::runtime_error("Handle parameter \"settings\" is invalid"); }
    auto& settings_cpp = *settings->ptr;
        self_cpp->add_file(file_cpp, settings_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_add_iterator(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_iterator_t* iterator) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (iterator == nullptr || iterator->ptr == nullptr) { throw std::runtime_error("Handle parameter \"iterator\" is invalid"); }
    auto& iterator_cpp = *iterator->ptr;
        self_cpp->add_file(iterator_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_clash_clearance_many(ifcopenshell_geom_tree_t* self, const ifcopenshell_instance_list_t* set_a, const ifcopenshell_instance_list_t* set_b, double clearance, bool check_all, ifcopenshell_geom_tree_clash_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (set_a == nullptr) { throw std::runtime_error("Parameter \"set_a\" must not be null"); }
    auto set_a_cpp = to_cpp_instance_list(set_a);
    if (set_b == nullptr) { throw std::runtime_error("Parameter \"set_b\" must not be null"); }
    auto set_b_cpp = to_cpp_instance_list(set_b);
    auto clearance_cpp = static_cast<double>(clearance);
    auto check_all_cpp = static_cast<bool>(check_all);
        *out_result = new ifcopenshell_geom_tree_clash_list_t{new std::vector<IfcGeom::clash>(self_cpp->clash_clearance_many(set_a_cpp, set_b_cpp, clearance_cpp, check_all_cpp)), true};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_clash_collision_many(ifcopenshell_geom_tree_t* self, const ifcopenshell_instance_list_t* set_a, const ifcopenshell_instance_list_t* set_b, bool allow_touching, ifcopenshell_geom_tree_clash_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (set_a == nullptr) { throw std::runtime_error("Parameter \"set_a\" must not be null"); }
    auto set_a_cpp = to_cpp_instance_list(set_a);
    if (set_b == nullptr) { throw std::runtime_error("Parameter \"set_b\" must not be null"); }
    auto set_b_cpp = to_cpp_instance_list(set_b);
    auto allow_touching_cpp = static_cast<bool>(allow_touching);
        *out_result = new ifcopenshell_geom_tree_clash_list_t{new std::vector<IfcGeom::clash>(self_cpp->clash_collision_many(set_a_cpp, set_b_cpp, allow_touching_cpp)), true};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_clash_intersection_many(ifcopenshell_geom_tree_t* self, const ifcopenshell_instance_list_t* set_a, const ifcopenshell_instance_list_t* set_b, double tolerance, bool check_all, ifcopenshell_geom_tree_clash_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (set_a == nullptr) { throw std::runtime_error("Parameter \"set_a\" must not be null"); }
    auto set_a_cpp = to_cpp_instance_list(set_a);
    if (set_b == nullptr) { throw std::runtime_error("Parameter \"set_b\" must not be null"); }
    auto set_b_cpp = to_cpp_instance_list(set_b);
    auto tolerance_cpp = static_cast<double>(tolerance);
    auto check_all_cpp = static_cast<bool>(check_all);
        *out_result = new ifcopenshell_geom_tree_clash_list_t{new std::vector<IfcGeom::clash>(self_cpp->clash_intersection_many(set_a_cpp, set_b_cpp, tolerance_cpp, check_all_cpp)), true};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_distances(ifcopenshell_geom_tree_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(self_cpp->distances());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_is_manifold(ifcopenshell_geom_tree_t* self, const ifcopenshell_int32_list_t* faces, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (faces == nullptr) { throw std::runtime_error("Parameter \"faces\" must not be null"); }
    auto faces_cpp = to_cpp_int32_list(faces);
        *out_result = self_cpp->is_manifold(faces_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_protrusion_distances(ifcopenshell_geom_tree_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(self_cpp->protrusion_distances());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_styles(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_taxonomy_style_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_geom_taxonomy_style_list(self_cpp->styles());
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_uint8_to_b64(ifcopenshell_geom_tree_t* self, const ifcopenshell_uint8_list_t* uuids_array, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (uuids_array == nullptr) { throw std::runtime_error("Parameter \"uuids_array\" must not be null"); }
    auto uuids_array_cpp = to_cpp_uint8_list(uuids_array);
        *out_result = make_string(self_cpp->uint8_to_b64(uuids_array_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_get_bool(ifcopenshell_geom_settings_t* self, const char* name, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto val = self_cpp->get(name_cpp);
        bool matched = false;
        if (auto* p = std::get_if<bool>(&val)) { *out_result = *p; matched = true; }
        if (!matched) { throw std::runtime_error("Setting is not of expected type"); }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_set_bool(ifcopenshell_geom_settings_t* self, const char* name, bool value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        self_cpp->set(name_cpp, ifcopenshell::geometry::Settings::value_variant_t(value));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_get_int(ifcopenshell_geom_settings_t* self, const char* name, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto val = self_cpp->get(name_cpp);
        bool matched = false;
        if (auto* p = std::get_if<int>(&val)) { *out_result = static_cast<int32_t>(*p); matched = true; }
        if (auto* p = std::get_if<ifcopenshell::geometry::settings::IteratorOutputOptions>(&val)) { *out_result = static_cast<int32_t>(*p); matched = true; }
        if (auto* p = std::get_if<ifcopenshell::geometry::settings::FunctionStepMethod>(&val)) { *out_result = static_cast<int32_t>(*p); matched = true; }
        if (auto* p = std::get_if<ifcopenshell::geometry::settings::OutputDimensionalityTypes>(&val)) { *out_result = static_cast<int32_t>(*p); matched = true; }
        if (auto* p = std::get_if<ifcopenshell::geometry::settings::TriangulationMethod>(&val)) { *out_result = static_cast<int32_t>(*p); matched = true; }
        if (!matched) { throw std::runtime_error("Setting is not of expected type"); }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_set_int(ifcopenshell_geom_settings_t* self, const char* name, int32_t value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        self_cpp->set(name_cpp, ifcopenshell::geometry::Settings::value_variant_t(int(value)));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_get_double(ifcopenshell_geom_settings_t* self, const char* name, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto val = self_cpp->get(name_cpp);
        bool matched = false;
        if (auto* p = std::get_if<double>(&val)) { *out_result = static_cast<double>(*p); matched = true; }
        if (!matched) { throw std::runtime_error("Setting is not of expected type"); }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_set_double(ifcopenshell_geom_settings_t* self, const char* name, double value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        self_cpp->set(name_cpp, ifcopenshell::geometry::Settings::value_variant_t(value));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_get_string(ifcopenshell_geom_settings_t* self, const char* name, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto val = self_cpp->get(name_cpp);
        bool matched = false;
        if (auto* p = std::get_if<std::string>(&val)) { *out_result = make_string(*p); matched = true; }
        if (!matched) { throw std::runtime_error("Setting is not of expected type"); }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_set_string(ifcopenshell_geom_settings_t* self, const char* name, const char* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    std::string value_cpp(value);
        self_cpp->set(name_cpp, ifcopenshell::geometry::Settings::value_variant_t(value_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_get_int_set(ifcopenshell_geom_settings_t* self, const char* name, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto val = self_cpp->get(name_cpp);
        bool matched = false;
        if (auto* p = std::get_if<std::set<int>>(&val)) { *out_result = make_int32_list(([&]() { auto tmp = *p; return std::vector(tmp.begin(), tmp.end()); })()); matched = true; }
        if (!matched) { throw std::runtime_error("Setting is not of expected type"); }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_set_int_set(ifcopenshell_geom_settings_t* self, const char* name, const ifcopenshell_int32_list_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    auto value_vec = to_cpp_int32_list(value);
    std::set<int> value_cpp(value_vec.begin(), value_vec.end());
        self_cpp->set(name_cpp, ifcopenshell::geometry::Settings::value_variant_t(value_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_get_string_set(ifcopenshell_geom_settings_t* self, const char* name, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto val = self_cpp->get(name_cpp);
        bool matched = false;
        if (auto* p = std::get_if<std::set<std::string>>(&val)) { *out_result = make_string_list(([&]() { auto tmp = *p; return std::vector(tmp.begin(), tmp.end()); })()); matched = true; }
        if (!matched) { throw std::runtime_error("Setting is not of expected type"); }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_set_string_set(ifcopenshell_geom_settings_t* self, const char* name, const ifcopenshell_string_list_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    auto value_vec = to_cpp_string_list(value);
    std::set<std::string> value_cpp(value_vec.begin(), value_vec.end());
        self_cpp->set(name_cpp, ifcopenshell::geometry::Settings::value_variant_t(value_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_get_double_list(ifcopenshell_geom_settings_t* self, const char* name, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto val = self_cpp->get(name_cpp);
        bool matched = false;
        if (auto* p = std::get_if<std::vector<double>>(&val)) { *out_result = make_double_list(*p); matched = true; }
        if (!matched) { throw std::runtime_error("Setting is not of expected type"); }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_settings_set_double_list(ifcopenshell_geom_settings_t* self, const char* name, const ifcopenshell_double_list_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    auto value_cpp = to_cpp_double_list(value);
        self_cpp->set(name_cpp, ifcopenshell::geometry::Settings::value_variant_t(value_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_settings_get_bool(ifcopenshell_geom_serializer_settings_t* self, const char* name, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto val = self_cpp->get(name_cpp);
        bool matched = false;
        if (auto* p = std::get_if<bool>(&val)) { *out_result = *p; matched = true; }
        if (!matched) { throw std::runtime_error("Setting is not of expected type"); }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_settings_set_bool(ifcopenshell_geom_serializer_settings_t* self, const char* name, bool value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        self_cpp->set(name_cpp, ifcopenshell::geometry::SerializerSettings::value_variant_t(value));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_settings_get_int(ifcopenshell_geom_serializer_settings_t* self, const char* name, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto val = self_cpp->get(name_cpp);
        bool matched = false;
        if (auto* p = std::get_if<int>(&val)) { *out_result = static_cast<int32_t>(*p); matched = true; }
        if (!matched) { throw std::runtime_error("Setting is not of expected type"); }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_settings_set_int(ifcopenshell_geom_serializer_settings_t* self, const char* name, int32_t value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        self_cpp->set(name_cpp, ifcopenshell::geometry::SerializerSettings::value_variant_t(int(value)));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_settings_get_double(ifcopenshell_geom_serializer_settings_t* self, const char* name, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto val = self_cpp->get(name_cpp);
        bool matched = false;
        if (auto* p = std::get_if<double>(&val)) { *out_result = static_cast<double>(*p); matched = true; }
        if (!matched) { throw std::runtime_error("Setting is not of expected type"); }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_settings_set_double(ifcopenshell_geom_serializer_settings_t* self, const char* name, double value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        self_cpp->set(name_cpp, ifcopenshell::geometry::SerializerSettings::value_variant_t(value));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_settings_get_string(ifcopenshell_geom_serializer_settings_t* self, const char* name, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto val = self_cpp->get(name_cpp);
        bool matched = false;
        if (auto* p = std::get_if<std::string>(&val)) { *out_result = make_string(*p); matched = true; }
        if (!matched) { throw std::runtime_error("Setting is not of expected type"); }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_settings_set_string(ifcopenshell_geom_serializer_settings_t* self, const char* name, const char* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    std::string value_cpp(value);
        self_cpp->set(name_cpp, ifcopenshell::geometry::SerializerSettings::value_variant_t(value_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_settings_get_int_set(ifcopenshell_geom_serializer_settings_t* self, const char* name, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        auto val = self_cpp->get(name_cpp);
        bool matched = false;
        if (auto* p = std::get_if<std::set<int>>(&val)) { *out_result = make_int32_list(([&]() { auto tmp = *p; return std::vector(tmp.begin(), tmp.end()); })()); matched = true; }
        if (!matched) { throw std::runtime_error("Setting is not of expected type"); }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_serializer_settings_set_int_set(ifcopenshell_geom_serializer_settings_t* self, const char* name, const ifcopenshell_int32_list_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    auto value_vec = to_cpp_int32_list(value);
    std::set<int> value_cpp(value_vec.begin(), value_vec.end());
        self_cpp->set(name_cpp, ifcopenshell::geometry::SerializerSettings::value_variant_t(value_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_verts_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->verts().size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_faces_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->faces().size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_normals_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->normals().size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_edges_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->edges().size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_material_ids_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->material_ids().size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_item_ids_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->item_ids().size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_edges_item_ids_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->edges_item_ids().size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_uvs_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->uvs().size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_material_count(ifcopenshell_geom_triangulation_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->materials().size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_material_at(ifcopenshell_geom_triangulation_t* self, size_t index, ifcopenshell_geom_taxonomy_style_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        const auto& items = self_cpp->materials();
        if (index >= items.size()) { throw std::runtime_error("Material index out of bounds"); }
        *out_result = new ifcopenshell_geom_taxonomy_style_t{items[index]};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_circle_matrix(ifcopenshell_geom_taxonomy_circle_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->matrix) { throw std::runtime_error("matrix is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_matrix4_t{self_cpp->matrix};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_circle_radius(ifcopenshell_geom_taxonomy_circle_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<double>(self_cpp->radius);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_line_matrix(ifcopenshell_geom_taxonomy_line_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->matrix) { throw std::runtime_error("matrix is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_matrix4_t{self_cpp->matrix};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_line_as_item(ifcopenshell_geom_taxonomy_line_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
        auto result_value = std::static_pointer_cast<ifcopenshell::geometry::taxonomy::item>(self->ptr);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_taxonomy_item_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_plane_matrix(ifcopenshell_geom_taxonomy_plane_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->matrix) { throw std::runtime_error("matrix is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_matrix4_t{self_cpp->matrix};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_ellipse_matrix(ifcopenshell_geom_taxonomy_ellipse_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->matrix) { throw std::runtime_error("matrix is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_matrix4_t{self_cpp->matrix};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_ellipse_radius1(ifcopenshell_geom_taxonomy_ellipse_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<double>(self_cpp->radius);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_ellipse_radius2(ifcopenshell_geom_taxonomy_ellipse_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<double>(self_cpp->radius2);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_style_diffuse(ifcopenshell_geom_taxonomy_style_t* self, ifcopenshell_geom_taxonomy_colour_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = new ifcopenshell_geom_taxonomy_colour_t{std::make_shared<ifcopenshell::geometry::taxonomy::colour>(self_cpp->diffuse)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_style_name(ifcopenshell_geom_taxonomy_style_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = make_string(self_cpp->name);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_style_specular(ifcopenshell_geom_taxonomy_style_t* self, ifcopenshell_geom_taxonomy_colour_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = new ifcopenshell_geom_taxonomy_colour_t{std::make_shared<ifcopenshell::geometry::taxonomy::colour>(self_cpp->specular)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_style_specularity(ifcopenshell_geom_taxonomy_style_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<double>(self_cpp->specularity);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_style_surface(ifcopenshell_geom_taxonomy_style_t* self, ifcopenshell_geom_taxonomy_colour_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = new ifcopenshell_geom_taxonomy_colour_t{std::make_shared<ifcopenshell::geometry::taxonomy::colour>(self_cpp->surface)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_style_transparency(ifcopenshell_geom_taxonomy_style_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<double>(self_cpp->transparency);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_style_use_surface_color(ifcopenshell_geom_taxonomy_style_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = self_cpp->use_surface_color;
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_sphere_matrix(ifcopenshell_geom_taxonomy_sphere_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->matrix) { throw std::runtime_error("matrix is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_matrix4_t{self_cpp->matrix};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_sphere_radius(ifcopenshell_geom_taxonomy_sphere_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<double>(self_cpp->radius);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_torus_matrix(ifcopenshell_geom_taxonomy_torus_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->matrix) { throw std::runtime_error("matrix is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_matrix4_t{self_cpp->matrix};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_torus_radius1(ifcopenshell_geom_taxonomy_torus_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<double>(self_cpp->radius1);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_torus_radius2(ifcopenshell_geom_taxonomy_torus_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<double>(self_cpp->radius2);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_cylinder_matrix(ifcopenshell_geom_taxonomy_cylinder_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->matrix) { throw std::runtime_error("matrix is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_matrix4_t{self_cpp->matrix};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_cylinder_radius(ifcopenshell_geom_taxonomy_cylinder_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<double>(self_cpp->radius);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_extrusion_basis(ifcopenshell_geom_taxonomy_extrusion_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->basis) { throw std::runtime_error("basis is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->basis};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_extrusion_depth(ifcopenshell_geom_taxonomy_extrusion_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<double>(self_cpp->depth);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_extrusion_direction(ifcopenshell_geom_taxonomy_extrusion_t* self, ifcopenshell_geom_taxonomy_direction3_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->direction) { throw std::runtime_error("direction is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_direction3_t{self_cpp->direction};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_extrusion_matrix(ifcopenshell_geom_taxonomy_extrusion_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->matrix) { throw std::runtime_error("matrix is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_matrix4_t{self_cpp->matrix};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_offset_curve_basis(ifcopenshell_geom_taxonomy_offset_curve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->basis) { throw std::runtime_error("basis is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->basis};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_offset_curve_offset(ifcopenshell_geom_taxonomy_offset_curve_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<double>(self_cpp->offset);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_offset_curve_reference(ifcopenshell_geom_taxonomy_offset_curve_t* self, ifcopenshell_geom_taxonomy_direction3_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->reference) { throw std::runtime_error("reference is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_direction3_t{self_cpp->reference};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_offset_curve_as_item(ifcopenshell_geom_taxonomy_offset_curve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
        auto result_value = std::static_pointer_cast<ifcopenshell::geometry::taxonomy::item>(self->ptr);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_taxonomy_item_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_revolve_has_angle(ifcopenshell_geom_taxonomy_revolve_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<bool>(self_cpp->angle);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_revolve_angle(ifcopenshell_geom_taxonomy_revolve_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->angle) { throw std::runtime_error("angle is not set"); }
        *out_result = static_cast<double>(*self_cpp->angle);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_revolve_axis_origin(ifcopenshell_geom_taxonomy_revolve_t* self, ifcopenshell_geom_taxonomy_point3_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->axis_origin) { throw std::runtime_error("axis_origin is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_point3_t{self_cpp->axis_origin};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_revolve_basis(ifcopenshell_geom_taxonomy_revolve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->basis) { throw std::runtime_error("basis is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->basis};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_revolve_direction(ifcopenshell_geom_taxonomy_revolve_t* self, ifcopenshell_geom_taxonomy_direction3_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->direction) { throw std::runtime_error("direction is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_direction3_t{self_cpp->direction};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_revolve_matrix(ifcopenshell_geom_taxonomy_revolve_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->matrix) { throw std::runtime_error("matrix is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_matrix4_t{self_cpp->matrix};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_curve_degree(ifcopenshell_geom_taxonomy_bspline_curve_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<int32_t>(self_cpp->degree);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_curve_knots(ifcopenshell_geom_taxonomy_bspline_curve_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = make_double_list(self_cpp->knots);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_curve_multiplicities(ifcopenshell_geom_taxonomy_bspline_curve_t* self, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = make_int32_list(self_cpp->multiplicities);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_curve_has_weights(ifcopenshell_geom_taxonomy_bspline_curve_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<bool>(self_cpp->weights);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_curve_weights(ifcopenshell_geom_taxonomy_bspline_curve_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->weights) { throw std::runtime_error("weights is not set"); }
        *out_result = make_double_list(*self_cpp->weights);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_curve_control_point_count(ifcopenshell_geom_taxonomy_bspline_curve_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = self_cpp->control_points.size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_curve_control_point_at(ifcopenshell_geom_taxonomy_bspline_curve_t* self, size_t index, ifcopenshell_geom_taxonomy_point3_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (index >= self_cpp->control_points.size()) { throw std::runtime_error("Index out of bounds"); }
        *out_result = new ifcopenshell_geom_taxonomy_point3_t{self_cpp->control_points[index]};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_curve_as_item(ifcopenshell_geom_taxonomy_bspline_curve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
        auto result_value = std::static_pointer_cast<ifcopenshell::geometry::taxonomy::item>(self->ptr);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_taxonomy_item_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_sweep_along_curve_basis(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->basis) { throw std::runtime_error("basis is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->basis};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_sweep_along_curve_has_basis(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = (self_cpp->basis != nullptr);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_sweep_along_curve_curve(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->curve) { throw std::runtime_error("curve is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->curve};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_sweep_along_curve_has_curve(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = (self_cpp->curve != nullptr);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_sweep_along_curve_direction(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, ifcopenshell_geom_taxonomy_direction3_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->direction) { throw std::runtime_error("direction is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_direction3_t{self_cpp->direction};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_sweep_along_curve_has_direction(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = (self_cpp->direction != nullptr);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_sweep_along_curve_matrix(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->matrix) { throw std::runtime_error("matrix is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_matrix4_t{self_cpp->matrix};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_sweep_along_curve_has_matrix(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = (self_cpp->matrix != nullptr);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_sweep_along_curve_surface(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->surface) { throw std::runtime_error("surface is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->surface};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_sweep_along_curve_has_surface(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = (self_cpp->surface != nullptr);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_face_basis(ifcopenshell_geom_taxonomy_face_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->basis) { throw std::runtime_error("basis is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->basis};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_face_loop_count(ifcopenshell_geom_taxonomy_face_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = self_cpp->children.size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_face_loop_at(ifcopenshell_geom_taxonomy_face_t* self, size_t index, ifcopenshell_geom_taxonomy_loop_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (index >= self_cpp->children.size()) { throw std::runtime_error("Index out of bounds"); }
        *out_result = new ifcopenshell_geom_taxonomy_loop_t{self_cpp->children[index]};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_face_matrix(ifcopenshell_geom_taxonomy_face_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->matrix) { throw std::runtime_error("matrix is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_matrix4_t{self_cpp->matrix};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_face_as_item(ifcopenshell_geom_taxonomy_face_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
        auto result_value = std::static_pointer_cast<ifcopenshell::geometry::taxonomy::item>(self->ptr);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_taxonomy_item_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_loft_axis(ifcopenshell_geom_taxonomy_loft_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->axis) { throw std::runtime_error("axis is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->axis};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_loft_has_axis(ifcopenshell_geom_taxonomy_loft_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = (self_cpp->axis != nullptr);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_loft_item_count(ifcopenshell_geom_taxonomy_loft_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = self_cpp->children.size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_loft_item_at(ifcopenshell_geom_taxonomy_loft_t* self, size_t index, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (index >= self_cpp->children.size()) { throw std::runtime_error("Index out of bounds"); }
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->children[index]};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_loft_add_item(ifcopenshell_geom_taxonomy_loft_t* self, ifcopenshell_geom_taxonomy_item_t* item) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
    if (item == nullptr || item->ptr == nullptr) { throw std::runtime_error("Handle parameter \"item\" is invalid"); }
    auto item_cpp = item->ptr;
        auto cast_item = ifcopenshell::geometry::taxonomy::dcast<ifcopenshell::geometry::taxonomy::geom_item>(item_cpp);
        if (!cast_item) { throw std::runtime_error("Invalid item type"); }
        self_cpp->children.push_back(cast_item);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_loft_set_axis(ifcopenshell_geom_taxonomy_loft_t* self, ifcopenshell_geom_taxonomy_item_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
    if (value == nullptr || value->ptr == nullptr) { throw std::runtime_error("Handle parameter \"value\" is invalid"); }
    auto value_cpp = value->ptr;
        self_cpp->axis = value_cpp;
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_loop_edge_count(ifcopenshell_geom_taxonomy_loop_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = self_cpp->children.size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_loop_edge_at(ifcopenshell_geom_taxonomy_loop_t* self, size_t index, ifcopenshell_geom_taxonomy_edge_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (index >= self_cpp->children.size()) { throw std::runtime_error("Index out of bounds"); }
        *out_result = new ifcopenshell_geom_taxonomy_edge_t{self_cpp->children[index]};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_shell_face_count(ifcopenshell_geom_taxonomy_shell_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = self_cpp->children.size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_shell_face_at(ifcopenshell_geom_taxonomy_shell_t* self, size_t index, ifcopenshell_geom_taxonomy_face_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (index >= self_cpp->children.size()) { throw std::runtime_error("Index out of bounds"); }
        *out_result = new ifcopenshell_geom_taxonomy_face_t{self_cpp->children[index]};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_solid_shell_count(ifcopenshell_geom_taxonomy_solid_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = self_cpp->children.size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_solid_shell_at(ifcopenshell_geom_taxonomy_solid_t* self, size_t index, ifcopenshell_geom_taxonomy_shell_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (index >= self_cpp->children.size()) { throw std::runtime_error("Index out of bounds"); }
        *out_result = new ifcopenshell_geom_taxonomy_shell_t{self_cpp->children[index]};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_solid_matrix(ifcopenshell_geom_taxonomy_solid_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (!self_cpp->matrix) { throw std::runtime_error("matrix is not set"); }
        *out_result = new ifcopenshell_geom_taxonomy_matrix4_t{self_cpp->matrix};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_collection_item_count(ifcopenshell_geom_taxonomy_collection_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = self_cpp->children.size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_collection_item_at(ifcopenshell_geom_taxonomy_collection_t* self, size_t index, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (index >= self_cpp->children.size()) { throw std::runtime_error("Index out of bounds"); }
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->children[index]};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_collection_add_item(ifcopenshell_geom_taxonomy_collection_t* self, ifcopenshell_geom_taxonomy_item_t* item) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
    if (item == nullptr || item->ptr == nullptr) { throw std::runtime_error("Handle parameter \"item\" is invalid"); }
    auto item_cpp = item->ptr;
        auto cast_item = ifcopenshell::geometry::taxonomy::dcast<ifcopenshell::geometry::taxonomy::geom_item>(item_cpp);
        if (!cast_item) { throw std::runtime_error("Invalid item type"); }
        self_cpp->children.push_back(cast_item);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_boolean_result_operation(ifcopenshell_geom_taxonomy_boolean_result_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<int32_t>(self_cpp->operation);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_boolean_result_item_count(ifcopenshell_geom_taxonomy_boolean_result_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = self_cpp->children.size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_boolean_result_item_at(ifcopenshell_geom_taxonomy_boolean_result_t* self, size_t index, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        if (index >= self_cpp->children.size()) { throw std::runtime_error("Index out of bounds"); }
        *out_result = new ifcopenshell_geom_taxonomy_item_t{self_cpp->children[index]};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_boolean_result_add_item(ifcopenshell_geom_taxonomy_boolean_result_t* self, ifcopenshell_geom_taxonomy_item_t* item) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
    if (item == nullptr || item->ptr == nullptr) { throw std::runtime_error("Handle parameter \"item\" is invalid"); }
    auto item_cpp = item->ptr;
        auto cast_item = ifcopenshell::geometry::taxonomy::dcast<ifcopenshell::geometry::taxonomy::geom_item>(item_cpp);
        if (!cast_item) { throw std::runtime_error("Invalid item type"); }
        self_cpp->children.push_back(cast_item);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_degree_u(ifcopenshell_geom_taxonomy_bspline_surface_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<int32_t>(self_cpp->degree[0]);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_degree_v(ifcopenshell_geom_taxonomy_bspline_surface_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<int32_t>(self_cpp->degree[1]);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_multiplicities_u(ifcopenshell_geom_taxonomy_bspline_surface_t* self, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = make_int32_list(self_cpp->multiplicities[0]);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_multiplicities_v(ifcopenshell_geom_taxonomy_bspline_surface_t* self, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = make_int32_list(self_cpp->multiplicities[1]);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_knots_u(ifcopenshell_geom_taxonomy_bspline_surface_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = make_double_list(self_cpp->knots[0]);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_knots_v(ifcopenshell_geom_taxonomy_bspline_surface_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = make_double_list(self_cpp->knots[1]);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_as_item(ifcopenshell_geom_taxonomy_bspline_surface_t* self, ifcopenshell_geom_taxonomy_item_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
        auto result_value = std::static_pointer_cast<ifcopenshell::geometry::taxonomy::item>(self->ptr);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_taxonomy_item_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_style_count(ifcopenshell_geom_tree_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = self_cpp->styles().size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_style_at(ifcopenshell_geom_tree_t* self, size_t index, ifcopenshell_geom_taxonomy_style_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        const auto& items = self_cpp->styles();
        if (index >= items.size()) { throw std::out_of_range("Style index out of range"); }
        *out_result = new ifcopenshell_geom_taxonomy_style_t{items[index]};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_clash_a(ifcopenshell_geom_tree_clash_t* self, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->a;
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_clash_b(ifcopenshell_geom_tree_clash_t* self, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = self_cpp->b;
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_clash_type(ifcopenshell_geom_tree_clash_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->clash_type);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_clash_distance(ifcopenshell_geom_tree_clash_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<double>(self_cpp->distance);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_clash_p1(ifcopenshell_geom_tree_clash_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(transform_sequence(std::vector<double>(self_cpp->p1.begin(), self_cpp->p1.end()), [](auto&& item) { return item; }));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_clash_p2(ifcopenshell_geom_tree_clash_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(transform_sequence(std::vector<double>(self_cpp->p2.begin(), self_cpp->p2.end()), [](auto&& item) { return item; }));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_ray_intersection_distance(ifcopenshell_geom_tree_ray_intersection_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<double>(self_cpp->distance);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_ray_intersection_dot_product(ifcopenshell_geom_tree_ray_intersection_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<double>(self_cpp->dot_product);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_ray_intersection_normal(ifcopenshell_geom_tree_ray_intersection_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(transform_sequence(std::vector<double>(self_cpp->normal.begin(), self_cpp->normal.end()), [](auto&& item) { return item; }));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_ray_intersection_position(ifcopenshell_geom_tree_ray_intersection_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(transform_sequence(std::vector<double>(self_cpp->position.begin(), self_cpp->position.end()), [](auto&& item) { return item; }));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_ray_intersection_ray_distance(ifcopenshell_geom_tree_ray_intersection_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<double>(self_cpp->ray_distance);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_ray_intersection_style_index(ifcopenshell_geom_tree_ray_intersection_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(self_cpp->style_index);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_point3_get_data(ifcopenshell_geom_taxonomy_point3_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        const auto& v = self_cpp->ccomponents();
        *out_result = make_double_list(std::vector<double>{{v(0), v(1), v(2)}});
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_direction3_get_data(ifcopenshell_geom_taxonomy_direction3_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        const auto& v = self_cpp->ccomponents();
        *out_result = make_double_list(std::vector<double>{{v(0), v(1), v(2)}});
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_matrix4_get_data(ifcopenshell_geom_taxonomy_matrix4_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        std::vector<double> data(16);
        const auto& mat = self_cpp->ccomponents();
        for (int i = 0; i < 4; ++i) {
            for (int j = 0; j < 4; ++j) {
                data[i * 4 + j] = mat(i, j);
            }
        }
        *out_result = make_double_list(data);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_colour_get_data(ifcopenshell_geom_taxonomy_colour_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        const auto& v = self_cpp->ccomponents();
        *out_result = make_double_list(std::vector<double>{{v(0), v(1), v(2)}});
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_transformation_matrix(ifcopenshell_geom_transformation_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        std::vector<double> data(16);
        const auto& mat = self_cpp->data()->ccomponents();
        for (int i = 0; i < 4; ++i) {
            for (int j = 0; j < 4; ++j) {
                data[i * 4 + j] = mat(i, j);
            }
        }
        *out_result = make_double_list(data);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_clash_count(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_tree_clash_list_t* clashes, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (clashes == nullptr || clashes->ptr == nullptr) { throw std::runtime_error("Handle parameter \"clashes\" is invalid"); }
    auto clashes_cpp = clashes->ptr;
        (void)self_cpp;
        *out_result = clashes_cpp->size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_clash_at(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_tree_clash_list_t* clashes, size_t index, ifcopenshell_geom_tree_clash_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (clashes == nullptr || clashes->ptr == nullptr) { throw std::runtime_error("Handle parameter \"clashes\" is invalid"); }
    auto clashes_cpp = clashes->ptr;
        (void)self_cpp;
        if (index >= clashes_cpp->size()) { throw std::out_of_range("Clash index out of range"); }
        auto result_value = std::unique_ptr<IfcGeom::clash>(new IfcGeom::clash((*clashes_cpp)[index]));
        *out_result = new ifcopenshell_geom_tree_clash_t{result_value.release(), true};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_ray_intersection_count(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_tree_ray_intersection_list_t* intersections, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (intersections == nullptr || intersections->ptr == nullptr) { throw std::runtime_error("Handle parameter \"intersections\" is invalid"); }
    auto intersections_cpp = intersections->ptr;
        (void)self_cpp;
        *out_result = intersections_cpp->size();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_ray_intersection_at(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_tree_ray_intersection_list_t* intersections, size_t index, ifcopenshell_geom_tree_ray_intersection_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (intersections == nullptr || intersections->ptr == nullptr) { throw std::runtime_error("Handle parameter \"intersections\" is invalid"); }
    auto intersections_cpp = intersections->ptr;
        (void)self_cpp;
        if (index >= intersections_cpp->size()) { throw std::out_of_range("Ray intersection index out of range"); }
        auto result_value = std::unique_ptr<IfcGeom::ray_intersection_result>(new IfcGeom::ray_intersection_result((*intersections_cpp)[index]));
        *out_result = new ifcopenshell_geom_tree_ray_intersection_t{result_value.release(), true};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_add_entity(ifcopenshell_file_t* self, ifcopenshell_instance_t* instance, uint32_t id, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (instance == nullptr) { throw std::runtime_error("Handle parameter \"instance\" must not be null"); }
    const auto& instance_cpp = instance->value;
    auto id_cpp = static_cast<unsigned int>(id);
        auto result_value = ifcparse::bindings::add_entity(*self_cpp, instance_cpp, id_cpp);
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_type_declaration_argument_types(ifcopenshell_type_declaration_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string_list(ifcparse::bindings::argument_types(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_enumeration_argument_types(ifcopenshell_enumeration_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string_list(ifcparse::bindings::argument_types(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_entity_argument_types(ifcopenshell_entity_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string_list(ifcparse::bindings::argument_types(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_bool(ifcopenshell_parse_attribute_value_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = ifcparse::bindings::as_bool(self_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_double(ifcopenshell_parse_attribute_value_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = static_cast<double>(ifcparse::bindings::as_double(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_double_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = make_double_list(ifcparse::bindings::as_double_list(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_double_list_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_double_list_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = make_double_list_list(ifcparse::bindings::as_double_list_list(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_enumeration_index(ifcopenshell_parse_attribute_value_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = static_cast<size_t>(ifcparse::bindings::as_enumeration_index(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_enumeration_type(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_enumeration_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        auto result_value = ifcparse::bindings::as_enumeration_type(self_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            auto unwrapped_result = *result_value;
            if (unwrapped_result == nullptr) {
                *out_result = nullptr;
            } else {
                *out_result = new ifcopenshell_enumeration_t{unwrapped_result, false};
            }
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_enumeration_value(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = make_string(ifcparse::bindings::as_enumeration_value(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_instance(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        auto result_value = ifcparse::bindings::as_instance(self_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            auto unwrapped_result = *result_value;
            if (!static_cast<bool>(unwrapped_result)) {
                *out_result = nullptr;
            } else {
                *out_result = new ifcopenshell_instance_t{unwrapped_result};
            }
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_instance_id_list_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_int32_list_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = make_int32_list_list(ifcparse::bindings::as_instance_id_list_list(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_instance_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = new ifcopenshell_parse_instance_list_t{ifcparse::bindings::as_instance_list(self_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_int32(ifcopenshell_parse_attribute_value_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = static_cast<int32_t>(ifcparse::bindings::as_int32(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_int32_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = make_int32_list(ifcparse::bindings::as_int32_list(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_int32_list_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_int32_list_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = make_int32_list_list(ifcparse::bindings::as_int32_list_list(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_logical(ifcopenshell_parse_attribute_value_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = static_cast<int32_t>(ifcparse::bindings::as_logical(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_string(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = make_string(ifcparse::bindings::as_string(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_as_string_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = make_string_list(ifcparse::bindings::as_string_list(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_class_name(ifcopenshell_instance_t* self, bool with_schema, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto with_schema_cpp = static_cast<bool>(with_schema);
        *out_result = make_string(ifcparse::bindings::class_name(*self_cpp, with_schema_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_create_entity_by_name(ifcopenshell_file_t* self, const char* type_name, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (type_name == nullptr) { throw std::runtime_error("Parameter \"type_name\" must not be null"); }
    std::string type_name_cpp(type_name);
        auto result_value = ifcparse::bindings::create_entity_by_name(*self_cpp, type_name_cpp);
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_create_entity_by_name_with_id(ifcopenshell_file_t* self, const char* type_name, uint32_t id, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (type_name == nullptr) { throw std::runtime_error("Parameter \"type_name\" must not be null"); }
    std::string type_name_cpp(type_name);
    auto id_cpp = static_cast<unsigned int>(id);
        auto result_value = ifcparse::bindings::create_entity_by_name_with_id(*self_cpp, type_name_cpp, id_cpp);
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_entity_names(ifcopenshell_file_t* self, ifcopenshell_uint32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_uint32_list(ifcparse::bindings::entity_names(*self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_file_pointer(ifcopenshell_file_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<size_t>(ifcparse::bindings::file_pointer(*self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_file_pointer(ifcopenshell_instance_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = static_cast<size_t>(ifcparse::bindings::file_pointer(*self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_instance_list_get(ifcopenshell_parse_instance_list_t* self, size_t index, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
        auto result_value = ifcparse::bindings::get(*self_cpp, index_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            auto unwrapped_result = *result_value;
            if (!static_cast<bool>(unwrapped_result)) {
                *out_result = nullptr;
            } else {
                *out_result = new ifcopenshell_instance_t{unwrapped_result};
            }
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_get_argument_by_name(ifcopenshell_instance_t* self, const char* name, ifcopenshell_parse_attribute_value_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        *out_result = new ifcopenshell_parse_attribute_value_t{ifcparse::bindings::get_argument_by_name(*self_cpp, name_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_get_argument_index(ifcopenshell_instance_t* self, const char* name, uint32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        *out_result = static_cast<uint32_t>(ifcparse::bindings::get_argument_index(*self_cpp, name_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_get_argument_name(ifcopenshell_instance_t* self, uint32_t index, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<unsigned int>(index);
        *out_result = make_string(ifcparse::bindings::get_argument_name(*self_cpp, index_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_get_argument_type(ifcopenshell_instance_t* self, uint32_t index, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<unsigned int>(index);
        *out_result = make_static_string(ifcparse::bindings::get_argument_type(*self_cpp, index_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_get_attribute_category(ifcopenshell_instance_t* self, const char* name, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        *out_result = static_cast<int32_t>(ifcparse::bindings::get_attribute_category(*self_cpp, name_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_get_attribute_names(ifcopenshell_instance_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = make_string_list(ifcparse::bindings::get_attribute_names(*self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_get_attribute_value(ifcopenshell_instance_t* self, size_t index, ifcopenshell_parse_attribute_value_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
        *out_result = new ifcopenshell_parse_attribute_value_t{ifcparse::bindings::get_attribute_value(*self_cpp, index_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_get_inverse(ifcopenshell_file_t* self, ifcopenshell_instance_t* instance, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (instance == nullptr) { throw std::runtime_error("Handle parameter \"instance\" must not be null"); }
    auto instance_cpp = &instance->value;
        *out_result = new ifcopenshell_parse_instance_list_t{ifcparse::bindings::get_inverse(self_cpp, instance_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_get_inverse(ifcopenshell_instance_t* self, const char* name, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        *out_result = new ifcopenshell_parse_instance_list_t{ifcparse::bindings::get_inverse(*self_cpp, name_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_get_inverse_attribute_by_name(ifcopenshell_instance_t* self, const char* name, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        *out_result = new ifcopenshell_parse_instance_list_t{ifcparse::bindings::get_inverse_attribute_by_name(*self_cpp, name_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_get_inverse_attribute_names(ifcopenshell_instance_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = make_string_list(ifcparse::bindings::get_inverse_attribute_names(*self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_get_inverse_indices(ifcopenshell_file_t* self, ifcopenshell_instance_t* instance, ifcopenshell_int32_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (instance == nullptr) { throw std::runtime_error("Handle parameter \"instance\" must not be null"); }
    const auto& instance_cpp = instance->value;
        *out_result = make_int32_list(ifcparse::bindings::get_inverse_indices(*self_cpp, instance_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_get_total_inverses(ifcopenshell_file_t* self, ifcopenshell_instance_t* instance, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (instance == nullptr) { throw std::runtime_error("Handle parameter \"instance\" must not be null"); }
    const auto& instance_cpp = instance->value;
        *out_result = static_cast<int32_t>(ifcparse::bindings::get_total_inverses(*self_cpp, instance_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_get_unit(ifcopenshell_file_t* self, const char* unit_type, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (unit_type == nullptr) { throw std::runtime_error("Parameter \"unit_type\" must not be null"); }
    std::string unit_type_cpp(unit_type);
        *out_result = static_cast<double>(ifcparse::bindings::get_unit(*self_cpp, unit_type_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_good(ifcopenshell_file_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(ifcparse::bindings::good(*self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_header(ifcopenshell_file_t* self, ifcopenshell_header_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcparse::bindings::header(self_cpp);
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_header_t{result_value, false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_header_file_description(ifcopenshell_file_t* self, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcparse::bindings::header_file_description(self_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            auto unwrapped_result = *result_value;
            if (!static_cast<bool>(unwrapped_result)) {
                *out_result = nullptr;
            } else {
                *out_result = new ifcopenshell_instance_t{unwrapped_result};
            }
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_header_file_name(ifcopenshell_file_t* self, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcparse::bindings::header_file_name(self_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            auto unwrapped_result = *result_value;
            if (!static_cast<bool>(unwrapped_result)) {
                *out_result = nullptr;
            } else {
                *out_result = new ifcopenshell_instance_t{unwrapped_result};
            }
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_header_file_schema(ifcopenshell_file_t* self, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcparse::bindings::header_file_schema(self_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            auto unwrapped_result = *result_value;
            if (!static_cast<bool>(unwrapped_result)) {
                *out_result = nullptr;
            } else {
                *out_result = new ifcopenshell_instance_t{unwrapped_result};
            }
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_streamer_inverses(ifcopenshell_instance_streamer_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(ifcparse::bindings::inverses(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_is_a(ifcopenshell_instance_t* self, const char* declaration_name, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (declaration_name == nullptr) { throw std::runtime_error("Parameter \"declaration_name\" must not be null"); }
    std::string declaration_name_cpp(declaration_name);
        *out_result = ifcparse::bindings::is_a(*self_cpp, declaration_name_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_is_null(ifcopenshell_parse_attribute_value_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = ifcparse::bindings::is_null(self_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_key_value_store_iter(ifcopenshell_file_t* self, const char* prefix, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (prefix == nullptr) { throw std::runtime_error("Parameter \"prefix\" must not be null"); }
    std::string prefix_cpp(prefix);
        *out_result = make_string_list(ifcparse::bindings::key_value_store_iter(*self_cpp, prefix_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_key_value_store_query(ifcopenshell_file_t* self, const char* key, ifcopenshell_uint8_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (key == nullptr) { throw std::runtime_error("Parameter \"key\" must not be null"); }
    std::string key_cpp(key);
        *out_result = make_uint8_list(ifcparse::bindings::key_value_store_query(*self_cpp, key_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parameter_type_kind(ifcopenshell_parameter_type_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_static_string(ifcparse::bindings::kind(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_simple_type_kind(ifcopenshell_simple_type_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_static_string(ifcparse::bindings::kind(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_aggregation_type_kind(ifcopenshell_aggregation_type_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_static_string(ifcparse::bindings::kind(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_streamer_read_instance_json(ifcopenshell_instance_streamer_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(ifcparse::bindings::read_instance_json(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_streamer_references(ifcopenshell_instance_streamer_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(ifcparse::bindings::references(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_schema_name(ifcopenshell_file_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(ifcparse::bindings::schema_name(*self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_select_type_select_list_names(ifcopenshell_select_type_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string_list(ifcparse::bindings::select_list_names(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_as_aggregate_of_aggregate_of_entity_instance(ifcopenshell_instance_t* self, size_t index, const ifcopenshell_int32_list_list_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    auto value_cpp = to_cpp_int32_list_list(value);
        ifcparse::bindings::set_argument_as_aggregate_of_aggregate_of_entity_instance(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_bool(ifcopenshell_instance_t* self, size_t index, bool value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    auto value_cpp = static_cast<bool>(value);
        ifcparse::bindings::set_argument_bool(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_double(ifcopenshell_instance_t* self, size_t index, double value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    auto value_cpp = static_cast<double>(value);
        ifcparse::bindings::set_argument_double(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_double_list(ifcopenshell_instance_t* self, size_t index, const ifcopenshell_double_list_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    auto value_cpp = to_cpp_double_list(value);
        ifcparse::bindings::set_argument_double_list(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_double_list_list(ifcopenshell_instance_t* self, size_t index, const ifcopenshell_double_list_list_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    auto value_cpp = to_cpp_double_list_list(value);
        ifcparse::bindings::set_argument_double_list_list(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_enumeration(ifcopenshell_instance_t* self, size_t index, ifcopenshell_enumeration_t* enumeration, size_t enumeration_index) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    if (enumeration == nullptr || enumeration->ptr == nullptr) { throw std::runtime_error("Handle parameter \"enumeration\" is invalid"); }
    auto enumeration_cpp = enumeration->ptr;
    auto enumeration_index_cpp = static_cast<size_t>(enumeration_index);
        ifcparse::bindings::set_argument_enumeration(*self_cpp, index_cpp, enumeration_cpp, enumeration_index_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_enumeration_by_name(ifcopenshell_instance_t* self, size_t index, const char* value, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    std::string value_cpp(value);
        *out_result = ifcparse::bindings::set_argument_enumeration_by_name(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_instance(ifcopenshell_instance_t* self, size_t index, ifcopenshell_instance_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    if (value == nullptr) { throw std::runtime_error("Handle parameter \"value\" must not be null"); }
    auto value_cpp = &value->value;
        ifcparse::bindings::set_argument_instance(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_instance_list(ifcopenshell_instance_t* self, size_t index, ifcopenshell_parse_instance_list_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    if (value == nullptr) { throw std::runtime_error("Handle parameter \"value\" must not be null"); }
    auto value_cpp = &value->value;
        ifcparse::bindings::set_argument_instance_list(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_int32(ifcopenshell_instance_t* self, size_t index, int32_t value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    auto value_cpp = static_cast<int>(value);
        ifcparse::bindings::set_argument_int32(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_int32_list(ifcopenshell_instance_t* self, size_t index, const ifcopenshell_int32_list_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    auto value_cpp = to_cpp_int32_list(value);
        ifcparse::bindings::set_argument_int32_list(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_int32_list_list(ifcopenshell_instance_t* self, size_t index, const ifcopenshell_int32_list_list_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    auto value_cpp = to_cpp_int32_list_list(value);
        ifcparse::bindings::set_argument_int32_list_list(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_logical(ifcopenshell_instance_t* self, size_t index, int32_t value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    auto value_cpp = static_cast<int>(value);
        ifcparse::bindings::set_argument_logical(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_string(ifcopenshell_instance_t* self, size_t index, const char* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    std::string value_cpp(value);
        ifcparse::bindings::set_argument_string(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_argument_string_list(ifcopenshell_instance_t* self, size_t index, const ifcopenshell_string_list_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
    if (value == nullptr) { throw std::runtime_error("Parameter \"value\" must not be null"); }
    auto value_cpp = to_cpp_string_list(value);
        ifcparse::bindings::set_argument_string_list(*self_cpp, index_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_set_attribute_value(ifcopenshell_instance_t* self, const char* name, ifcopenshell_parse_attribute_value_t* value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
    if (value == nullptr) { throw std::runtime_error("Handle parameter \"value\" must not be null"); }
    auto value_cpp = value->value;
        ifcparse::bindings::set_attribute_value(*self_cpp, name_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_size(ifcopenshell_parse_attribute_value_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = static_cast<size_t>(ifcparse::bindings::size(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_instance_list_size(ifcopenshell_parse_instance_list_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
        *out_result = static_cast<size_t>(ifcparse::bindings::size(*self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_streamer_status(ifcopenshell_instance_streamer_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(ifcparse::bindings::status(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_storage_mode(ifcopenshell_file_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(ifcparse::bindings::storage_mode(*self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_to_string(ifcopenshell_file_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(ifcparse::bindings::to_string(*self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_to_string(ifcopenshell_instance_t* self, bool valid_spf, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto valid_spf_cpp = static_cast<bool>(valid_spf);
        *out_result = make_string(ifcparse::bindings::to_string(*self_cpp, valid_spf_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_parse_attribute_value_type(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto& self_cpp = self->value;
        *out_result = make_static_string(ifcparse::bindings::type(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_aggregation_type_type_of_aggregation(ifcopenshell_aggregation_type_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(ifcparse::bindings::type_of_aggregation(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_inverse_attribute_type_of_aggregation(ifcopenshell_inverse_attribute_t* self, int32_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<int32_t>(ifcparse::bindings::type_of_aggregation(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_aggregation_type_type_of_aggregation_string(ifcopenshell_aggregation_type_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_static_string(ifcparse::bindings::type_of_aggregation_string(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_inverse_attribute_type_of_aggregation_string(ifcopenshell_inverse_attribute_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_static_string(ifcparse::bindings::type_of_aggregation_string(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_types(ifcopenshell_file_t* self, ifcopenshell_string_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string_list(ifcparse::bindings::types(*self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_unset_argument(ifcopenshell_instance_t* self, size_t index) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    auto index_cpp = static_cast<size_t>(index);
        ifcparse::bindings::unset_argument(*self_cpp, index_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_instance_unset_attribute_value(ifcopenshell_instance_t* self, const char* name) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    if (!static_cast<bool>(self->value)) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = &self->value;
    if (name == nullptr) { throw std::runtime_error("Parameter \"name\" must not be null"); }
    std::string name_cpp(name);
        ifcparse::bindings::unset_attribute_value(*self_cpp, name_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_file_write(ifcopenshell_file_t* self, const char* path) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (path == nullptr) { throw std::runtime_error("Parameter \"path\" must not be null"); }
    std::string path_cpp(path);
        ifcparse::bindings::write(*self_cpp, path_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_header_write(ifcopenshell_header_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(ifcparse::bindings::write(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_opaque_number_add(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t* other, ifcopenshell_geom_opaque_number_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (other == nullptr || other->ptr == nullptr) { throw std::runtime_error("Handle parameter \"other\" is invalid"); }
    auto other_cpp = other->ptr;
        auto result_value = ifcgeom::bindings::add(self_cpp, other_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_opaque_number_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_add(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t* arg_0, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (arg_0 == nullptr || arg_0->ptr == nullptr) { throw std::runtime_error("Handle parameter \"arg_0\" is invalid"); }
    auto arg_0_cpp = arg_0->ptr;
        auto result_value = ifcgeom::bindings::add(self_cpp, arg_0_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_area(ifcopenshell_geom_conversion_result_shape_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<double>(ifcgeom::bindings::area(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_representation_as_compound(ifcopenshell_geom_brep_representation_t* self, bool force_meters, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto force_meters_cpp = static_cast<bool>(force_meters);
        auto result_value = ifcgeom::bindings::as_compound(self_cpp, force_meters_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_svgfill_polygon_boundary_point(ifcopenshell_geom_svgfill_polygon_t* self, size_t index, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto index_cpp = static_cast<size_t>(index);
        *out_result = make_double_list(ifcgeom::bindings::boundary_point(self_cpp, index_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_svgfill_polygon_boundary_size(ifcopenshell_geom_svgfill_polygon_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<size_t>(ifcgeom::bindings::boundary_size(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_box(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcgeom::bindings::box(self_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_element_calc_surface_area(ifcopenshell_geom_brep_element_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<double>(ifcgeom::bindings::calc_surface_area(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_brep_element_calc_volume(ifcopenshell_geom_brep_element_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<double>(ifcgeom::bindings::calc_volume(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_opaque_number_clone(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcgeom::bindings::clone(self_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_opaque_number_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_colors_buffer(ifcopenshell_geom_triangulation_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(ifcgeom::bindings::colors_buffer(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_colors_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<size_t>(ifcgeom::bindings::colors_buffer_size(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_concat(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t* arg_0, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (arg_0 == nullptr || arg_0->ptr == nullptr) { throw std::runtime_error("Handle parameter \"arg_0\" is invalid"); }
    auto arg_0_cpp = arg_0->ptr;
        auto result_value = ifcgeom::bindings::concat(self_cpp, arg_0_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_control_point_at(ifcopenshell_geom_taxonomy_bspline_surface_t* self, size_t row, size_t col, ifcopenshell_geom_taxonomy_point3_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
    auto row_cpp = static_cast<size_t>(row);
    auto col_cpp = static_cast<size_t>(col);
        *out_result = new ifcopenshell_geom_taxonomy_point3_t{ifcgeom::bindings::control_point_at(self_cpp, row_cpp, col_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_control_point_col_count_at(ifcopenshell_geom_taxonomy_bspline_surface_t* self, size_t row, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
    auto row_cpp = static_cast<size_t>(row);
        *out_result = static_cast<size_t>(ifcgeom::bindings::control_point_col_count_at(self_cpp, row_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_control_point_row_count(ifcopenshell_geom_taxonomy_bspline_surface_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<size_t>(ifcgeom::bindings::control_point_row_count(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_convex_tag(ifcopenshell_geom_conversion_result_shape_t* self, bool value) {
    try {
        ifcopenshell_clear_error();
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto value_cpp = static_cast<bool>(value);
        ifcgeom::bindings::convex_tag(self_cpp, value_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_opaque_number_divide(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t* other, ifcopenshell_geom_opaque_number_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (other == nullptr || other->ptr == nullptr) { throw std::runtime_error("Handle parameter \"other\" is invalid"); }
    auto other_cpp = other->ptr;
        auto result_value = ifcgeom::bindings::divide(self_cpp, other_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_opaque_number_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_edges(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_geom_conversion_result_shape_list(ifcgeom::bindings::edges(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_edges_buffer(ifcopenshell_geom_triangulation_t* self, const int32_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = (ifcgeom::bindings::edges_buffer(self_cpp)).data();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_edges_item_ids_buffer(ifcopenshell_geom_triangulation_t* self, const int32_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = (ifcgeom::bindings::edges_item_ids_buffer(self_cpp)).data();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_opaque_number_equals(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t* other, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (other == nullptr || other->ptr == nullptr) { throw std::runtime_error("Handle parameter \"other\" is invalid"); }
    auto other_cpp = other->ptr;
        *out_result = ifcgeom::bindings::equals(self_cpp, other_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_function_item_evaluator_evaluate_at(ifcopenshell_geom_function_item_evaluator_t* self, double u, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto u_cpp = static_cast<double>(u);
        *out_result = make_double_list(ifcgeom::bindings::evaluate_at(self_cpp, u_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_faces_buffer(ifcopenshell_geom_triangulation_t* self, const int32_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = (ifcgeom::bindings::faces_buffer(self_cpp)).data();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_facets(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_geom_conversion_result_shape_list(ifcgeom::bindings::facets(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_get_as_brep_element(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_brep_element_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcgeom::bindings::get_as_brep_element(self_cpp);
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_brep_element_t{result_value, false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_get_as_serialized_element(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_serialized_element_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcgeom::bindings::get_as_serialized_element(self_cpp);
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_serialized_element_t{result_value, false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_get_as_triangulation_element(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_triangulation_element_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcgeom::bindings::get_as_triangulation_element(self_cpp);
        if (result_value == nullptr) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_triangulation_element_t{result_value, false};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_halfspaces(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcgeom::bindings::halfspaces(self_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_has_weights(ifcopenshell_geom_taxonomy_bspline_surface_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = ifcgeom::bindings::has_weights(self_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_svgfill_polygon_inner_boundary_count(ifcopenshell_geom_svgfill_polygon_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<size_t>(ifcgeom::bindings::inner_boundary_count(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_svgfill_polygon_inner_boundary_point(ifcopenshell_geom_svgfill_polygon_t* self, size_t boundary_index, size_t point_index, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto boundary_index_cpp = static_cast<size_t>(boundary_index);
    auto point_index_cpp = static_cast<size_t>(point_index);
        *out_result = make_double_list(ifcgeom::bindings::inner_boundary_point(self_cpp, boundary_index_cpp, point_index_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_svgfill_polygon_inner_boundary_size(ifcopenshell_geom_svgfill_polygon_t* self, size_t boundary_index, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto boundary_index_cpp = static_cast<size_t>(boundary_index);
        *out_result = static_cast<size_t>(ifcgeom::bindings::inner_boundary_size(self_cpp, boundary_index_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_ray_intersection_instance(ifcopenshell_geom_tree_ray_intersection_t* self, ifcopenshell_instance_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcgeom::bindings::instance(self_cpp);
        if (!static_cast<bool>(result_value)) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_instance_t{std::move(result_value)};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_style_instance_id(ifcopenshell_geom_taxonomy_style_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<size_t>(ifcgeom::bindings::instance_id(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_intersect(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t* arg_0, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (arg_0 == nullptr || arg_0->ptr == nullptr) { throw std::runtime_error("Handle parameter \"arg_0\" is invalid"); }
    auto arg_0_cpp = arg_0->ptr;
        auto result_value = ifcgeom::bindings::intersect(self_cpp, arg_0_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_item_ids_buffer(ifcopenshell_geom_triangulation_t* self, const int32_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = (ifcgeom::bindings::item_ids_buffer(self_cpp)).data();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_length(ifcopenshell_geom_conversion_result_shape_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<double>(ifcgeom::bindings::length(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_opaque_number_less_than(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t* other, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (other == nullptr || other->ptr == nullptr) { throw std::runtime_error("Handle parameter \"other\" is invalid"); }
    auto other_cpp = other->ptr;
        *out_result = ifcgeom::bindings::less_than(self_cpp, other_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_material_ids_buffer(ifcopenshell_geom_triangulation_t* self, const int32_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = (ifcgeom::bindings::material_ids_buffer(self_cpp)).data();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_moved(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_taxonomy_matrix4_t* arg_0, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (arg_0 == nullptr || arg_0->ptr == nullptr) { throw std::runtime_error("Handle parameter \"arg_0\" is invalid"); }
    auto arg_0_cpp = arg_0->ptr;
        auto result_value = ifcgeom::bindings::moved(self_cpp, arg_0_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_opaque_number_multiply(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t* other, ifcopenshell_geom_opaque_number_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (other == nullptr || other->ptr == nullptr) { throw std::runtime_error("Handle parameter \"other\" is invalid"); }
    auto other_cpp = other->ptr;
        auto result_value = ifcgeom::bindings::multiply(self_cpp, other_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_opaque_number_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_opaque_number_negate(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcgeom::bindings::negate(self_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_opaque_number_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_iterator_next(ifcopenshell_geom_iterator_t* self, bool* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = ifcgeom::bindings::next(self_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_normals_buffer(ifcopenshell_geom_triangulation_t* self, const double** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = (ifcgeom::bindings::normals_buffer(self_cpp)).data();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_svgfill_polygon_point_inside(ifcopenshell_geom_svgfill_polygon_t* self, ifcopenshell_double_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_double_list(ifcgeom::bindings::point_inside(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_select_box_bounds(ifcopenshell_geom_tree_t* self, double xmin, double ymin, double zmin, double xmax, double ymax, double zmax, bool completely_within, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto xmin_cpp = static_cast<double>(xmin);
    auto ymin_cpp = static_cast<double>(ymin);
    auto zmin_cpp = static_cast<double>(zmin);
    auto xmax_cpp = static_cast<double>(xmax);
    auto ymax_cpp = static_cast<double>(ymax);
    auto zmax_cpp = static_cast<double>(zmax);
    auto completely_within_cpp = static_cast<bool>(completely_within);
        *out_result = new ifcopenshell_parse_instance_list_t{ifcgeom::bindings::select_box_bounds(self_cpp, xmin_cpp, ymin_cpp, zmin_cpp, xmax_cpp, ymax_cpp, zmax_cpp, completely_within_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_select_box_element(ifcopenshell_geom_tree_t* self, ifcopenshell_instance_t* instance, bool completely_within, double extend, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (instance == nullptr) { throw std::runtime_error("Handle parameter \"instance\" must not be null"); }
    auto instance_cpp = &instance->value;
    auto completely_within_cpp = static_cast<bool>(completely_within);
    auto extend_cpp = static_cast<double>(extend);
        *out_result = new ifcopenshell_parse_instance_list_t{ifcgeom::bindings::select_box_element(self_cpp, instance_cpp, completely_within_cpp, extend_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_select_box_point(ifcopenshell_geom_tree_t* self, double x, double y, double z, double extend, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto x_cpp = static_cast<double>(x);
    auto y_cpp = static_cast<double>(y);
    auto z_cpp = static_cast<double>(z);
    auto extend_cpp = static_cast<double>(extend);
        *out_result = new ifcopenshell_parse_instance_list_t{ifcgeom::bindings::select_box_point(self_cpp, x_cpp, y_cpp, z_cpp, extend_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_select_brep_element(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_brep_element_t* element, bool completely_within, double extend, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (element == nullptr || element->ptr == nullptr) { throw std::runtime_error("Handle parameter \"element\" is invalid"); }
    auto element_cpp = element->ptr;
    auto completely_within_cpp = static_cast<bool>(completely_within);
    auto extend_cpp = static_cast<double>(extend);
        *out_result = new ifcopenshell_parse_instance_list_t{ifcgeom::bindings::select_brep_element(self_cpp, element_cpp, completely_within_cpp, extend_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_select_element(ifcopenshell_geom_tree_t* self, ifcopenshell_instance_t* instance, bool completely_within, double extend, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (instance == nullptr) { throw std::runtime_error("Handle parameter \"instance\" must not be null"); }
    auto instance_cpp = &instance->value;
    auto completely_within_cpp = static_cast<bool>(completely_within);
    auto extend_cpp = static_cast<double>(extend);
        *out_result = new ifcopenshell_parse_instance_list_t{ifcgeom::bindings::select_element(self_cpp, instance_cpp, completely_within_cpp, extend_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_select_point(ifcopenshell_geom_tree_t* self, double x, double y, double z, double extend, ifcopenshell_parse_instance_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto x_cpp = static_cast<double>(x);
    auto y_cpp = static_cast<double>(y);
    auto z_cpp = static_cast<double>(z);
    auto extend_cpp = static_cast<double>(extend);
        *out_result = new ifcopenshell_parse_instance_list_t{ifcgeom::bindings::select_point(self_cpp, x_cpp, y_cpp, z_cpp, extend_cpp)};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_tree_select_ray(ifcopenshell_geom_tree_t* self, double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, double length, ifcopenshell_geom_tree_ray_intersection_list_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    auto origin_x_cpp = static_cast<double>(origin_x);
    auto origin_y_cpp = static_cast<double>(origin_y);
    auto origin_z_cpp = static_cast<double>(origin_z);
    auto dir_x_cpp = static_cast<double>(dir_x);
    auto dir_y_cpp = static_cast<double>(dir_y);
    auto dir_z_cpp = static_cast<double>(dir_z);
    auto length_cpp = static_cast<double>(length);
        *out_result = new ifcopenshell_geom_tree_ray_intersection_list_t{new std::vector<IfcGeom::ray_intersection_result>(ifcgeom::bindings::select_ray(self_cpp, origin_x_cpp, origin_y_cpp, origin_z_cpp, dir_x_cpp, dir_y_cpp, dir_z_cpp, length_cpp)), true};
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_serialize(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(ifcgeom::bindings::serialize(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_serialize_obj(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_string_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_string(ifcgeom::bindings::serialize_obj(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_solid(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcgeom::bindings::solid(self_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_solid_mt(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcgeom::bindings::solid_mt(self_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_opaque_number_subtract(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t* other, ifcopenshell_geom_opaque_number_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (other == nullptr || other->ptr == nullptr) { throw std::runtime_error("Handle parameter \"other\" is invalid"); }
    auto other_cpp = other->ptr;
        auto result_value = ifcgeom::bindings::subtract(self_cpp, other_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_opaque_number_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_subtract(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t* arg_0, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
    if (arg_0 == nullptr || arg_0->ptr == nullptr) { throw std::runtime_error("Handle parameter \"arg_0\" is invalid"); }
    auto arg_0_cpp = arg_0->ptr;
        auto result_value = ifcgeom::bindings::subtract(self_cpp, arg_0_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_element_transformation_buffer(ifcopenshell_geom_element_t* self, const double** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = ifcgeom::bindings::transformation_buffer(self_cpp);
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_element_transformation_buffer_size(ifcopenshell_geom_element_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<size_t>(ifcgeom::bindings::transformation_buffer_size(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_uvs_buffer(ifcopenshell_geom_triangulation_t* self, const double** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = (ifcgeom::bindings::uvs_buffer(self_cpp)).data();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_vertices(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_list_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = make_geom_conversion_result_shape_list(ifcgeom::bindings::vertices(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_triangulation_verts_buffer(ifcopenshell_geom_triangulation_t* self, const double** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = (ifcgeom::bindings::verts_buffer(self_cpp)).data();
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_volume(ifcopenshell_geom_conversion_result_shape_t* self, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        *out_result = static_cast<double>(ifcgeom::bindings::volume(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_weight_at(ifcopenshell_geom_taxonomy_bspline_surface_t* self, size_t row, size_t col, double* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
    auto row_cpp = static_cast<size_t>(row);
    auto col_cpp = static_cast<size_t>(col);
        *out_result = static_cast<double>(ifcgeom::bindings::weight_at(self_cpp, row_cpp, col_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_weight_col_count_at(ifcopenshell_geom_taxonomy_bspline_surface_t* self, size_t row, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
    auto row_cpp = static_cast<size_t>(row);
        *out_result = static_cast<size_t>(ifcgeom::bindings::weight_col_count_at(self_cpp, row_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_taxonomy_bspline_surface_weight_row_count(ifcopenshell_geom_taxonomy_bspline_surface_t* self, size_t* out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr.get();
        *out_result = static_cast<size_t>(ifcgeom::bindings::weight_row_count(self_cpp));
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}

bool ifcopenshell_geom_conversion_result_shape_wrap_in_compound(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t** out_result) {
    try {
        ifcopenshell_clear_error();
    if (out_result == nullptr) { throw std::runtime_error("out_result must not be null"); }
    if (self == nullptr || self->ptr == nullptr) { throw std::runtime_error("Receiver handle is invalid"); }
    auto* self_cpp = self->ptr;
        auto result_value = ifcgeom::bindings::wrap_in_compound(self_cpp);
        if (!result_value) {
            *out_result = nullptr;
        } else {
            *out_result = new ifcopenshell_geom_conversion_result_shape_t{std::move(result_value).release(), true};
        }
        if (ifcopenshell_last_error_kind() != IFCOPENSHELL_ERROR_NONE) {
            return false;
        }
        return true;
    } catch (...) {
        ifcopenshell::capi::set_error_from_current_exception();
        return false;
    }
}
