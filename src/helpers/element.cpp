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

#include "element.h"

#include "../ifcparse/exception.h"
#include "../ifcparse/file.h"
#include "../ifcparse/instance_data.h"
#include "../ifcparse/schema.h"
#include "schema_dispatch.i"

#include <boost/logic/tribool.hpp>

#include <cstddef>
#include <sstream>
#include <type_traits>

namespace {

template <typename Schema, typename = void>
struct is_ifc4_or_higher : std::false_type {};

template <typename Schema>
struct is_ifc4_or_higher<Schema, std::void_t<typename Schema::IfcMaterialDefinition>> : std::true_type {};

std::string schema_name(const express::base& instance) {
    return instance.declaration().schema()->name();
}

[[noreturn]] void unsupported_schema(const std::string& name) {
    throw ifcopenshell::exception("No helper implementation was built for schema " + name);
}

// A primitive scalar attribute value formatted for display, or std::nullopt for
// IFC null and for non-primitive values (entity references, aggregates/lists,
// binary) — which the properties UI omits.
std::optional<std::string> format_scalar(const ifcopenshell::attribute_value& value) {
    if (value.isNull()) {
        return std::nullopt;
    }
    switch (value.type()) {
    case ifcopenshell::Argument_STRING:
        return static_cast<std::string>(value);
    case ifcopenshell::Argument_ENUMERATION: {
        const ifcopenshell::enumeration_reference enumeration = value;
        return enumeration.value() ? std::string(enumeration.value()) : std::string();
    }
    case ifcopenshell::Argument_INT:
        return std::to_string(static_cast<int>(value));
    case ifcopenshell::Argument_DOUBLE: {
        std::ostringstream stream;
        stream << static_cast<double>(value);
        return stream.str();
    }
    case ifcopenshell::Argument_BOOL:
        return static_cast<bool>(value) ? std::string("True") : std::string("False");
    case ifcopenshell::Argument_LOGICAL: {
        const boost::logic::tribool logical = value;
        if (boost::logic::indeterminate(logical)) {
            return std::string("UNKNOWN");
        }
        return static_cast<bool>(logical) ? std::string("True") : std::string("False");
    }
    default:
        return std::nullopt;
    }
}

// ifcopenshell.util.element.get_type: the construction type of an occurrence
// (get_type(type_element) == type_element).
template <typename Schema>
express::base get_type_s(const express::base& element) {
    if (element.template as<typename Schema::IfcTypeObject>()) {
        return element;
    }
    const auto object = element.template as<typename Schema::IfcObject>();
    if (!object) {
        return {};
    }
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
std::optional<std::string> get_predefined_type_s(const express::base& element) {
    // Prefer the associated type element's predefined type.
    if (const express::base type = get_type_s<Schema>(element)) {
        std::optional<std::string> predefined_type = get_string_attribute(type, "PredefinedType");
        if (!predefined_type || *predefined_type == "USERDEFINED") {
            // ElementType (IfcElementType) or ProcessType (IfcTypeProcess) — the
            // two are mutually exclusive by type, so whichever is present wins.
            std::optional<std::string> custom = get_string_attribute(type, "ElementType");
            if (!custom) {
                custom = get_string_attribute(type, "ProcessType");
            }
            predefined_type = custom;
        }
        if (predefined_type && !predefined_type->empty() && *predefined_type != "NOTDEFINED") {
            return predefined_type;
        }
    }

    // Fall back to the occurrence's own predefined type / user-defined ObjectType.
    std::optional<std::string> predefined_type = get_string_attribute(element, "PredefinedType");
    if (!predefined_type || *predefined_type == "USERDEFINED") {
        predefined_type = get_string_attribute(element, "ObjectType");
    }
    return predefined_type;
}

// ifcopenshell.util.element.get_aggregate: the aggregate parent, via the
// Decomposes inverse (IfcRelAggregates.RelatingObject).
template <typename Schema>
express::base get_aggregate_s(const express::base& element) {
    const auto object = element.template as<typename Schema::IfcObjectDefinition>();
    if (!object) {
        return {};
    }
    const auto decomposes = object.Decomposes();
    if (decomposes.empty()) {
        return {};
    }
    const auto relationship = decomposes.front();
    if constexpr (!is_ifc4_or_higher<Schema>::value) {
        // IFC2X3 reuses Decomposes for both aggregates and nests.
        if (!relationship.template as<typename Schema::IfcRelAggregates>()) {
            return {};
        }
    }
    return relationship.RelatingObject();
}

// The spatial-structure children aggregated under this element (IsDecomposedBy →
// RelatedObjects, filtered to spatial elements).
template <typename Schema>
std::vector<express::base> get_spatial_children_s(const express::base& element) {
    std::vector<express::base> children;
    const auto object = element.template as<typename Schema::IfcObjectDefinition>();
    if (!object) {
        return children;
    }
    for (const auto& relationship : object.IsDecomposedBy()) {
        for (const auto& related : relationship.RelatedObjects()) {
            if (related.template as<typename Schema::IfcSpatialStructureElement>()) {
                children.push_back(related);
            }
        }
    }
    return children;
}

// ifcopenshell.util.element.get_container (should_get_direct=false, no
// ifc_class): the directly containing spatial element, or the container of the
// aggregate parent for an aggregated part.
template <typename Schema>
express::base get_container_s(const express::base& element) {
    if (const auto product = element.template as<typename Schema::IfcElement>()) {
        const auto relationships = product.ContainedInStructure();
        if (!relationships.empty()) {
            return relationships.front().RelatingStructure();
        }
    }
    if (const express::base aggregate = get_aggregate_s<Schema>(element)) {
        return get_container_s<Schema>(aggregate);
    }
    return {};
}

} // namespace

std::optional<std::string> get_predefined_type(const express::base& element) {
    if (!element) {
        return std::nullopt;
    }
    const std::string name = schema_name(element);
#define IFCOPENSHELL_DISPATCH(Schema, Identifier)      \
    if (name == Identifier) {                          \
        return get_predefined_type_s<Schema>(element); \
    }
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

std::vector<std::pair<std::string, std::string>> get_scalar_attributes(const express::base& element) {
    std::vector<std::pair<std::string, std::string>> result;
    if (!element) {
        return result;
    }
    const ifcopenshell::entity* declaration = element.declaration().as_entity();
    if (declaration == nullptr) {
        return result;
    }
    // all_attributes() is supertype-first, matching get_attribute_value(index).
    const auto& attributes = declaration->all_attributes();
    for (std::size_t index = 0; index < attributes.size(); ++index) {
        if (auto value = format_scalar(element.get_attribute_value(index))) {
            result.emplace_back(attributes[index]->name(), std::move(*value));
        }
    }
    return result;
}

express::base get_type(const express::base& element) {
    if (!element) {
        return {};
    }
    const std::string name = schema_name(element);
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier) {                     \
        return get_type_s<Schema>(element);       \
    }
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

express::base get_container(const express::base& element) {
    if (!element) {
        return {};
    }
    const std::string name = schema_name(element);
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier) {                     \
        return get_container_s<Schema>(element);  \
    }
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

std::vector<express::base> get_spatial_children(const express::base& element) {
    if (!element) {
        return {};
    }
    const std::string name = schema_name(element);
#define IFCOPENSHELL_DISPATCH(Schema, Identifier)       \
    if (name == Identifier) {                           \
        return get_spatial_children_s<Schema>(element); \
    }
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

// getattr(element, name) for a string- or enum-valued attribute. Reads by name,
// so it works uniformly across the various subtypes that carry a given
// attribute (PredefinedType, Name, ...).
std::optional<std::string> get_string_attribute(const express::base& element,
                                                const std::string& name) {
    if (!element) {
        return std::nullopt;
    }
    const ifcopenshell::entity* declaration = element.declaration().as_entity();
    if (declaration == nullptr) {
        return std::nullopt;
    }
    const std::ptrdiff_t index = declaration->attribute_index(name);
    if (index < 0) {
        return std::nullopt;
    }
    const ifcopenshell::attribute_value value = element.get_attribute_value(static_cast<std::size_t>(index));
    if (value.isNull()) {
        return std::nullopt;
    }
    switch (value.type()) {
    case ifcopenshell::Argument_ENUMERATION: {
        const ifcopenshell::enumeration_reference enumeration = value;
        return enumeration.value() ? std::string(enumeration.value()) : std::string();
    }
    case ifcopenshell::Argument_STRING:
        return static_cast<std::string>(value);
    default:
        return std::nullopt;
    }
}
