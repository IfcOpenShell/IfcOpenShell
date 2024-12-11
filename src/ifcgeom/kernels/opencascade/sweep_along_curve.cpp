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
#include "wire_utils.h"

#include <BRepOffsetAPI_MakePipeShell.hxx>
#include <Geom_Plane.hxx>
#include <ShapeAnalysis_Surface.hxx>
#include <BRepBuilderAPI_Transform.hxx>
#include <ShapeFix_Edge.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <TopExp.hxx>
#include <Geom_Circle.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;
using namespace IfcGeom::util;

namespace {
	bool wire_is_c1_continuous(const TopoDS_Wire& w, double tol) {
		// NB Note that c0 continuity is NOT checked!

		TopTools_IndexedDataMapOfShapeListOfShape map;
		TopExp::MapShapesAndAncestors(w, TopAbs_VERTEX, TopAbs_EDGE, map);
		for (int i = 1; i <= map.Extent(); ++i) {
			const auto& li = map.FindFromIndex(i);
			if (li.Extent() == 2) {
				const TopoDS_Vertex& v = TopoDS::Vertex(map.FindKey(i));

				const TopoDS_Edge& e0 = TopoDS::Edge(li.First());
				const TopoDS_Edge& e1 = TopoDS::Edge(li.Last());

				double u0 = BRep_Tool::Parameter(v, e0);
				double u1 = BRep_Tool::Parameter(v, e1);

				double _, __;
				Handle(Geom_Curve) c0 = BRep_Tool::Curve(e0, _, __);
				Handle(Geom_Curve) c1 = BRep_Tool::Curve(e1, _, __);

				gp_Pnt p;
				gp_Vec v0, v1;
				c0->D1(u0, p, v0);
				c1->D1(u1, p, v1);

				if (1. - std::abs(v0.Normalized().Dot(v1.Normalized())) > tol) {
					return false;
				}
			}
		}
		return true;
	}

	bool contains_circular_segments(const TopoDS_Wire& w) {
		for (TopoDS_Iterator it(w); it.More(); it.Next()) {
			const auto& e = TopoDS::Edge(it.Value());
			double _, __;
			auto crv = BRep_Tool::Curve(e, _, __);
			if (crv && crv->DynamicType() == STANDARD_TYPE(Geom_Circle)) {
				return true;
			}
		}
		return false;
	}
}

bool OpenCascadeKernel::convert(const taxonomy::sweep_along_curve::ptr scs, TopoDS_Shape& result) {
	auto w = convert_curve(scs->curve);
	if (w.which() != 2) {
		Logger::Error("Unsupported directrix");
		return false;
	}
	TopoDS_Shape face_;
	convert(taxonomy::cast<taxonomy::face>(scs->basis), face_);
	TopoDS_Face face;
	if (face_.ShapeType() == TopAbs_FACE) {
		face = TopoDS::Face(face_);
	} else if (face_.ShapeType() == TopAbs_WIRE) {
		wire_tolerance_settings settings{
			!settings_.get<settings::NoWireIntersectionCheck>().get(),
			!settings_.get<settings::NoWireIntersectionTolerance>().get(),
			0.,
			settings_.get<settings::Precision>().get()
		};
		if (!IfcGeom::util::convert_wire_to_face(TopoDS::Wire(face_), face, settings)) {
			return false;
		}
	} else {
		return false;
	}
	
	Handle(Geom_Surface) surface;
	if (scs->surface) {
		convert_surface(scs->surface);
	}	

	gp_Trsf directrix;
	TopoDS_Wire wire = boost::get<TopoDS_Wire>(w);

	const bool is_plane = surface && surface->DynamicType() == STANDARD_TYPE(Geom_Plane);

	gp_Pln pln;
	gp_Pnt directrix_origin;
	gp_Vec directrix_tangent;
	bool directrix_on_plane = is_plane;

	if (is_plane) {
		pln = Handle(Geom_Plane)::DownCast(surface)->Pln();
		// As per Informal propositions 2: The Directrix shall lie on the ReferenceSurface.
		// This is not always the case with the test files in the repository. I am not sure
		// how to deal with this and whether my interpretation of the propositions is
		// correct. However, if it has been asserted that the vertices of the directrix do
		// not conform to the ReferenceSurface, the ReferenceSurface is ignored.
		{
			for (TopExp_Explorer exp(wire, TopAbs_VERTEX); exp.More(); exp.Next()) {
				if (pln.Distance(BRep_Tool::Pnt(TopoDS::Vertex(exp.Current()))) > ALMOST_ZERO) {
					directrix_on_plane = false;
					Logger::Message(Logger::LOG_WARNING, "The Directrix does not lie on the ReferenceSurface", scs->instance);
					break;
				}
			}
		}
	}

	{
		TopoDS_Vertex v0, v1;
		TopExp::Vertices(wire, v0, v1);
		TopTools_IndexedDataMapOfShapeListOfShape m;
		TopExp::MapShapesAndAncestors(wire, TopAbs_VERTEX, TopAbs_EDGE, m);
		const TopoDS_Edge& edge = TopoDS::Edge(m.FindFromKey(v0).First());
		double u0, u1;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(edge, u0, u1);
		crv->D1(u0, directrix_origin, directrix_tangent);
	}

	if (is_plane && pln.Axis().Direction().IsNormal(directrix_tangent, 1.e-5) && directrix_on_plane) {
		directrix.SetTransformation(gp_Ax3(directrix_origin, directrix_tangent, pln.Axis().Direction()), gp::XOY());
	} else if (!is_plane && surface) {
		ShapeAnalysis_Surface sas(surface);
		auto pnt2d = sas.ValueOfUV(directrix_origin, settings_.get<settings::Precision>().get());
		// @todo should we revisit this pre 0.7 code wrt orientation?
		/*
		BRepGProp_Face prop(surface_face);
		gp_Pnt _;
		gp_Vec surface_normal;
		prop.Normal(pnt2d.X(), pnt2d.Y(), _, surface_normal);
		*/
		gp_Pnt _;
		gp_Vec surface_normal_u, surface_normal_v;
		surface->D1(pnt2d.X(), pnt2d.Y(), _, surface_normal_u, surface_normal_v);
		// @todo check order
		auto surface_normal = surface_normal_u.Crossed(surface_normal_v);
		directrix.SetTransformation(gp_Ax3(directrix_origin, directrix_tangent, surface_normal), gp::XOY());
	} else {
		directrix.SetTransformation(gp_Ax3(directrix_origin, directrix_tangent), gp::XOY());
	}
	face = TopoDS::Face(BRepBuilderAPI_Transform(face, directrix));

	TopoDS_Face surface_face;
	if (surface) {
		surface_face = BRepBuilderAPI_MakeFace(surface, settings_.get<settings::Precision>().get()).Face();
	}

	if (!is_plane && surface) {
		TopExp_Explorer exp(wire, TopAbs_EDGE);
		for (; exp.More(); exp.Next()) {
			ShapeFix_Edge sfe;
			sfe.FixAddPCurve(TopoDS::Edge(exp.Current()), surface_face, false, settings_.get<settings::Precision>().get());
		}
	}

	BRep_Builder BB;
	TopoDS_Shell comp;
	BB.MakeShell(comp);

	// NB: Note that StartParam and EndParam param are ignored and the assumption is
	// made that the parametric range over which to be swept matches the IfcCurve in
	// its entirety.

	// BRepOffsetAPI_MakePipeShell does not support FACE, so we need to manually iterate
	// over the wires, first processing the outer, then inner. Where the cap face is
	// constructed using MakeFace.

	auto outer = BRepTools::OuterWire(face);
	std::unique_ptr<BRepBuilderAPI_MakeFace> mf0, mf1;
	TopoDS_Face f0, f1;

	for (int i = 0; i < 2; ++i) {
		for (TopExp_Explorer exp(face, TopAbs_WIRE); exp.More(); exp.Next()) {
			const auto& section = TopoDS::Wire(exp.Current());
			if (section.IsSame(outer) != i == 0) {
				continue;
			}

			BRepOffsetAPI_MakePipeShell builder(wire);
			builder.Add(section);
			builder.SetTransitionMode(contains_circular_segments(wire) && wire_is_c1_continuous(wire, 1.e-2) ? BRepBuilderAPI_Transformed : BRepBuilderAPI_RightCorner);
			if (directrix_on_plane) {
				builder.SetMode(pln.Axis().Direction());
			} else if (!is_plane) {
				builder.SetMode(surface_face);
			}
			builder.Build();
			if (!builder.IsDone()) {
				return false;
			}
			auto w0 = TopoDS::Wire(builder.FirstShape());
			auto w1 = TopoDS::Wire(builder.LastShape());
			if (mf0) {
				mf0->Add(w0);
				mf1->Add(w1);
			} else {
				f0 = BRepBuilderAPI_MakeFace(w0).Face();
				f1 = BRepBuilderAPI_MakeFace(w1).Face();
				mf0.reset(new BRepBuilderAPI_MakeFace(f0));
				mf1.reset(new BRepBuilderAPI_MakeFace(f1));
			}

			for (TopExp_Explorer exp(builder.Shape(), TopAbs_FACE); exp.More(); exp.Next()) {
				BB.Add(comp, exp.Current());
			}
		}
	}

	if (mf0->IsDone() && mf1->IsDone()) {
		BB.Add(comp, mf0->Face());
		BB.Add(comp, mf1->Face());
	} else {
		BB.Add(comp, f0);
		BB.Add(comp, f1);
	}

	result = BRepBuilderAPI_MakeSolid(comp).Solid();

	return true;
}

bool OpenCascadeKernel::convert_impl(const taxonomy::sweep_along_curve::ptr scs, IfcGeom::ConversionResults& results) {
	TopoDS_Shape shape;
	// For tiny radii occt will fail building the sweep, in which case we enlarge the inputs to occt, and add a scale matrix to the output
	bool enlarged = false;
	static double enlarge_factor = 1000.;
	if (scs->basis->kind() == taxonomy::FACE) {
		auto w = std::static_pointer_cast<taxonomy::face>(scs->basis)->children[0];
		if (w->children.size() == 1 && w->children[0]->basis && w->children[0]->basis->kind() == taxonomy::CIRCLE) {
			auto circ = std::static_pointer_cast<taxonomy::circle>(w->children[0]->basis);
			enlarged = circ->radius < 1.e-4;
			if (enlarged) {
				// @todo immutability
				circ->radius *= enlarge_factor;
				auto crv = std::static_pointer_cast<taxonomy::geom_item>(scs->curve);
				if (crv->matrix) {
					crv->matrix = taxonomy::make<taxonomy::matrix4>(
						Eigen::Scaling(enlarge_factor) *
						crv->matrix->ccomponents()
					);
				} else {
					crv->matrix = taxonomy::make<taxonomy::matrix4>();
					crv->matrix->components().topLeftCorner<3, 3>() = Eigen::Scaling(enlarge_factor, enlarge_factor, enlarge_factor).toDenseMatrix();
				}
			}
		}
	}
	if (!convert(scs, shape)) {
		return false;
	}
	taxonomy::matrix4::ptr m;
	if (enlarged) {
		m = taxonomy::make<taxonomy::matrix4>(
			Eigen::Scaling(1. / enlarge_factor) *
			scs->matrix->ccomponents()
		);
	} else {
		m = scs->matrix;
	}
	results.emplace_back(ConversionResult(
		scs->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		m,
		new OpenCascadeShape(shape),
		scs->surface_style
	));
	return true;
}
