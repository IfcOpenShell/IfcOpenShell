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

// This file was generated with the assistance of an AI coding tool.

// Prototype for issue #134 / #1409: maps IfcVertexPoint as a top-level
// representation item, not just as an IfcEdge's EdgeStart/-End (IfcEdge.cpp).

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcVertexPoint* inst) {
	IfcSchema::IfcPoint* pnt = inst->VertexGeometry();
	if (!pnt->declaration().is(IfcSchema::IfcCartesianPoint::Class())) {
		logger_.Message(Logger::LOG_ERROR, "GEO", 257, "Only IfcCartesianPoints are supported for VertexGeometry", inst);
		return nullptr;
	}
	return map(pnt);
}
