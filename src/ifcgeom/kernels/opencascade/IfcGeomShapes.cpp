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

/********************************************************************************
 *                                                                              *
 * Implementations of the various conversion functions defined in IfcRegister.h *
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

#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>

#include <TopLoc_Location.hxx>

#include <BRepCheck_Analyzer.hxx>
#include <BRepClass3d_SolidClassifier.hxx>

#include <Standard_Version.hxx>

#include <TopTools_ListIteratorOfListOfShape.hxx>

#include "OpenCascadeKernel.h"

#include <memory>

#include "../../../ifcparse/IfcLogger.h"

using namespace ifcopenshell::geometry; 
using namespace ifcopenshell::geometry::kernels;

bool OpenCascadeKernel::convert(const taxonomy::extrusion& extrusion, TopoDS_Shape& shape) {
	const double& height = extrusion.depth;

	if (height < precision_) {
		Logger::Error("Non-positive extrusion height encountered for:", extrusion.instance);
		return false;
	}

	TopoDS_Shape face;
	if (!convert(extrusion.basis, face)) {
		return false;
	}

	gp_Trsf trsf;
	if (!convert(extrusion.matrix, trsf)) {
		Logger::Error("Unable to move extrusion");
	}
	
	gp_Dir dir;
	if (!convert(extrusion.direction, dir)) {
		return false;
	}

	shape.Nullify();

	if (face.ShapeType() == TopAbs_COMPOUND) {
		
		// For compounds (most likely the result of a IfcCompositeProfileDef) 
		// create a compound solid shape.
		
		TopExp_Explorer exp(face, TopAbs_FACE);
		
		TopoDS_CompSolid compound;
		BRep_Builder builder;
		builder.MakeCompSolid(compound);
		
		int num_faces_extruded = 0;
		for (; exp.More(); exp.Next(), ++num_faces_extruded) {
			builder.Add(compound, BRepPrimAPI_MakePrism(exp.Current(), height*dir));
		}

		if (num_faces_extruded) {
			shape = compound;
		}

	}
	
	if (shape.IsNull()) {	
		shape = BRepPrimAPI_MakePrism(face, height*dir);
	}

	if (!shape.IsNull()) {
		// IfcSweptAreaSolid.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}

	return !shape.IsNull();
}
