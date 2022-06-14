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
#include <BRepOffsetAPI_Sewing.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopExp_Explorer.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepBuilderAPI_MakeShell.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>
#include <BRepFilletAPI_MakeFillet2d.hxx>
#include <TopLoc_Location.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcObjectPlacement* l, gp_Trsf& trsf) {
	IN_CACHE(IfcObjectPlacement,l,gp_Trsf,trsf)
	if ( ! l->declaration().is(IfcSchema::IfcLocalPlacement::Class()) ) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported IfcObjectPlacement:", l);
		return false; 		
	}
	IfcSchema::IfcLocalPlacement* current = (IfcSchema::IfcLocalPlacement*)l;
	for (;;) {

		gp_Trsf trsf2;
		IfcSchema::IfcAxis2Placement* relplacement = current->RelativePlacement();
		if (relplacement->as<IfcSchema::IfcAxis2Placement3D>()) {
			IfcGeom::Kernel::convert(relplacement->as<IfcSchema::IfcAxis2Placement3D>(),trsf2);
			trsf.PreMultiply(trsf2);
		}

		if (current->PlacementRelTo()) {
			IfcSchema::IfcObjectPlacement* parent = current->PlacementRelTo();

			bool parent_placement_ignored = false;
			if (placement_rel_to_type_ || placement_rel_to_instance_) {
				IfcSchema::IfcProduct::list::ptr parent_places = parent->PlacesObject();
				for (auto iter = parent_places->begin(); iter != parent_places->end(); ++iter) {
					if ((placement_rel_to_type_ && (*iter)->declaration().is(*placement_rel_to_type_)) ||
						(placement_rel_to_instance_ && (*iter)->as<IfcUtil::IfcBaseEntity>() == placement_rel_to_instance_)) {
						parent_placement_ignored = true;
					}
				}
			}

			if (parent_placement_ignored) {
				// The parent placement of the current is a placement for a type that is
				// being ignored (Site or Building) or it is the host element of an opening.
				break;
			} else if (parent->declaration().is(IfcSchema::IfcLocalPlacement::Class())) {
				// Keep processing parent placements
				current = current->PlacementRelTo()->as<IfcSchema::IfcLocalPlacement>();
			} else {
				// This is the root placement (typically Site).
				break;
			}
		} else {
			break;
		}
	}

	trsf.PreMultiply(offset_and_rotation);
	
	CACHE(IfcObjectPlacement,l,trsf)
	return true;
}
