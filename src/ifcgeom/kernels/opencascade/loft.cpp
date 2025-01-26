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
#include <BRepTools_WireExplorer.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepOffsetAPI_ThruSections.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;
using namespace IfcGeom::util;

bool OpenCascadeKernel::convert(const taxonomy::loft::ptr loft, TopoDS_Shape& result) {
	if (loft->children.size() < 2) {
		return false;
	}

	bool non_polygonal = false;
	for (auto& ch : loft->children) {
		if (ch->kind() == taxonomy::FACE) {
			const auto& f = std::static_pointer_cast<taxonomy::face>(ch);
			for (auto& w : f->children) {
				for (auto& e : w->children) {
					if (e->basis && e->basis->kind() != taxonomy::LINE) {
						non_polygonal = true;
						break;
					}
				}
				if (non_polygonal) {
					break;
				}
			}
			if (non_polygonal) {
				break;
			}
		}
	}

	if (non_polygonal) {
		if (loft->children.size() == 2) {
			BRep_Builder BB;
			TopoDS_Shell comp;
			BB.MakeShell(comp);


			TopoDS_Shape f0, f1;
			if (!convert(std::static_pointer_cast<taxonomy::face>(loft->children.front()), f0) ||
				!convert(std::static_pointer_cast<taxonomy::face>(loft->children.back()), f1))
			{
				return false;
			}
			if (f0.ShapeType() != TopAbs_FACE || f1.ShapeType() != TopAbs_FACE) {
				return false;
			}

			TopExp_Explorer exp1(f0, TopAbs_WIRE);
			TopExp_Explorer exp2(f1, TopAbs_WIRE);
			for (; exp1.More() && exp2.More(); exp1.Next(), exp2.Next()) {
				const auto& w1 = TopoDS::Wire(exp1.Current());
				const auto& w2 = TopoDS::Wire(exp2.Current());
				BRepOffsetAPI_ThruSections builder;
				builder.AddWire(w1);
				builder.AddWire(w2);
				builder.Build();
				if (!builder.IsDone()) {
					return false;
				}
				for (TopExp_Explorer exp(builder.Shape(), TopAbs_FACE); exp.More(); exp.Next()) {
					BB.Add(comp, exp.Current());
				}
			}

			BB.Add(comp, f0.Reversed());
			BB.Add(comp, f1);

			result = BRepBuilderAPI_MakeSolid(comp).Solid();

			return true;
		} else {
			Logger::Error("Lofting more than two sections is not supported");
			return false;
		}
	}
	
	TopTools_ListOfShape faces;
	TopoDS_Compound comp;
	BRep_Builder BB;
	BB.MakeCompound(comp);

	// @todo this approach is
	// potentially incorrect as there is no guarantee that the wires for
	// subsequently placed profiles are traversed from an equivalent start vertex.

	for (auto it = loft->children.begin(); it < loft->children.end() - 1; ++it) {
		auto jt = it + 1;
		std::array<taxonomy::item::ptr, 2> fa = { *it, *jt };
		std::array<TopoDS_Shape, 2> shps;
		std::array<TopoDS_Wire, 2> ws;
		for (int i = 0; i < 2; ++i) {
			if (fa[i]->kind() == taxonomy::FACE) {
				if (!convert(std::static_pointer_cast<taxonomy::face>(fa[i]), shps[i])) {
					return false;
				}
			}
			if (fa[i]->kind() == taxonomy::LOOP) {
				TopoDS_Wire w;
				if (!convert(std::static_pointer_cast<taxonomy::loop>(fa[i]), w)) {
					return false;
				}
				shps[i] = w;
			}
			if (shps[i].ShapeType() != TopAbs_FACE && shps[i].ShapeType() != TopAbs_WIRE) {
				return false;
			}
			// @todo this is only outer wire
			if (shps[i].ShapeType() == TopAbs_FACE) {
				ws[i] = BRepTools::OuterWire(TopoDS::Face(shps[i]));
			} else {
				ws[i] = TopoDS::Wire(shps[i]);
			}
		}
		if (shps[0].ShapeType() == TopAbs_FACE) {
			// When processing a sectioned *surface* there are no
			// begin and end caps that need to be added.
			if (it == loft->children.begin()) {
				// faces.Append(shps[0]);
				BB.Add(comp, shps[0]);
			}
			if (jt == loft->children.end() - 1) {
				// faces.Append(shps[1]);
				BB.Add(comp, shps[1]);
			}
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
