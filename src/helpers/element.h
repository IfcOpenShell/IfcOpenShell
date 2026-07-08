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

// Mirrors ifcopenshell.util.element.get_predefined_type. Returns the element's
// PredefinedType, falling back to the user-defined ObjectType / ElementType /
// ProcessType when it is USERDEFINED or unset, and preferring the predefined
// type of the associated type element (via IsTypedBy / IsDefinedBy) first.
// std::nullopt when there is no such attribute (e.g. the element is not an
// IfcObject, or a geometry-only proxy with no live IFC data).
std::optional<std::string> get_predefined_type(const express::Base& element);

#endif // ELEMENT_H
