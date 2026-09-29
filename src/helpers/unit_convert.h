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

// Unit conversion that needs no IFC file: the ported lookup tables from
// src/ifcopenshell-python/ifcopenshell/util/unit.py plus the two pure
// functions over them.
//
// Split out of unit.h/unit.cpp because those pull in ../ifcparse/express.h for
// the entity-walking helpers (calculate_unit_scale, si_scale_from_named_unit,
// convert_unit).  IfcViewerCore — and through it the Emscripten build — needs
// convert() to resolve a federation unit name to metres, but links neither
// IfcParse nor Qt.  Keeping one copy of the tables here rather than a second
// one in the web layer is the whole point of the split.

#ifndef UNIT_CONVERT_H
#define UNIT_CONVERT_H

#include <string>
#include <unordered_map>

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

// Lowercase an IFC unit name so it can be looked up in the tables above,
// which are keyed by the lowercase IFC convention ("foot", "square foot").
std::string to_lower(const std::string& s);

// Returns the multiplier for an SI prefix.  Empty string returns 1.0.
double get_prefix_multiplier(const std::string& prefix);

// Convert between two units identified by name + optional SI prefix.
// SQUARE_/CUBIC_ prefixed SI names get the prefix multiplier squared/cubed
// (matches python ifcopenshell.util.unit.convert).
double convert(double value,
               const std::string& from_prefix,
               const std::string& from_unit,
               const std::string& to_prefix,
               const std::string& to_unit);

#endif // UNIT_CONVERT_H
