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

#include <cstddef>
#include <type_traits>

namespace {

template <typename Schema, typename = void>
struct is_ifc4_or_higher : std::false_type {};

template <typename Schema>
struct is_ifc4_or_higher<Schema, std::void_t<typename Schema::IfcMaterialDefinition>> : std::true_type {};

std::string schema_name(const express::Base& instance) {
    return instance.declaration().schema()->name();
}

[[noreturn]] void unsupported_schema(const std::string& name) {
    throw ifcopenshell::exception("No helper implementation was built for schema " + name);
}

// getattr(element, name) for a string- or enum-valued attribute. std::nullopt
// when the attribute is not part of this entity's type (Python's absent
// getattr) or when it is IFC null. Reads by name, so it works uniformly across
// the various IfcElement / IfcType* subtypes that carry PredefinedType et al.
std::optional<std::string> get_string_attribute(const express::Base& element,
                                                const std::string& name) {
    const ifcopenshell::entity* declaration = element.declaration().as_entity();
    if (declaration == nullptr) {
        return std::nullopt;
    }
    const std::ptrdiff_t index = declaration->attribute_index(name);
    if (index < 0) {
        return std::nullopt;
    }
    const attribute_value value = element.get_attribute_value(static_cast<std::size_t>(index));
    if (value.isNull()) {
        return std::nullopt;
    }
    switch (value.type()) {
    case ifcopenshell::Argument_ENUMERATION: {
        const enumeration_reference enumeration = value;
        return enumeration.value() ? std::string(enumeration.value()) : std::string();
    }
    case ifcopenshell::Argument_STRING:
        return static_cast<std::string>(value);
    default:
        return std::nullopt;
    }
}

// ifcopenshell.util.element.get_type: the construction type of an occurrence
// (get_type(type_element) == type_element).
template <typename Schema>
express::Base get_type_s(const express::Base& element) {
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
std::optional<std::string> get_predefined_type_s(const express::Base& element) {
    // Prefer the associated type element's predefined type.
    if (const express::Base type = get_type_s<Schema>(element)) {
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

} // namespace

std::optional<std::string> get_predefined_type(const express::Base& element) {
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
