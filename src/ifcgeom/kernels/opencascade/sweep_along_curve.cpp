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

#include <BRepOffsetAPI_MakePipeShell.hxx>
#include <Geom_Plane.hxx>
#include <ShapeAnalysis_Surface.hxx>
#include <BRepBuilderAPI_Transform.hxx>
#include <ShapeFix_Edge.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;
using namespace IfcGeom::util;

bool OpenCascadeKernel::convert(const taxonomy::sweep_along_curve::ptr scs, TopoDS_Shape& result) {
	auto w = convert_curve(scs->curve);
	if (w.which() == 0) {
		Logger::Error("Unsupported directrix");
	}
	TopoDS_Shape face;
	convert(taxonomy::cast<taxonomy::face>(scs->basis), face);
	
	Handle(Geom_Surface) surface;
	if (scs->surface) {
		convert_surface(scs->surface);
	}	

	gp_Trsf directrix;
	TopoDS_Wire wire = boost::get<TopoDS_Wire>(w);
	TopoDS_Wire section;

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
		TopExp_Explorer exp(wire, TopAbs_EDGE);
		TopoDS_Edge edge = TopoDS::Edge(exp.Current());
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
	face = BRepBuilderAPI_Transform(face, directrix);

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

	// NB: Note that StartParam and EndParam param are ignored and the assumption is
	// made that the parametric range over which to be swept matches the IfcCurve in
	// its entirety.
	BRepOffsetAPI_MakePipeShell builder(wire);

	{
		TopExp_Explorer exp(face, TopAbs_WIRE);
		section = TopoDS::Wire(exp.Current());
	}

	builder.Add(section);
	builder.SetTransitionMode(BRepBuilderAPI_RightCorner);
	if (directrix_on_plane) {
		builder.SetMode(pln.Axis().Direction());
	} else if (!is_plane) {
		builder.SetMode(surface_face);
	}
	builder.Build();
	builder.MakeSolid();
	result = builder.Shape();

	return true;
}

bool OpenCascadeKernel::convert_impl(const taxonomy::sweep_along_curve::ptr scs, IfcGeom::ConversionResults& results) {
	TopoDS_Shape shape;
	if (!convert(scs, shape)) {
		return false;
	}
	results.emplace_back(ConversionResult(
		scs->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		scs->matrix,
		new OpenCascadeShape(shape),
		scs->surface_style
	));
	return true;
}
