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
#include <gp_Dir.hxx>
#include <gp_Ax3.hxx>
#include <gp_Pln.hxx>
#include <Geom_Plane.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <Standard_Version.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)
#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcPlane* l, TopoDS_Shape& face) {
	gp_Pln pln;
	convert(l, pln);
	Handle_Geom_Surface surf = new Geom_Plane(pln);
#if OCC_VERSION_HEX < 0x60502
	face = BRepBuilderAPI_MakeFace(surf);
#else
	face = BRepBuilderAPI_MakeFace(surf, getValue(GV_PRECISION));
#endif
	return true;
}
bool IfcGeom::Kernel::convert(const IfcSchema::IfcPlane* pln, gp_Pln& plane) {
	IN_CACHE(IfcPlane,pln,gp_Pln,plane)
	IfcSchema::IfcAxis2Placement3D* l = pln->Position();
	gp_Pnt o;gp_Dir axis = gp_Dir(0,0,1);gp_Dir refDirection;

	if (!l->Location()->declaration().is("IfcCartesianPoint")) {
		// only applicable to 4x3 rc2
		Logger::Error("Not implemented", l->Location());
		return false;
	}

	IfcGeom::Kernel::convert((const IfcSchema::IfcCartesianPoint*) l->Location(),o);
	bool hasRef = !!l->RefDirection();
	if ( l->Axis() ) IfcGeom::Kernel::convert(l->Axis(),axis);
	if ( hasRef ) IfcGeom::Kernel::convert(l->RefDirection(),refDirection);
	gp_Ax3 ax3;
	if ( hasRef ) ax3 = gp_Ax3(o,axis,refDirection);
	else ax3 = gp_Ax3(o,axis);
	plane = gp_Pln(ax3);
	CACHE(IfcPlane,pln,plane)
	return true;
}
