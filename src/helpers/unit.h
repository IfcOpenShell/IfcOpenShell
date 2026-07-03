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

// Port of selected helpers from
// src/ifcopenshell-python/ifcopenshell/util/unit.py.

#ifndef UNIT_H
#define UNIT_H

#include "../ifcparse/express.h"

#include <optional>
#include <string>
#include <unordered_map>

namespace ifcopenshell {
class file;
}

// SI prefix multipliers, e.g. "MILLI" -> 1e-3.  Empty key not present;
// callers should pass an empty prefix string for "no prefix".
extern const std::unordered_map<std::string, double> SI_PREFIXES;

// SI prefix display symbols, e.g. "MILLI" -> "m".
extern const std::unordered_map<std::string, std::string> SI_PREFIX_SYMBOLS;

// Conversion-based unit name (lowercase, IFC convention) -> SI base scale.
// e.g. "foot" -> 0.3048, "square foot" -> 0.09290304.
extern const std::unordered_map<std::string, double> SI_CONVERSIONS;

// Conversion-based unit name -> IFC unit type, e.g. "foot" -> "LENGTHUNIT".
extern const std::unordered_map<std::string, std::string> IMPERIAL_TYPES;

// Display symbol per unit name.  Covers IfcSIUnit names ("METRE" -> "m") and
// IfcConversionBasedUnit names ("foot" -> "ft").
extern const std::unordered_map<std::string, std::string> UNIT_SYMBOLS;

// Returns the multiplier for an SI prefix.  Empty string returns 1.0.
double get_prefix_multiplier(const std::string& prefix);

// Returns the SI scale for an IfcNamedUnit such that
//   value_in_unit * scale == value_in_si_base
// Walks IfcConversionBasedUnit chains down to IfcSIUnit.  Returns nullopt
// when the chain bottoms out in IfcContextDependentUnit (cannot convert).
std::optional<double> si_scale_from_named_unit(express::Base named_unit);

// IfcProject.UnitsInContext (the IfcUnitAssignment).  Returns nullopt if
// the file has no project or no assignment.
std::optional<express::Base> get_unit_assignment(ifcopenshell::file* ifc_file);

// First unit in the project's IfcUnitAssignment matching `unit_type`
// (e.g. "LENGTHUNIT").  Returns nullopt if not found.
std::optional<express::Base> get_project_unit(ifcopenshell::file* ifc_file,
                                              const std::string& unit_type);

// Project unit -> SI base scale (e.g. project in mm => 0.001).  Defaults
// to 1.0 when no project unit of the requested type is set.
double calculate_unit_scale(ifcopenshell::file* ifc_file,
                            const std::string& unit_type = "LENGTHUNIT");

// Convert between two units identified by name + optional SI prefix.
// SQUARE_/CUBIC_ prefixed SI names get the prefix multiplier squared/cubed
// (matches python ifcopenshell.util.unit.convert).
double convert(double value,
               const std::string& from_prefix,
               const std::string& from_unit,
               const std::string& to_prefix,
               const std::string& to_unit);

// Convert between two IfcNamedUnit entities.  Pulls Name and Prefix off each
// and delegates to convert().  IfcConversionBasedUnit names that don't appear
// in SI_CONVERSIONS return the value unchanged.
double convert_unit(double value, express::Base from_unit, express::Base to_unit);

#endif // UNIT_H
