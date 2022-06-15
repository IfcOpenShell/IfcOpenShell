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

#include <BRepBuilderAPI_MakeWire.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include "../ifcgeom/IfcGeom.h"

#define _USE_MATH_DEFINES
#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcEdgeLoop* l, TopoDS_Wire& result) {
	IfcSchema::IfcOrientedEdge::list::ptr li = l->EdgeList();
	BRepBuilderAPI_MakeWire mw;
	for (IfcSchema::IfcOrientedEdge::list::it it = li->begin(); it != li->end(); ++it) {
		TopoDS_Wire w;
		if (convert_wire(*it, w)) {
			mw.Add(TopoDS::Edge(TopoDS_Iterator(w).Value()));
		}
	}
	if (!mw.IsDone()) {
		return false;
	}
	result = mw.Wire();
	return true;
}
