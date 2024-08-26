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

#include "OpenCascadeKernel.h"
#include "base_utils.h"

#include <TopExp.hxx>
#include <BRepFill_Filling.hxx>
#include <BRepTools_WireExplorer.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;
using namespace IfcGeom::util;

bool OpenCascadeKernel::convert(const taxonomy::loft::ptr loft, TopoDS_Shape& result) {
	// @todo this approach based on BRepFill_Filling is both slow, as well as
	// potentially incorrect as there is no guarantee that the wires for
	// subsequently placed profiles are traversed from an equivalent start vertex.
	
	if (loft->children.size() < 2) {
		return false;
	}
	
	TopTools_ListOfShape faces;
	TopoDS_Compound comp;
	BRep_Builder BB;
	BB.MakeCompound(comp);

	for (auto it = loft->children.begin(); it < loft->children.end() - 1; ++it) {
		auto jt = it + 1;
		std::array<taxonomy::face::ptr, 2> fa = { *it, *jt };
		std::array<TopoDS_Shape, 2> shps;
		std::array<TopoDS_Wire, 2> ws;
		for (int i = 0; i < 2; ++i) {
			if (!convert(fa[i], shps[i])) {
				return false;
			}
			if (shps[i].ShapeType() != TopAbs_FACE) {
				return false;
			}
			// @todo this is only outer wire
			ws[i] = BRepTools::OuterWire(TopoDS::Face(shps[i]));
		}
		if (it == loft->children.begin()) {
			// faces.Append(shps[0]);
			BB.Add(comp, shps[0]);
		}
		if (jt == loft->children.end() - 1) {
			// faces.Append(shps[1]);
			BB.Add(comp, shps[1]);
		}
		BRepTools_WireExplorer a(ws[0]);
		BRepTools_WireExplorer b(ws[1]);
		for (; a.More() && b.More(); a.Next(), b.Next()) {
			auto& e1 = a.Current();
			// auto e3 = TopoDS::Edge(b.Current().Reversed());
			auto& e3 = b.Current();

			// Documentation says unconnected edges are automatically connected, but this is not the case
			TopoDS_Vertex e1a, e1b, e3a, e3b;
			TopExp::Vertices(e1, e1a, e1b, true);
			TopExp::Vertices(e3, e3a, e3b, true);
			auto e2 = BRepBuilderAPI_MakeEdge(e1b, e3a).Edge();
			auto e4 = BRepBuilderAPI_MakeEdge(e3b, e1a).Edge();
			
			/*
			BRepFill_Filling fill;
			fill.Add(e1, GeomAbs_C0);
			fill.Add(e2, GeomAbs_C0);
			fill.Add(e3, GeomAbs_C0);
			fill.Add(e4, GeomAbs_C0);
			fill.Build();
			// faces.Append(fill.Face());
			BB.Add(comp, fill.Face());
			*/

			auto f = BRepBuilderAPI_MakeFace(BRepBuilderAPI_MakePolygon(e1a, e1b, e3b, true).Wire()).Face();
			BB.Add(comp, f);
			auto g = BRepBuilderAPI_MakeFace(BRepBuilderAPI_MakePolygon(e3b, e3a, e1a, true).Wire()).Face();
			BB.Add(comp, g);
		}
	}

	// create_solid_from_faces(faces, result, settings_.get<settings::Precision>().get());
	result = comp;

	return true;
}

bool OpenCascadeKernel::convert_impl(const taxonomy::loft::ptr loft, IfcGeom::ConversionResults& results) {
	TopoDS_Shape shape;
	if (!convert(loft, shape)) {
		return false;
	}
	results.emplace_back(ConversionResult(
		loft->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		loft->matrix,
		new OpenCascadeShape(shape),
		loft->surface_style
	));
	return true;
}
