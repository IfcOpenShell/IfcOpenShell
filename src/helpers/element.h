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

#ifndef ELEMENT_H
#define ELEMENT_H

#include "../ifcparse/express.h"

#include <optional>
#include <string>
#include <utility>
#include <vector>

// Mirrors ifcopenshell.util.element.get_predefined_type. Returns the element's
// PredefinedType, falling back to the user-defined ObjectType / ElementType /
// ProcessType when it is USERDEFINED or unset, and preferring the predefined
// type of the associated type element (via IsTypedBy / IsDefinedBy) first.
// std::nullopt when there is no such attribute (e.g. the element is not an
// IfcObject, or a geometry-only proxy with no live IFC data).
std::optional<std::string> get_predefined_type(const express::base& element);

// Mirrors ifcopenshell.util.element.get_type: the construction type element of
// an occurrence (via IsTypedBy on IFC4+, IsDefinedBy on IFC2X3). A type element
// returns itself. Empty express::base when the element is untyped.
express::base get_type(const express::base& element);

// Mirrors ifcopenshell.util.element.get_container (indirect, no ifc_class
// filter): the spatial element that contains this element — the directly
// containing spatial structure, or, for an aggregated part, the container of its
// aggregate parent. Empty when uncontained. (The nest / filled-void /
// voided-element branches of the Python original are not ported.)
express::base get_container(const express::base& element);

// Safely read a string- or enum-valued attribute by name (Python's getattr).
// std::nullopt when the attribute is absent for this entity's type or IFC null.
std::optional<std::string> get_string_attribute(const express::base& element,
                                                const std::string& name);

// The spatial-structure elements aggregated directly under `element` (its
// IsDecomposedBy → RelatedObjects, filtered to spatial elements). Used to walk
// the IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey → IfcSpace tree.
std::vector<express::base> get_spatial_children(const express::base& element);

// The element's direct EXPRESS attributes that have a primitive scalar value
// (string / enum / integer / real / boolean / logical), as (name, formatted
// value) pairs in declaration order. Attributes that are entity references,
// aggregates / lists, or unset (IFC null) are omitted — so the caller gets a
// flat, display-ready view with no nested objects.
std::vector<std::pair<std::string, std::string>> get_scalar_attributes(const express::base& element);

#endif // ELEMENT_H
