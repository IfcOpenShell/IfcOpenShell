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
#include "unit_convert.h"

#include <optional>
#include <string>
#include <unordered_map>

namespace ifcopenshell {
class file;
}

// Returns the SI scale for an IfcNamedUnit such that
//   value_in_unit * scale == value_in_si_base
// Walks IfcConversionBasedUnit chains down to IfcSIUnit.  Returns nullopt
// when the chain bottoms out in IfcContextDependentUnit (cannot convert).
std::optional<double> si_scale_from_named_unit(express::base named_unit);

// IfcProject.UnitsInContext (the IfcUnitAssignment).  Returns nullopt if
// the file has no project or no assignment.
std::optional<express::base> get_unit_assignment(ifcopenshell::file* ifc_file);

// First unit in the project's IfcUnitAssignment matching `unit_type`
// (e.g. "LENGTHUNIT").  Returns nullopt if not found.
std::optional<express::base> get_project_unit(ifcopenshell::file* ifc_file,
                                              const std::string& unit_type);

// Project unit -> SI base scale (e.g. project in mm => 0.001).  Defaults
// to 1.0 when no project unit of the requested type is set.
double calculate_unit_scale(ifcopenshell::file* ifc_file,
                            const std::string& unit_type = "LENGTHUNIT");

// Convert between two IfcNamedUnit entities.  Pulls Name and Prefix off each
// and delegates to convert().  IfcConversionBasedUnit names that don't appear
// in SI_CONVERSIONS return the value unchanged.
double convert_unit(double value, express::base from_unit, express::base to_unit);

#endif // UNIT_H
