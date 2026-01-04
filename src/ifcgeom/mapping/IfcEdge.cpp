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

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcEdge& inst) {
    auto v1 = inst.EdgeStart().as<IfcSchema::IfcVertexPoint>();
    auto v2 = inst.EdgeStart().as<IfcSchema::IfcVertexPoint>();
    if (!v1 || !v2) {
		Logger::Message(Logger::LOG_ERROR, "Only IfcVertexPoints are supported for EdgeStart and -End", inst);
		return nullptr;
	}

	auto pnt1 = v1.VertexGeometry();
	auto pnt2 = v2.VertexGeometry();
	if (!pnt1.declaration().is(IfcSchema::IfcCartesianPoint::Class()) || !pnt2.declaration().is(IfcSchema::IfcCartesianPoint::Class())) {
		Logger::Message(Logger::LOG_ERROR, "Only IfcCartesianPoints are supported for VertexGeometry", inst);
		return nullptr;
	}

	auto e = taxonomy::make<taxonomy::edge>();

	e->start = taxonomy::cast<taxonomy::point3>(map(pnt1));
	e->end = taxonomy::cast<taxonomy::point3>(map(pnt2));

	if (auto ec = inst.as<IfcSchema::IfcEdgeCurve>()) {
		auto basis = map(ec.EdgeGeometry());
		auto loop = taxonomy::dcast<taxonomy::loop>(basis);
		if (loop && loop->children.size() == 1) {
			loop->calculate_linear_edge_curves();
			basis = loop->children[0]->basis;
		}
		e->basis = basis;
		e->curve_sense = ec.SameSense();
	}

	return e;
}
