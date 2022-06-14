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
#include <gp_Vec2d.hxx>
#include <gp_Dir2d.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Ax1.hxx>
#include <gp_Ax3.hxx>
#include <gp_Ax2d.hxx>
#include <gp_Pln.hxx>
#include <gp_Circ.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TColgp_Array1OfPnt2d.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include <Geom_Line.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <Geom_TrimmedCurve.hxx>
#include <Geom_CylindricalSurface.hxx>
#include <BRepOffsetAPI_Sewing.hxx>
#include <BRepOffsetAPI_MakePipe.hxx>
#include <BRepOffsetAPI_MakePipeShell.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_CompSolid.hxx>
#include <TopExp.hxx>
#include <TopExp_Explorer.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepPrimAPI_MakeRevol.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeCone.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <BRepPrimAPI_MakeSphere.hxx>
#include <BRepPrimAPI_MakeWedge.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_Transform.hxx>
#include <BRepBuilderAPI_MakeShell.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepAlgoAPI_Fuse.hxx>
#include <BRepAlgoAPI_Common.hxx>
#include <ShapeFix_Edge.hxx>
#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>
#include <TopLoc_Location.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepClass3d_SolidClassifier.hxx>
#include <Standard_Version.hxx>
#include <TopTools_ListIteratorOfListOfShape.hxx>
#include <ShapeAnalysis_Surface.hxx>
#include "../ifcgeom/IfcGeom.h"
#include <memory>
#include <Geom_ToroidalSurface.hxx>

#include "../ifcgeom_schema_agnostic/sweep_utils.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSweptDiskSolid* l, TopoDS_Shape& shape) {
	TopoDS_Wire wire, section1, section2;

	bool hasInnerRadius = !!l->InnerRadius();

	if (!convert_wire(l->Directrix(), wire)) {
		return false;
	}
	
	// Start- EndParam became optional in IFC4
#ifdef SCHEMA_IfcSweptDiskSolid_StartParam_IS_OPTIONAL
	auto sp = l->StartParam();
	auto ep = l->EndParam();
#else
	boost::optional<double> sp, ep;
	sp = l->StartParam();
	ep = l->EndParam();
#endif

	if (count(wire, TopAbs_EDGE) == 1 && sp && ep) {
		TopoDS_Vertex v0, v1;
		TopExp::Vertices(wire, v0, v1);
		if (v0.IsSame(v1)) {
			TopExp_Explorer exp(wire, TopAbs_EDGE);
			auto& e = TopoDS::Edge(exp.Current());
			double a, b;
			auto crv = BRep_Tool::Curve(e, a, b);
			if ((crv->DynamicType() == STANDARD_TYPE(Geom_Circle)) ||
				(crv->DynamicType() == STANDARD_TYPE(Geom_Ellipse))) 
			{
				BRepBuilderAPI_MakeEdge me(crv, *sp, *ep);
				if (me.IsDone()) {
					auto e2 = me.Edge();
					BRep_Builder B;
					wire.Nullify();
					B.MakeWire(wire);
					B.Add(wire, e2);
				}
			}
		}
	}

	// NB: Note that StartParam and EndParam param are ignored and the assumption is
	// made that the parametric range over which to be swept matches the IfcCurve in
	// its entirety.
	
	util::process_sweep(wire, l->Radius() * getValue(GV_LENGTH_UNIT), shape);

	if (shape.IsNull()) {
		return false;
	}

	double r2 = 0.;

	if (hasInnerRadius) {
		// Subtraction of pipes with small radii is unstable.
		r2 = *l->InnerRadius() * getValue(GV_LENGTH_UNIT);
	}

	if (r2 > getValue(GV_PRECISION) * 10.) {
		TopoDS_Shape inner;
		util::process_sweep(wire, r2, inner);

		bool is_valid = false;

		// Boolean op on the compound of separately processed sweeps
		// is not attempted.
		// @todo iterate over compound subshapes and process boolean
		// separately.
		// @todo don't process as boolean op at all, since we know
		// only the start and end faces intersect and we know they
		// are co-planar and we know they are circles.
		if (shape.ShapeType() != TopAbs_COMPOUND) {
			BRepAlgoAPI_Cut brep_cut(shape, inner);
			if (brep_cut.IsDone()) {
				TopoDS_Shape result = brep_cut;

				ShapeFix_Shape fix(result);
				fix.Perform();
				result = fix.Shape();

				is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
				if (is_valid) {
					shape = result;
				}
			}
		}

		if (!is_valid) {
			Logger::Message(Logger::LOG_WARNING, "Failed to subtract inner radius void for:", l);
		}
	}

	return true;
}
