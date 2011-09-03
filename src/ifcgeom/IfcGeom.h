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

#ifndef IFCGEOM_H
#define IFCGEOM_H

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <Geom_Curve.hxx>
#include <gp_Pln.hxx>

#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcUtil.h"

namespace IfcGeom {
	bool convert_wire_to_face(const TopoDS_Wire& wire, TopoDS_Face& face);
	bool convert_shape(const IfcUtil::IfcBaseClass* L, TopoDS_Shape& result);
	bool convert_wire(const IfcUtil::IfcBaseClass* L, TopoDS_Wire& result);
	bool convert_curve(const IfcUtil::IfcBaseClass* L, Handle(Geom_Curve)& result);
	bool convert_face(const IfcUtil::IfcBaseClass* L, TopoDS_Face& result);
	bool convert_openings(const Ifc2x3::IfcProduct::ptr L, const Ifc2x3::IfcRelVoidsElement::list& openings, TopoDS_Shape& result, const gp_Trsf& trsf);
	bool profile_helper(int numVerts, float* verts, int numFillets, int* filletIndices, float* filletRadii, gp_Trsf2d trsf, TopoDS_Face& face); 
	namespace Cache {
		void Purge();
		void PurgeShapeCache();
	}
#include "IfcRegisterGeomHeader.h"
}
#endif
