/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * GNU Lesser General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the GNU Lesser General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

// This file was generated with the assistance of an AI coding tool.

#include "pset.h"

#include "../ifcparse/exception.h"
#include "../ifcparse/file.h"
#include "../ifcparse/instance_data.h"
#include "schema_dispatch.i"

#include <boost/logic/tribool.hpp>
#include <type_traits>

namespace {

template <typename T>
struct is_optional : std::false_type {};

template <typename T>
struct is_optional<std::optional<T>> : std::true_type {};

template <typename Schema, typename = void>
struct is_ifc4_or_higher : std::false_type {};

template <typename Schema>
struct is_ifc4_or_higher<Schema, std::void_t<typename Schema::IfcMaterialDefinition>> : std::true_type {};

template <typename Schema, typename = void>
struct has_predefined_property_set : std::false_type {};

template <typename Schema>
struct has_predefined_property_set<Schema, std::void_t<typename Schema::IfcPreDefinedPropertySet>> : std::true_type {};

template <typename T, typename = void>
struct has_set_point_value : std::false_type {};

template <typename T>
struct has_set_point_value<T, std::void_t<decltype(std::declval<T>().SetPointValue())>> : std::true_type {};

template <typename T, typename = void>
struct has_curve_interpolation : std::false_type {};

template <typename T>
struct has_curve_interpolation<T, std::void_t<decltype(std::declval<T>().CurveInterpolation())>> : std::true_type {};

std::string schema_name(const express::base& instance) {
    return instance.declaration().schema()->name();
}

[[noreturn]] void unsupported_schema(const std::string& name) {
    throw ifcopenshell::exception("No helper implementation was built for schema " + name);
}

property_value from_attribute(const attribute_value& value);

template <typename T>
property_list scalar_list(const std::vector<T>& values) {
    property_list result;
    result.reserve(values.size());
    for (const auto& value : values) {
        result.emplace_back(value);
    }
    return result;
}

property_value from_attribute(const attribute_value& value) {
    if (value.isNull()) {
        return {};
    }

    switch (value.type()) {
    case ifcopenshell::Argument_INT:
        return static_cast<int64_t>(value);
    case ifcopenshell::Argument_BOOL:
        return static_cast<bool>(value);
    case ifcopenshell::Argument_LOGICAL: {
        const boost::logic::tribool logical = value;
        if (boost::logic::indeterminate(logical)) {
            return "UNKNOWN";
        }
        return static_cast<bool>(logical);
    }
    case ifcopenshell::Argument_DOUBLE:
        return static_cast<double>(value);
    case ifcopenshell::Argument_STRING:
        return static_cast<std::string>(value);
    case ifcopenshell::Argument_ENUMERATION: {
        const enumeration_reference enumeration = value;
        return enumeration.value() ? enumeration.value() : "";
    }
    case ifcopenshell::Argument_BINARY: {
        const boost::dynamic_bitset<> bits = value;
        std::string result;
        boost::to_string(bits, result);
        return result;
    }
    case ifcopenshell::Argument_ENTITY_INSTANCE: {
        const express::base instance = value;
        if (instance && !instance.declaration().as_entity()) {
            return from_attribute(instance.get_attribute_value(0));
        }
        return instance;
    }
    case ifcopenshell::Argument_AGGREGATE_OF_INT:
        return scalar_list(static_cast<std::vector<int64_t>>(value));
    case ifcopenshell::Argument_AGGREGATE_OF_DOUBLE:
        return scalar_list(static_cast<std::vector<double>>(value));
    case ifcopenshell::Argument_AGGREGATE_OF_STRING:
        return scalar_list(static_cast<std::vector<std::string>>(value));
    case ifcopenshell::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
        property_list result;
        for (const auto& instance : static_cast<std::vector<express::base>>(value)) {
            if (instance && !instance.declaration().as_entity()) {
                result.push_back(from_attribute(instance.get_attribute_value(0)));
            } else {
                result.emplace_back(instance);
            }
        }
        return result;
    }
    case ifcopenshell::Argument_EMPTY_AGGREGATE:
        return property_list{};
    default:
        return {};
    }
}

template <typename Select>
property_value from_select(const Select& value) {
    if (!value) {
        return {};
    }
    return from_attribute(value.concrete().get_attribute_value(0));
}

template <typename Values>
property_value from_select_values(const Values& maybe_values) {
    if constexpr (is_optional<Values>::value) {
        if (!maybe_values || maybe_values->empty()) {
            return {};
        }
        return from_select_values(*maybe_values);
    } else {
        if (maybe_values.empty()) {
            return {};
        }
        property_list result;
        result.reserve(maybe_values.size());
        for (const auto& value : maybe_values) {
            result.push_back(from_select(value));
        }
        return result;
    }
}

property_value verbose_value(const express::base& instance,
                             property_value value,
                             const std::optional<std::string>& value_type = std::nullopt) {
    property_map result = {
        {"id", instance.id()},
        {"class", instance.declaration().name()},
        {"value", std::move(value)},
    };
    if (value_type) {
        result["value_type"] = *value_type;
    }
    return result;
}

template <typename Schema>
property_map get_properties_s(const std::vector<typename Schema::IfcProperty>& properties, bool verbose);

template <typename Schema>
property_map get_quantities_s(const std::vector<typename Schema::IfcPhysicalQuantity>& quantities, bool verbose);

template <typename Schema>
std::optional<property_value> property_value_s(const typename Schema::IfcProperty& property, bool verbose) {
    property_value result;
    std::optional<std::string> value_type;

    if (auto single = property.template as<typename Schema::IfcPropertySingleValue>()) {
        const auto nominal = single.NominalValue();
        result = from_select(nominal);
        if (nominal) {
            value_type = nominal.concrete().declaration().name();
        }
    } else if (auto enumerated = property.template as<typename Schema::IfcPropertyEnumeratedValue>()) {
        result = from_select_values(enumerated.EnumerationValues());
    } else if (auto list = property.template as<typename Schema::IfcPropertyListValue>()) {
        result = from_select_values(list.ListValues());
    } else if (auto bounded = property.template as<typename Schema::IfcPropertyBoundedValue>()) {
        property_map data = {
            {"id", bounded.id()},
            {"type", bounded.declaration().name()},
            {"UpperBoundValue", from_select(bounded.UpperBoundValue())},
            {"LowerBoundValue", from_select(bounded.LowerBoundValue())},
        };
        if constexpr (has_set_point_value<decltype(bounded)>::value) {
            data["SetPointValue"] = from_select(bounded.SetPointValue());
        }
        result = std::move(data);
    } else if (auto table = property.template as<typename Schema::IfcPropertyTableValue>()) {
        property_map data = {
            {"id", table.id()},
            {"type", table.declaration().name()},
            {"DefiningValues", from_select_values(table.DefiningValues())},
            {"DefinedValues", from_select_values(table.DefinedValues())},
        };
        if (const auto expression = table.Expression()) {
            data["Expression"] = *expression;
        }
        if (const auto defining_unit = table.DefiningUnit()) {
            data["DefiningUnit"] = defining_unit.concrete();
        }
        if (const auto defined_unit = table.DefinedUnit()) {
            data["DefinedUnit"] = defined_unit.concrete();
        }
        if constexpr (has_curve_interpolation<decltype(table)>::value) {
            if (const auto interpolation = table.CurveInterpolation()) {
                data["CurveInterpolation"] =
                    Schema::IfcCurveInterpolationEnum::ToString(*interpolation);
            }
        }
        result = std::move(data);
    } else if (auto complex = property.template as<typename Schema::IfcComplexProperty>()) {
        result = property_map{
            {"id", complex.id()},
            {"type", complex.declaration().name()},
            {"UsageName", complex.UsageName()},
            {"properties", get_properties_s<Schema>(complex.HasProperties(), verbose)},
        };
    } else {
        return std::nullopt;
    }

    if (verbose) {
        return verbose_value(property, std::move(result), value_type);
    }
    return result;
}

template <typename Schema>
std::optional<property_value> get_property_s(const std::vector<typename Schema::IfcProperty>& properties,
                                             const std::string& name,
                                             bool verbose) {
    for (const auto& property : properties) {
        if (property.Name() == name) {
            return property_value_s<Schema>(property, verbose);
        }
    }
    return std::nullopt;
}

template <typename Schema>
property_map get_properties_s(const std::vector<typename Schema::IfcProperty>& properties, bool verbose) {
    property_map result;
    for (const auto& property : properties) {
        if (auto value = property_value_s<Schema>(property, verbose)) {
            result[property.Name()] = std::move(*value);
        }
    }
    return result;
}

template <typename Schema>
std::optional<property_value> quantity_value_s(const typename Schema::IfcPhysicalQuantity& quantity,
                                               bool verbose) {
    property_value result;
    if (quantity.template as<typename Schema::IfcPhysicalSimpleQuantity>()) {
        result = from_attribute(quantity.get_attribute_value(3));
    } else if (auto complex = quantity.template as<typename Schema::IfcPhysicalComplexQuantity>()) {
        result = property_map{
            {"id", complex.id()},
            {"type", complex.declaration().name()},
            {"Discrimination", complex.Discrimination()},
            {"properties", get_quantities_s<Schema>(complex.HasQuantities(), verbose)},
        };
    } else {
        return std::nullopt;
    }
    if (verbose) {
        return verbose_value(quantity, std::move(result));
    }
    return result;
}

template <typename Schema>
std::optional<property_value> get_quantity_s(
    const std::vector<typename Schema::IfcPhysicalQuantity>& quantities,
    const std::string& name,
    bool verbose) {
    for (const auto& quantity : quantities) {
        if (quantity.Name() == name) {
            return quantity_value_s<Schema>(quantity, verbose);
        }
    }
    return std::nullopt;
}

template <typename Schema>
property_map get_quantities_s(const std::vector<typename Schema::IfcPhysicalQuantity>& quantities, bool verbose) {
    property_map result;
    for (const auto& quantity : quantities) {
        if (auto value = quantity_value_s<Schema>(quantity, verbose)) {
            result[quantity.Name()] = std::move(*value);
        }
    }
    return result;
}

template <typename Schema>
std::optional<property_value> predefined_properties_s(
    const typename Schema::IfcPreDefinedPropertySet& definition,
    const std::optional<std::string>& property_name) {
    property_map result;
    const auto* declaration = definition.declaration().as_entity();
    for (std::size_t index = 4; index < declaration->attribute_count(); ++index) {
        const auto* attribute = declaration->attribute_by_index(index);
        if (property_name && attribute->name() != *property_name) {
            continue;
        }
        const auto value = definition.get_attribute_value(index);
        if (value.isNull()) {
            continue;
        }
        if (property_name) {
            return from_attribute(value);
        }
        result[attribute->name()] = from_attribute(value);
    }
    if (property_name) {
        return std::nullopt;
    }
    result["id"] = definition.id();
    return result;
}

template <typename Schema>
std::optional<property_value> get_property_definition_s(
    const express::base& definition,
    const std::optional<std::string>& property_name,
    bool verbose) {
    if (!definition) {
        return std::nullopt;
    }
    if (auto quantity = definition.template as<typename Schema::IfcElementQuantity>()) {
        if (property_name) {
            return get_quantity_s<Schema>(quantity.Quantities(), *property_name, verbose);
        }
        auto result = get_quantities_s<Schema>(quantity.Quantities(), verbose);
        result["id"] = definition.id();
        return result;
    }
    if (auto pset = definition.template as<typename Schema::IfcPropertySet>()) {
        if (property_name) {
            return get_property_s<Schema>(pset.HasProperties(), *property_name, verbose);
        }
        auto result = get_properties_s<Schema>(pset.HasProperties(), verbose);
        result["id"] = definition.id();
        return result;
    }
    if constexpr (is_ifc4_or_higher<Schema>::value) {
        if (auto extended = definition.template as<typename Schema::IfcExtendedProperties>()) {
            if (property_name) {
                return get_property_s<Schema>(extended.Properties(), *property_name, verbose);
            }
            auto result = get_properties_s<Schema>(extended.Properties(), verbose);
            result["id"] = definition.id();
            return result;
        }
    } else {
        if (auto extended = definition.template as<typename Schema::IfcExtendedMaterialProperties>()) {
            if (property_name) {
                return get_property_s<Schema>(extended.ExtendedProperties(), *property_name, verbose);
            }
            auto result = get_properties_s<Schema>(extended.ExtendedProperties(), verbose);
            result["id"] = definition.id();
            return result;
        }
    }
    if constexpr (has_predefined_property_set<Schema>::value) {
        if (auto predefined = definition.template as<typename Schema::IfcPreDefinedPropertySet>()) {
            return predefined_properties_s<Schema>(predefined, property_name);
        }
    }
    return std::nullopt;
}

template <typename Definition>
express::base concrete_definition(const Definition& definition) {
    if constexpr (std::is_base_of_v<express::select, Definition>) {
        return definition.concrete();
    } else {
        return definition;
    }
}

template <typename Schema>
bool definition_is_pset_s(const express::base& definition) {
    if (definition.template as<typename Schema::IfcPropertySet>()) {
        return true;
    }
    if constexpr (has_predefined_property_set<Schema>::value) {
        if (definition.template as<typename Schema::IfcPreDefinedPropertySet>()) {
            return true;
        }
    }
    if constexpr (!is_ifc4_or_higher<Schema>::value) {
        if (definition.template as<typename Schema::IfcExtendedMaterialProperties>()) {
            return true;
        }
    }
    return false;
}

template <typename Schema>
std::optional<std::string> definition_name_s(const express::base& definition) {
    if (auto pset = definition.template as<typename Schema::IfcPropertySet>()) {
        return pset.Name();
    }
    if (auto quantity = definition.template as<typename Schema::IfcElementQuantity>()) {
        return quantity.Name();
    }
    if constexpr (is_ifc4_or_higher<Schema>::value) {
        if (auto extended = definition.template as<typename Schema::IfcExtendedProperties>()) {
            return extended.Name();
        }
    } else {
        if (auto extended = definition.template as<typename Schema::IfcExtendedMaterialProperties>()) {
            return extended.Name();
        }
    }
    if constexpr (has_predefined_property_set<Schema>::value) {
        if (auto predefined = definition.template as<typename Schema::IfcPreDefinedPropertySet>()) {
            return predefined.Name();
        }
    }
    return std::nullopt;
}

template <typename Schema>
void merge_definition_s(element_properties& result,
                        const express::base& definition,
                        bool psets_only,
                        bool qtos_only,
                        bool verbose) {
    const bool is_quantity = static_cast<bool>(definition.template as<typename Schema::IfcElementQuantity>());
    if (psets_only && !definition_is_pset_s<Schema>(definition)) {
        return;
    }
    if (qtos_only && !is_quantity) {
        return;
    }
    const auto name = definition_name_s<Schema>(definition);
    if (!name) {
        return;
    }
    auto values = get_property_definition_s<Schema>(definition, std::nullopt, verbose);
    if (!values) {
        return;
    }
    const auto* properties = values->template get_if<property_map>();
    if (!properties) {
        return;
    }
    auto& destination = result[*name];
    for (const auto& [property_name, value] : *properties) {
        destination.insert_or_assign(property_name, value);
    }
}

template <typename Schema>
typename Schema::IfcTypeObject get_type_s(const typename Schema::IfcObject& object) {
    if constexpr (is_ifc4_or_higher<Schema>::value) {
        const auto relationships = object.IsTypedBy();
        if (!relationships.empty()) {
            return relationships.front().RelatingType();
        }
    } else {
        for (const auto& relationship : object.IsDefinedBy()) {
            if (auto by_type = relationship.template as<typename Schema::IfcRelDefinesByType>()) {
                return by_type.RelatingType();
            }
        }
    }
    return {};
}

template <typename Schema>
element_properties get_psets_s(const express::base& element,
                               bool psets_only,
                               bool qtos_only,
                               bool should_inherit,
                               bool verbose) {
    element_properties result;

    if (auto type = element.template as<typename Schema::IfcTypeObject>()) {
        if (const auto definitions = type.HasPropertySets()) {
            for (const auto& definition : *definitions) {
                merge_definition_s<Schema>(result, definition, psets_only, qtos_only, verbose);
            }
        }
        return result;
    }

    if constexpr (is_ifc4_or_higher<Schema>::value) {
        if (auto material = element.template as<typename Schema::IfcMaterialDefinition>()) {
            if (qtos_only) {
                return result;
            }
            for (const auto& definition : material.HasProperties()) {
                merge_definition_s<Schema>(result, definition, false, false, verbose);
            }
            return result;
        }
        if (auto profile = element.template as<typename Schema::IfcProfileDef>()) {
            if (qtos_only) {
                return result;
            }
            for (const auto& definition : profile.HasProperties()) {
                merge_definition_s<Schema>(result, definition, false, false, verbose);
            }
            return result;
        }
    } else {
        if (auto material = element.template as<typename Schema::IfcMaterial>()) {
            if (qtos_only) {
                return result;
            }
            for (const auto& definition :
                 element.file()->template instances_by_type<typename Schema::IfcExtendedMaterialProperties>()) {
                if (definition.Material() == material) {
                    merge_definition_s<Schema>(result, definition, false, false, verbose);
                }
            }
            return result;
        }
        if (element.template as<typename Schema::IfcProfileDef>()) {
            return result;
        }
    }

    if (auto object = element.template as<typename Schema::IfcObject>()) {
        if (should_inherit) {
            if (const auto type = get_type_s<Schema>(object)) {
                result = get_psets_s<Schema>(type, psets_only, qtos_only, false, verbose);
            }
        }
        for (const auto& relationship : object.IsDefinedBy()) {
            if (auto by_properties = relationship.template as<typename Schema::IfcRelDefinesByProperties>()) {
                merge_definition_s<Schema>(result,
                                           concrete_definition(by_properties.RelatingPropertyDefinition()),
                                           psets_only,
                                           qtos_only,
                                           verbose);
            }
        }
    }
    return result;
}

template <typename Schema>
std::optional<property_value> get_inherited_property_s(const express::base& element,
                                                       const std::string& pset_name,
                                                       const std::string& property_name,
                                                       bool psets_only,
                                                       bool qtos_only,
                                                       bool verbose) {
    const auto object = element.template as<typename Schema::IfcObject>();
    if (!object) {
        return std::nullopt;
    }
    const auto type = get_type_s<Schema>(object);
    if (!type) {
        return std::nullopt;
    }
    const auto psets = get_psets_s<Schema>(type, psets_only, qtos_only, false, verbose);
    const auto pset = psets.find(pset_name);
    if (pset == psets.end()) {
        return std::nullopt;
    }
    const auto property = pset->second.find(property_name);
    if (property == pset->second.end()) {
        return std::nullopt;
    }
    return property->second;
}

template <typename Schema, typename Entity>
std::vector<Entity> cast_entities(const std::vector<express::base>& values) {
    std::vector<Entity> result;
    result.reserve(values.size());
    for (const auto& value : values) {
        if (auto typed = value.template as<Entity>()) {
            result.push_back(typed);
        }
    }
    return result;
}

void print_value(std::ostream& stream, const property_value& value) {
    std::visit(
        [&stream](const auto& item) {
            using T = std::decay_t<decltype(item)>;
            if constexpr (std::is_same_v<T, std::monostate>) {
                stream << "null";
            } else if constexpr (std::is_same_v<T, bool>) {
                stream << (item ? "true" : "false");
            } else if constexpr (std::is_same_v<T, express::base>) {
                if (item) {
                    item.to_string(stream);
                } else {
                    stream << "null";
                }
            } else if constexpr (std::is_same_v<T, property_list>) {
                stream << '[';
                bool first = true;
                for (const auto& child : item) {
                    if (!first) {
                        stream << ", ";
                    }
                    first = false;
                    print_value(stream, child);
                }
                stream << ']';
            } else if constexpr (std::is_same_v<T, property_map>) {
                stream << '{';
                bool first = true;
                for (const auto& [name, child] : item) {
                    if (!first) {
                        stream << ", ";
                    }
                    first = false;
                    stream << name << ": ";
                    print_value(stream, child);
                }
                stream << '}';
            } else {
                stream << item;
            }
        },
        value.value);
}

} // namespace

std::ostream& operator<<(std::ostream& stream, const property_value& value) {
    print_value(stream, value);
    return stream;
}

element_properties get_psets(const express::base& element,
                             bool psets_only,
                             bool qtos_only,
                             bool should_inherit,
                             bool verbose) {
    if (!element) {
        return {};
    }
    const auto name = schema_name(element);
#define IFCOPENSHELL_DISPATCH(Schema, Identifier)                                            \
    if (name == Identifier) {                                                                \
        return get_psets_s<Schema>(element, psets_only, qtos_only, should_inherit, verbose); \
    }
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

std::optional<property_value> get_pset(const express::base& element,
                                       const std::string& name,
                                       const std::optional<std::string>& property_name,
                                       bool psets_only,
                                       bool qtos_only,
                                       bool should_inherit,
                                       bool verbose) {
    auto psets = get_psets(element, psets_only, qtos_only, should_inherit, verbose);
    const auto set = psets.find(name);
    if (set == psets.end()) {
        return std::nullopt;
    }
    if (!property_name) {
        return set->second;
    }
    const auto property = set->second.find(*property_name);
    if (property == set->second.end()) {
        return std::nullopt;
    }
    if (property->second.is_null() && should_inherit) {
        const auto schema = schema_name(element);
#define IFCOPENSHELL_DISPATCH(Schema, Identifier)                                                                               \
    if (schema == Identifier) {                                                                                                 \
        if (auto inherited = get_inherited_property_s<Schema>(element, name, *property_name, psets_only, qtos_only, verbose)) { \
            return inherited;                                                                                                   \
        }                                                                                                                       \
    }
        IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    }
    return property->second;
}

std::optional<property_value> get_property_definition(
    const express::base& definition,
    const std::optional<std::string>& property_name,
    bool verbose) {
    if (!definition) {
        return std::nullopt;
    }
    const auto name = schema_name(definition);
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier)                       \
        return get_property_definition_s<Schema>(definition, property_name, verbose);
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

std::optional<property_value> get_quantity(const std::vector<express::base>& quantities,
                                           const std::string& name,
                                           bool verbose) {
    if (quantities.empty()) {
        return std::nullopt;
    }
    const auto schema = schema_name(quantities.front());
#define IFCOPENSHELL_DISPATCH(Schema, Identifier)                                                              \
    if (schema == Identifier) {                                                                                \
        return get_quantity_s<Schema>(cast_entities<Schema, typename Schema::IfcPhysicalQuantity>(quantities), \
                                      name,                                                                    \
                                      verbose);                                                                \
    }
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(schema);
}

property_map get_quantities(const std::vector<express::base>& quantities, bool verbose) {
    if (quantities.empty()) {
        return {};
    }
    const auto schema = schema_name(quantities.front());
#define IFCOPENSHELL_DISPATCH(Schema, Identifier)                                                                \
    if (schema == Identifier) {                                                                                  \
        return get_quantities_s<Schema>(cast_entities<Schema, typename Schema::IfcPhysicalQuantity>(quantities), \
                                        verbose);                                                                \
    }
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(schema);
}

std::optional<property_value> get_property(const std::vector<express::base>& properties,
                                           const std::string& name,
                                           bool verbose) {
    if (properties.empty()) {
        return std::nullopt;
    }
    const auto schema = schema_name(properties.front());
#define IFCOPENSHELL_DISPATCH(Schema, Identifier)                                                      \
    if (schema == Identifier) {                                                                        \
        return get_property_s<Schema>(cast_entities<Schema, typename Schema::IfcProperty>(properties), \
                                      name,                                                            \
                                      verbose);                                                        \
    }
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(schema);
}

property_map get_properties(const std::vector<express::base>& properties, bool verbose) {
    if (properties.empty()) {
        return {};
    }
    const auto schema = schema_name(properties.front());
#define IFCOPENSHELL_DISPATCH(Schema, Identifier)                                                        \
    if (schema == Identifier) {                                                                          \
        return get_properties_s<Schema>(cast_entities<Schema, typename Schema::IfcProperty>(properties), \
                                        verbose);                                                        \
    }
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(schema);
}
