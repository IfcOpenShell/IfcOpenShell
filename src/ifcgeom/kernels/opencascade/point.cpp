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
// representations (issues #134, #1409, #5218). Points become a
// TopoDS_Compound of TopoDS_Vertex, per aothms's suggested approach.
// convert_impl(point3) handles a lone point; convert_impl(collection) takes a
// bulk fast path for a collection made up entirely of point3 children (e.g. a
// whole IfcCartesianPointList3D "PointCloud"), converting it to a single
// compound in one pass instead of once per point. See commit message for the
// overhead/benchmark discussion.

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
		point->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		new OpenCascadeShape(compound),
		point->surface_style
	));
	return true;
}

bool OpenCascadeKernel::convert_impl(const taxonomy::collection::ptr collection, IfcGeom::ConversionResults& results) {
	bool all_points = !collection->children.empty();
	for (auto& c : collection->children) {
		if (c->kind() != taxonomy::POINT3) {
			all_points = false;
			break;
		}
	}

	if (!all_points || !collection->instance) {
		// Not a homogeneous point cloud (or has no entity to attribute the
		// resulting shape to), fall back to the generic per-child conversion.
		return ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(collection, results);
	}

	std::vector<gp_Pnt> points;
	points.reserve(collection->children.size());
	for (auto& c : collection->children) {
		points.push_back(convert_xyz<gp_Pnt>(*std::static_pointer_cast<taxonomy::point3>(c)));
	}

	auto compound = make_vertex_compound(points);

	auto s = results.size();
	results.emplace_back(ConversionResult(
		collection->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		new OpenCascadeShape(compound),
		collection->surface_style
	));
	if (collection->matrix) {
		results[s].prepend(collection->matrix);
	}
	return true;
}
