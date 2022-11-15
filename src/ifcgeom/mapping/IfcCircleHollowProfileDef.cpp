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

#include <gp_Trsf2d.hxx>
#include <Geom_Circle.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <ShapeFix_Shape.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCircleHollowProfileDef* l, TopoDS_Shape& face) {
	const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
	const double t = l->WallThickness() * getValue(GV_LENGTH_UNIT);
	
	if ( r == 0.0f || t == 0.0f ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l);
		return false;
	}
	
	gp_Trsf2d trsf2d;
	bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
	has_position = l->Position() != nullptr;
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf2d);
	}

	gp_Ax2 ax = gp_Ax2().Transformed(trsf2d);

	BRepBuilderAPI_MakeWire outer;	
	Handle(Geom_Circle) outerCircle = new Geom_Circle(ax, r);
	outer.Add(BRepBuilderAPI_MakeEdge(outerCircle));
	BRepBuilderAPI_MakeFace mf(outer.Wire(), false);

	BRepBuilderAPI_MakeWire inner;	
	Handle(Geom_Circle) innerCirlce = new Geom_Circle(ax, r-t);
	inner.Add(BRepBuilderAPI_MakeEdge(innerCirlce));
	mf.Add(inner);

	ShapeFix_Shape sfs(mf.Face());
	sfs.Perform();
	face = TopoDS::Face(sfs.Shape());	
	return true;		
}
