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

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcMappedItem* l, IfcRepresentationShapeItems& shapes) {
	gp_GTrsf gtrsf;
	IfcSchema::IfcCartesianTransformationOperator* transform = l->MappingTarget();
	if ( transform->declaration().is(IfcSchema::IfcCartesianTransformationOperator3DnonUniform::Class()) ) {
		IfcGeom::Kernel::convert((IfcSchema::IfcCartesianTransformationOperator3DnonUniform*)transform,gtrsf);
	} else if ( transform->declaration().is(IfcSchema::IfcCartesianTransformationOperator2DnonUniform::Class()) ) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported MappingTarget:", transform);
		return false;
	} else if ( transform->declaration().is(IfcSchema::IfcCartesianTransformationOperator3D::Class()) ) {
		gp_Trsf trsf;
		IfcGeom::Kernel::convert((IfcSchema::IfcCartesianTransformationOperator3D*)transform,trsf);
		gtrsf = trsf;
	} else if ( transform->declaration().is(IfcSchema::IfcCartesianTransformationOperator2D::Class()) ) {
		gp_Trsf2d trsf_2d;
		IfcGeom::Kernel::convert((IfcSchema::IfcCartesianTransformationOperator2D*)transform,trsf_2d);
		gtrsf = (gp_Trsf) trsf_2d;
	}
	IfcSchema::IfcRepresentationMap* map = l->MappingSource();
	IfcSchema::IfcAxis2Placement* placement = map->MappingOrigin();
	gp_Trsf trsf;
	if (placement->declaration().is(IfcSchema::IfcAxis2Placement3D::Class())) {
		IfcGeom::Kernel::convert((IfcSchema::IfcAxis2Placement3D*)placement,trsf);
	} else {
		gp_Trsf2d trsf_2d;
		IfcGeom::Kernel::convert((IfcSchema::IfcAxis2Placement2D*)placement,trsf_2d);
		trsf = trsf_2d;
	}
	gtrsf.Multiply(trsf);

	auto mapped_item_style = get_style(l);
	
	const size_t previous_size = shapes.size();
	bool b = convert_shapes(map->MappedRepresentation(), shapes);
	
	for (size_t i = previous_size; i < shapes.size(); ++ i ) {
		shapes[i].prepend(gtrsf);

		// Apply styles assigned to the mapped item only if on
		// a more granular level no styles have been applied
		if (!shapes[i].hasStyle()) {
			shapes[i].setStyle(mapped_item_style);
		}
	}

	return b;
}
