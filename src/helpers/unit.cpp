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
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#include "unit.h"
#include "unit_convert.h"

#include "../ifcparse/exception.h"
#include "../ifcparse/file.h"
#include "../ifcparse/instance_data.h"
#include "schema_dispatch.i"

#include <algorithm>
#include <cctype>

namespace {

[[noreturn]] void unsupported_schema(const std::string& name) {
    throw ifcopenshell::exception("No helper implementation was built for schema " + name);
}

std::optional<double> numeric_value(const express::base& value) {
    if (!value) {
        return std::nullopt;
    }
    const auto inner = value.get_attribute_value(0);
    if (inner.isNull()) {
        return std::nullopt;
    }
    if (inner.type() == ifcopenshell::Argument_DOUBLE) {
        return static_cast<double>(inner);
    }
    if (inner.type() == ifcopenshell::Argument_INT) {
        return static_cast<double>(static_cast<int>(inner));
    }
    return std::nullopt;
}

template <typename Schema>
std::optional<double> si_scale_from_named_unit_s(express::base unit) {
    double scale = 1.0;
    while (auto conversion = unit.template as<typename Schema::IfcConversionBasedUnit>()) {
        if (const auto it = SI_CONVERSIONS.find(to_lower(conversion.Name()));
            it != SI_CONVERSIONS.end()) {
            return scale * it->second;
        }
        const auto factor = conversion.ConversionFactor();
        const auto value = numeric_value(factor.ValueComponent().concrete());
        if (!value) {
            return std::nullopt;
        }
        scale *= *value;
        const auto component = factor.UnitComponent();
        if (!component) {
            return std::nullopt;
        }
        unit = component.concrete();
    }

    if (auto si = unit.template as<typename Schema::IfcSIUnit>()) {
        std::string prefix;
        if (const auto value = si.Prefix()) {
            prefix = Schema::IfcSIPrefix::ToString(*value);
        }
        const std::string name = Schema::IfcSIUnitName::ToString(si.Name());
        double multiplier = get_prefix_multiplier(prefix);
        if (name.find("SQUARE") != std::string::npos) {
            multiplier *= get_prefix_multiplier(prefix);
        } else if (name.find("CUBIC") != std::string::npos) {
            multiplier *= get_prefix_multiplier(prefix) * get_prefix_multiplier(prefix);
        }
        return scale * multiplier;
    }
    if (unit.template as<typename Schema::IfcContextDependentUnit>()) {
        return std::nullopt;
    }
    return scale;
}

template <typename Schema>
std::optional<express::base> get_unit_assignment_s(ifcopenshell::file* ifc_file) {
    const auto projects = ifc_file->template instances_by_type<typename Schema::IfcProject>();
    if (projects.empty()) {
        return std::nullopt;
    }
    const auto assignment = projects.front().UnitsInContext();
    if (!assignment) {
        return std::nullopt;
    }
    return assignment;
}

template <typename Schema>
std::optional<express::base> get_project_unit_s(ifcopenshell::file* ifc_file,
                                                const std::string& unit_type) {
    const auto assignment = get_unit_assignment_s<Schema>(ifc_file);
    if (!assignment) {
        return std::nullopt;
    }
    const auto typed_assignment = assignment->template as<typename Schema::IfcUnitAssignment>();
    for (const auto& selected_unit : typed_assignment.Units()) {
        const auto unit = selected_unit.concrete();
        if (auto named = unit.template as<typename Schema::IfcNamedUnit>()) {
            if (unit_type == Schema::IfcUnitEnum::ToString(named.UnitType())) {
                return unit;
            }
        } else if (auto derived = unit.template as<typename Schema::IfcDerivedUnit>()) {
            if (unit_type == Schema::IfcDerivedUnitEnum::ToString(derived.UnitType())) {
                return unit;
            }
        }
    }
    return std::nullopt;
}

template <typename Schema>
double calculate_unit_scale_s(ifcopenshell::file* ifc_file, const std::string& unit_type) {
    const auto unit = get_project_unit_s<Schema>(ifc_file, unit_type);
    if (!unit) {
        return 1.0;
    }
    return si_scale_from_named_unit_s<Schema>(*unit).value_or(1.0);
}

template <typename Schema>
void unit_name_s(const express::base& unit, std::string& prefix, std::string& name) {
    prefix.clear();
    name.clear();
    if (auto si = unit.template as<typename Schema::IfcSIUnit>()) {
        if (const auto value = si.Prefix()) {
            prefix = Schema::IfcSIPrefix::ToString(*value);
        }
        name = Schema::IfcSIUnitName::ToString(si.Name());
    } else if (auto conversion = unit.template as<typename Schema::IfcConversionBasedUnit>()) {
        name = conversion.Name();
    } else if (auto contextual = unit.template as<typename Schema::IfcContextDependentUnit>()) {
        name = contextual.Name();
    }
}

template <typename Schema>
double convert_unit_s(double value, const express::base& from_unit, const express::base& to_unit) {
    std::string from_prefix;
    std::string from_name;
    std::string to_prefix;
    std::string to_name;
    unit_name_s<Schema>(from_unit, from_prefix, from_name);
    unit_name_s<Schema>(to_unit, to_prefix, to_name);
    return convert(value, from_prefix, from_name, to_prefix, to_name);
}

} // namespace

std::optional<double> si_scale_from_named_unit(express::base unit) {
    if (!unit) {
        return std::nullopt;
    }
    const auto name = unit.declaration().schema()->name();
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier)                       \
        return si_scale_from_named_unit_s<Schema>(unit);
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

std::optional<express::base> get_unit_assignment(ifcopenshell::file* ifc_file) {
    const auto name = ifc_file->schema()->name();
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier)                       \
        return get_unit_assignment_s<Schema>(ifc_file);
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

std::optional<express::base> get_project_unit(ifcopenshell::file* ifc_file,
                                              const std::string& unit_type) {
    const auto name = ifc_file->schema()->name();
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier)                       \
        return get_project_unit_s<Schema>(ifc_file, unit_type);
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

double calculate_unit_scale(ifcopenshell::file* ifc_file,
                            const std::string& unit_type) {
    const auto name = ifc_file->schema()->name();
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier)                       \
        return calculate_unit_scale_s<Schema>(ifc_file, unit_type);
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}


double convert_unit(double value, express::base from_unit, express::base to_unit) {
    if (!from_unit || !to_unit) {
        return value;
    }
    const auto name = from_unit.declaration().schema()->name();
    if (name != to_unit.declaration().schema()->name()) {
        throw ifcopenshell::exception("Cannot convert units from different IFC schemas");
    }
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier)                       \
        return convert_unit_s<Schema>(value, from_unit, to_unit);
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}
