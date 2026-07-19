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

// Prototype kernel-level support for single-vertex / point-cloud
// representations (issues #134, #1409, #5218). A point becomes a
// TopoDS_Compound of TopoDS_Vertex. Point-cloud batching lives generically
// in AbstractKernel::convert_impl(collection), see that file.

#include "OpenCascadeKernel.h"

#include <BRepBuilderAPI_MakeVertex.hxx>
#include <BRep_Builder.hxx>
#include <TopoDS_Compound.hxx>

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;

namespace {
	TopoDS_Compound make_vertex_compound(const std::vector<gp_Pnt>& points) {
		TopoDS_Compound compound;
		BRep_Builder builder;
		builder.MakeCompound(compound);
		for (auto& p : points) {
			builder.Add(compound, BRepBuilderAPI_MakeVertex(p).Vertex());
		}
		return compound;
	}
}

bool OpenCascadeKernel::convert_impl(const taxonomy::point3::ptr point, IfcGeom::ConversionResults& results) {
	if (!point->instance) {
		return false;
	}

	auto p = convert_xyz<gp_Pnt>(*point);
	auto compound = make_vertex_compound({ p });

	results.emplace_back(ConversionResult(
		point->instance.id(),
		new OpenCascadeShape(compound),
		point->surface_style
	));
	return true;
}
