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

#ifndef PSET_H
#define PSET_H

#include "../ifcparse/express.h"

#include <cstdint>
#include <map>
#include <optional>
#include <ostream>
#include <string>
#include <utility>
#include <variant>
#include <vector>

struct property_value;

using property_list = std::vector<property_value>;
using property_map = std::map<std::string, property_value>;
using element_properties = std::map<std::string, property_map>;

// Recursive value used by the pset helpers. A default-constructed value is
// IFC null. Entity values are retained for compound property metadata that
// cannot be flattened to a scalar.
struct property_value {
    using storage_type = std::variant<std::monostate, bool, std::int64_t, double, std::string, express::base, property_list, property_map>;

    storage_type value;

    property_value() = default;
    property_value(bool value) : value(value) {}
    property_value(int value) : value(static_cast<std::int64_t>(value)) {}
    property_value(unsigned value) : value(static_cast<std::int64_t>(value)) {}
    property_value(std::int64_t value) : value(value) {}
    property_value(double value) : value(value) {}
    property_value(const char* value) : value(std::string(value)) {}
    property_value(std::string value) : value(std::move(value)) {}
    property_value(express::base value) : value(std::move(value)) {}
    property_value(property_list value) : value(std::move(value)) {}
    property_value(property_map value) : value(std::move(value)) {}

    bool is_null() const { return std::holds_alternative<std::monostate>(value); }

    template <typename T>
    const T* get_if() const {
        return std::get_if<T>(&value);
    }
};

std::ostream& operator<<(std::ostream& stream, const property_value& value);

// Mirrors ifcopenshell.util.element.get_pset. When property_name is unset,
// the returned value contains a property_map. A selected IFC null property is
// represented by an engaged optional containing a null property_value.
std::optional<property_value> get_pset(
    const express::base& element,
    const std::string& name,
    const std::optional<std::string>& property_name = std::nullopt,
    bool psets_only = false,
    bool qtos_only = false,
    bool should_inherit = true,
    bool verbose = false);

// Mirrors ifcopenshell.util.element.get_psets, including occurrence-over-type
// precedence and the definition instance id in each returned property map.
element_properties get_psets(const express::base& element,
                             bool psets_only = false,
                             bool qtos_only = false,
                             bool should_inherit = true,
                             bool verbose = false);

std::optional<property_value> get_property_definition(
    const express::base& definition,
    const std::optional<std::string>& property_name = std::nullopt,
    bool verbose = false);

std::optional<property_value> get_quantity(const std::vector<express::base>& quantities,
                                           const std::string& name,
                                           bool verbose = false);
property_map get_quantities(const std::vector<express::base>& quantities,
                            bool verbose = false);

std::optional<property_value> get_property(const std::vector<express::base>& properties,
                                           const std::string& name,
                                           bool verbose = false);
property_map get_properties(const std::vector<express::base>& properties,
                            bool verbose = false);

#endif // PSET_H
