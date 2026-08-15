# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations


def _render_cpp_support_runtime() -> str:
    """Render C++ runtime helpers emitted before generated call bodies.

    This intentionally remains an f-string even though it has no substitutions:
    the generated C++ contains many literal braces, and keeping the original
    f-string escaping avoids hand-unescaping JSON/C++ brace literals.
    """
    return f"""// Error reporting state. Defined in the named ifcopenshell::capi namespace so
// that external translation units can participate via the internal header.
namespace ifcopenshell {{
namespace capi {{
thread_local std::string g_last_error;
thread_local int g_last_error_kind = IFCOPENSHELL_ERROR_NONE;
thread_local int g_last_error_code = IFCOPENSHELL_ERROR_CODE_NONE;

void set_last_error(const std::string& message) {{
    g_last_error_kind = IFCOPENSHELL_ERROR_RUNTIME;
    g_last_error_code = IFCOPENSHELL_ERROR_CODE_UNSPECIFIED;
    g_last_error = message;
}}

void set_last_error(int kind, const std::string& message) {{
    g_last_error_kind = kind;
    g_last_error_code = kind == IFCOPENSHELL_ERROR_NONE
        ? IFCOPENSHELL_ERROR_CODE_NONE
        : IFCOPENSHELL_ERROR_CODE_UNSPECIFIED;
    g_last_error = message;
}}

void set_last_error(int kind, int code, const std::string& message) {{
    g_last_error_kind = kind;
    g_last_error_code = code;
    g_last_error = message;
}}

int last_error_kind() {{
    return g_last_error_kind;
}}

void set_error_from_current_exception() {{
    if (last_error_kind() != IFCOPENSHELL_ERROR_NONE) {{
        return;
    }}
    try {{
        throw;
    }} catch (const std::invalid_argument& error) {{
        set_last_error(IFCOPENSHELL_ERROR_VALUE, IFCOPENSHELL_ERROR_CODE_INVALID_ARGUMENT, error.what());
    }} catch (const std::domain_error& error) {{
        set_last_error(IFCOPENSHELL_ERROR_VALUE, IFCOPENSHELL_ERROR_CODE_DOMAIN_ERROR, error.what());
    }} catch (const std::bad_cast& error) {{
        set_last_error(IFCOPENSHELL_ERROR_TYPE, IFCOPENSHELL_ERROR_CODE_UNSPECIFIED, error.what());
    }} catch (const std::bad_typeid& error) {{
        set_last_error(IFCOPENSHELL_ERROR_TYPE, IFCOPENSHELL_ERROR_CODE_UNSPECIFIED, error.what());
    }} catch (const std::exception& error) {{
        set_last_error(IFCOPENSHELL_ERROR_RUNTIME, IFCOPENSHELL_ERROR_CODE_UNSPECIFIED, error.what());
    }} catch (...) {{
        set_last_error(IFCOPENSHELL_ERROR_RUNTIME, IFCOPENSHELL_ERROR_CODE_UNSPECIFIED, "Unknown C++ exception");
    }}
}}
}} // namespace capi
}} // namespace ifcopenshell

namespace {{
using ifcopenshell::capi::g_last_error;
using ifcopenshell::capi::set_last_error;

struct capi_buffer_owner {{
    virtual ~capi_buffer_owner() = default;
}};

template <typename T>
struct capi_value_owner final : capi_buffer_owner {{
    explicit capi_value_owner(T value) : value(std::move(value)) {{}}
    T value;
}};

template <typename T>
struct capi_array_owner final : capi_buffer_owner {{
    explicit capi_array_owner(size_t size)
        : values(size == 0 ? nullptr : std::make_unique<T[]>(size)) {{}}
    std::unique_ptr<T[]> values;
}};

template <size_t N, typename Sequence>
auto to_fixed_array(Sequence&& values) {{
    if (values.size() != N) {{
        throw std::invalid_argument("Fixed-size sequence has invalid cardinality");
    }}
    using item_type = std::decay_t<decltype(values[0])>;
    std::array<item_type, N> result{{}};
    std::move(values.begin(), values.end(), result.begin());
    return result;
}}

template <typename Sequence, typename Transform>
auto transform_sequence(Sequence&& values, Transform transform) {{
    using item_type = decltype(transform(std::move(values[0])));
    std::vector<item_type> result;
    result.reserve(values.size());
    for (auto& value : values) {{
        result.push_back(transform(std::move(value)));
    }}
    return result;
}}

template <size_t N, typename Sequence, typename Transform>
auto transform_fixed_sequence(Sequence&& values, Transform transform) {{
    if (values.size() != N) {{
        throw std::invalid_argument("Fixed-size sequence has invalid cardinality");
    }}
    using item_type = decltype(transform(std::move(values[0])));
    std::array<item_type, N> result{{}};
    for (size_t index = 0; index < N; ++index) {{
        result[index] = transform(std::move(values[index]));
    }}
    return result;
}}

bool feature_use_attribute_value_derived = false;
std::stringstream ifcopenshell_log_stream;
bool g_log_stream_initialized = false;

void ensure_log_stream_initialized() {{
    if (!g_log_stream_initialized) {{
        logger::set_output(nullptr, &ifcopenshell_log_stream);
        g_log_stream_initialized = true;
    }}
}}

ifcopenshell::argument_type helper_fn_attribute_type(const express::Base* inst, unsigned index) {{
    const ifcopenshell::parameter_type* parameter_type = nullptr;
    if (inst->declaration().as_entity()) {{
        parameter_type = inst->declaration().as_entity()->attribute_by_index(index)->type_of_attribute();
        if (inst->declaration().as_entity()->derived()[index]) {{
            return ifcopenshell::Argument_DERIVED;
        }}
    }} else if (inst->declaration().as_type_declaration() && index == 0) {{
        parameter_type = inst->declaration().as_type_declaration()->declared_type();
    }} else if (inst->declaration().as_enumeration_type() && index == 0) {{
        return ifcopenshell::Argument_STRING;
    }}

    if (parameter_type == nullptr) {{
        return ifcopenshell::Argument_UNKNOWN;
    }}
    return ifcopenshell::from_parameter_type(parameter_type);
}}

void validate_list_items(const char* name, const void* items, size_t size) {{
    if (size > 0 && items == nullptr) {{
        throw std::runtime_error(std::string("Parameter '") + name + "' has a null items pointer");
    }}
}}

template <typename T>
struct capi_is_std_vector : std::false_type {{}};

template <typename T, typename Alloc>
struct capi_is_std_vector<std::vector<T, Alloc>> : std::true_type {{}};

template <typename T>
inline constexpr bool capi_is_std_vector_v = capi_is_std_vector<T>::value;

std::string json_escape_string(const std::string& value) {{
    std::ostringstream out;
    for (unsigned char ch : value) {{
        switch (ch) {{
        case '\\\\': out << "\\\\\\\\"; break;
        case '"': out << "\\\\\\""; break;
        case '\\b': out << "\\\\b"; break;
        case '\\f': out << "\\\\f"; break;
        case '\\n': out << "\\\\n"; break;
        case '\\r': out << "\\\\r"; break;
        case '\\t': out << "\\\\t"; break;
        default:
            if (ch < 0x20) {{
                out << "\\\\u"
                    << "00"
                    << "0123456789abcdef"[ch >> 4]
                    << "0123456789abcdef"[ch & 0x0f];
            }} else {{
                out << static_cast<char>(ch);
            }}
        }}
    }}
    return out.str();
}}

std::string json_quote(const std::string& value) {{
    return std::string(1, '"') + json_escape_string(value) + '"';
}}

std::string instance_to_info_json_string(const express::Base& instance, bool include_identifier);

template <typename T>
std::string value_to_json_string(const T& value, bool include_identifier);

template <typename T>
std::string vector_to_json_string(const std::vector<T>& values, bool include_identifier) {{
    std::ostringstream out;
    out << "[";
    for (size_t i = 0; i < values.size(); ++i) {{
        if (i != 0) {{
            out << ",";
        }}
        out << value_to_json_string(values[i], include_identifier);
    }}
    out << "]";
    return out.str();
}}

std::string reference_or_simple_type_to_json_string(const ifcopenshell::reference_or_simple_type& value, bool include_identifier) {{
    if (auto* instance = std::get_if<express::Base>(&value)) {{
        return *instance ? instance_to_info_json_string(*instance, include_identifier) : "null";
    }}
    auto reference = std::get<ifcopenshell::instance_reference>(value);
    return std::string(R"({{"ref":)") + std::to_string(reference.v) + "}}";
}}

template <typename T>
std::string value_to_json_string(const T& value, bool include_identifier) {{
    if constexpr (capi_is_std_vector_v<T>) {{
        return vector_to_json_string(value, include_identifier);
    }} else if constexpr (std::is_same_v<T, std::string>) {{
        return json_quote(value);
    }} else if constexpr (std::is_same_v<T, const char*>) {{
        return value ? json_quote(value) : "null";
    }} else if constexpr (std::is_same_v<T, bool>) {{
        return value ? "true" : "false";
    }} else if constexpr (std::is_integral_v<T> || std::is_floating_point_v<T>) {{
        std::ostringstream out;
        out << value;
        return out.str();
    }} else if constexpr (std::is_same_v<T, enumeration_reference>) {{
        return json_quote(std::string(value.value()));
    }} else if constexpr (std::is_same_v<T, ifcopenshell::reference_or_simple_type>) {{
        return reference_or_simple_type_to_json_string(value, include_identifier);
    }} else if constexpr (std::is_same_v<T, express::Base>) {{
        return value ? instance_to_info_json_string(value, include_identifier) : "null";
    }} else if constexpr (
        std::is_same_v<T, empty_aggregate_t> ||
        std::is_same_v<T, empty_aggregate_of_aggregate_t> ||
        std::is_same_v<T, blank> ||
        std::is_same_v<T, derived>) {{
        return "null";
    }} else {{
        return json_quote("<unsupported>");
    }}
}}

std::string attribute_value_to_json_string(const attribute_value& value, bool include_identifier) {{
    return value.apply_visitor([include_identifier](const auto& inner) -> std::string {{
        return value_to_json_string(inner, include_identifier);
    }});
}}

std::string instance_to_info_json_string(const express::Base& instance, bool include_identifier) {{
    if (!instance) {{
        return "null";
    }}
    std::ostringstream out;
    out << "{{";
    bool first = true;
    auto emit_field = [&](const std::string& key, const std::string& json_value) {{
        if (!first) {{
            out << ",";
        }}
        first = false;
        out << json_quote(key) << ":" << json_value;
    }};

    if (instance.declaration().as_entity()) {{
        const auto attributes = instance.declaration().as_entity()->all_attributes();
        for (size_t i = 0; i < attributes.size(); ++i) {{
            emit_field(attributes[i]->name(), attribute_value_to_json_string(instance.get_attribute_value(i), include_identifier));
        }}
        if (include_identifier) {{
            emit_field("id", std::to_string(instance.id()));
        }}
    }} else {{
        emit_field("wrappedValue", attribute_value_to_json_string(instance.get_attribute_value(0), include_identifier));
    }}

    emit_field("type", json_quote(instance.declaration().name()));
    out << "}}";
    return out.str();
}}

std::string unresolved_reference_variant_to_json_string(
    const std::variant<
        ifcopenshell::reference_or_simple_type,
        std::vector<ifcopenshell::reference_or_simple_type>,
        std::vector<std::vector<ifcopenshell::reference_or_simple_type>>>& value,
    bool include_identifier) {{
    return std::visit(
        [include_identifier](const auto& inner) -> std::string {{
            return value_to_json_string(inner, include_identifier);
        }},
        value);
}}

std::string unresolved_references_to_json_string(
    const ifcopenshell::unresolved_references& references,
    const ifcopenshell::declaration* declaration) {{
    std::ostringstream out;
    out << "[";
    bool first = true;
    for (const auto& entry : references) {{
        if (!first) {{
            out << ",";
        }}
        first = false;
        const auto& mutable_value = entry.first;
        out << "{{"
            << R"("entity_name":)" << mutable_value.name_
            << R"(,"attribute_index":)" << static_cast<int>(mutable_value.index_);
        if (declaration && declaration->as_entity() && mutable_value.index_ < declaration->as_entity()->attribute_count()) {{
            out << R"(,"attribute_name":)" << json_quote(declaration->as_entity()->attribute_by_index(mutable_value.index_)->name());
        }}
        out << R"(,"value":)" << unresolved_reference_variant_to_json_string(entry.second, true) << "}}";
    }}
    out << "]";
    return out.str();
}}

std::string inverses_to_json_string(const ifcopenshell::impl::in_memory_file_storage::entities_by_ref_t& inverses) {{
    std::ostringstream out;
    out << "[";
    bool first = true;
    for (const auto& entry : inverses) {{
        for (const auto& inverse : entry.second) {{
            if (!first) {{
                out << ",";
            }}
            first = false;
            out << "{{"
                << R"("instance_id":)" << entry.first
                << R"(,"instance_type":)" << std::get<0>(inverse.first)
                << R"(,"attribute_index":)" << std::get<1>(inverse.first)
                << R"(,"referencing_ids":)" << vector_to_json_string(inverse.second, true)
                << "}}";
        }}
    }}
    out << "]";
    return out.str();
}}

std::string instance_stream_read_instance_json(ifcopenshell::instance_streamer<>* streamer, bool type_as_declaration_instance) {{
    if (!(*streamer)) {{
        return "null";
    }}
    auto inst = streamer->read_instance();
    if (!inst) {{
        return "null";
    }}

    std::ostringstream out;
    out << "{{";
    bool first = true;
    auto emit_field = [&](const std::string& key, const std::string& json_value) {{
        if (!first) {{
            out << ",";
        }}
        first = false;
        out << json_quote(key) << ":" << json_value;
    }};

    emit_field("id", std::to_string(std::get<0>(*inst)));
    if (type_as_declaration_instance) {{
        emit_field("type", json_quote(std::get<1>(*inst)->name()));
    }} else {{
        emit_field("type", json_quote(std::get<1>(*inst)->name()));
    }}

    const auto* declaration = std::get<1>(*inst);
    const auto& data = std::get<2>(*inst);
    if (declaration->as_entity()) {{
        for (size_t i = 0; i < declaration->as_entity()->attribute_count(); ++i) {{
            emit_field(
                declaration->as_entity()->attribute_by_index(i)->name(),
                attribute_value_to_json_string(data->get_attribute_value(i), true));
        }}
    }}

    for (const auto& reference : streamer->references()) {{
        std::string key = std::to_string(reference.first.index_);
        if (declaration->as_entity() && reference.first.index_ < declaration->as_entity()->attribute_count()) {{
            key = declaration->as_entity()->attribute_by_index(reference.first.index_)->name();
        }}
        emit_field(key, unresolved_reference_variant_to_json_string(reference.second, true));
    }}

    streamer->references().clear();
    streamer->inverses().clear();
    out << "}}";
    return out.str();
}}

ifcopenshell_string_t make_string(std::string value) {{
    auto owner = std::make_unique<capi_value_owner<std::string>>(std::move(value));
    auto& stored = owner->value;
    return ifcopenshell_string_t{{stored.data(), stored.size(), false, owner.release()}};
}}

ifcopenshell_string_t make_static_string(const char* value) {{
    if (value == nullptr) {{
        return ifcopenshell_string_t{{nullptr, 0, false, nullptr}};
    }}
    return ifcopenshell_string_t{{const_cast<char*>(value), std::strlen(value), false, nullptr}};
}}

template <typename T>
void set_instance_argument(express::Base* instance, size_t index, const T& value) {{
    instance->set_attribute_value(index, value);
}}

void set_instance_argument(express::Base* instance, size_t index, express::Base* value) {{
    if (value == nullptr) {{
        instance->unset_attribute_value(index);
    }} else {{
        instance->set_attribute_value(index, *value);
    }}
}}

void set_instance_argument(express::Base* instance, size_t index, std::vector<express::Base>* value) {{
    if (value == nullptr) {{
        instance->unset_attribute_value(index);
    }} else {{
        instance->set_attribute_value(index, *value);
    }}
}}

void unset_instance_argument(express::Base* instance, size_t index) {{
    instance->unset_attribute_value(index);
}}

void set_instance_attribute_from_attribute_value(express::Base* instance, size_t index, const attribute_value& value) {{
    value.apply_visitor([&](const auto& inner) -> void {{
        using T = std::decay_t<decltype(inner)>;
        if constexpr (std::is_same_v<T, derived>) {{
            throw std::runtime_error("Cannot assign a derived attribute sentinel.");
        }} else if constexpr (std::is_same_v<T, empty_aggregate_t> ||
                              std::is_same_v<T, empty_aggregate_of_aggregate_t>) {{
            // Empty-aggregate sentinels arise when reading absent aggregate
            // values; assigning them is equivalent to unsetting the attribute.
            unset_instance_argument(instance, index);
        }} else {{
            set_instance_argument(instance, index, inner);
        }}
    }});
}}
}} // namespace

namespace ifcopenshell {{
namespace capi {{

void set_feature(const std::string& name, bool value) {{
    if (name == "use_attribute_value_derived") {{
        feature_use_attribute_value_derived = value;
        return;
    }}
    throw std::runtime_error("Invalid feature specification");
}}

bool get_feature(const std::string& name) {{
    if (name == "use_attribute_value_derived") {{
        return feature_use_attribute_value_derived;
    }}
    throw std::runtime_error("Invalid feature specification");
}}

std::string get_log() {{
    ensure_log_stream_initialized();
    std::string log = ifcopenshell_log_stream.str();
    ifcopenshell_log_stream.str("");
    ifcopenshell_log_stream.clear();
    return log;
}}

void turn_on_detailed_logging() {{
    logger::set_output(&std::cout, &std::cout);
    logger::verbosity(logger::LOG_DEBUG);
}}

void turn_off_detailed_logging() {{
    ensure_log_stream_initialized();
    logger::set_output(nullptr, &ifcopenshell_log_stream);
    logger::verbosity(logger::LOG_WARNING);
}}

void set_log_format_json() {{
    ensure_log_stream_initialized();
    ifcopenshell_log_stream.str("");
    ifcopenshell_log_stream.clear();
    logger::output_format(logger::FMT_JSON);
}}

void set_log_format_text() {{
    ensure_log_stream_initialized();
    ifcopenshell_log_stream.str("");
    ifcopenshell_log_stream.clear();
    logger::output_format(logger::FMT_PLAIN);
}}

std::string get_info_cpp(const express::Base& instance, bool include_identifier) {{
    return instance_to_info_json_string(instance, include_identifier);
}}

std::string streamer_references(ifcopenshell::instance_streamer<>* streamer) {{
    return unresolved_references_to_json_string(streamer->references(), nullptr);
}}

std::string streamer_inverses(ifcopenshell::instance_streamer<>* streamer) {{
    return inverses_to_json_string(streamer->inverses());
}}

std::string streamer_read_instance_json(ifcopenshell::instance_streamer<>* streamer, bool type_as_declaration_instance) {{
    return instance_stream_read_instance_json(streamer, type_as_declaration_instance);
}}

void unset_instance_argument_value(express::Base& instance, size_t index) {{
    instance.set_attribute_value(index, blank{{}});
}}

void unset_instance_argument(express::Base& instance, size_t index) {{
    instance.set_attribute_value(index, blank{{}});
}}

ifcopenshell::argument_type instance_attribute_type(const express::Base& instance, unsigned index) {{
    return ::helper_fn_attribute_type(&instance, index);
}}

void set_instance_attribute_from_attribute_value(express::Base& instance, size_t index, const attribute_value& value) {{
    ::set_instance_attribute_from_attribute_value(&instance, index, value);
}}

void set_instance_argument_bool(express::Base& instance, size_t index, bool value) {{
    set_instance_argument(&instance, index, value);
}}

void set_instance_argument_int32(express::Base& instance, size_t index, int value) {{
    set_instance_argument(&instance, index, value);
}}

void set_instance_argument_double(express::Base& instance, size_t index, double value) {{
    set_instance_argument(&instance, index, value);
}}

void set_instance_argument_string(express::Base& instance, size_t index, const std::string& value) {{
    set_instance_argument(&instance, index, value);
}}

void set_instance_argument_instance(express::Base& instance, size_t index, express::Base* value) {{
    set_instance_argument(&instance, index, value);
}}

void set_instance_argument_instance_list(express::Base& instance, size_t index, std::vector<express::Base>* value) {{
    set_instance_argument(&instance, index, value);
}}

void set_instance_argument_int32_list(express::Base& instance, size_t index, const std::vector<int>& value) {{
    set_instance_argument(&instance, index, value);
}}

void set_instance_argument_double_list(express::Base& instance, size_t index, const std::vector<double>& value) {{
    set_instance_argument(&instance, index, value);
}}

void set_instance_argument_string_list(express::Base& instance, size_t index, const std::vector<std::string>& value) {{
    set_instance_argument(&instance, index, value);
}}

void set_instance_argument_int32_list_list(express::Base& instance, size_t index, const std::vector<std::vector<int>>& value) {{
    set_instance_argument(&instance, index, value);
}}

void set_instance_argument_double_list_list(express::Base& instance, size_t index, const std::vector<std::vector<double>>& value) {{
    set_instance_argument(&instance, index, value);
}}

void set_instance_argument_logical(express::Base& instance, size_t index, int value) {{
    ifcopenshell::argument_type arg_type = helper_fn_attribute_type(&instance, static_cast<unsigned>(index));
    if (arg_type != ifcopenshell::Argument_LOGICAL) {{
        throw ifcopenshell::exception("Attribute not set");
    }}
    boost::logic::tribool logical_value;
    if (value == 0) {{
        logical_value = false;
    }} else if (value == 1) {{
        logical_value = true;
    }} else if (value == -1) {{
        logical_value = boost::logic::indeterminate;
    }} else {{
        throw ifcopenshell::exception("Logical value must be -1, 0, or 1");
    }}
    set_instance_argument(&instance, index, logical_value);
}}

void set_instance_argument_aggregate_of_aggregate_of_entity_instance(
    express::Base& instance,
    size_t index,
    const std::vector<std::vector<int>>& value
) {{
    ifcopenshell::argument_type arg_type = helper_fn_attribute_type(&instance, static_cast<unsigned>(index));
    if (arg_type != ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {{
        throw ifcopenshell::exception("Attribute not set");
    }}
    if (instance.file() == nullptr) {{
        throw ifcopenshell::exception("Instance is not attached to a file.");
    }}
    std::vector<std::vector<express::Base>> aggregate;
    for (const auto& group : value) {{
        std::vector<express::Base> instances;
        instances.reserve(group.size());
        for (int identifier : group) {{
            auto resolved = instance.file()->instance_by_id(identifier);
            if (!resolved) {{
                throw ifcopenshell::exception("Unable to resolve instance id " + std::to_string(identifier));
            }}
            instances.push_back(resolved);
        }}
        aggregate.push_back(std::move(instances));
    }}
    set_instance_argument(&instance, index, aggregate);
}}

void set_instance_argument_enumeration(
    express::Base& instance,
    size_t index,
    const ifcopenshell::enumeration_type* enumeration,
    size_t enumeration_index
) {{
    set_instance_argument(&instance, index, enumeration_reference(enumeration, enumeration_index));
}}

bool set_instance_argument_enumeration_by_name(express::Base& instance, size_t index, const std::string& value) {{
    auto* entity_decl = instance.declaration().as_entity();
    if (entity_decl == nullptr) {{
        return false;
    }}
    const auto attrs = entity_decl->all_attributes();
    if (index >= attrs.size()) {{
        return false;
    }}
    const ifcopenshell::parameter_type* parameter_type = attrs[index]->type_of_attribute();
    const ifcopenshell::enumeration_type* enumeration = nullptr;
    while (parameter_type != nullptr) {{
        auto* named = parameter_type->as_named_type();
        if (named == nullptr) {{
            break;
        }}
        auto* declaration = named->declared_type();
        if ((enumeration = declaration->as_enumeration_type()) != nullptr) {{
            break;
        }}
        auto* type_declaration = declaration->as_type_declaration();
        if (type_declaration == nullptr) {{
            break;
        }}
        parameter_type = type_declaration->declared_type();
    }}
    if (enumeration == nullptr) {{
        return false;
    }}
    const auto& items = enumeration->enumeration_items();
    auto it = std::find(items.begin(), items.end(), value);
    if (it == items.end()) {{
        throw ifcopenshell::exception("'" + value + "' is not a valid value for enumeration " + enumeration->name());
    }}
    set_instance_argument(&instance, index, enumeration_reference(enumeration, static_cast<size_t>(std::distance(items.begin(), it))));
    return true;
}}

}} // namespace capi
}} // namespace ifcopenshell"""
