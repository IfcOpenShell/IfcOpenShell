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

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Ax1.hxx>
#include <gp_Ax3.hxx>
#include <gp_Pln.hxx>
#include <BRepOffsetAPI_MakePipeShell.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopExp_Explorer.hxx>
#include <BRepBuilderAPI_Transform.hxx>
#include <ShapeFix_Edge.hxx>
#include <ShapeAnalysis_Surface.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSurfaceCurveSweptAreaSolid* l, TopoDS_Shape& shape) {
	gp_Trsf directrix;
	TopoDS_Shape face;
	TopoDS_Face surface_face;
	TopoDS_Wire wire, section;

	const bool is_plane = l->ReferenceSurface()->declaration().is(IfcSchema::IfcPlane::Class());

	if (!is_plane) {
		TopoDS_Shape surface_shell;
		if (!convert_shape(l->ReferenceSurface(), surface_shell)) {
			Logger::Error("Failed to convert reference surface", l);
			return false;
		}
		if (count(surface_shell, TopAbs_FACE) != 1) {
			Logger::Error("Non-continuous reference surface", l);
			return false;
		}
		surface_face = TopoDS::Face(TopExp_Explorer(surface_shell, TopAbs_FACE).Current());
	}
	
	gp_Trsf trsf;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
	has_position = l->Position() != nullptr;
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf);
	}

	if (!convert_face(l->SweptArea(), face) || 
		!convert_wire(l->Directrix(), wire)    ) {
		return false;
	}

	gp_Pln pln;
	gp_Pnt directrix_origin;
	gp_Vec directrix_tangent;
	bool directrix_on_plane = is_plane;

	if (is_plane) {
		IfcGeom::Kernel::convert((IfcSchema::IfcPlane*) l->ReferenceSurface(), pln);

		// As per Informal propositions 2: The Directrix shall lie on the ReferenceSurface.
		// This is not always the case with the test files in the repository. I am not sure
		// how to deal with this and whether my interpretation of the propositions is
		// correct. However, if it has been asserted that the vertices of the directrix do
		// not conform to the ReferenceSurface, the ReferenceSurface is ignored.
		{
			for (TopExp_Explorer exp(wire, TopAbs_VERTEX); exp.More(); exp.Next()) {
				if (pln.Distance(BRep_Tool::Pnt(TopoDS::Vertex(exp.Current()))) > ALMOST_ZERO) {
					directrix_on_plane = false;
					Logger::Message(Logger::LOG_WARNING, "The Directrix does not lie on the ReferenceSurface", l);
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

	if (is_plane && pln.Axis().Direction().IsNormal(directrix_tangent, Precision::Approximation()) && directrix_on_plane) {
		directrix.SetTransformation(gp_Ax3(directrix_origin, directrix_tangent, pln.Axis().Direction()), gp::XOY());
	} else if (!is_plane) {
		ShapeAnalysis_Surface sas(BRep_Tool::Surface(surface_face));
		auto pnt2d = sas.ValueOfUV(directrix_origin, getValue(GV_PRECISION) * 10.);
		BRepGProp_Face prop(surface_face);
		gp_Pnt _;
		gp_Vec surface_normal;
		prop.Normal(pnt2d.X(), pnt2d.Y(), _, surface_normal);
		directrix.SetTransformation(gp_Ax3(directrix_origin, directrix_tangent, surface_normal), gp::XOY());
	} else {
		directrix.SetTransformation(gp_Ax3(directrix_origin, directrix_tangent), gp::XOY());
	}
	face = BRepBuilderAPI_Transform(face, directrix);

	if (!is_plane) {
		TopExp_Explorer exp(wire, TopAbs_EDGE);
		for (; exp.More(); exp.Next()) {
			ShapeFix_Edge sfe;
			sfe.FixAddPCurve(TopoDS::Edge(exp.Current()), surface_face, false, getValue(GV_PRECISION));
		}
	}

	// NB: Note that StartParam and EndParam param are ignored and the assumption is
	// made that the parametric range over which to be swept matches the IfcCurve in
	// its entirety.
	BRepOffsetAPI_MakePipeShell builder(wire);

	{ TopExp_Explorer exp(face, TopAbs_WIRE);
	section = TopoDS::Wire(exp.Current()); }

	builder.Add(section);
	builder.SetTransitionMode(BRepBuilderAPI_RightCorner);
	if (directrix_on_plane) {
		builder.SetMode(pln.Axis().Direction());
	} else if (!is_plane) {
		builder.SetMode(surface_face);
	}
	builder.Build();
	builder.MakeSolid();
	shape = builder.Shape();

	if (has_position) {
		// IfcSweptAreaSolid.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}

	return true;
}
