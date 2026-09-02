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

#include <boost/math/constants/constants.hpp>

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcRightCircularCylinder* inst) {
	const double r = inst->Radius() * length_unit_;
	const double h = inst->Height() * length_unit_;

	const double precision = settings_.get<settings::Precision>().get();
	if (r < precision || h < precision) {
		logger_.Message(Logger::LOG_ERROR, "GEO", 89, "Non-positive radius or height encountered for:", inst);
		return nullptr;
	}

	// A right circular cylinder is a disk of radius r extruded by its height h
	// along the local +Z axis. Build the disk as a single circular loop face,
	// mirroring IfcCircleProfileDef, then wrap it in a taxonomy::extrusion so
	// both geometry kernels handle it through the ordinary swept-solid path.
	auto circle = taxonomy::make<taxonomy::circle>();
	circle->radius = r;
	circle->matrix = taxonomy::make<taxonomy::matrix4>();

	auto edge = taxonomy::make<taxonomy::edge>();
	edge->basis = circle;
	edge->start = 0.;
	edge->end = 2 * boost::math::constants::pi<double>();

	auto loop = taxonomy::make<taxonomy::loop>();
	loop->children = { edge };
	loop->external = true;

	auto face = taxonomy::make<taxonomy::face>();
	face->children.push_back(loop);

	// IfcCsgPrimitive3D.Position places the whole solid; map() applies the unit scale.
	auto matrix = taxonomy::cast<taxonomy::matrix4>(map(inst->Position()));
	auto direction = taxonomy::make<taxonomy::direction3>(0, 0, 1);

	return taxonomy::make<taxonomy::extrusion>(matrix, face, direction, h);
}
